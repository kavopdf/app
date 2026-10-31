package com.kavopdf.app.util

import android.content.Context
import java.io.File

/**
 * Keeps the working cache from growing without bound.
 *
 * Everything the app works on is copied into cacheDir/work: the document you picked, the
 * intermediate PDFs, and the output before it is handed to the place you chose. None of it
 * used to be removed when a job finished. The only cleanup ran once at start-up, dropped
 * only files older than six hours, and never looked at the cache root at all - which is
 * where LinksActivity writes its icon overlays. A few documents in one day could therefore
 * leave gigabytes behind that only Android itself would ever clear.
 *
 * Two rules now:
 *   - a screen deletes the files it made when it closes (PdfActivity.onDestroy), except the
 *     one it just shared or opened, which another app may still be reading;
 *   - this sweep removes whatever is left: anything past its age limit, in work/ and in the
 *     cache root.
 *
 * The age rule itself lives in CachePolicy, which is plain Java so it can be tested.
 */
object CacheSweep {

    @Volatile
    private var lastRunAt = 0L

    private val lock = Any()

    /**
     * Sweep in the background. [force] skips the once-a-minute debounce; without it a
     * screen opening and closing repeatedly cannot cause a directory listing each time.
     */
    fun sweep(context: Context, force: Boolean = false) {
        val now = System.currentTimeMillis()
        synchronized(lock) {
            if (!force && now - lastRunAt < 60_000L) return
            lastRunAt = now
        }
        val app = context.applicationContext
        Thread {
            try {
                run(app)
            } catch (_: Throwable) {
                // A cache sweep must never be the reason something else fails.
            }
        }.start()
    }

    private fun run(context: Context) {
        val now = System.currentTimeMillis()
        sweepDir(File(context.cacheDir, "work"), now)
        sweepDir(context.cacheDir, now)
    }

    private fun sweepDir(dir: File, now: Long) {
        dir.listFiles()?.forEach { f ->
            if (!f.isFile) return@forEach
            val age = now - f.lastModified()
            if (CachePolicy.isStale(f.name, age)) f.delete()
        }
    }

    /** Delete these now. Used by a screen that is closing. */
    fun deleteNow(files: Collection<File>) {
        files.forEach { f ->
            try {
                if (f.exists()) f.delete()
            } catch (_: Throwable) {
            }
        }
    }
}
