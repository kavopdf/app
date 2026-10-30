import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import com.tom_roush.pdfbox.text.*;
import java.io.File;
import java.util.*;

/**
 * Does the invisible OCR layer sit exactly on the ink?
 *
 * A page is drawn with text at known coordinates. OCR boxes are then handed in that
 * match those coordinates exactly (a perfect OCR result), addTextLayer writes the
 * invisible layer, and the layer is read back with the text stripper to compare where
 * each character actually landed against where the ink was. The answer is in points;
 * 1 pt is 1/72 inch, so 2 pt is well under a millimetre on any screen.
 */
public class TestOcrPos {
    /** getCharactersByArticle is protected, so expose it through a subclass. */
    static class Collector extends PDFTextStripper {
        Collector() throws java.io.IOException { super(); }
        List<TextPosition> all() {
            List<TextPosition> out = new ArrayList<>();
            for (List<TextPosition> art : getCharactersByArticle()) out.addAll(art);
            return out;
        }
    }

    static final int IMG_W = 2600, IMG_H = 3368;   // A4 at 2600 px wide, like the app

    public static void main(String[] a) throws Exception {
        File dir = new File(System.getProperty("java.io.tmpdir"), "kavopdf-ocr");
        dir.mkdirs();
        File src = new File(dir, "ocr_src.pdf");

        // A4 in points, and the same page as the 2600 px raster the app OCRs
        float pw = 595f, ph = 842f;
        float sx = IMG_W / pw;               // px per point
        float sy = IMG_H / ph;
        float size = 24f;
        float[] xs = {100f, 260f};
        float ys = 700f;
        String[] words = {"HELLO", "WORLD"};

        try (PDDocument d = new PDDocument()) {
            PDPage page = new PDPage(new PDRectangle(pw, ph));
            d.addPage(page);
            try (PDPageContentStream cs = new PDPageContentStream(d, page)) {
                cs.setFont(PDType1Font.HELVETICA, size);
                for (int i = 0; i < words.length; i++) {
                    cs.beginText();
                    cs.newLineAtOffset(xs[i], ys);
                    cs.showText(words[i]);
                    cs.endText();
                }
            }
            d.save(src);
        }

        // OCR boxes in IMAGE pixels that correspond to the ink above.
        // The app's y is measured from the top of the raster.
        List<PdfEngine.OcrWord> ocr = new ArrayList<>();
        for (int i = 0; i < words.length; i++) {
            float wpt = PDType1Font.HELVETICA.getStringWidth(words[i]) / 1000f * size;
            float xpx = xs[i] * sx;
            float wpx = wpt * sx;
            float hpx = size * sy;                       // cap height roughly
            float ypx = (ph - ys - size * 0.72f) * sy;   // top of the ink
            ocr.add(new PdfEngine.OcrWord(words[i], xpx, ypx, wpx, hpx));
        }
        List<PdfEngine.PageText> pages = new ArrayList<>();
        pages.add(new PdfEngine.PageText(1, IMG_W, IMG_H, ocr));

        File out = new File(dir, "ocr_out.pdf");
        PdfEngine.addTextLayer(src, pages, out);

        // read the layer back and compare
        Collector ts = new Collector();
        ts.setSortByPosition(true);
        List<TextPosition> chars = new ArrayList<>();
        try (PDDocument d = PDDocument.load(out)) {
            ts.setStartPage(1);
            ts.setEndPage(1);
            ts.getText(d);
            chars.addAll(ts.all());
        }
        String got = "";
        for (TextPosition t : chars) got += t.getUnicode();
        System.out.println("layer text: \"" + got.replace("\n", " ") + "\"");
        System.out.println("characters found: " + chars.size());

        int fail = 0;
        if (!got.replaceAll("\\s+", "").contains("HELLOWORLD")) {
            System.out.println("  FAIL text not in the layer");
            fail++;
        }

        // expected start of each word in points
        double maxErr = 0;
        int idx = 0;
        for (int i = 0; i < words.length; i++) {
            while (idx < chars.size() && !Character.isLetterOrDigit(chars.get(idx).getUnicode().charAt(0))) idx++;
            if (idx >= chars.size()) { System.out.println("  FAIL ran out of characters"); fail++; break; }
            TextPosition first = chars.get(idx);
            double ex = first.getXDirAdj(), ey = first.getYDirAdj();
            // YDirAdj is measured from the top of the page
            double wantX = xs[i], wantYtop = ph - ys;
            double dx = Math.abs(ex - wantX);
            double dy = Math.abs(ey - wantYtop);
            System.out.printf("  %-6s ink x=%.1f  layer x=%.1f  (dx=%.2f pt)   ink top y=%.1f  layer y=%.1f  (dy=%.2f pt)%n",
                    words[i], wantX, ex, dx, wantYtop, ey, dy);
            maxErr = Math.max(maxErr, Math.max(dx, dy));
            idx += words[i].length();
        }
        System.out.printf("worst offset: %.2f pt  (%.2f mm)%n", maxErr, maxErr * 25.4 / 72);
        if (maxErr > 2.0) { System.out.println("  FAIL more than 2 pt off"); fail++; }
        else System.out.println("  PASS - every word lands within 2 pt of the ink");

        // a Devanagari word must be skipped, never written as "?"
        List<PdfEngine.OcrWord> hi = new ArrayList<>();
        hi.add(new PdfEngine.OcrWord("\u0928\u092e\u0938\u094d\u0924\u0947", 100, 100, 200, 40));
        hi.add(new PdfEngine.OcrWord("Hello", 400, 100, 150, 40));
        File hiOut = new File(dir, "ocr_hi.pdf");
        PdfEngine.addTextLayer(src, Collections.singletonList(new PdfEngine.PageText(1, IMG_W, IMG_H, hi)), hiOut);
        String hiText = "";
        try (PDDocument d = PDDocument.load(hiOut)) {
            PDFTextStripper s2 = new PDFTextStripper();
            hiText = s2.getText(d);
        }
        System.out.println("mixed page layer: \"" + hiText.replace("\n", " ").trim() + "\"");
        if (hiText.contains("?")) { System.out.println("  FAIL a question mark was written"); fail++; }
        else if (!hiText.contains("Hello")) { System.out.println("  FAIL the Latin word was lost"); fail++; }
        else System.out.println("  PASS - Hindi skipped, Latin kept, no '?' in the index");

        // a rupee amount must survive as something a reader can copy and search
        List<PdfEngine.OcrWord> bill = new ArrayList<>();
        bill.add(new PdfEngine.OcrWord("\u20b9500", 100, 100, 160, 40));
        bill.add(new PdfEngine.OcrWord("What is 2+2?", 400, 100, 300, 40));
        File billOut = new File(dir, "ocr_bill.pdf");
        PdfEngine.addTextLayer(src, Collections.singletonList(
                new PdfEngine.PageText(1, IMG_W, IMG_H, bill)), billOut);
        String billText;
        try (PDDocument d = PDDocument.load(billOut)) {
            billText = new PDFTextStripper().getText(d).replace("\n", " ").trim();
        }
        System.out.println("bill layer: \"" + billText + "\"");
        if (!billText.contains("Rs.500")) {
            System.out.println("  FAIL the rupee amount did not survive"); fail++;
        } else if (!billText.contains("2+2?")) {
            System.out.println("  FAIL the question mark was lost"); fail++;
        } else {
            System.out.println("  PASS - \u20b9500 copies as Rs.500 and '?' survives");
        }

        System.out.println(fail == 0 ? "\nOCRPOS: PASS" : "\nOCRPOS: " + fail + " FAILED");
        if (fail != 0) System.exit(1);
    }
}
