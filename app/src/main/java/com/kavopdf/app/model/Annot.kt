package com.kavopdf.app.model

import android.graphics.Bitmap
import android.graphics.PointF

/**
 * An annotation, stored in normalised page coordinates (fractions of page width /
 * height, origin top-left). Preview and export use the same numbers, so what you
 * see is what you get.
 */
sealed class Annot {

    abstract fun copy(): Annot

    class Text(
        var fx: Float, var fy: Float, var sizePt: Float, var color: Int, var text: String
    ) : Annot() {
        override fun copy() = Text(fx, fy, sizePt, color, text)
    }

    class Highlight(
        var fx: Float, var fy: Float, var fw: Float, var fh: Float, var color: Int
    ) : Annot() {
        override fun copy() = Highlight(fx, fy, fw, fh, color)
    }

    /** Opaque rectangle used to cover existing text before retyping over it. */
    class Cover(
        var fx: Float, var fy: Float, var fw: Float, var fh: Float, var color: Int
    ) : Annot() {
        override fun copy() = Cover(fx, fy, fw, fh, color)
    }

    class Stroke(
        val points: MutableList<PointF>, var widthPt: Float, var color: Int, var opacity: Float = 1f,
        /**
         * A ruled or grid line the app put on the page. It is page furniture, not ink,
         * so no eraser removes it - the whole-stroke eraser used to wipe a whole grid
         * away with one touch.
         */
        var guide: Boolean = false
    ) : Annot() {
        override fun copy() =
            Stroke(points.map { PointF(it.x, it.y) }.toMutableList(), widthPt, color, opacity, guide)
    }

    class Stamp(
        var fx: Float, var fy: Float, var fw: Float, var fh: Float, val bitmap: Bitmap
    ) : Annot() {
        override fun copy() = Stamp(fx, fy, fw, fh, bitmap)
    }

    /** A rectangle or an arrow, drawn as an outline. */
    class Shape(
        var fx: Float, var fy: Float, var fw: Float, var fh: Float,
        var color: Int, var widthPt: Float, var kind: Int = KIND_RECT,
        var flipX: Boolean = false, var flipY: Boolean = false
    ) : Annot() {
        override fun copy() = Shape(fx, fy, fw, fh, color, widthPt, kind, flipX, flipY)

        companion object {
            const val KIND_RECT = 0
            const val KIND_ELLIPSE = 1
            const val KIND_LINE = 2
            const val KIND_ARROW = 3
            const val KIND_TRIANGLE = 4
            const val KIND_STAR = 5
            val NAMES = arrayOf("Rectangle", "Ellipse", "Line", "Arrow", "Triangle", "Star")
        }
    }
}
