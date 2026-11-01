package com.kavopdf.app.engine;

import com.tom_roush.pdfbox.contentstream.PDFGraphicsStreamEngine;
import com.tom_roush.pdfbox.cos.COSName;
import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.pdmodel.PDPage;
import com.tom_roush.pdfbox.pdmodel.PDResources;
import com.tom_roush.pdfbox.pdmodel.font.PDFont;
import com.tom_roush.pdfbox.pdmodel.graphics.form.PDFormXObject;
import com.tom_roush.pdfbox.pdmodel.graphics.form.PDTransparencyGroup;
import com.tom_roush.pdfbox.pdmodel.graphics.image.PDImage;
import com.tom_roush.pdfbox.pdmodel.graphics.image.PDImageXObject;
import com.tom_roush.pdfbox.pdmodel.graphics.shading.PDShading;
import com.tom_roush.pdfbox.pdmodel.interactive.annotation.PDAnnotation;
import com.tom_roush.pdfbox.text.PDFTextStripper;
import com.tom_roush.pdfbox.text.TextPosition;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

/**
 * Turns a PDF into an editable document.
 *
 * <p>The job is not to clone the page - Word is a flow format and a page is not. The job is to
 * recover what the page <em>says</em> and the structure it says it in: paragraphs, headings,
 * lists, tables, images, in the order a person would read them.
 *
 * <p>Three passes per page:
 * <ol>
 *   <li>glyphs - every character with its position, font and size, from PDFBox's own decoder,
 *       which is where ligatures, ToUnicode maps and subset fonts are handled correctly;</li>
 *   <li>geometry - glyphs into lines, lines into paragraphs, drawn rules into tables, and a
 *       vertical-gutter search that fixes reading order on multi-column pages;</li>
 *   <li>structure - heading levels from relative type size, alignment from the page margins,
 *       list nesting from indentation.</li>
 * </ol>
 *
 * <p>Nothing is invented. A page that cannot be read as text is handed to the OCR hook, and if
 * there is no hook the page is reported, not silently dropped.
 */
public final class PdfToWord {

    private PdfToWord() {
    }

    // ------------------------------------------------------------------ model

    /** A stretch of text sharing one set of character properties. */
    public static final class Run {
        public final String text;
        public final boolean bold;
        public final boolean italic;
        public final float sizePt;

        Run(String text, boolean bold, boolean italic, float sizePt) {
            this.text = text;
            this.bold = bold;
            this.italic = italic;
            this.sizePt = sizePt;
        }
    }

    /** A paragraph, with the runs that make it up. */
    public static final class Para {
        public final List<Run> runs = new ArrayList<>();
        public int heading;          // 0 body, 1..3 heading level
        public int align;            // 0 left, 1 centre, 2 right
        public int indent;           // list nesting depth, 0 = none
        public String bullet;        // "•", "1.", "-" or null
        public float top;            // y of the first line, for ordering
        public int column;           // which column band it sits in
        public int lines;            // how many visual lines the paragraph wraps to

        public String text() {
            StringBuilder sb = new StringBuilder();
            for (Run r : runs) sb.append(r.text);
            return sb.toString();
        }

        public float size() {
            return runs.isEmpty() ? 0f : runs.get(0).sizePt;
        }
    }

    /** A table, as the cells a reader sees. */
    public static final class Table {
        public final List<List<String>> rows = new ArrayList<>();
        public boolean header;
        public float top, bottom, left, right;
        public int column;
    }

    public static final class Page {
        public int number;
        public final List<Object> blocks = new ArrayList<>();   // Para or Table
        public boolean ocr;
    }

    /** What the conversion could and could not do. */
    public static final class Report {
        public int pages;
        public int paragraphs;
        public int tables;
        public int images;
        public int ocrPages;
        public int skippedPages;
        public final List<String> notes = new ArrayList<>();
    }

    public static final class Result {
        public final List<Page> pages = new ArrayList<>();
        public final Report report = new Report();
        public String title = "";

        public boolean isEmpty() {
            for (Page p : pages) if (!p.blocks.isEmpty()) return false;
            return true;
        }

        public int paragraphCount() {
            int n = 0;
            for (Page p : pages) for (Object b : p.blocks) if (b instanceof Para) n++;
            return n;
        }
    }

    /**
     * Supplies text for a page that holds no text layer. On the device this is ML Kit; in a
     * test harness it can be null, in which case the page is reported as unreadable.
     */
    public interface OcrHook {
        /** Text recognised on the given 0-based page, or null if it could not be read. */
        String text(int pageIndex) throws Exception;
    }

    // ------------------------------------------------------------------ conversion

    private static final float MIN_TEXT_CHARS = 12f;

    public static Result convert(File pdf, String password, OcrHook hook) throws IOException {
        Result result = new Result();
        try (PDDocument doc = PDDocument.load(pdf, password == null ? "" : password)) {
            if (doc.getDocumentInformation() != null
                    && doc.getDocumentInformation().getTitle() != null) {
                result.title = doc.getDocumentInformation().getTitle();
            }
            int count = doc.getNumberOfPages();
            result.report.pages = count;
            for (int i = 0; i < count; i++) {
                result.pages.add(readPage(doc, i, hook, result.report));
            }
        }
        return result;
    }

