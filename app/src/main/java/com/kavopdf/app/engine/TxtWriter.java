package com.kavopdf.app.engine;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * The plain-text rendering of a conversion.
 *
 * <p>A .txt carries no coordinates, no fonts and no colours, so position has to be
 * expressed in the only two things it does have: leading spaces for x, and blank lines
 * for y. Everything here is read from the numbers {@code buildPara} and
 * {@code buildTables} already kept, and nothing here writes back to the model. The .docx
 * path reads runs and never reads the line fields this uses, so a change in this class
 * cannot alter a .docx.
 *
 * <p>Two values are derived rather than guessed.
 *
 * <p>The <b>character width</b> is one value for the whole document, taken from the size
 * the page drew most of its characters at. Using each line's own size meant two lines
 * drawn at the same x landed in different columns, because a 16 pt title and an 8 pt
 * table cell give different widths from the same x. A table only lines up if every row
 * is measured with the same ruler.
 *
 * <p>The <b>line pitch</b> is the median of the gaps the page actually left between
 * consecutive lines, measured per page. A document set solid at 9 pt and one set at
 * 14 pt both get blank lines that match their own leading.
 *
 * <p>The constants below are safety limits, not formatting choices: a malformed PDF can
 * report an x of 100000 pt, and without a cap that becomes a seventeen-thousand-space
 * line and a file nobody can open.
 */
public final class TxtWriter {

    /** Most blank lines a vertical gap may open. A page-break artefact can report a gap
     *  of several hundred points; without a cap that is forty empty lines. */
    private static final int MAX_BLANK_LINES = 10;

    /** Most leading spaces any single line may carry, as a guard against a malformed
     *  coordinate. At a 5.7 pt character this is well past the width of any real page. */
    private static final int MAX_INDENT = 400;

    /** A monospace cell is about 0.6 of the point size. */
    private static final float CELL_RATIO = 0.6f;

    /** Leading a page at a given size uses when no line pair can be measured. */
    private static final float PITCH_RATIO = 1.2f;

    /** The size assumed when a document reports no usable font size at all. */
    private static final float DEFAULT_SIZE = 9f;

    private TxtWriter() {
    }

    public static void write(PdfToWord.Result result, File out) throws IOException {
        if (result == null || out == null) throw new IOException("nothing to write");
        float charW = documentCharWidth(result);
        float docPitch = documentPitch(result);
        StringBuilder sb = new StringBuilder(1 << 14);
        if (result.pages != null) {
            for (PdfToWord.Page page : result.pages) {
                if (page == null || page.blocks == null) continue;
                float pitch = pagePitch(page, docPitch);
                float lastY = -1f;
                for (Object block : page.blocks) {
                    if (block instanceof PdfToWord.Table) {
                        if (sb.length() > 0 && sb.charAt(sb.length() - 1) != '\n') sb.append('\n');
                        appendTable(sb, (PdfToWord.Table) block, charW);
                    } else if (block instanceof PdfToWord.Para) {
                        lastY = appendPara(sb, (PdfToWord.Para) block, charW, pitch, lastY);
                    }
                }
            }
        }
        if (sb.length() > 0 && sb.charAt(sb.length() - 1) != '\n') sb.append('\n');
        // A PDF can carry NUL and other control bytes inside its text. They are legal in a
        // .txt but every editor shows them as garbage. They become a space, not nothing: a
        // NUL between two words is a word separator, and deleting it ran "Strongly agree"
        // together. Tabs become spaces so a tab stop cannot shift a column the padding
        // has just set.
        String clean = sb.toString()
                .replaceAll("[\\u0000-\\u0008\\u000B\\u000C\\u000E-\\u001F]", " ")
                .replace("\t", "    ");
        // java.nio.file.Files.write is API 26 and minSdk is 24, so the bytes go through a
        // FileOutputStream: on Android 7.0/7.1 the nio call threw NoClassDefFoundError and
        // PDF-to-text failed on every document.
        byte[] bytes = clean.getBytes(java.nio.charset.StandardCharsets.UTF_8);
        try (java.io.OutputStream fos = new java.io.FileOutputStream(out)) {
            fos.write(bytes);
        }
    }

