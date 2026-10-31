import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import com.tom_roush.pdfbox.text.PDFTextStripper;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Independent checks for everything 3.32.0 added to the OCR path.
 *
 * Nothing here trusts the code: each assertion builds a real PDF, runs the real engine,
 * reads the result back with PDFTextStripper and compares what a reader would copy.
 */
public class TestOcrPlan {
    static final int W = 2600, H = 3368;
    static int pass = 0, fail = 0;

    public static void main(String[] a) throws Exception {
        byte[] font = Files.readAllBytes(Paths.get(a[0]));
        File dir = new File(System.getProperty("java.io.tmpdir"), "kavopdf_plan");
        dir.mkdirs();

        // ---------------------------------------------------------------- item 1
        System.out.println("== item 1: exact characters ==");
        PdfEngine.setOcrFont(font);

        String[] words = {
                "\u20b9500", "30\u201340", "a\u2014b", "\u201cquoted\u201d", "CO\u2082",
                "25\u00b0C", "50%", "caf\u00e9", "\u00fcber", "5\u219210", "x\u2265y",
                "a\u2260b", "\u6f22", "\u2192"
        };
        File src = blank(dir, "s1.pdf");
        File out = layer(src, dir, "o1.pdf", words);
        String got = text(out);
        System.out.println("  layer: " + got);

        want(got, "\u20b9500", "rupee amount is exact, not Rs.");
        want(got, "30\u201340", "en dash is exact, not -");
        want(got, "a\u2014b", "em dash is exact");
        want(got, "\u201cquoted\u201d", "curly quotes are exact");
        want(got, "CO\u2082", "subscript is exact");
        want(got, "25\u00b0C", "degree sign is exact");
        want(got, "50%", "percent survives");
        want(got, "caf\u00e9", "accented e is exact");
        want(got, "\u00fcber", "accented u is exact");
        want(got, "5->10", "arrow falls back to -> (the font has no arrow)");
        want(got, "x>=y", ">= falls back to >=");
        want(got, "a!=b", "!= falls back to !=");
        wantNot(got, "?", "nothing is written as a question mark");
        wantNot(got, "\u6f22", "a character with no glyph and no substitute is dropped");
        // a word that is only a symbol and has no letter or digit must not be written at all
        check(!got.trim().endsWith("->"), "a lone arrow does not leave a dangling glyph");

        check(out.length() < 200_000, "the font is subset, not copied whole (" + out.length() + " bytes)");
        check(PdfEngine.search(out, "\u20b9500", false).size() == 1, "search finds the rupee amount");
        check(PdfEngine.search(out, "CO\u2082", false).size() == 1, "search finds the subscript");

        // the glyph cache must not survive a font change
        PdfEngine.setOcrFont(null);
        File outNoFont = layer(src, dir, "o1b.pdf", words);
        String plain = text(outNoFont);
        System.out.println("  no font: " + plain);
        want(plain, "Rs.500", "without the font the rupee becomes Rs. (old behaviour)");
        want(plain, "CO2", "without the font the subscript becomes 2");
        want(plain, "caf\u00e9", "without the font accented Latin still works (WinAnsi has it)");
        wantNot(plain, "?", "without the font nothing becomes a question mark either");

        PdfEngine.setOcrFont(font);
        File again = layer(src, dir, "o1c.pdf", words);
        want(text(again), "\u20b9500", "loading the font again still writes the rupee exactly (cache cleared)");

        // ---------------------------------------------------------------- item 5
        System.out.println();
        System.out.println("== item 5: no stacked layers ==");

        // a second run must not write the words again
        File twice = dir(dir, "o2.pdf");
        PdfEngine.addTextLayer(out, page(W, H, words), twice);
        String twiceText = text(twice);
        check(count(twiceText, "\u20b9500") == 1, "running the layer twice leaves one copy of the rupee amount");
        check(count(twiceText, "CO\u2082") == 1, "running the layer twice leaves one copy of the subscript");
        check(twice.length() <= out.length() + 2048,
                "the second run does not grow the file (" + out.length() + " -> " + twice.length() + ")");

        // a page that already has VISIBLE text still needs a layer: that was the bug
        File visible = dir(dir, "visible.pdf");
        try (PDDocument d = new PDDocument()) {
            PDPage pg = new PDPage(new PDRectangle(595f, 842f));
            d.addPage(pg);
            try (PDPageContentStream cs = new PDPageContentStream(d, pg)) {
                cs.beginText();
                cs.setFont(PDType1Font.HELVETICA_BOLD, 18);
                cs.newLineAtOffset(60, 760);
                cs.showText("ACCOUNT OPENING FORM");
                cs.endText();
            }
            d.save(visible);
        }
        File visibleOut = layer(visible, dir, "visible_o.pdf",
                new String[]{"PASSBOOK", "NUMBER"});
        String visibleText = text(visibleOut);
        want(visibleText, "ACCOUNT OPENING FORM", "the visible text is untouched");
        want(visibleText, "PASSBOOK", "a page with visible text still gets an OCR layer");

        // a blank page and an empty word list must be no-ops, not errors
        File emptyOut = dir(dir, "empty.pdf");
        PdfEngine.addTextLayer(visible, Collections.<PdfEngine.PageText>emptyList(), emptyOut);
        check(emptyOut.length() > 0, "an empty word list still produces a valid file");

        // ---------------------------------------------------------------- item 4
        System.out.println();
        System.out.println("== item 4: the junk filter must not eat real text ==");
        String[] shortWords = {"of", "50", "is", "7", "Rs"};
        File shortOut = layer(blank(dir, "s3.pdf"), dir, "o3.pdf", shortWords);
        String shortText = text(shortOut);
        for (String w : shortWords) {
            want(shortText, w, "short word \"" + w + "\" survives");
        }

        // ---------------------------------------------------------------- summary
        System.out.println();
        System.out.println(pass + " passed, " + fail + " failed");
        System.out.println(fail == 0 ? "OCRPAN: PASS" : "OCRPAN: FAIL");
        if (fail != 0) System.exit(1);
    }

