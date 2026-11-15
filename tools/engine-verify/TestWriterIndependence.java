import com.kavopdf.app.engine.DocxWriter;
import com.kavopdf.app.engine.PdfToWord;
import com.kavopdf.app.engine.ReadingOrder;
import com.tom_roush.pdfbox.android.PDFBoxResourceLoader;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/**
 * Do the two writers see the same document? SECTOR 19.
 *
 * <pre>
 *   java TestWriterIndependence <pdfDir> [limit]   (limit = the first N documents)
 * </pre>
 *
 * <p>The bug this exists for: {@code DocxWriter.write} moved a stamp's paragraphs inside
 * {@code page.blocks} - the list {@code TxtWriter} walks - so the .txt of one PDF depended on
 * whether the .docx writer had run first. It was invisible to every text check, because all of
 * them pair by text and a reordering pairs just as well one way as the other: 11 of 211 documents
 * wrote a different .txt, and all 11 scored identically both ways.
 *
 * <p>So this asks the question directly, per document, and it fails loudly:
 *
 * <ol>
 *   <li><b>the model does not move</b> - a fingerprint of the whole {@code Result} is taken
 *       before and after {@code DocxWriter.write} and must be equal, so any writer that writes
 *       on the document again (a new field, a new list, a new order) fails here rather than in a
 *       .txt nobody diffs;</li>
 *   <li><b>the .txt does not depend on the .docx</b> - the .txt is written before and after the
 *       .docx write and the two byte arrays must be equal;</li>
 *   <li><b>a second write is the same write</b> - the .docx is written twice and every member of
 *       the archive must hash the same, so writer state cannot leak into the next call.</li>
 * </ol>
 *
 * <p>Exit 0 only when every document passes all three. Exit 2 when it cannot run.
 */
public class TestWriterIndependence {

    private static File findAssets() {
        String[] candidates = {"libs/aar/assets", "tools/engine-verify/libs/aar/assets",
                "../libs/aar/assets"};
        for (String c : candidates) {
            File f = new File(c);
            if (f.isDirectory()) return f;
        }
        return null;
    }

    public static void main(String[] a) throws Exception {
        File assets = findAssets();
        if (assets == null) {
            System.err.println("no PDFBox asset folder - run this from tools/engine-verify");
            System.exit(2);
        }
        PDFBoxResourceLoader.init(new android.content.Context(
                new android.content.res.AssetManager(assets)));
        String dir = a.length > 0 ? a[0] : System.getenv("P2W_CORPUS");
        if (dir == null) {
            System.err.println("usage: TestWriterIndependence <pdfDir> [limit]");
            System.exit(2);
        }
        int limit = a.length > 1 ? Integer.parseInt(a[1]) : 0;
        File inDir = new File(dir);
        File[] files = inDir.listFiles((d, n) -> n.toLowerCase().endsWith(".pdf"));
        if (files == null) {
            System.err.println("no pdfs in " + dir);
            System.exit(2);
        }
        Arrays.sort(files);
        if (limit > 0 && files.length > limit) {
            File[] head = new File[limit];
            System.arraycopy(files, 0, head, 0, limit);
            files = head;
        }
        // /tmp on the measurement image is 64 MB and a run of the whole corpus needs far more
        // than that if the files are kept, so they are deleted as each document finishes and the
        // folder can be moved with -Dp2w.indep.dir.
        File tmp = Files.createTempDirectory(
                new File(System.getProperty("p2w.indep.dir", System.getProperty("java.io.tmpdir")))
                        .toPath(), "p2w-indep").toFile();
        int bad = 0;
        int modelMoves = 0, txtMoves = 0, secondDiffers = 0;
        for (File in : files) {
            String base = in.getName().replaceFirst("\\.pdf$", "");
            try {
                PdfToWord.Result r = PdfToWord.convert(in, "", null);
                PdfToWord.classifyHeadings(r);
                ReadingOrder.apply(r);

                String before = fingerprint(r);
                File txtA = new File(tmp, base + ".a.txt");
                PdfToWord.writeTxt(r, txtA);
                byte[] txtAbytes = Files.readAllBytes(txtA.toPath());

                File docx1 = new File(tmp, base + ".1.docx");
                DocxWriter.write(r, docx1);

                String after = fingerprint(r);
                File txtB = new File(tmp, base + ".b.txt");
                PdfToWord.writeTxt(r, txtB);
                byte[] txtBbytes = Files.readAllBytes(txtB.toPath());

                File docx2 = new File(tmp, base + ".2.docx");
                DocxWriter.write(r, docx2);

                boolean modelOk = before.equals(after);
                boolean txtOk = Arrays.equals(txtAbytes, txtBbytes);
                Map<String, String> m1 = members(docx1), m2 = members(docx2);
                boolean twiceOk = m1.equals(m2);

                if (!modelOk) {
                    modelMoves++;
                    System.out.println("MODEL MOVED  " + base + "  " + firstDiff(before, after));
                }
                if (!txtOk) {
                    txtMoves++;
                    System.out.println("TXT CHANGED  " + base + "  " + txtAbytes.length
                            + " -> " + txtBbytes.length + " bytes");
                }
                if (!twiceOk) {
                    secondDiffers++;
                    List<String> changed = new ArrayList<>();
                    for (String n : m1.keySet()) {
                        if (!m1.get(n).equals(m2.get(n))) changed.add(n);
                    }
                    System.out.println("SECOND WRITE DIFFERS  " + base + "  " + changed);
                }
                if (!modelOk || !txtOk || !twiceOk) bad++;
                txtA.delete();
                txtB.delete();
                docx1.delete();
                docx2.delete();
            } catch (Throwable t) {
                bad++;
                System.out.println(base + "  FAILED  " + t);
            }
        }
        System.out.println("independence: " + (files.length - bad) + "/" + files.length
                + " documents clean (model moved " + modelMoves
                + ", .txt changed " + txtMoves
                + ", second write differed " + secondDiffers + ")");
        System.exit(bad == 0 ? 0 : 1);
    }

