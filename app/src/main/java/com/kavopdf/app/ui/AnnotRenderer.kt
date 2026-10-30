package com.kavopdf.app.ui

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
import com.kavopdf.app.model.Annot

/**
 * Draws annotations. The very same routine powers the on-screen preview and the
 * exported raster layer, so preview and output are consistent.
 */
object AnnotRenderer {

    fun draw(
        canvas: Canvas,
        items: List<Annot>,
        pageW: Float,
        pageH: Float,
        pxPerPt: Float,
        ox: Float,
        oy: Float
    ) {
        val fill = Paint(Paint.ANTI_ALIAS_FLAG)
        val stroke = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            style = Paint.Style.STROKE
            strokeCap = Paint.Cap.ROUND
            strokeJoin = Paint.Join.ROUND
        }
        val textPaint = Paint(Paint.ANTI_ALIAS_FLAG)

        for (item in items) {
            when (item) {
                is Annot.Cover -> {
                    fill.style = Paint.Style.FILL
                    fill.color = item.color
                    canvas.drawRect(
                        ox + item.fx * pageW * pxPerPt, oy + item.fy * pageH * pxPerPt,
                        ox + (item.fx + item.fw) * pageW * pxPerPt, oy + (item.fy + item.fh) * pageH * pxPerPt, fill
                    )
                }
                is Annot.Highlight -> {
                    fill.style = Paint.Style.FILL
                    fill.color = item.color
                    canvas.drawRect(
                        ox + item.fx * pageW * pxPerPt, oy + item.fy * pageH * pxPerPt,
                        ox + (item.fx + item.fw) * pageW * pxPerPt, oy + (item.fy + item.fh) * pageH * pxPerPt, fill
                    )
                }
                is Annot.Shape -> {
                    stroke.style = Paint.Style.STROKE
                    stroke.color = item.color
                    stroke.strokeWidth = Math.max(1f, item.widthPt * pxPerPt)
                    stroke.strokeCap = Paint.Cap.ROUND
                    stroke.strokeJoin = Paint.Join.ROUND
                    val l = ox + item.fx * pageW * pxPerPt
                    val t = oy + item.fy * pageH * pxPerPt
                    val r = l + item.fw * pageW * pxPerPt
                    val b = t + item.fh * pageH * pxPerPt
                    // a line or arrow remembers which way it was drawn
                    val ax = if (item.flipX) r else l
                    val ay = if (item.flipY) b else t
                    val bx = if (item.flipX) l else r
                    val by = if (item.flipY) t else b
                    drawShape(canvas, stroke, item.kind, ax, ay, bx, by)
                }
                is Annot.Stroke -> {
                    if (item.points.size < 2) continue
                    val path = Path()
                    item.points.forEachIndexed { i, p ->
                        val x = ox + p.x * pageW * pxPerPt
                        val y = oy + p.y * pageH * pxPerPt
                        if (i == 0) path.moveTo(x, y) else path.lineTo(x, y)
                    }
                    stroke.color = withAlpha(item.color, item.opacity)
                    stroke.strokeWidth = (item.widthPt * pxPerPt).coerceAtLeast(1f)
                    canvas.drawPath(path, stroke)
                }
                is Annot.Text -> {
                    textPaint.color = item.color
                    textPaint.textSize = (item.sizePt * pxPerPt).coerceAtLeast(4f)
                    canvas.drawText(
                        item.text,
                        ox + item.fx * pageW * pxPerPt,
                        oy + item.fy * pageH * pxPerPt,
                        textPaint
                    )
                }
                is Annot.Stamp -> {
                    val dst = RectF(
                        ox + item.fx * pageW * pxPerPt, oy + item.fy * pageH * pxPerPt,
                        ox + (item.fx + item.fw) * pageW * pxPerPt,
                        oy + (item.fy + item.fh) * pageH * pxPerPt
                    )
                    canvas.drawBitmap(item.bitmap, null, dst, fill)
                }
            }
        }
    }

    /** Rasterise the annotations for one page onto a transparent bitmap. */
    fun rasterize(items: List<Annot>, pageW: Float, pageH: Float, scale: Float): Bitmap {
        var w = (pageW * scale).toInt().coerceAtLeast(1)
        var h = (pageH * scale).toInt().coerceAtLeast(1)
        // never allocate more than ~16 MP, whatever the page claims to be
        val maxPixels = 16_000_000.0
        val px = w.toDouble() * h
        if (px > maxPixels) {
            val s = Math.sqrt(maxPixels / px)
            w = (w * s).toInt().coerceAtLeast(1)
            h = (h * s).toInt().coerceAtLeast(1)
        }
        val bmp = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        draw(Canvas(bmp), items, pageW, pageH, scale, 0f, 0f)
        return bmp
    }

    private fun withAlpha(color: Int, alpha: Float): Int {
        val a = (Color.alpha(color) * alpha).toInt().coerceIn(0, 255)
        return (a shl 24) or (color and 0x00FFFFFF)
    }

    /** One place that knows how every shape kind is drawn - preview and export both use it. */
    fun drawShape(canvas: Canvas, paint: Paint, kind: Int, l: Float, t: Float, r: Float, b: Float) {
        when (kind) {
            Annot.Shape.KIND_ELLIPSE ->
                canvas.drawOval(Math.min(l, r), Math.min(t, b), Math.max(l, r), Math.max(t, b), paint)
            Annot.Shape.KIND_LINE ->
                canvas.drawLine(l, t, r, b, paint)
            Annot.Shape.KIND_ARROW -> {
                canvas.drawLine(l, t, r, b, paint)
                val ang = Math.atan2((b - t).toDouble(), (r - l).toDouble())
                val len = Math.min(34f, Math.hypot((r - l).toDouble(), (b - t).toDouble()).toFloat() * 0.3f)
                val a1 = ang - Math.PI / 7
                val a2 = ang + Math.PI / 7
                canvas.drawLine(r, b, (r - len * Math.cos(a1)).toFloat(), (b - len * Math.sin(a1)).toFloat(), paint)
                canvas.drawLine(r, b, (r - len * Math.cos(a2)).toFloat(), (b - len * Math.sin(a2)).toFloat(), paint)
            }
            Annot.Shape.KIND_TRIANGLE -> {
                val path = Path()
                path.moveTo((l + r) / 2f, Math.min(t, b))
                path.lineTo(Math.max(l, r), Math.max(t, b))
                path.lineTo(Math.min(l, r), Math.max(t, b))
                path.close()
                canvas.drawPath(path, paint)
            }
            Annot.Shape.KIND_STAR -> {
                val path = Path()
                val cx = (l + r) / 2f
                val cy = (t + b) / 2f
                val rx = Math.abs(r - l) / 2f
                val ry = Math.abs(b - t) / 2f
                for (i in 0 until 10) {
                    val ang = -Math.PI / 2 + i * Math.PI / 5
                    val k = if (i % 2 == 0) 1f else 0.42f
                    val px = cx + (rx * k * Math.cos(ang)).toFloat()
                    val py = cy + (ry * k * Math.sin(ang)).toFloat()
                    if (i == 0) path.moveTo(px, py) else path.lineTo(px, py)
                }
                path.close()
                canvas.drawPath(path, paint)
            }
            else -> canvas.drawRect(Math.min(l, r), Math.min(t, b), Math.max(l, r), Math.max(t, b), paint)
        }
    }
}