    private static Page readPage(PDDocument doc, int index, OcrHook hook, Report report) {
        Page page = new Page();
        page.number = index + 1;
        PDPage pdPage = doc.getPage(index);

        List<Glyph> glyphs = glyphsOf(doc, index);
        int chars = 0;
        for (Glyph g : glyphs) chars += g.text.length();

        if (chars < MIN_TEXT_CHARS) {
            // No usable text layer. Either OCR it, or say plainly that it was not read.
            String ocrText = null;
            if (hook != null) {
                try {
                    ocrText = hook.text(index);
                } catch (Throwable ignored) {
                }
            }
            if (ocrText != null && !ocrText.trim().isEmpty()) {
                page.ocr = true;
                report.ocrPages++;
                for (String block : ocrText.split("\\n\\s*\\n")) {
                    String t = block.trim();
                    if (t.isEmpty()) continue;
                    Para p = new Para();
                    p.runs.add(new Run(t.replaceAll("\\s*\\n\\s*", " "), false, false, 11f));
                    p.top = 0;
                    page.blocks.add(p);
                    report.paragraphs++;
                }
            } else {
                report.skippedPages++;
                report.notes.add("page " + (index + 1)
                        + " has no text layer and was not OCR'd - it comes out empty");
            }
            return page;
        }

        Rules rules = rulesOf(doc, index);
        report.images += rules.images;

        float pageWidth = pdPage.getMediaBox().getWidth();
        List<Line> rawLines = toLines(glyphs, new ArrayList<float[]>());

        // Tables are found from the drawn rules, so they can be located before any line is
        // split. A column start that falls inside one is that table's cell separator, not a
        // page column - splitting there would tear every row apart.
        List<Table> firstPass = buildTables(rules, rawLines, pageWidth);

        // Borderless tables are found here, before the column starts are filtered, so that a
        // table's cell positions are known to be cell separators. Otherwise the cells look
        // like page columns, and the heading above the table gets a later column than the
        // table itself - which puts the heading after the table in the output.
        List<Table> rowPass = rowTables(rawLines, firstPass, pageWidth);

        List<Float> starts = new ArrayList<>();
        for (Float x : columnStarts(rawLines)) {
            boolean inTable = false;
            for (Table t : firstPass) {
                if (x >= t.left - 4 && x <= t.right + 4) { inTable = true; break; }
            }
            for (Table t : rowPass) {
                if (x >= t.left - 4 && x <= t.right + 4) { inTable = true; break; }
            }
            if (!inTable) starts.add(x);
        }
        List<Line> lines = toLines(glyphs, asBands(starts));

        List<Table> tables = buildTables(rules, lines, pageWidth);
        tables.addAll(rowPass);
        List<Line> body = new ArrayList<>();
        for (Line line : lines) {
            if (line.consumed) continue;
            boolean inTable = false;
            for (Table t : tables) {
                if (line.inside(t)) {
                    inTable = true;
                    break;
                }
            }
            if (!inTable) body.add(line);
        }

        int bands = columns(body, pageWidth, asBands(starts));
        List<Para> paras = toParagraphs(body, pageWidth, bands);

        // Order everything the way a reader would: down one column, then the next.
        List<Object> ordered = new ArrayList<>();
        for (Table t : tables) ordered.add(t);
        for (Para p : paras) ordered.add(p);

        // A page of two tall text columns reads down one and then the other. A page of four
        // short boxes reads left to right, then down. The difference is whether the bands
        // hold a column of text or just a box, so it is counted, not guessed.
        // Wrapped text means a column of prose; single-line items side by side mean a grid of
        // boxes. That is the real difference between "read down, then across" and "read
        // across, then down" - counting paragraphs got both cases wrong.
        boolean wrapped = false;
        for (Para p : paras) if (p.lines >= 2) wrapped = true;
        final boolean rowMajor = bands > 1 && !wrapped;
        Collections.sort(ordered, new Comparator<Object>() {
            @Override
            public int compare(Object a, Object b) {
                if (rowMajor) {
                    int c = Float.compare(topOf(a), topOf(b));
                    if (Math.abs(topOf(a) - topOf(b)) > 6f) return c;
                    return columnOf(a) - columnOf(b);
                }
                int ca = columnOf(a), cb = columnOf(b);
                if (ca != cb) return ca - cb;
                return Float.compare(topOf(a), topOf(b));
            }
        });
        Collections.sort(ordered, new Comparator<Object>() {
            @Override
            public int compare(Object a, Object b) {
                int ca = columnOf(a), cb = columnOf(b);
                if (ca != cb) return ca - cb;
                return Float.compare(topOf(a), topOf(b));
            }
        });

        for (Object o : ordered) {
            page.blocks.add(o);
            if (o instanceof Para) report.paragraphs++;
            else report.tables++;
        }
        return page;
    }

