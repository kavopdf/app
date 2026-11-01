package com.kavopdf.app

import com.kavopdf.app.util.AppLog
import android.graphics.RectF
import android.graphics.pdf.PdfRenderer
import android.net.Uri
import android.os.Bundle
import android.os.ParcelFileDescriptor
import android.view.Menu
import android.view.MenuItem
import android.view.inputmethod.EditorInfo
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import androidx.viewpager2.widget.ViewPager2
import com.kavopdf.app.databinding.ActivityViewerBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.ui.PageRenderer
import com.kavopdf.app.ui.ViewerAdapter
import com.kavopdf.app.util.Files
import java.io.File

/** Fast, smooth, offline PDF reader with pinch-zoom, rotation and crisp zoom. */
class ViewerActivity : PdfActivity() {

    private lateinit var binding: ActivityViewerBinding
    private var renderer: PageRenderer? = null
    private var pfd: ParcelFileDescriptor? = null
    private var current: File? = null
    /** the outline, loaded once when the file opens so Contents is instant */
    private var outline: List<PdfEngine.Bookmark> = emptyList()
    /** link annotations per page, so a tap on a link opens it */
    private var links: Map<Int, List<PdfEngine.FoundLink>> = emptyMap()
    /** the line the user last picked, so Copy has something to give */
    private var adapter: ViewerAdapter? = null
    private var viewRotation = 0
    private val sizes = mutableListOf<FloatArray>()
    private var textIndex: PdfEngine.TextIndex? = null
    /** true once the link list has arrived for the open document */
    private var linksReady = false
    private var tapRetryPending = false
    private var lastMissKey: String? = null
    private var matches: List<PdfEngine.Match> = emptyList()
    private var matchIndex = -1

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityViewerBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        binding.toolbar.setNavigationOnClickListener { finish() }
        // pages scroll vertically, the way a document is read
        binding.pager.orientation = ViewPager2.ORIENTATION_VERTICAL

