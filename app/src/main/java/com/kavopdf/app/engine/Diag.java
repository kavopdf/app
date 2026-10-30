package com.kavopdf.app.engine;

import java.text.SimpleDateFormat;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * The diagnostics core.
 *
 * Deliberately free of Android types so it can be exercised on a plain JVM - a
 * detector nobody has tested is a detector nobody can trust.
 *
 * Two rules it exists to enforce:
 *   1. Nothing is recorded unless something is actually wrong.
 *   2. When something is wrong, enough is recorded to fix it.
 *
 * Breadcrumbs are the trick that makes both possible: the last few actions are
 * kept in memory only, and they are written out only when a real problem occurs.
 */
public final class Diag {

    /** How many recent actions are remembered. Kept small on purpose. */
    public static final int MAX_BREADCRUMBS = 20;

    /** A step slower than this is a problem worth recording; anything faster is normal. */
    public static final long SLOW_MS = 2000L;

    /** Frames kept from a stack trace: enough to locate the line, not a wall of text. */
    public static final int MAX_FRAMES = 12;

    private static final ArrayDeque<String> BREADCRUMBS = new ArrayDeque<>();
    private static final SimpleDateFormat CLOCK =
            new SimpleDateFormat("HH:mm:ss", Locale.US);

    private Diag() {
    }

    /** Remember what the app just did. Memory only - never written to the log. */
    public static synchronized void breadcrumb(String what) {
        if (what == null) return;
        String t = what.trim();
        if (t.isEmpty()) return;
        BREADCRUMBS.addLast(CLOCK.format(new Date()) + "  " + t);
        while (BREADCRUMBS.size() > MAX_BREADCRUMBS) BREADCRUMBS.removeFirst();
    }

    /** The remembered actions, oldest first. */
    public static synchronized List<String> crumbs() {
        return new ArrayList<>(BREADCRUMBS);
    }

    public static synchronized void clear() {
        BREADCRUMBS.clear();
    }

    /** True only when a step really was too slow - no guessing, no rounding. */
    public static boolean isSlow(long elapsedMs) {
        return elapsedMs >= SLOW_MS;
    }

    /**
     * A compact but complete description: what was thrown, what it said, what
     * caused it, and the first frames. Empty string for a null, never throws.
     */
    public static String describe(Throwable error) {
        if (error == null) return "";
        StringBuilder sb = new StringBuilder();
        sb.append(error.getClass().getName());
        String msg = error.getMessage();
        if (msg != null && !msg.trim().isEmpty()) sb.append(": ").append(msg.trim());

        Throwable cause = error.getCause();
        int depth = 0;
        while (cause != null && depth < 3) {
            sb.append("\nCaused by ").append(cause.getClass().getName());
            String cm = cause.getMessage();
            if (cm != null && !cm.trim().isEmpty()) sb.append(": ").append(cm.trim());
            cause = cause.getCause();
            depth++;
        }

        sb.append("\n");
        StackTraceElement[] st = error.getStackTrace();
        int n = Math.min(MAX_FRAMES, st.length);
        for (int i = 0; i < n; i++) {
            StackTraceElement e = st[i];
            sb.append("\n  at ").append(e.getClassName()).append(".")
              .append(e.getMethodName()).append("(")
              .append(e.getFileName()).append(":").append(e.getLineNumber()).append(")");
        }
        if (st.length > n) sb.append("\n  ... ").append(st.length - n).append(" more");
        return sb.toString();
    }

    /** The breadcrumbs as one block, for the crash record. Empty when there are none. */
    public static String crumbBlock() {
        List<String> list = crumbs();
        if (list.isEmpty()) return "";
        StringBuilder sb = new StringBuilder("Last actions:");
        for (String c : list) sb.append("\n  ").append(c);
        return sb.toString();
    }
}
