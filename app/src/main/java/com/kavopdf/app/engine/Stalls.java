package com.kavopdf.app.engine;

/**
 * Spots the main thread going quiet - the first sign of an ANR.
 *
 * A tick is posted to the main thread on a fixed beat. If the gap between two
 * ticks is far longer than the beat, the main thread was busy for that long, and
 * that is exactly what an ANR is made of.
 *
 * One report per block: a five-second stall must not produce ten entries.
 *
 * Pure Java, no Android types, so the behaviour can be proven on a plain JVM.
 */
public final class Stalls {

    /** The beat, in milliseconds. */
    public static final long TICK_MS = 500L;

    /** How often to look while the app is behind another app and nothing can be seen. */
    public static final long IDLE_MS = 5000L;

    /** A gap this long means the main thread was blocked. */
    public static final long BLOCK_MS = 2000L;

    /**
     * Beyond this the gap is not a block at all: Android stops delivering timers
     * when the app is backgrounded or the device is dozing, and the gap grows to
     * tens of seconds. Reporting those produced 433 false entries with a median of
     * 6.8s - an app cannot block its own main thread that often.
     */
    public static final long MAX_BLOCK_MS = 30000L;

    private long last = -1L;
    private boolean reported = false;

    /** Called on every tick. Returns the blocked duration once, or 0. */
    public synchronized long onTick(long nowMs) {
        if (last < 0L) {
            last = nowMs;
            return 0L;
        }
        long gap = nowMs - last;
        last = nowMs;
        if (gap >= MAX_BLOCK_MS) {
            // timers were suspended, not blocked - start a fresh beat, report nothing
            reported = false;
            return 0L;
        }
        if (gap >= BLOCK_MS) {
            if (reported) return 0L;      // still the same block, already recorded
            reported = true;
            return gap;
        }
        reported = false;                  // healthy beat again: a new block may be reported
        return 0L;
    }

    public synchronized void reset() {
        last = -1L;
        reported = false;
    }
}
