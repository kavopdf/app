import com.kavopdf.app.engine.PdfEngine;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import java.io.File;
import java.util.*;

/**
 * Two things this proves:
 *  1. A PDF whose document properties live ONLY in the XMP packet still reports them,
 *     instead of showing an empty metadata screen.
 *  2. The URL detector finds second-level domains used in India (nic.in, co.in) which
 *     the old pattern split into words.
 */
public class TestMeta {
    public static void main(String[] a) throws Exception {
        File dir = new File(System.getProperty("java.io.tmpdir"), "kavopdf-meta");
        dir.mkdirs();
        int fail = 0;

        // ---- 1. XMP only ----
        File xmpOnly = new File(dir, "xmp_only.pdf");
        String xmp = "<?xpacket begin=\"\" id=\"W5M0MpCehiHzreSzNTczkc9d\"?>\n"
            + "<x:xmpmeta xmlns:x=\"adobe:ns:meta/\"><rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
            + "<rdf:Description rdf:about=\"\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
            + "xmlns:xmp=\"http://ns.adobe.com/xap/1.0/\" xmlns:pdf=\"http://ns.adobe.com/pdf/1.3/\">"
            + "<dc:title><rdf:Alt><rdf:li xml:lang=\"x-default\">Annual Report 2026</rdf:li></rdf:Alt></dc:title>"
            + "<dc:creator><rdf:Seq><rdf:li>SALUTATION NAME</rdf:li></rdf:Seq></dc:creator>"
            + "<pdf:Producer>Acme Writer 4.1</pdf:Producer>"
            + "<xmp:CreatorTool>Acme Writer</xmp:CreatorTool>"
            + "<xmp:CreateDate>2026-03-04T09:15:00+05:30</xmp:CreateDate>"
            + "</rdf:Description></rdf:RDF></x:xmpmeta><?xpacket end=\"w\"?>";
        try (PDDocument d = new PDDocument()) {
            d.addPage(new PDPage(PDRectangle.A4));
            PDMetadata md = new PDMetadata(d);
            md.importXMPMetadata(xmp.getBytes("UTF-8"));
            d.getDocumentCatalog().setMetadata(md);
            d.save(xmpOnly);            // Info dictionary left completely empty
        }
        Map<String, String> m = PdfEngine.getMetadata(xmpOnly);
        System.out.println("XMP-only PDF:");
        for (String k : new String[]{"title","author","producer","creator","creationDate"}) {
            System.out.println("   " + k + " = " + m.get(k));
        }
        if (!"Annual Report 2026".equals(m.get("title"))) { System.out.println("   FAIL title"); fail++; }
        if (!"SALUTATION NAME".equals(m.get("author"))) { System.out.println("   FAIL author"); fail++; }
        if (!"Acme Writer 4.1".equals(m.get("producer"))) { System.out.println("   FAIL producer"); fail++; }
        if (!"2026-03-04 09:15".equals(m.get("creationDate"))) { System.out.println("   FAIL date"); fail++; }
        if (fail == 0) System.out.println("   PASS - XMP is read when Info is empty");

        // ---- 2. Info wins over XMP when both exist ----
        File both = new File(dir, "both.pdf");
        try (PDDocument d = PDDocument.load(xmpOnly)) {
            PDDocumentInformation info = d.getDocumentInformation();
            info.setTitle("Info Title Wins");
            d.save(both);
        }
        Map<String, String> m2 = PdfEngine.getMetadata(both);
        System.out.println("Both present: title = " + m2.get("title"));
        if (!"Info Title Wins".equals(m2.get("title"))) { System.out.println("   FAIL precedence"); fail++; }
        else System.out.println("   PASS - Info dictionary wins, XMP only fills the gaps");

        // ---- 3. link detector: Indian second-level domains ----
        File links = new File(dir, "links.pdf");
        try (PDDocument d = new PDDocument()) {
            PDPage p = new PDPage(PDRectangle.A4);
            d.addPage(p);
            try (PDPageContentStream cs = new PDPageContentStream(d, p)) {
                cs.beginText();
                cs.setFont(com.tom_roush.pdfbox.pdmodel.font.PDType1Font.HELVETICA, 11);
                cs.newLineAtOffset(50, 700);
                cs.showText("Visit https://www.nic.in today");
                cs.newLineAtOffset(0, -20);
                cs.showText("or write to help@example.co.in");
                cs.newLineAtOffset(0, -20);
                cs.showText("and see oursite.co.in/page for details");
                cs.endText();
            }
            d.save(links);
        }
        List<PdfEngine.FoundLink> found = PdfEngine.findLinks(links);
        System.out.println("Links found: " + found.size());
        for (PdfEngine.FoundLink l : found) System.out.println("   " + l.url);
        boolean hasNic = false, hasEmail = false, hasCoIn = false;
        for (PdfEngine.FoundLink l : found) {
            if (l.url.contains("nic.in")) hasNic = true;
            if (l.url.contains("help@example.co.in")) hasEmail = true;
            if (l.url.contains("oursite.co.in")) hasCoIn = true;
        }
        if (!hasNic) { System.out.println("   FAIL nic.in"); fail++; }
        if (!hasEmail) { System.out.println("   FAIL email"); fail++; }
        if (!hasCoIn) { System.out.println("   FAIL co.in domain"); fail++; }
        if (hasNic && hasEmail && hasCoIn) System.out.println("   PASS - .in / .co.in / e-mail all found");

        System.out.println(fail == 0 ? "\nMETA: PASS" : "\nMETA: " + fail + " FAILED");
        if (fail != 0) System.exit(1);
    }
}