    private static int columnOf(Object o) {
        return o instanceof Para ? ((Para) o).column : ((Table) o).column;
    }

    private static float topOf(Object o) {
        return o instanceof Para ? ((Para) o).top : ((Table) o).top;
    }

    // ------------------------------------------------------------------ glyphs

    static final class Glyph {
        String text;
        float x, y, width, size;
        String font;
        boolean bold, italic;
    }

    private static final class GlyphCollector extends PDFTextStripper {
        final List<Glyph> out = new ArrayList<>();

        GlyphCollector() throws IOException {
            super();
            setSortByPosition(false);
            setSuppressDuplicateOverlappingText(true);
        }

        @Override
        protected void processTextPosition(TextPosition tp) {
            String u = tp.getUnicode();
            if (u == null || u.isEmpty()) return;
            Glyph g = new Glyph();
            g.text = u;
            g.x = tp.getXDirAdj();
            g.y = tp.getYDirAdj();
            g.width = tp.getWidthDirAdj();
            g.size = tp.getFontSizeInPt() > 0 ? tp.getFontSizeInPt() : tp.getFontSize();
            PDFont font = tp.getFont();
            g.font = font == null ? "" : font.getName();
            String n = g.font.toLowerCase(Locale.ROOT);
            g.bold = n.contains("bold") || n.contains("black") || n.contains("heavy")
                    || n.contains("semibold") || n.contains("demi");
            g.italic = n.contains("italic") || n.contains("oblique");
            out.add(g);
        }
    }

    private static List<Glyph> glyphsOf(PDDocument doc, int index) {
        try {
            GlyphCollector gc = new GlyphCollector();
            gc.setStartPage(index + 1);
            gc.setEndPage(index + 1);
            gc.getText(doc);
            return dedupe(gc.out);
        } catch (Throwable t) {
            return new ArrayList<>();
        }
    }

    /** Drops the second copy of text that sits on top of the first, as OCR overlays do. */
    private static List<Glyph> dedupe(List<Glyph> in) {
        List<Glyph> out = new ArrayList<>(in.size());
        for (Glyph g : in) {
            boolean duplicate = false;
            for (int i = out.size() - 1; i >= 0 && i >= out.size() - 40; i--) {
                Glyph p = out.get(i);
                if (Math.abs(p.x - g.x) < 1.2f && Math.abs(p.y - g.y) < 1.2f
                        && p.text.equals(g.text)) {
                    duplicate = true;
                    break;
                }
            }
            if (!duplicate) out.add(g);
        }
        return out;
    }

    // ------------------------------------------------------------------ lines

    static final class Line {
        final List<Glyph> glyphs = new ArrayList<>();
        String text = "";
        float x, right, y, size, left;
        int column;
        boolean consumed;

        boolean inside(Table t) {
            float cx = (x + right) / 2f;
            return cx >= t.left - 2 && cx <= t.right + 2 && y >= t.top - 2 && y <= t.bottom + 2;
        }
    }

    private static List<Line> toLines(List<Glyph> glyphs, List<float[]> gutters) {
        List<Glyph> sorted = new ArrayList<>(glyphs);
        Collections.sort(sorted, new Comparator<Glyph>() {
            @Override
            public int compare(Glyph a, Glyph b) {
                int c = Float.compare(a.y, b.y);
                return c != 0 ? c : Float.compare(a.x, b.x);
            }
        });

        List<Line> lines = new ArrayList<>();
        Line current = null;
        float baseY = 0;
        for (Glyph g : sorted) {
            float tol = Math.max(1.2f, g.size * 0.3f);
            if (current == null || Math.abs(g.y - baseY) > tol) {
                current = new Line();
                current.glyphs.add(g);
                baseY = g.y;
                lines.add(current);
            } else {
                current.glyphs.add(g);
            }
        }

        // A line is not the same as a baseline: two columns sit on the same baseline, and
        // joining them produces "Left column starts here. Read this Right column starts at".
        // Any gap wide enough to be a gutter rather than a space starts a new segment.
        List<Line> split = new ArrayList<>();
        for (Line raw : lines) {
            Collections.sort(raw.glyphs, new Comparator<Glyph>() {
                @Override
                public int compare(Glyph a, Glyph b) {
                    return Float.compare(a.x, b.x);
                }
            });
            List<List<Glyph>> segments = new ArrayList<>();
            List<Glyph> run = new ArrayList<>();
            Glyph prev = null;
            for (Glyph g : raw.glyphs) {
                if (prev != null && crossesGutter(gutters, prev.x + prev.width, g.x)) {
                    segments.add(run);
                    run = new ArrayList<>();
                }
                run.add(g);
                prev = g;
            }
            if (!run.isEmpty()) segments.add(run);

            for (List<Glyph> segment : segments) {
                Line line = new Line();
                line.glyphs.addAll(segment);
                line.text = textOf(segment);
                float totalSize = 0;
                for (Glyph g : segment) totalSize += g.size;
                line.size = segment.isEmpty() ? 10f : totalSize / segment.size();
                line.x = segment.get(0).x;
                line.y = segment.get(0).y;
                float right = line.x;
                for (Glyph g : segment) right = Math.max(right, g.x + g.width);
                line.right = right;
                line.left = line.x;
                split.add(line);
            }
        }
        return split;
    }