    // ------------------------------------------------------------------ fingerprints

    /**
     * Everything a writer could possibly change, in order, with object identity included.
     *
     * <p>Identity matters: swapping two blocks changes the page, and so does replacing one
     * paragraph with an equal copy - the first is what orderStamps did, the second is what a
     * writer that "tidies up" would do, and both must fail here.
     */
    private static String fingerprint(PdfToWord.Result r) {
        StringBuilder sb = new StringBuilder(1 << 16);
        sb.append("title=").append(r.title).append('\n');
        sb.append("report=").append(r.report.pages).append(',').append(r.report.paragraphs)
                .append(',').append(r.report.tables).append(',').append(r.report.images)
                .append(',').append(r.report.ocrPages).append(',').append(r.report.skippedPages)
                .append(',').append(r.report.imagesFailed).append(',')
                .append(r.report.imagesRecovered).append(',').append(r.report.zeroGap)
                .append(',').append(r.report.zeroGapAnchored).append(',')
                .append(r.report.zeroGapInCol).append(',').append(r.report.zeroGapNoRoom)
                .append(',').append(r.report.zeroGapWorstPt).append('\n');
        for (PdfToWord.Page p : r.pages) {
            sb.append("page ").append(p.number).append(' ').append(p.width).append('x')
                    .append(p.height).append(" cols=").append(p.columns).append('/')
                    .append(p.columnGap).append(" ocr=").append(p.ocr)
                    .append(" n=").append(p.blocks.size()).append('\n');
            for (Object b : p.blocks) {
                if (b instanceof PdfToWord.Para) {
                    PdfToWord.Para q = (PdfToWord.Para) b;
                    sb.append("  P@").append(System.identityHashCode(q)).append(' ')
                            .append(q.heading).append('/').append(q.align).append('/')
                            .append(q.indent).append('/').append(q.bullet).append('/')
                            .append(q.top).append('/').append(q.left).append('/')
                            .append(q.right).append('/').append(q.stamp).append('/')
                            .append(q.pinned).append('/').append(q.column)
                            .append(" r=").append(q.runs.size())
                            .append(" b=").append(q.boxes.size())
                            .append(" l=").append(q.lines.size()).append('/')
                            .append(q.lineX).append('/').append(q.lineY).append('/')
                            .append(q.lineSize).append(' ').append(hash(q.text())).append('\n');
                    for (PdfToWord.Box bx : q.boxes) {
                        sb.append("    B@").append(System.identityHashCode(bx)).append(' ')
                                .append(bx.x).append(',').append(bx.y).append(',')
                                .append(bx.right).append(',').append(bx.bottom).append(',')
                                .append(bx.size).append(',').append(bx.length).append(',')
                                .append(bx.rotated).append(',').append(bx.angle).append(',')
                                .append(bx.ring).append(' ').append(hash(bx.text())).append('\n');
                    }
                } else if (b instanceof PdfToWord.Table) {
                    PdfToWord.Table t = (PdfToWord.Table) b;
                    sb.append("  T@").append(System.identityHashCode(t)).append(' ')
                            .append(hash(t.rows)).append(' ').append(hash(t.cellX)).append(' ')
                            .append(hash(t.cellR)).append(' ').append(hash(t.cellY)).append(' ')
                            .append(hash(t.cellXPage)).append(' ').append(hash(t.fonts))
                            .append(' ').append(hash(t.sizes)).append(" paras=")
                            .append(t.paras.size()).append(" hasParas=").append(t.hasParas())
                            .append(" colX=").append(t.colX == null ? "-" : hash(Arrays.toString(t.colX)))
                            .append(" col=").append(t.column).append('\n');
                } else if (b instanceof DocxWriter.Shape) {
                    DocxWriter.Shape s = (DocxWriter.Shape) b;
                    sb.append("  S@").append(System.identityHashCode(s)).append(' ')
                            .append(s.xPt).append(',').append(s.topPt).append(',')
                            .append(s.wPt).append(',').append(s.hPt).append(" fill=")
                            .append(s.fillRgb).append('/').append(s.fillAlpha).append(" line=")
                            .append(s.lineRgb).append('/').append(s.lineWidthPt).append('/')
                            .append(s.lineAlpha).append(" kind=").append(s.kind)
                            .append(" closed=").append(s.freeformClosed)
                            .append(" consumed=").append(s.consumed)
                            .append(" stampFrame=").append(s.stampFrame)
                            .append(" stampDrawn=").append(s.stampDrawn)
                            .append(" host=").append(s.mergedHost == null ? "-"
                                    : String.valueOf(System.identityHashCode(s.mergedHost)))
                            .append(" merged=").append(s.mergedShape == null ? "-"
                                    : String.valueOf(System.identityHashCode(s.mergedShape)))
                            .append('\n');
                } else {
                    sb.append("  ?").append(b == null ? "null" : b.getClass().getName())
                            .append('@').append(System.identityHashCode(b)).append('\n');
                }
            }
        }
        return sb.toString();
    }

