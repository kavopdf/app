import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.text.PDFTextStripper;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * With the bundled Unicode font loaded, the invisible layer must carry the characters
 * that were on the page - not substitutes. Helvetica could only draw Latin-1, so the
 * rupee sign became "Rs." and an en dash became "-".
 */
public class TestFontExact {
    static final int W = 2600, H = 3368;
    static int fail = 0;

    public static void main(String[] a) throws Exception {
        byte[] font = Files.readAllBytes(Paths.get(a[0]));
        PdfEngine.setOcrFont(font);
        check(PdfEngine.hasOcrFont(), "the bundled font loads");

        File dir = new File(System.getProperty("java.io.tmpdir"), "kavopdf_font");
        dir.mkdirs();
        File src = new File(dir, "s.pdf");
        try (PDDocument d = new PDDocument()) {
            d.addPage(new PDPage(new PDRectangle(595f, 842f)));
            d.save(src);
        }

        String[] words = {"\u20b9500", "only", "30\u201340", "CO\u2082", "What", "is", "2+2?"};
        float size = 24f, cursor = 60f, gap = 6f;
        List<PdfEngine.OcrWord> boxes = new ArrayList<>();
        for (String wd : words) {
            float boxW = Math.max(20f, wd.length() * size * 0.55f);
            boxes.add(new PdfEngine.OcrWord(wd, cursor / 595f * W,
                    (842f - 700f - size * 0.72f) / 842f * H, boxW / 595f * W, size / 842f * H));
            cursor += boxW + gap;
        }

        File out = new File(dir, "o.pdf");
        PdfEngine.addTextLayer(src, Collections.singletonList(
                new PdfEngine.PageText(1, W, H, boxes)), out);

        String got;
        try (PDDocument d = PDDocument.load(out)) {
            got = new PDFTextStripper().getText(d).replace("\n", " ").trim();
        }
        System.out.println("layer: \"" + got + "\"   (" + out.length() + " bytes)");

        check(got.contains("\u20b9500"), "the rupee amount is written exactly");
        check(got.contains("30\u201340"), "the en dash is written exactly");
        check(got.contains("CO\u2082"), "the subscript is written exactly");
        check(got.contains("2+2?"), "the question mark survives");
        check(got.contains("What is"), "word spaces survive");
        check(out.length() < 200_000, "the font is subset, not copied whole");

        // searching has to agree with what is in the layer
        check(PdfEngine.search(out, "\u20b9500", false).size() == 1, "search finds the rupee amount");
        check(PdfEngine.search(out, "CO\u2082", false).size() == 1, "search finds the subscript");

        // and the plain fallback still works when no font is available
        PdfEngine.setOcrFont(null);
        check(!PdfEngine.hasOcrFont(), "the font can be cleared");
        File out2 = new File(dir, "o2.pdf");
        PdfEngine.addTextLayer(src, Collections.singletonList(
                new PdfEngine.PageText(1, W, H, boxes)), out2);
        String got2;
        try (PDDocument d = PDDocument.load(out2)) {
            got2 = new PDFTextStripper().getText(d).replace("\n", " ").trim();
        }
        System.out.println("no font: \"" + got2 + "\"");
        check(got2.contains("Rs.500"), "without the font the rupee becomes Rs. (the old behaviour)");
        check(got2.contains("2+2?"), "without the font the question mark still survives");

        System.out.println(fail == 0 ? "\nFONTEXACT: PASS" : "\nFONTEXACT: " + fail + " FAILED");
        if (fail != 0) System.exit(1);
    }

    static void check(boolean ok, String what) {
        System.out.println((ok ? "  PASS - " : "  FAIL - ") + what);
        if (!ok) fail++;
    }
}
