package com.kavopdf.app.util

import android.app.Activity
import android.content.Context
import android.view.WindowManager

/**
 * Let the window run at the fastest refresh the screen can do.
 *
 * Android hands an app the display's default mode, which on a 120 Hz phone is usually
 * 60 Hz - the panel can do twice the frames and the app never asks for them, so scrolling
 * looks the same as on a cheap phone. `preferredRefreshRate` is a hint: the system honours
 * it when the panel supports that rate and ignores it otherwise, so this costs nothing on
 * a 60 Hz device.
 *
 * Called from every screen, because the rate belongs to the window and each activity gets
 * a fresh one.
 */
fun Activity.useHighestRefreshRate() {
    try {
        val wm = getSystemService(Context.WINDOW_SERVICE) as? WindowManager ?: return

        @Suppress("DEPRECATION")
        val d = wm.defaultDisplay ?: return

        // supportedModes lists every mode the panel can switch to; the fastest wins.
        val fromModes: Float? = try {
            d.supportedModes
                ?.filter { it.physicalWidth > 0 && it.physicalHeight > 0 }
                ?.maxByOrNull { it.refreshRate }
                ?.refreshRate
        } catch (_: Throwable) {
            null
        }

        val fastest: Float = fromModes ?: try {
            @Suppress("DEPRECATION")
            d.refreshRate
        } catch (_: Throwable) {
            0f
        }

        // Anything at or below the usual 60 Hz needs no request at all.
        if (fastest <= 60.5f) return

        val attrs = window.attributes
        attrs.preferredRefreshRate = fastest
        window.attributes = attrs
    } catch (_: Throwable) {
        // A window that refuses the hint keeps its default rate; nothing to report.
    }
}