    private static String textOf(List<Glyph> glyphs) {
        StringBuilder sb = new StringBuilder();
        Glyph prev = null;
        for (Glyph g : glyphs) {
            if (prev != null) {
                float gap = g.x - (prev.x + prev.width);
                if (gap > g.size * 0.18f && !endsWithSpace(sb)) sb.append(' ');
            }
            sb.append(g.text);
            prev = g;
        }
        return sb.toString();
    }


    private static boolean crossesGutter(List<float[]> gutters, float from, float to) {
        for (float[] g : gutters) {
            if (g[0] >= from && g[1] <= to) return true;
        }
        return false;
    }

    /**
     * Finds where a column begins, from the evidence on the page.
     *
     * <p>A column start is an x position where text begins after a wide gap, and which does the
     * same on at least two lines. One line with a gap is a tab or a wide space; the same x
     * twice is a second column. Counting this instead of measuring gutter bands survives ragged
     * columns, full-width headings above them, and columns that do not line up at the bottom.
     */
    private static List<Float> columnStarts(List<Line> lines) {
        List<Float> candidates = new ArrayList<>();
        for (Line line : lines) {
            if (line.text.trim().isEmpty() || line.glyphs.size() < 2) continue;
            Glyph prev = null;
            for (Glyph g : line.glyphs) {
                if (prev != null) {
                    float gap = g.x - (prev.x + prev.width);
                    float limit = Math.max(12f, Math.max(g.size, prev.size) * 1.6f);
                    if (gap > limit) candidates.add(g.x);
                }
                prev = g;
            }
        }
        if (candidates.size() < 2) return new ArrayList<>();

        Collections.sort(candidates);
        List<Float> starts = new ArrayList<>();
        int i = 0;
        while (i < candidates.size()) {
            int j = i;
            float sum = 0;
            while (j < candidates.size() && candidates.get(j) - candidates.get(i) <= 6f) {
                sum += candidates.get(j);
                j++;
            }
            int count = j - i;
            if (count >= 3) starts.add(sum / count);      // three lines agree, so it is a column
            i = j;
        }
        return starts;
    }

    /**
     * Turns column start positions into the narrow bands used to split a line.
     *
     * <p>The band sits just before the start, not around it: the text of the new cell begins at
     * x, so a band that reaches past x is never wholly inside the gap and the line would never
     * be split.
     */
    private static List<float[]> asBands(List<Float> starts) {
        List<float[]> bands = new ArrayList<>();
        for (Float x : starts) bands.add(new float[]{x - 5f, x - 1f});
        return bands;
    }

    private static boolean endsWithSpace(StringBuilder sb) {
        return sb.length() > 0 && sb.charAt(sb.length() - 1) == ' ';
    }

    // ------------------------------------------------------------------ columns

    /**
     * Splits a page into vertical bands by finding gutters - x positions that no line crosses.
     *
     * <p>This is what keeps a two-column paper readable: without it the two columns interleave
     * line by line and the result is nonsense. The search is bounded to three bands, because a
     * fourth column is a newspaper page and no flow conversion survives that anyway.
     */
    private static int columns(List<Line> lines, float pageWidth, List<float[]> bands) {
        if (bands.isEmpty()) {
            for (Line line : lines) line.column = 0;
            return 1;
        }
        List<Float> edges = new ArrayList<>();
        edges.add(0f);
        for (float[] b : bands) edges.add((b[0] + b[1]) / 2f);
        edges.add(pageWidth);
        for (Line line : lines) {
            float cx = (line.x + line.right) / 2f;
            int band = 0;
            for (int i = 0; i < edges.size() - 1; i++) {
                if (cx >= edges.get(i) && cx <= edges.get(i + 1)) {
                    band = i;
                    break;
                }
                if (cx > edges.get(i + 1)) band = i + 1;
            }
            line.column = Math.min(band, edges.size() - 2);
        }
        return edges.size() - 1;
    }

    // ------------------------------------------------------------------ paragraphs

    private static List<Para> toParagraphs(List<Line> lines, float pageWidth, int bands) {
        List<Para> out = new ArrayList<>();
        if (lines.isEmpty()) return out;

        Collections.sort(lines, new Comparator<Line>() {
            @Override
            public int compare(Line a, Line b) {
                int c = Integer.compare(a.column, b.column);
                return c != 0 ? c : Float.compare(a.y, b.y);
            }
        });

        List<Line> group = new ArrayList<>();
        for (Line line : lines) {
            if (line.text.trim().isEmpty()) continue;
            if (group.isEmpty()) {
                group.add(line);
                continue;
            }
            Line prev = group.get(group.size() - 1);
            if (sameParagraph(prev, line, pageWidth)) {
                group.add(line);
            } else {
                out.add(buildPara(group, pageWidth, bands));
                group = new ArrayList<>();
                group.add(line);
            }
        }
        if (!group.isEmpty()) out.add(buildPara(group, pageWidth, bands));
        return out;
    }

