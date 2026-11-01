import com.kavopdf.app.engine.PdfRepair;
import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.pdmodel.PDDocumentInformation;
import com.tom_roush.pdfbox.pdmodel.PDPage;
import com.tom_roush.pdfbox.pdmodel.PDPageContentStream;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import com.tom_roush.pdfbox.text.PDFTextStripper;

import java.io.File;
import java.io.FileOutputStream;
import java.io.RandomAccessFile;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;

/**
 * Proves the repair engine against files that were deliberately broken.
 *
 * <p>Every damaged file here is made by mutating a known-good PDF byte by byte, so the
 * expected outcome is known in advance: the repair must recover the pages that are still
 * physically present, must say so honestly in its report, and must never claim success on a
 * file it could not actually read.
 */
public class TestRepair {
    static int pass = 0, fail = 0;
    static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
    static final int PAGES = 3;

    static void check(String name, boolean ok) {
        if (ok) { pass++; System.out.println("  PASS  " + name); }
        else { fail++; System.out.println("  FAIL  " + name); }
    }

    public static void main(String[] a) throws Exception {
        W.mkdirs();
        File good = makeGood();
        byte[] original = Files.readAllBytes(good.toPath());

        System.out.println("== a file that is not damaged is reported as undamaged ==");
        {
            PdfRepair.Report r = PdfRepair.diagnose(good, "");
            check("good file is readable", r.readable);
            check("good file parses strictly", "strict".equals(r.stage));
            check("good file reports " + PAGES + " pages", r.pagesBefore == PAGES);
            check("good file has no findings", r.findings.isEmpty());
            check("good file: header found at 0", r.headerFound && r.headerOffset == 0);
            check("good file: %%EOF present", r.eofFound);
            check("good file: startxref lands on a cross-reference section", r.startxrefOk);
            check("good file: objects were parsed", r.objectsLoaded > 0);
            check("good file: not encrypted", !r.encrypted);
            check("good file: nothing lost", r.lostPages.isEmpty());
        }

        // ---- the damaged variants -------------------------------------------------------
        // name, bytes, how many pages must survive, must the report claim damage?
        List<Case> cases = new ArrayList<>();
        cases.add(new Case("startxref points at 0", mutateStartxref(original, 0), PAGES, true));
        cases.add(new Case("startxref points past the end", mutateStartxref(original, original.length + 500), PAGES, true));
        cases.add(new Case("startxref digits replaced with a wrong offset", mutateStartxref(original, 17), PAGES, true));
        cases.add(new Case("%%EOF removed", removeEof(original), PAGES, true));
        cases.add(new Case("xref table wiped", wipeXref(original), PAGES, true));
        cases.add(new Case("trailer dictionary removed", removeTrailer(original), PAGES, true));
        cases.add(new Case("header removed", removeHeader(original), PAGES, true));
        cases.add(new Case("2 KB of junk before the header", junkPrefix(original, 2048), PAGES, true));
        cases.add(new Case("8 KB of junk appended", junkSuffix(original, 8192), PAGES, true));
        cases.add(new Case("zeroed bytes in the middle", zeroMiddle(original), PAGES, false));
        cases.add(new Case("truncated to 90%", truncate(original, 0.90), 1, true));
        cases.add(new Case("truncated to 70%", truncate(original, 0.70), 1, true));
        cases.add(new Case("truncated to 50%", truncate(original, 0.50), 1, true));

        System.out.println("== every damaged file is diagnosed, then repaired ==");
        for (Case c : cases) {
            File bad = write(c.name.replace(' ', '_').replace('%', 'p').replace('.', '_') + ".pdf", c.bytes);
            File out = new File(W, "repaired_" + bad.getName());

            PdfRepair.Report d = PdfRepair.diagnose(bad, "");
            boolean sawProblem = !d.findings.isEmpty() || !d.readable;
            // A content-level corruption that still parses is invisible to a structural
            // diagnosis - claiming otherwise would be the gimmick this must not be.
            if (c.structural) check(c.name + ": diagnose noticed the damage", sawProblem);

            PdfRepair.Report r = PdfRepair.repair(bad, "", out);
            check(c.name + ": repaired file is readable", r.readable);
            check(c.name + ": pages survived (>= " + c.minPages + ")", r.pagesAfter >= c.minPages);
            check(c.name + ": at most " + PAGES + " pages", r.pagesAfter <= PAGES);
            check(c.name + ": passed its own verification", r.verified);
            check(c.name + ": output file exists", out.isFile() && out.length() > 0);
            check(c.name + ": output reopens strictly",
                    opensStrictly(out) && pageCount(out) == r.pagesAfter);
            if (c.structural) {
                check(c.name + ": text survived", textOf(out).contains("PAGE_1_MARKER"));
            }
            if (r.verified) check(c.name + ": no page was reported lost", r.lostPages.isEmpty());
        }

        System.out.println("== a truncated file keeps the pages that are still whole ==");
        {
            File bad = write("trunc_keep.pdf", truncate(original, 0.70));
            File out = new File(W, "repaired_trunc_keep.pdf");
            PdfRepair.Report r = PdfRepair.repair(bad, "", out);
            String text = textOf(out);
            check("truncated: first page text survived", text.contains("PAGE_1_MARKER"));
            check("truncated: it did not invent pages", r.pagesAfter <= PAGES);
            check("truncated: report says the file was incomplete",
                    r.findings.toString().contains("EOF")
                            || r.findings.toString().contains("incomplete")
                            || !"strict".equals(r.stage));
        }

        System.out.println("== a file that is not a PDF at all is refused, not faked ==");
        {
            byte[] noise = new byte[4096];
            new java.util.Random(7).nextBytes(noise);
            File bad = write("not_a_pdf.pdf", noise);
            File out = new File(W, "repaired_not_a_pdf.pdf");
            PdfRepair.Report r = PdfRepair.repair(bad, "", out);
            check("garbage: reported as unreadable", !r.readable);
            check("garbage: a reason is given", !r.failure.isEmpty());
            check("garbage: no output file was left behind", !out.exists());
            check("garbage: no pages claimed", r.pagesAfter == 0);
        }

        System.out.println("== an empty file is refused, not faked ==");
        {
            File bad = write("empty.pdf", new byte[0]);
            File out = new File(W, "repaired_empty.pdf");
            PdfRepair.Report r = PdfRepair.repair(bad, "", out);
            check("empty: reported as unreadable", !r.readable);
            check("empty: a reason is given", !r.failure.isEmpty());
            check("empty: no output file was left behind", !out.exists());
        }

        System.out.println("== a password-protected file asks for the password ==");
        {
            File enc = new File(W, "repair_locked.pdf");
            com.kavopdf.app.engine.PdfEngine.encrypt(good, "s3cret", "s3cret", enc);
            File out = new File(W, "repaired_locked.pdf");
            PdfRepair.Report r = PdfRepair.repair(enc, "", out);
            check("locked: refused without a password", !r.readable);
            check("locked: says it is encrypted", r.encrypted);
            check("locked: no output file was left behind", !out.exists());

            PdfRepair.Report r2 = PdfRepair.repair(enc, "s3cret", out);
            check("locked: repaired once the password is given", r2.readable && r2.pagesAfter == PAGES);
            check("locked: the result still needs the password", needsPassword(out));
            check("locked: it opens with that password", pageCountWithPassword(out, "s3cret") == PAGES);
        }

        System.out.println("== repairing an undamaged file is a clean copy ==");
        {
            File out = new File(W, "repaired_clean.pdf");
            PdfRepair.Report r = PdfRepair.repair(good, "", out);
            check("clean: still " + PAGES + " pages", r.pagesAfter == PAGES);
            check("clean: verified", r.verified);
            check("clean: nothing reported as lost", r.lostPages.isEmpty());
            check("clean: every page's text is intact", allMarkers(out, PAGES));
            check("clean: report says nothing was wrong", r.findings.isEmpty());
        }

        System.out.println("== the report never claims more than it did ==");
        {
            File bad = write("claim.pdf", removeEof(original));
            File out = new File(W, "repaired_claim.pdf");
            PdfRepair.Report r = PdfRepair.repair(bad, "", out);
            check("claim: verified is only true when pages were walked",
                    r.verified == (r.pagesAfter > 0 && r.lostPages.isEmpty()));
            check("claim: a failed repair leaves no file",
                    r.verified || !out.exists());
            check("claim: size is measured, not guessed",
                    r.sizeAfter == (out.exists() ? out.length() : 0));
        }

        System.out.println("== a broken page tree is rebuilt from the page objects ==");
        {
            File bad = write("no_tree.pdf", breakPageTree(original));
            File out = new File(W, "repaired_no_tree.pdf");
            PdfRepair.Report d = PdfRepair.diagnose(bad, "");
            check("no tree: diagnose rebuilds the tree to see the pages", d.pagesBefore == PAGES);
            check("no tree: diagnose says it rebuilt the tree",
                    d.actions.toString().contains("rebuilt the page tree"));
            PdfRepair.Report r = PdfRepair.repair(bad, "", out);
            check("no tree: repaired", r.readable);
            check("no tree: every page recovered", r.pagesAfter == PAGES);
            check("no tree: the report says it rebuilt the tree",
                    r.actions.toString().contains("rebuilt the page tree"));
            check("no tree: verified", r.verified);
            check("no tree: all text intact", allMarkers(out, PAGES));
            check("no tree: the output opens strictly", opensStrictly(out));
        }

        System.out.println("== a page whose content is gone is kept and reported, not deleted ==");
        {
            File bad = write("bad_page2.pdf", breakPageContent(original, 8));
            File out = new File(W, "repaired_bad_page2.pdf");
            PdfRepair.Report d = PdfRepair.diagnose(bad, "");
            check("gone content: diagnose names the page", d.blankPages.contains(2));
            PdfRepair.Report r = PdfRepair.repair(bad, "", out);
            check("gone content: repaired", r.readable);
            check("gone content: every page is still there", r.pagesAfter == PAGES);
            check("gone content: verified", r.verified);
            // Blank or partial - both name the page. Which word fits depends on whether
            // anything of the stream still drew before it broke, and the point of the check
            // is that the page is named at all.
            check("gone content: the report names page 2",
                    r.blankPages.contains(2) || r.partialPages.contains(2));
            String t = textOf(out);
            check("gone content: page 1 and page 3 text intact",
                    t.contains("PAGE_1_MARKER") && t.contains("PAGE_3_MARKER"));
        }

        System.out.println("== metadata survives a repair ==");
        {
            File meta = new File(W, "with_metadata.pdf");
            try (PDDocument d = new PDDocument()) {
                PDPage page = new PDPage(PDRectangle.A4);
                d.addPage(page);
                try (PDPageContentStream cs = new PDPageContentStream(d, page)) {
                    cs.beginText();
                    cs.setFont(PDType1Font.HELVETICA, 12);
                    cs.newLineAtOffset(60, 700);
                    cs.showText("metadata fixture page");
                    cs.endText();
                }
                PDDocumentInformation info = new PDDocumentInformation();
                info.setTitle("Metadata Title");
                info.setAuthor("Metadata Author");
                info.setSubject("Metadata Subject");
                info.setKeywords("alpha; beta; gamma");
                info.setCreator("Metadata Creator");
                d.setDocumentInformation(info);
                d.save(meta);
            }
            // Damage the container so the repair actually rebuilds something.
            byte[] broken = Files.readAllBytes(meta.toPath());
            File bad = write("with_metadata_bad_startxref.pdf", corruptStartxref(broken));
            File out = new File(W, "repaired_metadata.pdf");
            PdfRepair.Report r = PdfRepair.repair(bad, "", out);
            check("metadata: repaired", r.readable && r.verified);
            try (PDDocument d = PDDocument.load(out)) {
                PDDocumentInformation info = d.getDocumentInformation();
                check("metadata: title kept", "Metadata Title".equals(info.getTitle()));
                check("metadata: author kept", "Metadata Author".equals(info.getAuthor()));
                check("metadata: subject kept", "Metadata Subject".equals(info.getSubject()));
                check("metadata: keywords kept", "alpha; beta; gamma".equals(info.getKeywords()));
                check("metadata: creator kept", "Metadata Creator".equals(info.getCreator()));
            }
        }

        System.out.println("== an impossible PDF version is not passed through ==");
        {
            String text = new String(original, StandardCharsets.ISO_8859_1);
            String withBadVersion = text.replaceFirst("%PDF-[0-9.]+", "%PDF-9.9");
            File bad = write("bad_version.pdf", withBadVersion.getBytes(StandardCharsets.ISO_8859_1));
            File out = new File(W, "repaired_version.pdf");
            PdfRepair.Report r = PdfRepair.repair(bad, "", out);
            check("version: repaired", r.readable && r.verified);
            String head = new String(Files.readAllBytes(out.toPath()), 0, 8,
                    StandardCharsets.ISO_8859_1);
            check("version: the header is a published version, not %PDF-9.9",
                    !head.startsWith("%PDF-9.9") && head.startsWith("%PDF-1."));
        }

        System.out.println("== text containing operator letters is not mistaken for damage ==");
        {
            // "q", "Q", "BT" and "ET" inside a string are just letters. A page whose caption
            // happens to read "(q Q BT)" is a healthy page, and counting those letters as
            // operators would mark it partial - a false alarm on an ordinary document.
            File ok = new File(W, "strings_with_operator_letters.pdf");
            try (PDDocument d = new PDDocument()) {
                PDPage page = new PDPage(PDRectangle.A4);
                d.addPage(page);
                try (PDPageContentStream cs = new PDPageContentStream(d, page)) {
                    cs.beginText();
                    cs.setFont(PDType1Font.HELVETICA, 12);
                    cs.newLineAtOffset(60, 700);
                    cs.showText("(q q q) - three q words in a caption");
                    cs.endText();
                }
                d.save(ok);
            }
            PdfRepair.Report r = PdfRepair.repair(ok, "", new File(W, "repaired_strings.pdf"));
            check("string letters: repaired", r.readable && r.verified);
            check("string letters: the page is complete, not partial",
                    r.partialPages.isEmpty());
            check("string letters: the page is not called blank", r.blankPages.isEmpty());
            check("string letters: the text survives", textOf(new File(W, "repaired_strings.pdf"))
                    .contains("three q words"));
        }

        System.out.println("== a page whose content stream is corrupt is kept and reported ==");
        {
            // The page was already broken when it arrived, so deleting it would shift every
            // page number after it. It is kept, reported as blank, and the page count holds.
            File bad = write("corrupt_stream2.pdf", corruptStream(original, 8));
            File out = new File(W, "repaired_corrupt_stream2.pdf");
            PdfRepair.Report r = PdfRepair.repair(bad, "", out);
            check("corrupt stream: repaired", r.readable);
            check("corrupt stream: every page is still there", r.pagesAfter == PAGES);
            check("corrupt stream: verified", r.verified);
            check("corrupt stream: the report names the blank page", r.blankPages.contains(2));
            String t = textOf(out);
            check("corrupt stream: page 1 and page 3 text intact",
                    t.contains("PAGE_1_MARKER") && t.contains("PAGE_3_MARKER"));
        }

        System.out.println("== repairing a repaired file changes nothing ==");
        {
            File once = new File(W, "again_once.pdf");
            File twice = new File(W, "again_twice.pdf");
            PdfRepair.Report first = PdfRepair.repair(write("again_src.pdf", removeEof(original)), "", once);
            PdfRepair.Report second = PdfRepair.repair(once, "", twice);
            check("again: first repair verified", first.verified);
            check("again: second repair verified", second.verified);
            check("again: page count is stable",
                    first.pagesAfter == second.pagesAfter && second.pagesAfter == PAGES);
            check("again: text is stable", textOf(once).equals(textOf(twice)));
            check("again: second pass reports nothing wrong", second.findings.isEmpty());
        }

        System.out.println("== a longer document keeps every page ==");
        {
            File big = makeMany(10);
            File out = new File(W, "repaired_ten.pdf");
            PdfRepair.Report r = PdfRepair.repair(write("ten_broken.pdf", wipeXref(Files.readAllBytes(big.toPath()))), "", out);
            check("ten pages: all recovered", r.pagesAfter == 10);
            check("ten pages: verified", r.verified);
            check("ten pages: first and last text intact", allMarkers(out, 10));
        }

        System.out.println();
        System.out.println("REPAIR TOTAL: " + pass + " passed, " + fail + " failed");
        if (fail > 0) System.exit(1);
    }

