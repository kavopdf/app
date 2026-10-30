package com.kavopdf.app.ui

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.View

/** A signature pad: draw with a finger, choose the ink colour, export as a bitmap. */
class SignaturePad @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val path = Path()
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLACK
        style = Paint.Style.STROKE
        strokeWidth = 5f
        strokeCap = Paint.Cap.ROUND
        strokeJoin = Paint.Join.ROUND
    }
    private var lastX = 0f
    private var lastY = 0f
    private var hasInk = false

    fun setInkColor(color: Int) {
        paint.color = color
        invalidate()
    }

    fun clear() {
        path.reset()
        hasInk = false
        invalidate()
    }

    fun isEmpty() = !hasInk

    fun toBitmap(): Bitmap {
        val bmp = Bitmap.createBitmap(
            width.coerceAtLeast(1), height.coerceAtLeast(1), Bitmap.Config.ARGB_8888
        )
        val canvas = Canvas(bmp)
        canvas.drawColor(Color.TRANSPARENT)
        canvas.drawPath(path, paint)
        return bmp
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawPath(path, paint)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                path.moveTo(event.x, event.y)
                lastX = event.x
                lastY = event.y
                hasInk = true
            }
            MotionEvent.ACTION_MOVE -> {
                path.quadTo(lastX, lastY, event.x, event.y)
                lastX = event.x
                lastY = event.y
            }
        }
        invalidate()
        return true
    }
}