    /** Writes one paragraph, opening blank lines for the gap the page left above it. */
    private static float appendPara(StringBuilder sb, PdfToWord.Para para, float charW,
                                    float pitch, float lastY) {
        if (para.text().trim().isEmpty()) return lastY;
        if (para.lines == null || para.lines.isEmpty()) {
            sb.append(rtrim(para.text())).append('\n');
            return lastY;
        }
        for (int li = 0; li < para.lines.size(); li++) {
            String ln = para.lines.get(li);
            if (ln == null) continue;
            String trimmed = rtrim(ln);
            if (trimmed.isEmpty()) continue;
            float ly = li < para.lineY.size() ? para.lineY.get(li) : 0f;
            float lx = li < para.lineX.size() ? para.lineX.get(li) : 0f;
            if (lastY >= 0f && ly > lastY && pitch > 0f) {
                int blanks = Math.round((ly - lastY) / pitch) - 1;
                if (blanks > MAX_BLANK_LINES) blanks = MAX_BLANK_LINES;
                for (int b = 0; b < blanks; b++) sb.append('\n');
            }
            int pad = column(lx, charW);
            for (int i = 0; i < pad; i++) sb.append(' ');
            sb.append(trimmed).append('\n');
            lastY = ly;
        }
        return lastY;
    }

    /**
     * One cell per line, which is what a reader searching the text expects: every line the
     * PDF drew stays a line of its own. A row glued back together with padding would put
     * words on a line that appears nowhere in the file.
     */
    private static void appendTable(StringBuilder sb, PdfToWord.Table t, float charW) {
        if (t.rows == null) return;
        for (int ri = 0; ri < t.rows.size(); ri++) {
            List<String> row = t.rows.get(ri);
            if (row == null) continue;
            for (int ci = 0; ci < row.size(); ci++) {
                String cell = row.get(ci);
                if (cell == null) continue;
                int baseCol = column(cellLeft(t, ri, ci), charW);
                float right = cellRight(t, ri, ci);
                String[] parts = cell.split("\n");
                for (int pi = 0; pi < parts.length; pi++) {
                    String c = parts[pi].trim();
                    if (c.isEmpty()) continue;
                    int col = baseCol;
                    // A number the page drew flush against a cell's right edge belongs at
                    // that edge. Without this every amount sat at the cell's left edge and
                    // a column of figures stopped being a column.
                    if (isNumeric(c) && !Float.isNaN(right)) {
                        int startCol = column(right, charW) - c.length();
                        if (startCol > col) col = startCol;
                    }
                    for (int i = 0; i < col; i++) sb.append(' ');
                    sb.append(c).append('\n');
                }
            }
        }
        sb.append('\n');
    }

    private static float cellLeft(PdfToWord.Table t, int ri, int ci) {
        // Where the page drew it, when the table pass had to move it. A right-to-left table's
        // cellX is mirrored about the table's own extent, which is a Word column order and not
        // a page x; cellXPage is the number this file needs and is empty for every table that
        // was never reversed. See PdfToWord.Table#cellXPage.
        if (t.cellXPage != null && ri < t.cellXPage.size()) {
            List<Float> row = t.cellXPage.get(ri);
            if (row != null && ci < row.size()) {
                Float v = row.get(ci);
                if (v != null && !Float.isNaN(v) && v > 0f) return v;
            }
        }
        if (t.cellX != null && ri < t.cellX.size()) {
            List<Float> row = t.cellX.get(ri);
            if (row != null && ci < row.size()) {
                Float v = row.get(ci);
                if (v != null && !Float.isNaN(v) && v > 0f) return v;
            }
        }
        if (t.colX != null && ci < t.colX.length) return t.colX[ci];
        return Float.NaN;
    }

    private static float cellRight(PdfToWord.Table t, int ri, int ci) {
        if (t.cellR == null || ri >= t.cellR.size()) return Float.NaN;
        List<Float> row = t.cellR.get(ri);
        if (row == null || ci >= row.size()) return Float.NaN;
        Float v = row.get(ci);
        return v == null ? Float.NaN : v;
    }

