package com.kavopdf.app.ui

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Bitmap
import android.graphics.Matrix
import android.graphics.drawable.Drawable
import android.util.AttributeSet
import android.view.GestureDetector
import android.view.animation.DecelerateInterpolator
import android.view.MotionEvent
import android.view.ScaleGestureDetector
import androidx.appcompat.widget.AppCompatImageView

/**
 * Pinch-zoom / pan image view used for PDF pages.
 *
 * [panEnabled] lets a drawing overlay sit on top: when it is false a single-finger
 * drag no longer pans (so the overlay can draw) while two-finger pinch still zooms.
 */
class ZoomableImageView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : AppCompatImageView(context, attrs, defStyleAttr) {

    private val m = Matrix()
    private var zoom = 1f
    var lastDownX = 0f
    var lastDownY = 0f
    private val minZoom = 1f
    private val maxZoom = 8f
    private var tx = 0f
    private var ty = 0f
    private var suppressReset = false

    /** When false, single-finger drags are ignored (used while an overlay draws). */
    var panEnabled = true

    var onZoomChanged: ((Boolean) -> Unit)? = null

    /** Fired on every matrix change, including each pinch frame. An overlay uses it to repaint. */
    var onMatrixChanged: (() -> Unit)? = null

    /** Fires when a zoom gesture ends, with the resulting zoom factor. */
    var onZoomSettled: ((Float) -> Unit)? = null

    init {
        scaleType = ScaleType.MATRIX
    }

    /** Where the pinch focus sat on the previous frame, so a moving pinch can pan. */
    private var focusX = 0f
    private var focusY = 0f

