import com.kavopdf.app.engine.PdfEngine;
import android.graphics.Bitmap;
import java.io.*;
import java.util.*;

/**
 * Stands in for the app: loads the rendered page images, paints the black boxes on
 * them exactly like the Android Canvas does, then asks the engine to flatten.
 */
public class TestRedact {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  public static void main(String[] a) throws Exception {
    // spec file: pageNo \t pngPath \t pxPerPoint \t x0 \t y0 \t x1 \t y1 (display points)
    List<Integer> pages = new ArrayList<>();
    List<Bitmap> bmps = new ArrayList<>();
    BufferedReader r = new BufferedReader(new InputStreamReader(
            new FileInputStream(new File(W, "redact_spec.tsv")), "UTF-8"));
    String line;
    while ((line = r.readLine()) != null) {
      if (line.trim().isEmpty()) continue;
      String[] f = line.split("\t");
      int page = Integer.parseInt(f[0]);
      java.awt.image.BufferedImage srcImg = javax.imageio.ImageIO.read(new File(f[1]));
      java.awt.image.BufferedImage bi = new java.awt.image.BufferedImage(
              srcImg.getWidth(), srcImg.getHeight(), java.awt.image.BufferedImage.TYPE_INT_ARGB);
      java.awt.Graphics2D bg = bi.createGraphics();
      bg.drawImage(srcImg, 0, 0, null); bg.dispose();
      Bitmap bmp = new Bitmap(bi);
      float k = Float.parseFloat(f[2]);
      java.awt.Graphics2D g = bi.createGraphics();
      g.setColor(java.awt.Color.BLACK);
      for (int i = 3; i + 3 < f.length; i += 4) {
        float x0 = Float.parseFloat(f[i]) * k, y0 = Float.parseFloat(f[i+1]) * k;
        float x1 = Float.parseFloat(f[i+2]) * k, y1 = Float.parseFloat(f[i+3]) * k;
        // paint a little wider than asked, so no edge can bleed
        g.fillRect((int)x0 - 6, (int)y0 - 6, (int)(x1 - x0) + 12, (int)(y1 - y0) + 12);
      }
      g.dispose();
      pages.add(page);
      bmps.add(bmp);
    }
    r.close();
    int[] pn = new int[pages.size()];
    for (int i = 0; i < pn.length; i++) pn[i] = pages.get(i);
    File src = new File(W, "redact_src.pdf");
    File out = new File(W, "redact_out.pdf");
    PdfEngine.redactPages(src, pn, bmps.toArray(new Bitmap[0]), out);
    System.out.println("redacted " + pn.length + " page(s)");
  }
}
