package com.kavopdf.app.ui

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.DashPathEffect
import android.graphics.Paint
import android.graphics.PointF
import android.graphics.RectF
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.ScaleGestureDetector
import android.view.View
import com.kavopdf.app.model.Annot
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min

/**
 * Transparent drawing surface over the page image. It converts touches into
 * normalised page coordinates, records annotations, and lets an item be selected,
 * dragged and pinched to resize. Two-finger gestures are handed to the image view
 * so zooming always works.
 */
class OverlayView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    enum class Tool { PAN, PEN, HIGHLIGHT, TEXT, COVER, SIGN, IMAGE, SELECT, ERASE, SHAPE }

    /**
     * The page under this overlay. Setting it also subscribes to the image matrix, so
     * the drawing is repainted on every pinch frame. Without that the page zoomed while
     * the ink stayed put, which is what made zooming feel rough.
     */
    var imageView: ZoomableImageView? = null
        set(value) {
            field?.onMatrixChanged = null
            field = value
            value?.onMatrixChanged = { postInvalidateOnAnimation() }
        }
    var pageW: Float = 595f
    var pageH: Float = 842f
    var tool: Tool = Tool.PAN
    /** Which shape SHAPE draws. */
    var shapeKind: Int = Annot.Shape.KIND_RECT
    /** true = the eraser removes the whole stroke, false = only the part touched. */
    var eraserWholeStroke: Boolean = false   // false = erase only the part touched
    private var eraseLast: PointF? = null
    private var eraseTouched = false

    var items: MutableList<Annot> = mutableListOf()
    var selected: Int = -1

    var color: Int = Color.BLACK
    var penWidthPt: Float = 3f
    var highlightWidthPt: Float = 18f
    var highlightOpacity: Float = 0.35f
    /** True once a second finger lands, so the gesture is a zoom, not a draw. */
    private var multiTouched = false
    var textSizePt: Float = 16f

    var onTextAt: ((Float, Float) -> Unit)? = null
    var onStampAt: ((Float, Float) -> Unit)? = null
    var onCoverRect: ((Float, Float, Float, Float) -> Unit)? = null
    var onBeforeChange: (() -> Unit)? = null
    var onChanged: (() -> Unit)? = null
    var onSelectionChanged: ((Int) -> Unit)? = null

    private val preview = Paint(Paint.ANTI_ALIAS_FLAG)
    private var dragStart: PointF? = null
    private var dragNow: PointF? = null
    private var stroke: MutableList<PointF>? = null
    private var downAt: PointF? = null
    private var moving = false
    private var moveLast: PointF? = null
    private var changeNotified = false

    private val resizeDetector = ScaleGestureDetector(
        context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                if (selected !in items.indices) return false
                if (!changeNotified) { onBeforeChange?.invoke(); changeNotified = true }
                scaleItem(selected, detector.scaleFactor)
                invalidate()
                onChanged?.invoke()
                return true
            }
        }
    )

    fun applyTool(t: Tool) {
        tool = t
        if (t != Tool.SELECT) selectItem(-1)
        imageView?.panEnabled = (t == Tool.PAN)
        invalidate()
    }

    fun refresh() = invalidate()

    fun selectItem(index: Int) {
        selected = index
        onSelectionChanged?.invoke(index)
        invalidate()
    }

    // ---- geometry ----------------------------------------------------------

    private fun pageRect(): RectF {
        val r = RectF()
        val iv = imageView
        val d = iv?.drawable
        if (iv != null && d != null && d.intrinsicWidth > 0) {
            val pts = floatArrayOf(0f, 0f, d.intrinsicWidth.toFloat(), d.intrinsicHeight.toFloat())
            iv.imageMatrix.mapPoints(pts)
            r.set(pts[0], pts[1], pts[2], pts[3])
            return r
        }
        r.set(0f, 0f, width.toFloat(), height.toFloat())
        return r
    }

    private fun normalize(x: Float, y: Float): PointF {
        val r = pageRect()
        if (r.width() <= 0f || r.height() <= 0f) return PointF(0f, 0f)
        return PointF(
            ((x - r.left) / r.width()).coerceIn(0f, 1f),
            ((y - r.top) / r.height()).coerceIn(0f, 1f)
        )
    }

    private fun bounds(a: Annot): RectF = when (a) {
        is Annot.Cover -> RectF(a.fx, a.fy, a.fx + a.fw, a.fy + a.fh)
        is Annot.Highlight -> RectF(a.fx, a.fy, a.fx + a.fw, a.fy + a.fh)
        is Annot.Stamp -> RectF(a.fx, a.fy, a.fx + a.fw, a.fy + a.fh)
        is Annot.Shape -> RectF(a.fx, a.fy, a.fx + a.fw, a.fy + a.fh)
        is Annot.Text -> {
            val w = a.text.length * a.sizePt * 0.5f / pageW
            val h = a.sizePt / pageH
            RectF(a.fx, a.fy - h, a.fx + max(w, 0.02f), a.fy + h * 0.25f)
        }
        is Annot.Stroke -> {
            var l = 1f; var t = 1f; var rr = 0f; var b = 0f
            for (p in a.points) { l = min(l, p.x); t = min(t, p.y); rr = max(rr, p.x); b = max(b, p.y) }
            val pad = max(0.01f, a.widthPt / pageH)
            RectF(l - pad, t - pad, rr + pad, b + pad)
        }
    }

    private fun hitTest(nx: Float, ny: Float): Int {
        for (i in items.indices.reversed()) {
            val b = bounds(items[i])
            if (nx >= b.left && nx <= b.right && ny >= b.top && ny <= b.bottom) return i
        }
        return -1
    }

    private fun moveItem(i: Int, dfx: Float, dfy: Float) {
        if (i !in items.indices) return
        when (val a = items[i]) {
            is Annot.Cover -> { a.fx = (a.fx + dfx).coerceIn(-a.fw + 0.02f, 1f - 0.02f); a.fy = (a.fy + dfy).coerceIn(-a.fh + 0.02f, 1f - 0.02f) }
            is Annot.Highlight -> { a.fx = (a.fx + dfx).coerceIn(-a.fw + 0.02f, 1f - 0.02f); a.fy = (a.fy + dfy).coerceIn(-a.fh + 0.02f, 1f - 0.02f) }
            is Annot.Stamp -> { a.fx = (a.fx + dfx).coerceIn(-a.fw + 0.02f, 1f - 0.02f); a.fy = (a.fy + dfy).coerceIn(-a.fh + 0.02f, 1f - 0.02f) }
            is Annot.Shape -> { a.fx = (a.fx + dfx).coerceIn(-a.fw + 0.02f, 1f - 0.02f); a.fy = (a.fy + dfy).coerceIn(-a.fh + 0.02f, 1f - 0.02f) }
            is Annot.Text -> { a.fx = (a.fx + dfx).coerceIn(0f, 1f); a.fy = (a.fy + dfy).coerceIn(0f, 1f) }
            is Annot.Stroke -> a.points.forEach { it.x += dfx; it.y += dfy }
        }
    }

    private fun scaleItem(i: Int, f: Float) {
        if (i !in items.indices) return
        when (val a = items[i]) {
            is Annot.Cover -> { a.fw = (a.fw * f).coerceIn(0.03f, 1f); a.fh = (a.fh * f).coerceIn(0.03f, 1f) }
            is Annot.Highlight -> { a.fw = (a.fw * f).coerceIn(0.03f, 1f); a.fh = (a.fh * f).coerceIn(0.02f, 1f) }
            is Annot.Shape -> { a.fw = (a.fw * f).coerceIn(0.02f, 1f); a.fh = (a.fh * f).coerceIn(0.02f, 1f) }
            is Annot.Stamp -> { a.fw = (a.fw * f).coerceIn(0.05f, 1.5f); a.fh = (a.fh * f).coerceIn(0.05f, 1.5f) }
            is Annot.Text -> a.sizePt = (a.sizePt * f).coerceIn(6f, 96f)
            is Annot.Stroke -> {
                var cx = 0f; var cy = 0f
                for (p in a.points) { cx += p.x; cy += p.y }
                cx /= a.points.size; cy /= a.points.size
                a.points.forEach { it.x = cx + (it.x - cx) * f; it.y = cy + (it.y - cy) * f }
                a.widthPt = (a.widthPt * f).coerceIn(0.5f, 40f)
            }
        }
    }

    // ---- drawing -----------------------------------------------------------

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val r = pageRect()
        if (r.width() <= 0f) return
        val pxPerPt = r.width() / pageW
        AnnotRenderer.draw(canvas, items, pageW, pageH, pxPerPt, r.left, r.top)

        // live previews
        val hs = dragStart
        val hn = dragNow
        if ((tool == Tool.HIGHLIGHT || tool == Tool.COVER) && hs != null && hn != null) {
            preview.style = Paint.Style.FILL
            preview.color = if (tool == Tool.COVER) color
            else Color.argb((highlightOpacity * 255).toInt(), Color.red(color), Color.green(color), Color.blue(color))
            canvas.drawRect(
                r.left + hs.x * r.width(), r.top + hs.y * r.height(),
                r.left + hn.x * r.width(), r.top + hn.y * r.height(), preview
            )
        }
        if (tool == Tool.SHAPE && hs != null && hn != null) {
            preview.style = Paint.Style.STROKE
            preview.strokeCap = Paint.Cap.ROUND
            preview.strokeJoin = Paint.Join.ROUND
            preview.strokeWidth = (penWidthPt * pxPerPt).coerceAtLeast(1f)
            preview.color = color
            preview.pathEffect = null
            AnnotRenderer.drawShape(
                canvas, preview, shapeKind,
                r.left + hs.x * r.width(), r.top + hs.y * r.height(),
                r.left + hn.x * r.width(), r.top + hn.y * r.height()
            )
        }
        val s = stroke
        if (tool == Tool.PEN && s != null && s.size >= 2) {
            preview.style = Paint.Style.STROKE
            preview.strokeCap = Paint.Cap.ROUND
            preview.strokeJoin = Paint.Join.ROUND
            preview.strokeWidth = (penWidthPt * pxPerPt).coerceAtLeast(1f)
            preview.color = color
            // The same curve the export draws, so what is on screen is what gets saved.
            val path = AnnotRenderer.strokePath(
                s,
                { p -> r.left + p.x * r.width() },
                { p -> r.top + p.y * r.height() }
            )
            canvas.drawPath(path, preview)
        }

        // selection outline
        if (tool == Tool.SELECT && selected in items.indices) {
            val b = bounds(items[selected])
            preview.style = Paint.Style.STROKE
            preview.strokeWidth = 2f * resources.displayMetrics.density
            preview.color = Color.argb(220, 59, 91, 219)
            preview.pathEffect = DashPathEffect(floatArrayOf(12f, 10f), 0f)
            canvas.drawRect(
                r.left + b.left * r.width(), r.top + b.top * r.height(),
                r.left + b.right * r.width(), r.top + b.bottom * r.height(), preview
            )
            preview.pathEffect = null
        }
    }

    // ---- touch -------------------------------------------------------------

    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (tool == Tool.SELECT && selected in items.indices && event.pointerCount >= 2) {
            resizeDetector.onTouchEvent(event)
            if (event.actionMasked == MotionEvent.ACTION_UP ||
                event.actionMasked == MotionEvent.ACTION_CANCEL) changeNotified = false
            return true
        }

        // everything else is handed to the image view so pinch-zoom / pan keep working
        imageView?.onTouchEvent(event)
        if (event.actionMasked == MotionEvent.ACTION_POINTER_DOWN) {
            // a second finger means the user is zooming: throw away whatever the first
            // finger had started, otherwise a stray dot or shape is committed on lift
            multiTouched = true
            stroke = null
            dragStart = null
            dragNow = null
            moving = false
            changeNotified = false
            invalidate()
        }
        if (event.pointerCount >= 2) return true

        val p = normalize(event.x, event.y)
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                downAt = p
                changeNotified = false
                when (tool) {
                    Tool.PEN -> { onBeforeChange?.invoke(); changeNotified = true; stroke = mutableListOf(p) }
                    Tool.HIGHLIGHT, Tool.COVER, Tool.SHAPE -> { onBeforeChange?.invoke(); changeNotified = true; dragStart = p; dragNow = p }
                    Tool.SELECT -> {
                        val hit = hitTest(p.x, p.y)
                        selectItem(hit)
                        if (hit >= 0) { moving = true; moveLast = p; onBeforeChange?.invoke(); changeNotified = true }
                    }
                    else -> { }
                }
                invalidate()
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                when (tool) {
                    Tool.PEN -> stroke?.add(p)
                    // drag to erase: step along the movement so a fast swipe
                    // leaves no gaps, and only ask for undo once per gesture
                    Tool.ERASE -> eraseAlong(p.x, p.y)
                    Tool.HIGHLIGHT, Tool.COVER, Tool.SHAPE -> dragNow = p
                    Tool.SELECT -> {
                        val last = moveLast
                        if (moving && last != null && selected in items.indices) {
                            moveItem(selected, p.x - last.x, p.y - last.y)
                            moveLast = p
                            onChanged?.invoke()
                        }
                    }
                    else -> { }
                }
                invalidate()
                return true
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                if (multiTouched) {
                    // the gesture was a pinch, not a draw - commit nothing
                    multiTouched = false
                    stroke = null
                    dragStart = null
                    dragNow = null
                    moving = false
                    changeNotified = false
                    invalidate()
                    return true
                }
                when (tool) {
                    Tool.PEN -> {
                        val st = stroke
                        if (st != null && st.size >= 2) {
                            items.add(Annot.Stroke(st, penWidthPt, color, 1f))
                            onChanged?.invoke()
                        }
                    }
                    Tool.HIGHLIGHT -> {
                        val a = dragStart
                        if (a != null) {
                            val x0 = min(a.x, p.x); val y0 = min(a.y, p.y)
                            val w = abs(p.x - a.x); val h = abs(p.y - a.y)
                            if (w > 0.01f && h > 0.004f) {
                                val a255 = (highlightOpacity.coerceIn(0.05f, 1f) * 255).toInt()
                                items.add(Annot.Highlight(x0, y0, w, h, (color and 0x00FFFFFF) or (a255 shl 24)))
                                onChanged?.invoke()
                            }
                        }
                    }
                    Tool.COVER -> {
                        val a = dragStart
                        if (a != null) {
                            val x0 = min(a.x, p.x); val y0 = min(a.y, p.y)
                            val w = abs(p.x - a.x); val h = abs(p.y - a.y)
                            if (w > 0.01f && h > 0.004f) onCoverRect?.invoke(x0, y0, w, h)
                        }
                    }
                    Tool.SHAPE -> {
                        val a = dragStart
                        if (a != null) {
                            val x0 = min(a.x, p.x); val y0 = min(a.y, p.y)
                            val w = abs(p.x - a.x); val h = abs(p.y - a.y)
                            // a line may be dragged in any direction, so remember which
                            val flipX = p.x < a.x
                            val flipY = p.y < a.y
                            val thin = shapeKind == Annot.Shape.KIND_LINE || shapeKind == Annot.Shape.KIND_ARROW
                            if (w > 0.008f || (thin && h > 0.008f)) {
                                items.add(Annot.Shape(x0, y0, w, h, color, penWidthPt, shapeKind, flipX, flipY))
                                onChanged?.invoke()
                            }
                        }
                    }
                    Tool.TEXT, Tool.SIGN, Tool.IMAGE -> {
                        val d = downAt
                        val moved = d != null &&
                                (abs(p.x - d.x) > 0.02f || abs(p.y - d.y) > 0.02f)
                        if (!moved && d != null) {
                            if (tool == Tool.TEXT) onTextAt?.invoke(d.x, d.y)
                            else onStampAt?.invoke(d.x, d.y)
                        }
                    }
                    Tool.ERASE -> {
                        eraseLast = null
                        eraseTouched = false
                        eraseAt(p.x, p.y)
                    }
                    else -> { }
                }
                dragStart = null; dragNow = null; stroke = null; downAt = null
                moving = false; moveLast = null; changeNotified = false
                invalidate()
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    /**
     * A real eraser: it takes out only the part of a stroke under the finger, and
     * leaves the rest. A stroke cut in the middle becomes two strokes.
     *
     * The drag path is walked in small steps so a fast swipe leaves no gaps.
     */
    private fun eraseAlong(fx: Float, fy: Float) {
        val lx = eraseLast?.x
        val ly = eraseLast?.y
        if (lx == null || ly == null) {
            eraseAt(fx, fy)
        } else {
            val dx = fx - lx
            val dy = fy - ly
            val dist = kotlin.math.hypot(dx, dy)
            var steps = (dist / 0.004f).toInt()
            if (steps < 1) steps = 1
            var i = 1
            while (i <= steps) {
                val t = i.toFloat() / steps
                eraseAt(lx + dx * t, ly + dy * t)
                i++
            }
        }
        eraseLast = PointF(fx, fy)
    }

    private fun eraseAt(fx: Float, fy: Float) {
        val hit = hitTest(fx, fy)
        if (hit < 0) return
        // Ruled and grid lines are page furniture, not ink. Neither eraser touches
        // them; before this the whole-stroke eraser removed an entire grid at once
        // while the partial eraser left it alone, which looked like a bug because it
        // was one.
        if ((items[hit] as? Annot.Stroke)?.guide == true) return
        onBeforeChange?.invoke()
        val a = items[hit]
        if (eraserWholeStroke) {
            // whole-stroke mode: one touch removes the entire line
            items.removeAt(hit)
            selected = -1
            invalidate()
            onChanged?.invoke()
            return
        }
        if (a is Annot.Stroke) {
            // A fingertip is about 1.5% of the page. The stroke itself matters only a
            // little: widthPt is in points (a page is ~595pt wide), so a 72pt pen is
            // 0.12 of the page, not 0.72. Scaling by /100 made a thick pen swallow
            // the whole line - that is why thick strokes looked fully erased.
            val strokeFrac = (a.widthPt / 595f).coerceAtMost(0.12f)
            val reach = (strokeFrac * 0.5f + 0.015f).coerceAtMost(0.04f)
            val runs = ArrayList<MutableList<PointF>>()
            var run = ArrayList<PointF>()
            for (pt in a.points) {
                val d = Math.hypot((pt.x - fx).toDouble(), (pt.y - fy).toDouble()).toFloat()
                if (d <= reach) {
                    if (run.size >= 2) runs.add(run)
                    run = ArrayList()
                } else {
                    run.add(PointF(pt.x, pt.y))
                }
            }
            if (run.size >= 2) runs.add(run)
            items.removeAt(hit)
            runs.forEachIndexed { i, pts ->
                items.add(hit + i, Annot.Stroke(pts, a.widthPt, a.color, a.opacity, a.guide))
            }
            selectItem(-1)
            onChanged?.invoke()
        } else {
            items.removeAt(hit)
            selectItem(-1)
            onChanged?.invoke()
        }
    }
}
