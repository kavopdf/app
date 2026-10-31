package com.kavopdf.app.util

import android.content.Context
import android.os.Build
import com.kavopdf.app.engine.Diag
import com.kavopdf.app.engine.NormStore
import com.kavopdf.app.engine.Stalls

/**
 * The one place that records problems.
 *
 * Everything here is deliberately quiet: it writes to the activity log only when
 * something actually went wrong. Normal use leaves the log exactly as it was.
 *
 * Breadcrumbs live in memory ([Diag]) and are only written out when a crash or a
 * genuinely slow step happens - that is what makes a crash report complete while
 * keeping the log clean.
 */
object CrashGuard {

    @Volatile
    private var installed = false

    /** Held back only to be released when memory runs out, so the report can be written. */
    @Volatile
    private var reserve: ByteArray? = ByteArray(1 shl 20)

    /** When this process started, for the uptime line in a report. */
    private var startedAt = android.os.SystemClock.elapsedRealtime()

    /** Remember what the app just did. Memory only, cheap, cannot fail. */
    fun step(what: String) {
        try {
            Diag.breadcrumb(what)
        } catch (_: Throwable) {
        }
    }

    /** Record a handled failure. Only call this when something really failed. */
    fun problem(context: Context?, action: String, error: Throwable?) {
        if (context == null) return
        try {
            val app = context.applicationContext
            val detail = buildString {
                append(Diag.describe(error))
                val crumbs = Diag.crumbBlock()
                if (crumbs.isNotEmpty()) append("\n").append(crumbs)
                append("\n").append(environment(app))
            }
            AppLog.record(app, action, detail, false)
        } catch (_: Throwable) {
        }
    }

    /**
     * Run something and record it only when it is genuinely slower than this
     * device's own norm for that tool. The work itself is untouched - same result,
     * same exceptions, same timing.
     */
    fun <T> timed(context: Context?, name: String, pages: Int = 1, bytes: Long = 0L, block: () -> T): T {
        val started = System.currentTimeMillis()
        var finished = false
        return try {
            block().also { finished = true }
        } finally {
            // a run that threw says nothing about how long this tool normally takes
            if (finished) note(context, name, pages, bytes, System.currentTimeMillis() - started)
        }
    }

    /**
     * Anything run this soon after the process started is measuring warm-up, not the
     * app: the JIT has not compiled anything yet and the dex may still be optimising.
     * Learning from those runs made every later healthy run look fast.
     */
    private const val COLD_MS = 60_000L

    /** Compare one finished run against the norm and learn from it. */
    private fun note(context: Context?, name: String, pages: Int, bytes: Long, took: Long) {
        if (context == null) return
        try {
            val app = context.applicationContext
            // warm-up runs are neither judged nor learned from
            if (android.os.SystemClock.elapsedRealtime() - startedAt < COLD_MS) return
            val norms = loadNorms(app)
            if (norms.isAnomalous(name, pages, bytes, took)) {
                val norm = norms.normFor(name, pages, bytes)
                AppLog.record(
                    app,
                    name,
                    "took ${took}ms, normal is ${norm}ms " +
                            "(${NormStore.bucket(pages)} pages, ${NormStore.sizeBucket(bytes)} size)\n" +
                            environment(app),
                    AppLog.Level.SLOW
                )
            }
            norms.record(name, pages, bytes, took)   // healthy runs teach; a stall never does
            saveNorms(app, norms)
        } catch (_: Throwable) {
        }
    }

    /**
     * Bumped whenever the norms learned by an older build no longer describe this
     * one. Their numbers were measured under different behaviour (the reader used
     * to load three things at once), so keeping them would flag perfectly normal
     * work as slow for ever.
     */
    private const val NORMS_VERSION = 3

    @Volatile
    private var normsCache: NormStore? = null

    private fun loadNorms(context: Context): NormStore {
        normsCache?.let { return it }
        val loaded = try {
            val prefs = context.getSharedPreferences("diag_norms", Context.MODE_PRIVATE)
            if (prefs.getInt("version", 0) != NORMS_VERSION) {
                // learned by an older build: start clean rather than trust stale numbers
                prefs.edit().clear().putInt("version", NORMS_VERSION).apply()
                NormStore()
            } else {
                NormStore.fromText(prefs.getString("data", ""))
            }
        } catch (_: Throwable) {
            NormStore()
        }
        normsCache = loaded
        return loaded
    }

