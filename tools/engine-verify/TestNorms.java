import com.kavopdf.app.engine.NormStore;

public class TestNorms {
    static int pass = 0, fail = 0;
    static void check(String what, boolean ok) {
        System.out.println((ok ? "  PASS  " : "  FAIL  ") + what);
        if (ok) pass++; else fail++;
    }
    public static void main(String[] a) {
        // ---- 1. a fast tool: an 11x slowdown used to slip under the 1500ms floor ----
        NormStore n1 = new NormStore();
        for (int i = 0; i < 9; i++) n1.record("WATERMARK", 1, 105);
        check("105ms norm: 400ms is quiet (noise)",        !n1.isAnomalous("WATERMARK", 1, 400));
        check("105ms norm: 1200ms IS flagged (11x)",        n1.isAnomalous("WATERMARK", 1, 1200));
        check("105ms norm: 5600ms IS flagged",              n1.isAnomalous("WATERMARK", 1, 5600));

        // ---- 2. a slow tool still keeps the absolute floor ----
        NormStore n2 = new NormStore();
        for (int i = 0; i < 9; i++) n2.record("OCR", 1, 5000);
        check("5000ms norm: 6000ms is quiet",              !n2.isAnomalous("OCR", 1, 6000));
        check("5000ms norm: 20000ms IS flagged",            n2.isAnomalous("OCR", 1, 20000));

        // ---- 3. file size is its own bucket ----
        NormStore n3 = new NormStore();
        // record(tool, pages, bytes, ms)
        for (int i = 0; i < 9; i++) n3.record("COMPRESS", 1, 200_000L, 300L);   // 1 page, 200 KB, 300 ms
        check("1 page 200KB: a 5MB run has no norm yet", !n3.isAnomalous("COMPRESS", 1, 5_000_000L, 9000L));
        check("1 page 200KB: 900ms quiet",               !n3.isAnomalous("COMPRESS", 1, 200_000L, 900L));
        check("1 page 200KB: 2000ms IS flagged",          n3.isAnomalous("COMPRESS", 1, 200_000L, 2000L));
        check("size buckets differ", NormStore.sizeBucket(500_000L).equals("S")
                && NormStore.sizeBucket(5_000_000L).equals("M")
                && NormStore.sizeBucket(50_000_000L).equals("L"));

        // ---- 4. nothing is reported before a norm exists ----
        NormStore n4 = new NormStore();
        check("first run is silent",  !n4.isAnomalous("X", 1, 99999));
        n4.record("X", 1, 100);
        check("one run is still silent", !n4.isAnomalous("X", 1, 99999));

        // ---- 5. a stall never poisons the norm ----
        NormStore n5 = new NormStore();
        for (int i = 0; i < 9; i++) n5.record("Y", 1, 100);
        long before = n5.normFor("Y", 1);
        n5.record("Y", 1, 50000);                      // one stall
        check("one stall leaves the norm alone", n5.normFor("Y", 1) == before);
        n5.record("Y", 1, 50000);
        n5.record("Y", 1, 50000);                      // three in a row = really slower
        check("three stalls reset the norm", n5.normFor("Y", 1) == -1 || n5.normFor("Y", 1) >= 40000);

        System.out.println("\n" + pass + " passed, " + fail + " failed");
        if (fail > 0) System.exit(1);
    }
}
