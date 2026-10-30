import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.text.PDFTextStripper;
import java.io.File;
import java.util.*;

/**
 * What a reader copies out of a scanned page, checked through addTextLayer itself.
 * Covers the three things that used to go wrong: a rupee amount losing its currency,
 * a question mark being turned into something else, and word spaces disappearing.
 */
public class TestOcrText {
    static final int W = 2600, H = 3368;
    static int fail = 0;

    public static void main(String[] a) throws Exception {
        File dir = new File(System.getProperty("java.io.tmpdir"), "kavopdf_ocrtext");
        dir.mkdirs();
        File src = new File(dir, "t.pdf");
        try (PDDocument d = new PDDocument()) {
            d.addPage(new PDPage(new PDRectangle(595f, 842f)));
            d.save(src);
        }

        // one line of word boxes, the way ML Kit hands them over
        String[] words = {"Rs.", "\u20b9500", "What", "is", "2+2?", "30\u201340", "\u00b0C", "CO\u2082"};
        float size = 24f, cursor = 60f, gap = 0.28f * size;
        List<PdfEngine.OcrWord> boxes = new ArrayList<>();
        for (String wd : words) {
            // Helvetica cannot measure the rupee sign, so measure what it will be
            // written as - the same substitution the layer makes.
            String measure = wd.replace("\u20b9", "Rs.").replace("\u2082", "2");
            float wpt = com.tom_roush.pdfbox.pdmodel.font.PDType1Font.HELVETICA
                    .getStringWidth(measure) / 1000f * size;
            float boxW = wpt;
            boxes.add(new PdfEngine.OcrWord(wd,
                    cursor / 595f * W,
                    (842f - 700f - size * 0.72f) / 842f * H,
                    boxW / 595f * W,
                    size / 842f * H));
            cursor += boxW + gap;
        }

        File out = new File(dir, "t_out.pdf");
        PdfEngine.addTextLayer(src, Collections.singletonList(
                new PdfEngine.PageText(1, W, H, boxes)), out);

        String got;
        try (PDDocument d = PDDocument.load(out)) {
            got = new PDFTextStripper().getText(d).replace("\n", " ").trim();
        }
        System.out.println("layer: \"" + got + "\"");

        check(got.contains("Rs.500"), "the rupee amount keeps its currency");
        check(got.contains("2+2?"), "the question mark survives");
        int q = 0;
        for (int i = 0; i < got.length(); i++) if (got.charAt(i) == '?') q++;
        // exactly one question mark, and it is the one that was printed
        check(q == 1, "exactly one question mark, the printed one, nothing invented");
        check(got.contains("What is"), "word spaces survive");
        check(got.contains("30-40"), "the en dash becomes a plain hyphen");
        check(got.contains("CO2"), "the subscript becomes a digit");

        // search has to agree with what is in the layer
        check(PdfEngine.search(out, "500", false).size() == 1, "search finds 500");
        check(PdfEngine.search(out, "What is", false).size() == 1, "search finds two words in a row");
        check(PdfEngine.search(out, "CO2", false).size() == 1, "search finds CO2");

        System.out.println(fail == 0 ? "\nOCRTEXT: PASS" : "\nOCRTEXT: " + fail + " FAILED");
        if (fail != 0) System.exit(1);
    }

    static void check(boolean ok, String what) {
        System.out.println((ok ? "  PASS - " : "  FAIL - ") + what);
        if (!ok) fail++;
    }
}
