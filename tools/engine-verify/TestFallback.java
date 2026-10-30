import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import com.tom_roush.pdfbox.pdmodel.interactive.annotation.*;
import com.tom_roush.pdfbox.pdmodel.interactive.form.*;
import java.io.File;
import java.util.*;

/**
 * Builds its own two-field form, so this runs anywhere - no sample PDF needed.
 * Strips every widget appearance first, which is the situation a viewer shows as an
 * empty form even though the values are in the file, then checks that fillForm still
 * makes them visible.
 */
public class TestFallback {
    /** A writable directory that exists on any machine, including CI. */
    static File tmp() {
        File d = new File(System.getProperty("java.io.tmpdir"), "kavopdf-test");
        d.mkdirs();
        return d;
    }

    public static void main(String[] a) throws Exception {
        File src = new File(tmp(), "fb_src.pdf");
        try (PDDocument d = new PDDocument()) {
            PDPage page = new PDPage(PDRectangle.A4);
            d.addPage(page);
            PDAcroForm form = new PDAcroForm(d);
            d.getDocumentCatalog().setAcroForm(form);
            form.setDefaultResources(new PDResources());
            form.setDefaultAppearance("/Helv 10 Tf 0 g");
            List<PDField> fields = new ArrayList<>();
            for (int i = 0; i < 2; i++) {
                PDTextField tf = new PDTextField(form);
                tf.setPartialName("field" + i);
                PDAnnotationWidget w = tf.getWidgets().get(0);
                w.setRectangle(new PDRectangle(80, 700 - i * 40, 300, 22));
                w.setPage(page);
                page.getAnnotations().add(w);
                fields.add(tf);
            }
            form.setFields(fields);
            d.save(src);
        }

        // strip every appearance: now nothing is drawn until we fill it
        try (PDDocument d = PDDocument.load(src)) {
            for (PDField f : d.getDocumentCatalog().getAcroForm().getFields())
                for (PDAnnotationWidget w : f.getWidgets()) w.setAppearance(null);
            d.save(src);
        }

        Map<String, String> vals = new LinkedHashMap<>();
        vals.put("field0", "MARKER-A");
        vals.put("field1", "MARKER-B");
        File out = new File(tmp(), "fb_out.pdf");
        PdfEngine.fillForm(src, vals, out);

        StringBuilder all = new StringBuilder();
        try (PDDocument d = PDDocument.load(out)) {
            for (int i = 0; i < d.getNumberOfPages(); i++) {
                PDPage p = d.getPage(i);
                java.io.InputStream in = p.getContents();
                java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
                byte[] b = new byte[8192]; int n;
                while ((n = in.read(b)) > 0) bo.write(b, 0, n);
                all.append(new String(bo.toByteArray(), "ISO-8859-1"));
                for (PDAnnotation an : p.getAnnotations()) {
                    if (an.getAppearance() != null && an.getAppearance().getNormalAppearance() != null) {
                        PDAppearanceStream as = an.getAppearance().getNormalAppearance().getAppearanceStream();
                        if (as != null) all.append(new String(as.getStream().toByteArray(), "ISO-8859-1"));
                    }
                }
            }
        }
        String hay = all.toString();
        int found = 0;
        for (String v : vals.values()) if (hay.contains(v)) found++;
        System.out.println("  values visible after stripping every appearance: " + found + " / " + vals.size());
        System.out.println(found == vals.size() ? "FALLBACK: PASS" : "FALLBACK: FAIL");
        if (found != vals.size()) System.exit(1);
    }
}
