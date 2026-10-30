import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.interactive.annotation.*;
import com.tom_roush.pdfbox.pdmodel.interactive.form.*;
import java.io.File;
import java.util.*;

/**
 * Android's PdfRenderer - the one KavoPDF reads with - draws page CONTENT only and
 * ignores annotations. A form value lives in an annotation appearance, so the app's own
 * reader shows an empty form while Google Drive (which does draw annotations) shows the
 * value. This test proves the value is missing from the page content, then proves that
 * flattening puts it there.
 */
public class TestFlatten {
    public static void main(String[] a) throws Exception {
        File dir = new File(System.getProperty("java.io.tmpdir"), "kavopdf-flat");
        dir.mkdirs();
        File src = new File(dir, "flat_src.pdf");

        try (PDDocument d = new PDDocument()) {
            PDPage page = new PDPage(PDRectangle.A4);
            d.addPage(page);
            PDAcroForm form = new PDAcroForm(d);
            d.getDocumentCatalog().setAcroForm(form);
            form.setDefaultResources(new PDResources());
            form.setDefaultAppearance("/Helv 10 Tf 0 g");
            PDTextField tf = new PDTextField(form);
            tf.setPartialName("branch");
            PDAnnotationWidget w = tf.getWidgets().get(0);
            w.setRectangle(new PDRectangle(80, 700, 300, 22));
            w.setPage(page);
            page.getAnnotations().add(w);
            form.setFields(Collections.singletonList((PDField) tf));
            d.save(src);
        }

        Map<String, String> vals = new LinkedHashMap<>();
        vals.put("branch", "jalalpur");

        // ---- 1. exactly what the app does today ----
        File filled = new File(dir, "flat_filled.pdf");
        PdfEngine.fillForm(src, vals, filled);
        System.out.println("after fillForm (what ships today):");
        System.out.println("  value in PAGE CONTENT  : " + inPageContent(filled, "jalalpur")
                + "   <- Android PdfRenderer only reads this");
        System.out.println("  value in ANNOTATION    : " + inAppearance(filled, "jalalpur")
                + "   <- Google Drive reads this");

        // ---- 2. now flatten the same file ----
        File flat = new File(dir, "flat_out.pdf");
        try (PDDocument d = PDDocument.load(filled)) {
            d.getDocumentCatalog().getAcroForm().flatten();
            d.save(flat);
        }
        System.out.println("\nafter flatten():");
        System.out.println("  value in PAGE CONTENT  : " + inPageContent(flat, "jalalpur"));
        System.out.println("  value in ANNOTATION    : " + inAppearance(flat, "jalalpur"));

        boolean pass = inPageContent(flat, "jalalpur");
        System.out.println("\n" + (pass ? "FLATTEN: PASS - the value is in the page content now"
                                         : "FLATTEN: FAIL"));
        if (!pass) System.exit(1);
    }

    static String pageText(File f) throws Exception {
        StringBuilder sb = new StringBuilder();
        try (PDDocument d = PDDocument.load(f)) {
            for (int i = 0; i < d.getNumberOfPages(); i++) {
                java.io.InputStream in = d.getPage(i).getContents();
                java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
                byte[] b = new byte[8192]; int n;
                while ((n = in.read(b)) > 0) bo.write(b, 0, n);
                sb.append(new String(bo.toByteArray(), "ISO-8859-1"));
            }
        }
        return sb.toString();
    }

    static String appearanceText(File f) throws Exception {
        StringBuilder sb = new StringBuilder();
        try (PDDocument d = PDDocument.load(f)) {
            for (int i = 0; i < d.getNumberOfPages(); i++) {
                for (PDAnnotation an : d.getPage(i).getAnnotations()) {
                    if (an.getAppearance() != null && an.getAppearance().getNormalAppearance() != null) {
                        PDAppearanceStream as = an.getAppearance().getNormalAppearance().getAppearanceStream();
                        if (as != null) sb.append(new String(as.getStream().toByteArray(), "ISO-8859-1"));
                    }
                }
            }
        }
        return sb.toString();
    }

    static boolean inPageContent(File f, String v) throws Exception {
        return pageText(f).contains(v);
    }

    static boolean inAppearance(File f, String v) throws Exception {
        return appearanceText(f).contains(v);
    }
}
