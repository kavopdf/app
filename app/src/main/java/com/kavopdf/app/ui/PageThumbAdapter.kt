package com.kavopdf.app.ui

import android.graphics.Bitmap
import android.util.LruCache
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.kavopdf.app.R
import com.kavopdf.app.databinding.ItemThumbBinding
import com.kavopdf.app.model.PageEntry
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class PageThumbAdapter(
    private val items: MutableList<PageEntry>,
    private val renderer: PageRenderer,
    private val scope: CoroutineScope,
    private val onToggle: (Int) -> Unit
) : RecyclerView.Adapter<PageThumbAdapter.VH>() {

    private val cache = object : LruCache<Int, Bitmap>(40) {
        override fun sizeOf(key: Int, value: Bitmap) = 1
    }

    class VH(val b: ItemThumbBinding) : RecyclerView.ViewHolder(b.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH =
        VH(ItemThumbBinding.inflate(LayoutInflater.from(parent.context), parent, false))

    override fun getItemCount() = items.size

    override fun onBindViewHolder(holder: VH, position: Int) {
        val item = items[position]
        val ctx = holder.itemView.context
        val stroke = (if (item.selected) 3 else 1) * ctx.resources.displayMetrics.density
        holder.b.apply {
            pageNo.text = (position + 1).toString()
            thumb.rotation = item.rotation.toFloat()
            card.strokeColor = ctx.getColor(if (item.selected) R.color.brand_primary else R.color.divider)
            card.strokeWidth = stroke.toInt()
            check.visibility = if (item.selected) View.VISIBLE else View.GONE
            root.setOnClickListener { onToggle(position) }

            val cached = cache.get(item.original)
            if (cached != null) {
                thumb.setImageBitmap(cached)
            } else {
                thumb.setImageBitmap(null)
                val targetW = (ctx.resources.displayMetrics.widthPixels / 3) * 2
                scope.launch {
                    val bmp = withContext(Dispatchers.IO) {
                        runCatching { renderer.render(item.original - 1, targetW) }.getOrNull()
                    }
                    if (bmp != null) cache.put(item.original, bmp)
                    if (bmp != null && holder.bindingAdapterPosition == position) {
                        thumb.setImageBitmap(bmp)
                        thumb.alpha = 0.2f
                        thumb.animate().alpha(1f).setDuration(150).start()
                    }
                }
            }
        }
    }
}
