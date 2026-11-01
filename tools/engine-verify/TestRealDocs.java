import com.kavopdf.app.engine.PdfToWord;
import java.io.*; import java.util.*;
import java.util.regex.*;

/**
 * Real documents that once converted wrongly while the corpus said they passed.
 *
 * The v3 corpus grades each file with a few "must contain" strings. A scrambled document still
 * contains those strings, so a prescription that came out as one 30-column table and a question
 * paper ordered by x both counted as passes. These three are graded on word order instead.
 */
public class TestRealDocs {
    private static List<String> words(String s) {
        List<String> out = new ArrayList<>();
        for (String w : s.replace('\u00a0', ' ').trim().split("\\s+")) if (!w.isEmpty()) out.add(w);
        return out;
    }
    private static double similarity(List<String> a, List<String> b) {
        int n = a.size(), m = b.size();
        int[] prev = new int[m + 1], cur = new int[m + 1];
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= m; j++) {
                cur[j] = a.get(i - 1).equals(b.get(j - 1))
                        ? prev[j - 1] + 1 : Math.max(prev[j], cur[j - 1]);
            }
            int[] t = prev; prev = cur; cur = t;
            Arrays.fill(cur, 0);
        }
        int lcs = prev[m];
        return (2.0 * lcs) / (n + m);
    }
    public static void main(String[] args) throws Exception {
        File dir = new File("real/pdfs"), exp = new File("real/expected");
        File[] pdfs = dir.listFiles();
        if (pdfs == null) { System.out.println("REALDOCS: no fixtures"); return; }
        Arrays.sort(pdfs);
        int pass = 0, fail = 0;
        for (File pdf : pdfs) {
            String stem = pdf.getName().replaceAll("\\.pdf$", "");
            PdfToWord.Result r = PdfToWord.convert(pdf, "", null);
            PdfToWord.classifyHeadings(r);
            File got = File.createTempFile("realdoc", ".txt");
            PdfToWord.writeTxt(r, got);
            String mine = new String(java.nio.file.Files.readAllBytes(got.toPath()), "UTF-8");
            got.delete();
            String want = new String(java.nio.file.Files.readAllBytes(
                    new File(exp, stem + ".txt").toPath()), "UTF-8");
            double s = similarity(words(want), words(mine));
            boolean ok = s >= 0.90;
            System.out.println(String.format("  %-32s %.1f%%  %s", stem, s * 100, ok ? "ok" : "FAIL"));
            if (ok) pass++; else fail++;
        }
        System.out.println("REALDOCS TOTAL: " + pass + " passed, " + fail + " failed");
    }
}
