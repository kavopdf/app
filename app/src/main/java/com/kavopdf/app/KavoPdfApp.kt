package com.kavopdf.app

import android.app.Application
import androidx.appcompat.app.AppCompatDelegate
import com.tom_roush.pdfbox.android.PDFBoxResourceLoader

/** Initialises PDFBox and applies the saved theme before any UI is created. */
class KavoPdfApp : Application() {
    override fun onCreate() {
        super.onCreate()
        AppCompatDelegate.setDefaultNightMode(when (themePref(this)) {
            1 -> AppCompatDelegate.MODE_NIGHT_NO
            2 -> AppCompatDelegate.MODE_NIGHT_YES
            else -> AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
        })
        PDFBoxResourceLoader.init(applicationContext)
        // Decide once how much memory a page bitmap may use on THIS device, so a budget
        // phone and a flagship both render the same page without either running out.
        com.kavopdf.app.ui.PageRenderer.configure(this)
        // The OCR layer writes exact characters (rupee sign, dashes, subscripts) with an
        // embedded Unicode font. Read once here so the engine needs no Context.
        loadOcrFont()
        cleanStaleCache()
        com.kavopdf.app.util.CrashGuard.install(this)
    }

    /**
     * The system is short of memory. A budget phone hits this constantly; a flagship
     * almost never. Shrink the page budget and clear the temp copies so the app keeps
     * working instead of being killed in the background.
     */
    override fun onTrimMemory(level: Int) {
        super.onTrimMemory(level)
        try {
            if (level >= android.content.ComponentCallbacks2.TRIM_MEMORY_RUNNING_LOW) {
                com.kavopdf.app.ui.PageRenderer.reduceBudget()
            }
            if (level >= android.content.ComponentCallbacks2.TRIM_MEMORY_RUNNING_CRITICAL) {
                cleanStaleCache()
            }
        } catch (_: Throwable) {
        }
    }

    /** Older platforms call this instead of onTrimMemory. */
    override fun onLowMemory() {
        super.onLowMemory()
        try {
            com.kavopdf.app.ui.PageRenderer.reduceBudget()
        } catch (_: Throwable) {
        }
    }

    /** Documents are copied to the cache while they are worked on; drop old ones so
     *  nothing lingers on the device longer than it needs to. */
    private fun cleanStaleCache() {
        Thread {
            try {
                val dir = java.io.File(cacheDir, "work")
                val cutoff = System.currentTimeMillis() - 6L * 3600_000L
                dir.listFiles()?.forEach { if (it.lastModified() < cutoff) it.delete() }
            } catch (_: Exception) {
            }
        }.start()
    }

    companion object {
        const val PREFS = "kavopdf"
        const val KEY_THEME = "theme"
        const val KEY_ACCENT = "accent"

        fun themePref(context: android.content.Context): Int =
            context.getSharedPreferences(PREFS, MODE_PRIVATE).getInt(KEY_THEME, 0)

        fun setThemePref(context: android.content.Context, mode: Int) {
            context.getSharedPreferences(PREFS, MODE_PRIVATE).edit().putInt(KEY_THEME, mode).apply()
        }

        fun accentPref(context: android.content.Context): Int =
            context.getSharedPreferences(PREFS, MODE_PRIVATE).getInt(KEY_ACCENT, 5)

        fun setAccentPref(context: android.content.Context, index: Int) {
            context.getSharedPreferences(PREFS, MODE_PRIVATE).edit().putInt(KEY_ACCENT, index).apply()
        }
    }

    /**
     * Hand the OCR layer its Unicode font. If the asset is missing or unreadable the
     * engine keeps using Helvetica, so a build without the font still works - it just
     * substitutes the rupee sign instead of writing it.
     */
    private fun loadOcrFont() {
        try {
            assets.open("fonts/NotoSans-Regular.ttf").use { input ->
                val bytes = input.readBytes()
                if (bytes.isNotEmpty()) com.kavopdf.app.engine.PdfEngine.setOcrFont(bytes)
            }
        } catch (_: Throwable) {
            // no font: the layer falls back to Helvetica
        }
    }
}
