package com.kavopdf.app

import android.net.Uri
import android.os.Bundle
import androidx.recyclerview.widget.LinearLayoutManager
import com.kavopdf.app.databinding.ActivityPicklistBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.model.PickedFile
import com.kavopdf.app.ui.FileListAdapter
import com.kavopdf.app.util.Files

class MergeActivity : PdfActivity() {

    private lateinit var binding: ActivityPicklistBinding
    private val files = mutableListOf<PickedFile>()
    private lateinit var adapter: FileListAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPicklistBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        binding.toolbar.title = getString(R.string.tool_merge)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.hint.text = getString(R.string.tool_merge_desc)
        binding.actionButton.text = getString(R.string.tool_merge)
        binding.addButton.text = getString(R.string.action_choose_pdf)

        adapter = FileListAdapter(files, { pos, dir -> move(pos, dir) }, { pos -> remove(pos) })
        binding.recycler.layoutManager = LinearLayoutManager(this)
        binding.recycler.adapter = adapter

        binding.addButton.setOnClickListener { pickPdfs() }
        binding.actionButton.setOnClickListener { doMerge() }

        pickAfterEnter { pickPdfs() }
    }

    override fun onPdfsChosen(uris: List<Uri>) {
        uris.forEach { files.add(PickedFile(it, Files.displayName(this, it))) }
        adapter.notifyDataSetChanged()
        updateState()
    }

    private fun move(pos: Int, dir: Int) {
        val target = pos + dir
        if (target < 0 || target >= files.size) return
        val tmp = files[pos]; files[pos] = files[target]; files[target] = tmp
        adapter.notifyItemMoved(pos, target)
    }

    private fun remove(pos: Int) {
        files.removeAt(pos)
        adapter.notifyItemRemoved(pos)
        adapter.notifyItemRangeChanged(pos, files.size)
        updateState()
    }

    private fun updateState() {
        binding.actionButton.isEnabled = files.size >= 2
    }

    private fun doMerge() {
        if (files.size < 2) { toast(getString(R.string.msg_need_two)); return }
        val name = Files.suggestName(files.first().name, "_merged")
        runAndSave(name) { out ->
            val inputs = files.map { Files.copyToCache(this, it.uri) }
            PdfEngine.merge(inputs, out)
        }
    }
}
