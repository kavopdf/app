import com.kavopdf.app.engine.PdfRepair;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Runs repair over a folder and writes, per file, the repaired PDF (if any) plus a JSON
 * record of what the engine claims. A separate grader compares those claims against what
 * the output really contains.
 */
public class RepairRun {

    public static void main(String[] a) throws Exception {
        File dir = new File(a.length > 0 ? a[0] : "/scratch/work/tort");
        File outDir = new File(a.length > 1 ? a[1] : "/scratch/work/tort-out");
        outDir.mkdirs();

        File[] all = dir.listFiles();
        List<File> files = new ArrayList<>();
        if (all != null) Arrays.sort(all);
        for (File f : all) {
            String n = f.getName().toLowerCase();
            if (n.endsWith(".pdf") && !n.equals("original.pdf")) files.add(f);
        }

        for (File f : files) {
            String name = f.getName();
            String stem = name.substring(0, name.length() - 4);
            File out = new File(outDir, "fixed_" + name);
            long t0 = System.currentTimeMillis();
            PdfRepair.Report r;
            try {
                r = PdfRepair.repair(f, "", out);
            } catch (Throwable t) {
                r = new PdfRepair.Report();
                r.failure = "threw: " + t;
            }
            long ms = System.currentTimeMillis() - t0;

            boolean outExists = out.isFile() && out.length() > 0;
            try (PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, stem + ".json")))) {
                w.println("{");
                w.println("  \"file\": \"" + name + "\",");
                w.println("  \"ms\": " + ms + ",");
                w.println("  \"readable\": " + r.readable + ",");
                w.println("  \"verified\": " + r.verified + ",");
                w.println("  \"stage\": \"" + r.stage + "\",");
                w.println("  \"pagesBefore\": " + r.pagesBefore + ",");
                w.println("  \"pagesAfter\": " + r.pagesAfter + ",");
                w.println("  \"outExists\": " + outExists + ",");
                w.println("  \"failure\": \"" + esc(r.failure) + "\",");
                w.println("  \"findings\": " + arr(r.findings) + ",");
                w.println("  \"actions\": " + arr(r.actions) + ",");
                w.println("  \"lostPages\": " + ints(r.lostPages) + ",");
                w.println("  \"blankPages\": " + ints(r.blankPages) + ",");
                w.println("  \"partialPages\": " + ints(r.partialPages));
                w.println("}");
            }
            System.out.println(name + " -> pages=" + r.pagesAfter + " verified=" + r.verified
                    + " out=" + outExists + " " + ms + "ms");
        }
    }

    static String esc(String s) {
        return s == null ? "" : s.replace("\\", "\\\\").replace("\"", "\\\"")
                .replace("\n", " ").replace("\r", " ");
    }

    static String arr(List<String> xs) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < xs.size(); i++) {
            if (i > 0) sb.append(", ");
            sb.append('"').append(esc(xs.get(i))).append('"');
        }
        return sb.append(']').toString();
    }

    static String ints(List<Integer> xs) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < xs.size(); i++) {
            if (i > 0) sb.append(", ");
            sb.append(xs.get(i));
        }
        return sb.append(']').toString();
    }
}
