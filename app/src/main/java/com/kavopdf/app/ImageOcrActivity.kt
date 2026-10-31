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
                val bmp = withContext(Dispatchers.IO) {
                    runCatching { decodeBounded(uri, OCR_MAX) }.getOrNull()
                } ?: continue
                val w = bmp.width
                val h = bmp.height
                val words = recognise(bmp)
                bmp.recycle()
                val f = withContext(Dispatchers.IO) {
                    runCatching { Files.copyToCache(this@ImageOcrActivity, uri) }.getOrNull()
                } ?: continue
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

    private fun decodeBounded(uri: Uri, maxDim: Int): Bitmap? {
        val bounds = android.graphics.BitmapFactory.Options().apply { inJustDecodeBounds = true }
        try {
            contentResolver.openInputStream(uri)?.use {
                android.graphics.BitmapFactory.decodeStream(it, null, bounds)
            }
        } catch (_: Exception) { return null }
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return null
        var sample = 1
        while (max(bounds.outWidth, bounds.outHeight) / (sample * 2) >= maxDim) sample *= 2
        val opts = android.graphics.BitmapFactory.Options().apply { inSampleSize = sample }
        return try {
            contentResolver.openInputStream(uri)?.use {
                android.graphics.BitmapFactory.decodeStream(it, null, opts)
            }
        } catch (_: Exception) { null }
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
