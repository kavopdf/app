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
        check("wrapped lines joined into one paragraph",
                text.contains("with ordinary words in it. A second line"));

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
        check("borderless rows keep their cells", ttext.contains("Widgets | 1200"));

        System.out.println("PDF2WORD TOTAL: " + pass + " passed, " + fail + " failed");
        if (fail > 0) System.exit(1);
    }
}
