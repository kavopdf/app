package com.kavopdf.app.engine;

import com.tom_roush.pdfbox.android.PDFBoxResourceLoader;

import java.io.File;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

/**
 * Diagnostic: the engine's own rule-ownership ledger.
 *
 * One TSV line per rule the page drew:
 *
 *   RULE name page orient perp a b width rgb claim side owner
 *
 *   claim   KEEP / DROP - what attachShapes did with the shape that carries this rule
 *   side    which of the six sides of a table the rule lies on, or "-"
 *   owner   SHAPE    the rule is emitted as a wps shape
 *           TABLE    the shape pass dropped it and the table writer draws that side
 *           NEITHER  the shape pass dropped it and the table writer draws nothing there
 *           BOTH     the shape survived AND the table also draws a side on it
 *           NO-SHAPE the rule has no shape at all (it can only come from a table)
 *
 * The shape pass is reproduced by calling the real attachShapes() on a probe page and the
 * the writer's per-side answer from PdfToWord.Table#sideDrawn, on the
 * same Shape objects the conversion used, so identity is meaningful.
 */
public class RuleLedger {
    public static void main(String[] a) throws Exception {
        PDFBoxResourceLoader.init(new android.content.Context(
                new android.content.res.AssetManager(new File(a[1]))));
        Method attachShapes = PdfToWord.class.getDeclaredMethod("attachShapes",
                PdfToWord.Page.class, PdfToWord.Rules.class, float.class, List.class,
                int.class);
        attachShapes.setAccessible(true);
        Method rulesOf = PdfToWord.class.getDeclaredMethod("rulesOf",
                com.tom_roush.pdfbox.pdmodel.PDDocument.class, int.class);
        rulesOf.setAccessible(true);

        for (int ai = 2; ai < a.length; ai++) {
            File in = new File(a[ai]);
            PdfToWord.Result r = PdfToWord.convert(in, "", null);
            com.tom_roush.pdfbox.pdmodel.PDDocument doc =
                    com.tom_roush.pdfbox.pdmodel.PDDocument.load(in);
            for (int i = 0; i < r.pages.size(); i++) {
                PdfToWord.Page p = r.pages.get(i);
                PdfToWord.Rules rules = (PdfToWord.Rules) rulesOf.invoke(null, doc, i);
                List<PdfToWord.Table> tables = new ArrayList<>();
                for (Object b : p.blocks) if (b instanceof PdfToWord.Table) tables.add((PdfToWord.Table) b);

                // attachShapes rewrites s.topPt into the top-down frame on the objects it
                // keeps, so the raw geometry has to be read before it runs.
                float[] rawTop = new float[rules.shapes.size()];
                float[] rawX = new float[rules.shapes.size()];
                float[] rawW = new float[rules.shapes.size()];
                float[] rawH = new float[rules.shapes.size()];
                for (int q = 0; q < rules.shapes.size(); q++) {
                    DocxWriter.Shape s = rules.shapes.get(q);
                    rawTop[q] = s.topPt; rawX[q] = s.xPt; rawW[q] = s.wPt; rawH[q] = s.hPt;
                }
                PdfToWord.Page probe = new PdfToWord.Page();
                probe.width = p.width; probe.height = p.height;
                attachShapes.invoke(null, probe, rules, p.height, tables, 0);
                List<DocxWriter.Shape> kept = new ArrayList<>();
                for (Object b : probe.blocks) if (b instanceof DocxWriter.Shape) kept.add((DocxWriter.Shape) b);

                boolean[] drawn = new boolean[tables.size() * 6];
                for (int ti = 0; ti < tables.size(); ti++) {
                    PdfToWord.Table t = tables.get(ti);
                    boolean ruledTable = t.ruled;
                    for (int k = 0; k < 6; k++) drawn[ti * 6 + k] = ruledTable || t.sideDrawn[k];
                    StringBuilder sb = new StringBuilder();
                    for (int k = 0; k < 6; k++) {
                        float[] s = t.sideStroke[k];
                        sb.append(s == null ? "-" : String.format("%.2f/%s", s[0],
                                Integer.toHexString((int) s[1]))).append(' ');
                    }
                    System.out.printf("TBL\t%s\t%d\t%.2f\t%.2f\t%.2f\t%.2f\t%d\t%s\t%s\t%s\t%s\t%s%n",
                            in.getName(), i, t.left, t.right, t.top, t.bottom, t.rows.size(),
                            t.ruled, t.innerH, t.innerV, ruledTable, sb.toString().trim());
                }

                for (int o = 0; o < 2; o++) {
                    List<float[]> rl = o == 0 ? rules.horizontal : rules.vertical;
                    List<float[]> sl = o == 0 ? rules.hStroke : rules.vStroke;
                    for (int k = 0; k < rl.size(); k++) {
                        float[] ru = rl.get(k);
                        float[] st = k < sl.size() ? sl.get(k) : null;
                        double perp = ru[0], lo = ru[1], hi = ru[2];
                        double td = o == 0 ? p.height - perp : 0;
                        double topTd = o == 0 ? td : p.height - hi;
                        double botTd = o == 0 ? td : p.height - lo;
                        // the shape that carries this rule
                        DocxWriter.Shape carrier = null;
                        int cq = -1;
                        for (int q = 0; q < rules.shapes.size(); q++) {
                            if (o == 0) {
                                if (Math.abs(p.height + rawTop[q] + rawH[q] / 2 - td) < 1.5
                                        && Math.abs(rawX[q] - lo) < 1.5) { carrier = rules.shapes.get(q); cq = q; }
                            } else {
                                if (Math.abs(rawX[q] + rawW[q] / 2 - perp) < 1.5
                                        && Math.abs(p.height + rawTop[q] - topTd) < 1.5) { carrier = rules.shapes.get(q); cq = q; }
                            }
                        }
                        boolean claimDrop = carrier != null && !kept.contains(carrier);
                        String side = "-";
                        boolean tablePaints = false;
                        for (int ti = 0; ti < tables.size(); ti++) {
                            PdfToWord.Table t = tables.get(ti);
                            String s = sideOf(t, o, o == 0 ? td : perp,
                                    o == 0 ? lo : p.height - hi,
                                    o == 0 ? hi : p.height - lo);
                            if (s == null) continue;
                            if (side.equals("-")) side = s;
                            int idx = "top".equals(s) ? 0 : "left".equals(s) ? 1
                                    : "bottom".equals(s) ? 2 : "right".equals(s) ? 3
                                    : "insideH".equals(s) ? 4 : 5;
                            if (drawn[ti * 6 + idx]) tablePaints = true;
                        }
                        boolean shapeKept = carrier != null && kept.contains(carrier);
                        String owner = carrier == null ? (tablePaints ? "TABLE" : "NO-SHAPE")
                                : shapeKept ? (tablePaints ? "BOTH" : "SHAPE")
                                : (tablePaints ? "TABLE" : "NEITHER");
                        System.out.printf("RULE\t%s\t%d\t%s\t%.2f\t%.2f\t%.2f\t%.2f\t%s\t%s\t%s\t%s\t%s%n",
                                in.getName(), i, o == 0 ? "h" : "v", perp, lo, hi,
                                st == null ? -1 : st[0],
                                st == null ? "-" : Integer.toHexString((int) st[1]),
                                claimDrop ? "DROP" : "KEEP", side, owner, carrier != null);
                    }
                }
            }
            doc.close();
        }
    }

    static String sideOf(PdfToWord.Table t, int o, double perp, double lo, double hi) {
        float tol = 2.5f;
        float tw = t.right - t.left, th = t.bottom - t.top;
        if (o == 0) {
            if (Math.min(hi, t.right) - Math.max(lo, t.left) < 0.5 * tw) return null;
            if (Math.abs(perp - t.top) <= tol) return "top";
            if (Math.abs(perp - t.bottom) <= tol) return "bottom";
            if (perp > t.top + tol && perp < t.bottom - tol) return "insideH";
            return null;
        }
        if (Math.min(hi, t.bottom) - Math.max(lo, t.top) < 0.5 * th) return null;
        if (Math.abs(perp - t.left) <= tol) return "left";
        if (Math.abs(perp - t.right) <= tol) return "right";
        if (perp > t.left + tol && perp < t.right - tol) return "insideV";
        return null;
    }
}
