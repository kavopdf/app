import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.cos.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.security.MessageDigest;
import java.util.*;

/**
 * The image-OCR page path: a JPEG must be embedded as its original bytes (no re-encode),
 * and the EXIF rotation mapping must be right.
 */
public class TestImagePdf {
    static int pass = 0, fail = 0;
    static void check(boolean ok, String what) {
        if (ok) { pass++; System.out.println("  PASS  " + what); }
        else { fail++; System.out.println("  FAIL  " + what); }
    }
    static void eq(Object a, Object b, String what) {
        check(Objects.equals(a, b), what + " (got " + a + ", want " + b + ")");
    }

    public static void main(String[] args) throws Exception {
        File dir = new File(System.getProperty("java.io.tmpdir"), "kavopdf_imgpdf");
        dir.mkdirs();

        // --- a real JPEG on disk, the way a phone photo arrives -------------------------
        File jpeg = new File(dir, "photo.jpg");
        BufferedImage bi = new BufferedImage(900, 1200, BufferedImage.TYPE_INT_RGB);
        java.awt.Graphics2D g = bi.createGraphics();
        g.setColor(java.awt.Color.WHITE); g.fillRect(0, 0, 900, 1200);
        g.setColor(java.awt.Color.BLACK);
        for (int i = 0; i < 40; i++) g.drawString("Line " + i + " invoice 12345", 40, 60 + i * 26);
        g.dispose();
        javax.imageio.ImageIO.write(bi, "jpg", jpeg);
        check(jpeg.length() > 1000, "source JPEG written (" + jpeg.length() + " bytes)");
        String srcHash = sha(jpeg);

        // --- build a two-page PDF through the writer -----------------------------------
        File out = new File(dir, "out.pdf");
        PdfEngine.ImagePdfWriter w = new PdfEngine.ImagePdfWriter(2600, false);
        try {
            w.addPage(jpeg, 900, 1200);
            w.addPage(jpeg, 900, 1200);
            w.finish(out);
        } finally {
            w.close();
        }
        check(out.length() > 0, "PDF written (" + out.length() + " bytes)");

        try (PDDocument d = PDDocument.load(out)) {
            eq(d.getNumberOfPages(), 2, "two pages");
            // 900x1200 px at 72/96 scale = 675 x 900 pt
            PDRectangle box = d.getPage(0).getCropBox();
            eq((long) Math.round(box.getWidth()), 900L, "page width in points (1px = 1pt, as imagesToPdf)");
            eq((long) Math.round(box.getHeight()), 1200L, "page height in points");
        }

        // --- the embedded JPEG must be byte-identical to the file ---------------------
        List<String> hashes = imageHashes(out);
        eq(hashes.size(), 2, "two image streams");
        eq(hashes.get(0), srcHash, "embedded JPEG is byte-identical to the source (no re-encode)");
        eq(hashes.get(1), srcHash, "second page too");

        // --- EXIF mapping -------------------------------------------------------------
        eq(PdfEngine.exifRotationSigned(1), 0, "EXIF normal -> no rotation");
        eq(PdfEngine.exifRotationSigned(3), 180, "EXIF rotate 180 -> 180");
        eq(PdfEngine.exifRotationSigned(6), 90, "EXIF rotate 90 -> +90");
        eq(PdfEngine.exifRotationSigned(8), -90, "EXIF rotate 270 -> -90");
        eq(PdfEngine.exifRotationSigned(0), 0, "EXIF unset -> no rotation");
        eq(PdfEngine.exifRotation(6), 90, "exifRotation(6)");
        eq(PdfEngine.exifRotation(8), 90, "exifRotation(8)");
        eq(PdfEngine.exifRotation(3), 180, "exifRotation(3)");

        // --- rotation: the page carries /Rotate, the JPEG is still untouched ----------
        File rotOut = new File(dir, "rot.pdf");
        PdfEngine.ImagePdfWriter wr = new PdfEngine.ImagePdfWriter(2600, false);
        try {
            wr.addPage(jpeg, 1200, 900, 90);   // recogniser saw the turned picture
            wr.addPage(jpeg, 900, 1200, 180);
            wr.addPage(jpeg, 900, 1200, 0);
            wr.finish(rotOut);
        } finally { wr.close(); }
        try (PDDocument d = PDDocument.load(rotOut)) {
            eq(d.getNumberOfPages(), 3, "three rotated pages");
            eq(d.getPage(0).getRotation(), 90, "page 1 /Rotate is 90");
            eq(d.getPage(1).getRotation(), 180, "page 2 /Rotate is 180");
            eq(d.getPage(2).getRotation(), 0, "page 3 /Rotate is 0");
            // the box stays the unturned picture, so the viewer's /Rotate makes it upright
            eq((long) Math.round(d.getPage(0).getCropBox().getWidth()), 900L, "rotated page box keeps image width");
            eq((long) Math.round(d.getPage(0).getCropBox().getHeight()), 1200L, "rotated page box keeps image height");
        }
        List<String> rotHashes = imageHashes(rotOut);
        eq(rotHashes.size(), 3, "three image streams");
        boolean allSame = true;
        for (String h : rotHashes) if (!h.equals(srcHash)) allSame = false;
        check(allSame, "rotation did not re-encode the JPEG");

        // --- exifDegrees on a file with no EXIF block --------------------------------
        eq(PdfEngine.exifDegrees(jpeg), 0, "exifDegrees on a plain JPEG is 0");

        // --- end to end: writer -> text layer -> search -------------------------------
        File e2e = new File(dir, "e2e.pdf");
        File e2eLayer = new File(dir, "e2e_layer.pdf");
        PdfEngine.ImagePdfWriter we = new PdfEngine.ImagePdfWriter(2600, false);
        try {
            we.addPage(jpeg, 900, 1200);
            we.finish(e2e);
        } finally { we.close(); }
        List<PdfEngine.OcrWord> wl = new ArrayList<>();
        wl.add(new PdfEngine.OcrWord("INVOICE", 40f, 60f, 200f, 30f));
        wl.add(new PdfEngine.OcrWord("12345", 40f, 100f, 150f, 30f));
        PdfEngine.addTextLayer(e2e,
                Collections.singletonList(new PdfEngine.PageText(1, 900, 1200, wl)), e2eLayer);
        List<?> hits = PdfEngine.search(e2eLayer, "INVOICE", false);
        check(hits.size() >= 1, "a word written onto an image page is searchable");
        check(PdfEngine.search(e2eLayer, "12345", false).size() >= 1, "and so is the number");
        check(!imageHashes(e2eLayer).isEmpty() &&
              imageHashes(e2eLayer).get(0).equals(srcHash),
              "adding the text layer left the embedded JPEG byte-identical");

        // --- imagesToPdf (Images -> PDF, Scan -> PDF) must also be lossless -----------
        File i2p = new File(dir, "i2p.pdf");
        PdfEngine.imagesToPdf(Collections.singletonList(jpeg), i2p, 3000, false);
        List<String> i2pHashes = imageHashes(i2p);
        eq(i2pHashes.size(), 1, "imagesToPdf wrote one image");
        eq(i2pHashes.get(0), srcHash, "Images-to-PDF embeds the JPEG's own bytes (no re-encode)");

        File i2pA4 = new File(dir, "i2p_a4.pdf");
        PdfEngine.imagesToPdf(Collections.singletonList(jpeg), i2pA4, 3000, true);
        eq(imageHashes(i2pA4).get(0), srcHash, "fit-to-A4 path is lossless too");
        try (PDDocument d = PDDocument.load(i2pA4)) {
            PDRectangle b = d.getPage(0).getCropBox();
            eq((long) Math.round(b.getWidth()), 595L, "A4 width");
            eq((long) Math.round(b.getHeight()), 842L, "A4 height");
        }

        // --- extract images must hand back the original bytes ------------------------
        File exDir = new File(dir, "extracted");
        exDir.mkdirs();
        for (File old : exDir.listFiles() == null ? new File[0] : exDir.listFiles()) old.delete();
        java.util.List<File> got = PdfEngine.extractImages(i2p, exDir);
        eq(got.size(), 1, "one image extracted");
        eq(got.get(0).getName().endsWith(".jpg") ? ".jpg" : got.get(0).getName(),
                ".jpg", "a plain JPEG is extracted as .jpg");
        eq(sha(got.get(0)), srcHash, "the extracted image is byte-identical to the original (no re-encode)");

        // --- a corrupt file must throw, not produce a broken page ---------------------
        File junk = new File(dir, "junk.bin");
        try (FileOutputStream fo = new FileOutputStream(junk)) { fo.write(new byte[]{1,2,3,4,5}); }
        boolean threw = false;
        PdfEngine.ImagePdfWriter w2 = new PdfEngine.ImagePdfWriter(2600, false);
        try {
            try { w2.addPage(junk, 100, 100); } catch (Exception e) { threw = true; }
        } finally { w2.close(); }
        check(threw, "a corrupt image is rejected instead of written as a broken page");

        // --- no size given: it comes from the picture, so nothing is decoded ---------
        File auto = new File(dir, "auto.pdf");
        PdfEngine.ImagePdfWriter w3 = new PdfEngine.ImagePdfWriter(2600, false);
        try {
            w3.addPage(jpeg, 0, 0);
            w3.finish(auto);
        } finally { w3.close(); }
        try (PDDocument d = PDDocument.load(auto)) {
            eq((long) Math.round(d.getPage(0).getCropBox().getWidth()), 900L, "size taken from the image");
            eq((long) Math.round(d.getPage(0).getCropBox().getHeight()), 1200L, "and the height too");
        }
        eq(imageHashes(auto).get(0), srcHash, "still byte-identical with no size given");

        // --- a file that is not an image at all is still rejected -------------------
        File notImage = new File(dir, "notes.txt");
        try (FileOutputStream fo = new FileOutputStream(notImage)) {
            fo.write("just some text, not a picture".getBytes("UTF-8"));
        }
        boolean refused = false;
        PdfEngine.ImagePdfWriter w4 = new PdfEngine.ImagePdfWriter(2600, false);
        try {
            try { w4.addPage(notImage); } catch (Exception e) { refused = true; }
        } finally { w4.close(); }
        check(refused, "a text file is rejected as an image");

        System.out.println("IMAGEPDF TOTAL: " + pass + " passed, " + fail + " failed");
        if (fail > 0) System.exit(1);
    }

