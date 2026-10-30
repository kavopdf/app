import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import android.graphics.Bitmap;
import java.io.*;

public class TestOpacity {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  public static void main(String[] a) throws Exception {
    W.mkdirs();
    // an icon to place
    Bitmap bmp = Bitmap.createBitmap(256, 256, Bitmap.Config.ARGB_8888);
    java.awt.image.BufferedImage bi = bmp._image();
    java.awt.Graphics2D g = bi.createGraphics();
    g.setRenderingHint(java.awt.RenderingHints.KEY_ANTIALIASING, java.awt.RenderingHints.VALUE_ANTIALIAS_ON);
    g.setColor(new java.awt.Color(0x14, 0x9E, 0x8C)); g.fillRoundRect(8,8,240,240,72,72);
    g.dispose();
    File icon = new File(W, "op_icon.png");
    try (FileOutputStream fos = new FileOutputStream(icon)) { bmp.compress(Bitmap.CompressFormat.PNG, 100, fos); }

    File src = new File(W, "op_src.pdf");
    try (PDDocument d = new PDDocument()) {
      for (int i = 0; i < 4; i++) d.addPage(new PDPage(PDRectangle.A4));
      d.save(src);
    }
    // page 1: text 100%   page 2: text 40%   page 3: icon 100%   page 4: icon 40%
    File cur = src;
    String[] names = new String[5];
    // text pages
    File t1 = new File(W, "op_text100.pdf");
    PdfEngine.addTextLink(cur, 1, 150f, 300f, 40f, "SAMPLE", "Helvetica Bold", 0xFFCC0000,
            "https://example.com", 1.0f, t1);
    File t2 = new File(W, "op_text40.pdf");
    PdfEngine.addTextLink(t1, 2, 150f, 300f, 40f, "SAMPLE", "Helvetica Bold", 0xFFCC0000,
            "https://example.com", 0.4f, t2);
    // icon pages
    File i1 = new File(W, "op_icon100.pdf");
    PdfEngine.addLinkIcon(t2, 3, 200f, 300f, 60f, icon, "https://example.com", 1.0f, i1);
    File i2 = new File(W, "op_icon40.pdf");
    PdfEngine.addLinkIcon(i1, 4, 200f, 300f, 60f, icon, "https://example.com", 0.4f, i2);
    System.out.println("opacity test written");
    try (Writer w = new OutputStreamWriter(new FileOutputStream(new File(W, "op_name.txt")), "UTF-8")) {
      w.write(i2.getName());
    }
  }
}
