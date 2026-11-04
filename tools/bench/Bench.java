import com.kavopdf.app.engine.*;
import java.io.*;
import java.util.*;
import android.graphics.Bitmap;
import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.rendering.PDFRenderer;

/**
 * Runs the measurable KavoPDF tools once each, on the fixtures make_fixtures.py builds.
 *
 * It decides nothing. Every judgement is made later by score_all.py against an independent
 * library. This class only produces the files and a note of what ran.
 *
 *   java Bench <inDir> <outDir> <TOOL,TOOL,...|ALL>
 *
 * Tools are named exactly as they are in run.tsv and in baseline.json.
 */
public class Bench {

    interface Step { void run() throws Throwable; }

    static File IN, OUT;
    static final StringBuilder LOG = new StringBuilder();
    static final List<String> WANTED = new ArrayList<>();

    static File in(String n) { return new File(IN, n); }
    static File out(String n) { File f = new File(OUT, n); f.getParentFile().mkdirs(); return f; }

    static boolean want(String tool) {
        return WANTED.isEmpty() || WANTED.contains("ALL") || WANTED.contains(tool);
    }

    static void run(String tool, Step s) {
        if (!want(tool)) { return; }
        long t0 = System.nanoTime();
        try {
            s.run();
            long ms = (System.nanoTime() - t0) / 1_000_000;
            LOG.append(tool).append('\t').append("ok").append('\t').append(ms).append('\n');
            System.out.println("  " + tool + ": ok  " + ms + " ms");
        } catch (Throwable t) {
            long ms = (System.nanoTime() - t0) / 1_000_000;
            String msg = t.toString().replace('\n', ' ');
            if (msg.length() > 160) msg = msg.substring(0, 160);
            LOG.append(tool).append('\t').append("FAIL").append('\t').append(ms)
               .append('\t').append(msg).append('\n');
            System.out.println("  " + tool + ": FAIL " + msg);
        }
    }

