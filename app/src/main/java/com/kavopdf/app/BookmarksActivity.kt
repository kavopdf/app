package com.kavopdf.app

import android.net.Uri
import android.os.Bundle
import android.os.ParcelFileDescriptor
import android.text.InputType
import android.view.View
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import androidx.lifecycle.lifecycleScope
import com.kavopdf.app.databinding.ActivityBookmarksBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.util.Files
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

/**
 * Read and write a PDF's outline.
 *
 * What is saved here is the real PDF outline, so every reader - not just this one -
 * shows the entries in its sidebar.
 */
class BookmarksActivity : PdfActivity() {

    private lateinit var binding: ActivityBookmarksBinding
    private var pfd: ParcelFileDescriptor? = null
    private var source: File? = null
    private var sourceName = "document.pdf"
    private var pageCount = 0

    private class Row(val box: LinearLayout, val title: EditText, val page: EditText)

    private val rows = ArrayList<Row>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityBookmarksBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.btnChoose.setOnClickListener { pickPdf() }
        binding.btnAdd.setOnClickListener { addRow("", rows.size + 1) }
        binding.btnSave.setOnClickListener { save() }
        render()
        pickAfterEnter { pickPdf() }
    }

    override fun onDestroy() {
        super.onDestroy()
        runCatching { pfd?.close() }
        pfd = null
    }

    override fun onPdfChosen(uri: Uri) {
        lifecycleScope.launch {
            val f = withContext(Dispatchers.IO) { runCatching { Files.copyToCache(this@BookmarksActivity, uri) }.getOrNull() }
            if (f == null) return@launch toast(getString(R.string.msg_failed, "copy"))
            source = f
            sourceName = Files.displayName(this@BookmarksActivity, uri)
            binding.fileName.text = sourceName
            loadExisting(f)
        }
    }

    private fun loadExisting(f: File) {
        runTask(getString(R.string.msg_processing), onDone = loaded@{ info ->
            if (info == null) return@loaded
            pageCount = info.first
            rows.clear()
            binding.list.removeAllViews()
            for (b in info.second) addRow(b.title, b.page)
            if (info.second.isEmpty()) addRow("", 1)
            binding.btnSave.isEnabled = true
            binding.info.text = getString(R.string.bookmarks_info) + "\n" +
                getString(R.string.bookmark_page) + ": 1 – $pageCount"
        }) {
            val n = PdfEngine.pageCount(f, "")
            n to PdfEngine.bookmarks(f)
        }
    }

    private fun addRow(title: String, page: Int) {
        if (pageCount > 0 && page > pageCount) return
        val box = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(dp(8), dp(8), dp(8), dp(8))
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
        val t = EditText(this).apply {
            hint = getString(R.string.bookmark_title)
            setText(title)
            inputType = InputType.TYPE_CLASS_TEXT
            background = getDrawable(R.drawable.bg_field_pill)
            setPadding(dp(18), dp(14), dp(18), dp(14))
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        val pg = EditText(this).apply {
            hint = getString(R.string.bookmark_page)
            setText(page.toString())
            inputType = InputType.TYPE_CLASS_NUMBER
            background = getDrawable(R.drawable.bg_field_pill)
            setPadding(dp(18), dp(14), dp(18), dp(14))
            layoutParams = LinearLayout.LayoutParams(dp(96), LinearLayout.LayoutParams.WRAP_CONTENT)
                .also { it.marginStart = dp(10) }
        }
        val del = TextView(this).apply {
            text = "\u2715"
            contentDescription = getString(R.string.bookmark_remove)
            setTextColor(getColor(R.color.danger))
            textSize = 18f
            setPadding(dp(12), dp(10), dp(12), dp(10))
            setOnClickListener { removeRow(box) }
        }
        box.addView(t); box.addView(pg); box.addView(del)
        rows.add(Row(box, t, pg))
        binding.list.addView(box)
        if (rows.size == 1) binding.list.post { t.requestFocus() }
    }

    private fun removeRow(box: View) {
        val r = rows.firstOrNull { it.box === box } ?: return
        rows.remove(r)
        binding.list.removeView(box)
    }

    private fun render() {
        binding.btnSave.isEnabled = source != null
    }

    private fun save() {
        val src = source ?: return toast(getString(R.string.msg_pick_file_first))
        val marks = ArrayList<PdfEngine.Bookmark>()
        for (r in rows) {
            val title = r.title.text?.toString()?.trim().orEmpty()
            val page = r.page.text?.toString()?.trim()?.toIntOrNull() ?: 0
            if (title.isEmpty() && page <= 0) continue          // skip blank rows
            marks.add(PdfEngine.Bookmark(title.ifEmpty { "Page $page" }, page.coerceIn(1, maxOf(1, pageCount))))
        }
        if (marks.isEmpty()) return toast(getString(R.string.msg_need_bookmark))
        runAndSave(Files.suggestName(sourceName, "_bookmarks")) { out ->
            PdfEngine.setBookmarks(src, marks, out)
        }
    }

    private fun dp(v: Int): Int = (v * resources.displayMetrics.density).toInt()
}