    // ------------------------------------------------------------------ helpers

    static File dir(File d, String n) { return new File(d, n); }

    static File blank(File d, String n) throws Exception {
        File f = new File(d, n);
        try (PDDocument doc = new PDDocument()) {
            doc.addPage(new PDPage(new PDRectangle(595f, 842f)));
            doc.save(f);
        }
        return f;
    }

    /** Lay out the words left to right across the page, like a real line of text. */
    static List<PdfEngine.PageText> page(int w, int h, String[] words) {
        float size = 24f, cursor = 60f, gap = 6f;
        List<PdfEngine.OcrWord> boxes = new ArrayList<>();
        for (String wd : words) {
            float boxW = Math.max(20f, wd.length() * size * 0.55f);
            boxes.add(new PdfEngine.OcrWord(wd, cursor / 595f * w,
                    (842f - 700f - size * 0.72f) / 842f * h, boxW / 595f * w, size / 842f * h));
            cursor += boxW + gap;
        }
        return Collections.singletonList(new PdfEngine.PageText(1, w, h, boxes));
    }

    static File layer(File src, File d, String name, String[] words) throws Exception {
        File out = new File(d, name);
        PdfEngine.addTextLayer(src, page(W, H, words), out);
        return out;
    }

    static String text(File f) throws Exception {
        try (PDDocument d = PDDocument.load(f)) {
            return new PDFTextStripper().getText(d).replace("\n", " ").replaceAll("\\s+", " ").trim();
        }
    }

    static int count(String hay, String needle) {
        int n = 0, i = 0;
        while ((i = hay.indexOf(needle, i)) >= 0) { n++; i += needle.length(); }
        return n;
    }

    static void want(String hay, String needle, String what) { check(hay.contains(needle), what); }

    static void wantNot(String hay, String needle, String what) { check(!hay.contains(needle), what); }

    static void check(boolean ok, String what) {
        System.out.println((ok ? "  PASS - " : "  FAIL - ") + what);
        if (ok) pass++; else fail++;
    }
}
