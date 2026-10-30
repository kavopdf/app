import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import java.io.*;
import java.util.*;

public class TestBookmarks {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  public static void main(String[] a) throws Exception {
    W.mkdirs();
    File src = new File(W, "bm_src.pdf");
    try (PDDocument d = new PDDocument()) {
      for (int i = 1; i <= 5; i++) {
        PDPage p = new PDPage(); d.addPage(p);
        try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
          cs.beginText(); cs.setFont(PDType1Font.HELVETICA, 14);
          cs.newLineAtOffset(72, 700); cs.showText("Chapter " + i); cs.endText();
        }
      }
      d.save(src);
    }
    List<PdfEngine.Bookmark> marks = new ArrayList<>();
    marks.add(new PdfEngine.Bookmark("Introduction", 1));
    marks.add(new PdfEngine.Bookmark("Methods", 3));
    marks.add(new PdfEngine.Bookmark("Results", 4));
    marks.add(new PdfEngine.Bookmark("Appendix", 5));
    File out = new File(W, "bm_out.pdf");
    PdfEngine.setBookmarks(src, marks, out);
    List<PdfEngine.Bookmark> back = PdfEngine.bookmarks(out);
    System.out.println("READBACK " + back.size());
    for (PdfEngine.Bookmark b : back) System.out.println("  " + b.page + "\t" + b.title);

    // report PDF
    List<String> lines = new ArrayList<>();
    for (int i = 1; i <= 120; i++) lines.add("2026-10-24 12:0" + (i % 10) + "  |  Encrypt PDF  |  report-" + i + ".pdf");
    File rep = new File(W, "log_report.pdf");
    PdfEngine.reportPdf(rep, "KavoPDF activity log", lines);
    System.out.println("REPORT_PAGES " + PdfEngine.pageCount(rep));
  }
}
