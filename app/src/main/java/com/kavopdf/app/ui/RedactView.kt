package com.kavopdf.app.ui

import android.content.Context
import android.graphics.Canvas
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
 * Draw as many redaction boxes as you like over a page.
 *
 * Drag anywhere to add a box; tap an existing box to remove it.
 * Boxes are kept normalised (0..1) to the page, so rotation does not matter.
 */
class RedactView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    var imageView: ZoomableImageView? = null

    /** When false the view only draws existing boxes and lets the image zoom/pan. */
    var drawingEnabled = true

    /** Committed boxes, normalised to the page. */
    val rects = ArrayList<RectF>()

    private var drawing: RectF? = null
    private var tapTarget: RectF? = null
    private var downX = 0f
    private var downY = 0f
    private var moved = false
    private val rect = RectF()
    private val slop = 12f

    private val fill = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = 0xE6000000.toInt()
        style = Paint.Style.FILL
    }
    private val border = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = 0xFFE03131.toInt()
        style = Paint.Style.STROKE
        strokeWidth = 3f
    }
    private val pending = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = 0x99000000.toInt()
        style = Paint.Style.FILL
    }
    private val pendingEdge = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = 0xFFE03131.toInt()
        style = Paint.Style.STROKE
        strokeWidth = 2.5f
        pathEffect = android.graphics.DashPathEffect(floatArrayOf(12f, 8f), 0f)
    }

    fun clear() {
        rects.clear()
        drawing = null
        tapTarget = null
        invalidate()
    }

    fun isEmpty() = rects.isEmpty()

    private fun pageRect(out: RectF): Boolean {
        val iv = imageView ?: return false
        return drawnImageRect(iv, out)
    }

    /** The normalised box, mapped to view coordinates. */
    private fun toView(pr: RectF, n: RectF): RectF = RectF(
        pr.left + n.left * pr.width(), pr.top + n.top * pr.height(),
        pr.left + n.right * pr.width(), pr.top + n.bottom * pr.height()
    )

    private fun toNorm(pr: RectF, x: Float, y: Float): Pair<Float, Float> {
        val nx = ((x - pr.left) / pr.width()).coerceIn(0f, 1f)
        val ny = ((y - pr.top) / pr.height()).coerceIn(0f, 1f)
        return nx to ny
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // The image view gets every event so pinch-zoom keeps working. Panning is
        // switched on only while two fingers are down, so one finger never drags
        // the page out from under a box being drawn.
        imageView?.panEnabled = event.pointerCount >= 2
        imageView?.onTouchEvent(event)
        // ...but two fingers mean zoom, never a redaction box.
        if (event.pointerCount >= 2) {
            drawing = null
            tapTarget = null
            invalidate()
            return true
        }
        if (!drawingEnabled) return false
        val pr = RectF()
        if (!pageRect(pr)) return false
        val x = event.x
        val y = event.y
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                downX = x; downY = y; moved = false
                tapTarget = rects.firstOrNull { toView(pr, it).contains(x, y) }
                if (tapTarget == null) {
                    val (nx, ny) = toNorm(pr, x, y)
                    drawing = RectF(nx, ny, nx, ny)
                }
                invalidate()
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                if (abs(x - downX) > slop || abs(y - downY) > slop) moved = true
                val d = drawing
                if (d != null) {
                    val (nx, ny) = toNorm(pr, x, y)
                    d.right = nx
                    d.bottom = ny
                    invalidate()
                }
                return true
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                val d = drawing
                if (d != null) {
                    val box = RectF(
                        min(d.left, d.right), min(d.top, d.bottom),
                        max(d.left, d.right), max(d.top, d.bottom)
                    )
                    // ignore an accidental tap
                    if (box.width() * pr.width() > 14f && box.height() * pr.height() > 8f) {
                        rects.add(box)
                    }
                    drawing = null
                } else if (tapTarget != null && !moved) {
                    rects.remove(tapTarget)
                    tapTarget = null
                }
                invalidate()
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val pr = RectF()
        if (!pageRect(pr)) return
        for (n in rects) {
            val r = toView(pr, n)
            canvas.drawRect(r, fill)
            canvas.drawRect(r, border)
        }
        drawing?.let {
            val r = toView(pr, it)
            canvas.drawRect(r, pending)
            canvas.drawRect(r, pendingEdge)
        }
    }
}
