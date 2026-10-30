package com.kavopdf.app.ui

import android.app.ActivityManager
import android.content.Context
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.Matrix
import android.graphics.pdf.PdfRenderer

/**
 * Renders PDF pages to bitmaps using the platform renderer (fast, offline).
 *
 * Every page goes through here, so this is the one place where the app can behave the
 * same on a 2 GB budget phone and a 12 GB flagship. Two rules do that:
 *
 *   1. A page bitmap is never allowed to take more than a fixed share of the heap this
 *      device actually gave us. The old code allowed 6000 px wide, which on an A4 page
 *      is 6000 x 8485 x 4 bytes = 203 MB - an instant OutOfMemoryError on anything
 *      cheap, while a flagship never noticed.
 *   2. If the allocation still fails, the size is halved and retried, so a page always
 *      renders rather than crashing the screen.
 */
class PageRenderer(private val renderer: PdfRenderer) {

    val pageCount: Int get() = renderer.pageCount

    @Synchronized
    fun render(index: Int, targetWidth: Int, rotation: Int = 0): Bitmap {
        val page = renderer.openPage(index)
        try {
            if (page.width <= 0 || page.height <= 0) {
                return Bitmap.createBitmap(1, 1, Bitmap.Config.ARGB_8888)
            }
            val ratio = page.height.toFloat() / page.width.toFloat()
            var w = targetWidth.coerceIn(1, MAX_SIDE)
            // never let one page exceed this device's own budget
            val allowed = maxPixels
            while (w > MIN_SIDE && (w.toLong() * (w * ratio).toLong()) > allowed) {
                w /= 2
            }
            var attempt = 0
            while (true) {
                val h = (w * ratio).toInt().coerceAtLeast(1)
                try {
                    // PdfRenderer refuses anything but ARGB_8888 - it throws
                    // IllegalArgumentException("Unsupported pixel format") and the page
                    // never appears. Memory is saved by drawing fewer pixels, never by
                    // dropping to 16-bit colour.
                    val bmp = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
                    bmp.eraseColor(Color.WHITE)
                    page.render(bmp, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
                    return rotate(bmp, w, h, rotation)
                } catch (oom: OutOfMemoryError) {
                    // cheaper phone, or another screen holding memory: go smaller
                    if (attempt >= 3 || w <= MIN_SIDE) throw oom
                    attempt++
                    w /= 2
                }
            }
        } finally {
            page.close()
        }
    }

    private fun rotate(bmp: Bitmap, w: Int, h: Int, rotation: Int): Bitmap {
        val deg = ((rotation % 360) + 360) % 360
        if (deg == 0) return bmp
        val m = Matrix().apply { postRotate(deg.toFloat()) }
        val rotated = Bitmap.createBitmap(bmp, 0, 0, w, h, m, true)
        if (rotated != bmp) bmp.recycle()
        return rotated
    }

    @Synchronized
    fun close() {
        try { renderer.close() } catch (_: Exception) { }
    }

    companion object {
        /** Hard ceiling on a page's short side, whatever the caller asks for. */
        private const val MAX_SIDE = 4000
        private const val MIN_SIDE = 240

        /** Pixels allowed per page, decided once per process. */
        @Volatile private var maxPixels: Long = 4_000_000L

        /**
         * How much memory the reader's page cache may hold. A fixed number was backwards:
         * 72 MB is a fifth of the heap on a 2 GB phone and a seventh on a flagship, so the
         * cheap device was the one at risk. It is now a sixth of whatever this device
         * grants the app, so a flagship keeps more pages ready and a budget phone keeps
         * fewer.
         */
        @Volatile private var cacheBudget: Int = 48 * 1024 * 1024

        /**
         * Called once at start-up. A low-RAM device gets a smaller page budget, so a page
         * is drawn with fewer pixels; the bitmap format is always ARGB_8888 because that
         * is the only one PdfRenderer can draw to.
         */
        fun configure(context: Context) {
            try {
                val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
                val mb = am.memoryClass.toLong()          // heap this app may use, in MB
                val lowRam = am.isLowRamDevice
                // Always 4 bytes per pixel: that is the only format PdfRenderer draws to.
                // A low-RAM device gets fewer pixels instead of a cheaper format.
                val bytesPerPixel = 4L
                val share = if (lowRam || mb <= 192L) 6L else 4L
                maxPixels = ((mb * 1024L * 1024L / share) / bytesPerPixel)
                        .coerceIn(400_000L, 16_000_000L)
                cacheBudget = (mb * 1024L * 1024L / 6L)
                        .coerceIn(24L * 1024 * 1024, 192L * 1024 * 1024).toInt()
            } catch (_: Throwable) {
                // keep the conservative defaults
            }
        }

        /**
         * Page sizes from a renderer that is already open. Asking PdfEngine as well
         * loaded the whole document a second time with pdfbox - the slowest thing in
         * every open path. Used by the reader, crop, links and redact screens.
         */
        fun displaySizes(r: PdfRenderer): List<FloatArray> {
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

        /** For tests: what the current budget works out to. */
        fun budgetPixels(): Long = maxPixels

        /** Memory the reader's page cache may use on this device. */
        fun cacheBytes(): Int = cacheBudget

        /**
         * The system told us it is short of memory. Halve the page budget so the next
         * render is smaller instead of failing, and drop to 16-bit colour. A phone that
         * is under pressure keeps working; nothing else changes.
         */
        fun reduceBudget() {
            try {
                // Only the pixel count changes. Switching the bitmap format here used to
                // break every later render, because PdfRenderer rejects anything but
                // ARGB_8888 - the screen went black until the app was restarted.
                maxPixels = (maxPixels / 2).coerceAtLeast(400_000L)
            } catch (_: Throwable) {
            }
        }
    }
}