    public static void main(String[] a) throws Exception {
        if (a.length < 3) {
            System.err.println("usage: Bench <inDir> <outDir> <TOOL,TOOL|ALL>");
            System.exit(2);
        }
        IN = new File(a[0]);
        OUT = new File(a[1]);
        OUT.mkdirs();
        for (String s : a[2].split(",")) {
            String t = s.trim();
            if (!t.isEmpty()) WANTED.add(t);
        }

        run("MERGE", () -> PdfEngine.merge(
                Arrays.asList(in("a.pdf"), in("b.pdf")), out("merge.pdf")));

        run("MERGE_IMG", () -> PdfEngine.merge(
                Arrays.asList(in("img.pdf"), in("img.pdf")), out("merge_img.pdf")));

        run("SPLIT", () -> {
            List<int[]> r = new ArrayList<>();
            r.add(new int[]{1, 2});
            r.add(new int[]{3, 4});
            File dir = out("split/x");
            dir.mkdirs();
            PdfEngine.splitToFiles(in("multi.pdf"), r, dir, "s");
        });

        run("CROP", () -> PdfEngine.cropPages(
                in("multi.pdf"), 1, 60f, 60f, 300f, 300f, true, out("crop.pdf")));

        run("CROP_LEAK", () -> PdfEngine.cropPages(
                in("cropbox.pdf"), 1, 60f, 60f, 300f, 300f, true, out("crop_leak.pdf")));

        run("PAGES", () -> PdfEngine.rebuild(
                in("multi.pdf"), Arrays.asList(4, 2, 3, 1), null, out("organize.pdf")));

        run("ROTATE", () -> PdfEngine.rotatePages(
                in("multi.pdf"), Arrays.asList(1, 2), 90, out("rotate.pdf")));

        run("WATERMARK", () -> {
            PdfEngine.WatermarkOptions o = new PdfEngine.WatermarkOptions();
            o.text = "CONFIDENTIAL";
            o.fontSize = 40f;
            o.opacity = 0.30f;
            PdfEngine.watermarkText(in("multi.pdf"), o, out("watermark.pdf"));
        });

        run("PAGENUM", () -> PdfEngine.addPageNumbers(
                in("multi.pdf"), "Page {n} of {total}", 10f, 0xFF000000, out("pagenum.pdf")));

        run("COMPRESS", () -> PdfEngine.compress(in("img.pdf"), out("compress.pdf")));

        run("PROTECT", () -> PdfEngine.encrypt(
                in("multi.pdf"), "secret123", "owner456", out("protect.pdf")));

        run("UNLOCK", () -> PdfEngine.decrypt(
                out("protect.pdf"), "secret123", out("unlock.pdf")));

        run("METADATA", () -> {
            PdfEngine.MetadataInfo mi = new PdfEngine.MetadataInfo();
            mi.title = "Benchmark Title";
            mi.author = "Benchmark Author";
            mi.subject = "Benchmark Subject";
            mi.keywords = "one,two,three";
            PdfEngine.setMetadata(in("multi.pdf"), mi, out("metadata.pdf"));
        });

        run("EXTRACT", () -> {
            File dir = out("extract/x");
            dir.mkdirs();
            PdfEngine.extractImages(in("img.pdf"), dir);
        });

        run("LINKS", () -> PdfEngine.addTextLink(
                in("rot.pdf"), 1, 100f, 100f, 14f, "TESTLINK", null, 0xFF0000FF,
                "https://example.com/bench", 1f, out("link.pdf")));

        run("LINKS_ALL", () -> PdfEngine.addTextLinkAllPages(
                in("rot.pdf"), 100f, 100f, 14f, "ALLLINK", null, 0xFF0000FF,
                "https://example.com/all", 1f, out("link_all.pdf")));

        run("SIGN", () -> {
            PdfSigner.SignParams p = new PdfSigner.SignParams();
            p.name = "Benchmark Signer";
            p.organisation = "KavoPDF";
            p.reason = "Benchmark";
            p.location = "India";
            PdfSigner.sign(in("multi.pdf"), out("sign.pdf"), p);
        });

        // --- the signature must break when the file is altered -------------------
        run("TAMPER", () -> {
            byte[] b = java.nio.file.Files.readAllBytes(out("sign.pdf").toPath());
            // flip a byte inside the signed range, well past the header
            int at = Math.min(b.length - 200, b.length / 2);
            b[at] = (byte) (b[at] ^ 0xFF);
            java.nio.file.Files.write(out("tampered.pdf").toPath(), b);
        });

        run("VERIFY_TAMPER", () -> {
            List<PdfSigner.SignatureInfo> si = PdfSigner.verify(out("tampered.pdf"));
            int ok = 0;
            for (PdfSigner.SignatureInfo s : si) if (s.valid) ok++;
            try (PrintWriter w = new PrintWriter(new FileWriter(out("verify_tamper.txt")))) {
                w.println("signatures=" + si.size());
                w.println("valid=" + ok);
            }
        });

        run("VERIFY", () -> {
            List<PdfSigner.SignatureInfo> si = PdfSigner.verify(out("sign.pdf"));
            int ok = 0;
            for (PdfSigner.SignatureInfo s : si) if (s.valid) ok++;
            // score_all.py reads this line; the engine's own verdict is not the measurement,
            // it is one input to it.
            try (PrintWriter w = new PrintWriter(new FileWriter(out("verify.txt")))) {
                w.println("signatures=" + si.size());
                w.println("valid=" + ok);
            }
        });

        run("FORMS", () -> {
            Map<String, String> v = new LinkedHashMap<>();
            v.put("name", "SANDEEP KULKARNI");
            v.put("email", "sandeep@example.com");
            v.put("city", "Pune");
            PdfEngine.fillForm(in("form.pdf"), v, out("forms.pdf"));
        });

        run("ANNOTATE", () -> PdfEngine.addText(
                in("multi.pdf"), 1, "ANNOTATED TEXT", 120f, 500f, 16f,
                0xFFCC0000, out("annotate.pdf")));

        run("CREATE_PDF", () -> {
            List<PdfEngine.PageSpec> pages = new ArrayList<>();
            pages.add(new PdfEngine.PageSpec(595f, 842f, 0xFFFFFFFF, null));
            pages.add(new PdfEngine.PageSpec(595f, 842f, 0xFFF0F0F0, null));
            PdfEngine.createPdf(pages, out("create.pdf"));
        });

        run("IMAGES_PDF", () -> {
            File dir = out("png/x");
            dir.mkdirs();
            List<File> pngs = new ArrayList<>();
            int[] cols = {0xFFD05050, 0xFF50A0D0, 0xFF50B070};
            for (int i = 0; i < 3; i++) {
                int[] px = new int[200 * 150];
                Arrays.fill(px, cols[i]);
                Bitmap bm = Bitmap.createBitmap(px, 200, 150, Bitmap.Config.ARGB_8888);
                File f = new File(dir, "src" + i + ".png");
                try (FileOutputStream fo = new FileOutputStream(f)) {
                    bm.compress(Bitmap.CompressFormat.PNG, 100, fo);
                }
                pngs.add(f);
            }
            PdfEngine.imagesToPdf(pngs, out("img2pdf.pdf"));
        });

        run("BOOKMARKS", () -> {
            List<PdfEngine.Bookmark> bm = new ArrayList<>();
            String[] titles = {"First", "Second", "Third", "Fourth"};
            for (int i = 0; i < 4; i++) {
                bm.add(new PdfEngine.Bookmark(titles[i], i + 1, 0));
            }
            PdfEngine.setBookmarks(in("multi.pdf"), bm, out("bookmarks.pdf"));
        });

        run("REDACT", () -> {
            // The page is rendered by PyMuPDF ahead of time, because PDFBox-Android's
            // renderer needs a Canvas the desktop stubs do not implement. The painter hands
            // back exactly the picture the real screen would have produced.
            final Bitmap painted = android.graphics.BitmapFactory.decodeFile(
                    in("page1.png").getAbsolutePath());
            if (painted == null) throw new IllegalStateException("page1.png did not decode");
            PdfEngine.redactPagesLazy(in("secret.pdf"), new int[]{1},
                    page1 -> painted, out("redact.pdf"));
        });

        run("PDF_TO_WORD", () -> {
            PdfToWord.Result r = PdfToWord.convert(in("multi.pdf"), null, null);
            PdfToWord.classifyHeadings(r);
            PdfToWord.writeTxt(r, out("p2w/multi.txt"));
            DocxWriter.write(r, out("p2w/multi.docx"));
        });

        run("REPAIR", () -> {
            File damaged = new File(IN, "damaged.pdf");
            byte[] all = java.nio.file.Files.readAllBytes(in("multi.pdf").toPath());
            java.nio.file.Files.write(damaged.toPath(), Arrays.copyOf(all, all.length / 2));
            PdfRepair.repair(damaged, "", out("repair.pdf"));
        });

        try (PrintWriter w = new PrintWriter(new File(OUT, "run.tsv"), "UTF-8")) {
            w.print(LOG);
        }
        System.out.println("DONE");
    }
}
