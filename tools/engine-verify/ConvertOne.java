import com.kavopdf.app.engine.DocxWriter;
import com.kavopdf.app.engine.PdfToWord;
import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.android.PDFBoxResourceLoader;

import java.io.File;

/**
 * Converts one PDF to .docx and .txt. Used by the corpus bench.
 *
 *   java ConvertOne <in.pdf> <outDir>
 *
 * Both outputs come from the same PdfToWord.Result, so the .txt costs nothing extra and
 * cannot describe a different document from the .docx.
 */
public class ConvertOne {
    public static void main(String[] a) throws Exception {
        if (a.length < 2) {
            System.err.println("usage: ConvertOne <in.pdf> <outDir>");
            System.exit(2);
        }
        // Without this the pages come back with no text at all: the font resources live in
        // the aar's assets/ and are only reachable through the loader.
        File assets = new File(System.getProperty("p2w.assets", "libs/aar/assets"));
        PDFBoxResourceLoader.init(new android.content.Context(
                new android.content.res.AssetManager(assets)));

        File in = new File(a[0]);
        File outDir = new File(a[1]);
        outDir.mkdirs();

        String base = in.getName().replaceFirst("\\.pdf$", "");
        PdfToWord.Result r = PdfToWord.convert(in, "", null);
        PdfToWord.classifyHeadings(r);

        DocxWriter.write(r, new File(outDir, base + ".docx"));
        PdfToWord.writeTxt(r, new File(outDir, base + ".txt"));

        System.out.println(base + "\tpages=" + r.report.pages
                + "\tparagraphs=" + r.paragraphCount());
    }
}