    /** SHA-256 of every image stream's stored bytes, in document order. */
    static List<String> imageHashes(File f) throws Exception {
        List<String> out = new ArrayList<>();
        try (PDDocument d = PDDocument.load(f)) {
            for (COSObject o : d.getDocument().getObjects()) {
                if (!(o.getObject() instanceof COSStream)) continue;
                COSStream s = (COSStream) o.getObject();
                if (!"Image".equals(s.getNameAsString(COSName.SUBTYPE))) continue;
                MessageDigest md = MessageDigest.getInstance("SHA-256");
                try (InputStream in = s.createRawInputStream()) {
                    byte[] b = new byte[8192]; int n;
                    while ((n = in.read(b)) > 0) md.update(b, 0, n);
                }
                StringBuilder sb = new StringBuilder();
                for (byte x : md.digest()) sb.append(String.format("%02x", x));
                out.add(sb.toString());
            }
        }
        return out;
    }

    static String sha(File f) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        try (InputStream in = new FileInputStream(f)) {
            byte[] b = new byte[8192]; int n;
            while ((n = in.read(b)) > 0) md.update(b, 0, n);
        }
        StringBuilder sb = new StringBuilder();
        for (byte x : md.digest()) sb.append(String.format("%02x", x));
        return sb.toString();
    }
}
