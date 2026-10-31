package com.kavopdf.app.util

import android.app.Activity
import android.view.LayoutInflater
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import com.kavopdf.app.R

/**
 * Keep content out from under the camera cutout now that the window is allowed to use it.
 *
 * The theme asks for the whole display (shortEdges). In portrait that changes nothing -
 * the status bar already holds content below the notch - so only the LEFT and RIGHT safe
 * insets are applied: those are what matter in landscape, where a punch-hole sits beside
 * the toolbar. Padding the top as well would double-count the status bar and push every
 * screen down by the notch height.
 *
 * Below Android 9 there is no cutout, so nothing happens at all.
 */
fun applyCutoutInsets(activity: Activity) {
    val content = activity.findViewById<android.view.View>(android.R.id.content) ?: return
    content.setOnApplyWindowInsetsListener { v, insets ->
        if (android.os.Build.VERSION.SDK_INT >= 28) {
            val cut = insets.displayCutout
            if (cut != null) {
                v.setPadding(cut.safeInsetLeft, 0, cut.safeInsetRight, 0)
            }
        }
        insets
    }
    content.requestApplyInsets()
}

/** A simple, non-cancelable progress dialog used while the engine works. */
class Busy(private val activity: Activity) {
    private var dialog: AlertDialog? = null
    private val hideHandler = android.os.Handler(android.os.Looper.getMainLooper())
    private var hidePending: Runnable? = null
    private var text: TextView? = null

    private fun alive() = !activity.isFinishing && !activity.isDestroyed

    fun show(text: String) {
        if (!alive()) return
        // A task that follows immediately (open the file, then render it) used to
        // dismiss and re-show the card, which flashed. The dismiss now happens on the
        // next frame, so a task that starts straight away cancels it and keeps the
        // same card up - and the last card still goes the moment the work ends.
        hidePending?.let { hideHandler.removeCallbacks(it); hidePending = null }
        val existing = dialog
        if (existing != null && existing.isShowing) {
            this.text?.text = text
            return
        }
        dismiss()
        val view = LayoutInflater.from(activity).inflate(R.layout.dialog_busy, null)
        this.text = view.findViewById(R.id.busyText)
        this.text?.text = text
        dialog = AlertDialog.Builder(activity).setView(view).setCancelable(false).create()
        dialog?.show()
        // dead centre, and a little wider than the default dialog margin allows
        dialog?.window?.setGravity(android.view.Gravity.CENTER)
        dialog?.window?.attributes = dialog?.window?.attributes?.apply { y = 0 }
    }

    /** Update the message while work is in progress (e.g. "page 3 of 12"). */
    fun update(message: String) {
        if (!alive()) return
        text?.text = message
    }

    fun dismiss() {
        val d = dialog ?: return
        if (hidePending != null) return
        val r = Runnable {
            hidePending = null
            if (dialog === d) {
                dialog = null
                try { d.dismiss() } catch (_: Exception) { }
            }
        }
        hidePending = r
        hideHandler.post(r)   // next frame: a follow-up task cancels this
    }

    /** Dismiss now, no waiting. */
    fun dismissNow() {
        hidePending?.let { hideHandler.removeCallbacks(it) }
        hidePending = null
        try { dialog?.dismiss() } catch (_: Exception) { }
        dialog = null
    }
}

