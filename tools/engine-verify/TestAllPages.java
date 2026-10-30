import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import android.graphics.Bitmap;
import java.io.*;

public class TestAllPages {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  public static void main(String[] a) throws Exception {
    W.mkdirs();
    Bitmap bmp = Bitmap.createBitmap(256, 256, Bitmap.Config.ARGB_8888);
    java.awt.image.BufferedImage bi = bmp._image();
    java.awt.Graphics2D g = bi.createGraphics();
    g.setRenderingHint(java.awt.RenderingHints.KEY_ANTIALIASING, java.awt.RenderingHints.VALUE_ANTIALIAS_ON);
    g.setColor(new java.awt.Color(0x14,0x9E,0x8C)); g.fillRoundRect(8,8,240,240,72,72);
    g.dispose();
    File icon = new File(W, "ap_icon.png");
    try (FileOutputStream fos = new FileOutputStream(icon)) { bmp.compress(Bitmap.CompressFormat.PNG, 100, fos); }

    File src = new File(W, "ap_src.pdf");
    try (PDDocument d = new PDDocument()) {
      for (int i = 0; i < 5; i++) {
        PDPage p = new PDPage(PDRectangle.A4);
        d.addPage(p);
        if (i == 2) p.setRotation(90);      // one page rotated, must still work
      }
      d.save(src);
    }
    File out = new File(W, "ap_out.pdf");
    PdfEngine.addLinkIconAllPages(src, 380f, 90f, 40f, icon, "https://example.com/all", 1f, out);
    System.out.println("all-pages icon applied");
    File out2 = new File(W, "ap_out2.pdf");
    PdfEngine.addTextLinkAllPages(src, 120f, 500f, 22f, "KavoPDF", "Helvetica Bold",
            0xFF1D4ED8, "https://example.com/text", 1f, out2);
    System.out.println("all-pages text applied");
  }
}
