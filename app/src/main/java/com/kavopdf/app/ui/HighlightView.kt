package com.kavopdf.app.ui

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.RectF
import android.util.AttributeSet
import android.view.View
import android.widget.ImageView

/** Draws a translucent highlight over a region of the page (normalised 0..1). */
class HighlightView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    var imageView: ImageView? = null
    var norm: RectF? = null
        set(value) {
            field = value
            invalidate()
        }

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply { style = Paint.Style.FILL }

    private val outline = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 2.5f
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val iv = imageView ?: return
        val d = iv.drawable ?: return
        val n = norm ?: return
        val dw = d.intrinsicWidth.toFloat()
        val dh = d.intrinsicHeight.toFloat()
        if (dw <= 0f || dh <= 0f) return
        val pts = floatArrayOf(0f, 0f, dw, dh)
        iv.imageMatrix.mapPoints(pts)
        val w = pts[2] - pts[0]
        val h = pts[3] - pts[1]
        val r = RectF(
            pts[0] + n.left * w, pts[1] + n.top * h,
            pts[0] + n.right * w, pts[1] + n.bottom * h
        )
        r.inset(-3f, -3f)
        paint.color = 0x59FFC107
        outline.color = 0xCCFF8F00.toInt()
        canvas.drawRect(r, paint)
        canvas.drawRect(r, outline)
    }
}
