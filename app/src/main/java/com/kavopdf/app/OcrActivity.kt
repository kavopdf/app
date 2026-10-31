package com.kavopdf.app

import android.graphics.Bitmap
import android.graphics.pdf.PdfRenderer
import android.net.Uri
import android.os.Bundle
import android.os.ParcelFileDescriptor
import androidx.lifecycle.lifecycleScope
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.TextRecognizer
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import com.kavopdf.app.databinding.ActivityOcrBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.ui.PageRenderer
import com.kavopdf.app.util.Files
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.launch
import kotlin.coroutines.suspendCoroutine
import kotlinx.coroutines.withContext
import java.io.File
import kotlin.coroutines.resume

/**
 * Makes a scanned PDF searchable. Every page is rendered and read by ML Kit's
 * on-device text recogniser (bundled model: offline, no Play Services, no extra
 * permission), and the recognised words are written back as an invisible text
 * layer. The page itself is not changed at all.
 */
class OcrActivity : PdfActivity() {

    private lateinit var binding: ActivityOcrBinding
    private var renderer: PageRenderer? = null
    private var pfd: ParcelFileDescriptor? = null
    private var source: File? = null
    private var sourceName: String = "document.pdf"
    private var pageCount = 0

    private val recogniser: TextRecognizer by lazy {
        TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityOcrBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.btnChoose.setOnClickListener { pickPdf() }
        binding.btnRun.setOnClickListener { run() }
        pickAfterEnter { pickPdf() }
    }

    override fun onPdfChosen(uri: Uri) {
        sourceName = Files.displayName(this, uri)
        openPdf(uri) { f ->
            binding.fileName.text = sourceName
            runTask(getString(R.string.msg_processing), onDone = opened@{ count ->
                if (count == null || count == 0) return@opened
                pageCount = count
                binding.btnRun.isEnabled = true
            }) {
                source = f
                val d = ParcelFileDescriptor.open(f, ParcelFileDescriptor.MODE_READ_ONLY)
                try { pfd?.close() } catch (_: Exception) { }
                pfd = d
                val r = PdfRenderer(d)
                renderer = PageRenderer(r)
                r.pageCount
            }
        }
    }

    private fun run() {
        val src = source ?: return toast(getString(R.string.msg_pick_file_first))
        val r = renderer ?: return
        val pages = parsePages(binding.pagesInput.text?.toString().orEmpty())
        if (pages.isEmpty()) return toast(getString(R.string.msg_invalid_ranges))

        lifecycleScope.launch {
            busy.show(getString(R.string.ocr_working, 1, pages.size))
            val found = ArrayList<PdfEngine.PageText>()
            // Render one page ahead: the next page is drawn while ML Kit is still
            // reading the current one, which overlaps the two slowest steps. The
            // resolution is untouched, so accuracy is unchanged.
            var nextJob: Deferred<Bitmap?> = async(Dispatchers.IO) {
                runCatching { r.render(pages[0] - 1, OCR_WIDTH) }.getOrNull()
            }
            for ((i, page) in pages.withIndex()) {
                busy.update(getString(R.string.ocr_working, i + 1, pages.size))
                val bmp = nextJob.await()
                if (i + 1 < pages.size) {
                    val upcoming = pages[i + 1]
                    nextJob = async(Dispatchers.IO) {
                        runCatching { r.render(upcoming - 1, OCR_WIDTH) }.getOrNull()
                    }
                }
                if (bmp == null) continue
                // a completely empty page has nothing to recognise: skip it.
                // Deliberately strict (only truly blank pages) so no text is lost.
                if (isBlank(bmp)) { bmp.recycle(); continue }
                var w = bmp.width
                var h = bmp.height
                var words = recognise(bmp)
                bmp.recycle()
                // A page that came back almost empty usually means small print - footnotes,
                // terms, a dense table. One more pass at the largest width the page budget
                // allows, and only that page pays for it. If the second pass finds more,
                // it wins; otherwise the first result stands untouched.
                if (words.size < 6) {
                    val bigger = runCatching {
                        r.render(page - 1, (OCR_WIDTH * 1.6f).toInt())
                    }.getOrNull()
                    if (bigger != null) {
                        val again = recognise(bigger)
                        if (again.size > words.size) {
                            words = again
                            w = bigger.width
                            h = bigger.height
                        }
                        bigger.recycle()
                    }
                }
                if (words.isNotEmpty()) found.add(PdfEngine.PageText(page, w, h, words))
            }
            busy.dismiss()
            if (found.isEmpty()) {
                toast(getString(R.string.ocr_none))
                return@launch
            }
            val n = found.size
            runAndSave(Files.suggestName(sourceName, "_searchable")) { out ->
                PdfEngine.addTextLayer(src, found, out)
                n
            }
        }
    }

    /** "1-3, 5" -> [1,2,3,5]; blank means every page. Clamped to the real page count. */
    private fun parsePages(s: String): List<Int> {
        val out = ArrayList<Int>()
        s.split(',').forEach { part ->
            val p = part.trim()
            if (p.isEmpty()) return@forEach
            if (p.contains('-')) {
                val a = p.split('-')
                val f = a.getOrNull(0)?.trim()?.toIntOrNull()
                val t = a.getOrNull(1)?.trim()?.toIntOrNull()
                if (f != null && t != null && f >= 1 && t >= f) {
                    out.addAll(f..minOf(t, maxOf(1, pageCount)))
                }
            } else {
                p.toIntOrNull()?.let { if (it in 1..pageCount) out.add(it) }
            }
        }
        val cleaned = out.distinct().sorted()
        return if (cleaned.isEmpty()) (1..pageCount).toList() else cleaned
    }

    /** True only for a page with essentially no ink at all. */
    private fun isBlank(bmp: Bitmap): Boolean = try {
        val small = Bitmap.createScaledBitmap(bmp, 32, 32, true)
        val px = IntArray(32 * 32)
        small.getPixels(px, 0, 32, 0, 0, 32, 32)
        small.recycle()
        var dark = 0
        for (v in px) {
            val r = (v shr 16) and 0xFF
            val g = (v shr 8) and 0xFF
            val b = v and 0xFF
            if ((r + g + b) / 3 < 200) dark++
        }
        dark <= 1
    } catch (_: Throwable) { false }

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
                                        t,
                                        b.left.toFloat(), b.top.toFloat(),
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

    override fun onConfigurationChanged(newConfig: android.content.res.Configuration) {
        super.onConfigurationChanged(newConfig)
    }

    override fun onDestroy() {
        super.onDestroy()
        try { recogniser.close() } catch (_: Exception) { }
        renderer?.close()
        try { pfd?.close() } catch (_: Exception) { }
    }

    private companion object {
        /**
         * Render width handed to the recogniser. Higher is meaningfully more accurate
         * on small print, so pages are rendered well above screen size.
         */
        const val OCR_WIDTH = 2600
    }
}
