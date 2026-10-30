package com.kavopdf.app.ui

import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.Matrix
import android.graphics.pdf.PdfRenderer

/** Renders PDF pages to bitmaps using the platform renderer (fast, offline). */
class PageRenderer(private val renderer: PdfRenderer) {

    val pageCount: Int get() = renderer.pageCount

    @Synchronized
    fun render(index: Int, targetWidth: Int, rotation: Int = 0): Bitmap {
        val page = renderer.openPage(index)
        try {
            if (page.width <= 0 || page.height <= 0) return Bitmap.createBitmap(1, 1, Bitmap.Config.ARGB_8888)
            val ratio = page.height.toFloat() / page.width.toFloat()
            val w = targetWidth.coerceIn(1, 6000)
            val h = (w * ratio).toInt().coerceAtLeast(1)
            val bmp = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
            bmp.eraseColor(Color.WHITE)
            page.render(bmp, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
            val deg = ((rotation % 360) + 360) % 360
            if (deg == 0) return bmp
            val m = Matrix().apply { postRotate(deg.toFloat()) }
            val rotated = Bitmap.createBitmap(bmp, 0, 0, w, h, m, true)
            if (rotated != bmp) bmp.recycle()
            return rotated
        } finally {
            page.close()
        }
    }

    @Synchronized
    fun close() {
        try { renderer.close() } catch (_: Exception) { }
    }
    companion object {
        /**
         * Page sizes from a renderer that is already open. Asking PdfEngine as well
         * loaded the whole document a second time with pdfbox - the slowest thing in
         * every open path.
         */
        fun displaySizes(r: android.graphics.pdf.PdfRenderer): List<FloatArray> {
            val out = ArrayList<FloatArray>(r.pageCount)
            for (i in 0 until r.pageCount) {
                val pg = r.openPage(i)
                try {
                    out.add(floatArrayOf(pg.width.toFloat(), pg.height.toFloat()))
                } finally {
                    pg.close()
                }
            }
            return out
        }
    }

}
