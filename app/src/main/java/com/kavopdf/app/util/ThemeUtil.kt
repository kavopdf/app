package com.kavopdf.app.util

import android.app.Activity
import android.content.Context
import androidx.annotation.StyleRes
import com.kavopdf.app.KavoPdfApp
import com.kavopdf.app.R

/** Applies the user's chosen accent colour theme to an Activity. */
object ThemeUtil {

    val ACCENTS: List<Pair<String, Int>> = listOf(
        "Indigo" to R.style.Theme_KavoPDF,
        "Teal" to R.style.Theme_KavoPDF_Teal,
        "Violet" to R.style.Theme_KavoPDF_Violet,
        "Green" to R.style.Theme_KavoPDF_Green,
        "Crimson" to R.style.Theme_KavoPDF_Crimson,
        "Amber" to R.style.Theme_KavoPDF_Amber
    )

    @StyleRes
    fun themeRes(context: Context): Int {
        val i = KavoPdfApp.accentPref(context).coerceIn(0, ACCENTS.size - 1)
        return ACCENTS[i].second
    }

    /** Call before setContentView(). */
    fun apply(activity: Activity) {
        activity.setTheme(themeRes(activity))
    }
}
