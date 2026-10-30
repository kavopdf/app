import com.kavopdf.app.engine.PdfEngine;
import com.kavopdf.app.engine.PdfSigner;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import com.tom_roush.pdfbox.pdmodel.graphics.image.PDImageXObject;
import com.tom_roush.pdfbox.pdmodel.interactive.form.*;
import com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotationWidget;
import com.tom_roush.pdfbox.text.PDFTextStripper;

import java.io.File;
import java.util.*;

public class TestEngine {
  static int pass = 0, fail = 0;
  static File W = new File(System.getProperty("java.io.tmpdir"), "kavopdf-engine-test");

  static void check(String name, boolean ok) {
    if (ok) { pass++; System.out.println("  PASS  " + name); }
    else { fail++; System.out.println("  FAIL  " + name); }
  }

  static File makePdf(String name, int pages, boolean withImage) throws Exception {
    PDDocument d = new PDDocument();
    for (int i = 1; i <= pages; i++) {
      PDPage p = new PDPage(PDRectangle.A4);
      d.addPage(p);
      try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
        cs.beginText();
        cs.setFont(PDType1Font.HELVETICA, 20);
        cs.newLineAtOffset(72, 700);
        cs.showText("PAGE_" + i + "_MARKER");
        cs.endText();
        if (withImage && i == 1) {
          PDImageXObject img = PDImageXObject.createFromFile(new File(W, "red.png").getAbsolutePath(), d);
          cs.drawImage(img, 72, 400, 200, 150);
        }
      }
    }
    File f = new File(W, name);
    d.save(f);
    d.close();
    return f;
  }

  static String textOf(File f, int page) throws Exception {
    try (PDDocument d = PDDocument.load(f)) {
      PDFTextStripper s = new PDFTextStripper();
      s.setStartPage(page); s.setEndPage(page);
      return s.getText(d);
    }
  }

  static int rotationOf(File f, int page) throws Exception {
    try (PDDocument d = PDDocument.load(f)) { return d.getPage(page - 1).getRotation(); }
  }

  public static void main(String[] args) throws Exception {
    W.mkdirs();
    // test images
    if (!new File(W, "red.png").exists()) {
      java.awt.image.BufferedImage bi = new java.awt.image.BufferedImage(600, 400, java.awt.image.BufferedImage.TYPE_INT_RGB);
      java.awt.Graphics2D g = bi.createGraphics(); g.setColor(java.awt.Color.RED); g.fillRect(0, 0, 600, 400); g.dispose();
      javax.imageio.ImageIO.write(bi, "png", new File(W, "red.png"));
    }
    if (!new File(W, "sig.png").exists()) {
      java.awt.image.BufferedImage bi = new java.awt.image.BufferedImage(400, 200, java.awt.image.BufferedImage.TYPE_INT_ARGB);
      java.awt.Graphics2D g = bi.createGraphics(); g.setColor(java.awt.Color.BLUE); g.drawLine(10, 100, 380, 100); g.dispose();
      javax.imageio.ImageIO.write(bi, "png", new File(W, "sig.png"));
    }

    File a = makePdf("a.pdf", 3, true);
    File b = makePdf("b.pdf", 2, false);

    System.out.println("== info ==");
    check("pageCount(a)=3", PdfEngine.pageCount(a) == 3);
    check("isEncrypted(a)=false", !PdfEngine.isEncrypted(a));

    System.out.println("== merge ==");
    File merged = new File(W, "merged.pdf");
    PdfEngine.merge(Arrays.asList(a, b), merged);
    check("merged pages=5", PdfEngine.pageCount(merged) == 5);
    check("merged page1 has marker", textOf(merged, 1).contains("PAGE_1_MARKER"));

    System.out.println("== keep/remove/reorder ==");
    File kept = new File(W, "kept.pdf");
    PdfEngine.keepPages(a, Arrays.asList(3, 1), kept);
    check("kept pages=2", PdfEngine.pageCount(kept) == 2);
    check("kept order 3 then 1", textOf(kept, 1).contains("PAGE_3_MARKER") && textOf(kept, 2).contains("PAGE_1_MARKER"));
    File rem = new File(W, "rem.pdf");
    PdfEngine.removePages(a, Arrays.asList(2), rem);
    check("removed pages=2", PdfEngine.pageCount(rem) == 2);
    check("page2 gone", !textOf(rem, 2).contains("PAGE_2_MARKER"));
    File reo = new File(W, "reo.pdf");
    PdfEngine.reorderPages(a, Arrays.asList(2, 3, 1), reo);
    check("reorder ok", textOf(reo, 1).contains("PAGE_2_MARKER") && textOf(reo, 3).contains("PAGE_1_MARKER"));

    System.out.println("== rebuild ==");
    File rb = new File(W, "rb.pdf");
    PdfEngine.rebuild(a, Arrays.asList(3, 1, 2), Arrays.asList(0, 0, 0), rb);
    check("rebuild pages=3", PdfEngine.pageCount(rb) == 3);
    check("rebuild order 3,1,2", textOf(rb, 1).contains("PAGE_3_MARKER") && textOf(rb, 3).contains("PAGE_2_MARKER"));
    File rb2 = new File(W, "rb2.pdf");
    PdfEngine.rebuild(a, Arrays.asList(1, 2, 3), Arrays.asList(90, 0, 180), rb2);
    check("rebuild rotation p1=90", rotationOf(rb2, 1) == 90);
    check("rebuild rotation p3=180", rotationOf(rb2, 3) == 180);

    System.out.println("== rotate ==");
    File rot = new File(W, "rot.pdf");
    PdfEngine.rotatePages(a, Arrays.asList(1), 90, rot);
    check("page1 rotation=90", rotationOf(rot, 1) == 90);
    check("page2 rotation=0", rotationOf(rot, 2) == 0);

    System.out.println("== split ==");
    File spDir = new File(W, "split"); spDir.mkdirs();
    List<File> parts = PdfEngine.splitToFiles(a, Arrays.asList(new int[]{1, 2}, new int[]{3, 3}), spDir, "doc");
    check("split made 2 parts", parts.size() == 2);
    check("part1 pages=2", PdfEngine.pageCount(parts.get(0)) == 2);
    check("part2 pages=1", PdfEngine.pageCount(parts.get(1)) == 1);

    System.out.println("== text & image content ==");
    File txt = new File(W, "txt.pdf");
    PdfEngine.addText(a, 1, "HELLO_STAMP", 100, 100, 18, 0xFFFF0000, txt);
    check("addText present", textOf(txt, 1).contains("HELLO_STAMP"));
    File stamp = new File(W, "stamp.pdf");
    PdfEngine.applyStamps(a,
        Arrays.asList(new PdfEngine.TextStamp(2, 80, 200, 14, 0xFF000000, "STAMP_TEXT")),
        Arrays.asList(new PdfEngine.ImageStamp(1, 200, 300, 150, 100, new File(W, "sig.png"))),
        Arrays.asList(new PdfEngine.HighlightStamp(3, 70, 690, 300, 25, 0xFFFFFF00)),
        stamp);
    check("applyStamps text", textOf(stamp, 2).contains("STAMP_TEXT"));
    check("applyStamps valid", PdfEngine.pageCount(stamp) == 3);

    System.out.println("== watermark / page numbers ==");
    File wm = new File(W, "wm.pdf");
    PdfEngine.watermarkText(a, "CONFIDENTIAL", 48, 0.3f, 0xFFFF0000, 45, wm);
    check("watermark text present", textOf(wm, 1).replaceAll("\\s+", "").contains("CONFIDENTIAL"));
    File wmi = new File(W, "wmi.pdf");
    PdfEngine.watermarkImage(a, new File(W, "sig.png"), 0.25f, 0.6f, wmi);
    check("watermark image valid", PdfEngine.pageCount(wmi) == 3);
    File pn = new File(W, "pn.pdf");
    PdfEngine.addPageNumbers(a, "Page {n} of {total}", 10, 0xFF333333, pn);
    check("page number present", textOf(pn, 2).contains("Page 2 of 3"));

    System.out.println("== security ==");
    File enc = new File(W, "enc.pdf");
    PdfEngine.encrypt(a, "secret", "owner", enc);
    check("encrypted opens with pw", PdfEngine.pageCount(enc, "secret") == 3);
    boolean blocked = false;
    try { PdfEngine.pageCount(enc); } catch (Exception e) { blocked = true; }
    check("encrypted blocked without pw", blocked);
    File dec = new File(W, "dec.pdf");
    PdfEngine.decrypt(enc, "secret", dec);
    check("decrypted opens freely", PdfEngine.pageCount(dec) == 3);
    check("decrypted not encrypted", !PdfEngine.isEncrypted(dec));

    System.out.println("== compress ==");
    // Build an image-heavy PDF from a large photo and confirm real size reduction.
    File bigImg = new File(W, "big.jpg");
    if (!bigImg.exists()) {
      java.awt.image.BufferedImage bi = new java.awt.image.BufferedImage(2400, 1800, java.awt.image.BufferedImage.TYPE_INT_RGB);
      java.awt.Graphics2D g = bi.createGraphics();
      for (int y = 0; y < 1800; y += 8) { g.setColor(new java.awt.Color((y * 7) % 255, (y * 3) % 255, (y * 11) % 255)); g.fillRect(0, y, 2400, 8); }
      g.dispose();
      javax.imageio.ImageIO.write(bi, "jpg", bigImg);
    }
    File big = new File(W, "big.pdf");
    PdfEngine.imagesToPdf(Arrays.asList(bigImg), big);
    File cmp = new File(W, "cmp.pdf");
    PdfEngine.compress(big, cmp);
    check("compress valid", PdfEngine.pageCount(cmp) == 1);
    check("compress actually shrinks a big image PDF", cmp.length() < big.length());
    System.out.println("     size " + big.length() + " -> " + cmp.length());

    System.out.println("== metadata ==");
    File meta = new File(W, "meta.pdf");
    PdfEngine.MetadataInfo basic = new PdfEngine.MetadataInfo();
    basic.title = "My Title"; basic.author = "Author X"; basic.subject = "Subject Y";
    basic.keywords = "kw1 kw2"; basic.creator = "KavoPDF";
    PdfEngine.setMetadata(a, basic, meta);
    Map<String, String> m = PdfEngine.getMetadata(meta);
    check("title set", "My Title".equals(m.get("title")));
    check("author set", "Author X".equals(m.get("author")));

    System.out.println("== images -> pdf ==");
    File ipdf = new File(W, "ipdf.pdf");
    PdfEngine.imagesToPdf(Arrays.asList(new File(W, "red.png"), new File(W, "sig.png")), ipdf);
    check("imagesToPdf pages=2", PdfEngine.pageCount(ipdf) == 2);

    System.out.println("== extract images ==");
    File exDir = new File(W, "extract"); exDir.mkdirs();
    List<File> ex = PdfEngine.extractImages(a, exDir);
    check("extracted >=1 image", ex.size() >= 1);
    check("extracted file exists", ex.get(0).exists() && ex.get(0).length() > 0);
    java.awt.image.BufferedImage back = javax.imageio.ImageIO.read(ex.get(0));
    check("extracted image decodes", back != null && back.getWidth() > 0);

    System.out.println("== forms ==");
    File form = makeForm();
    List<PdfEngine.FormField> fields = PdfEngine.listFormFields(form);
    check("form has 1 field", fields.size() == 1);
    check("field name", fields.size() == 1 && "name".equals(fields.get(0).name));
    File filled = new File(W, "filled.pdf");
    Map<String, String> vals = new HashMap<>(); vals.put("name", "Ravi Kumar");
    PdfEngine.fillForm(form, vals, filled);
    List<PdfEngine.FormField> after = PdfEngine.listFormFields(filled);
    check("form value set", after.size() == 1 && "Ravi Kumar".equals(after.get(0).value));


    System.out.println("== unlock variants ==");
    File encOwner = new File(W, "encOwner.pdf");
    PdfEngine.encrypt(a, "", "ownersecret", encOwner);
    check("owner-only file is encrypted", PdfEngine.isEncrypted(encOwner));
    check("owner-only needs no password", !PdfEngine.needsPassword(encOwner));
    File decOwner = new File(W, "decOwner.pdf");
    PdfEngine.decrypt(encOwner, "", decOwner);
    check("owner-only unlock works", PdfEngine.pageCount(decOwner) == 3);
    check("owner-only unlock removed protection", !PdfEngine.isEncrypted(decOwner));

    File encUser = new File(W, "encUser.pdf");
    PdfEngine.encrypt(a, "userpw", "ownerpw", encUser);
    check("user-password file needs password", PdfEngine.needsPassword(encUser));
    File decUser = new File(W, "decUser.pdf");
    PdfEngine.decrypt(encUser, "userpw", decUser);
    check("user-password unlock works", PdfEngine.pageCount(decUser) == 3);

    System.out.println("== watermark options ==");
    PdfEngine.WatermarkOptions wo = new PdfEngine.WatermarkOptions();
    wo.text = "SAMPLE"; wo.randomPosition = true; wo.font = "Times"; wo.bold = true;
    wo.color = 0xFF008000; wo.opacity = 0.3f; wo.angle = 0f; wo.fontSize = 36f;
    File wm2 = new File(W, "wm2.pdf");
    PdfEngine.watermarkText(a, wo, wm2);
    check("watermark(random, Times) valid", PdfEngine.pageCount(wm2) == 3);
    boolean every = true;
    for (int i = 1; i <= 3; i++) if (!textOf(wm2, i).replaceAll("\\s+","").contains("SAMPLE")) every = false;
    check("watermark(random) on every page", every);
    PdfEngine.WatermarkOptions wo2 = new PdfEngine.WatermarkOptions();
    wo2.text = "COURIER"; wo2.font = "Courier"; wo2.italic = true; wo2.bold = false; wo2.angle = 0f;
    File wm3 = new File(W, "wm3.pdf");
    PdfEngine.watermarkText(a, wo2, wm3);
    check("watermark(courier italic) valid", PdfEngine.pageCount(wm3) == 3);
    check("watermark(courier) present", textOf(wm3, 1).replaceAll("\\s+","").contains("COURIER"));

    System.out.println("== multi-image pdf ==");
    File m1 = new File(W, "mi1.jpg"), m2 = new File(W, "mi2.png"), m3 = new File(W, "mi3.jpg");
    if (!m1.exists()) { writeImg(m1, 1600, 1200, "jpg"); writeImg(m2, 900, 1400, "png"); writeImg(m3, 2000, 1500, "jpg"); }
    File mipdf = new File(W, "mipdf.pdf");
    PdfEngine.imagesToPdf(Arrays.asList(m1, m2, m3), mipdf);
    check("multi-image pages=3", PdfEngine.pageCount(mipdf) == 3);
    check("multi-image has 3 embedded images", countImages(mipdf) >= 3);

    System.out.println("== strong compress ==");
    File scanDir = new File(W, "scan"); scanDir.mkdirs();
    List<File> scans = new ArrayList<>();
    for (int i = 0; i < 6; i++) {
      File sf = new File(scanDir, "scan" + i + ".jpg");
      if (!sf.exists()) writePhoto(sf, 3000, 2250, i);
      scans.add(sf);
    }
    File bigScan = new File(W, "bigScan.pdf");
    PdfEngine.imagesToPdf(scans, bigScan, 0, true);
    File smallScan = new File(W, "smallScan.pdf");
    PdfEngine.compress(bigScan, smallScan, 2);
    check("strong compress valid", PdfEngine.pageCount(smallScan) == 6);
    double ratio = smallScan.length() / (double) bigScan.length();
    System.out.println("     scan " + bigScan.length() + " -> " + smallScan.length() + " (" + Math.round(ratio * 100) + "%)");
    check("strong compress >50% smaller", ratio < 0.5);


    System.out.println("== metadata extras ==");
    PdfEngine.MetadataInfo mi = new PdfEngine.MetadataInfo();
    mi.title = "T"; mi.author = "A"; mi.subject = "S"; mi.keywords = "k1 k2";
    mi.creator = "KavoPDF"; mi.producer = "KavoPDF 1.2";
    mi.creationDate = "2026-01-02 03:04"; mi.modDate = "2026-05-06 07:08";
    File metaX = new File(W, "meta2.pdf");
    PdfEngine.setMetadata(a, mi, metaX);
    Map<String, String> mm = PdfEngine.getMetadata(metaX);
    check("meta creator", "KavoPDF".equals(mm.get("creator")));
    check("meta producer", "KavoPDF 1.2".equals(mm.get("producer")));
    check("meta creationDate", "2026-01-02 03:04".equals(mm.get("creationDate")));
    check("meta modDate", "2026-05-06 07:08".equals(mm.get("modDate")));
    File metaY = new File(W, "meta3.pdf");
    PdfEngine.clearMetadata(metaX, metaY);
    Map<String, String> mc = PdfEngine.getMetadata(metaY);
    check("cleared title", mc.get("title").isEmpty());
    check("cleared author", mc.get("author").isEmpty());

    System.out.println("== create pdf ==");
    File r1 = new File(W, "rast1.png");
    if (!r1.exists()) writeImg(r1, 1190, 1684, "png");
    File created = new File(W, "created.pdf");
    PdfEngine.createPdf(Arrays.asList(
        new PdfEngine.PageSpec(595, 842, 0xFFFFFFFF, r1),
        new PdfEngine.PageSpec(595, 842, 0xFFEFF3FF, null)), created);
    check("createPdf pages=2", PdfEngine.pageCount(created) == 2);
    check("createPdf A4 width", Math.abs(PdfEngine.pageSizes(created).get(0)[0] - 595f) < 1f);

    System.out.println("== digital signature ==");
    PdfSigner.SignParams sp = new PdfSigner.SignParams();
    sp.name = "Ravi Kumar"; sp.organisation = "Acme"; sp.reason = "Approved";
    sp.location = "Delhi"; sp.contact = "ravi@example.com";
    File signed = new File(W, "signed.pdf");
    PdfSigner.sign(a, signed, sp);
    check("signed file created", signed.exists() && signed.length() > 0);
    List<PdfSigner.SignatureInfo> vs = PdfSigner.verify(signed);
    check("one signature found", vs.size() == 1);
    if (!vs.isEmpty()) {
      PdfSigner.SignatureInfo si = vs.get(0);
      check("signature cryptographically valid", si.valid);
      check("signature covers whole document", si.coversWholeDocument);
      check("signer name preserved", "Ravi Kumar".equals(si.signerName));
      check("cert subject CN", si.subject.contains("CN=Ravi Kumar"));
      check("cert subject O", si.subject.contains("O=Acme"));
      check("reason preserved", "Approved".equals(si.reason));
      check("location preserved", "Delhi".equals(si.location));
    }
    check("unsigned doc reports no signatures", PdfSigner.verify(a).isEmpty());

    // tamper: change the document after signing -> must fail verification
    File tampered = new File(W, "tampered.pdf");
    try (PDDocument td = PDDocument.load(signed)) {
      td.getDocumentInformation().setTitle("TAMPERED");
      td.save(tampered);
    }
    boolean tamperCaught;
    try {
      List<PdfSigner.SignatureInfo> vt = PdfSigner.verify(tampered);
      tamperCaught = vt.isEmpty() || !vt.get(0).valid || !vt.get(0).coversWholeDocument;
    } catch (Exception e) { tamperCaught = true; }
    check("tampered document fails verification", tamperCaught);


    System.out.println("== crop ==");
    File cropOut = new File(W, "cropout.pdf");
    PdfEngine.cropPages(a, 1, 10f, 20f, 300f, 400f, false, cropOut);
    float[] cs = PdfEngine.pageDisplaySizes(cropOut).get(0);
    check("crop page1 to 300x400", Math.abs(cs[0] - 300f) < 2f && Math.abs(cs[1] - 400f) < 2f);
    check("crop keeps page count", PdfEngine.pageCount(cropOut) == 3);
    float[] cs2 = PdfEngine.pageDisplaySizes(cropOut).get(1);
    check("crop leaves other pages", Math.abs(cs2[0] - 595f) < 3f);
    File cropAll = new File(W, "cropall.pdf");
    PdfEngine.cropPages(a, 1, 0f, 0f, 500f, 700f, true, cropAll);
    check("crop all pages", PdfEngine.pageDisplaySizes(cropAll).get(2)[0] < 510f);

    System.out.println("== extract images by range ==");
    File exRangeDir = new File(W, "exrange");
    exRangeDir.mkdirs();
    List<File> exAll = PdfEngine.extractImages(a, exRangeDir);
    List<File> exOne = PdfEngine.extractImages(a, exRangeDir, Arrays.asList(1));
    check("extract all images", exAll.size() >= 1);
    check("extract one page <= all", exOne.size() <= exAll.size());

    System.out.println("== page numbers with opacity ==");
    File pnOpaque = new File(W, "pnopaque.pdf");
    PdfEngine.addPageNumbers(a, "P{n}", 10f, 0xFF333333, 0.4f, pnOpaque);
    check("page numbers with opacity valid", PdfEngine.pageCount(pnOpaque) == 3);
    check("page number text present", textOf(pnOpaque, 1).replaceAll("\\s+", "").contains("P1"));

    System.out.println();
    System.out.println("TOTAL: " + pass + " passed, " + fail + " failed");
    if (fail > 0) System.exit(1);
  }

  static void writeImg(File f, int w, int h, String fmt) throws Exception {
    java.awt.image.BufferedImage bi = new java.awt.image.BufferedImage(w, h, java.awt.image.BufferedImage.TYPE_INT_RGB);
    java.awt.Graphics2D g = bi.createGraphics();
    for (int y = 0; y < h; y += 12) { g.setColor(new java.awt.Color((y*5)%255,(y*9)%255,(y*13)%255)); g.fillRect(0, y, w, 12); }
    g.dispose();
    javax.imageio.ImageIO.write(bi, fmt, f);
  }

  static void writePhoto(File f, int w, int h, int seed) throws Exception {
    java.awt.image.BufferedImage bi = new java.awt.image.BufferedImage(w, h, java.awt.image.BufferedImage.TYPE_INT_RGB);
    java.util.Random rnd = new java.util.Random(seed);
    for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) {
      int r = (int)((Math.sin((x+seed*31)/37.0)*0.5+0.5)*200) + rnd.nextInt(40);
      int gg = (int)((Math.cos((y+seed*17)/29.0)*0.5+0.5)*200) + rnd.nextInt(40);
      int b = (int)((Math.sin((x+y)/23.0)*0.5+0.5)*200) + rnd.nextInt(40);
      bi.setRGB(x, y, (Math.min(255,r)<<16)|(Math.min(255,gg)<<8)|Math.min(255,b));
    }
    javax.imageio.ImageIO.write(bi, "jpg", f);
  }

  static int countImages(File f) throws Exception {
    int n = 0;
    try (PDDocument d = PDDocument.load(f)) {
      for (PDPage p : d.getPages()) {
        PDResources res = p.getResources();
        if (res == null) continue;
        for (com.tom_roush.pdfbox.cos.COSName nm : res.getXObjectNames()) {
          if (res.getXObject(nm) instanceof com.tom_roush.pdfbox.pdmodel.graphics.image.PDImageXObject) n++;
        }
      }
    }
    return n;
  }

  static byte[] readBytes(File f) throws Exception {
    return java.nio.file.Files.readAllBytes(f.toPath());
  }
  static void writeBytes(File f, byte[] b) throws Exception {
    java.nio.file.Files.write(f.toPath(), b);
  }

  static File makeForm() throws Exception {
    PDDocument d = new PDDocument();
    PDPage page = new PDPage(PDRectangle.A4);
    d.addPage(page);
    PDAcroForm form = new PDAcroForm(d);
    d.getDocumentCatalog().setAcroForm(form);
    form.setDefaultResources(new PDResources());
    PDTextField f = new PDTextField(form);
    f.setPartialName("name");
    form.getFields().add(f);
    PDAnnotationWidget w = f.getWidgets().get(0);
    w.setPage(page);
    w.setRectangle(new PDRectangle(50, 700, 220, 22));
    page.getAnnotations().add(w);
    File out = new File(W, "form.pdf");
    d.save(out);
    d.close();
    return out;
  }
}