        wireSearch()
        val uri: Uri? = incomingUri(intent)
        if (uri != null) openUri(uri) else pickPdf()
    }

    /**
     * The PDF this screen was opened with, however it arrived.
     *
     * Tapping a PDF sends ACTION_VIEW with the file in the intent data. Sharing a PDF
     * sends ACTION_SEND with the file in EXTRA_STREAM instead, so an app that only looked
     * at intent.data would open nothing at all after being picked from the share sheet.
     * clipData is the third place a sender may put it.
     */
    private fun incomingUri(intent: android.content.Intent?): Uri? {
        intent ?: return null
        intent.data?.let { return it }
        val extra: Uri? = if (android.os.Build.VERSION.SDK_INT >= 33) {
            intent.getParcelableExtra(android.content.Intent.EXTRA_STREAM, Uri::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra(android.content.Intent.EXTRA_STREAM)
        }
        extra?.let { return it }
        val clip = intent.clipData
        if (clip != null && clip.itemCount > 0) return clip.getItemAt(0).uri
        return null
    }

    /** Opening another PDF from another app while this screen is up. */
    override fun onNewIntent(intent: android.content.Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        incomingUri(intent)?.let { openUri(it) }
    }

    override fun onPdfChosen(uri: Uri) = openUri(uri)

    private fun openUri(uri: Uri) {
        openPdf(uri) { f ->
            current = f
            binding.toolbar.title = Files.displayName(this, uri)
            show(f)
        }
    }

    private fun show(file: File) {
        try {
            val descriptor = ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
            pfd = descriptor
            val raw = PdfRenderer(descriptor)
            val pr = PageRenderer(raw)
            renderer = pr
            textIndex = null
            pagesHint = pr.pageCount
            sizes.clear()   // filled in the background below; the page shows at once
            val adapter = ViewerAdapter(
                pr.pageCount, pr, lifecycleScope,
                rotationProvider = { viewRotation },
                baseWidthProvider = { (resources.displayMetrics.widthPixels * BASE_FACTOR).toInt() },
                onZoom = { zoomed -> binding.pager.isUserInputEnabled = !zoomed },
                onZoomSettled = { position, z -> upgrade(position, z) },
                onTap = { position, fx, fy -> onPageTap(position, fx, fy) }
            )
            this.adapter = adapter
            // Render the page either side before the user swipes to it. Without this a
            // swipe always landed on an empty frame while the page was being drawn, which
            // is the one place the reader felt slow on every device.
            binding.pager.offscreenPageLimit = 1
            binding.pager.adapter = adapter
            // The pager's inner RecyclerView animates item changes, which shows up as a
            // small stutter when a page is rebound mid-swipe. Nothing here needs an item
            // animation, and caching one extra view keeps the next page ready.
            (binding.pager.getChildAt(0) as? androidx.recyclerview.widget.RecyclerView)?.apply {
                itemAnimator = null
                setItemViewCacheSize(3)
            }
            binding.pager.registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
                override fun onPageSelected(position: Int) {
                    updateIndicator(position, pr.pageCount)
                }
            })
            updateIndicator(0, pr.pageCount)
            outline = emptyList()
            // All three are CPU-bound: opening and parsing the same document. Run
            // side by side they simply share the CPU and each takes three times as
            // long, which is exactly what the log showed (three ~5s entries at the
            // same second). One after another they are three times faster overall.
            links = emptyMap()
            linksReady = false
            lifecycleScope.launch {
                val sizesOut = com.kavopdf.app.util.CrashGuard.io(
                    this@ViewerActivity, "Reader: page sizes", pagesHint
                ) {
                    // Sizes come from the renderer that is already open. Asking pdfbox
                    // opened the whole document a second time - that was the double open
                    // the other tools no longer have.
                    runCatching { PageRenderer.displaySizes(raw) }.getOrDefault(emptyList())
                }
                if (current !== file) return@launch
                sizes.clear(); sizes.addAll(sizesOut)

                // One pass for both. Asking separately loaded the whole document twice,
                // and on a big file that was the slowest part of opening it.
                val both = com.kavopdf.app.util.CrashGuard.io(
                    this@ViewerActivity, "Reader: outline and links", pagesHint
                ) { runCatching { PdfEngine.outlineAndLinks(file) }.getOrNull() }
                if (current !== file) return@launch
                outline = both?.bookmarks ?: emptyList()
                links = both?.links ?: emptyMap()
                linksReady = true
            }
        } catch (t: Throwable) {
            AppLog.problem(applicationContext, "Open", t)
            toast(getString(R.string.msg_could_not_open))
        }
    }

    /** Re-render the current page at a resolution matching how far the user zoomed in. */
    private fun upgrade(position: Int, zoom: Float) {
        val factor = zoom.coerceIn(BASE_FACTOR, MAX_FACTOR)
        val width = (resources.displayMetrics.widthPixels * factor).toInt().coerceAtMost(MAX_WIDTH)
        adapter?.upgradePage(position, width)
    }

    override fun onConfigurationChanged(newConfig: android.content.res.Configuration) {
        super.onConfigurationChanged(newConfig)
        adapter?.invalidateAll()
    }

    /** One tap turns the page a quarter turn clockwise; the next tap puts it back. */
    private fun rotate() {
        viewRotation = if (viewRotation == 0) 90 else 0
        adapter?.invalidateAll()
    }

    private fun wireSearch() {
        binding.searchClose.setOnClickListener { closeSearch() }
        binding.searchPrev.setOnClickListener { stepMatch(-1) }
        binding.searchNext.setOnClickListener { stepMatch(1) }
        binding.searchInput.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH) { runSearch(); true } else false
        }
    }

    private fun openSearch() {
        binding.searchBar.visibility = android.view.View.VISIBLE
        binding.searchInput.requestFocus()
        val imm = getSystemService(android.content.Context.INPUT_METHOD_SERVICE)
                as android.view.inputmethod.InputMethodManager
        imm.showSoftInput(binding.searchInput, android.view.inputmethod.InputMethodManager.SHOW_IMPLICIT)
    }

    private fun closeSearch() {
        binding.searchBar.visibility = android.view.View.GONE
        binding.searchInput.setText("")
        matches = emptyList()
        matchIndex = -1
        binding.searchCount.text = ""
        adapter?.setHighlight(-1, null)
    }

    private fun runSearch() {
        val f = current ?: return
        val q = binding.searchInput.text?.toString().orEmpty().trim()
        if (q.isEmpty()) {
            matches = emptyList(); matchIndex = -1; binding.searchCount.text = ""
            adapter?.setHighlight(-1, null)
            return
        }
        val cached = textIndex
        if (cached != null) {
            applyMatches(PdfEngine.searchIndex(cached, q, false))
            return
        }
        runTask(getString(R.string.search_progress), onDone = found@{ list ->
            if (list == null) return@found
            applyMatches(list)
        }) {
            val built = PdfEngine.indexText(f)
            textIndex = built
            PdfEngine.searchIndex(built, q, false)
        }
    }

    private fun applyMatches(list: List<PdfEngine.Match>) {
        matches = list
        matchIndex = if (list.isEmpty()) -1 else 0
        updateSearchCount()
        showMatch()
    }

    /** Long press on a page: offer to copy the word or the whole page. */
    /**
     * Long press the page: the page's text opens in Android's own selectable view.
     * Real handles, real Copy / Select all - exactly like any other app.
     *
     * Nothing is guessed and nothing is drawn over the page, so nothing can drift
     * when the page is zoomed. A page with no text layer does nothing at all:
     * that PDF is a picture and the user can see that for themselves.
     */
    private fun stepMatch(delta: Int) {
        if (matches.isEmpty()) return
        matchIndex = ((matchIndex + delta) % matches.size + matches.size) % matches.size
        updateSearchCount()
        showMatch()
    }

    private fun updateSearchCount() {
        binding.searchCount.text = if (matches.isEmpty()) getString(R.string.search_none)
        else getString(R.string.search_count, matchIndex + 1, matches.size)
    }

    private fun showMatch() {
        val m = matches.getOrNull(matchIndex) ?: run { adapter?.setHighlight(-1, null); return }
        val size = sizes.getOrNull(m.page - 1)
        if (size == null || size[0] <= 0f || size[1] <= 0f) return
        val norm = RectF(
            m.x / size[0], m.y / size[1],
            (m.x + m.w) / size[0], (m.y + m.h) / size[1]
        )
        adapter?.setHighlight(m.page - 1, norm)
        if (binding.pager.currentItem != m.page - 1) binding.pager.setCurrentItem(m.page - 1, true)
    }

    private fun updateIndicator(position: Int, count: Int) {
        binding.pageIndicator.text = "${position + 1} / $count"
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menu.add(0, 1, 0, R.string.action_rotate)
            .setIcon(R.drawable.ic_rotate)
            .setShowAsAction(MenuItem.SHOW_AS_ACTION_ALWAYS)
        menu.add(0, 3, 0, R.string.action_search)
            .setIcon(R.drawable.ic_search)
            .setShowAsAction(MenuItem.SHOW_AS_ACTION_ALWAYS)
        menu.add(0, 4, 0, R.string.action_contents)
            .setIcon(R.drawable.ic_contents)
            .setShowAsAction(MenuItem.SHOW_AS_ACTION_ALWAYS)
        menu.add(0, 2, 1, R.string.action_share)
            .setIcon(R.drawable.ic_share)
            .setShowAsAction(MenuItem.SHOW_AS_ACTION_ALWAYS)
        return true
    }

    /**
     * The PDF's own outline, so a bookmark made with the Bookmarks tool is visible
     * here too. Tapping an entry jumps to its page.
     */
    /**
     * A tap inside the page: if it lands on a link annotation, open it in the
     * browser. Links in the file were dead in the reader before - the page is
     * drawn as a bitmap, so nothing knew where the links were.
     */
    private fun onPageTap(position: Int, fx: Float, fy: Float) {
        // The page size and the link list arrive in the background. If a tap lands
        // before they are ready, wait for them and then honour that same tap -
        // otherwise the first tap on a freshly opened document silently does nothing.
        val size = sizes.getOrNull(position)
        val pw = size?.getOrElse(0) { 0f } ?: 0f
        val ph = size?.getOrElse(1) { 0f } ?: 0f
        if (pw <= 0f || ph <= 0f || !linksReady) {
            if (tapRetryPending) return
            tapRetryPending = true
            val f = current ?: return
            lifecycleScope.launch {
                try {
                    if (sizes.getOrNull(position)?.getOrElse(0) { 0f }?.let { it > 0f } != true) {
                        val list = com.kavopdf.app.util.CrashGuard.io(
                            this@ViewerActivity, "Reader: page sizes", pagesHint
                        ) { runCatching { PdfEngine.pageDisplaySizes(f) }.getOrDefault(emptyList()) }
                        if (current === f) { sizes.clear(); sizes.addAll(list) }
                    }
                    if (!linksReady) {
                        val map = com.kavopdf.app.util.CrashGuard.io(
                            this@ViewerActivity, "Reader: links", pagesHint
                        ) { runCatching { PdfEngine.allPageLinks(f) }.getOrDefault(emptyMap()) }
                        if (current === f) { links = map; linksReady = true }
                    }
                } finally {
                    tapRetryPending = false
                }
                if (current === f) onPageTap(position, fx, fy)
            }
            return
        }

        val pageLinks = links[position + 1]
        if (pageLinks.isNullOrEmpty()) return

        // generous: a fingertip is wide, and a link should open when it looks tapped
        val tolerance = 0.045f
        var best: PdfEngine.FoundLink? = null
        var bestScore = Float.MAX_VALUE
        for (l in pageLinks) {
            val lx = l.x / pw
            val ly = l.y / ph
            val lw = l.w / pw
            val lh = l.h / ph
            if (fx >= lx - tolerance && fx <= lx + lw + tolerance &&
                fy >= ly - tolerance && fy <= ly + lh + tolerance
            ) {
                // distance from the middle of the link, so overlapping links resolve
                val dx = fx - (lx + lw / 2f)
                val dy = fy - (ly + lh / 2f)
                val score = dx * dx + dy * dy
                if (score < bestScore) { bestScore = score; best = l }
            }
        }
        best?.let { openUrl(it.url); return }
        // a page with links was tapped and nothing matched: say so, once, with the
        // numbers needed to see why - and stay silent on every other tap
        val key = "miss|$position|$fx|$fy"
        if (lastMissKey != key) {
            lastMissKey = key
            com.kavopdf.app.util.AppLog.record(
                this, "Link tap missed",
                "tap=${"%.3f".format(fx)},${"%.3f".format(fy)} pageSize=${pw.toInt()}x${ph.toInt()} " +
                        "links=" + pageLinks.joinToString("; ") {
                            "${"%.3f".format(it.x / pw)},${"%.3f".format(it.y / ph)}," +
                                    "${"%.3f".format(it.w / pw)},${"%.3f".format(it.h / ph)}"
                        },
                false
            )
        }
    }

    private fun openUrl(url: String) {
        val raw = url.trim()
        val target = if (raw.contains("://")) raw else "https://$raw"
        val uri = runCatching { Uri.parse(target) }.getOrNull()
        val scheme = uri?.scheme?.lowercase()
        // A PDF is untrusted input, and a link inside one is just as untrusted as the file
        // itself. Its /Link annotation can carry anything - intent://, file://,
        // content://, javascript: - and launching that from here would let a document make
        // this app start something on its behalf, or hand it a private file path. Only the
        // four schemes a document has any business carrying are allowed through; the QR
        // scanner has always been this strict, the PDF path was not.
        if (uri == null || scheme !in LINK_SCHEMES) {
            toast(getString(R.string.msg_failed, "this link cannot be opened"))
            com.kavopdf.app.util.AppLog.record(
                this, "Link blocked", (scheme ?: "no scheme") + ": " + target.take(120), false
            )
            return
        }
        try {
            startActivity(android.content.Intent(android.content.Intent.ACTION_VIEW, uri))
        } catch (t: Throwable) {
            toast(getString(R.string.msg_failed, "no app can open that link"))
        }
    }

    private fun openContents() {
        if (current == null) return
        val marks = outline
        if (marks.isEmpty()) {
            toast(getString(R.string.msg_no_outline))
            return
        }
        val labels = marks.map { "${it.title}   \u00b7   ${it.page}" }.toTypedArray()
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle(R.string.action_contents)
            .setItems(labels) { _, which ->
                val last = ((adapter?.itemCount ?: 1) - 1).coerceAtLeast(0)
                binding.pager.setCurrentItem((marks[which].page - 1).coerceIn(0, last), true)
            }
            .setNegativeButton(android.R.string.cancel, null)
            .show()
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            1 -> { rotate(); return true }
            3 -> { openSearch(); return true }
            2 -> { current?.let { Files.share(this, it, "application/pdf") }; return true }
            4 -> { openContents(); return true }
        }
        return super.onOptionsItemSelected(item)
    }

    override fun onDestroy() {
        super.onDestroy()
        renderer?.close()
        try { pfd?.close() } catch (_: Exception) { }
    }

    companion object {
        /** The only schemes a link inside a document may use. */
        private val LINK_SCHEMES = setOf("http", "https", "mailto", "tel")
        private const val BASE_FACTOR = 2.0f
        private const val MAX_FACTOR = 4.0f
        private const val MAX_WIDTH = 2800
    }
}
