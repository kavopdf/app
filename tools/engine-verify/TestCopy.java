import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import java.io.*;
import java.util.*;

public class TestCopy {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  public static void main(String[] a) throws Exception {
    W.mkdirs();
    File src = new File(W, "copy_src.pdf");
    try (PDDocument d = new PDDocument()) {
      PDPage p = new PDPage(PDRectangle.A4);
      try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
        cs.beginText(); cs.setFont(PDType1Font.HELVETICA, 16);
        cs.newLineAtOffset(72, 700);
        cs.showText("Hello world from KavoPDF"); cs.newLineAtOffset(0, -30);
        cs.showText("second line of text"); cs.endText();
      }
      d.addPage(p);
      d.save(src);
    }
    // index once
    long t0 = System.currentTimeMillis();
    PdfEngine.TextIndex idx = PdfEngine.indexText(src);
    long t1 = System.currentTimeMillis();
    System.out.println("INDEX_MS " + (t1 - t0));

    // repeated searches must be near-instant (no re-parse)
    long t2 = System.currentTimeMillis();
    int hits = 0;
    for (int i = 0; i < 5; i++) hits = PdfEngine.searchIndex(idx, "world", false).size();
    long t3 = System.currentTimeMillis();
    System.out.println("REPEAT5_MS " + (t3 - t2) + " hits=" + hits);

    // words for tap-to-copy
    StringBuilder sb = new StringBuilder();
    for (PdfEngine.Word w : PdfEngine.wordsOnPage(idx, 1)) {
      sb.append("WORD\t").append(w.page).append('\t').append(w.x).append('\t').append(w.y)
        .append('\t').append(w.w).append('\t').append(w.h).append('\t').append(w.text).append('\n');
    }
    sb.append("PAGETEXT\t").append(PdfEngine.pageText(src, 1).replace('\n', '|')).append('\n');
    try (Writer w = new OutputStreamWriter(new FileOutputStream(new File(W, "copy_out.tsv")), "UTF-8")) {
      w.write(sb.toString());
    }
    System.out.println("words + page text written");
  }
}
