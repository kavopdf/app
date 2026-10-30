import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import java.io.*;
import java.util.*;

public class TestSearch {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  public static void main(String[] a) throws Exception {
    W.mkdirs();
    File src = new File(W, "search_src.pdf");
    try (PDDocument d = new PDDocument()) {
      for (int r : new int[]{0, 90}) {
        PDPage p = new PDPage(PDRectangle.A4);
        try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
          cs.beginText();
          cs.setFont(PDType1Font.HELVETICA, 16);
          cs.newLineAtOffset(72, 700);
          cs.showText("Invoice 48213 for KavoPDF");
          cs.newLineAtOffset(0, -30);
          cs.showText("Visit https://example.com/help for details");
          cs.newLineAtOffset(0, -30);
          cs.showText("Contact support@example.com today");
          cs.endText();
        }
        p.setRotation(r);
        d.addPage(p);
      }
      d.save(src);
    }
    StringBuilder out = new StringBuilder();
    for (String q : new String[]{"KavoPDF", "Invoice", "example"}) {
      for (PdfEngine.Match m : PdfEngine.search(src, q, false)) {
        out.append("SEARCH\t").append(m.page).append('\t').append(m.x).append('\t').append(m.y)
           .append('\t').append(m.w).append('\t').append(m.h).append('\t').append(q).append('\n');
      }
    }
    List<PdfEngine.FoundLink> found = PdfEngine.findLinks(src);
    for (PdfEngine.FoundLink l : found) {
      out.append("FOUND\t").append(l.page).append('\t').append(l.x).append('\t').append(l.y)
         .append('\t').append(l.w).append('\t').append(l.h).append('\t').append(l.url).append('\n');
    }
    File outPdf = new File(W, "search_links.pdf");
    int n = PdfEngine.addLinks(src, found, outPdf);
    out.append("ADDED\t").append(n).append('\n');
    new File(W, "search_results.tsv").delete();
    try (Writer w = new OutputStreamWriter(new FileOutputStream(new File(W, "search_results.tsv")), "UTF-8")) {
      w.write(out.toString());
    }
    System.out.println("search hits + links written (" + n + " links added)");
  }
}