    private val scaleDetector = ScaleGestureDetector(
        context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScaleBegin(detector: ScaleGestureDetector): Boolean {
                focusX = detector.focusX
                focusY = detector.focusY
                return true
            }

            override fun onScale(detector: ScaleGestureDetector): Boolean {
                val old = zoom
                zoom = (zoom * detector.scaleFactor).coerceIn(minZoom, maxZoom)
                val f = zoom / old
                // Keep whatever is under the fingers under the fingers. The old
                // form scaled tx by 1 instead of f, so as soon as the page had been
                // panned the zoom drifted back toward the middle.
                val cx = detector.focusX - width / 2f
                val cy = detector.focusY - height / 2f
                tx = f * tx + (1f - f) * cx
                ty = f * ty + (1f - f) * cy
                // Two fingers also drag the page. Following the pinch focus is the
                // jitter-free way to do it: the scroll detector cannot be used while
                // a pinch is in progress, which is why moving two fingers did nothing
                // and the Move page / Pan tool had to be switched to by hand.
                val dx = detector.focusX - focusX
                val dy = detector.focusY - focusY
                focusX = detector.focusX
                focusY = detector.focusY
                if (dx != 0f || dy != 0f) {
                    tx += dx
                    ty += dy
                }
                apply()
                notifyZoom()
                return true
            }
        }
    )

    private val gesture = GestureDetector(
        context,
        object : GestureDetector.SimpleOnGestureListener() {
            override fun onDown(e: MotionEvent) = true

            override fun onScroll(e1: MotionEvent?, e2: MotionEvent, dx: Float, dy: Float): Boolean {
                // Two fingers always pan, whatever tool is selected. Before this, pan
                // was allowed only with the Pan tool, so with a pen selected you could
                // zoom but never move to a corner - and drawing there was impossible.
                // One finger still goes to the tool, so drawing is unaffected.
                if (zoom <= 1f) return false
                // While a pinch is in progress the scale detector owns the gesture.
                // Letting the scroll detector also apply its delta made the page fight
                // itself - that is the jitter that made zooming feel like hard work.
                if (scaleDetector.isInProgress) return false
                if (!panEnabled && e2.pointerCount < 2) return false
                tx -= dx
                ty -= dy
                apply()
                return true
            }

            override fun onDoubleTap(e: MotionEvent): Boolean {
                // zoom towards the spot that was tapped, not the middle of the screen
                val target = if (zoom > 1.05f) 1f else 2.5f
                if (target <= 1.01f) {
                    animateTo(1f, 0f, 0f)
                    return true
                }
                val d = drawable
                val vw = width.toFloat()
                val vh = height.toFloat()
                if (d == null || vw <= 0f || vh <= 0f || d.intrinsicWidth <= 0) {
                    animateTo(target, 0f, 0f)
                    return true
                }
                val base = minOf(vw / d.intrinsicWidth, vh / d.intrinsicHeight)
                val s0 = base * zoom
                val s1 = base * target
                // where the tapped pixel sits in the image
                val ix = (e.x - (vw - d.intrinsicWidth * s0) / 2f - tx) / s0
                val iy = (e.y - (vh - d.intrinsicHeight * s0) / 2f - ty) / s0
                // and what offset keeps it under the finger afterwards
                val tx1 = e.x - (vw - d.intrinsicWidth * s1) / 2f - ix * s1
                val ty1 = e.y - (vh - d.intrinsicHeight * s1) / 2f - iy * s1
                animateTo(target, tx1, ty1)
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (event.actionMasked == MotionEvent.ACTION_DOWN) {
            lastDownX = event.x; lastDownY = event.y
        }
        scaleDetector.onTouchEvent(event)
        gesture.onTouchEvent(event)
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> parent?.requestDisallowInterceptTouchEvent(zoom > 1f)
            MotionEvent.ACTION_POINTER_DOWN -> parent?.requestDisallowInterceptTouchEvent(true)
            MotionEvent.ACTION_POINTER_UP ->
                if (event.pointerCount <= 2) onZoomSettled?.invoke(zoom)
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                parent?.requestDisallowInterceptTouchEvent(false)
                onZoomSettled?.invoke(zoom)
            }
        }
        // Hand the event to the framework as well: that is what runs the click and
        // long-press detection. Without it setOnLongClickListener never fires, which
        // is why long-pressing a page to copy its text did nothing.
        super.onTouchEvent(event)
        return true
    }

    override fun setImageBitmap(bm: Bitmap?) {
        super.setImageBitmap(bm)
        if (!suppressReset) reset()
    }

    override fun setImageDrawable(drawable: Drawable?) {
        super.setImageDrawable(drawable)
        if (!suppressReset) reset()
    }

    /** Swap the bitmap in while keeping the current zoom and pan (used for hi-res re-render). */
    fun setImageBitmapPreservingTransform(bm: Bitmap?) {
        val z = zoom
        val px = tx
        val py = ty
        suppressReset = true
        super.setImageBitmap(bm)
        suppressReset = false
        zoom = z
        tx = px
        ty = py
        apply()
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        // reset() here threw the user's zoom away whenever the layout shifted - and
        // the layout shifts on almost every tool change, because the hint line below
        // the toolbar appears or disappears. That is why picking Select-and-move (or
        // any tool) snapped a zoomed page back to full size mid-work. Keep the zoom
        // and simply re-fit to the new size.
        if (pendingFit || zoom <= 1.01f) reset() else apply()
    }

    private var zoomAnimator: ValueAnimator? = null

    /** Smoothly move to a zoom level; the jump used to be instant, which felt broken. */
    private fun animateTo(targetZoom: Float, targetTx: Float, targetTy: Float) {
        zoomAnimator?.cancel()
        val fromZoom = zoom
        val fromTx = tx
        val fromTy = ty
        zoomAnimator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 220L
            interpolator = DecelerateInterpolator()
            addUpdateListener {
                val t = it.animatedValue as Float
                zoom = fromZoom + (targetZoom - fromZoom) * t
                tx = fromTx + (targetTx - fromTx) * t
                ty = fromTy + (targetTy - fromTy) * t
                apply()
            }
            addListener(object : android.animation.AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: android.animation.Animator) {
                    notifyZoom()
                    onZoomSettled?.invoke(zoom)
                }
            })
            start()
        }
    }

    fun reset() {
        zoom = 1f
        tx = 0f
        ty = 0f
        apply()
        notifyZoom()
    }

    fun isZoomed() = zoom > 1.05f

    private fun notifyZoom() = onZoomChanged?.invoke(isZoomed())

    /** True when a fit was skipped because the size was not known yet. */
    private var pendingFit = false

    private fun apply() {
        val d = drawable
        val vw = width.toFloat()
        val vh = height.toFloat()
        val dw = d?.intrinsicWidth?.toFloat() ?: 0f
        val dh = d?.intrinsicHeight?.toFloat() ?: 0f
        if (d == null || vw <= 0f || vh <= 0f || dw <= 0f || dh <= 0f) {
            // No size or no picture yet. Assigning the old matrix here drew the new page
            // at the previous page's scale and offset, and nothing corrected it. Ask for
            // a fit as soon as both are known instead.
            pendingFit = true
            return
        }
        pendingFit = false
        val base = minOf(vw / dw, vh / dh)
        val s = base * zoom
        val w = dw * s
        val h = dh * s
        val maxTx = maxOf(0f, (w - vw) / 2f)
        val maxTy = maxOf(0f, (h - vh) / 2f)
        tx = tx.coerceIn(-maxTx, maxTx)
        ty = ty.coerceIn(-maxTy, maxTy)
        m.reset()
        m.postScale(s, s)
        m.postTranslate((vw - w) / 2f + tx, (vh - h) / 2f + ty)
        imageMatrix = m
        onMatrixChanged?.invoke()
    }
}
