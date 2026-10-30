import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import java.io.*;

public class TestEncrypt {
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");
  public static void main(String[] a) throws Exception {
    W.mkdirs();
    File plain = new File(W, "enc_plain.pdf");
    try (PDDocument d = new PDDocument()) {
      PDPage p = new PDPage(); d.addPage(p);
      try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
        cs.beginText(); cs.setFont(PDType1Font.HELVETICA, 14);
        cs.newLineAtOffset(72, 700); cs.showText("Confidential balance 42"); cs.endText();
      }
      d.save(plain);
    }
    File enc = new File(W, "enc_out.pdf");
    PdfEngine.encrypt(plain, "user-pass-123", "owner-pass-999", enc);
    System.out.println("ENC_OK " + enc.length());

    // opens with the user password
    try (PDDocument d = PDDocument.load(enc, "user-pass-123")) {
      System.out.println("USER_PW_OPENS " + d.getNumberOfPages());
    }
    // fails with a wrong password
    try {
      PDDocument.load(enc, "wrong-password");
      System.out.println("WRONG_PW_OPENED  <-- BAD");
    } catch (Exception e) {
      System.out.println("WRONG_PW_REJECTED " + e.getClass().getSimpleName());
    }
    // owner password also opens it
    try (PDDocument d = PDDocument.load(enc, "owner-pass-999")) {
      System.out.println("OWNER_PW_OPENS " + d.getNumberOfPages());
    }
    // needs a password at all?
    System.out.println("NEEDS_PW " + PdfEngine.needsPassword(enc));
    // round-trip: decrypt and confirm the text survived
    File dec = new File(W, "enc_dec.pdf");
    PdfEngine.decrypt(enc, "user-pass-123", dec);
    System.out.println("DEC_OK " + PdfEngine.needsPassword(dec));
  }
}
