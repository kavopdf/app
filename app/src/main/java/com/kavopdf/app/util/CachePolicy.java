package com.kavopdf.app.util;

/**
 * When a file in the working cache may be deleted.
 *
 * Pure, with no Android types, so the rule can be checked directly instead of only being
 * read and hoped for.
 *
 * Two ages:
 *   - a document copy or an intermediate PDF is kept for 45 minutes. Nothing younger is
 *     ever touched, so a long job can never lose the file it is still working from - a
 *     file being written has a fresh timestamp, and an input that is still in use is
 *     always well inside the window.
 *   - a link-icon overlay is a few KB and is rebuilt on demand, so it can go after 10
 *     minutes. These used to be written into the cache root, which no cleanup ever looked
 *     at, so they were never removed at all.
 */
public final class CachePolicy {

    /** How long a document copy or intermediate PDF may stay in the cache. */
    public static final long MAX_AGE_MS = 45L * 60_000L;

    /** How long a link-icon overlay may stay. */
    public static final long ICON_AGE_MS = 10L * 60_000L;

    private static final String ICON_PREFIX = "link_shape_";
    private static final String ICON_SUFFIX = ".png";

    private CachePolicy() {
    }

    /** True when this cache entry is old enough to be removed. */
    public static boolean isStale(String name, long ageMs) {
        if (ageMs < 0) return false;
        return ageMs > limitFor(name);
    }

    /** The age limit that applies to this cache entry. */
    public static long limitFor(String name) {
        return isIcon(name) ? ICON_AGE_MS : MAX_AGE_MS;
    }

    /** True for the small PNG overlays LinksActivity writes. */
    public static boolean isIcon(String name) {
        return name != null && name.startsWith(ICON_PREFIX) && name.endsWith(ICON_SUFFIX);
    }
}
