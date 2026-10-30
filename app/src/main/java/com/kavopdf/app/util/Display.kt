package com.kavopdf.app.util

import android.app.Activity
import android.os.Build

/**
 * Let the window run at the fastest refresh the screen can do.
 *
 * Android gives an app the display's default mode, which on a 120 Hz phone is usually
 * 60 Hz - the panel is capable of twice the frames and the app never asks for them, so
 * scrolling looks the same as on a cheap phone. `preferredRefreshRate` is a hint: the
 * system honours it when the panel supports that rate and ignores it otherwise, so this
 * costs nothing on a 60 Hz device and does not change anything if it is refused.
 *
 * Called from every screen, because the rate belongs to the window and each activity
 * gets a fresh one.
 */
fun Activity.useHighestRefreshRate() {
    try {
        val display = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            display
        } else {
            @Suppress("DEPRECATION")
            windowManager.defaultDisplay
        } ?: return

        val modes = try {
            display.supportedModes
        } catch (_: Throwable) {
            null
        }
        val fastest = modes
            ?.filter { it.physicalWidth > 0 && it.physicalHeight > 0 }
            ?.maxByOrNull { it.refreshRate }
            ?.refreshRate
            ?: try {
                @Suppress("DEPRECATION")
                display.refreshRate
            } catch (_: Throwable) {
                null
            }

        // Anything at or below the usual 60 Hz needs no request at all.
        if (fastest == null || fastest <= 60.5f) return

        val attrs = window.attributes
        attrs.preferredRefreshRate = fastest
        window.attributes = attrs
    } catch (_: Throwable) {
        // A window that refuses the hint keeps its default rate; nothing to report.
    }
}
