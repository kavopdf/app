import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import java.io.*;
import java.util.*;

public class TestCrop {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  public static void main(String[] a) throws Exception {
    W.mkdirs();
    File base = new File(W, "cropbase.pdf");
    try (PDDocument d = new PDDocument()) {
      PDPage p = new PDPage(PDRectangle.A4);
      d.addPage(p);
      try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
        cs.setNonStrokingColor(230, 20, 20);
        cs.addRect(0, 421, 297.5f, 421); cs.fill();          // top-left quadrant
        cs.setNonStrokingColor(20, 20, 230);
        cs.addRect(297.5f, 0, 297.5f, 421); cs.fill();       // bottom-right quadrant
      }
      d.addPage(new PDPage(PDRectangle.A4));                  // page 2 stays untouched
      d.save(base);
    }
    File out = new File(W, "cropped.pdf");
    // crop page 1 to the top-left quadrant of the DISPLAYED page
    PdfEngine.cropPages(base, 1, 0f, 0f, 297.5f, 421f, false, out);
    System.out.println("cropped page1 display size: " + Arrays.toString(PdfEngine.pageDisplaySizes(out).get(0)));
    System.out.println("page count: " + PdfEngine.pageCount(out));
  }
}