    // =====================================================================================
    //  Building the known-good file, and breaking it in specific ways
    // =====================================================================================

    static File makeGood() throws Exception {
        File f = new File(W, "repair_good.pdf");
        PDDocument d = new PDDocument();
        for (int i = 1; i <= PAGES; i++) {
            PDPage p = new PDPage(PDRectangle.A4);
            d.addPage(p);
            try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
                cs.beginText();
                cs.setFont(PDType1Font.HELVETICA, 20);
                cs.newLineAtOffset(72, 700);
                cs.showText("PAGE_" + i + "_MARKER");
                cs.endText();
            }
        }
        d.save(f);
        d.close();
        return f;
    }

    /** Points the catalog at an object that does not exist: the page tree is gone. */
    static byte[] breakPageTree(byte[] src) {
        String s = new String(src, StandardCharsets.ISO_8859_1);
        return s.replaceFirst("/Pages \\d+ 0 R", "/Pages 0 0 R").getBytes(StandardCharsets.ISO_8859_1);
    }

    /** Points one page at a content object that does not exist. */
    /** Points startxref at an offset that holds no cross-reference table. */
    static byte[] corruptStartxref(byte[] src) {
        String s = new String(src, StandardCharsets.ISO_8859_1);
        int at = s.lastIndexOf("startxref");
        if (at < 0) return src;
        int numStart = at + 9;
        while (numStart < s.length() && Character.isWhitespace(s.charAt(numStart))) numStart++;
        int numEnd = numStart;
        while (numEnd < s.length() && Character.isDigit(s.charAt(numEnd))) numEnd++;
        if (numEnd <= numStart) return src;
        return (s.substring(0, numStart) + "999999" + s.substring(numEnd))
                .getBytes(StandardCharsets.ISO_8859_1);
    }

    static byte[] breakPageContent(byte[] src, int objNum) {
        String s = new String(src, StandardCharsets.ISO_8859_1);
        return s.replace("/Contents " + objNum + " 0 R", "/Contents 0 0 R")
                .getBytes(StandardCharsets.ISO_8859_1);
    }

    /** Overwrites the compressed bytes of one content stream, so FlateDecode fails. */
    static byte[] corruptStream(byte[] src, int objNum) {
        String s = new String(src, StandardCharsets.ISO_8859_1);
        int obj = s.indexOf("\n" + objNum + " 0 obj");
        if (obj < 0) return src;
        int stream = s.indexOf("stream", obj);
        if (stream < 0) return src;
        int start = stream + "stream".length();
        while (start < s.length() && (s.charAt(start) == '\r' || s.charAt(start) == '\n')) start++;
        byte[] out = src.clone();
        int end = Math.min(out.length, start + 24);
        for (int i = start; i < end; i++) out[i] = (byte) 0xFF;
        return out;
    }

    static File makeMany(int pages) throws Exception {
        File f = new File(W, "repair_many.pdf");
        PDDocument d = new PDDocument();
        for (int i = 1; i <= pages; i++) {
            PDPage p = new PDPage(PDRectangle.A4);
            d.addPage(p);
            try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
                cs.beginText();
                cs.setFont(PDType1Font.HELVETICA, 18);
                cs.newLineAtOffset(72, 700);
                cs.showText("PAGE_" + i + "_MARKER");
                cs.endText();
            }
        }
        d.save(f);
        d.close();
        return f;
    }

    static File write(String name, byte[] bytes) throws Exception {
        File f = new File(W, name);
        try (FileOutputStream o = new FileOutputStream(f)) { o.write(bytes); }
        return f;
    }

    /** Rewrites the number after the last "startxref". */
    static byte[] mutateStartxref(byte[] src, long value) {
        String s = new String(src, StandardCharsets.ISO_8859_1);
        int at = s.lastIndexOf("startxref");
        String head = s.substring(0, at + "startxref".length());
        int i = at + "startxref".length();
        while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++;
        int j = i;
        while (j < s.length() && Character.isDigit(s.charAt(j))) j++;
        String rebuilt = head + s.substring(at + "startxref".length(), i) + value + s.substring(j);
        return rebuilt.getBytes(StandardCharsets.ISO_8859_1);
    }

    static byte[] removeEof(byte[] src) {
        String s = new String(src, StandardCharsets.ISO_8859_1);
        int at = s.lastIndexOf("%%EOF");
        if (at < 0) return src;
        return (s.substring(0, at) + s.substring(at + 5)).getBytes(StandardCharsets.ISO_8859_1);
    }

    /** Blanks everything between the last "xref" keyword and "trailer". */
    static byte[] wipeXref(byte[] src) {
        String s = new String(src, StandardCharsets.ISO_8859_1);
        int a = s.lastIndexOf("\nxref");
        int b = s.indexOf("trailer", a < 0 ? 0 : a);
        if (a < 0 || b < 0 || b <= a) return src;
        StringBuilder sb = new StringBuilder(s);
        for (int i = a + 1; i < b; i++) sb.setCharAt(i, ' ');
        return sb.toString().getBytes(StandardCharsets.ISO_8859_1);
    }

    static byte[] removeTrailer(byte[] src) {
        String s = new String(src, StandardCharsets.ISO_8859_1);
        int a = s.lastIndexOf("trailer");
        if (a < 0) return src;
        int b = s.indexOf("startxref", a);
        if (b < 0) return src;
        StringBuilder sb = new StringBuilder(s);
        for (int i = a; i < b; i++) sb.setCharAt(i, ' ');
        return sb.toString().getBytes(StandardCharsets.ISO_8859_1);
    }

    static byte[] removeHeader(byte[] src) {
        String s = new String(src, StandardCharsets.ISO_8859_1);
        int at = s.indexOf("%PDF-");
        if (at < 0) return src;
        return (s.substring(0, at) + "     " + s.substring(at + 5))
                .getBytes(StandardCharsets.ISO_8859_1);
    }

    static byte[] junkPrefix(byte[] src, int n) {
        byte[] junk = new byte[n];
        new java.util.Random(11).nextBytes(junk);
        byte[] out = new byte[n + src.length];
        System.arraycopy(junk, 0, out, 0, n);
        System.arraycopy(src, 0, out, n, src.length);
        return out;
    }

    static byte[] junkSuffix(byte[] src, int n) {
        byte[] junk = new byte[n];
        new java.util.Random(13).nextBytes(junk);
        byte[] out = new byte[src.length + n];
        System.arraycopy(src, 0, out, 0, src.length);
        System.arraycopy(junk, 0, out, src.length, n);
        return out;
    }

    /** Zeroes a slice in the middle, where the page content streams live. */
    static byte[] zeroMiddle(byte[] src) {
        byte[] out = src.clone();
        int from = src.length / 3;
        int to = Math.min(src.length, from + Math.max(8, src.length / 40));
        for (int i = from; i < to; i++) out[i] = 0;
        return out;
    }

    static byte[] truncate(byte[] src, double fraction) {
        int keep = (int) (src.length * fraction);
        byte[] out = new byte[keep];
        System.arraycopy(src, 0, out, 0, keep);
        return out;
    }

    // =====================================================================================
    //  Reading the result back, independently of the engine's own checks
    // =====================================================================================

    static boolean opensStrictly(File f) {
        try (PDDocument d = PDDocument.load(f)) { return true; }
        catch (Throwable t) { return false; }
    }

    static int pageCount(File f) {
        try (PDDocument d = PDDocument.load(f)) { return d.getNumberOfPages(); }
        catch (Throwable t) { return -1; }
    }

    static int pageCountWithPassword(File f, String pw) {
        try (PDDocument d = PDDocument.load(f, pw)) { return d.getNumberOfPages(); }
        catch (Throwable t) { return -1; }
    }

    static boolean needsPassword(File f) {
        try (PDDocument d = PDDocument.load(f)) { return !d.isEncrypted(); }
        catch (Throwable t) { return true; }
    }

    static String textOf(File f) {
        try (PDDocument d = PDDocument.load(f)) {
            return new PDFTextStripper().getText(d);
        } catch (Throwable t) { return ""; }
    }

    static boolean allMarkers(File f, int pages) {
        String t = textOf(f);
        for (int i = 1; i <= pages; i++) if (!t.contains("PAGE_" + i + "_MARKER")) return false;
        return true;
    }

    static final class Case {
        final String name;
        final byte[] bytes;
        final int minPages;
        /** True when the damage is in the structure, so a diagnosis must see it. */
        final boolean structural;

        Case(String name, byte[] bytes, int minPages, boolean structural) {
            this.name = name;
            this.bytes = bytes;
            this.minPages = minPages;
            this.structural = structural;
        }
    }
}