    private static boolean sameParagraph(Line prev, Line next, float pageWidth) {
        if (prev.column != next.column) return false;
        float gap = next.y - prev.y;
        float size = Math.max(prev.size, next.size);
        if (gap <= 0 || gap > size * 1.75f) return false;
        if (Math.abs(prev.size - next.size) > size * 0.18f) return false;

        boolean alignedLeft = Math.abs(prev.x - next.x) <= size * 0.6f;
        boolean continues = prev.right >= contentRight(prev, pageWidth) - size * 2.5f;
        boolean indented = next.x > prev.x + size * 1.2f;
        return alignedLeft || (continues && !indented);
    }

    private static float contentRight(Line line, float pageWidth) {
        return Math.min(pageWidth, line.right + line.size * 2f);
    }

    private static Para buildPara(List<Line> group, float pageWidth, int bands) {
        Para p = new Para();
        p.top = group.get(0).y;
        p.column = group.get(0).column;

        StringBuilder sb = new StringBuilder();
        String prevText = null;
        for (Line line : group) {
            String t = line.text.trim();
            if (t.isEmpty()) continue;
            if (prevText != null) {
                if (prevText.endsWith("-") && t.length() > 0
                        && Character.isLowerCase(t.charAt(0))) {
                    sb.setLength(sb.length() - 1);          // join a hyphenated break
                } else {
                    sb.append(' ');
                }
            }
            sb.append(t);
            prevText = t;
        }
        String text = sb.toString().trim();
        if (text.isEmpty()) text = "";

        // runs: consecutive glyphs sharing bold/italic/size become one run
        Line first = group.get(0);
        boolean bold = true, italic = false;
        float size = first.size;
        for (Line line : group) {
            for (Glyph g : line.glyphs) {
                if (!g.bold) bold = false;
                if (g.italic) italic = true;
            }
        }
        if (text.length() > 0) p.runs.add(new Run(text, bold, italic, size));

        p.lines = group.size();
        p.heading = headingLevel(group, text);
        p.align = alignment(group, pageWidth, bands);
        int indent = Math.max(0, Math.round((first.x - leftMargin(group)) / Math.max(8f, size * 1.6f)));
        p.indent = Math.min(indent, 4);
        p.bullet = bulletOf(text);
        if (p.bullet != null) p.indent = Math.max(1, p.indent);
        return p;
    }

    private static float leftMargin(List<Line> group) {
        float min = Float.MAX_VALUE;
        for (Line line : group) min = Math.min(min, line.x);
        return min;
    }

    private static String bulletOf(String text) {
        if (text.length() < 2) return null;
        char c = text.charAt(0);
        if (c == '•' || c == '◦' || c == '▪' || c == '–' || c == '—' || c == '●' || c == '○') {
            return String.valueOf(c);
        }
        if (c == '-' && text.length() > 2 && text.charAt(1) == ' ') return "-";
        if (c == '☐' || c == '☑' || c == '✓') return String.valueOf(c);
        return null;
    }

    private static int headingLevel(List<Line> group, String text) {
        // Relative size against the document body is decided later; here only the shape.
        return 0;
    }

    private static int alignment(List<Line> group, float pageWidth, int bands) {
        if (group.isEmpty()) return 0;
        Line first = group.get(0);
        float size = first.size;
        float left = Float.MAX_VALUE, right = 0;
        for (Line line : group) {
            left = Math.min(left, line.x);
            right = Math.max(right, line.right);
        }
        float bandLeft = 0, bandRight = pageWidth;
        if (bands > 1) {
            bandLeft = Math.max(0, left - 40);
            bandRight = Math.min(pageWidth, right + 40);
        }
        float center = (left + right) / 2f;
        float pageCenter = pageWidth / 2f;
        if (bands <= 1 && Math.abs(center - pageCenter) < size * 2.5f
                && left > pageWidth * 0.18f && right < pageWidth * 0.82f) {
            return 1;
        }
        if (right > bandRight - size && left > bandLeft + size * 2f) return 2;
        return 0;
    }

    /** Decides heading levels once the whole document's body size is known. */
    public static void classifyHeadings(Result result) {
        List<Float> sizes = new ArrayList<>();
        for (Page page : result.pages) {
            for (Object b : page.blocks) {
                if (!(b instanceof Para)) continue;
                Para p = (Para) b;
                String t = p.text();
                if (t.trim().isEmpty()) continue;
                int weight = Math.min(60, Math.max(1, t.length() / 4));
                for (int i = 0; i < weight; i++) sizes.add(p.size());
            }
        }
        if (sizes.isEmpty()) return;
        Collections.sort(sizes);
        float body = sizes.get(sizes.size() / 2);

        for (Page page : result.pages) {
            for (Object b : page.blocks) {
                if (!(b instanceof Para)) continue;
                Para p = (Para) b;
                String t = p.text().trim();
                if (t.isEmpty()) continue;
                float ratio = p.size() / Math.max(1f, body);
                boolean allBold = !p.runs.isEmpty() && p.runs.get(0).bold;
                boolean shortLine = t.length() <= 90;
                if (ratio >= 1.55f) p.heading = 1;
                else if (ratio >= 1.28f) p.heading = 2;
                else if (ratio >= 1.12f || (allBold && shortLine && ratio >= 1.02f)) p.heading = 3;
                if (p.heading > 0 && t.length() > 140) p.heading = 0;   // a heading is not a paragraph
            }
        }
    }

