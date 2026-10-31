import com.kavopdf.app.util.CachePolicy;

/**
 * The rule that decides when a cache file may go. Plain Java, so it runs here.
 */
public class TestCachePolicy {
    static int pass = 0, fail = 0;
    static void check(boolean ok, String what) {
        if (ok) { pass++; System.out.println("  PASS  " + what); }
        else { fail++; System.out.println("  FAIL  " + what); }
    }

    static final long MIN = 60_000L;

    public static void main(String[] a) {
        // --- a document copy or an intermediate PDF ---------------------------------
        check(!CachePolicy.isStale("123_1_report.pdf", 0), "a brand new document copy is kept");
        check(!CachePolicy.isStale("123_1_report.pdf", 44 * MIN), "44 minutes old is still kept");
        check(CachePolicy.isStale("123_1_report.pdf", 46 * MIN), "46 minutes old is removed");
        check(CachePolicy.isStale("123_1_report.pdf", 6 * 60 * MIN),
                "six hours old is removed (the old window is gone)");
        check(!CachePolicy.isStale("123_1_report.pdf", -5 * MIN),
                "a clock that went backwards never deletes anything");

        // --- the link-icon overlays ---------------------------------------------------
        check(CachePolicy.isIcon("link_shape_1698000000000.png"), "an icon overlay is recognised");
        check(!CachePolicy.isIcon("123_1_report.pdf"), "a document copy is not an icon");
        check(!CachePolicy.isIcon("link_shape_1.png.bak"), "a lookalike name is not an icon");
        check(!CachePolicy.isIcon(null), "a null name is not an icon");
        check(!CachePolicy.isStale("link_shape_1698000000000.png", 9 * MIN), "an icon is kept for 9 minutes");
        check(CachePolicy.isStale("link_shape_1698000000000.png", 11 * MIN), "an icon is removed after 11 minutes");

        // --- the limits themselves -----------------------------------------------------
        check(CachePolicy.limitFor("link_shape_1.png") == CachePolicy.ICON_AGE_MS,
                "icons use the icon limit");
        check(CachePolicy.limitFor("a.pdf") == CachePolicy.MAX_AGE_MS, "documents use the document limit");
        check(CachePolicy.MAX_AGE_MS <= 60 * MIN,
                "the document window is an hour or less (it was six)");
        check(CachePolicy.MAX_AGE_MS >= 30 * MIN,
                "the document window is at least 30 minutes, so a long job cannot lose its input");
        check(CachePolicy.ICON_AGE_MS < CachePolicy.MAX_AGE_MS,
                "icons go sooner than documents");

        System.out.println("CACHEPOLICY TOTAL: " + pass + " passed, " + fail + " failed");
        if (fail > 0) System.exit(1);
    }
}
