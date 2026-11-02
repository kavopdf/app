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
import java.util.TreeSet;
import java.util.ArrayDeque;
import java.util.Map;
import java.util.HashMap;
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
        public float left, right;    // horizontal extent, for the layout cut
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
        final float pageHeight = pdPage.getMediaBox().getHeight();
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

        // Rules come from the graphics engine with y measured up from the page bottom; glyphs
        // carry y measured down from the top. Without flipping one into the other, no glyph ever
        // falls inside a cell and every table comes out empty.
        float pageH = pageHeight;
        List<Edge> edges = new ArrayList<>();
        for (float[] h : rules.horizontal) {
            float y = pageH > 0 ? pageH - h[0] : h[0];
            edges.add(new Edge(true, h[1], y, h[2], y));
        }
        for (float[] v : rules.vertical) {
            float y0 = pageH > 0 ? pageH - v[2] : v[1];
            float y1 = pageH > 0 ? pageH - v[1] : v[2];
            edges.add(new Edge(false, v[0], y0, v[0], y1));
        }
        List<Table> tables = findTables(edges, glyphs, pageWidth);
        if (tables.isEmpty()) {
            tables = buildTables(rules, lines, pageWidth);
            tables.addAll(rowPass);
        }
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

        // Reading order by recursive whitespace cut (the XY-cut of pdfminer.six, MIT), not by
        // column index. Sorting by column is what put a question paper's questions out of
        // order: the gap after "1a." looked like a column boundary.
        // The cut is applied to the prose, not to the tables: a table is one block with its own
        // internal order, and letting the cut move it away from its heading broke documents
        // that were right. Tables keep their place by vertical position; the prose around them
        // is cut so a two- or three-column page reads down one column and then the next.
        List<Object> prose = new ArrayList<>();
        for (Object o : ordered) if (o instanceof Para) prose.add(o);
        List<Object> cut = new ArrayList<>();
        // Only a page that actually has columns needs the cut. On a single-column page the old
        // top-to-bottom order is already right, and cutting there separated a heading from the
        // line under it.
        if (bands > 1) xyCut(prose, cut, 8f); else cut.addAll(prose);
        List<Object> reordered = new ArrayList<>();
        List<Table> pending = new ArrayList<>();
        for (Object o : ordered) if (o instanceof Table) pending.add((Table) o);
        Collections.sort(pending, new Comparator<Table>() {
            @Override
            public int compare(Table a, Table b) { return Float.compare(a.top, b.top); }
        });
        int ti = 0;
        for (Object o : cut) {
            while (ti < pending.size() && pending.get(ti).top <= topOf(o)) {
                reordered.add(pending.get(ti++));
            }
            reordered.add(o);
        }
        while (ti < pending.size()) reordered.add(pending.get(ti++));
        ordered = reordered;

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

    /**
     * Puts a baseline's glyphs in reading order without breaking a run apart.
     *
     * <p>Sorting every glyph by x interleaves runs that overlap - text that runs past its cell
     * and a label that starts inside it become one nonsense word. A run is a sequence drawn
     * left to right without overlap; runs are ordered by where they start.
     */
    private static void orderRuns(List<Glyph> glyphs) {
        if (glyphs.size() < 2) return;
        List<List<Glyph>> runs = new ArrayList<>();
        List<Glyph> run = new ArrayList<>();
        Glyph prev = null;
        for (Glyph g : glyphs) {
            if (prev != null && g.x < prev.x + prev.width - 0.5f) {
                runs.add(run);
                run = new ArrayList<>();
            }
            run.add(g);
            prev = g;
        }
        if (!run.isEmpty()) runs.add(run);
        if (runs.size() == 1) return;

        Collections.sort(runs, new Comparator<List<Glyph>>() {
            @Override
            public int compare(List<Glyph> a, List<Glyph> b) {
                return Float.compare(a.get(0).x, b.get(0).x);
            }
        });
        glyphs.clear();
        for (List<Glyph> r : runs) glyphs.addAll(r);
    }

    private static List<Line> toLines(List<Glyph> glyphs, List<float[]> gutters) {
        List<Glyph> sorted = new ArrayList<>(glyphs);
        // Sort by baseline only. Collections.sort is stable, so glyphs drawn on the same
        // baseline stay in the order the page drew them - which is what keeps two overlapping
        // runs whole. Sorting by x here interleaved them: a value that ran past its cell and a
        // label that began inside it came out as "56M0o0b6i7le".
        Collections.sort(sorted, new Comparator<Glyph>() {
            @Override
            public int compare(Glyph a, Glyph b) {
                return Float.compare(a.y, b.y);
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
            orderRuns(raw.glyphs);
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
                // A gap is a space. A negative gap means the next run starts inside the last
                // one - text that ran past its cell - and the two must not be welded together.
                if ((gap > g.size * 0.18f || gap < -g.size * 0.6f) && !endsWithSpace(sb)) {
                    sb.append(' ');
                }
            }
            sb.append(g.text);
            prev = g;
        }
        return logicalOrder(sb.toString());
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
    /** True when the line has a wide gap right where [at] falls - it is two columns in one row. */
    private static boolean splitAt(Line line, float at) {
        Glyph prev = null;
        for (Glyph g : line.glyphs) {
            if (prev != null) {
                float gap = g.x - (prev.x + prev.width);
                float limit = Math.max(12f, Math.max(g.size, prev.size) * 1.6f);
                if (gap > limit && prev.x + prev.width <= at + 2f && g.x >= at - 2f) return true;
            }
            prev = g;
        }
        return false;
    }


    /**
     * Reading order by recursive whitespace cut - the XY-cut of pdfminer.six (MIT).
     *
     * <p>Two columns are not "column index then y": that is what put a question paper's
     * questions out of order. A page is cut at its widest empty strip, each half is cut again,
     * and the pieces come out in the order a reader takes them - down a column, then the next.
     */
    private static void xyCut(List<Object> items, List<Object> out, float minGap) {
        if (items.size() <= 1) {
            out.addAll(items);
            return;
        }
        // widest vertical gap (a column boundary)
        List<Object> byX = new ArrayList<>(items);
        Collections.sort(byX, new Comparator<Object>() {
            @Override
            public int compare(Object a, Object b) { return Float.compare(leftOf(a), leftOf(b)); }
        });
        float bestV = 0f;
        int bestVi = -1;
        float runRight = rightOf(byX.get(0));
        for (int i = 1; i < byX.size(); i++) {
            float gap = leftOf(byX.get(i)) - runRight;
            if (gap > bestV) { bestV = gap; bestVi = i; }
            runRight = Math.max(runRight, rightOf(byX.get(i)));
        }
        // widest horizontal gap (a block boundary)
        List<Object> byY = new ArrayList<>(items);
        Collections.sort(byY, new Comparator<Object>() {
            @Override
            public int compare(Object a, Object b) { return Float.compare(topOf(a), topOf(b)); }
        });
        float bestH = 0f;
        int bestHi = -1;
        float runBottom = bottomOf(byY.get(0));
        for (int i = 1; i < byY.size(); i++) {
            float gap = topOf(byY.get(i)) - runBottom;
            if (gap > bestH) { bestH = gap; bestHi = i; }
            runBottom = Math.max(runBottom, bottomOf(byY.get(i)));
        }

        // A cut is only a cut if the two sides sit beside each other. Two blocks stacked one
        // above the other can have disjoint x-ranges and would look like a column boundary;
        // cutting there swapped a heading with the line under it. The sides must overlap on the
        // other axis for the cut to mean anything.
        boolean vValid = false, hValid = false;
        if (bestVi > 0) {
            float aTop = Float.MAX_VALUE, aBot = -Float.MAX_VALUE;
            for (int i = 0; i < bestVi; i++) {
                aTop = Math.min(aTop, topOf(byX.get(i)));
                aBot = Math.max(aBot, bottomOf(byX.get(i)));
            }
            float bTop = Float.MAX_VALUE, bBot = -Float.MAX_VALUE;
            for (int i = bestVi; i < byX.size(); i++) {
                bTop = Math.min(bTop, topOf(byX.get(i)));
                bBot = Math.max(bBot, bottomOf(byX.get(i)));
            }
            float overlap = Math.min(aBot, bBot) - Math.max(aTop, bTop);
            float smaller = Math.min(aBot - aTop, bBot - bTop);
            vValid = smaller <= 0 || overlap >= smaller * 0.3f;
        }
        if (bestHi > 0) {
            float aL = Float.MAX_VALUE, aR = -Float.MAX_VALUE;
            for (int i = 0; i < bestHi; i++) {
                aL = Math.min(aL, leftOf(byY.get(i)));
                aR = Math.max(aR, rightOf(byY.get(i)));
            }
            float bL = Float.MAX_VALUE, bR = -Float.MAX_VALUE;
            for (int i = bestHi; i < byY.size(); i++) {
                bL = Math.min(bL, leftOf(byY.get(i)));
                bR = Math.max(bR, rightOf(byY.get(i)));
            }
            float overlap = Math.min(aR, bR) - Math.max(aL, bL);
            float smaller = Math.min(aR - aL, bR - bL);
            hValid = smaller <= 0 || overlap >= smaller * 0.3f;
        }

        // Prefer the column cut: a page is more often read down a column than split across.
        // A horizontal cut needs a clearly wider gap, or it separates a paragraph from its own
        // next line and the text comes out in the wrong order.
        float horizontalFloor = minGap * 1.6f;
        boolean cutVertically = vValid && bestV >= minGap && bestVi > 0
                && (bestH < horizontalFloor || bestV >= bestH || !hValid);
        if (cutVertically) {
            xyCut(new ArrayList<>(byX.subList(0, bestVi)), out, minGap);   // left first
            xyCut(new ArrayList<>(byX.subList(bestVi, byX.size())), out, minGap);
        } else if (hValid && bestH >= horizontalFloor && bestHi > 0) {
            xyCut(new ArrayList<>(byY.subList(0, bestHi)), out, minGap);   // top first
            xyCut(new ArrayList<>(byY.subList(bestHi, byY.size())), out, minGap);
        } else {
            // nothing to cut: read down, then across
            out.addAll(byY);
        }
    }

    private static float leftOf(Object o) {
        return o instanceof Para ? ((Para) o).left : ((Table) o).left;
    }

    private static float rightOf(Object o) {
        return o instanceof Para ? ((Para) o).right : ((Table) o).right;
    }

    private static float bottomOf(Object o) {
        return o instanceof Para ? ((Para) o).top : ((Table) o).bottom;
    }

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

        // A real column boundary is one that many lines share. A single wide space inside one
        // cell is not a column: on the salary slip and the simple table that turned 4 columns
        // into 6, because one cell happened to contain a wide gap.
        Map<Integer, Integer> support = new HashMap<>();
        for (Line line : lines) {
            if (line.text.trim().isEmpty()) continue;
            // one vote per line per boundary, however many glyphs that line has there
            java.util.HashSet<Integer> voted = new java.util.HashSet<>();
            for (Glyph g : line.glyphs) {
                int key = Math.round(g.x);
                if (!voted.add(key)) continue;
                Integer have = support.get(key);
                support.put(key, have == null ? 1 : have + 1);
            }
        }
        // A column boundary has to be shared by a good part of the page. Two lines are not
        // enough: a single wide space inside one cell produced the extra columns on the salary
        // slip and the simple table. A quarter of the lines is a column; two lines is a gap.
        int need = Math.max(3, Math.round(lines.size() * 0.25f));
        List<Float> kept = new ArrayList<>();
        for (Float c : candidates) {
            int key = Math.round(c);
            int seen = 0;
            for (int dx = -3; dx <= 3; dx++) {
                Integer v = support.get(key + dx);
                if (v != null && v > seen) seen = v;
            }
            if (seen >= need) kept.add(c);
        }
        candidates = kept;
        if (candidates.size() < 2) return new ArrayList<>();

        Collections.sort(candidates);

        // A column has to be a column's width. The marks on a question paper sit in a 44 pt
        // strip at the right margin; treating that as a column moved every "[08]" to the end of
        // the page instead of leaving it beside its question.
        float contentLeft = Float.MAX_VALUE, contentRight = -Float.MAX_VALUE;
        for (Line line : lines) {
            if (line.text.trim().isEmpty()) continue;
            contentLeft = Math.min(contentLeft, line.x);
            contentRight = Math.max(contentRight, line.right);
        }
        float minColumnWidth = (contentRight - contentLeft) * 0.12f;

        List<Float> starts = new ArrayList<>();
        float lastBoundary = contentLeft;
        int i = 0;
        while (i < candidates.size()) {
            int j = i;
            float sum = 0;
            while (j < candidates.size() && candidates.get(j) - candidates.get(i) <= 6f) {
                sum += candidates.get(j);
                j++;
            }
            int count = j - i;
            if (count >= 3) {
                float at = sum / count;
                // Three lines agreeing on a gap is not enough. In a question paper the gap
                // after "1a." agrees with the gap after "2a." and so on, and the page was split
                // into columns at the start of every question's text - the questions then came
                // out grouped by that x instead of in reading order.
                //
                // A real column boundary is a place no text crosses: the left column stops
                // before it and the right column starts after it. A handful of crossings is
                // allowed, because a title spanning both columns is normal.
                int crossings = 0;
                for (Line other : lines) {
                    if (other.text.trim().isEmpty()) continue;
                    if (other.x >= at - 2f || other.right <= at + 2f) continue;
                    // A line that is itself split at this point is a two-column row, not prose
                    // running through the gutter - it is the evidence for the column, not
                    // against it.
                    if (splitAt(other, at)) continue;
                    crossings++;
                }
                boolean wideEnough = at - lastBoundary >= minColumnWidth
                        && contentRight - at >= minColumnWidth;
                if (crossings <= Math.max(1, (int) (lines.size() * 0.12f)) && wideEnough) {
                    starts.add(at);
                    lastBoundary = at;
                }
            }
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

    /** Characters that begin a list item. */
    private static boolean startsWithBullet(String text) {
        String t = text.trim();
        if (t.isEmpty()) return false;
        char c = t.charAt(0);
        return c == '\u2022' || c == '\u25e6' || c == '\u25aa' || c == '\u25ab'
                || c == '\u2023' || c == '\u00b7' || c == '\u2043';
    }

    private static boolean sameParagraph(Line prev, Line next, float pageWidth) {
        if (prev.column != next.column) return false;
        // A bullet starts its own item. Its glyph is often set larger than the words beside
        // it, which made the alignment test pass and swallowed three advice lines into one.
        if (startsWithBullet(next.text)) return false;
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
        float l = Float.MAX_VALUE, r = -Float.MAX_VALUE;
        for (Line ln : group) { l = Math.min(l, ln.x); r = Math.max(r, ln.right); }
        Para p = new Para();
        p.left = l;
        p.right = r;
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
    // ---------------------------------------------------------------- tables
    // Ported from pdfplumber's table.py (MIT). The algorithm is theirs, line for line:
    // snap edges, join collinear edges, find intersections, read cells off the intersections,
    // group touching cells into tables. Nothing here is invented.

    private static final float SNAP_TOL = 3f;
    private static final float JOIN_TOL = 3f;
    private static final float EDGE_MIN = 3f;
    private static final float ISECT_TOL = 3f;

    /** One drawn edge. A horizontal edge has top == bottom; a vertical one has left == right. */
    private static final class Edge {
        boolean horizontal;
        float x0, top, x1, bottom;
        Edge(boolean horizontal, float x0, float top, float x1, float bottom) {
            this.horizontal = horizontal; this.x0 = x0; this.top = top; this.x1 = x1; this.bottom = bottom;
        }
    }

    /**
     * Snap edges that lie within a tolerance of each other to their average.
     *
     * <p>Clusters are built by comparing each edge with the one before it, not with the start
     * of the cluster - that is what pdfplumber's cluster_objects does, and it is why a run of
     * edges at 100, 102, 104 is one cluster and not two. Comparing with the cluster start split
     * such runs, which left extra vertical edges and extra empty columns.
     */
    private static List<Edge> snapEdges(List<Edge> edges, float xtol, float ytol) {
        List<Edge> out = new ArrayList<>();
        for (boolean horiz : new boolean[]{false, true}) {
            List<Edge> group = new ArrayList<>();
            for (Edge e : edges) if (e.horizontal == horiz) group.add(e);
            if (group.isEmpty()) continue;
            group.sort(new Comparator<Edge>() {
                @Override public int compare(Edge a, Edge b) {
                    return Float.compare(horiz ? a.top : a.x0, horiz ? b.top : b.x0);
                }
            });
            float tol = horiz ? ytol : xtol;
            List<List<Edge>> clusters = new ArrayList<>();
            List<Edge> current = new ArrayList<>();
            float prev = 0f;
            boolean first = true;
            for (Edge e : group) {
                float v = horiz ? e.top : e.x0;
                if (first || Math.abs(v - prev) <= tol) {
                    current.add(e);
                } else {
                    clusters.add(current);
                    current = new ArrayList<>();
                    current.add(e);
                }
                prev = v;
                first = false;
            }
            if (!current.isEmpty()) clusters.add(current);
            for (List<Edge> cluster : clusters) {
                float sum = 0f;
                for (Edge e : cluster) sum += horiz ? e.top : e.x0;
                float avg = sum / cluster.size();
                for (Edge e : cluster) {
                    if (horiz) out.add(new Edge(true, e.x0, avg, e.x1, avg));
                    else out.add(new Edge(false, avg, e.top, avg, e.bottom));
                }
            }
        }
        return out;
    }

    /** Join edges that sit on the same line and overlap or nearly touch. */
    private static List<Edge> joinEdgeGroup(List<Edge> edges, boolean horizontal, float tol) {
        if (edges.isEmpty()) return edges;
        List<Edge> sorted = new ArrayList<>(edges);
        final boolean h = horizontal;
        sorted.sort(new Comparator<Edge>() {
            @Override public int compare(Edge a, Edge b) {
                return Float.compare(h ? a.x0 : a.top, h ? b.x0 : b.top);
            }
        });
        List<Edge> joined = new ArrayList<>();
        joined.add(sorted.get(0));
        for (int i = 1; i < sorted.size(); i++) {
            Edge e = sorted.get(i);
            Edge last = joined.get(joined.size() - 1);
            float eMin = h ? e.x0 : e.top, eMax = h ? e.x1 : e.bottom;
            float lMax = h ? last.x1 : last.bottom;
            if (eMin <= lMax + tol) {
                if (eMax > lMax) {
                    joined.set(joined.size() - 1, h
                            ? new Edge(true, last.x0, last.top, eMax, last.top)
                            : new Edge(false, last.x0, last.top, last.x0, eMax));
                }
            } else {
                joined.add(e);
            }
        }
        return joined;
    }

    /** Snap, then join every group of collinear edges. */
    private static List<Edge> mergeEdges(List<Edge> edges) {
        List<Edge> snapped = snapEdges(edges, SNAP_TOL, SNAP_TOL);
        List<Edge> out = new ArrayList<>();
        for (boolean horiz : new boolean[]{true, false}) {
            Map<Integer, List<Edge>> groups = new HashMap<>();
            for (Edge e : snapped) {
                if (e.horizontal != horiz) continue;
                int key = Math.round(horiz ? e.top : e.x0);
                groups.computeIfAbsent(key, k -> new ArrayList<>()).add(e);
            }
            List<Integer> keys = new ArrayList<>(groups.keySet());
            Collections.sort(keys);
            for (Integer k : keys) out.addAll(joinEdgeGroup(groups.get(k), horiz, JOIN_TOL));
        }
        return out;
    }

    /** A point keyed by value: arrays would hash by identity and never match. */
    private static long pointKey(float x, float y) {
        return ((long) Math.round(x) << 32) | (Math.round(y) & 0xffffffffL);
    }

    private static float keyX(long key) { return (float) (key >> 32); }

    private static float keyY(long key) { return (float) (int) (key & 0xffffffffL); }

    /** Points where a vertical and a horizontal edge meet, with the edges touching each point. */
    private static Map<Long, List<Edge>[]> edgesToIntersections(List<Edge> edges) {
        List<Edge> vs = new ArrayList<>(), hs = new ArrayList<>();
        for (Edge e : edges) (e.horizontal ? hs : vs).add(e);
        Map<Long, List<Edge>[]> out = new HashMap<>();
        for (Edge v : vs) {
            for (Edge h : hs) {
                if (v.top <= h.top + ISECT_TOL && v.bottom >= h.top - ISECT_TOL
                        && v.x0 >= h.x0 - ISECT_TOL && v.x0 <= h.x1 + ISECT_TOL) {
                    long key = pointKey(v.x0, h.top);
                    List<Edge>[] slot = out.get(key);
                    if (slot == null) {
                        slot = new List[]{new ArrayList<Edge>(), new ArrayList<Edge>()};
                        out.put(key, slot);
                    }
                    slot[0].add(v);
                    slot[1].add(h);
                }
            }
        }
        return out;
    }

    /** Does an edge join the two intersection points? */
    private static boolean edgeConnects(Map<Long, List<Edge>[]> isect, long p1, long p2) {
        List<Edge>[] a = isect.get(p1), b = isect.get(p2);
        if (a == null || b == null) return false;
        if (keyX(p1) == keyX(p2)) {
            for (Edge x : a[0]) for (Edge y : b[0]) if (sameEdge(x, y)) return true;
        }
        if (keyY(p1) == keyY(p2)) {
            for (Edge x : a[1]) for (Edge y : b[1]) if (sameEdge(x, y)) return true;
        }
        return false;
    }

    private static boolean sameEdge(Edge a, Edge b) {
        return a.horizontal == b.horizontal
                && Math.abs(a.x0 - b.x0) < 0.5f && Math.abs(a.top - b.top) < 0.5f
                && Math.abs(a.x1 - b.x1) < 0.5f && Math.abs(a.bottom - b.bottom) < 0.5f;
    }

    /** Read the rectangular cells off the intersections. */
    private static List<float[]> intersectionsToCells(Map<Long, List<Edge>[]> isect) {
        List<Long> points = new ArrayList<>(isect.keySet());
        Collections.sort(points);
        List<float[]> cells = new ArrayList<>();
        for (int i = 0; i < points.size(); i++) {
            long pt = points.get(i);
            float px = keyX(pt), py = keyY(pt);
            List<Long> below = new ArrayList<>(), right = new ArrayList<>();
            for (int j = i + 1; j < points.size(); j++) {
                long q = points.get(j);
                if (keyX(q) == px) below.add(q);
                if (keyY(q) == py) right.add(q);
            }
            boolean found = false;
            for (Long bp : below) {
                if (!edgeConnects(isect, pt, bp)) continue;
                for (Long rp : right) {
                    if (!edgeConnects(isect, pt, rp)) continue;
                    long br = pointKey(keyX(rp), keyY(bp));
                    if (isect.containsKey(br) && edgeConnects(isect, br, rp) && edgeConnects(isect, br, bp)) {
                        cells.add(new float[]{px, py, keyX(rp), keyY(bp)});
                        found = true;
                        break;
                    }
                }
                if (found) break;
            }
        }
        return cells;
    }

    /** Group cells that touch at a corner into tables. */
    private static List<List<float[]>> cellsToTables(List<float[]> cells) {
        List<float[]> remaining = new ArrayList<>(cells);
        List<List<float[]>> tables = new ArrayList<>();
        List<float[]> current = new ArrayList<>();
        java.util.HashSet<String> corners = new java.util.HashSet<>();
        while (!remaining.isEmpty()) {
            int before = current.size();
            for (float[] cell : new ArrayList<>(remaining)) {
                String[] cs = {
                        cell[0] + "," + cell[1], cell[0] + "," + cell[3],
                        cell[2] + "," + cell[1], cell[2] + "," + cell[3]};
                if (current.isEmpty()) {
                    for (String c : cs) corners.add(c);
                    current.add(cell);
                    remaining.remove(cell);
                } else {
                    int shared = 0;
                    for (String c : cs) if (corners.contains(c)) shared++;
                    if (shared > 0) {
                        for (String c : cs) corners.add(c);
                        current.add(cell);
                        remaining.remove(cell);
                    }
                }
            }
            if (current.size() == before) {
                tables.add(new ArrayList<>(current));
                corners.clear();
                current.clear();
            }
        }
        if (!current.isEmpty()) tables.add(current);
        List<List<float[]>> kept = new ArrayList<>();
        for (List<float[]> t : tables) if (t.size() > 1) kept.add(t);
        return kept;
    }

    /** Build a Table from a group of cells, placing every glyph in the cell it falls in. */
    private static Table tableFromCells(List<float[]> group, List<Glyph> glyphs) {
        TreeSet<Float> colXs = new TreeSet<>(), rowYs = new TreeSet<>();
        for (float[] c : group) { colXs.add(c[0]); rowYs.add(c[1]); }
        List<Float> C = new ArrayList<>(colXs), R = new ArrayList<>(rowYs);
        int ncol = C.size(), nrow = R.size();
        if (ncol < 2 || nrow < 1) return null;

        List<List<List<Glyph>>> buckets = new ArrayList<>();
        for (int r = 0; r < nrow; r++) {
            List<List<Glyph>> row = new ArrayList<>();
            for (int c = 0; c < ncol; c++) row.add(new ArrayList<>());
            buckets.add(row);
        }
        for (Glyph g : glyphs) {
            float cx = g.x + g.width / 2f;
            float cy = g.y + g.size * 0.35f;
            float[] hit = null;
            for (float[] cell : group) {
                if (cx >= cell[0] - 2f && cx <= cell[2] + 2f
                        && cy >= cell[1] - 2f && cy <= cell[3] + 2f) { hit = cell; break; }
            }
            if (hit == null) continue;
            int ri = R.indexOf(hit[1]);
            int ci = C.indexOf(hit[0]);
            if (ri >= 0 && ci >= 0) buckets.get(ri).get(ci).add(g);
        }

        Table t = new Table();
        float top = Float.MAX_VALUE, bottom = -Float.MAX_VALUE;
        float left = Float.MAX_VALUE, right = -Float.MAX_VALUE;
        for (float[] c : group) {
            top = Math.min(top, c[1]); bottom = Math.max(bottom, c[3]);
            left = Math.min(left, c[0]); right = Math.max(right, c[2]);
        }
        t.top = top; t.bottom = bottom; t.left = left; t.right = right;
        t.header = nrow > 1;
        int filled = 0;
        for (int r = 0; r < nrow; r++) {
            List<String> row = new ArrayList<>();
            for (int c = 0; c < ncol; c++) {
                String str = glyphText(buckets.get(r).get(c));
                if (!str.isEmpty()) filled++;
                row.add(str);
            }
            t.rows.add(row);
        }
        // A QR code, a logo or a chart is drawn from the same rectangles a table is, so the
        // cells are real but the words are not there. A real table has text in a good share of
        // its cells; without this test a 21x21 QR code becomes a table and swallows the invoice.
        if (filled < Math.max(2, group.size() / 4)) return null;

        // If one cell's text runs straight into the next with no space and the next begins with
        // a small letter, the drawn grid is cutting through a word - "Strongly agree" became
        // "S | trongly agre | e". A table that breaks words is worse than no table, so the
        // caller falls back to the older pass for this page.
        for (List<String> row : t.rows) {
            for (int c = 0; c + 1 < row.size(); c++) {
                String cellL = row.get(c), cellR = row.get(c + 1);
                if (cellL.isEmpty() || cellR.isEmpty()) continue;
                char last = cellL.charAt(cellL.length() - 1);
                char first = cellR.charAt(0);
                if (Character.isLetter(last) && Character.isLowerCase(first)) return null;
            }
        }
        return t;
    }

    /** Join a cell's glyphs into one string, in reading order. */
    private static String glyphText(List<Glyph> gs) {
        if (gs.isEmpty()) return "";
        List<Glyph> sorted = new ArrayList<>(gs);
        Collections.sort(sorted, new Comparator<Glyph>() {
            @Override
            public int compare(Glyph a, Glyph b) {
                if (Math.abs(a.y - b.y) > 2f) return Float.compare(a.y, b.y);
                return Float.compare(a.x, b.x);
            }
        });
        StringBuilder sb = new StringBuilder();
        Glyph prev = null;
        for (Glyph g : sorted) {
            if (prev != null) {
                float gap = g.x - (prev.x + prev.width);
                if (gap > Math.max(1.5f, prev.size * 0.18f) && sb.length() > 0
                        && sb.charAt(sb.length() - 1) != ' ') sb.append(' ');
            }
            sb.append(g.text);
            prev = g;
        }
        return logicalOrder(sb.toString().trim());
    }

    /** All tables on a page, found the way pdfplumber finds them. */
    private static List<Table> findTables(List<Edge> rawEdges, List<Glyph> glyphs, float pageWidth) {
        List<Table> out = new ArrayList<>();
        List<Edge> edges = new ArrayList<>();
        for (Edge e : rawEdges) {
            float len = e.horizontal ? (e.x1 - e.x0) : (e.bottom - e.top);
            if (len >= EDGE_MIN) edges.add(e);
        }
        if (edges.size() < 4) return out;
        edges = mergeEdges(edges);
        Map<Long, List<Edge>[]> isect = edgesToIntersections(edges);
        if (isect.size() < 4) return out;
        List<float[]> cells = intersectionsToCells(isect);
        if (cells.size() < 2) return out;
        for (List<float[]> group : cellsToTables(cells)) {
            Table t = tableFromCells(group, glyphs);
            if (t == null) continue;
            float area = (t.right - t.left) * (t.bottom - t.top);
            if (pageWidth > 0 && area > pageWidth * pageWidth * 0.42f) continue;
            out.add(t);
        }
        return out;
    }

    /**
     * Tables drawn with lines, found one region at a time.
     *
     * <p>Collecting every rule on the page and clustering them globally turned a prescription
     * into a single thirty-column table: the page frame, a decorative header band and a
     * hand-drawn signature all contributed lines, and the real five-column table disappeared
     * inside it. A table is a region, so its rules are grouped first: horizontal rules that
     * share a horizontal extent are rows of one table, and only the vertical rules standing
     * inside that extent, tall enough to cross its rows, are its columns.
     */
    private static List<Table> buildTables(Rules rules, List<Line> lines, float pageWidth) {
        List<Table> out = new ArrayList<>();

        // Short segments are decoration, not edges: a signature squiggle is a hundred 2 pt
        // strokes, and every one of them used to become a column.
        List<float[]> hs = new ArrayList<>();
        List<float[]> vs = new ArrayList<>();
        for (float[] h : rules.horizontal) if (h[2] - h[1] >= 12f) hs.add(h);
        for (float[] v : rules.vertical) if (v[2] - v[1] >= 6f) vs.add(v);
        if (hs.size() < 2 || vs.size() < 2) return out;

        // Horizontal rules with the same extent are rows of the same table.
        List<List<float[]>> groups = new ArrayList<>();
        for (float[] h : hs) {
            List<float[]> target = null;
            for (List<float[]> g : groups) {
                float[] first = g.get(0);
                float overlap = Math.min(first[2], h[2]) - Math.max(first[1], h[1]);
                float shorter = Math.min(first[2] - first[1], h[2] - h[1]);
                if (shorter > 0 && overlap >= shorter * 0.6f) {
                    target = g;
                    break;
                }
            }
            if (target == null) {
                target = new ArrayList<>();
                groups.add(target);
            }
            target.add(h);
        }

        for (List<float[]> group : groups) {
            if (group.size() < 2) continue;

            float left = Float.MAX_VALUE, right = -Float.MAX_VALUE;
            for (float[] h : group) {
                left = Math.min(left, h[1]);
                right = Math.max(right, h[2]);
            }
            List<Float> ys = new ArrayList<>();
            for (float[] h : group) ys.add(h[0]);
            Collections.sort(ys);
            ys = mergeNear(ys, 1.6f);
            if (ys.size() < 2) continue;

            float top = ys.get(0), bottom = ys.get(ys.size() - 1);
            if (bottom - top < 12 || right - left < 30) continue;

            // Columns: the region's own edges, plus the vertical rules that stand inside it
            // and are tall enough to cross its rows.
            List<Float> xs = new ArrayList<>();
            xs.add(left);
            xs.add(right);
            for (float[] v : vs) {
                if (v[0] < left - 2f || v[0] > right + 2f) continue;
                float overlap = Math.min(v[2], bottom) - Math.max(v[1], top);
                if (overlap < (bottom - top) * 0.5f) continue;
                xs.add(v[0]);
            }
            Collections.sort(xs);
            xs = mergeNear(xs, 1.6f);

            int rows = ys.size() - 1, cols = xs.size() - 1;
            if (rows < 1 || cols < 2 || rows > 400 || cols > 40) continue;

            String[][] cells = new String[rows][cols];
            for (Line line : lines) {
                float cx = (line.x + line.right) / 2f;
                int r = band(ys, line.y);
                int c = band(xs, cx);
                if (r < 0 || c < 0) continue;
                cells[r][c] = cells[r][c] == null
                        ? line.text.trim() : cells[r][c] + " " + line.text.trim();
            }

            int filled = 0;
            for (String[] row : cells) for (String cell : row) if (cell != null) filled++;
            if (filled < 2) continue;                     // a box, not a table

            // A column nobody wrote in carries nothing but its separators. A drawing sheet's
            // frame produces a grid of six columns where four are always empty, and the output
            // was a page of "|  |  |  |" with the real text buried in it.
            List<Integer> keep = new ArrayList<>();
            for (int c = 0; c < cols; c++) {
                for (int r = 0; r < rows; r++) {
                    if (cells[r][c] != null) {
                        keep.add(c);
                        break;
                    }
                }
            }
            if (keep.size() < 2) continue;
            if (keep.size() < cols) {
                String[][] trimmed = new String[rows][keep.size()];
                for (int r = 0; r < rows; r++) {
                    for (int k = 0; k < keep.size(); k++) trimmed[r][k] = cells[r][keep.get(k)];
                }
                cells = trimmed;
                cols = keep.size();
            }

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
        }
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
            orderRuns(glyphs);
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
    /** Collapses positions closer together than [near] into one, keeping the first. */
    private static List<Float> mergeNear(List<Float> sorted, float near) {
        List<Float> out = new ArrayList<>();
        for (float v : sorted) {
            if (out.isEmpty() || v - out.get(out.size() - 1) > near) out.add(v);
        }
        return out;
    }

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


    /** True for the characters Arabic, Hebrew, Syriac and the presentation forms use. */
    private static boolean isRtl(char c) {
        // Digits are numbers, not letters: ١٢٠ is 120 and must not be mirrored into ٠٢١.
        if ((c >= 0x0660 && c <= 0x0669) || (c >= 0x06F0 && c <= 0x06F9)) return false;
        return (c >= 0x0590 && c <= 0x05FF)      // Hebrew
                || (c >= 0x0600 && c <= 0x06FF)  // Arabic
                || (c >= 0x0700 && c <= 0x074F)  // Syriac
                || (c >= 0x0750 && c <= 0x077F)  // Arabic supplement
                || (c >= 0x08A0 && c <= 0x08FF)  // Arabic extended-A
                || (c >= 0xFB1D && c <= 0xFDFF)  // Hebrew/Arabic presentation
                || (c >= 0xFE70 && c <= 0xFEFF); // Arabic presentation-B
    }

    /**
     * A right-to-left line comes out of the PDF in visual order - the last letter first - which
     * reads as mirror writing. Reversing the whole line gives logical order, and each run of
     * Latin letters or digits is then turned back so numbers still read left to right.
     */
    private static String logicalOrder(String text) {
        int rtl = 0, ltr = 0;
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (isRtl(c)) rtl++;
            else if (Character.isLetter(c)) ltr++;
        }
        if (rtl <= ltr || rtl == 0) return text;          // not an RTL line

        StringBuilder sb = new StringBuilder(text).reverse();
        int i = 0;
        while (i < sb.length()) {
            if (isRtl(sb.charAt(i))) { i++; continue; }
            int j = i;
            while (j < sb.length() && !isRtl(sb.charAt(j))) j++;
            // a run of non-RTL characters: reverse it back so "2024" stays "2024"
            String run = sb.substring(i, j);
            if (run.trim().length() > 0) {
                sb.replace(i, j, new StringBuilder(run).reverse().toString());
            }
            i = j;
        }
        return sb.toString();
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
