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
        // Zooming in re-renders the page sharper, exactly like the annotate and reader
        // screens do. Without this the page was drawn once at 1.8x and then stretched,
        // which is why a redaction page looked softer than the same page anywhere else.
        binding.pageImage.onZoomSettled = { z -> upgradeCurrent(z) }
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
                // A new document starts with no page rendered yet, so a stale width from
                // the previous one cannot make the zoom upgrade skip a re-render.
                renderedWidth.clear()
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
        val targetW = baseRenderWidth()
        renderedWidth[index] = targetW
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

    /** Resolution each page was last rendered at, so zooming only ever goes sharper. */
    private val renderedWidth = HashMap<Int, Int>()

    /**
     * The width a page is drawn at before any zoom. Same rule as the annotate and reader
     * screens - twice the screen width, capped - so a page looks identical in every tool.
     */
    private fun baseRenderWidth() =
        (resources.displayMetrics.widthPixels * 2.0f).toInt().coerceAtMost(MAX_WIDTH)

    /** Zooming in re-renders the page sharper without disturbing the zoom. */
    private fun upgradeCurrent(zoom: Float) {
        val r = renderer ?: return
        val index = current
        val target = (resources.displayMetrics.widthPixels * zoom.coerceIn(2f, 4f))
            .toInt().coerceAtMost(MAX_WIDTH)
        if ((renderedWidth[index] ?: 0) >= target) return
        renderedWidth[index] = target
        lifecycleScope.launch {
            val bmp = withContext(Dispatchers.IO) {
                runCatching { r.render(index, target) }.getOrNull()
            }
            if (bmp != null && current == index) {
                // Keeps the zoom and pan where the user put them; a plain setImageBitmap
                // would snap the page back to fit.
                binding.pageImage.setImageBitmapPreservingTransform(bmp)
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
            // One open and one save for the whole document.
            //
            // This used to call the engine once per page, so every redacted page reloaded
            // and rewrote the entire file: twenty redactions on a two-hundred page
            // document meant twenty full loads and twenty full saves, plus a temp copy per
            // step. The engine still asks for one painted page at a time, so only a single
            // full-page bitmap exists at any moment - the memory this loop protected is
            // still protected.
            val pages = todo.map { it + 1 }.toIntArray()
            PdfEngine.redactPagesLazy(src, pages, { page ->
                val index = page - 1
                val size = sizes[index]
                val boxes = marks[index] ?: emptyList()
                val w = (size[0] * PRINT_DPI / 72f).toInt().coerceIn(600, 4000)
                val rendered = r.render(index, w)
                val painted = try {
                    paintBlack(rendered, boxes)
                } finally {
                    // a fresh bitmap from the renderer; the painted copy is independent
                    runCatching { rendered.recycle() }
                }
                painted ?: throw IllegalStateException("Could not prepare page $page")
            }, out)
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

        /** Same ceiling as the annotate and reader screens, so no tool is the soft one. */
        const val MAX_WIDTH = 2800
    }
}
