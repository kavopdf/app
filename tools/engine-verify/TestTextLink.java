import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import java.io.*;

public class TestTextLink {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  public static void main(String[] a) throws Exception {
    W.mkdirs();
    File src = new File(W, "tl_src2.pdf");
    try (PDDocument d = new PDDocument()) {
      for (int r : new int[]{0, 90, 180, 270}) {
        PDPage p = new PDPage(PDRectangle.A4);
        d.addPage(p);
        p.setRotation(r);
      }
      d.save(src);
    }
    File out = new File(W, "tl_out2.pdf");
    // red Helvetica-Bold text, 18pt, at a known display spot
    try (PDDocument d = PDDocument.load(src)) {
      d.save(out);
    }
    // apply per page (each page needs its own call, so chain through temp files)
    File cur = out;
    for (int page = 1; page <= 4; page++) {
      File next = new File(W, "tl_out2_" + page + ".pdf");
      PdfEngine.addTextLink(cur, page, 300f, 200f, 18f, "Click here", "Helvetica Bold",
              0xFFCC0000, "https://example.com/offer", 1f, next);
      cur = next;
    }
    System.out.println("text links written: " + cur.getName());
    // also record which file to check
    try (Writer w = new OutputStreamWriter(new FileOutputStream(new File(W, "tl2_name.txt")), "UTF-8")) {
      w.write(cur.getName());
    }
  }
}