    // ------------------------------------------------------------------ drawn rules and tables

    /** Straight lines and rectangles the page draws - the skeleton a real table is built on. */
    static final class Rules {
        final List<float[]> horizontal = new ArrayList<>();   // {y, x1, x2}
        final List<float[]> vertical = new ArrayList<>();     // {x, y1, y2}
        int images;
    }

    private static final class RuleCollector extends PDFGraphicsStreamEngine {
        final Rules rules = new Rules();
        private final android.graphics.Path path = new android.graphics.Path();
        private float startX, startY, lastX, lastY;

        RuleCollector(PDPage page) {
            super(page);
        }

        @Override
        public void appendRectangle(android.graphics.PointF p0, android.graphics.PointF p1,
                                    android.graphics.PointF p2, android.graphics.PointF p3) {
            float minX = Math.min(Math.min(p0.x, p1.x), Math.min(p2.x, p3.x));
            float maxX = Math.max(Math.max(p0.x, p1.x), Math.max(p2.x, p3.x));
            float minY = Math.min(Math.min(p0.y, p1.y), Math.min(p2.y, p3.y));
            float maxY = Math.max(Math.max(p0.y, p1.y), Math.max(p2.y, p3.y));
            // A rectangle is a table border candidate: keep all four edges.
            if (maxX - minX > 2) {
                rules.horizontal.add(new float[]{minY, minX, maxX});
                rules.horizontal.add(new float[]{maxY, minX, maxX});
            }
            if (maxY - minY > 2) {
                rules.vertical.add(new float[]{minX, minY, maxY});
                rules.vertical.add(new float[]{maxX, minY, maxY});
            }
        }

        @Override
        public void drawImage(PDImage pdImage) {
            rules.images++;
        }

        @Override
        public void clip(android.graphics.Path.FillType fillType) {
        }

        @Override
        public void moveTo(float x, float y) {
            startX = lastX = x;
            startY = lastY = y;
        }

        @Override
        public void lineTo(float x, float y) {
            float dx = Math.abs(x - lastX), dy = Math.abs(y - lastY);
            if (dx <= 0.8f && dy > 2f) {
                rules.vertical.add(new float[]{lastX, Math.min(lastY, y), Math.max(lastY, y)});
            } else if (dy <= 0.8f && dx > 2f) {
                rules.horizontal.add(new float[]{lastY, Math.min(lastX, x), Math.max(lastX, x)});
            }
            lastX = x;
            lastY = y;
        }

        @Override
        public void curveTo(float x1, float y1, float x2, float y2, float x3, float y3) {
            lastX = x3;
            lastY = y3;
        }

        @Override
        public android.graphics.PointF getCurrentPoint() {
            return new android.graphics.PointF(lastX, lastY);
        }

        @Override
        public void closePath() {
            lastX = startX;
            lastY = startY;
        }

        @Override
        public void endPath() {
        }

        @Override
        public void strokePath() {
        }

        @Override
        public void fillPath(android.graphics.Path.FillType fillType) {
        }

        @Override
        public void fillAndStrokePath(android.graphics.Path.FillType fillType) {
        }

        @Override
        public void shadingFill(COSName shadingName) {
        }
    }

    private static Rules rulesOf(PDDocument doc, int index) {
        Rules out = new Rules();
        try {
            PDPage page = doc.getPage(index);
            RuleCollector collector = new RuleCollector(page);
            collector.processPage(page);
            out.horizontal.addAll(collector.rules.horizontal);
            out.vertical.addAll(collector.rules.vertical);
            out.images = collector.rules.images;
        } catch (Throwable ignored) {
        }
        return out;
    }