    /** True when the text is only a number and its punctuation, which is what a page
     *  right-aligns. A label is not, however close to the margin it sits. */
    private static boolean isNumeric(String s) {
        boolean sawDigit = false;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c >= '0' && c <= '9') {
                sawDigit = true;
                continue;
            }
            if (c == ',' || c == '.' || c == '-' || c == '+' || c == '(' || c == ')'
                    || c == '%' || c == '/' || c == ':' || c == ' ' || c == '\u20B9'
                    || c == '$' || c == '\u00A0') continue;
            return false;
        }
        return sawDigit;
    }

    private static int column(float x, float charW) {
        if (charW <= 0f || Float.isNaN(x) || x <= 0f) return 0;
        long c = Math.round(x / charW);
        if (c < 0) return 0;
        if (c > MAX_INDENT) return MAX_INDENT;
        return (int) c;
    }

    private static String rtrim(String s) {
        int end = s.length();
        while (end > 0 && (s.charAt(end - 1) == ' ' || s.charAt(end - 1) == '\t')) end--;
        return end == s.length() ? s : s.substring(0, end);
    }

    /** One character width for the whole document, from the size the page drew most of its
     *  characters at. Weighted by character count, not by line count: a document with one
     *  16 pt title and five thousand characters of 8 pt table text is an 8 pt document,
     *  and measuring it at 16 pt would halve every column. */
    private static float documentCharWidth(PdfToWord.Result result) {
        TreeMap<Integer, Integer> weight = new TreeMap<>();
        if (result.pages != null) {
            for (PdfToWord.Page page : result.pages) {
                if (page == null || page.blocks == null) continue;
                for (Object block : page.blocks) {
                    if (block instanceof PdfToWord.Para) {
                        PdfToWord.Para p = (PdfToWord.Para) block;
                        if (p.lines == null) continue;
                        for (int i = 0; i < p.lines.size(); i++) {
                            String ln = p.lines.get(i);
                            if (ln == null) continue;
                            int n = ln.trim().length();
                            if (n == 0) continue;
                            addWeight(weight, i < p.lineSize.size() ? p.lineSize.get(i) : 0f, n);
                        }
                    } else if (block instanceof PdfToWord.Table) {
                        PdfToWord.Table t = (PdfToWord.Table) block;
                        if (t.rows == null) continue;
                        for (int ri = 0; ri < t.rows.size(); ri++) {
                            List<String> row = t.rows.get(ri);
                            if (row == null) continue;
                            for (int ci = 0; ci < row.size(); ci++) {
                                String cell = row.get(ci);
                                if (cell == null) continue;
                                int n = cell.replace('\n', ' ').trim().length();
                                if (n == 0) continue;
                                float s = 0f;
                                if (t.sizes != null && ri < t.sizes.size()) {
                                    List<Float> sr = t.sizes.get(ri);
                                    if (sr != null && ci < sr.size()) {
                                        Float v = sr.get(ci);
                                        if (v != null) s = v;
                                    }
                                }
                                addWeight(weight, s, n);
                            }
                        }
                    }
                }
            }
        }
        float size = weightedMedian(weight);
        if (size <= 0f) size = DEFAULT_SIZE;
        return Math.max(1f, size * CELL_RATIO);
    }

    private static void addWeight(TreeMap<Integer, Integer> weight, float size, int n) {
        if (size <= 0f || Float.isNaN(size) || n <= 0) return;
        // Half-point buckets: finer than any type scale, coarse enough that a PDF which
        // reports 9.004 and 8.997 for the same run does not split into two entries.
        int key = Math.round(size * 2f);
        if (key <= 0) return;
        Integer old = weight.get(key);
        weight.put(key, (old == null ? 0 : old) + n);
    }

    private static float weightedMedian(TreeMap<Integer, Integer> weight) {
        if (weight.isEmpty()) return 0f;
        long total = 0;
        for (Integer v : weight.values()) total += v;
        if (total <= 0) return 0f;
        long half = total / 2;
        long acc = 0;
        for (Map.Entry<Integer, Integer> e : weight.entrySet()) {
            acc += e.getValue();
            if (acc >= half) return e.getKey() / 2f;
        }
        return weight.lastKey() / 2f;
    }

    /** The leading this document uses, for a page with too few lines to measure one. */
    private static float documentPitch(PdfToWord.Result result) {
        List<Float> all = new ArrayList<>();
        if (result.pages != null) {
            for (PdfToWord.Page page : result.pages) {
                if (page != null) collectDeltas(page, all);
            }
        }
        float m = median(all);
        if (m > 0f) return m;
        float size = documentCharWidth(result) / CELL_RATIO;
        return Math.max(1f, size * PITCH_RATIO);
    }

    private static float pagePitch(PdfToWord.Page page, float docPitch) {
        List<Float> deltas = new ArrayList<>();
        collectDeltas(page, deltas);
        float m = median(deltas);
        return m > 0f ? m : docPitch;
    }

    private static void collectDeltas(PdfToWord.Page page, List<Float> out) {
        if (page.blocks == null) return;
        for (Object block : page.blocks) {
            if (!(block instanceof PdfToWord.Para)) continue;
            PdfToWord.Para p = (PdfToWord.Para) block;
            if (p.lineY == null) continue;
            for (int i = 1; i < p.lineY.size(); i++) {
                Float a = p.lineY.get(i - 1);
                Float b = p.lineY.get(i);
                if (a == null || b == null) continue;
                float d = b - a;
                if (d > 0f && !Float.isNaN(d)) out.add(d);
            }
        }
    }

    private static float median(List<Float> values) {
        if (values.isEmpty()) return 0f;
        List<Float> s = new ArrayList<>(values);
        Collections.sort(s);
        int n = s.size();
        if (n % 2 == 1) return s.get(n / 2);
        return (s.get(n / 2 - 1) + s.get(n / 2)) / 2f;
    }
}
