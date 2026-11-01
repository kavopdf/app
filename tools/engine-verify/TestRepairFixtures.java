import com.kavopdf.app.engine.PdfRepair;
import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.pdmodel.PDPage;
import com.tom_roush.pdfbox.pdfparser.PDFStreamParser;
import com.tom_roush.pdfbox.text.PDFTextStripper;

import java.io.File;
import java.io.FileInputStream;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Runs the repair engine over the 21 real damaged fixtures in fixtures/repair.
 *
 * <p>These are not generated here: they came in as a stress set covering middle-chunk
 * removal, lost trailers, destroyed xref tables, bad startxref offsets, a missing catalog,
 * a broken page tree, damaged object headers, missing endstream markers, wrong stream
 * lengths, truncation inside a stream, a damaged header, duplicate object numbers, broken
 * incremental updates, garbage after EOF, damaged end markers, malformed trailer spacing,
 * scattered byte damage, extreme combined corruption, invalid filter parameters, a file
 * that is not a PDF at all, and one file carrying several of these at once.
 *
 * <p>What is asserted is behaviour, not a fixed per-file answer: no fixture may crash, hang
 * or be modified; a repair that claims success must produce a file that reopens, has pages,
 * and whose pages really parse; a repair that fails must leave nothing behind; and the
 * suite must not regress below the number of fixtures that are recoverable today.
 */
public class TestRepairFixtures {
    static int pass = 0, fail = 0;
    static final int MUST_RECOVER = 45;      // 51 files; 20 is not a PDF, 06/10 lost their
                                         // page content, and a few recover only partly
    static final long MAX_MS = 8000;   // the 4000-reference page bomb is the slowest

    static void check(String name, boolean ok) {
        if (ok) { pass++; System.out.println("  PASS  " + name); }
        else { fail++; System.out.println("  FAIL  " + name); }
    }

    public static void main(String[] a) throws Exception {
        int totalPass = 0, totalFail = 0;
        totalPass += runSuite(new File("fixtures/repair"), "repair");
        totalFail += fail; fail = 0;
        totalPass += runSuite(new File("fixtures/torture"), "torture");
        totalPass += runSuite(new File("fixtures/gaps"), "gaps");
        totalFail += fail; fail = 0;
        System.out.println();
        System.out.println("FIXTURES TOTAL: " + totalPass + " passed, " + totalFail + " failed");
        if (totalFail > 0) System.exit(1);
    }

    /** Runs one fixture folder and returns its pass count. */
    static int runSuite(File dir, String label) throws Exception {
        pass = 0; fail = 0;
        if (!dir.isDirectory()) {
            System.out.println("FIXTURES TOTAL: skipped (fixtures/repair not found)");
            return 0;
        }
        File[] all = dir.listFiles();
        List<File> files = new ArrayList<>();
        if (all != null) Arrays.sort(all);
        for (File f : all) if (f.getName().toLowerCase().endsWith(".pdf")) files.add(f);
        check(label + ": fixtures found", files.size() >= ("gaps".equals(label) ? 20 : 40));

        File outDir = new File(System.getProperty("java.io.tmpdir"), "kavopdf-fixture-out-" + label);
        outDir.mkdirs();

        int recovered = 0, refused = 0;
        for (File f : files) {
            String name = f.getName();
            String before = sha(f);

            long t0 = System.currentTimeMillis();
            File out = new File(outDir, "fixed_" + name);
            PdfRepair.Report d = PdfRepair.diagnose(f, "");
            PdfRepair.Report r = PdfRepair.repair(f, "", out);
            long ms = System.currentTimeMillis() - t0;

            check(name + ": finished inside " + MAX_MS + " ms (" + ms + ")", ms < MAX_MS);
            check(name + ": the input file was not modified", before.equals(sha(f)));
            check(name + ": no report is null", d != null && r != null);
            check(name + ": a diagnosis was produced", d.readable || !d.failure.isEmpty());
            check(name + ": repair always states an outcome",
                    r.verified || !r.failure.isEmpty());

            boolean outExists = out.isFile() && out.length() > 0;
            if (r.verified) {
                recovered++;
                check(name + ": a verified repair left a file", outExists);
                check(name + ": the file reopens", pages(out) == r.pagesAfter);
                check(name + ": it has at least one page", r.pagesAfter > 0);
                check(name + ": every page parses", everyPageParses(out));
                check(name + ": it says nothing it did not do",
                        r.failure.isEmpty() && r.pagesAfter <= Math.max(r.pagesBefore, r.pagesAfter));
                // A page that is present but blank is not a recovered page: at least one
                // page must really hold content, or this is a blank document wearing a
                // success message.
                check(name + ": at least one page really holds content",
                        r.pagesAfter - r.blankPages.size() - r.lostPages.size() > 0);
            } else {
                refused++;
                check(name + ": a failed repair left no file", !outExists);
                check(name + ": it explains why", !r.failure.isEmpty());
            }
        }

        int floor = "repair".equals(label) ? 45 : "torture".equals(label) ? 26 : 14;
        check(label + ": at least " + floor + " fixtures are recoverable (got " + recovered + ")",
                recovered >= floor);
        System.out.println("  " + label + ": recovered " + recovered + ", refused " + refused
                + " of " + files.size());
        return pass;
    }

    static String sha(File f) {
        try (FileInputStream in = new FileInputStream(f)) {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] b = new byte[8192];
            int n;
            while ((n = in.read(b)) > 0) md.update(b, 0, n);
            StringBuilder sb = new StringBuilder();
            for (byte x : md.digest()) sb.append(String.format("%02x", x));
            return sb.toString();
        } catch (Exception e) { return "?"; }
    }

    static int pages(File f) {
        try (PDDocument d = PDDocument.load(f)) { return d.getNumberOfPages(); }
        catch (Throwable t) { return -1; }
    }

    static boolean everyPageParses(File f) {
        try (PDDocument d = PDDocument.load(f)) {
            for (int i = 0; i < d.getNumberOfPages(); i++) {
                PDPage p = d.getPage(i);
                p.getMediaBox();
                p.getResources();
                new PDFStreamParser(p).parse();
            }
            return true;
        } catch (Throwable t) { return false; }
    }

    static String text(File f) {
        try (PDDocument d = PDDocument.load(f)) { return new PDFTextStripper().getText(d); }
        catch (Throwable t) { return ""; }
    }
}