    private fun saveNorms(context: Context, norms: NormStore) {
        try {
            context.getSharedPreferences("diag_norms", Context.MODE_PRIVATE)
                .edit().putString("data", norms.toText()).putInt("version", NORMS_VERSION).apply()
        } catch (_: Throwable) {
        }
    }

    /**
     * Dispatchers.IO with the stopwatch attached. Same thread, same result - the
     * only difference is that a background load is now measured like a tool.
     */
    suspend fun <T> io(
        context: Context?,
        name: String,
        pages: Int = 1,
        block: suspend kotlinx.coroutines.CoroutineScope.() -> T
    ): T = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
        val started = System.currentTimeMillis()
        var finished = false
        try {
            block().also { finished = true }
        } finally {
            if (finished) note(context, name, pages, 0L, System.currentTimeMillis() - started)
        }
    }

    /**
     * Install the global handler. A crash is recorded with everything needed to
     * fix it, then the process is allowed to die exactly as it would have.
     */
    fun install(context: Context) {
        if (installed) return
        installed = true
        val app = context.applicationContext
        // B7: a launch that ended while it was still in front of the user is the shape of
        // a crash. The flag used to be cleared by a five-second timer instead, so any
        // launch that was closed inside five seconds - or reclaimed by Android - reported
        // "the app stopped before it finished starting" on the next start. Those entries
        // all carried uptime=0s and a near-empty heap, which is a process that ended
        // normally, not one that crashed.
        //
        // It is now driven by the activity lifecycle: set while the app is in front,
        // cleared the moment it goes behind another app. A kill in the background is
        // normal and is never reported; an end while in front still is.
        try {
            val boot = app.getSharedPreferences("diag_boot", Context.MODE_PRIVATE)
            if (boot.getBoolean("running", false)) {
                AppLog.record(app, "Previous launch crashed",
                    "the app stopped while it was in the foreground\n" + environment(app), false)
            }
            boot.edit().putBoolean("running", false).commit()
            app.registerActivityLifecycleCallbacks(
                object : android.app.Application.ActivityLifecycleCallbacks {
                    private var started = 0

                    override fun onActivityStarted(activity: android.app.Activity) {
                        if (started == 0) {
                            try { boot.edit().putBoolean("running", true).commit() } catch (_: Throwable) {}
                        }
                        started++
                    }

                    override fun onActivityStopped(activity: android.app.Activity) {
                        if (started > 0) started--
                        if (started == 0) {
                            try { boot.edit().putBoolean("running", false).apply() } catch (_: Throwable) {}
                        }
                    }

                    override fun onActivityCreated(a: android.app.Activity, b: android.os.Bundle?) {}
                    override fun onActivityResumed(a: android.app.Activity) {}
                    override fun onActivityPaused(a: android.app.Activity) {}
                    override fun onActivitySaveInstanceState(a: android.app.Activity, b: android.os.Bundle) {}
                    override fun onActivityDestroyed(a: android.app.Activity) {}
                }
            )
        } catch (_: Throwable) {
        }

        // B5: a quiet main thread is the first sign of an ANR
        try {
            val handler = android.os.Handler(android.os.Looper.getMainLooper())
            val stalls = Stalls()
            val tick = object : Runnable {
                private var expected = Stalls.TICK_MS
                private var startedInFront = true

                override fun run() {
                    try {
                        val inFront = isForeground(app)
                        // A stall is only real when the beat was running in front of the
                        // user AND it is still in front now. The ticker slows to IDLE_MS
                        // behind another app, and the gap that creates is five seconds
                        // wide - which the detector read as a five-second freeze. Every
                        // "blocked for 5001ms" entry in the log came from exactly that.
                        val blocked = if (startedInFront && inFront) {
                            stalls.onTick(android.os.SystemClock.elapsedRealtime(), expected)
                        } else {
                            stalls.reset()
                            0L
                        }
                        if (blocked > 0L && screenOn(app)) {
                            AppLog.record(
                                app,
                                "Main thread blocked",
                                "for ${blocked}ms\n" + environment(app),
                                AppLog.Level.SLOW
                            )
                        }
                        // 500 ms while the app is in front, where a stall matters and can
                        // be seen; 5 s once it is behind another app, where the tick cannot
                        // catch anything a user would notice.
                        val next = if (inFront) Stalls.TICK_MS else Stalls.IDLE_MS
                        expected = next
                        startedInFront = inFront
                        handler.postDelayed(this, next)
                    } catch (_: Throwable) {
                        expected = Stalls.TICK_MS
                        startedInFront = false
                        handler.postDelayed(this, Stalls.TICK_MS)
                    }
                }
            }
            handler.postDelayed(tick, Stalls.TICK_MS)
        } catch (_: Throwable) {
        }

        val previous = Thread.getDefaultUncaughtExceptionHandler()
        Thread.setDefaultUncaughtExceptionHandler { thread, error ->
            try {
                if (error is OutOfMemoryError) reserve = null   // make room to write
                val detail = buildString {
                    append("thread=").append(thread.name).append("\n")
                    append(Diag.describe(error))
                    val crumbs = Diag.crumbBlock()
                    if (crumbs.isNotEmpty()) append("\n").append(crumbs)
                    append("\n").append(environment(app))
                }
                AppLog.record(app, "Crash: " + (error.javaClass.simpleName), detail, false)
            } catch (_: Throwable) {
            }
            if (previous != null) {
                previous.uncaughtException(thread, error)
            } else {
                // nothing else will kill us - a crash handler that hangs is worse
                // than no crash handler
                try {
                    android.os.Process.killProcess(android.os.Process.myPid())
                } catch (_: Throwable) {
                }
                kotlin.system.exitProcess(10)
            }
        }
    }

    /** Facts that make a report reproducible. */
    private fun environment(context: Context): String = try {
        val pi = context.packageManager.getPackageInfo(context.packageName, 0)
        val rt = Runtime.getRuntime()
        buildString {
            append("app=").append(pi.versionName).append(" (").append(
                if (Build.VERSION.SDK_INT >= 28) pi.longVersionCode else @Suppress("DEPRECATION") pi.versionCode.toLong()
            ).append(")")
            append(" android=").append(Build.VERSION.RELEASE).append(" (API ").append(Build.VERSION.SDK_INT).append(")")
            append(" device=").append(Build.MANUFACTURER).append(" ").append(Build.MODEL)
            // heap = what this app is using of its own limit. It says nothing about
            // whether the device itself was under pressure, so free RAM is recorded too -
            // without it a system kill looks exactly like an app fault.
            append(" heap=").append((rt.totalMemory() - rt.freeMemory()) / 1048576)
                .append("/").append(rt.maxMemory() / 1048576).append("MB")
            try {
                val mi = android.app.ActivityManager.MemoryInfo()
                (context.getSystemService(Context.ACTIVITY_SERVICE) as? android.app.ActivityManager)
                    ?.getMemoryInfo(mi)
                append(" ram=").append(mi.availMem / 1048576)
                    .append("/").append(mi.totalMem / 1048576).append("MB free")
            } catch (_: Throwable) {
            }
            append(" uptime=").append(
                (android.os.SystemClock.elapsedRealtime() - startedAt) / 1000
            ).append("s")
        }
    } catch (_: Throwable) {
        "environment unavailable"
    }
    /** True when this app is the one on screen, so a late tick means a real block. */
    /**
     * False positives come in two flavours: the app in the background, and the screen
     * switched off. Both stop the main thread from receiving its beat, which is
     * indistinguishable from a freeze unless we ask. This asks.
     */
    private fun screenOn(app: android.content.Context): Boolean = try {
        val pm = app.getSystemService(android.content.Context.POWER_SERVICE)
                as android.os.PowerManager
        pm.isInteractive
    } catch (_: Throwable) {
        true
    }

    private fun isForeground(app: android.content.Context): Boolean = try {
        val am = app.getSystemService(android.content.Context.ACTIVITY_SERVICE)
                as android.app.ActivityManager
        val me = app.packageName
        val list = am.runningAppProcesses
        val mine = list?.firstOrNull { it.processName == me }
        mine != null && mine.importance ==
                android.app.ActivityManager.RunningAppProcessInfo.IMPORTANCE_FOREGROUND
    } catch (_: Throwable) {
        false
    }

}
