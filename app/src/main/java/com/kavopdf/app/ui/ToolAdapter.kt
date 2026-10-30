package com.kavopdf.app.ui

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.annotation.StringRes
import androidx.recyclerview.widget.RecyclerView
import com.kavopdf.app.databinding.ItemHeaderBinding
import com.kavopdf.app.databinding.ItemToolBinding
import com.kavopdf.app.model.Action
import com.kavopdf.app.model.ToolItem

sealed class HomeRow {
    data class Header(@StringRes val title: Int) : HomeRow()
    data class Tool(val item: ToolItem) : HomeRow()
}

class ToolAdapter(
    val rows: List<HomeRow>,
    /** True while the list is moving. We never animate mid-scroll, or cards pop
     *  in at odd moments and the scroll looks like it is stuttering. */
    private val isScrolling: () -> Boolean = { false },
    private val onClick: (Action) -> Unit
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    private val animated = HashSet<Int>()

    override fun getItemViewType(position: Int) = if (rows[position] is HomeRow.Header) 0 else 1

    override fun getItemCount() = rows.size

    class HeaderVH(val b: ItemHeaderBinding) : RecyclerView.ViewHolder(b.root)
    class ToolVH(val b: ItemToolBinding) : RecyclerView.ViewHolder(b.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        val inflater = LayoutInflater.from(parent.context)
        return if (viewType == 0) {
            HeaderVH(ItemHeaderBinding.inflate(inflater, parent, false))
        } else {
            ToolVH(ItemToolBinding.inflate(inflater, parent, false))
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (val row = rows[position]) {
            is HomeRow.Header -> (holder as HeaderVH).b.headerText.setText(row.title)
            is HomeRow.Tool -> (holder as ToolVH).b.apply {
                toolIcon.setImageResource(row.item.icon)
                toolTitle.setText(row.item.title)
                toolDesc.setText(row.item.desc)
                root.setOnClickListener { onClick(row.item.action) }
                // light stagger-in, but only on a still screen
                if (!isScrolling() && animated.add(position)) {
                    root.alpha = 0f
                    root.translationY = 24f
                    root.animate()
                        .alpha(1f)
                        .translationY(0f)
                        .setStartDelay((position % 12) * 22L)
                        .setDuration(240)
                        .start()
                }
            }
        }
    }
}
