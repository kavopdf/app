import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Builds a rotated test document, then applies an OCR-style text layer to it. */
public class TestTextLayer {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");

  public static void main(String[] a) throws Exception {
    W.mkdirs();
    String mode = a.length > 0 ? a[0] : "make";
    if (mode.equals("make")) make();
    else apply();
  }

  /** four pages, same two text lines, one per rotation */
  static void make() throws Exception {
    try (PDDocument d = new PDDocument()) {
      for (int r : new int[]{0, 90, 180, 270}) {
        PDPage page = new PDPage(PDRectangle.A4);
        try (PDPageContentStream cs = new PDPageContentStream(d, page)) {
          cs.beginText();
          cs.setFont(PDType1Font.HELVETICA, 20);
          cs.newLineAtOffset(72, 700);
          cs.showText("Searchable rotation test");
          cs.setFont(PDType1Font.HELVETICA, 14);
          cs.newLineAtOffset(0, -45);
          cs.showText("Amount Rs 42,000 payable");
          cs.endText();
        }
        page.setRotation(r);
        d.addPage(page);
      }
      d.save(new File(W, "tl_src.pdf"));
    }
    System.out.println("built tl_src.pdf (4 pages, rotations 0/90/180/270)");
  }

  /** apply the text layer from measured boxes */
  static void apply() throws Exception {
    List<String> lines = Files.readAllLines(new File(W, "tl_words.tsv").toPath(), StandardCharsets.UTF_8);
    Map<Integer, List<PdfEngine.OcrWord>> byPage = new LinkedHashMap<>();
    Map<Integer, int[]> sizes = new HashMap<>();
    for (String l : lines) {
      if (l.trim().isEmpty()) continue;
      String[] f = l.split("\t");
      int page = Integer.parseInt(f[0].trim());
      int iw = Integer.parseInt(f[1].trim()), ih = Integer.parseInt(f[2].trim());
      byPage.computeIfAbsent(page, k -> new ArrayList<>()).add(new PdfEngine.OcrWord(f[7],
          Float.parseFloat(f[3]), Float.parseFloat(f[4]),
          Float.parseFloat(f[5]), Float.parseFloat(f[6])));
      sizes.put(page, new int[]{iw, ih});
    }
    List<PdfEngine.PageText> pages = new ArrayList<>();
    for (Map.Entry<Integer, List<PdfEngine.OcrWord>> e : byPage.entrySet()) {
      int[] sz = sizes.get(e.getKey());
      pages.add(new PdfEngine.PageText(e.getKey(), sz[0], sz[1], e.getValue()));
    }
    File out = new File(W, "tl_out.pdf");
    PdfEngine.addTextLayer(new File(W, "tl_src.pdf"), pages, out);
    System.out.println("applied text layer -> tl_out.pdf");
  }
}
