package com.kavopdf.app

import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import androidx.lifecycle.lifecycleScope
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.TextRecognizer
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import com.kavopdf.app.databinding.ActivityImageOcrBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.util.Files
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlin.coroutines.suspendCoroutine
import kotlinx.coroutines.withContext
import java.io.File
import kotlin.coroutines.resume
import kotlin.math.max

/**
 * Reads the text in photos / screenshots on-device and saves them as a PDF that
 * can be searched and copied.
 */
class ImageOcrActivity : PdfActivity() {

    private lateinit var binding: ActivityImageOcrBinding
    private val uris = ArrayList<Uri>()
    private val names = ArrayList<String>()

    /** The text recognised so far, so it can be copied anywhere. */
    private var recognisedText = ""


    private val recogniser: TextRecognizer by lazy {
        TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityImageOcrBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.btnChoose.setOnClickListener { pickImages() }
        binding.btnRun.setOnClickListener { run() }
        pickAfterEnter { pickImages() }
    }


    override fun onImagesChosen(uris: List<Uri>) {
        this.uris.clear()
        names.clear()
        this.uris.addAll(uris)
        uris.forEach { names.add(Files.displayName(this, it)) }
        binding.fileName.text = if (names.isEmpty()) getString(R.string.image_ocr_no_images)
        else getString(R.string.image_ocr_images, names.size)
        binding.btnRun.isEnabled = names.isNotEmpty()
    }

    private fun run() {
        if (uris.isEmpty()) return toast(getString(R.string.msg_need_one_image))
        lifecycleScope.launch {
            busy.show(getString(R.string.image_ocr_working, 1, uris.size))
            val inputs = ArrayList<File>()
            val pages = ArrayList<PdfEngine.PageText>()
            val text = StringBuilder()
            for ((i, uri) in uris.withIndex()) {
                busy.update(getString(R.string.image_ocr_working, i + 1, uris.size))
                // Copy once, then decode that same file through the shared decoder, which
                // applies EXIF orientation. Decoding the uri separately left the OCR
                // reading a sideways bitmap while the PDF embedded an upright one, so the
                // text layer sat 90 degrees away from the page on portrait photos.
                val f = withContext(Dispatchers.IO) {
                    runCatching { Files.copyToCache(this@ImageOcrActivity, uri) }.getOrNull()
                } ?: continue
                val bmp = withContext(Dispatchers.IO) {
                    runCatching { PdfEngine.decodeImage(f, OCR_MAX) }.getOrNull()
                } ?: continue
                val w = bmp.width
                val h = bmp.height
                val words = recognise(bmp)
                bmp.recycle()
                inputs.add(f)
                pages.add(PdfEngine.PageText(inputs.size, w, h, words))
                if (words.isNotEmpty()) {
                    if (text.isNotEmpty()) text.append("\n\n")
                    text.append(names.getOrElse(i) { "image ${i + 1}" }).append("\n")
                    text.append(words.joinToString(" ") { it.text })
                }
            }
            busy.dismiss()
            recognisedText = text.toString()
            val chars = recognisedText.count { !it.isWhitespace() }
            if (pages.isEmpty()) {
                toast(getString(R.string.image_ocr_none))
                return@launch
            }
            runAndSave(Files.sanitize("images_searchable.pdf")) { out ->
                val flat = Files.newFile(this@ImageOcrActivity, "imgflat.pdf")
                PdfEngine.imagesToPdf(inputs, flat, OCR_MAX, false)
                PdfEngine.addTextLayer(flat, pages, out)
            }
        }
    }

    private suspend fun recognise(bitmap: Bitmap): List<PdfEngine.OcrWord> =
        suspendCoroutine { cont ->
            recogniser.process(InputImage.fromBitmap(bitmap, 0))
                .addOnSuccessListener { result ->
                    val words = ArrayList<PdfEngine.OcrWord>()
                    for (block in result.textBlocks) {
                        for (line in block.lines) {
                            for (el in line.elements) {
                                val b = el.boundingBox ?: continue
                                val t = el.text
                                if (t.isBlank() || b.width() <= 0 || b.height() <= 0) continue
                                // A single character the recogniser barely believes is a
                                // spec of dirt or a rule, not a word. Kept deliberately
                                // narrow: the layer is invisible, so a stray glyph costs
                                // nothing while a dropped real character costs a search
                                // hit. Only one character AND very low confidence.
                                val conf = el.confidence
                                if (t.trim().length <= 1 && conf != null && conf < 0.3f) continue
                                words.add(
                                    PdfEngine.OcrWord(
                                        t, b.left.toFloat(), b.top.toFloat(),
                                        b.width().toFloat(), b.height().toFloat()
                                    )
                                )
                            }
                        }
                    }
                    cont.resume(words)
                }
                .addOnFailureListener { cont.resume(emptyList()) }
        }

    override fun onDestroy() {
        super.onDestroy()
        try { recogniser.close() } catch (_: Exception) { }
    }

    private companion object {
        /** Decode size for recognition: higher is noticeably more accurate. */
        /**
         * Longest edge for the image that goes INTO the PDF, and for the bitmap handed to
         * the recogniser.
         *
         * It is the same number Images-to-PDF uses on purpose: the same photo must not
         * come out at a different size depending on which tool made the file. Note that
         * decodeBounded samples by powers of two, so this is a target rather than a hard
         * cap - a 4000 px photo is decoded at 4000 px, not at 3000.
         */
        const val OCR_MAX = 3000
    }
}
