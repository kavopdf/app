import com.kavopdf.app.engine.DocxWriter;
import com.kavopdf.app.engine.PdfToWord;
import com.tom_roush.pdfbox.android.PDFBoxResourceLoader;

import java.io.File;
import java.util.Arrays;

/**
 * Converts every PDF in a folder to .docx and .txt in one JVM.
 *
 *   java ConvertAll <inDir> <outDir>
 *
 * Same Result for both outputs, exactly as ConvertOne, so the .txt cannot describe a
 * different document from the .docx. One JVM for the whole corpus because starting a
 * JVM per document is 90 % of the wall time when the conversion itself is 0.3 s.
 */
public class ConvertAll {
    /** The asset folder, looked for where it actually is rather than assumed. */
    private static File findAssets() {
        String[] candidates = {
                "libs/aar/assets",
                "tools/engine-verify/libs/aar/assets",
                "../libs/aar/assets",
        };
        for (String c : candidates) {
            File f = new File(c);
            if (f.isDirectory()) return f;
        }
        return null;
    }

    public static void main(String[] a) throws Exception {
        if (a.length < 2) {
            System.err.println("usage: ConvertAll <inDir> <outDir>");
            System.exit(2);
        }
        // The font resources are what make text extraction work at all. With the wrong
        // path PDFBox returns no glyphs and every document converts to an empty file that
        // still reports success - a rebuild on 7 Nov produced 208 blank documents and said
        // "done: 208 files, 0 failed". So the path is found rather than assumed.
        String configured = System.getProperty("p2w.assets");
        File assets = configured != null ? new File(configured) : findAssets();
        if (assets == null || !assets.isDirectory()) {
            System.err.println("no PDFBox asset folder. Run this from tools/engine-verify, "
                    + "or pass -Dp2w.assets=/path/to/libs/aar/assets");
            System.exit(2);
        }
        PDFBoxResourceLoader.init(new android.content.Context(
                new android.content.res.AssetManager(assets)));

        File inDir = new File(a[0]);
        File outDir = new File(a[1]);
        outDir.mkdirs();
        File[] files = inDir.listFiles((d, n) -> n.toLowerCase().endsWith(".pdf"));
        if (files == null) { System.err.println("no pdfs in " + inDir); System.exit(2); }
        Arrays.sort(files);
        int bad = 0;
        for (File in : files) {
            String base = in.getName().replaceFirst("\\.pdf$", "");
            try {
                PdfToWord.Result r = PdfToWord.convert(in, "", null);
                PdfToWord.classifyHeadings(r);
                DocxWriter.write(r, new File(outDir, base + ".docx"));
                PdfToWord.writeTxt(r, new File(outDir, base + ".txt"));
                // An empty Result is not a conversion. It means the fonts did not load,
                // or the page really holds nothing - and either way a .docx with no
                // paragraphs must not be counted as a success.
                if (r.paragraphCount() == 0) {
                    System.err.println("EMPTY  " + in.getName()
                            + " - no paragraphs, so this conversion did not work");
                    bad++;
                    continue;
                }
                System.out.println(base + "\tpages=" + r.report.pages
                        + "\tparagraphs=" + r.paragraphCount()
                        + "\tzeroGap=" + r.report.zeroGap
                        + "\tzeroGapWorst=" + Math.round(r.report.zeroGapWorstPt * 10f) / 10f
                        + "\tzeroGapInCol=" + r.report.zeroGapInCol
                        + "\tzeroGapAnchored=" + r.report.zeroGapAnchored
                        + "\tzeroGapNoRoom=" + r.report.zeroGapNoRoom
                        + "\timages=" + r.report.images
                        + "\timagesFailed=" + r.report.imagesFailed
                        + "\timagesRecovered=" + r.report.imagesRecovered);
                for (String note : r.report.notes) {
                    System.out.println("  NOTE " + base + "  " + note);
                }
            } catch (Throwable t) {
                bad++;
                System.out.println(base + "\tFAILED\t" + t);
            }
        }
        System.out.println("done: " + files.length + " files, " + bad + " failed");
    }
}
