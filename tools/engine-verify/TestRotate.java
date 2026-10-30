import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import android.graphics.Bitmap;
import java.io.*;
import java.util.*;

public class TestRotate {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  public static void main(String[] a) throws Exception {
    W.mkdirs();
    File base = new File(W, "rotbase.pdf");
    try (PDDocument d = new PDDocument()) { d.addPage(new PDPage(PDRectangle.A4)); d.save(base); }

    for (int deg : new int[]{90, 180, 270}) {
      File rotated = new File(W, "rot" + deg + ".pdf");
      PdfEngine.rotatePages(base, null, deg, rotated);
      float[] ds = PdfEngine.pageDisplaySizes(rotated).get(0);
      int wd = Math.round(ds[0]), hd = Math.round(ds[1]);

      Bitmap bmp = Bitmap.createBitmap(wd, hd, Bitmap.Config.ARGB_8888);
      java.awt.image.BufferedImage bi = bmp._image();
      java.awt.Graphics2D g = bi.createGraphics();
      g.setColor(new java.awt.Color(0, 0, 255, 255));
      g.fillRect(0, 0, 160, 160);   // top-left corner of the DISPLAYED page
      g.dispose();
      File raster = new File(W, "ov" + deg + ".png");
      try (FileOutputStream fos = new FileOutputStream(raster)) {
        bmp.compress(Bitmap.CompressFormat.PNG, 100, fos);
      }
      File out = new File(W, "stamped" + deg + ".pdf");
      PdfEngine.stampDisplayRasters(rotated, Arrays.asList(1), Arrays.asList(raster), out);
      System.out.println("built " + deg + " (display " + wd + "x" + hd + ")");
    }
  }
}
