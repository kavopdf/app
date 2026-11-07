package com.kavopdf.app.ui

import android.graphics.RectF
import android.widget.ImageView

/**
 * Where is the page actually drawn inside an ImageView, in view coordinates?
 *
 * A plain ImageView with scaleType="fitCenter" places the image itself and leaves
 * imageMatrix as identity, so mapping through imageMatrix gives nonsense. A
 * ZoomableImageView uses scaleType="matrix" and does keep imageMatrix up to date.
 * This handles both, so a box drawn on screen always maps to the right spot on the
 * page no matter which kind of view is showing it.
 */
internal fun drawnImageRect(iv: ImageView, out: RectF): Boolean {
    val d = iv.drawable ?: return false
    val dw = d.intrinsicWidth.toFloat()
    val dh = d.intrinsicHeight.toFloat()
    if (dw <= 0f || dh <= 0f) return false

    if (iv.scaleType == ImageView.ScaleType.MATRIX) {
        val pts = floatArrayOf(0f, 0f, dw, dh)
        iv.imageMatrix.mapPoints(pts)
        out.set(pts[0], pts[1], pts[2], pts[3])
        return out.width() > 0f && out.height() > 0f
    }

    // fitCentre: the framework scales to fit and centres the result
    val padL = iv.paddingLeft.toFloat()
    val padT = iv.paddingTop.toFloat()
    val contentW = (iv.width - iv.paddingLeft - iv.paddingRight).toFloat()
    val contentH = (iv.height - iv.paddingTop - iv.paddingBottom).toFloat()
    if (contentW <= 0f || contentH <= 0f) return false
    val scale = minOf(contentW / dw, contentH / dh)
    val w = dw * scale
    val h = dh * scale
    val left = padL + (contentW - w) / 2f
    val top = padT + (contentH - h) / 2f
    out.set(left, top, left + w, top + h)
    return true
}
