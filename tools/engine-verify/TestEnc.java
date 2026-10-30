import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.encryption.AccessPermission;
import com.tom_roush.pdfbox.cos.*;
import java.io.File;

public class TestEnc {
  public static void main(String[] a) throws Exception {
    File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
    W.mkdirs();
    File src = new File(W, "encsrc.pdf");
    try (PDDocument d = new PDDocument()) { d.addPage(new PDPage(PDRectangle.A4)); d.save(src); }

    File out = new File(W, "encprobe.pdf");
    PdfEngine.encrypt(src, "user123", "owner123", out);

    try (PDDocument d = PDDocument.load(out, "user123")) {
      COSDictionary enc = d.getDocument().getEncryptionDictionary();
      int v = enc.getInt(COSName.V), r = enc.getInt(COSName.R);
      System.out.println("V=" + v + " R=" + r + "  => "
          + (v == 5 ? "AES-256 (modern)" : v == 2 ? "RC4 (old)" : "other"));
      AccessPermission p = d.getCurrentAccessPermission();
      System.out.println("print=" + p.canPrint() + " extract=" + p.canExtractContent()
          + " modify=" + p.canModify() + " annotate=" + p.canModifyAnnotations());
    }
    boolean locked;
    try { PdfEngine.pageCount(out); locked = false; } catch (Exception e) { locked = true; }
    System.out.println("opens without password: " + (locked ? "NO (locked, good)" : "YES (BAD)"));
    System.out.println("opens with password:    " + (PdfEngine.pageCount(out, "user123") == 1 ? "YES" : "NO"));
    boolean wrongRejected;
    try { PdfEngine.pageCount(out, "wrongpw"); wrongRejected = false; } catch (Exception e) { wrongRejected = true; }
    System.out.println("wrong password rejected: " + (wrongRejected ? "YES (good)" : "NO (BAD)"));
  }
}
