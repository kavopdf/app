package com.kavopdf.app.util

import android.content.Context
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * A plain, local record of what the app has done and when.
 *
 * It lives in the app's own private storage, is never uploaded anywhere, and is
 * capped so it cannot grow without bound. Passwords and document contents are
 * never written here - only the task name, the file it produced, and the outcome.
 *
 * A detail may be many lines long (a crash report is), so newlines are escaped
 * rather than flattened, and the size limit is generous enough to keep a full
 * stack trace intact.
 */
object AppLog {

    private const val FILE_NAME = "kavopdf-activity.log"
    private const val MAX_BYTES = 512 * 1024

    /** Room for a whole crash report; the old 300 was cutting them in half. */
    private const val MAX_DETAIL = 8000

    private const val NEWLINE = "\\n"
    private const val TAB = "\\t"

    private val lock = Any()

    /** Three outcomes, because "slow" is not a failure. */
    enum class Level { OK, SLOW, FAIL }

    data class Entry(val time: Long, val level: Level, val action: String, val detail: String) {
        val ok: Boolean get() = level == Level.OK
    }

    private fun file(ctx: Context) = File(ctx.filesDir, FILE_NAME)

    fun record(ctx: Context, action: String, detail: String = "", ok: Boolean = true) =
        record(ctx, action, detail, if (ok) Level.OK else Level.FAIL)

    /** Logs a failure with the real cause, for the log - never for the screen. */
    fun problem(ctx: Context, action: String, t: Throwable) {
        val detail = t.javaClass.simpleName + ": " + (t.message ?: "")
        record(ctx, action, detail, Level.FAIL)
    }

    // A repeated SLOW for the same action within a minute is the same problem, not a
    // new one - the log showed FormsActivity twice in three minutes. Repeats are
    // counted and written as "(xN)" instead of a fresh entry each time, so nothing is
    // hidden but the log stays readable.
    private var lastSlow = ""
    private var lastSlowAt = 0L
    private var lastSlowCount = 0
    private var lastFail = ""
    private var lastFailAt = 0L
    private var lastFailCount = 0

    fun record(ctx: Context, action: String, detail: String, level: Level) {
        synchronized(lock) {
            try {
                val f = file(ctx)
                // keep the file bounded: when it gets big, drop the older half
                if (f.length() > MAX_BYTES) {
                    val lines = f.readLines()
                    f.writeText(lines.drop(lines.size / 2).joinToString("\n") + "\n")
                }
                var detailOut = detail
                if (level == Level.SLOW) {
                    val key = action + "|" + detail.lineSequence().firstOrNull().orEmpty()
                    val now = System.currentTimeMillis()
                    if (key == lastSlow && now - lastSlowAt < 60000L) {
                        lastSlowCount++
                        lastSlowAt = now
                        return@synchronized   // already recorded, just counted
                    }
                    if (key == lastSlow && lastSlowCount > 0) detailOut = detail + "\n(x$lastSlowCount more)"
                    lastSlow = key
                    lastSlowAt = now
                    lastSlowCount = 0
                }
                // A crash loop at startup wrote one entry per launch and buried
                // everything else. The same failure within ten minutes is one event;
                // repeats are counted instead of written again.
                if (level == Level.FAIL) {
                    val key = action + "|" + detail.lineSequence().firstOrNull().orEmpty()
                    val now = System.currentTimeMillis()
                    if (key == lastFail && now - lastFailAt < 600000L) {
                        lastFailCount++
                        lastFailAt = now
                        return@synchronized
                    }
                    if (key == lastFail && lastFailCount > 0) detailOut = detail + "\n(x$lastFailCount more)"
                    lastFail = key
                    lastFailAt = now
                    lastFailCount = 0
                }
                val line = buildString {
                    append(System.currentTimeMillis()).append('\t')
                    append(level.name).append('\t')
                    append(clean(action)).append('\t')
                    append(cleanDetail(detailOut))
                }
                f.appendText(line + "\n")
            } catch (_: Exception) {
                // logging must never break a task
            }
        }
    }

    fun entries(ctx: Context): List<Entry> = try {
        file(ctx).readLines().mapNotNull { raw ->
            val p = raw.split('\t')
            if (p.size < 4) return@mapNotNull null
            val level = when (p[1]) {
                "OK" -> Level.OK
                "SLOW" -> Level.SLOW
                else -> Level.FAIL
            }
            Entry(p[0].toLongOrNull() ?: 0L, level, p[2], unescape(p.drop(3).joinToString("\t")))
        }
    } catch (_: Exception) {
        emptyList()
    }

    fun clear(ctx: Context) {
        synchronized(lock) { runCatching { file(ctx).delete() } }
    }

    /** One readable block, used by the screen and the exported PDF. */
    fun format(e: Entry): String {
        val head = "${stampFor(e.time)}   ${label(e.level)}   ${stripSlowPrefix(e.action)}"
        return if (e.detail.isEmpty()) head else "$head\n${e.detail}"
    }

    fun label(level: Level): String = when (level) {
        Level.OK -> "OK  "
        Level.SLOW -> "SLOW"
        Level.FAIL -> "FAIL"
    }

    private fun stampFor(time: Long): String =
        SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(Date(time))

    /** Single-line field: tabs and newlines escaped so the file stays line-based. */
    private fun clean(s: String): String =
        s.replace("\\", "\\\\").replace("\t", TAB).replace("\n", NEWLINE).take(400)

    /** Multi-line field: newlines survive as escapes, and a whole report fits. */
    private fun cleanDetail(s: String): String =
        s.replace("\\", "\\\\").replace("\t", TAB).replace("\n", NEWLINE).take(MAX_DETAIL)

    private fun unescape(s: String): String {
        val sb = StringBuilder(s.length)
        var i = 0
        while (i < s.length) {
            val c = s[i]
            if (c == '\\' && i + 1 < s.length) {
                when (s[i + 1]) {
                    'n' -> { sb.append('\n'); i += 2; continue }
                    't' -> { sb.append('\t'); i += 2; continue }
                    '\\' -> { sb.append('\\'); i += 2; continue }
                }
            }
            sb.append(c)
            i++
        }
        return sb.toString()
    }
    private fun stripSlowPrefix(action: String): String =
        if (action.startsWith("Slow: ")) action.removePrefix("Slow: ") else action

}
