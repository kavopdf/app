package com.kavopdf.app

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.pdf.PdfRenderer
import android.net.Uri
import android.os.Bundle
import android.os.ParcelFileDescriptor
import android.view.View
import androidx.lifecycle.lifecycleScope
import com.kavopdf.app.databinding.ActivityRedactBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.ui.PageRenderer
import com.kavopdf.app.util.Files
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

/**
 * Permanently removes private content from a PDF.
 *
 * Marking an area only paints a box - the text would still be in the file and could
 * be copied straight out. So a redacted page is REPLACED by a flat image with the
 * marked areas painted black, and the page's original content, resources and
 * annotations are all discarded. Only pages you mark are flattened.
 */
class RedactActivity : PdfActivity() {

    private lateinit var binding: ActivityRedactBinding
    private var renderer: PageRenderer? = null
    private var pfd: ParcelFileDescriptor? = null
    private var source: File? = null
    private var sourceName: String = "document.pdf"
    private var pageCount = 0
    private var current = 0
    private val sizes = mutableListOf<FloatArray>()
    private val marks = HashMap<Int, MutableList<RectF>>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityRedactBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.redactView.imageView = binding.pageImage
        // one finger draws; two fingers zoom and pan (RedactView toggles this)
        binding.btnChoose.setOnClickListener { pickPdf() }
        binding.prevPage.setOnClickListener { goTo(current - 1) }
        binding.nextPage.setOnClickListener { goTo(current + 1) }
        binding.btnClear.setOnClickListener {
            binding.redactView.clear()
            marks.remove(current)
        }
        binding.btnRun.setOnClickListener { run() }
        pickAfterEnter { pickPdf() }
    }


    override fun onPdfChosen(uri: Uri) {
        sourceName = Files.displayName(this, uri)
        openPdf(uri) { f ->
            binding.fileName.text = sourceName
            runTask(getString(R.string.msg_processing), onDone = opened@{ res ->
                if (res == null) return@opened
                pageCount = res
                binding.btnRun.isEnabled = true
                goTo(0)
            }) {
                source = f
                marks.clear()
                sizes.clear()
                // sizes come from the renderer below, so the file is opened once
                val d = ParcelFileDescriptor.open(f, ParcelFileDescriptor.MODE_READ_ONLY)
                try { pfd?.close() } catch (_: Exception) { }
                pfd = d
                val r = PdfRenderer(d)
                renderer = PageRenderer(r)
                sizes.addAll(PageRenderer.displaySizes(r))
                r.pageCount
            }
        }
    }

    /** Remember what was marked on the page we are leaving. */
    private fun stashCurrent() {
        if (pageCount == 0) return
        val list = marks.getOrPut(current) { ArrayList() }
        list.clear()
        list.addAll(binding.redactView.rects)
    }

    private fun goTo(index: Int) {
        if (index < 0 || index >= pageCount) return
        stashCurrent()
        current = index
        binding.pageLabel.text = "${index + 1} / $pageCount"
        binding.prevPage.isEnabled = index > 0
        binding.nextPage.isEnabled = index < pageCount - 1
        binding.redactView.clear()
        binding.redactView.rects.addAll(marks[current] ?: emptyList())
        val r = renderer ?: return
        val targetW = (resources.displayMetrics.widthPixels * 1.8f).toInt().coerceAtMost(2400)
        lifecycleScope.launch {
            val bmp = withContext(Dispatchers.IO) {
                runCatching { r.render(index, targetW) }.getOrNull()
            }
            if (bmp != null && current == index) {
                binding.pageImage.setImageBitmap(bmp)
                binding.redactView.post { binding.redactView.invalidate() }
            }
        }
    }

    private fun run() {
        stashCurrent()
        val src = source ?: return toast(getString(R.string.msg_pick_file_first))
        val r = renderer ?: return
        val todo = marks.filterValues { it.isNotEmpty() }.keys.sorted()
            .filter { sizes.getOrNull(it) != null }
        if (todo.isEmpty()) return toast(getString(R.string.redact_need_boxes))

        // NOTE: runAndSave hands the work back later (the user picks a file first),
        // so nothing may be recycled before the block actually runs.
        runAndSave(Files.suggestName(sourceName, "_redacted")) { out ->
            var cur = src
            todo.forEachIndexed { i, page ->
                val size = sizes[page]
                val boxes = marks[page] ?: emptyList()
                val w = (size[0] * PRINT_DPI / 72f).toInt().coerceIn(600, 4000)
                val rendered = r.render(page, w)
                val painted = paintBlack(rendered, boxes)
                    ?: throw IllegalStateException("Could not prepare page ${page + 1}")
                val target = if (i == todo.lastIndex) out
                else Files.newFile(this@RedactActivity, "redact_step_$i.pdf")
                try {
                    PdfEngine.redactPages(cur, intArrayOf(page + 1),
                        arrayOf(painted), target)
                } finally {
                    // only the copy we made; the renderer's bitmap is left alone
                    runCatching { painted.recycle() }
                }
                cur = target
            }
            todo.size
        }
    }

    /** Paint the marked boxes solid black, with a margin so no edge can bleed.
     *  Always returns a fresh bitmap, or null if a copy could not be made. */
    private fun paintBlack(bmp: Bitmap, boxes: List<RectF>): Bitmap? {
        val out = try {
            bmp.copy(Bitmap.Config.ARGB_8888, true)
        } catch (t: Throwable) {
            null
        } ?: return null
        val c = Canvas(out)
        val p = Paint().apply {
            color = Color.BLACK
            style = Paint.Style.FILL
            isAntiAlias = false
        }
        val pad = 8f
        for (b in boxes) {
            c.drawRect(
                b.left * out.width - pad, b.top * out.height - pad,
                b.right * out.width + pad, b.bottom * out.height + pad, p
            )
        }
        return out
    }

    override fun onDestroy() {
        super.onDestroy()
        renderer?.close()
        try { pfd?.close() } catch (_: Exception) { }
    }

    private companion object {
        /** Resolution used for the flattened page. */
        /**
         * Redaction has to rasterise the page - that is what makes the removal permanent -
         * so the DPI decides what the rest of the page looks like afterwards. 300 is the
         * usual print standard and keeps text and line art crisp; the page budget in
         * PageRenderer is what keeps the memory for it in check.
         */
        const val PRINT_DPI = 300f
    }
}
