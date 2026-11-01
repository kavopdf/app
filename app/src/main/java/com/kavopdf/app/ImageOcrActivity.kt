package com.kavopdf.app

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
import kotlin.coroutines.resume

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
            val pages = ArrayList<PdfEngine.PageText>()
            val text = StringBuilder()
            val flat = runCatching { Files.newFile(this@ImageOcrActivity, "imgflat.pdf") }.getOrNull()
            if (flat == null) {
                busy.dismiss()
                toast(getString(R.string.msg_failed, "PDF"))
                return@launch
            }
            val writer = PdfEngine.ImagePdfWriter(OCR_MAX, false)
            var built = false
            try {
                for ((i, uri) in uris.withIndex()) {
                    busy.update(getString(R.string.image_ocr_working, i + 1, uris.size))
                    // Copy first, then decode that one copy. The picture the recogniser reads
                    // is the same picture that goes onto the page, so an image is decoded once
                    // instead of twice and the boxes cannot drift away from what is shown.
                    val file = withContext(Dispatchers.IO) {
                        runCatching { Files.copyToCache(this@ImageOcrActivity, uri) }.getOrNull()
                    } ?: continue
                    val bmp = withContext(Dispatchers.IO) {
                        runCatching { PdfEngine.decodeImage(file, OCR_MAX) }.getOrNull()
                    } ?: continue
                    val w = bmp.width
                    val h = bmp.height
                    val words = recognise(bmp)
                    bmp.recycle()
                    // The page is built from the file itself: a JPEG is embedded as its
                    // original bytes, so there is no re-encode and no loss.
                    // A phone photo keeps its rotation in EXIF: the bitmap is already turned
                    // for the recogniser, so the page is told to rotate to match instead of
                    // the JPEG being re-encoded.
                    val degrees = withContext(Dispatchers.IO) {
                        runCatching { PdfEngine.exifDegrees(file) }.getOrDefault(0)
                    }
                    val added = withContext(Dispatchers.IO) {
                        runCatching { writer.addPage(file, w, h, degrees) }.isSuccess
                    }
                    if (!added) continue
                    pages.add(PdfEngine.PageText(pages.size + 1, w, h, words))
                    if (words.isNotEmpty()) {
                        if (text.isNotEmpty()) text.append("\n\n")
                        text.append(names.getOrElse(i) { "image ${i + 1}" }).append("\n")
                        text.append(words.joinToString(" ") { it.text })
                    }
                }
                built = withContext(Dispatchers.IO) {
                    runCatching { writer.finish(flat) }.isSuccess
                }
            } finally {
                writer.close()
            }
            busy.dismiss()
            if (!built) {
                toast(getString(R.string.msg_failed, "PDF"))
                return@launch
            }
            recognisedText = text.toString()
            if (pages.isEmpty()) {
                toast(getString(R.string.image_ocr_none))
                return@launch
            }
            runAndSave(Files.sanitize("images_searchable.pdf")) { out ->
                PdfEngine.addTextLayer(flat, pages, out)
                pages.size
            }
        }
    }

    private suspend fun recognise(bitmap: android.graphics.Bitmap): List<PdfEngine.OcrWord> =
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
        const val OCR_MAX = 2600
    }
}
