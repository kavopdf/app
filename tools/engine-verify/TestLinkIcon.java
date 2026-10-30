import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import android.graphics.Bitmap;
import java.io.*;
import java.util.*;

public class TestLinkIcon {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  public static void main(String[] a) throws Exception {
    W.mkdirs();
    // ---- 1. a small icon bitmap (a coloured disc with a white glyph) ----
    Bitmap bmp = Bitmap.createBitmap(256, 256, Bitmap.Config.ARGB_8888);
    java.awt.image.BufferedImage bi = bmp._image();
    java.awt.Graphics2D g = bi.createGraphics();
    g.setRenderingHint(java.awt.RenderingHints.KEY_ANTIALIASING, java.awt.RenderingHints.VALUE_ANTIALIAS_ON);
    g.setColor(new java.awt.Color(0x14, 0x9E, 0x8C)); g.fillRoundRect(8,8,240,240,72,72);
    g.setColor(java.awt.Color.WHITE); g.setStroke(new java.awt.BasicStroke(26f, java.awt.BasicStroke.CAP_ROUND, java.awt.BasicStroke.JOIN_ROUND));
    g.drawLine(96,150,150,96); g.drawLine(150,96,168,114); g.drawLine(88,158,106,176);
    g.drawOval(66,120,60,60); g.drawOval(132,66,60,60);
    g.dispose();
    File icon = new File(W, "link_icon.png");
    try (FileOutputStream fos = new FileOutputStream(icon)) { bmp.compress(Bitmap.CompressFormat.PNG, 100, fos); }

    // ---- 2. a source page + a link icon placed at a known display spot ----
    File src = new File(W, "icon_src.pdf");
    try (PDDocument d = new PDDocument()) {
      PDPage p = new PDPage(PDRectangle.A4);
      try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
        cs.beginText(); cs.setFont(PDType1Font.HELVETICA, 14);
        cs.newLineAtOffset(72, 700); cs.showText("Page with a link icon"); cs.endText();
      }
      d.addPage(p);
      d.save(src);
    }
    File out = new File(W, "icon_out.pdf");
    PdfEngine.addLinkIcon(src, 1, 420f, 120f, 40f, icon, "https://example.com", 1f, out);
    System.out.println("icon link written");

    // ---- 3. search timing on a 200 page document ----
    File big = new File(W, "big_search.pdf");
    try (PDDocument d = new PDDocument()) {
      for (int i = 0; i < 200; i++) {
        PDPage p = new PDPage(PDRectangle.A4);
        try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
          cs.beginText(); cs.setFont(PDType1Font.HELVETICA, 12);
          cs.newLineAtOffset(72, 700);
          cs.showText("Page " + (i + 1) + " contains the marker word needle" + (i % 7));
          cs.endText();
        }
        d.addPage(p);
      }
      d.save(big);
    }
    long t0 = System.currentTimeMillis();
    List<PdfEngine.Match> hits = PdfEngine.search(big, "needle", false);
    long t1 = System.currentTimeMillis();
    System.out.println("SEARCH_TIME_MS " + (t1 - t0) + " over 200 pages, hits=" + hits.size());
    long t2 = System.currentTimeMillis();
    int links = PdfEngine.findLinks(big).size();
    long t3 = System.currentTimeMillis();
    System.out.println("LINKSCAN_TIME_MS " + (t3 - t2) + " links=" + links);
  }
}
