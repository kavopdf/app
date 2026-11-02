import com.kavopdf.app.engine.DocxWriter;
import com.kavopdf.app.engine.PdfToWord;
import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.pdmodel.PDPage;
import com.tom_roush.pdfbox.pdmodel.PDPageContentStream;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/** Checks the PDF to Word engine: text, structure, and that the .docx is a real package. */
public class TestPdfToWord {

    static int pass, fail;
    static File W;

    static void check(String what, boolean ok) {
        if (ok) { pass++; System.out.println("  PASS  " + what); }
        else { fail++; System.out.println("  FAIL  " + what); }
    }

    public static void main(String[] a) throws Exception {
        W = new File("/tmp/p2w-test");
        W.mkdirs();

        File pdf = new File(W, "sample.pdf");
        try (PDDocument d = new PDDocument()) {
            PDPage page = new PDPage(PDRectangle.A4);
            d.addPage(page);
            try (PDPageContentStream cs = new PDPageContentStream(d, page)) {
                cs.beginText();
                cs.setFont(PDType1Font.HELVETICA_BOLD, 22);
                cs.newLineAtOffset(70, 760);
                cs.showText("BIG HEADING");
                cs.endText();
                cs.beginText();
                cs.setFont(PDType1Font.HELVETICA, 11);
                cs.newLineAtOffset(70, 720);
                cs.showText("This is a body paragraph with ordinary words in it.");
                cs.endText();
                cs.beginText();
                cs.setFont(PDType1Font.HELVETICA, 11);
                cs.newLineAtOffset(70, 705);
                cs.showText("A second line that belongs to the same paragraph.");
                cs.endText();
            }
            d.save(pdf);
        }

        PdfToWord.Result r = PdfToWord.convert(pdf, "", null);
        PdfToWord.classifyHeadings(r);

        check("one page read", r.report.pages == 1);
        check("paragraphs found", r.paragraphCount() >= 2);

        File txt = new File(W, "out.txt");
        PdfToWord.writeTxt(r, txt);
        String text = new String(Files.readAllBytes(txt.toPath()), StandardCharsets.UTF_8);
        check("txt has the heading", text.contains("BIG HEADING"));
        check("txt has the body text", text.contains("ordinary words"));
        // The plain-text file keeps the lines the PDF drew. A .txt has no paragraph of its
        // own, and hard-wrapping a paragraph back into lines at a width the reader never saw
        // was the thing that made the text stop matching the document it came from.
        check("txt keeps the PDF's own line break",
                text.contains("with ordinary words in it.\n")
                        && text.contains("A second line that belongs to the same paragraph."));
        check("txt does not glue the two lines together",
                !text.contains("in it. A second line"));

        File docx = new File(W, "out.docx");
        DocxWriter.write(r, docx);
        boolean zipOk = false, hasDocument = false, hasStyles = false, hasHeadingStyle = false;
        try (ZipFile z = new ZipFile(docx)) {
            zipOk = true;
            ZipEntry doc = z.getEntry("word/document.xml");
            hasDocument = doc != null;
            hasStyles = z.getEntry("word/styles.xml") != null;
            if (doc != null) {
                java.io.InputStream in = z.getInputStream(doc);
                byte[] bytes = com.tom_roush.pdfbox.io.IOUtils.toByteArray(in);
                String xml = new String(bytes, StandardCharsets.UTF_8);
                hasHeadingStyle = xml.contains("Heading1");
                check("docx carries the text", xml.contains("BIG HEADING"));
                check("docx is well formed enough to contain w:body",
                        xml.startsWith("<?xml") && xml.contains("<w:body>"));
            }
        }
        check("docx is a zip package", zipOk);
        check("docx has document.xml", hasDocument);
        check("docx has styles.xml", hasStyles);
        check("the big line became a heading", hasHeadingStyle);

        // A borderless table: three rows of two aligned cells, no drawn lines anywhere.
        File tbl = new File(W, "borderless.pdf");
        try (PDDocument d = new PDDocument()) {
            PDPage page = new PDPage(PDRectangle.A4);
            d.addPage(page);
            try (PDPageContentStream cs = new PDPageContentStream(d, page)) {
                String[][] rows = {{"Item", "Amount"}, {"Widgets", "1200"}, {"Gadgets", "3400"}};
                float y = 720;
                for (String[] row : rows) {
                    cs.beginText();
                    cs.setFont(PDType1Font.HELVETICA, 11);
                    cs.newLineAtOffset(70, y);
                    cs.showText(row[0]);
                    cs.endText();
                    cs.beginText();
                    cs.setFont(PDType1Font.HELVETICA, 11);
                    cs.newLineAtOffset(260, y);
                    cs.showText(row[1]);
                    cs.endText();
                    y -= 16;
                }
            }
            d.save(tbl);
        }
        PdfToWord.Result tr = PdfToWord.convert(tbl, "", null);
        File ttxt = new File(W, "borderless.txt");
        PdfToWord.writeTxt(tr, ttxt);
        String ttext = new String(Files.readAllBytes(ttxt.toPath()), StandardCharsets.UTF_8);
        check("borderless table became a table", tr.report.tables >= 1);
        // A .txt has no table, so the cells go on their own lines, in row order. The table
        // itself is still a real table in the .docx.
        check("borderless rows keep their cells",
                ttext.contains("Widgets") && ttext.contains("1200")
                        && ttext.indexOf("Widgets") < ttext.indexOf("1200"));

        // A table whose rows carry different numbers of cells: a real table has empty cells,
        // and a row that stops early is still that row, not a reason to abandon the table.
        File uneven = new File(W, "uneven.pdf");
        try (PDDocument d = new PDDocument()) {
            PDPage page = new PDPage(PDRectangle.A4);
            d.addPage(page);
            try (PDPageContentStream cs = new PDPageContentStream(d, page)) {
                String[][] rows = {{"Name", "Qty", "Price"}, {"Bolts", "40", "12"}, {"Nuts", "25"}};
                float y = 720;
                float[] x = {70, 200, 330};
                for (String[] row : rows) {
                    for (int c = 0; c < row.length; c++) {
                        cs.beginText();
                        cs.setFont(PDType1Font.HELVETICA, 11);
                        cs.newLineAtOffset(x[c], y);
                        cs.showText(row[c]);
                        cs.endText();
                    }
                    y -= 16;
                }
            }
            d.save(uneven);
        }
        PdfToWord.Result ur = PdfToWord.convert(uneven, "", null);
        File utxt = new File(W, "uneven.txt");
        PdfToWord.writeTxt(ur, utxt);
        String utext = new String(Files.readAllBytes(utxt.toPath()), StandardCharsets.UTF_8);
        check("table with an uneven last row still becomes a table", ur.report.tables >= 1);
        check("uneven row keeps its cells in the right columns",
                utext.contains("Bolts") && utext.contains("40") && utext.contains("12")
                        && utext.contains("Nuts") && utext.contains("25"));

        // ---- annotations vs OCR: the two fallbacks must not both fire on one page ----
        {
            // A page whose words live only in a free-text annotation.
            File ann = new File(W, "annotation_only.pdf");
            try (PDDocument d = new PDDocument()) {
                PDPage pg = new PDPage(PDRectangle.A4);
                d.addPage(pg);
                com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotationText note =
                        new com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotationText();
                note.setRectangle(new PDRectangle(72, 700, 24, 24));
                note.setContents("STICKY NOTE MARKER");
                pg.getAnnotations().add(note);
                d.save(ann);
            }
            final int[] calls = {0};
            PdfToWord.OcrHook hook = new PdfToWord.OcrHook() {
                @Override public String text(int pageIndex) { calls[0]++; return "OCR MARKER"; }
            };
            PdfToWord.Result ra = PdfToWord.convert(ann, "", hook);
            File taF = new File(W, "annotation_only.txt");
            PdfToWord.writeTxt(ra, taF);
            String ta = new String(Files.readAllBytes(taF.toPath()), StandardCharsets.UTF_8);
            check("annotation text is read", ta.contains("STICKY NOTE MARKER"));
            check("OCR is not called when annotations gave the words", calls[0] == 0);
            check("OCR text does not appear twice", !ta.contains("OCR MARKER"));
            check("annotation page is not counted as OCR", ra.report.ocrPages == 0);
            check("annotation page is not counted as skipped", ra.report.skippedPages == 0);
            check("annotation page is not reported as empty", !ra.isEmpty());
        }
        {
            // A page with nothing on it at all: OCR must still be offered.
            File blank = new File(W, "blank_page.pdf");
            try (PDDocument d = new PDDocument()) {
                d.addPage(new PDPage(PDRectangle.A4));
                d.save(blank);
            }
            final int[] calls = {0};
            PdfToWord.OcrHook hook = new PdfToWord.OcrHook() {
                @Override public String text(int pageIndex) { calls[0]++; return "OCR MARKER"; }
            };
            PdfToWord.Result ra = PdfToWord.convert(blank, "", hook);
            File tbF = new File(W, "blank_page.txt");
            PdfToWord.writeTxt(ra, tbF);
            String ta = new String(Files.readAllBytes(tbF.toPath()), StandardCharsets.UTF_8);
            check("OCR runs on a page with no text layer", calls[0] == 1);
            check("OCR text reaches the page", ta.contains("OCR MARKER"));
            check("OCR page is counted", ra.report.ocrPages == 1);

            PdfToWord.Result none = PdfToWord.convert(blank, "", null);
            check("no hook means the page is reported, not silently dropped",
                    none.report.skippedPages == 1);
        }

        // ---- the .docx must put sectPr last: it is the section properties of the body ----
        {
            File d = new File(W, "sectpr.docx");
            PdfToWord.Result rs = PdfToWord.convert(new File(W, "annotation_only.pdf"), "", null);
            DocxWriter.write(rs, d);
            String xml;
            try (ZipFile z = new ZipFile(d)) {
                try (java.io.InputStream in = z.getInputStream(z.getEntry("word/document.xml"))) {
                    xml = new String(in.readAllBytes(), StandardCharsets.UTF_8);
                }
            }
            int body = xml.indexOf("<w:body>");
            int sect = xml.indexOf("<w:sectPr>");
            int close = xml.indexOf("</w:body>");
            check("document.xml has a body", body >= 0 && close > body);
            check("sectPr sits inside the body", sect > body && sect < close);
            check("sectPr is the last thing in the body",
                    sect > 0 && xml.substring(sect, close).indexOf("<w:p>") < 0
                            && xml.substring(sect, close).indexOf("<w:tbl>") < 0);
        }

        System.out.println("PDF2WORD TOTAL: " + pass + " passed, " + fail + " failed");
        if (fail > 0) System.exit(1);
    }
}
