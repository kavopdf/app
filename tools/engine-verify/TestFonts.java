import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import java.io.*;

public class TestFonts {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  static File src;
  public static void main(String[] a) throws Exception {
    W.mkdirs();
    src = new File(W, "font_src.pdf");
    try (PDDocument d = new PDDocument()) {
      for (int i = 0; i < 2; i++) {
        PDPage p = new PDPage(); d.addPage(p);
        try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
          cs.beginText(); cs.setFont(PDType1Font.HELVETICA, 12);
          cs.newLineAtOffset(60, 700); cs.showText("body"); cs.endText();
        }
      }
      d.save(src);
    }
    String[] fonts = {"Helvetica", "Helvetica Bold", "Times", "Times Bold", "Courier"};
    for (int i = 0; i < fonts.length; i++) {
      PdfEngine.WatermarkOptions o = new PdfEngine.WatermarkOptions();
      o.text = "SAMPLE";
      o.font = fonts[i].startsWith("Times") ? "Times" : fonts[i].startsWith("Courier") ? "Courier" : "Helvetica";
      o.bold = fonts[i].endsWith("Bold");
      o.opacity = 1f;
      o.fontSize = 40f;
      File out = new File(W, "font_wm_" + i + ".pdf");
      PdfEngine.watermarkText(src, o, out);
      System.out.println("WM " + i + " requested=" + fonts[i] + " -> " + out.getName());
    }
    // custom text link, one page and all pages
    File t1 = new File(W, "font_link_one.pdf");
    PdfEngine.addTextLink(src, 1, 0.2f, 0.2f, 20f, "Times link", "Times", 0xFF0000FF, "https://example.com", 1f, t1);
    File t2 = new File(W, "font_link_all.pdf");
    PdfEngine.addTextLinkAllPages(src, 0.2f, 0.5f, 20f, "Courier link", "Courier", 0xFF00AA00, "https://example.com", 1f, t2);
    System.out.println("LINK one -> " + t1.getName() + " | all -> " + t2.getName());
  }
}