    private static String firstDiff(String a, String b) {
        String[] la = a.split("\n"), lb = b.split("\n");
        for (int i = 0; i < Math.min(la.length, lb.length); i++) {
            if (!la[i].equals(lb[i])) {
                return "line " + (i + 1) + ": [" + la[i] + "] -> [" + lb[i] + "]";
            }
        }
        return "length " + la.length + " -> " + lb.length;
    }

    private static String hash(Object o) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] d = md.digest(String.valueOf(o).getBytes("UTF-8"));
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 6; i++) sb.append(String.format("%02x", d[i]));
            return sb.toString();
        } catch (Exception e) {
            return "?";
        }
    }

    /** Every entry of a .docx by SHA-256 - a zip's timestamps make the file bytes useless. */
    private static Map<String, String> members(File docx) throws IOException {
        Map<String, String> out = new java.util.TreeMap<>();
        try (ZipFile z = new ZipFile(docx)) {
            java.util.Enumeration<? extends ZipEntry> en = z.entries();
            while (en.hasMoreElements()) {
                ZipEntry e = en.nextElement();
                MessageDigest md;
                try {
                    md = MessageDigest.getInstance("SHA-256");
                } catch (Exception x) {
                    throw new IOException(x);
                }
                try (java.io.InputStream is = z.getInputStream(e)) {
                    byte[] buf = new byte[8192];
                    int n;
                    while ((n = is.read(buf)) > 0) md.update(buf, 0, n);
                }
                StringBuilder sb = new StringBuilder();
                for (byte bb : md.digest()) sb.append(String.format("%02x", bb));
                out.put(e.getName(), sb.toString());
            }
        }
        return out;
    }

    private TestWriterIndependence() {
    }
}
