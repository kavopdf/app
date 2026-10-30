import com.kavopdf.app.engine.*;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Feeds deliberately corrupted structures to the engine and checks it fails SAFELY. */
public class TestHostile {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  static int pass = 0, fail = 0;
  static void check(String what, boolean ok) {
    System.out.println((ok ? "  PASS  " : "  FAIL  ") + what);
    if (ok) pass++; else fail++;
  }

  public static void main(String[] a) throws Exception {
    W.mkdirs();
    File src = new File(W, "hostile_base.pdf");
    try (PDDocument d = new PDDocument()) {
      d.addPage(new PDPage(PDRectangle.A4));
      d.save(src);
    }
    // 1. a normal signed file still verifies
    File signed = new File(W, "hostile_signed.pdf");
    PdfSigner.SignParams p = new PdfSigner.SignParams();
    p.name = "Test"; p.reason = "r"; p.location = "l";
    PdfSigner.sign(src, signed, p);
    List<PdfSigner.SignatureInfo> good = PdfSigner.verify(signed);
    check("a genuine signature still verifies", good.size() == 1 && good.get(0).valid);

    // 2. corrupt /ByteRange to absurd values (same byte length, so the file still parses)
    byte[] raw = Files.readAllBytes(signed.toPath());
    String text = new String(raw, StandardCharsets.ISO_8859_1);
    int i = text.indexOf("/ByteRange");
    check("found /ByteRange to corrupt", i > 0);
    int open = text.indexOf('[', i), close = text.indexOf(']', open);
    int inner = close - open - 1;
    int base = (inner - 3) / 4, rem = (inner - 3) % 4;
    StringBuilder sb = new StringBuilder();
    for (int k = 0; k < 4; k++) {
      int len = base + (k < rem ? 1 : 0);
      if (k > 0) sb.append(' ');
      sb.append("9".repeat(Math.max(1, len)));
    }
    String rebuilt = text.substring(0, open + 1) + sb + text.substring(close);
    File corrupt = new File(W, "hostile_badrange.pdf");
    Files.write(corrupt.toPath(), rebuilt.getBytes(StandardCharsets.ISO_8859_1));

    boolean safe;
    List<PdfSigner.SignatureInfo> res = null;
    try {
      res = PdfSigner.verify(corrupt);
      safe = true;
    } catch (Throwable t) {
      safe = false;
      System.out.println("        (threw " + t.getClass().getSimpleName() + ")");
    }
    check("a corrupt byte range does NOT crash the verifier", safe);
    check("a corrupt byte range is reported as invalid",
        res != null && !res.isEmpty() && !res.get(0).valid);

    // 3. extract images from a file with no images
    File exDir = new File(W, "hostile_ex"); exDir.mkdirs();
    check("extract on an image-free PDF is safe", PdfEngine.extractImages(src, exDir).isEmpty());

    // 4. compress a plain PDF (no images) does not blow up
    File comp = new File(W, "hostile_comp.pdf");
    PdfEngine.compress(src, comp, 1600, 0.7f);
    check("compress on an image-free PDF is safe", comp.exists() && comp.length() > 0);

    // 5. crop with absurd coordinates is clamped, not crashing
    File cropped = new File(W, "hostile_crop.pdf");
    PdfEngine.cropPages(src, 1, -9999f, -9999f, 99999f, 99999f, true, cropped);
    check("crop with absurd coordinates is safe", cropped.exists() && cropped.length() > 0);

    // 6. split with an out-of-range range yields nothing, not a crash
    File dir = new File(W, "hostile_split"); dir.mkdirs();
    List<File> parts = PdfEngine.splitToFiles(src, Arrays.asList(new int[]{5, 999999999}), dir, "x");
    check("split with a huge range produces no runaway files", parts.size() <= 1);

    // 7. keepPages with a bogus page list must fail cleanly, not crash
    boolean clean;
    try {
      PdfEngine.keepPages(src, Arrays.asList(99999), new File(W, "hostile_keep.pdf"));
      clean = true;                       // ignoring the bogus page is acceptable
    } catch (IllegalArgumentException e) {
      clean = true;                       // a clear, explained refusal is also fine
    } catch (Throwable t) {
      clean = false;
      System.out.println("        (threw " + t.getClass().getSimpleName() + ")");
    }
    check("keepPages with an unknown page fails cleanly", clean);

    System.out.println();
    System.out.println("HOSTILE-INPUT TOTAL: " + pass + " passed, " + fail + " failed");
    if (fail > 0) System.exit(1);
  }
}