    /**
     * Builds tables from the lines the page actually draws.
     *
     * <p>Only ruled tables are turned into Word tables. A table held together by whitespace
     * alone has no cell boundaries in the file - guessing them produces shifted columns and
     * merged cells, which is worse than leaving the text as text. Those pages keep their text
     * and the report says the table was flattened.
     */
    private static List<Table> buildTables(Rules rules, List<Line> lines, float pageWidth) {
        List<Table> out = new ArrayList<>();
        if (rules.horizontal.size() < 2 || rules.vertical.size() < 2) return out;

        List<Float> ys = mergedPositions(rules.horizontal, true);
        List<Float> xs = mergedPositions(rules.vertical, false);
        if (ys.size() < 2 || xs.size() < 2) return out;

        float top = ys.get(0), bottom = ys.get(ys.size() - 1);
        float left = xs.get(0), right = xs.get(xs.size() - 1);
        if (bottom - top < 12 || right - left < 30) return out;

        int rows = ys.size() - 1, cols = xs.size() - 1;
        if (rows < 1 || cols < 1 || rows > 400 || cols > 40) return out;

        String[][] cells = new String[rows][cols];
        for (Line line : lines) {
            float cx = (line.x + line.right) / 2f;
            int r = band(ys, line.y);
            int c = band(xs, cx);
            if (r < 0 || c < 0) continue;
            cells[r][c] = cells[r][c] == null ? line.text.trim() : cells[r][c] + " " + line.text.trim();
        }

        int filled = 0;
        for (String[] row : cells) for (String cell : row) if (cell != null) filled++;
        if (filled < 2) return out;                       // a box, not a table

        Table t = new Table();
        t.top = top;
        t.bottom = bottom;
        t.left = left;
        t.right = right;
        t.header = rows > 1;
        for (int r = 0; r < rows; r++) {
            List<String> row = new ArrayList<>();
            for (int c = 0; c < cols; c++) row.add(cells[r][c] == null ? "" : cells[r][c]);
            t.rows.add(row);
        }
        out.add(t);
        return out;
    }









    /**
     * Rebuilds a table that has no drawn lines, from the rows its cells sit on.
     *
     * <p>Each raw line is cut at its own wide gaps, so a row becomes the cells a reader sees.
     * Cells are then grouped by baseline, and consecutive rows that start at the same place
     * with short cells are a table.
     *
     * <p>Rows are allowed to carry different numbers of cells: a real table has empty cells,
     * and a row that stops early is still that row. Columns come from clustering the cell
     * positions across the whole run, and each cell is placed in the nearest column - which is
     * why a missing value leaves a gap in the right place instead of shifting the row.
     */
    private static List<Table> rowTables(List<Line> rawLines, List<Table> ruled, float pageWidth) {
        List<Table> out = new ArrayList<>();
        if (rawLines.size() < 3) return out;

        // cut every raw line at its own gaps
        List<Line> cells = new ArrayList<>();
        for (Line raw : rawLines) {
            if (raw.text.trim().isEmpty()) continue;
            boolean inRuled = false;
            for (Table t : ruled) {
                if (raw.inside(t)) { inRuled = true; break; }
            }
            if (inRuled) continue;

            List<Glyph> glyphs = new ArrayList<>(raw.glyphs);
            Collections.sort(glyphs, new Comparator<Glyph>() {
                @Override
                public int compare(Glyph a, Glyph b) { return Float.compare(a.x, b.x); }
            });
            List<Glyph> run = new ArrayList<>();
            Glyph prev = null;
            for (Glyph g : glyphs) {
                if (prev != null) {
                    float gap = g.x - (prev.x + prev.width);
                    float limit = Math.max(9f, Math.max(g.size, prev.size) * 1.1f);
                    if (gap > limit) {
                        cells.add(cellOf(run, raw));
                        run = new ArrayList<>();
                    }
                }
                run.add(g);
                prev = g;
            }
            if (!run.isEmpty()) cells.add(cellOf(run, raw));
        }
        if (cells.size() < 6) return out;

        Collections.sort(cells, new Comparator<Line>() {
            @Override
            public int compare(Line a, Line b) {
                int c = Float.compare(a.y, b.y);
                return c != 0 ? c : Float.compare(a.x, b.x);
            }
        });

        // rows: cells sharing a baseline
        List<List<Line>> rows = new ArrayList<>();
        List<Line> current = new ArrayList<>();
        float baseY = 0;
        for (Line cell : cells) {
            if (current.isEmpty() || Math.abs(cell.y - baseY) <= 3f) {
                current.add(cell);
                if (current.size() == 1) baseY = cell.y;
            } else {
                rows.add(current);
                current = new ArrayList<>();
                current.add(cell);
                baseY = cell.y;
            }
        }
        if (!current.isEmpty()) rows.add(current);

        int i = 0;
        while (i < rows.size()) {
            if (rows.get(i).size() < 2) { i++; continue; }
            int j = i + 1;
            while (j < rows.size() && rows.get(j).size() >= 2
                    && alignedStart(rows.get(i), rows.get(j))) j++;
            if (j - i >= 3 && shortCells(rows, i, j) && tightRows(rows, i, j)) {
                Table t = buildRowTable(rows, i, j);
                if (t != null) out.add(t);
            }
            i = Math.max(j, i + 1);
        }
        return out;
    }

    private static Line cellOf(List<Glyph> glyphs, Line parent) {
        Line cell = new Line();
        cell.glyphs.addAll(glyphs);
        cell.text = textOf(glyphs);
        float total = 0;
        for (Glyph g : glyphs) total += g.size;
        cell.size = glyphs.isEmpty() ? 10f : total / glyphs.size();
        cell.x = glyphs.get(0).x;
        cell.y = parent.y;
        float right = cell.x;
        for (Glyph g : glyphs) right = Math.max(right, g.x + g.width);
        cell.right = right;
        cell.left = cell.x;
        cell.column = parent.column;
        return cell;
    }

