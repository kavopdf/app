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
    public static void main(String[] a) throws Exception {
        if (a.length < 2) {
            System.err.println("usage: ConvertAll <inDir> <outDir>");
            System.exit(2);
        }
        File assets = new File(System.getProperty("p2w.assets", "libs/aar/assets"));
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
                System.out.println(base + "\tpages=" + r.report.pages
                        + "\tparagraphs=" + r.paragraphCount());
            } catch (Throwable t) {
                bad++;
                System.out.println(base + "\tFAILED\t" + t);
            }
        }
        System.out.println("done: " + files.length + " files, " + bad + " failed");
    }
}
