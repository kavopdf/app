import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.interactive.annotation.*;
import com.tom_roush.pdfbox.pdmodel.interactive.form.*;
import java.io.File;
import java.util.*;

/**
 * Builds its own two-page form whose field names say nothing about the page - the names
 * are deliberately meaningless ("alpha", "beta"), so only the widget position can place
 * them. That is the general case; the old key parsing ("txt_p3_Address") was one
 * generator's private convention.
 */
public class TestOrder {
    /** A writable directory that exists on any machine, including CI. */
    static File tmp() {
        File d = new File(System.getProperty("java.io.tmpdir"), "kavopdf-test");
        d.mkdirs();
        return d;
    }

    public static void main(String[] a) throws Exception {
        File src = new File(tmp(), "order_src.pdf");
        String[] names = {"alpha", "beta", "gamma", "delta"};
        try (PDDocument d = new PDDocument()) {
            PDAcroForm form = new PDAcroForm(d);
            d.getDocumentCatalog().setAcroForm(form);
            form.setDefaultResources(new PDResources());
            form.setDefaultAppearance("/Helv 10 Tf 0 g");
            List<PDField> fields = new ArrayList<>();
            int k = 0;
            for (int page = 0; page < 2; page++) {
                PDPage p = new PDPage(PDRectangle.A4);
                d.addPage(p);
                for (int row = 0; row < 2; row++) {
                    PDTextField tf = new PDTextField(form);
                    tf.setPartialName(names[k++]);
                    PDAnnotationWidget w = tf.getWidgets().get(0);
                    w.setRectangle(new PDRectangle(80, 700 - row * 60, 300, 22));
                    w.setPage(p);
                    p.getAnnotations().add(w);
                    fields.add(tf);
                }
            }
            form.setFields(fields);
            d.save(src);
        }

        List<PdfEngine.FormField> fs = PdfEngine.listFormFields(src);
        System.out.println("  fields: " + fs.size());
        int withPage = 0;
        for (PdfEngine.FormField f : fs) {
            System.out.printf("    p%d  %s%n", f.page, f.name);
            if (f.page > 0) withPage++;
        }
        boolean ok = fs.size() == 4 && withPage == 4;
        // page 2 fields must not be reported as page 1
        if (ok) {
            for (PdfEngine.FormField f : fs) {
                boolean secondPage = f.name.equals("gamma") || f.name.equals("delta");
                if (secondPage != (f.page == 2)) ok = false;
            }
        }
        System.out.println(ok ? "ORDER: PASS (page comes from the widget, not the name)"
                              : "ORDER: FAIL");
        if (!ok) System.exit(1);
    }
}
