package com.kavopdf.app.ui

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.kavopdf.app.databinding.ItemFileRowBinding
import com.kavopdf.app.model.PickedFile

class FileListAdapter(
    private val items: MutableList<PickedFile>,
    private val onMove: (Int, Int) -> Unit,
    private val onRemove: (Int) -> Unit
) : RecyclerView.Adapter<FileListAdapter.VH>() {

    class VH(val b: ItemFileRowBinding) : RecyclerView.ViewHolder(b.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH =
        VH(ItemFileRowBinding.inflate(LayoutInflater.from(parent.context), parent, false))

    override fun getItemCount() = items.size

    override fun onBindViewHolder(holder: VH, position: Int) {
        val item = items[position]
        holder.b.apply {
            fileName.text = item.name
            btnUp.isEnabled = position > 0
            btnDown.isEnabled = position < items.size - 1
            btnUp.setOnClickListener { onMove(position, -1) }
            btnDown.setOnClickListener { onMove(position, 1) }
            btnRemove.setOnClickListener { onRemove(position) }
        }
    }
}
