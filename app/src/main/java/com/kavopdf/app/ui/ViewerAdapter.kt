package com.kavopdf.app.ui

import com.kavopdf.app.R

import android.graphics.Bitmap
import android.graphics.RectF
import android.util.LruCache
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.kavopdf.app.databinding.ItemPageBinding
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Pages of the reader. Bitmaps are cached by size (memory stays bounded no matter how
 * large the document is), and zooming re-renders the current page at higher resolution
 * and swaps it in **without** rebinding, so the zoom and pan are never lost.
 */
class ViewerAdapter(
    private val pageCount: Int,
    private val renderer: PageRenderer,
    private val scope: CoroutineScope,
    private val rotationProvider: () -> Int,
    private val baseWidthProvider: () -> Int,
    private val onZoom: (Boolean) -> Unit,
    private val onZoomSettled: (Int, Float) -> Unit,
    /** Called on a long press with the page and the point as a fraction of it. */
    private val onTap: (Int, Float, Float) -> Unit = { _, _, _ -> }
) : RecyclerView.Adapter<ViewerAdapter.VH>() {

    /** Which rotation each cached bitmap was rendered at. */
    private val cacheRotation = HashMap<Int, Int>()

    private val cache = object : LruCache<Int, Bitmap>(PageRenderer.cacheBytes()) {
        override fun sizeOf(key: Int, value: Bitmap) = value.byteCount
    }
    private val renderedWidth = HashMap<Int, Int>()
    private val inFlight = HashSet<Int>()
    private val holders = HashMap<Int, VH>()
    private val highlights = HashMap<Int, RectF>()

    class VH(val b: ItemPageBinding) : RecyclerView.ViewHolder(b.root) {
        var boundPosition = -1
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH =
        VH(ItemPageBinding.inflate(LayoutInflater.from(parent.context), parent, false))

    override fun getItemCount() = pageCount

    override fun onBindViewHolder(holder: VH, position: Int) {
        val iv = holder.b.pageImage
        holder.b.highlight.imageView = iv
        holder.b.highlight.norm = highlights[position]
        iv.onZoomChanged = { z ->
            // keep the selection glued to its text while zooming
            holder.b.highlight.invalidate()
            onZoom(z)
        }
        iv.onZoomSettled = { z -> holder.b.highlight.invalidate(); onZoomSettled(position, z) }
        // Taps must be detected for links to open. This lived in the block that was
        // removed along with the old copy/paste code, which silently killed every
        // link tap - the reader simply never told the screen that a page was tapped.
        val tapDetector = android.view.GestureDetector(iv.context,
            object : android.view.GestureDetector.SimpleOnGestureListener() {
                override fun onSingleTapConfirmed(e: android.view.MotionEvent): Boolean {
                    val d = iv.drawable ?: return false
                    if (d.intrinsicWidth <= 0 || d.intrinsicHeight <= 0) return false
                    val m = android.graphics.Matrix()
                    iv.imageMatrix.invert(m)
                    val pts = floatArrayOf(e.x, e.y)
                    m.mapPoints(pts)
                    onTap(
                        position,
                        (pts[0] / d.intrinsicWidth).coerceIn(0f, 1f),
                        (pts[1] / d.intrinsicHeight).coerceIn(0f, 1f)
                    )
                    return true
                }
            })
        iv.setOnTouchListener { _, ev -> tapDetector.onTouchEvent(ev); false }

        val samePage = holder.boundPosition == position
        holder.boundPosition = position
        holders[position] = holder

        val rot = rotationProvider()
        val cached = cache.get(position)
        if (cached != null && cacheRotation[position] == rot) {
            if (samePage) iv.setImageBitmapPreservingTransform(cached)
            else iv.setImageBitmap(cached)
            return
        }
        // never blank the page: whatever is there stays until the rotated bitmap
        // arrives, so rotating cannot flash black
        renderInto(position, baseWidthProvider()) { bmp ->
            if (bmp == null) return@renderInto
            cache.put(position, bmp)
            cacheRotation[position] = rotationProvider()
            if (holder.boundPosition == position) {
                iv.setImageBitmap(bmp)
                iv.alpha = 0.3f
                iv.animate().alpha(1f).setDuration(150).start()
            }
        }
    }

    override fun onViewRecycled(holder: VH) {
        if (holder.boundPosition >= 0) holders.remove(holder.boundPosition)
        holder.b.highlight.norm = null
        holder.boundPosition = -1
        // do not blank the page: recycling happens on every rotate, and blanking
        // here is exactly what made the screen flash black
    }

    /** Re-render a page at a higher resolution and swap it in without losing the zoom. */
    fun upgradePage(position: Int, targetWidth: Int) {
        val rendered = renderedWidth[position] ?: 0
        if (rendered >= targetWidth) return
        if (!inFlight.add(position)) return
        renderInto(position, targetWidth) { bmp ->
            inFlight.remove(position)
            if (bmp != null) {
                cache.put(position, bmp)
            cacheRotation[position] = rotationProvider()
                renderedWidth[position] = targetWidth
                val h = holders[position]
                if (h != null && h.boundPosition == position) {
                    h.b.pageImage.setImageBitmapPreservingTransform(bmp)
                }
            }
        }
    }

    /** Show (or clear) the search highlight for one page. */
    fun setHighlight(position: Int, norm: RectF?) {
        if (position < 0) {
            highlights.clear()
            holders.values.forEach { it.b.highlight.norm = null }
            return
        }
        if (norm == null) highlights.remove(position) else highlights.put(position, norm)
        holders[position]?.let {
            if (it.boundPosition == position) it.b.highlight.norm = norm
        }
    }

    fun invalidateAll() {
        // Deliberately keep the cached bitmaps: evicting them blanked every page
        // for a moment, which read as a black flash on every rotate. The stale
        // bitmap stays on screen until its replacement is rendered.
        renderedWidth.clear()
        inFlight.clear()
        // Re-render the pages that are actually on screen, in place. Calling
        // notifyDataSetChanged() recycled every holder, and that rebind is exactly
        // what made rotating feel jerky. Pages scrolled to later pick up the new
        // rotation on their own, because renderInto asks rotationProvider().
        val onScreen = holders.values.toList()
        if (onScreen.isEmpty()) { notifyDataSetChanged(); return }
        onScreen.forEach { h ->
            val pos = h.boundPosition
            if (pos < 0) return@forEach
            renderInto(pos, baseWidthProvider()) { bmp ->
                if (bmp != null) h.b.pageImage.setImageBitmap(bmp)
            }
        }
    }

    private fun renderInto(position: Int, width: Int, onReady: (Bitmap?) -> Unit) {
        val rot = rotationProvider()
        scope.launch {
            val bmp = withContext(Dispatchers.IO) {
                runCatching { renderer.render(position, width, rot) }.getOrNull()
            }
            onReady(bmp)
        }
    }

}
