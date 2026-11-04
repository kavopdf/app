import com.kavopdf.app.engine.PdfRepair;
import java.io.*;
import java.util.*;

/**
 * Runs PdfRepair over a directory of PDFs and writes one line of JSON per file.
 *
 * It records what the engine *says* it did. Whether that is true is decided afterwards by
 * score_repair.py, which opens the output with PyMuPDF and checks. The two are compared:
 * a report that claims success on a file that does not open is the worst failure this tool
 * can have, because the user walks away believing their data was saved.
 *
 *   java RepairBench <inDir> <outDir> <report.jsonl>
 *
 * Each output keeps the input's relative name so the scorer can pair them up.
 */
public class RepairBench {

    static String esc(String s) {
        if (s == null) return "";
        StringBuilder b = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"': b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                default:
                    if (c < 0x20) b.append(String.format("\\u%04x", (int) c));
                    else b.append(c);
            }
        }
        return b.toString();
    }

    static String list(List<?> l) {
        StringBuilder b = new StringBuilder("[");
        for (int i = 0; i < l.size(); i++) {
            if (i > 0) b.append(',');
            Object o = l.get(i);
            b.append(o instanceof String ? "\"" + esc((String) o) + "\"" : String.valueOf(o));
        }
        return b.append(']').toString();
    }

    public static void main(String[] a) throws Exception {
        if (a.length < 3) {
            System.err.println("usage: RepairBench <inDir> <outDir> <report.jsonl>");
            System.exit(2);
        }
        File inDir = new File(a[0]);
        File outDir = new File(a[1]);
        outDir.mkdirs();
        File report = new File(a[2]);
        report.getParentFile().mkdirs();

        List<File> files = new ArrayList<>();
        collect(inDir, files);
        Collections.sort(files);
        System.out.println("files: " + files.size());

        try (PrintWriter w = new PrintWriter(new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(report), "UTF-8")))) {
            int n = 0, ok = 0;
            for (File f : files) {
                String rel = inDir.toURI().relativize(f.toURI()).getPath();
                File out = new File(outDir, rel);
                out.getParentFile().mkdirs();
                long t0 = System.nanoTime();
                StringBuilder line = new StringBuilder();
                line.append("{\"file\":\"").append(esc(rel)).append('"');
                try {
                    PdfRepair.Report r = PdfRepair.repair(f, "", out);
                    long ms = (System.nanoTime() - t0) / 1_000_000;
                    line.append(",\"threw\":false");
                    line.append(",\"ms\":").append(ms);
                    line.append(",\"readable\":").append(r.readable);
                    line.append(",\"stage\":\"").append(esc(r.stage)).append('"');
                    line.append(",\"failure\":\"").append(esc(r.failure)).append('"');
                    line.append(",\"pagesBefore\":").append(r.pagesBefore);
                    line.append(",\"pagesAfter\":").append(r.pagesAfter);
                    line.append(",\"lostPages\":").append(list(r.lostPages));
                    line.append(",\"blankPages\":").append(list(r.blankPages));
                    line.append(",\"partialPages\":").append(list(r.partialPages));
                    line.append(",\"formFields\":").append(r.formFields);
                    line.append(",\"hasOutline\":").append(r.hasOutline);
                    line.append(",\"hasLinks\":").append(r.hasLinks);
                    line.append(",\"encrypted\":").append(r.encrypted);
                    line.append(",\"signed\":").append(r.signed);
                    line.append(",\"verified\":").append(r.verified);
                    line.append(",\"verifyNote\":\"").append(esc(r.verifyNote)).append('"');
                    line.append(",\"sizeBefore\":").append(r.sizeBefore);
                    line.append(",\"sizeAfter\":").append(r.sizeAfter);
                    line.append(",\"findings\":").append(list(r.findings));
                    line.append(",\"actions\":").append(list(r.actions));
                    line.append(",\"outExists\":").append(out.exists());
                    line.append(",\"outSize\":").append(out.exists() ? out.length() : -1);
                    ok++;
                } catch (Throwable t) {
                    long ms = (System.nanoTime() - t0) / 1_000_000;
                    String m = t.toString();
                    if (m.length() > 300) m = m.substring(0, 300);
                    line.append(",\"threw\":true");
                    line.append(",\"ms\":").append(ms);
                    line.append(",\"error\":\"").append(esc(m)).append('"');
                    line.append(",\"outExists\":").append(out.exists());
                    line.append(",\"outSize\":").append(out.exists() ? out.length() : -1);
                }
                line.append('}');
                w.println(line);
                n++;
                if (n % 25 == 0) System.out.println("  " + n + "/" + files.size());
            }
            System.out.println("done: " + n + " files, " + ok + " without an exception");
        }
    }

    static void collect(File d, List<File> out) {
        File[] fs = d.listFiles();
        if (fs == null) return;
        for (File f : fs) {
            if (f.isDirectory()) collect(f, out);
            else if (f.getName().toLowerCase(Locale.ROOT).endsWith(".pdf")) out.add(f);
        }
    }
}
