package com.kavopdf.app

import android.graphics.pdf.PdfRenderer
import android.net.Uri
import android.os.Bundle
import android.os.ParcelFileDescriptor
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.ItemTouchHelper
import androidx.recyclerview.widget.RecyclerView
import com.kavopdf.app.databinding.ActivityPagesBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.model.PageEntry
import com.kavopdf.app.ui.PageRenderer
import com.kavopdf.app.ui.PageThumbAdapter
import com.kavopdf.app.util.Files
import java.io.File
import java.util.Collections

/** Visual page organiser: drag to reorder, plus rotate, delete and extract. */
class PagesActivity : PdfActivity() {

    private lateinit var binding: ActivityPagesBinding
    private var renderer: PageRenderer? = null
    private var pfd: ParcelFileDescriptor? = null
    private var source: File? = null
    private var sourceName: String = "document.pdf"

    private val items = mutableListOf<PageEntry>()
    private val history = ArrayDeque<List<PageEntry>>()
    private var adapter: PageThumbAdapter? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPagesBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        binding.toolbar.setNavigationOnClickListener { finish() }

        binding.recycler.layoutManager = GridLayoutManager(this, 3)
        binding.recycler.setHasFixedSize(false)

        binding.btnRotate.setOnClickListener { rotateSelected() }
        binding.btnDelete.setOnClickListener { deleteSelected() }
        binding.btnSelectAll.setOnClickListener { toggleSelectAll() }
        binding.btnUndo.setOnClickListener { undo() }
        binding.btnSave.setOnClickListener { save() }
        binding.btnExtract.setOnClickListener { extract() }

        attachDragToReorder()
        pickAfterEnter { pickPdf() }
    }

    private fun attachDragToReorder() {
        val callback = object : ItemTouchHelper.SimpleCallback(
            ItemTouchHelper.UP or ItemTouchHelper.DOWN or ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT, 0
        ) {
            override fun onMove(
                rv: RecyclerView, vh: RecyclerView.ViewHolder, target: RecyclerView.ViewHolder
            ): Boolean {
                val from = vh.bindingAdapterPosition
                val to = target.bindingAdapterPosition
                if (from == RecyclerView.NO_POSITION || to == RecyclerView.NO_POSITION) return false
                if (from == to) return true
                Collections.swap(items, from, to)
                adapter?.notifyItemMoved(from, to)
                return true
            }

            override fun onSwiped(vh: RecyclerView.ViewHolder, direction: Int) { }

            override fun isLongPressDragEnabled() = true

            override fun onSelectedChanged(vh: RecyclerView.ViewHolder?, actionState: Int) {
                super.onSelectedChanged(vh, actionState)
                if (actionState == ItemTouchHelper.ACTION_STATE_DRAG) snapshot()
            }

            override fun clearView(rv: RecyclerView, vh: RecyclerView.ViewHolder) {
                super.clearView(rv, vh)
                updateInfo()
            }
        }
        ItemTouchHelper(callback).attachToRecyclerView(binding.recycler)
    }

    override fun onPdfChosen(uri: Uri) {
        sourceName = Files.displayName(this, uri)
        openPdf(uri) { f ->
            runTask(getString(R.string.msg_processing), onDone = loaded@{ count ->
                if (count == null) return@loaded
                items.clear()
                for (i in 1..count) items.add(PageEntry(i))
                val pr = renderer ?: return@loaded
                adapter = PageThumbAdapter(items, pr, lifecycleScope) { pos -> toggle(pos) }
                binding.recycler.adapter = adapter
                updateInfo()
            }) {
                source = f
                val d = ParcelFileDescriptor.open(f, ParcelFileDescriptor.MODE_READ_ONLY)
                pfd = d
                val r = PdfRenderer(d)
                renderer = PageRenderer(r)
                r.pageCount
            }
        }
    }

    private fun snapshot() {
        history.addLast(items.map { it.copy() })
        if (history.size > 30) history.removeFirst()
    }

    private fun undo() {
        val prev = history.removeLastOrNull() ?: return
        items.clear()
        items.addAll(prev)
        refresh()
    }

    private fun toggle(pos: Int) {
        if (pos !in items.indices) return
        items[pos].selected = !items[pos].selected
        adapter?.notifyItemChanged(pos)
        updateInfo()
    }

    private fun toggleSelectAll() {
        val allSelected = items.isNotEmpty() && items.all { it.selected }
        items.forEach { it.selected = !allSelected }
        refresh()
    }

    private fun rotateSelected() {
        val sel = items.filter { it.selected }
        if (sel.isEmpty()) { toast(getString(R.string.msg_need_selection)); return }
        snapshot()
        sel.forEach { it.rotation = (it.rotation + 90) % 360 }
        refresh()
    }

    private fun deleteSelected() {
        val sel = items.filter { it.selected }
        if (sel.isEmpty()) { toast(getString(R.string.msg_need_selection)); return }
        if (sel.size >= items.size) { toast(getString(R.string.msg_keep_one)); return }
        snapshot()
        items.removeAll { it.selected }
        refresh()
    }

    private fun save() {
        val src = source ?: return toast(getString(R.string.msg_pick_file_first))
        val order = items.map { it.original }
        val rots = items.map { it.rotation }
        runAndSave(Files.suggestName(sourceName, "_organized")) { out ->
            PdfEngine.rebuild(src, order, rots, out)
        }
    }

    private fun extract() {
        val src = source ?: return toast(getString(R.string.msg_pick_file_first))
        val selected = items.filter { it.selected }.map { it.original }
        if (selected.isEmpty()) { toast(getString(R.string.msg_need_selection)); return }
        runAndSave(Files.suggestName(sourceName, "_extract")) { out ->
            PdfEngine.keepPages(src, selected, out)
        }
    }

    private fun refresh() {
        adapter?.notifyDataSetChanged()
        updateInfo()
    }

    private fun updateInfo() {
        val sel = items.count { it.selected }
        binding.info.text = getString(R.string.label_pages, items.size) + "   •   " +
                getString(R.string.label_selected, sel)
        binding.btnSave.isEnabled = items.isNotEmpty()
        binding.btnExtract.isEnabled = sel > 0
    }

    override fun onDestroy() {
        super.onDestroy()
        renderer?.close()
        try { pfd?.close() } catch (_: Exception) { }
    }
}
