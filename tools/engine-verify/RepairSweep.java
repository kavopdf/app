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
 * Runs the repair engine over a directory of damaged PDFs and reports, per file, exactly
 * what happened - independently of the engine's own claims.
 */
public class RepairSweep {

    public static void main(String[] a) throws Exception {
        File dir = new File(a.length > 0 ? a[0] : "/scratch/work/tp");
        File outDir = new File(a.length > 1 ? a[1] : "/scratch/work/tp-out");
        outDir.mkdirs();

        List<File> files = new ArrayList<>();
        File[] all = dir.listFiles();
        if (all != null) Arrays.sort(all);
        for (File f : all) if (f.getName().toLowerCase().endsWith(".pdf")) files.add(f);
        if (a.length > 2) {                       // extra files given explicitly
            for (int i = 2; i < a.length; i++) {
                File f = new File(a[i]);
                if (f.isFile()) files.add(f);
            }
        }

        System.out.println("files: " + files.size());
        System.out.println();
        int ok = 0, partial = 0, failed = 0;

        for (File f : files) {
            String name = f.getName();
            String hashBefore = sha(f);

            long t0 = System.nanoTime();
            PdfRepair.Report d = PdfRepair.diagnose(f, "");
            long t1 = System.nanoTime();
            File out = new File(outDir, "fixed_" + name);
            PdfRepair.Report r = PdfRepair.repair(f, "", out);
            long t2 = System.nanoTime();

            // ---- independent checks, not trusting the report ----
            boolean outExists = out.isFile() && out.length() > 0;
            int reopenPages = outExists ? strictPages(out) : -1;
            boolean everyPageWalks = outExists && everyPageParses(out);
            int textChars = outExists ? text(out).length() : 0;
            boolean inputUntouched = hashBefore.equals(sha(f));

            String verdict;
            if (!r.readable) { verdict = "REFUSED"; failed++; }
            else if (outExists && r.verified && reopenPages == r.pagesAfter) { verdict = "OK"; ok++; }
            else { verdict = "PROBLEM"; failed++; }

            System.out.println("==================================================================");
            System.out.println(name + "   [" + verdict + "]");
            System.out.printf("  diagnose : readable=%s stage=%s pages=%d  (%.0f ms)%n",
                    d.readable, d.stage, d.pagesBefore, (t1 - t0) / 1e6);
            System.out.printf("  repair   : readable=%s stage=%s %d -> %d pages  verified=%s  (%.0f ms)%n",
                    r.readable, r.stage, r.pagesBefore, r.pagesAfter, r.verified, (t2 - t1) / 1e6);
            if (!r.failure.isEmpty()) System.out.println("  failure  : " + r.failure);
            if (!r.findings.isEmpty()) System.out.println("  found    : " + r.findings);
            if (!r.actions.isEmpty()) System.out.println("  did      : " + r.actions);
            if (!r.lostPages.isEmpty()) System.out.println("  dropped  : " + r.lostPages);
            if (!r.blankPages.isEmpty()) System.out.println("  blank    : " + r.blankPages);
            System.out.printf("  checks   : out=%s reopenPages=%d everyPageParses=%s textChars=%d inputUntouched=%s%n",
                    outExists, reopenPages, everyPageWalks, textChars, inputUntouched);
            if (!r.verifyNote.isEmpty()) System.out.println("  verify   : " + r.verifyNote);
        }

        System.out.println();
        System.out.println("SUMMARY: " + ok + " OK, " + failed + " refused/problem, "
                + files.size() + " total");
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

    static int strictPages(File f) {
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
