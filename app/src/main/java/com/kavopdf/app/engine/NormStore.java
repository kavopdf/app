package com.kavopdf.app.engine;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Learns how long each tool normally takes on this device, and speaks up only
 * when a run is far outside that norm.
 *
 * Why this and not a table of constants: "slow" has no absolute meaning. OCR on
 * forty pages takes seconds and that is normal; the same seconds on one page is a
 * hang. The only honest reference is the device's own history.
 *
 * Two rules keep it free of false positives:
 *   1. Nothing is reported until there is a norm - the first runs are silent.
 *   2. A stall is never learned from, so one bad run cannot poison the norm.
 *
 * Pure Java, no Android types, so it can be exercised on a plain JVM.
 */
public final class NormStore {

    /** A run this many times slower than the norm is a real problem. */
    public static final int FACTOR = 3;

    /** Timings kept per tool+bucket; the median of these is the norm. */
    public static final int HISTORY = 9;

    /**
     * A fast tool is judged on how much slower it got, not on an absolute floor.
     * With only the 1500 ms floor, a 1200 ms run of a tool that normally takes 105 ms
     * - eleven times slower - was never reported at all.
     */
    public static final int FAST_FACTOR = 10;

    /** Below this, a "3x slower" claim is noise. */
    public static final long FLOOR_MS = 1500L;

    private final Map<String, long[]> data = new HashMap<>();
    /** Consecutive runs that looked like a stall, per key. */
    private final Map<String, Integer> rejects = new HashMap<>();

    /** Page counts are bucketed so a 41-page run is never compared with a 1-page run. */
    public static String bucket(int pages) {
        if (pages <= 1) return "1";
        if (pages <= 5) return "2-5";
        if (pages <= 20) return "6-20";
        if (pages <= 50) return "21-50";
        return "50+";
    }

    /**
     * File size matters as much as page count: one 50 MB scan and one plain text page
     * are both "1 page" but nothing alike, and comparing them flagged healthy runs.
     */
    public static String sizeBucket(long bytes) {
        if (bytes <= 0) return "?";
        if (bytes < 1_000_000L) return "S";
        if (bytes < 10_000_000L) return "M";
        return "L";
    }

    public static String key(String tool, int pages) {
        return key(tool, pages, 0L);
    }

    public static String key(String tool, int pages, long bytes) {
        return (tool == null ? "?" : tool) + "|" + bucket(pages) + "|" + sizeBucket(bytes);
    }

    /** The point past which a run counts as a problem. */
    public static long trigger(long norm) {
        return Math.max(norm * FACTOR, Math.min(FLOOR_MS, norm * FAST_FACTOR));
    }

    /** True only when this run is genuinely far outside the device's own norm. */
    public boolean isAnomalous(String tool, int pages, long ms) {
        return isAnomalous(tool, pages, 0L, ms);
    }

    public boolean isAnomalous(String tool, int pages, long bytes, long ms) {
        long[] hist = data.get(key(tool, pages, bytes));
        if (hist == null || hist.length < 2) return false;      // no norm yet: silent
        long norm = median(hist);
        if (norm <= 0) return false;
        return ms > trigger(norm);
    }

    /** Feed a finished run. A stall is deliberately not learned from. */
    public void record(String tool, int pages, long ms) {
        record(tool, pages, 0L, ms);
    }

    public void record(String tool, int pages, long bytes, long ms) {
        if (ms <= 0) return;
        String k = key(tool, pages, bytes);
        long[] hist = data.get(k);
        if (hist != null && hist.length >= 2) {
            long norm = median(hist);
            if (norm > 0 && ms > trigger(norm)) {
                // One odd run is a stall and must not teach. But three in a row means
                // the app really is slower now, so throw the stale history away and
                // learn again - otherwise the norm is stuck for ever and every run
                // after it is reported as slow.
                int n = rejects.containsKey(k) ? rejects.get(k) : 0;
                n++;
                if (n < 3) {
                    rejects.put(k, n);
                    return;
                }
                rejects.remove(k);
                data.remove(k);
                hist = null;
            } else {
                rejects.remove(k);
            }
        }
        long[] next;
        if (hist == null) {
            next = new long[1];
        } else if (hist.length < HISTORY) {
            next = new long[hist.length + 1];
            System.arraycopy(hist, 0, next, 0, hist.length);
        } else {
            next = new long[HISTORY];
            System.arraycopy(hist, 1, next, 0, HISTORY - 1);
        }
        next[next.length - 1] = ms;
        data.put(k, next);
    }

    public long normFor(String tool, int pages) {
        return normFor(tool, pages, 0L);
    }

    public long normFor(String tool, int pages, long bytes) {
        long[] hist = data.get(key(tool, pages, bytes));
        return hist == null || hist.length == 0 ? -1 : median(hist);
    }

    public static long median(long[] values) {
        return p75(values);
    }

    /**
     * The upper quartile of the history.
     *
     * A plain median splits the difference between a 1-page run and a 41-page run,
     * so whichever comes next looks anomalous. The upper quartile follows the
     * heavier case instead, and is identical to the median when all runs are alike.
     */
    public static long p75(long[] values) {
        if (values == null || values.length == 0) return -1;
        long[] copy = values.clone();
        java.util.Arrays.sort(copy);
        int idx = (int) Math.round((copy.length - 1) * 0.75);
        if (idx < 0) idx = 0;
        if (idx >= copy.length) idx = copy.length - 1;
        return copy[idx];
    }

    /** One-line-per-entry text form, for SharedPreferences. */
    public String toText() {
        StringBuilder sb = new StringBuilder();
        // the streak of consecutive outliers, so it survives the app being closed
        for (Map.Entry<String, Integer> e : rejects.entrySet()) {
            sb.append("rej=").append(e.getKey()).append(':').append(e.getValue()).append('\n');
        }
        for (Map.Entry<String, long[]> e : data.entrySet()) {
            sb.append(e.getKey()).append('=');
            long[] v = e.getValue();
            for (int i = 0; i < v.length; i++) {
                if (i > 0) sb.append(',');
                sb.append(v[i]);
            }
            sb.append('\n');
        }
        return sb.toString();
    }

    public static NormStore fromText(String text) {
        NormStore store = new NormStore();
        if (text == null || text.trim().isEmpty()) return store;
        for (String line : text.split("\n")) {
            int eq = line.indexOf('=');
            if (eq <= 0) continue;
            String k = line.substring(0, eq).trim();
            if (k.startsWith("rej=")) {
                // a saved reject streak
                String body = k.substring(4);
                int c = body.lastIndexOf(':');
                if (c > 0) {
                    try {
                        store.rejects.put(body.substring(0, c), Integer.parseInt(body.substring(c + 1).trim()));
                    } catch (NumberFormatException ignored) { }
                }
                continue;
            }
            String[] parts = line.substring(eq + 1).split(",");
            List<Long> vals = new ArrayList<>();
            for (String p : parts) {
                try {
                    long v = Long.parseLong(p.trim());
                    if (v > 0) vals.add(v);
                } catch (NumberFormatException ignored) {
                }
            }
            if (k.isEmpty() || vals.isEmpty()) continue;
            long[] arr = new long[vals.size()];
            for (int i = 0; i < arr.length; i++) arr[i] = vals.get(i);
            store.data.put(k, arr);
        }
        return store;
    }

    public int size() {
        return data.size();
    }
}