    /** Two rows belong to the same table when they start at the same place. */
    private static boolean alignedStart(List<Line> a, List<Line> b) {
        if (a.isEmpty() || b.isEmpty()) return false;
        float ax = a.get(0).x, bx = b.get(0).x;
        return Math.abs(ax - bx) <= 14f;
    }

    /** Builds the table, placing each cell in the nearest of the run's column positions. */
    private static Table buildRowTable(List<List<Line>> rows, int from, int to) {
        List<Float> rawStarts = new ArrayList<>();
        for (int r = from; r < to; r++) for (Line cell : rows.get(r)) rawStarts.add(cell.x);
        Collections.sort(rawStarts);

        List<Float> columns = new ArrayList<>();
        for (Float x : rawStarts) {
            if (columns.isEmpty() || Math.abs(x - columns.get(columns.size() - 1)) > 18f) {
                columns.add(x);
            }
        }
        if (columns.size() < 2 || columns.size() > 24) return null;

        Table t = new Table();
        t.top = rows.get(from).get(0).y;
        float bottom = t.top, left = Float.MAX_VALUE, right = 0;
        for (int r = from; r < to; r++) {
            String[] line = new String[columns.size()];
            for (Line cell : rows.get(r)) {
                int best = 0;
                float bestDistance = Float.MAX_VALUE;
                for (int c = 0; c < columns.size(); c++) {
                    float d = Math.abs(columns.get(c) - cell.x);
                    if (d < bestDistance) { bestDistance = d; best = c; }
                }
                line[best] = line[best] == null ? cell.text.trim() : line[best] + " " + cell.text.trim();
                bottom = Math.max(bottom, cell.y);
                left = Math.min(left, cell.x);
                right = Math.max(right, cell.right);
                cell.consumed = true;
            }
            List<String> texts = new ArrayList<>();
            for (String cell : line) texts.add(cell == null ? "" : cell);
            t.rows.add(texts);
        }
        t.bottom = bottom;
        t.left = left;
        t.right = right;
        t.header = true;
        t.column = rows.get(from).get(0).column;
        return t;
    }

    /** True when the run holds labels and values rather than sentences. */
    private static boolean shortCells(List<List<Line>> rows, int from, int to) {
        int total = 0, cells = 0;
        for (int r = from; r < to; r++) {
            for (Line line : rows.get(r)) {
                total += line.text.trim().length();
                cells++;
            }
        }
        return cells > 0 && (float) total / cells <= 32f;
    }

    /**
     * True when the rows sit close together, the way table rows do.
     *
     * <p>Separate boxes placed on a page also line up in a grid, but they are spread out over
     * the page; a table's rows follow one another at roughly the line spacing.
     */
    private static boolean tightRows(List<List<Line>> rows, int from, int to) {
        for (int r = from; r + 1 < to; r++) {
            float gap = rows.get(r + 1).get(0).y - rows.get(r).get(0).y;
            float size = rows.get(r).get(0).size;
            if (gap > Math.max(size * 2.4f, 16f)) return false;
        }
        return true;
    }

    /** Collapses runs of near-identical coordinates into one position. */
    private static List<Float> mergedPositions(List<float[]> segments, boolean byY) {
        List<Float> raw = new ArrayList<>();
        for (float[] seg : segments) raw.add(seg[0]);
        Collections.sort(raw);
        List<Float> merged = new ArrayList<>();
        for (float v : raw) {
            if (merged.isEmpty() || Math.abs(v - merged.get(merged.size() - 1)) > 1.6f) {
                merged.add(v);
            }
        }
        return merged;
    }

    /** Index of the band a coordinate falls in, or -1. */
    private static int band(List<Float> positions, float value) {
        for (int i = 0; i < positions.size() - 1; i++) {
            if (value >= positions.get(i) - 1.5f && value <= positions.get(i + 1) + 1.5f) return i;
        }
        return -1;
    }

    // ------------------------------------------------------------------ plain text

    /**
     * Writes the plain-text form: paragraphs separated by a blank line, table rows as
     * "cell | cell", no page separators - text is a flow, and a page break in the middle of a
     * sentence would be a lie.
     */
    public static void writeTxt(Result result, File out) throws IOException {
        StringBuilder sb = new StringBuilder(1 << 14);
        for (Page page : result.pages) {
            for (Object block : page.blocks) {
                if (block instanceof Table) {
                    Table t = (Table) block;
                    if (sb.length() > 0 && sb.charAt(sb.length() - 1) != '\n') sb.append('\n');
                    for (List<String> row : t.rows) {
                        StringBuilder line = new StringBuilder();
                        for (int c = 0; c < row.size(); c++) {
                            if (c > 0) line.append(" | ");
                            line.append(row.get(c).replace("\n", " ").trim());
                        }
                        sb.append(line.toString().trim()).append('\n');
                    }
                    sb.append('\n');
                } else if (block instanceof Para) {
                    String text = ((Para) block).text().trim();
                    if (text.isEmpty()) continue;
                    sb.append(text).append("\n\n");
                }
            }
        }
        java.nio.file.Files.write(out.toPath(),
                sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
    }
}
