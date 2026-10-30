package com.kavopdf.app.ui

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.RectF
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.View
import android.widget.ImageView
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min

/**
 * A crop selection over a page image. The rectangle is stored in normalised page
 * coordinates (0..1), so it maps to points at any render size. Drag inside to move
 * it, drag a corner handle to resize.
 */
class CropView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    var imageView: ImageView? = null

    /** When true, a tap outside the selection moves it there and starts dragging.
     *  Used for placing link icons / link text, where you point at where it goes. */
    var moveOnTapOutside = false

    /** left, top, right, bottom in 0..1 of the displayed page. */
    private var l = 0.08f
    private var t = 0.08f
    private var r = 0.92f
    private var b = 0.92f

    private val dim = Paint().apply { color = 0x99000000.toInt() }
    private val line = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.WHITE
        style = Paint.Style.STROKE
        strokeWidth = 3f
    }
    private val handle = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.WHITE
        style = Paint.Style.FILL
    }
    private val rect = RectF()
    private var mode = 0 // 0 none, 1 move, 2 tl, 3 tr, 4 bl, 5 br
    private var lastX = 0f
    private var lastY = 0f

    fun reset() = resetTo(0.08f, 0.08f, 0.92f, 0.92f)

    /** Set the selection to a specific normalised box (e.g. a small icon area). */
    fun resetTo(left: Float, top: Float, right: Float, bottom: Float) {
        l = left; t = top; r = right; b = bottom
        invalidate()
    }

    /** Crop rectangle in normalised coordinates. */
    fun cropRect(): FloatArray = floatArrayOf(l, t, r - l, b - t)

    private fun pageRect(out: RectF): Boolean {
        val iv = imageView ?: return false
        return drawnImageRect(iv, out)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val pr = RectF()
        if (!pageRect(pr)) return
        rect.set(
            pr.left + l * pr.width(), pr.top + t * pr.height(),
            pr.left + r * pr.width(), pr.top + b * pr.height()
        )
        // dim everything outside the crop
        canvas.drawRect(pr.left, pr.top, pr.right, rect.top, dim)
        canvas.drawRect(pr.left, rect.bottom, pr.right, pr.bottom, dim)
        canvas.drawRect(pr.left, rect.top, rect.left, rect.bottom, dim)
        canvas.drawRect(rect.right, rect.top, pr.right, rect.bottom, dim)
        canvas.drawRect(rect, line)
        val hs = 22f
        for (cx in floatArrayOf(rect.left, rect.right)) {
            for (cy in floatArrayOf(rect.top, rect.bottom)) {
                canvas.drawCircle(cx, cy, hs / 2f, handle)
            }
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        val pr = RectF()
        if (!pageRect(pr)) return false
        val x = event.x
        val y = event.y
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                // the screen scrolls; while the box is being dragged the scroll must
                // keep its hands off, otherwise vertical moves stutter or scroll
                parent?.requestDisallowInterceptTouchEvent(true)
                val near = 64f
                mode = when {
                    abs(x - rect.left) < near && abs(y - rect.top) < near -> 2
                    abs(x - rect.right) < near && abs(y - rect.top) < near -> 3
                    abs(x - rect.left) < near && abs(y - rect.bottom) < near -> 4
                    abs(x - rect.right) < near && abs(y - rect.bottom) < near -> 5
                    rect.contains(x, y) -> 1
                    moveOnTapOutside -> {
                        // centre the selection on the tap, then drag from there
                        val w = r - l
                        val h = b - t
                        val nx = (x - pr.left) / pr.width().coerceAtLeast(1f) - w / 2f
                        val ny = (y - pr.top) / pr.height().coerceAtLeast(1f) - h / 2f
                        l = nx.coerceIn(0f, 1f - w)
                        t = ny.coerceIn(0f, 1f - h)
                        r = l + w
                        b = t + h
                        invalidate()
                        1
                    }
                    else -> 0
                }
                lastX = x; lastY = y
                return mode != 0
            }
            MotionEvent.ACTION_MOVE -> {
                if (mode == 0) return false
                val dx = (x - lastX) / pr.width().coerceAtLeast(1f)
                val dy = (y - lastY) / pr.height().coerceAtLeast(1f)
                lastX = x; lastY = y
                val minSize = 0.05f
                when (mode) {
                    1 -> {
                        val w = r - l; val h = b - t
                        l = (l + dx).coerceIn(0f, 1f - w)
                        t = (t + dy).coerceIn(0f, 1f - h)
                        r = l + w; b = t + h
                    }
                    2 -> { l = (l + dx).coerceIn(0f, r - minSize); t = (t + dy).coerceIn(0f, b - minSize) }
                    3 -> { r = (r + dx).coerceIn(l + minSize, 1f); t = (t + dy).coerceIn(0f, b - minSize) }
                    4 -> { l = (l + dx).coerceIn(0f, r - minSize); b = (b + dy).coerceIn(t + minSize, 1f) }
                    5 -> { r = (r + dx).coerceIn(l + minSize, 1f); b = (b + dy).coerceIn(t + minSize, 1f) }
                }
                invalidate()
                return true
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                mode = 0
                parent?.requestDisallowInterceptTouchEvent(false)
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
