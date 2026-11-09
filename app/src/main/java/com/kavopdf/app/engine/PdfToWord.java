package com.kavopdf.app.engine;

import com.tom_roush.pdfbox.contentstream.PDFGraphicsStreamEngine;
import com.tom_roush.pdfbox.contentstream.operator.Operator;
import com.tom_roush.pdfbox.cos.COSArray;
import com.tom_roush.pdfbox.cos.COSBase;
import com.tom_roush.pdfbox.cos.COSDictionary;
import com.tom_roush.pdfbox.cos.COSName;
import com.tom_roush.pdfbox.cos.COSString;
import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.pdmodel.PDPage;
import com.tom_roush.pdfbox.pdmodel.PDResources;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDFont;
import com.tom_roush.pdfbox.pdmodel.graphics.form.PDFormXObject;
import com.tom_roush.pdfbox.pdmodel.graphics.form.PDTransparencyGroup;
import com.tom_roush.pdfbox.pdmodel.graphics.color.PDColor;
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
        /** The typeface the PDF used, as it names it. Empty when the page did not say. */
        public final String font;
        /** 0xRRGGBB, or -1 when the page draws this run in the default black. */
        public final int color;

        Run(String text, boolean bold, boolean italic, float sizePt) {
            this(text, bold, italic, sizePt, "", -1);
        }

        Run(String text, boolean bold, boolean italic, float sizePt, String font, int color) {
            this.text = text;
            this.bold = bold;
            this.italic = italic;
            this.sizePt = sizePt;
            this.font = font == null ? "" : font;
            this.color = color;
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
        /**
         * True when every line of this paragraph was drawn on a non-horizontal baseline - a
         * stamp, a watermark. It is an overlay rather than part of the page's text, so it is
         * read after the page's own words.
         */
        public boolean stamp;
        public int column;           // which column band it sits in
        /** The lines the PDF actually drew, in order. A .txt has no paragraph concept, so the
         *  plain-text output keeps them instead of hard-wrapping a paragraph back into lines
         *  at a width the reader never saw. */
        public final List<String> lines = new ArrayList<>();
        /**
         * The x, y and size of each entry in {@link #lines}, in the same order.
         *
         * <p>These exist for one reason: a .txt has no coordinates, so a line's position has to
         * be rebuilt as leading spaces and blank lines at write time. Keeping the raw numbers
         * here means that work happens in writeTxt() and nowhere else - the .docx path reads
         * {@link #runs} and never touches any of these, so the document output cannot change.
         */
        public final List<Float> lineX = new ArrayList<>();
        public final List<Float> lineY = new ArrayList<>();
        public final List<Float> lineSize = new ArrayList<>();
        /**
         * The same lines, with the coordinates the page actually used.
         *
         * <p>{@link #runs} is one run holding the whole paragraph, which is all a .txt or a
         * flowed .docx can use. That is why the Word file used to put every paragraph at a
         * single indent: a value set at x=300 in the PDF reached the .docx as "indent 4".
         * Each {@link Box} is one drawn line and carries the x, the baseline y and the runs
         * with their own typeface, size and colour, so the writer can put the text back where
         * it was. Empty for paragraphs that were never on a page grid - an OCR block, an
         * annotation, a filled form value.
         */
        public final List<Box> boxes = new ArrayList<>();

        public String text() {
            StringBuilder sb = new StringBuilder();
            for (Run r : runs) sb.append(r.text);
            return sb.toString();
        }

        public float size() {
            return runs.isEmpty() ? 0f : runs.get(0).sizePt;
        }
    }

    /**
     * One line as the page drew it: where it starts, how wide it is, and the runs on it.
     *
     * <p>x and right are points from the left edge of the page, y is points from the TOP
     * edge - the same convention {@code Glyph} and {@code Line} use.
     */
    public static final class Box {
        public float x, y, right, size;
        /** Bottom edge of the line's box on the page, y down. */
        public float bottom;
        /** The line's extent along its own baseline - the width a text box needs. */
        public float length;
        /** True when the line was drawn on a non-horizontal baseline. */
        public boolean rotated;
        /** The baseline's angle in degrees, clockwise. */
        public float angle;
        public final List<Run> runs = new ArrayList<>();

        public String text() {
            StringBuilder sb = new StringBuilder();
            for (Run r : runs) sb.append(r.text);
            return sb.toString();
        }
    }

    /** A table, as the cells a reader sees. */
    public static final class Table {
        public final List<List<String>> rows = new ArrayList<>();
        /**
         * The x of every column edge, left to right, in points - one more entry than there are
         * columns. Null when the pass that built the table did not know them, in which case the
         * writer splits the width evenly.
         *
         * <p>Without this a five-column invoice reached Word as five equal columns: the table
         * started in the right place and every figure inside it was at the wrong x.
         */
        public float[] colX;
        /**
         * The x, in points, at which each cell's own text starts - same shape as {@link #rows},
         * {@link Float#NaN} where the pass did not measure it.
         *
         * <p>A cell's text does not begin at its left border. In the batch the distance is 6 pt
         * on a left-aligned cell (the generator's own cell padding), half the slack on a centred
         * cell - the timetable's period columns are centred, 27.12 pt in - and whatever the
         * string's own width leaves on a right-aligned amount. It also varies row by row in one
         * column, which no single cell margin can express. Recording where the text was drawn
         * is the only description that covers all three.
         */
        public final List<List<Float>> cellX = new ArrayList<>();
        /**
         * The x, in points, of the RIGHT edge of each cell's text - same shape as
         * {@link #rows}, {@link Float#NaN} where the pass did not measure it.
         *
         * <p>Where a cell's text starts is not enough to lay it out: a column can be narrower
         * than the words drawn in it, and then Word wraps them inside a 52 pt box - file 80's
         * dealer name came out as "SUNRISE / FASTENE / RS PVT / LTD". With the measured right
         * edge the writer can widen that cell over the empty cells beside it, which is what
         * the page did, instead of re-wrapping a line the page never wrapped.
         */
        public final List<List<Float>> cellR = new ArrayList<>();
        /** The typeface each cell was drawn in, same shape as {@link #rows}. */
        public final List<List<String>> fonts = new ArrayList<>();
        /**
         * The point size each cell's text was drawn at - same shape as {@link #rows},
         * {@link Float#NaN} where the pass did not measure it.
         *
         * <p>Without this every cell in every table was written at the paragraph style's own
         * 10 pt. A cell is a string, a face and a size, and the size was the one thing the
         * writer had no way to ask for: on file 22 the amounts are drawn at 8.5 pt and came
         * out 17.6 % wider than the page, which is enough to push "2,18,770.00" out of a
         * 45.15 pt column - the reader saw "2,18,770.0" with a lone "0" on the line below.
         */
        public final List<List<Float>> sizes = new ArrayList<>();
        /**
         * The colour each cell's text was drawn in (0xRRGGBB, -1 for the default black), same
         * shape as {@link #rows}. Without it every table cell reached Word in black: measured on
         * the corpus, 37 of the 98 colour pairs the page-level pass had already found correctly
         * were thrown away here, because a cell is written as a string and a font name.
         */
        public final List<List<Integer>> colors = new ArrayList<>();
        public boolean header;
        /**
         * Did the page draw the lines that make this a table?
         *
         * <p>Two passes build tables. The ruled pass reads the edges the page draws, so its
         * tables are ruled by construction. The row pass infers cells from whitespace alone -
         * a passport's field grid, a crossword's two clue columns - and on those pages the
         * page draws no line at all. The writer used to put a full single-line border on every
         * table whatever pass found it, so a whitespace table arrived with a box the page
         * never had: 11 rules on 403 where the page draws none, 19 on 406. A border is a claim
         * about the page, so it is only drawn where the page made one.
         */
        public boolean ruled = true;
        /**
         * Did the page draw the rules <em>inside</em> this table - the row separators
         * ({@code innerH}) and the column separators ({@code innerV}) - as opposed to only the
         * box around it?
         *
         * <p>A table the whitespace pass found has bounds that are its TEXT's ink, so the frame
         * the page draws round it is off those bounds and {@code DocxWriter.pageDrewRule} cannot
         * put it on the four outer sides without help. The rules inside the band can be read
         * here, where the page's own rule list is in hand. 04_stamp_180deg's fee table has five
         * row separators and no column separator; the student block above it has neither, only
         * the panel the page draws round it. Writing all six sides for both would draw four
         * lines the page never drew, so each side is decided on its own evidence.
         */
        public boolean innerH, innerV;
        /**
         * The stroke the page drew on each of the table's six sides, in
         * {@link DocxWriter#TABLE_SIDES} order - {@code {top, left, bottom, right, insideH,
         * insideV}} - each {@code {widthPt, rgb, alpha}}, or null where no rule this pass could
         * see lies on that side.
         *
         * <p>D-22. {@code w:tblBorders} carried one constant weight and one constant colour on
         * all six sides of every table (see {@code DocxWriter.borders}), so a table the page
         * ruled at 0.4 pt in grey came out at 1 pt in black and a table the page ruled at 2 pt
         * came out at 1 pt too. The user's words: some rules are thick, some thin, some dark,
         * some faint, and in the .docx they were all one weight and one colour. Each side now
         * carries the stroke of the rule that actually lies on it - filled by
         * {@code PdfToWord.markSideStrokes}, where the page's own rule list is in hand.
         *
         * <p>Null is not "undrawn": whether a side is drawn is still decided by {@link #ruled},
         * {@link #innerH} and {@link #innerV}. Null only means no rule of its own was read, and
         * {@code markSideStrokes} then lends it the stroke the table's other rules are drawn at;
         * a table with no rule at all leaves it null, and the writer falls back to the old
         * constant - so a side that used to be right stays right.
         */
        public final float[][] sideStroke = new float[6][];
        /**
         * The y of every row's top edge, in points, with one more entry than there are rows -
         * the last entry is the bottom edge of the last row. Null when the pass that built the
         * table did not know them.
         *
         * <p>The writer gave every row the table's extent divided by its row count, which is only
         * true of a table whose rows are evenly spaced. A ledger with a taller header, a wrapped
         * address or a merged cell does not have those, and every row below the odd one out then
         * sits a little further from the page than the row above it: 1.45 pt a row on
         * 16_right_aligned_amounts, 38 pt by the foot of the table, and it is why the error there
         * correlated with y. These are the page's own row edges, so each row can be given the
         * height the page gave it (D-26, cause 2).
         */
        public float[] rowEdge;
        /**
         * The y of the table's first row's TOP edge, in points, when the pass that built the
         * table could tell where that edge is ({@link Float#NaN} otherwise).
         *
         * <p>{@link #rowEdge} gives each row its own height, but its first entry is not always
         * the table's top: the grid pass reads a cell's rectangle, whose y is the rule BELOW the
         * row's text (on 16_right_aligned_amounts the first entry is 156 pt while the page's
         * first baseline is 148 and the row's top edge is 137). Placing the table from the first
         * entry therefore put it one pitch low. This is the edge the flow is placed against.
         */
        public float rowTopPt = Float.NaN;
        public float top, bottom, left, right;
        public int column;
    }

    public static final class Page {
        public int number;
        public final List<Object> blocks = new ArrayList<>();   // Para or Table
        public boolean ocr;
        /** The page box in points. A .docx section has to be told, or a landscape page comes
         *  out portrait and every x on it is measured against the wrong width. */
        public float width, height;
        /**
         * How many newspaper columns this page is set in - decided here, from the page's own
         * unsplit lines, because by the time the writer sees the blocks the page has already
         * been cut at the gutter and every band is half a page wide by construction.
         */
        public int columns = 1;
        /** The gutter between those columns, in points. */
        public float columnGap;
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
    static final boolean ROW = Boolean.getBoolean("p2w.row");
    /**
     * Splits a line where the next run starts inside the one before it.
     *
     * <p>A form draws its label and its value on one baseline, and on some of them the colon
     * after the label is placed over the label's own tail - x=65 while the label runs to 70.
     * Nothing separates them but the overlap, so the two were welded into one line. Measured
     * on the 80-document batch: file 21 goes 52.6 -> 100.0 on line order and 45.5 -> 100.0 on
     * exact, with ten files improved, none made worse, and file 46 - the chart labels, which
     * overlap by design - unchanged.
     */
    static final boolean OS = !"false".equals(System.getProperty("p2w.osplit"));
    static final float OVF = Float.parseFloat(System.getProperty("p2w.ovf", "0.6"));

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
                Page read = readPage(doc, i, hook, result.report);
                mergeClusterTails(read);
                result.pages.add(read);
            }
        }
        return result;
    }

    /**
     * Rejoins a paragraph that begins with a combining mark to the paragraph before it.
     *
     * <p>The converter cuts a drawn line wherever the typeface changes, and the cut can land
     * inside a grapheme cluster: file 78 draws "केवल" as one line, the cut fell between "क" and
     * "ेवल", and the two halves became two paragraphs - so Word started a text box with a lone
     * vowel sign and drew the dotted circle a mark without a consonant gets. "पंजीकृत" broke the
     * same way into "पंजीक" and "ृत".
     *
     * <p>A combining mark has no base of its own, so a paragraph that opens with one on the same
     * baseline as the paragraph before it is that paragraph's tail, not a line of the document.
     * Only text is joined - nothing is dropped, reordered or re-styled.
     */
    private static void mergeClusterTails(Page page) {
        for (int i = 1; i < page.blocks.size(); i++) {
            Object cur = page.blocks.get(i), prev = page.blocks.get(i - 1);
            if (!(cur instanceof Para) || !(prev instanceof Para)) continue;
            Para a = (Para) prev, b = (Para) cur;
            if (a.boxes.isEmpty() || b.boxes.isEmpty()) continue;
            Box tail = b.boxes.get(0);
            if (!startsWithCombiningMark(tail.text())) continue;
            Box last = a.boxes.get(a.boxes.size() - 1);
            if (Math.abs(last.y - tail.y) > Math.max(2f, tail.size * 0.5f)) continue;
            last.runs.addAll(tail.runs);
            last.right = Math.max(last.right, tail.right);
            last.bottom = Math.max(last.bottom, tail.bottom);
            last.length = last.right - last.x;
            b.boxes.remove(0);
            if (b.boxes.isEmpty()) {
                // The tail's own line still belongs in the plain-text output: joining the two
                // halves for Word must not remove a line from the .txt, which is what the text
                // metrics are read from. Measured when it did: char volume 99.91 -> 99.84 and
                // word recall 99.67 -> 99.60.
                a.lines.addAll(b.lines);
                page.blocks.remove(i);
                i--;
            }
        }
    }

    private static Page readPage(PDDocument doc, int index, OcrHook hook, Report report) {
        Page page = new Page();
        page.number = index + 1;
        PDPage pdPage = doc.getPage(index);
        // The page box, in points, is what a .docx section has to be told: without it a
        // landscape page comes out portrait and every x on it is measured against a width
        // the page never had. Measured on the 80-file batch: 77 A4 portrait, 2 A4 landscape
        // and one file that mixes the two across its pages.
        PDRectangle box = pdPage.getMediaBox();
        page.width = box.getWidth();
        page.height = box.getHeight();

        List<Glyph> glyphs = glyphsOf(doc, index);
        int chars = 0;
        for (Glyph g : glyphs) chars += g.text.length();

        // Read once, here: the images a page draws are needed by every path below, including
        // the one that has no text layer and returns early - a scanned page is nothing but one
        // image, and reading it only on the text path is how it came out blank.
        Rules rules = rulesOf(doc, index);
        report.images += rules.images;

        // A filled form keeps its answers in the field's /V, never in the content stream, so
        // they are read on every page - not only on a page with no text layer. Without this a
        // filled form converted to Word kept its printed labels and lost every answer.
        if (chars >= MIN_TEXT_CHARS) {
            StringBuilder pageText = new StringBuilder();
            for (Glyph g : glyphs) pageText.append(g.text);
            String flat = pageText.toString().replaceAll("\\s+", " ").toLowerCase(Locale.ROOT);
            // A stamp, a comment or a free-text box sits on a page that already has text, so
            // the annotation path below (which only runs on an empty page) never saw it: the
            // words "RECEIVED", "APPROVED" and every reviewer comment were dropped.
            List<String> outside = new ArrayList<>(formValuesOf(pdPage));
            outside.addAll(annotationContentsOf(pdPage));
            for (String v : outside) {
                // Some generators also draw the value into the content stream. Adding it again
                // would put the same words in twice, which is worse than not adding it.
                if (flat.contains(v.replaceAll("\\s+", " ").toLowerCase(Locale.ROOT))) continue;
                Para p = new Para();
                p.runs.add(new Run(v, false, false, 11f));
                p.top = 0;
                page.blocks.add(p);
                report.paragraphs++;
            }
        }

        if (chars < MIN_TEXT_CHARS) {
            // A page can carry its words in annotations rather than in its content stream - a
            // free-text box, a note, a comment, a highlight with a remark on it. That is still
            // text on the page, so it is read before falling back to OCR.
            String annotated = annotationTextOf(pdPage);
            boolean readAnnotations = false;
            if (!annotated.isEmpty()) {
                for (String block : annotated.split("\\n\\s*\\n")) {
                    String t = block.trim();
                    if (t.isEmpty()) continue;
                    Para p = new Para();
                    p.runs.add(new Run(t.replaceAll("\\s*\\n\\s*", " "), false, false, 11f));
                    p.top = 0;
                    page.blocks.add(p);
                    report.paragraphs++;
                }
                readAnnotations = true;
                report.notes.add("page " + (index + 1) + " has no text layer; read its annotations");
            }

            // No usable text layer. Either OCR it, or say plainly that it was not read.
            // Annotations already gave us the page's words: running OCR on top of that would
            // put the same text in twice.
            String ocrText = null;
            if (!readAnnotations && hook != null) {
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
            } else if (!readAnnotations) {
                // Only a page that produced nothing at all is skipped. A page read from its
                // annotations has text and must not be reported as empty.
                report.skippedPages++;
                report.notes.add("page " + (index + 1)
                        + " has no text layer and was not OCR'd - it comes out empty");
            }
            attachShapes(page, rules, page.height, null);
            attachPictures(page, rules, page.height);
            return page;
        }

        float pageWidth = pdPage.getMediaBox().getWidth();
        final float pageHeight = pdPage.getMediaBox().getHeight();
        List<Line> rawLines = toLines(glyphs, new ArrayList<float[]>());
        page.columns = proseColumns(rawLines, pageWidth);

        // Tables are found from the drawn rules, so they can be located before any line is
        // split. A column start that falls inside one is that table's cell separator, not a
        // page column - splitting there would tear every row apart.
        // The rules come out of the graphics engine with y measured up from the page bottom and
        // the lines carry y measured down from the top. buildTables compares the two, so it has
        // to be handed the rules in the lines' own frame. It was handed the raw ones: a rule at
        // PDF y=524 was matched against a line at y=268, and on the warehousing agreement the
        // schedule's rules were wrapped round two paragraphs of prose, which came out as a
        // two-column table with "2.2 Invoices shall be raised monthly and paid within 30 days of
        // receipt." squeezed into a 150 pt cell beside "3.1 ...".
        Rules topRules = flipY(rules, pageHeight);
        List<Table> firstPass = buildTables(topRules, rawLines, pageWidth);

        // Borderless tables are found here, before the column starts are filtered, so that a
        // table's cell positions are known to be cell separators. Otherwise the cells look
        // like page columns, and the heading above the table gets a later column than the
        // table itself - which puts the heading after the table in the output.
        List<Table> rowPass = rowTables(rawLines, firstPass, pageWidth);
        for (Table t : rowPass) markInnerRules(t, topRules);

        List<Float> starts = new ArrayList<>();
        for (Float x : columnStarts(rawLines)) {
            boolean inTable = false;
            for (Table t : firstPass) {
                if (!rowSane(t, rawLines)) continue;
                if (x >= t.left - 4 && x <= t.right + 4) { inTable = true; break; }
            }
            for (Table t : rowPass) {
                if (!rowSane(t, rawLines)) continue;
                if (x >= t.left - 4 && x <= t.right + 4) { inTable = true; break; }
            }
            if (!inTable) starts.add(x);
        }
        // A column can be evidenced two ways. The first is a line that spans the gutter - that
        // is what columnStarts finds. The second is a page where the columns are already
        // separate lines, so no line spans anything and columnStarts comes back empty: a
        // three-column newspaper page. Without this the page got no columns at all, the XY-cut
        // never ran, and the columns interleaved line by line.
        if (starts.isEmpty()) {
            List<Float> xs = new ArrayList<>();
            for (Line l : rawLines) if (!l.text.trim().isEmpty()) xs.add(l.x);
            Collections.sort(xs);
            if (xs.size() >= 8) {
                List<float[]> groups = new ArrayList<>();
                float gStart = xs.get(0), gEnd = xs.get(0);
                int gCount = 0;
                for (Float x : xs) {
                    if (x - gEnd > 24f) {
                        groups.add(new float[]{gStart, gEnd, gCount});
                        gStart = x; gCount = 0;
                    }
                    gEnd = x; gCount++;
                }
                groups.add(new float[]{gStart, gEnd, gCount});
                int need = Math.max(3, Math.round(xs.size() * 0.08f));
                List<Float> bounds = new ArrayList<>();
                for (int k = 1; k < groups.size(); k++) {
                    float[] left = groups.get(k - 1), right = groups.get(k);
                    if (left[2] < need || right[2] < need) continue;
                    bounds.add((left[1] + right[0]) / 2f);
                }
                if (bounds.size() >= 1 && bounds.size() <= 2) starts.addAll(bounds);
            }
        }
        // A gutter is an x-range that NO GLYPH on the page covers. Projecting every glyph's
        // extent is the only test that survives a fragmented layout: a headline drawn one word
        // per line still has glyphs that stop at the column edge, so the gap between the
        // columns stays empty even though ten different lines begin at ten different x values.
        // Projecting line extents fails there, and clustering line starts fails worse.
        if (glyphs.size() >= 40) {
            // A full-width headline or footer covers the gutter and hides it. Those lines are
            // not part of any column, so they are left out of the projection - the columns
            // underneath them are what we are trying to find.
            float contentLo = Float.MAX_VALUE, contentHi = -Float.MAX_VALUE;
            for (Line l : rawLines) {
                if (l.text.trim().isEmpty() || l.right <= l.x) continue;
                contentLo = Math.min(contentLo, l.x);
                contentHi = Math.max(contentHi, l.right);
            }
            float fullWidth = (contentHi - contentLo) * 0.62f;
            List<float[]> iv = new ArrayList<>();
            float lo = Float.MAX_VALUE, hi = -Float.MAX_VALUE;
            for (Line l : rawLines) {
                if (l.text.trim().isEmpty() || l.right - l.x > fullWidth) continue;
                for (Glyph g : l.glyphs) {
                    if (g.width <= 0 || g.text == null || g.text.trim().isEmpty()) continue;
                    iv.add(new float[]{g.x, g.x + g.width});
                    lo = Math.min(lo, g.x);
                    hi = Math.max(hi, g.x + g.width);
                }
            }
            // A pull quote, a footnote block or a section heading that spans both columns covers
            // the gutter, and one such block is enough to hide it from a whole-page projection.
            // Project each vertical band separately and keep a gutter that most bands agree on:
            // a spanning block only pollutes the bands it occupies.
            if (keep0(rawLines, fullWidth).isEmpty()) {
                float top = Float.MAX_VALUE, bot = -Float.MAX_VALUE;
                for (Line l : rawLines) {
                    if (l.text.trim().isEmpty()) continue;
                    top = Math.min(top, l.y);
                    bot = Math.max(bot, l.y);
                }
                int bandsN = 6;
                float bh = (bot - top) / bandsN;
                List<List<Float>> perBand = new ArrayList<>();
                if (bh > 8f) {
                    for (int b = 0; b < bandsN; b++) {
                        float y0 = top + b * bh, y1 = y0 + bh;
                        List<Line> sub = new ArrayList<>();
                        for (Line l : rawLines) if (l.y >= y0 && l.y < y1) sub.add(l);
                        if (sub.size() < 4) continue;
                        List<Float> g = keep0(sub, fullWidth);
                        if (g.size() == 1) perBand.add(g);
                    }
                }
                if (perBand.size() >= 2) {
                    List<Float> votes = new ArrayList<>();
                    for (List<Float> g : perBand) votes.add(g.get(0));
                    Collections.sort(votes);
                    float best = votes.get(0), bestN = 0;
                    for (float c : votes) {
                        int n = 0;
                        for (float v : votes) if (Math.abs(v - c) <= 6f) n++;
                        if (n > bestN) { bestN = n; best = c; }
                    }
                    if (bestN >= perBand.size() * 0.5f) {
                        starts.clear();
                        starts.add(best);
                    }
                }
            }

            if (iv.size() >= 40 && hi > lo) {
                Collections.sort(iv, new Comparator<float[]>() {
                    @Override
                    public int compare(float[] a, float[] b) { return Float.compare(a[0], b[0]); }
                });
                float span = hi - lo;
                List<float[]> gaps = new ArrayList<>();
                float reach = iv.get(0)[1];
                for (int i = 1; i < iv.size(); i++) {
                    float gs = iv.get(i)[0];
                    if (gs - reach > span * 0.015f) gaps.add(new float[]{reach, gs});
                    reach = Math.max(reach, iv.get(i)[1]);
                }
                // keep only gaps that leave real columns on both sides of them
                List<Float> keep = new ArrayList<>();
                for (float[] gp : gaps) {
                    float mid = (gp[0] + gp[1]) / 2f;
                    int left = 0, right = 0;
                    for (float[] v : iv) {
                        if (v[1] <= mid) left++;
                        else if (v[0] >= mid) right++;
                    }
                    if (left + right < iv.size() * 0.8f) continue;      // glyphs cross it
                    float ratio = Math.min(left, right) / (float) Math.max(left, right);
                    if (ratio < 0.30f) continue;                        // a margin, not a column
                    keep.add(mid);
                }
                // The glyph projection is the most reliable of the three detectors, so when it
                // finds a gutter it replaces what the other two guessed.
                if (keep.size() >= 1 && keep.size() <= 2) { starts.clear(); starts.addAll(keep); }
            }
        }
        if (Boolean.getBoolean("p2w.nocol")) starts.clear();
        // A gutter is not always empty space. A journal page separates its two columns with a
        // hairline rule and sets the text right up to it, so the projection above sees no gap
        // at all - the columns butt against the rule - and the page came out with no columns,
        // interleaving the two of them line by line. The rule itself is the evidence.
        if (!rules.vertical.isEmpty()) {
            float cLo = Float.MAX_VALUE, cHi = -Float.MAX_VALUE;
            for (Line l : rawLines) {
                if (l.text.trim().isEmpty() || l.right <= l.x) continue;
                cLo = Math.min(cLo, l.x);
                cHi = Math.max(cHi, l.right);
            }
            List<Float> ruleGutters = new ArrayList<>();
            for (float[] v : rules.vertical) {
                float len = Math.abs(v[2] - v[1]);
                if (len < pageHeight * 0.30f) continue;
                float x = v[0];
                if (x <= cLo + 60f || x >= cHi - 60f) continue;
                boolean inTable = false;
                for (Table t : firstPass) {
                    if (!rowSane(t, rawLines)) continue;
                    if (x >= t.left - 4 && x <= t.right + 4) { inTable = true; break; }
                }
                if (!inTable) ruleGutters.add(x);
            }
            if (ruleGutters.size() == 1) { starts.clear(); starts.add(ruleGutters.get(0)); }
            else if (ruleGutters.size() == 2 && starts.isEmpty()) {
                starts.clear(); starts.addAll(ruleGutters);
            }
        }
        // The page's column count is the number of bands the cut actually made, not the earlier
        // proseColumns() estimate.
        //
        // proseColumns() runs at the top of this method, before any of the three gutter
        // detectors below has finished - it clusters the raw lines' left edges and requires the
        // bands to be near-equal in width, so it answers 1 for a page whose columns are uneven
        // and for a page whose gutter is only visible to the glyph projection or to a vertical
        // rule. `starts` is the list the cut is really made from (asBands), so it is the only
        // honest answer to "how many columns is this page set in", and it is the one the writer
        // needs: it groups the page's blocks back into the bands they were cut out of, so a
        // count that disagrees with `starts` would put a block in the wrong cell.
        //
        // Capped at 4 because that is the widest newspaper grid the block pass is built for
        // (proseColumns refuses more), and a page that needed five would be a table.
        page.columns = starts.isEmpty() ? 1 : Math.min(4, starts.size() + 1);
        if (page.columns > 1 && !starts.isEmpty()) {
            float gLo = Float.MAX_VALUE;
            for (int k = 1; k < starts.size(); k++) gLo = Math.min(gLo, starts.get(k) - starts.get(k - 1));
            page.columnGap = gLo == Float.MAX_VALUE ? 0f : gLo;
        }
        uprightIfPageIsUpsideDown(glyphs);
        List<Line> lines = toLines(glyphs, asBands(starts));
        List<Line> ring = new ArrayList<>();
        for (java.util.Iterator<Line> it = lines.iterator(); it.hasNext(); ) {
            Line ln = it.next();
            if (ln.ring) { ring.add(ln); it.remove(); }
        }
        // The words inside the ring belong to the seal, not to the page's text: a round seal
        // carries its centre line - "SEAL", "TRAINING & PLACEMENT CELL", a year - inside the
        // circle it draws. They travel with the ring, in reading order, after its characters.
        if (ring.size() >= 8) {
            float rx0 = Float.MAX_VALUE, rx1 = -Float.MAX_VALUE;
            float ry0 = Float.MAX_VALUE, ry1 = -Float.MAX_VALUE;
            for (Line ln : ring) {
                rx0 = Math.min(rx0, ln.x);
                rx1 = Math.max(rx1, ln.right);
                ry0 = Math.min(ry0, ln.y);
                ry1 = Math.max(ry1, ln.y);
            }
            List<Line> inner = new ArrayList<>();
            for (java.util.Iterator<Line> it = lines.iterator(); it.hasNext(); ) {
                Line ln = it.next();
                float cx = (ln.x + ln.right) / 2f;
                if (cx > rx0 && cx < rx1 && ln.y > ry0 && ln.y < ry1) { inner.add(ln); it.remove(); }
            }
            Collections.sort(inner, new Comparator<Line>() {
                @Override
                public int compare(Line a, Line b) {
                    int c = Float.compare(a.y, b.y);
                    return c != 0 ? c : Float.compare(a.x, b.x);
                }
            });
            ring.addAll(inner);
        }

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
            tables = buildTables(topRules, lines, pageWidth);
        }
        // The row-based pass finds tables drawn without vertical rules - a bill of quantities,
        // a bank statement, an ITR schedule. It used to run only when the ruled pass found
        // NOTHING, so a page with one ruled table and one unruled table lost the second one
        // without a word: the tender document came out with its summary table and no BOQ.
        // It now always runs, and any table it finds that the ruled pass did not is added.
        for (Table cand : rowPass) {
            boolean known = false;
            for (Table t : tables) {
                float ox = Math.min(t.right, cand.right) - Math.max(t.left, cand.left);
                float oy = Math.min(t.bottom, cand.bottom) - Math.max(t.top, cand.top);
                if (ox > 0 && oy > 0) {
                    float inter = ox * oy;
                    float smaller = Math.min((t.right - t.left) * (t.bottom - t.top),
                                             (cand.right - cand.left) * (cand.bottom - cand.top));
                    if (smaller > 0 && inter / smaller >= 0.5f) { known = true; break; }
                }
            }
            if (!known) tables.add(cand);
        }
        // A form drawn round everything can swallow a real table inside it. The bill of lading
        // came out twice for exactly this reason: one big table for the whole form and one for
        // the marks grid. The outer box is dropped and the inner tables are kept.
        List<Table> keepTables = new ArrayList<>();
        for (Table a : tables) {
            boolean containsAnother = false;
            for (Table b : tables) {
                if (a == b) continue;
                boolean inside = b.left >= a.left - 4 && b.right <= a.right + 4
                        && b.top >= a.top - 4 && b.bottom <= a.bottom + 4;
                boolean smaller = (b.right - b.left) * (b.bottom - b.top)
                        < (a.right - a.left) * (a.bottom - a.top) * 0.9f;
                if (inside && smaller) { containsAnother = true; break; }
            }
            if (!containsAnother) keepTables.add(a);
        }
        tables = keepTables;

        // A table that does not account for the lines drawn inside it is not a table. A menu
        // read as a two-row table swallowed fifty of its lines: they were marked consumed and
        // the table never wrote them. Such a table is dropped and its lines handed back.
        List<Table> solid = new ArrayList<>();
        for (Table t : tables) {
            int inside = 0, covered = 0;
            for (Line line : lines) {
                if (!line.inside(t)) continue;
                inside++;
                String norm = line.text.trim().replaceAll("\\s+", " ");
                for (List<String> row : t.rows) {
                    boolean hit = false;
                    for (String cell : row) {
                        String c = cell.trim().replaceAll("\\s+", " ");
                        if (!c.isEmpty() && (c.contains(norm) || norm.contains(c))) { hit = true; break; }
                    }
                    if (hit) { covered++; break; }
                }
            }
            // A table row is a baseline. A two-column page's gutter rule plus its header and
            // footer rules form a rectangle that encloses the whole page, and the "table"
            // built from it put a whole column of prose into one cell: the abstract-spanning
            // journal page came out as four lines instead of thirty-nine. Counting baselines
            // against rows catches that - a real table has about one baseline per row, a
            // whole-page false one has thirty baselines and three rows.
            if ((inside == 0 || covered * 100 / inside >= 60) && rowSane(t, lines)
                    && cellsFilled(t)) solid.add(t);
            else for (Line line : lines) if (line.inside(t)) line.consumed = false;
        }
        tables = solid;
        // Every table that survives carries the stroke the page drew on each of its six sides,
        // read here - the last point at which the page's own rule list is still in hand and the
        // table's bounds are final. D-22: the writer used to draw all six at one constant
        // weight and one constant colour whatever the page did.
        for (Table t : tables) markSideStrokes(t, topRules);

        // Text already sitting in a table cell must not also come out as body text: the bill of
        // lading appeared twice, once as a run-on paragraph and once as its proper table.
        //
        // This set is built from the tables that SURVIVED, and it used to be built one step
        // earlier, from every candidate. A candidate that the check above throws out still
        // left its cells in this set, and any line whose text matched one of those cells was
        // then skipped as "already written by a table" - by a table that was never written.
        // On file 54 a whole-page rectangle made of the header and footer rules produced a
        // candidate table whose cells were the page's own prose; the candidate was dropped
        // and the running footer went with it, so "Indian Institute of Plantation Management
        // * Bengaluru 560 056" and "Quarterly bulletin * Page 1" are absent from the .docx.
        // File 63 lost its estate line and its kicker the same way.
        java.util.HashSet<String> cellText = new java.util.HashSet<>();
        for (Table t : tables) {
            for (List<String> row : t.rows) {
                for (String cell : row) {
                    String norm = cell.trim().replaceAll("\\s+", " ");
                    if (norm.length() > 3) cellText.add(norm);
                }
            }
        }

        List<Line> body = new ArrayList<>();
        for (Line line : lines) {
            if (line.consumed) continue;
            // A stamp is drawn over the page, not in its grid: a line whose baseline is not
            // horizontal is never a table cell, however squarely it lies on one. Without this
            // the "PAID" stamp on file 07 - laid across the lower rows of the item table - was
            // dropped as if it were cell text that the table had already written.
            boolean inTable = false;
            if (!line.rotated) {
                for (Table t : tables) {
                    if (line.inside(t)) {
                        inTable = true;
                        break;
                    }
                }
            }
            if (!inTable) {
                String norm = line.text.trim().replaceAll("\\s+", " ");
                if (!norm.isEmpty() && cellText.contains(norm)) inTable = true;
            }
            if (!inTable) body.add(line);
        }

        int bands = columns(body, pageWidth, asBands(starts));
        boolean row = ROW || rowMajor(body, starts, rules, pageHeight);
        List<Para> paras = toParagraphs(body, pageWidth, bands, row);

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
        if (bands > 1 && !row) xyCut(prose, cut, 8f); else cut.addAll(prose);
        List<Object> reordered = new ArrayList<>();
        List<Table> pending = new ArrayList<>();
        for (Object o : ordered) if (o instanceof Table) pending.add((Table) o);
        // A big grid's box starts at the top of the page even when its content sits in the
        // middle. Placing it by its top put it above paragraphs that belong before it, so the
        // page read out of order. The middle of the box is a better guess at where it belongs.
        Collections.sort(pending, new Comparator<Table>() {
            @Override
            public int compare(Table a, Table b) {
                return Float.compare((a.top + a.bottom) / 2f, (b.top + b.bottom) / 2f);
            }
        });
        int ti = 0;
        for (Object o : cut) {
            while (ti < pending.size()
                    && (pending.get(ti).top + pending.get(ti).bottom) / 2f <= topOf(o)) {
                reordered.add(pending.get(ti++));
            }
            reordered.add(o);
        }
        while (ti < pending.size()) reordered.add(pending.get(ti++));
        ordered = reordered;

        // A label and its value sit on the same baseline: "Employee name" left, "SANDEEP
        // KULKARNI" right. Reading those column by column gives every label first and every
        // value after - the payslip came out as five labels then five values, which is
        // unreadable and scores 40 % on line order while scoring 100 % on line content.
        // The test that separates this from a newspaper is alignment: in a label/value block
        // the two sides' rows pair up at the same y; in a newspaper they do not.
        List<Line> allLines = new ArrayList<>();
        for (Object o : ordered) if (o instanceof Para) allLines.addAll(((Para) o).lines == null
                ? new ArrayList<Line>() : new ArrayList<Line>());
        List<Para> ps2 = new ArrayList<>();
        for (Object o : ordered) if (o instanceof Para) ps2.add((Para) o);

        // A wide table the detector missed - a BOQ, an invoice grid - arrives as one block per
        // cell, and sorting those by column reads the whole first column, then the whole second.
        // Three or more x-clusters of SHORT blocks is a grid, not prose: prose columns are long.
        // Read a grid row by row, which is how the page is read.
        if (ps2.size() >= 9) {
            List<Float> gx = new ArrayList<>();
            for (Para p : ps2) gx.add(p.left);
            Collections.sort(gx);
            int clusters = 1;
            for (int i = 1; i < gx.size(); i++) if (gx.get(i) - gx.get(i - 1) > 12f) clusters++;
            float wSum = 0;
            for (Para p : ps2) wSum += p.right - p.left;
            float wMean = wSum / ps2.size();
            if (clusters >= 4 && wMean < 90f) {
                List<Para> byRow = new ArrayList<>(ps2);
                Collections.sort(byRow, new java.util.Comparator<Para>() {
                    @Override
                    public int compare(Para a, Para b) {
                        int c = Float.compare(a.top, b.top);
                        return c != 0 ? c : Float.compare(a.left, b.left);
                    }
                });
                List<Object> again = new ArrayList<>(byRow);
                for (Object o : ordered) if (!(o instanceof Para)) again.add(o);
                Collections.sort(again, new java.util.Comparator<Object>() {
                    @Override
                    public int compare(Object a, Object b) {
                        return Float.compare(topOf(a), topOf(b));
                    }
                });
                ordered = again;
            }
        }

        if (ps2.size() >= 6) {
            List<Float> xs2 = new ArrayList<>();
            for (Para p : ps2) xs2.add(p.left);
            Collections.sort(xs2);
            float bg = 0f, cx = 0f;
            for (int i = 1; i < xs2.size(); i++) {
                float gap = xs2.get(i) - xs2.get(i - 1);
                if (gap > bg) { bg = gap; cx = (xs2.get(i - 1) + xs2.get(i)) / 2f; }
            }
            List<Para> L = new ArrayList<>(), R = new ArrayList<>();
            for (Para p : ps2) (p.left < cx ? L : R).add(p);
            if (bg >= 24f && L.size() >= 3 && R.size() >= 3) {
                int aligned = 0;
                for (Para a : L) {
                    for (Para b : R) {
                        if (Math.abs(a.top - b.top) <= 3f) { aligned++; break; }
                    }
                }
                // Measure against the SMALLER side: a label/value block has many short labels
                // and fewer values, so aligned/L understates it badly - the payslip gave 23 of
                // 69 and never fired.
                float share = aligned / (float) Math.min(L.size(), R.size());
                // A newspaper's two columns also align at the same baselines, so alignment
                // alone is not enough - it cost Group A five points. What separates them is
                // length: a value column holds short values, a newspaper column holds prose.
                float rSum = 0, lSum = 0;
                for (Para b : R) rSum += b.right - b.left;
                for (Para a : L) lSum += a.right - a.left;
                float rMean = rSum / R.size();
                float lMean = lSum / L.size();
                boolean shortValues = rMean <= 90f;
                // Both sides must be short. A delivery challan puts an address block in one
                // column and a transport block in the other; the rows align, but each column is
                // a self-contained block of prose and the reference reads one then the other.
                // Testing only the right side fired there and interleaved two unrelated blocks.
                boolean shortLabels = lMean <= 90f;
                if (share >= 0.85f && shortValues && shortLabels) {
                    // row-wise: interleave by y, and when two blocks share a baseline the
                    // left one comes first, which is how the page reads
                    List<Para> byRow = new ArrayList<>(ps2);
                    Collections.sort(byRow, new java.util.Comparator<Para>() {
                        @Override
                        public int compare(Para a, Para b) {
                            int c = Float.compare(a.top, b.top);
                            return c != 0 ? c : Float.compare(a.left, b.left);
                        }
                    });
                    // Merge tables back in by position. Putting every table first and every
                    // paragraph after broke the top of the page on two documents: a newsletter
                    // masthead and a BOQ heading both jumped out of place.
                    List<Object> again = new ArrayList<>(byRow);
                    for (Object o : ordered) if (!(o instanceof Para)) again.add(o);
                    Collections.sort(again, new java.util.Comparator<Object>() {
                        @Override
                        public int compare(Object a, Object b) {
                            return Float.compare(topOf(a), topOf(b));
                        }
                    });
                    ordered = again;
                }
            }
        }

        // The ring of a seal is not part of the reading flow: its characters have no reading
        // order of their own, and leaving them inline tore the body text apart - on file 60
        // the sentence "in recognition of the first rank..." was split by four border letters.
        // They go together, in drawing order, after the page's text.
        if (ring.size() >= 8) ordered.add(ringPara(ring));
        // A stamp is an overlay, not part of the text flow: it is drawn across the page rather
        // than in it, so a reader meets it after the page's own words. Left where its baseline
        // falls, "AUDITED" and "FY 2024-25" landed between the signature lines of file 09.
        // Every rotated line of the reference sits at the end of its page on all eight stamped
        // files measured here.
        List<Object> overlay = new ArrayList<>();
        for (java.util.Iterator<Object> it = ordered.iterator(); it.hasNext(); ) {
            Object o = it.next();
            if (o instanceof Para && ((Para) o).stamp) {
                overlay.add(o);
                it.remove();
            }
        }
        ordered.addAll(overlay);
        // A table in a right-to-left document runs from the right margin to the left one, so
        // its first column is the rightmost. Every pass that builds a table places its cells
        // in the order the page draws them, left to right, which mirrors the rows: the Arabic
        // invoice's header reached the reader as "المبلغ السعر الكمية الوصف البند" and its
        // first line as "1380000 34500 40 … 1". The rows are turned round here, once, for
        // every table on the page, and the column geometry is mirrored with them.
        for (Object o : ordered) if (o instanceof Table) rtlTable((Table) o);
        for (Object o : ordered) {
            page.blocks.add(o);
            if (o instanceof Para) report.paragraphs++;
            else {
                report.tables++;
            }
        }
        List<Table> written = new ArrayList<>();
        for (Object o : ordered) if (o instanceof Table) written.add((Table) o);
        attachShapes(page, rules, page.height, written);
        attachPictures(page, rules, page.height);
        return page;
    }


    /**
     * Turns a right-to-left table round: first column on the right, rows read from the right.
     *
     * <p>The rows are reversed together with the three arrays that run alongside them - the
     * cell x, the typeface and the colour - so a cell keeps its own geometry after the move.
     * The column edges are mirrored about the table's own extent, which reverses the widths
     * and puts each width back over the text it belongs to.
     */
    private static void rtlTable(Table t) {
        if (t == null || t.rows.isEmpty()) return;
        boolean rtl = false;
        for (List<String> row : t.rows) {
            for (String c : row) {
                if (c == null) continue;
                int r = 0, l = 0;
                for (int i = 0; i < c.length(); i++) {
                    char ch = c.charAt(i);
                    if (isRtl(ch)) r++;
                    else if (Character.isLetter(ch)) l++;
                }
                if (r > l && r > 0) { rtl = true; break; }
            }
            if (rtl) break;
        }
        if (!rtl) return;

        for (List<String> row : t.rows) Collections.reverse(row);
        reverseRows(t.cellX);
        reverseRows(t.cellR);
        reverseRows(t.fonts);
        reverseRows(t.sizes);
        reverseRows(t.colors);

        float lo = t.colX != null && t.colX.length > 0 ? t.colX[0] : t.left;
        float hi = t.colX != null && t.colX.length > 0 ? t.colX[t.colX.length - 1] : t.right;
        if (hi <= lo) return;
        if (t.colX != null) {
            float[] nx = new float[t.colX.length];
            for (int i = 0; i < t.colX.length; i++) nx[i] = lo + hi - t.colX[t.colX.length - 1 - i];
            t.colX = nx;
        }
        for (List<Float> xs : t.cellX) {
            for (int i = 0; i < xs.size(); i++) {
                Float v = xs.get(i);
                if (v != null && !v.isNaN()) xs.set(i, lo + hi - v);
            }
        }
    }

    private static <E> void reverseRows(List<List<E>> rows) {
        for (List<E> r : rows) Collections.reverse(r);
    }

    /**
     * A table row is a baseline, so a real table has about one baseline of text per row.
     *
     * <p>A two-column page draws its gutter as a vertical rule and often draws a rule under the
     * masthead and one above the folio. Those three rules enclose the whole page, and the table
     * built from them is a rectangle with two columns and three rows - into which every line of
     * the page falls. The coverage test above then passes trivially, because one cell holding a
     * whole column of prose contains every line in it. The journal page with an abstract
     * spanning both columns came out as four lines instead of thirty-nine this way.
     *
     * <p>Thirty baselines under three rows is not a table. The same rectangle also suppressed
     * the gutter as a column start, so the page lost its columns as well as its rows.
     */
    /**
     * A candidate table whose cells are almost all empty is a drawing, not a table.
     *
     * <p>332_bom_on_drawing's upright frame is three vertical strips crossed by a few
     * dividers, and the only text inside it is six circled part numbers. The line grid
     * round those numbers is a perfect 7 x 3 rectangle, so it passed every test there was
     * and went out as a bordered table: the render drew 68 rules where the page draws 43,
     * and the circled numbers were pulled into cells 33 pt from where the page put them.
     * A real table carries text in most of its cells - the same page's bill of materials
     * fills all 42 - so the fill rate separates the two without naming any one document.
     */
    private static boolean cellsFilled(Table t) {
        if (t.rows == null || t.rows.isEmpty()) return true;
        int cells = 0, filled = 0;
        for (List<String> row : t.rows) {
            for (String raw : row) {
                cells++;
                if (raw != null && !raw.trim().isEmpty()) filled++;
            }
        }
        // Three real cells is the floor: the smallest real table here is two rows by two
        // columns, and a quarter of the grid is a conservative share to call a table filled.
        return filled >= 3 && filled * 100 >= cells * 25;
    }

    private static boolean rowSane(Table t, List<Line> lines) {
        if (t.rows == null || t.rows.isEmpty()) return true;
        int rowsN = t.rows.size();
        int worst = 0;
        for (List<String> row : t.rows) {
            for (String raw : row) {
                String c = raw.trim().replaceAll("\\s+", " ");
                if (c.length() < 12) continue;
                int n = 0;
                for (Line line : lines) {
                    if (!line.inside(t)) continue;
                    String norm = line.text.trim().replaceAll("\\s+", " ");
                    if (norm.length() > 3 && c.contains(norm)) n++;
                }
                if (n > worst) worst = n;
            }
        }
        return worst <= Math.max(6, rowsN * 2);
    }

    private static float topOf(Object o) {
        return o instanceof Para ? ((Para) o).top : ((Table) o).top;
    }

    // ------------------------------------------------------------------ glyphs

    static final class Glyph {
        String text;
        float x, y, width, size;
        /**
         * The size to a whole point - the value the word-boundary test has always used.
         *
         * <p>{@link #size} is now read exactly (a page that sets 5.8 pt reports 5.8, not 5),
         * which is what the typeface is set at and what the .txt indent divides by. But the
         * gap test that decides where a word ENDS was tuned against the whole-point value, and
         * a page that letterspaces its capitals by about a fifth of an em sits right on the
         * threshold: reading the size more precisely moved the boundary under it and turned
         * "E L E C T I O N" into "ELECTION" on 39_small_caps_letter_spacing. How tall a glyph
         * is and where its word ends are different questions, so they use different numbers.
         */
        float sizePt;
        String font;
        boolean bold, italic;
        /** Colour as 0xRRGGBB, or -1 when the page draws it in the default black. */
        int color = -1;
        /** True when the baseline is not horizontal - a rotated stamp, a seal, a watermark. */
        boolean rotated;
        /** Page position from the text matrix, y downwards - the same space for every
         *  direction. {@link #x}/{@link #y} are measured ALONG the baseline, so on a 90-degree
         *  stamp they are not page coordinates and a colour cannot be matched to them. */
        float px, py;
        /** Unit vector along the baseline, in page space (y up). */
        float dirx = 1f, diry = 0f;
        /**
         * Unit vector along the baseline, in the space {@link #x}/{@link #y} are measured in
         * (page points, y DOWN) - taken from the text rendering matrix, not from
         * {@code TextPosition.getDir()}.
         *
         * <p>A stamp's rotation lives in the form's own {@code cm}, and {@code getDir()} comes
         * back 0 for every glyph of both stamps measured here: "SUNRISE FASTENERS" on file 01
         * and "PAID" on file 06 report {@code dir=(1,0)} while their glyphs step 2.5 pt and
         * 3.7 pt down the page. The text rendering matrix does carry the form's matrix, so its
         * first column is the direction the glyph was really drawn in.
         */
        float tx = 1f, ty = 0f;
    }

    private static final class GlyphCollector extends PDFTextStripper {
        final List<Glyph> out = new ArrayList<>();

        /**
         * One open marked-content sequence, innermost last.
         *
         * <p>A shaping engine writes the glyphs it actually drew - one glyph for the ligature
         * "र्ना" - and puts the text a reader should get into /ActualText on the enclosing
         * /Span. The glyph codes are visual, not logical: on the Devanagari page the same glyph
         * code <02> is the ligature "र्ना" in one place and the plain "न" in another, and only
         * /ActualText says which. PDFBox 2.0.27 does not read /ActualText at all, so the page
         * came out as "कर्ना  टक" where the reference reads "कर्नाटक" - 20.3 % line order on
         * file 40, 25.7 % on 78 and 46.5 % on 76, the three lowest in the batch.
         */
        private static final class Marked {
            /** The /ActualText of this sequence, or null when it carries none. */
            String text;
            /** Glyphs drawn inside it, held until the sequence closes. */
            final List<Glyph> held = new ArrayList<>();
        }

        private final List<Marked> marked = new ArrayList<>();

        GlyphCollector() throws IOException {
            super();
            setSortByPosition(false);
            setSuppressDuplicateOverlappingText(true);
            // PDFTextStripper extends LegacyPDFStreamEngine, whose operator table holds only
            // the text operators - BDC and EMC are not in it, so the marked-content hooks above
            // would never be called and /ActualText would stay unread. Registering the three
            // marked-content operators is all that is needed; they dispatch to the hooks.
            addOperator(new com.tom_roush.pdfbox.contentstream.operator.markedcontent
                    .BeginMarkedContentSequence());
            addOperator(new com.tom_roush.pdfbox.contentstream.operator.markedcontent
                    .BeginMarkedContentSequenceWithProperties());
            addOperator(new com.tom_roush.pdfbox.contentstream.operator.markedcontent
                    .EndMarkedContentSequence());
        }

        @Override
        public void beginMarkedContentSequence(COSName tag, COSDictionary props) {
            Marked m = new Marked();
            if (props != null) {
                COSBase b = props.getItem(COSName.ACTUAL_TEXT);
                if (b instanceof COSString) {
                    String t = actualTextOf((COSString) b);
                    if (t != null && !t.isEmpty()) m.text = t;
                }
            }
            marked.add(m);
            super.beginMarkedContentSequence(tag, props);
        }

        @Override
        public void endMarkedContentSequence() {
            super.endMarkedContentSequence();
            if (marked.isEmpty()) return;
            Marked m = marked.remove(marked.size() - 1);
            // A sequence with no /ActualText is transparent: whatever was drawn inside it
            // belongs to the sequence around it, which is the one that can name the text.
            if (m.text == null) {
                if (!m.held.isEmpty()) {
                    if (marked.isEmpty()) out.addAll(m.held);
                    else marked.get(marked.size() - 1).held.addAll(m.held);
                }
                return;
            }
            emitActual(m);
        }

        /**
         * Puts the text a /ActualText sequence names in place of the glyph codes it drew.
         *
         * <p>The glyphs themselves stay where they were drawn and keep their advances: only
         * the first one carries the string and the rest carry nothing, so the geometry the
         * rest of the engine reads - baselines, gaps, line extents - is exactly what the page
         * drew. Widening the first glyph to cover the cluster instead moved the next glyph's
         * advance past the baseline tolerance on a rotated stamp and cut one line into four.
         *
         * <p>A sequence that spans more than one baseline is left alone: there the string
         * describes several lines, and taking them out would delete the line breaks.
         */
        private void emitActual(Marked m) {
            if (m.held.isEmpty()) return;
            Glyph first = m.held.get(0);
            float lo = first.y, hi = first.y, size = first.size;
            for (Glyph g : m.held) {
                lo = Math.min(lo, g.y);
                hi = Math.max(hi, g.y);
                size = Math.max(size, g.size);
            }
            if (hi - lo > Math.max(2f, size * 0.6f)) {
                // more than one baseline: the text describes several lines, keep the glyphs
                if (marked.isEmpty()) out.addAll(m.held);
                else marked.get(marked.size() - 1).held.addAll(m.held);
                return;
            }
            first.text = m.text;
            for (int i = 1; i < m.held.size(); i++) m.held.get(i).text = "";
            out.addAll(m.held);
        }

        /** The string a /ActualText entry names, honouring its UTF-16 byte-order mark. */
        private static String actualTextOf(COSString cs) {
            byte[] b = cs.getBytes();
            if (b == null || b.length == 0) return null;
            try {
                if (b.length >= 2 && (b[0] & 0xFF) == 0xFE && (b[1] & 0xFF) == 0xFF) {
                    return new String(b, 2, b.length - 2, java.nio.charset.StandardCharsets.UTF_16BE);
                }
                if (b.length >= 2 && (b[0] & 0xFF) == 0xFF && (b[1] & 0xFF) == 0xFE) {
                    return new String(b, 2, b.length - 2, java.nio.charset.StandardCharsets.UTF_16LE);
                }
                return cs.getString();
            } catch (Throwable t) {
                return null;
            }
        }

        @Override
        protected void processTextPosition(TextPosition tp) {
            String u = tp.getUnicode();
            PDFont f0 = tp.getFont();
            // A CID font with no ToUnicode hands back the raw code as if it were a character:
            // a page that says "not subject without a ToUnicode CMap" arrives as
            // ")RQW\u0003VXEVHW...". The font itself still knows the right answer, so the
            // codes are decoded through it instead of trusting the empty result.
            if (f0 != null && isJunk(u)) {
                String again = decodeThroughFont(tp, f0);
                if (again != null && !isJunk(again)) u = again;
            }
            if (u == null || u.isEmpty()) return;
            Glyph g = new Glyph();
            g.text = u;
            g.x = tp.getXDirAdj();
            g.y = tp.getYDirAdj();
            g.px = tp.getX();
            g.py = tp.getY();
            double ang = Math.toRadians(tp.getDir());
            g.dirx = (float) Math.cos(ang);
            g.diry = (float) Math.sin(ang);

            g.width = tp.getWidthDirAdj();
            // getFontSizeInPt() is the size ROUNDED TO A WHOLE POINT: a page that sets
            // 5.8 pt reports 5.0, and one that sets 6.5 reports 6.0. Every size in every
            // document was therefore snapped to an integer, so a dense price list (362)
            // rendered 14 % small and its .txt indent sat 15.7 % too far right - just
            // outside the tolerance the position check allows. getFontSize() is the same
            // number without the rounding; inPt is only the fallback for a font whose size
            // the page did not name.
            g.sizePt = tp.getFontSizeInPt() > 0 ? tp.getFontSizeInPt() : tp.getFontSize();
            g.size = tp.getFontSize() > 0 ? tp.getFontSize() : tp.getFontSizeInPt();
            PDFont font = tp.getFont();
            g.font = font == null ? "" : font.getName();
            String n = g.font.toLowerCase(Locale.ROOT);
            g.bold = n.contains("bold") || n.contains("black") || n.contains("heavy")
                    || n.contains("semibold") || n.contains("demi");
            g.italic = n.contains("italic") || n.contains("oblique");
            // A non-horizontal baseline. getDir() is the angle in degrees; the text matrix
            // shear catches stamps whose glyphs are placed individually, where getDir()
            // sometimes reports 0 because each glyph carries its own horizontal matrix.
            try {
                if (Math.abs(tp.getDir()) > 0.5f) {
                    g.rotated = true;
                } else {
                    com.tom_roush.pdfbox.util.Matrix tm = tp.getTextMatrix();
                    if (tm != null && Math.abs(tm.getShearY()) > 0.02f) g.rotated = true;
                }
                com.tom_roush.pdfbox.util.Matrix tm2 = tp.getTextMatrix();
                if (tm2 != null) {
                    // First column of the text rendering matrix: where the glyph's own +x
                    // points, in PDF space (y up). Flipped into page space (y down) it is the
                    // direction the stamp's line advances in the coordinates everything else
                    // here uses.
                    float a = tm2.getValue(0, 0), b = tm2.getValue(0, 1);
                    float len = (float) Math.sqrt(a * a + b * b);
                    if (len > 1e-4f) {
                        g.tx = a / len;
                        g.ty = -b / len;
                    }
                }
            } catch (Throwable ignored) {
            }
            // Inside a marked-content sequence the glyphs are held until the sequence closes,
            // because only then is it known whether the sequence names its own text.
            for (int i = marked.size() - 1; i >= 0; i--) {
                if (marked.get(i).text != null) {
                    marked.get(i).held.add(g);
                    return;
                }
            }
            out.add(g);
        }
    }

    /**
     * Text a page carries outside its content stream: form field values, free-text boxes,
     * notes, comments.
     *
     * <p>A filled form keeps its answers in the field's /V, not in the page content. A reader
     * shows them because it draws the widget; a converter that only reads the content stream
     * silently drops every answer the user typed. That is data loss, not a layout choice.
     */
    private static String annotationTextOf(PDPage page) {
        StringBuilder sb = new StringBuilder();
        try {
            for (PDAnnotation ann : page.getAnnotations()) {
                if (ann == null || ann.isHidden()) continue;
                String c = ann.getContents();
                if (ann instanceof com.tom_roush.pdfbox.pdmodel.interactive.annotation
                        .PDAnnotationWidget) {
                    String v = widgetValue(ann);
                    if (v != null && !v.trim().isEmpty()) c = v.trim();
                }
                if (c == null || c.trim().isEmpty()) continue;
                if (sb.length() > 0) sb.append("\n\n");
                sb.append(c.trim());
            }
        } catch (Throwable ignored) {
            return "";
        }
        return sb.toString();
    }

    /** Text an annotation carries in its own right: a comment, a note, a free-text box. */
    private static List<String> annotationContentsOf(PDPage page) {
        List<String> out = new ArrayList<>();
        try {
            for (PDAnnotation ann : page.getAnnotations()) {
                if (ann == null || ann.isHidden()) continue;
                if (ann instanceof com.tom_roush.pdfbox.pdmodel.interactive.annotation
                        .PDAnnotationWidget) continue;      // its /V was already read
                String c = ann.getContents();
                if (c != null && !c.trim().isEmpty()) out.add(c.trim());
            }
        } catch (Throwable ignored) {
        }
        return out;
    }

    /** True when a decoded string carries nothing a person could read. */
    private static boolean isJunk(String s) {
        if (s == null || s.isEmpty()) return true;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '\n' || c == '\r' || c == '\t') continue;
            if (c < 0x20 || (c >= 0x7F && c <= 0x9F)) continue;
            return false;
        }
        return true;
    }

    /** Decode a glyph again straight from its font, glyph names included. */
    private static String decodeThroughFont(TextPosition tp, PDFont font) {
        try {
            int[] codes = tp.getCharacterCodes();
            if (codes == null || codes.length == 0) return null;
            StringBuilder sb = new StringBuilder();
            for (int code : codes) {
                String part = font.toUnicode(code,
                        com.tom_roush.pdfbox.pdmodel.font.encoding.GlyphList.getAdobeGlyphList());
                if (part == null) part = font.toUnicode(code);
                if (part != null) sb.append(part);
            }
            return sb.toString();
        } catch (Throwable t) {
            return null;
        }
    }

    /** Every answer a page's form fields hold, in page order. */
    private static List<String> formValuesOf(PDPage page) {
        List<String> out = new ArrayList<>();
        try {
            for (PDAnnotation ann : page.getAnnotations()) {
                if (ann == null || ann.isHidden()) continue;
                if (!(ann instanceof com.tom_roush.pdfbox.pdmodel.interactive.annotation
                        .PDAnnotationWidget)) continue;
                String v = widgetValue(ann);
                if (v != null && !v.trim().isEmpty()) out.add(v.trim());
            }
        } catch (Throwable ignored) {
        }
        return out;
    }

    /** The answer a form field holds, in the form a reader would show. */
    private static String widgetValue(PDAnnotation ann) {
        try {
            COSDictionary d = ann.getCOSObject();
            COSBase parent = d.getDictionaryObject(COSName.PARENT);
            COSDictionary field = parent instanceof COSDictionary
                    ? (COSDictionary) parent : d;
            String ft = field.getNameAsString(COSName.FT);
            COSBase v = field.getDictionaryObject(COSName.V);
            if (v == null) return null;
            if ("Btn".equals(ft)) {
                // A tick box has no text of its own; its /V is a state name like "Yes".
                String state = v instanceof COSName ? ((COSName) v).getName() : String.valueOf(v);
                if (state.isEmpty() || "Off".equalsIgnoreCase(state)) return null;
                String label = field.getString(COSName.T);
                return label == null || label.trim().isEmpty() ? null : label.trim();
            }
            if (v instanceof COSString) {
                String t = ((COSString) v).getString();
                return t == null || t.trim().isEmpty() ? null : t;
            }
            if (v instanceof COSArray) {
                StringBuilder j = new StringBuilder();
                for (COSBase e : (COSArray) v) {
                    if (e instanceof COSString) {
                        if (j.length() > 0) j.append(", ");
                        j.append(((COSString) e).getString());
                    }
                }
                return j.length() == 0 ? null : j.toString();
            }
            return null;
        } catch (Throwable t) {
            return null;
        }
    }

    /**
     * Paints each glyph with the colour the page actually fills it in.
     *
     * <p>PDFBox's text stripper cannot supply this: measured on a document whose headings are
     * #1C6B33 and #9E1A1A, getGraphicsState().getNonStrokingColor() returned DeviceGray 0,0,0
     * for every glyph. PyMuPDF reads the real colours from the same file, so the information
     * is there - it just is not reachable through the stripper.
     *
     * <p>So the content stream is walked here instead, as a stream of operators rather than as
     * text matched by regular expressions. Three things the old regex walk could not see, each
     * measured on the 80-document corpus:
     *
     * <ul>
     *   <li>the CTM. A stamp drawn under {@code q ... cm BT ... Tj ET Q} records its colour at
     *       coordinates in the untransformed space, so nothing lands near the glyphs. That is
     *       every rotated stamp: 03, 04, 05, 60.</li>
     *   <li>Form XObjects. {@code /fzFrm0 Do} draws the stamp's text from a separate stream the
     *       page-level parse never opens - 12_stamp_across_page_break,
     *       13_stamp_non_english, and a third XObject inside the second.</li>
     *   <li>the glyph's page position. {@code TextPosition.getXDirAdj()/getYDirAdj()} are
     *       measured ALONG the baseline, so for 90-degree text they are not page coordinates at
     *       all; {@code getX()/getY()} are.</li>
     * </ul>
     *
     * <p>A mark is recorded per text-showing operator, in page space, together with the unit
     * vector of the baseline it draws on. A glyph then takes the colour of the nearest mark
     * behind it on its own baseline, which is what "the colour in force" means: operators paint
     * the text that follows them.
     */
    private static void applyColours(PDDocument doc, int index, List<Glyph> glyphs) {
        if (glyphs.isEmpty()) return;
        ColourWalker walker = new ColourWalker();
        try {
            PDPage page = doc.getPage(index);
            java.io.InputStream in = page.getContents();
            if (in == null) return;
            walker.walk(readAll(in), page.getResources(), new float[]{1, 0, 0, 1, 0, 0}, 0);
        } catch (Throwable ignored) {
            return;
        }
        if (walker.marks.isEmpty()) return;
        try {
            // PDF y grows upwards; the glyph y from the stripper grows downwards.
            float h = doc.getPage(index).getMediaBox().getHeight();
            for (Glyph g : glyphs) {
                // The direction the colour is matched along must be the direction the glyph was
                // really drawn in. getDir() reports 0 for every glyph of a stamp whose rotation
                // is in the form's cm, so the match was made along a horizontal baseline: the
                // vertical offset of a 15-degree stamp then read as "across the baseline" and
                // passed the tolerance for the first few characters only. Measured on file 01,
                // the first 9 glyphs of "SUNRISE FASTENERS" resolved to #BF0D0D and the other
                // 8 resolved to nothing, which split one stamp line into four runs.
                int colour = walker.colourAt(g.px, h - g.py, g.tx, -g.ty, g.size);
                if (colour > 0) g.color = colour;
            }
        } catch (Throwable ignored) {
        }
    }

    /** One fill-colour change, in page space (y up), and the baseline it starts on. */
    private static final class ColourMark {
        final float x, y;      // page space, y up
        final float ux, uy;    // unit vector along the baseline the operator draws on
        final int rgb;

        ColourMark(float x, float y, float ux, float uy, int rgb) {
            this.x = x; this.y = y; this.ux = ux; this.uy = uy; this.rgb = rgb;
        }
    }

    /**
     * Walks a content stream - and every Form XObject it draws - recording each fill colour
     * change against the page-space point the text that follows it starts from.
     */
    private static final class ColourWalker {
        final List<ColourMark> marks = new ArrayList<>();
        /** Form XObjects already visited, so a stream that draws itself cannot recurse for ever. */
        private final java.util.Set<Object> seen =
                java.util.Collections.newSetFromMap(new java.util.IdentityHashMap<Object, Boolean>());
        private static final int MAX_DEPTH = 8;
        private static final Object DUMMY = new Object();

        /** The colour a glyph at (gx, gy) - page space, y up - is drawn in, or -1. */
        int colourAt(float gx, float gy, float dirx, float diry, float size) {
            float tol = Math.max(2.5f, size * 0.45f);
            ColourMark behind = null, ahead = null, loose = null;
            float behindAlong = Float.MAX_VALUE, aheadAlong = Float.MAX_VALUE, looseDist = 60f;
            for (ColourMark m : marks) {
                // 0 is BLACK, not "no colour": a mark of #000000 used to be dropped here, so
                // the only mark left near a glyph could be an invisible white copy of the same
                // text. File 39's title is drawn twice - once in 1 pt white, once in black - and
                // the white one won, which wrote a black heading as #FFFFFF.
                if (m.rgb < 0) continue;
                float dot = m.ux * dirx + m.uy * diry;
                float dx = gx - m.x, dy = gy - m.y;
                if (dot > 0.9f) {
                    // the mark draws on the same baseline: measure along it and across it
                    float along = dx * dirx + dy * diry;
                    float perp = -dx * diry + dy * dirx;
                    if (Math.abs(perp) <= tol) {
                        if (along >= -tol) {
                            // "Nearest behind" must break a near-tie in favour of the mark drawn
                            // LAST, because that is the colour in force: an operator paints the
                            // text that follows it. File 39 draws an invisible 1 pt white copy of
                            // its title on the very baseline and origin the visible black title
                            // then uses, and the white mark sits a tenth of a point AHEAD of the
                            // glyph - so it was the nearest "behind" one and a black heading was
                            // written #FFFFFF. The title vanished from the Word file, and no text
                            // metric moved: the characters were all still in the XML.
                            if (along <= behindAlong) { behindAlong = along; behind = m; }
                        } else if (-along < aheadAlong) {
                            aheadAlong = -along; ahead = m;
                        }
                        continue;
                    }
                }
                // nothing on this baseline: fall back to the nearest mark anywhere, as before
                float d = Math.abs(dx) + Math.abs(dy) * 4f;
                if (d < looseDist) { looseDist = d; loose = m; }
            }
            if (behind != null) return behind.rgb;
            if (ahead != null) return ahead.rgb;
            return loose == null ? -1 : loose.rgb;
        }

        void walk(String cs, PDResources res, float[] startCtm, int depth) {
            float[] ctm = startCtm.clone();
            ArrayList<float[]> stack = new ArrayList<>();
            float[] tm = {1, 0, 0, 1, 0, 0};
            float leading = 0f, charSpacing = 0f, wordSpacing = 0f, hScale = 1f;
            int cur = -1;
            String space = "";
            ArrayList<Object> ops = new ArrayList<>();
            int i = 0, n = cs.length();
            while (i < n) {
                char c = cs.charAt(i);
                if (isWs(c)) { i++; continue; }
                if (c == '%') { while (i < n && cs.charAt(i) != '\n' && cs.charAt(i) != '\r') i++; continue; }
                if (c == '(') { i = skipString(cs, i); ops.add(DUMMY); continue; }
                if (c == '<') {
                    if (i + 1 < n && cs.charAt(i + 1) == '<') { i = skipDict(cs, i); }
                    else { while (i < n && cs.charAt(i) != '>') i++; i++; }
                    ops.add(DUMMY);
                    continue;
                }
                if (c == '[') { i = skipArray(cs, i); ops.add(DUMMY); continue; }
                if (c == ']' || c == '>' || c == '{' || c == '}') { i++; continue; }
                if (c == '/') {
                    int s = i + 1;
                    i = s;
                    while (i < n && !isDelim(cs.charAt(i))) i++;
                    ops.add(cs.substring(s, i));
                    continue;
                }
                int s = i;
                while (i < n && !isDelim(cs.charAt(i))) i++;
                if (i == s) { i++; continue; }
                String tok = cs.substring(s, i);
                float num;
                try {
                    num = Float.parseFloat(tok);
                } catch (Exception notANumber) {
                    if (tok.equals("BI")) { i = skipInlineImage(cs, i); ops.clear(); continue; }
                    String name = ops.isEmpty() ? "" : (ops.get(ops.size() - 1) instanceof String
                            ? (String) ops.get(ops.size() - 1) : "");
                    if (tok.equals("q")) {
                        stack.add(ctm.clone());
                    } else if (tok.equals("Q")) {
                        if (!stack.isEmpty()) ctm = stack.remove(stack.size() - 1);
                    } else if (tok.equals("cm") && ops.size() >= 6) {
                        ctm = mul(new float[]{num(ops, -6), num(ops, -5), num(ops, -4),
                                num(ops, -3), num(ops, -2), num(ops, -1)}, ctm);
                    } else if (tok.equals("BT")) {
                        tm = new float[]{1, 0, 0, 1, 0, 0};
                    } else if (tok.equals("Td") || tok.equals("TD")) {
                        float tx = num(ops, -2), ty = num(ops, -1);
                        if (tok.equals("TD")) leading = -ty;
                        tm = mul(new float[]{1, 0, 0, 1, tx, ty}, tm);
                    } else if (tok.equals("Tm") && ops.size() >= 6) {
                        tm = new float[]{num(ops, -6), num(ops, -5), num(ops, -4),
                                num(ops, -3), num(ops, -2), num(ops, -1)};
                    } else if (tok.equals("TL")) {
                        leading = num(ops, -1);
                    } else if (tok.equals("Tc")) {
                        charSpacing = num(ops, -1);
                    } else if (tok.equals("Tw")) {
                        wordSpacing = num(ops, -1);
                    } else if (tok.equals("Tz")) {
                        hScale = num(ops, -1) / 100f;
                    } else if (tok.equals("T*")) {
                        tm = mul(new float[]{1, 0, 0, 1, 0, -leading}, tm);
                    } else if (tok.equals("'")) {
                        tm = mul(new float[]{1, 0, 0, 1, 0, -leading}, tm);
                        addMark(tm, ctm, cur);
                    } else if (tok.equals("\"")) {
                        if (ops.size() >= 3) { wordSpacing = num(ops, -3); charSpacing = num(ops, -2); }
                        tm = mul(new float[]{1, 0, 0, 1, 0, -leading}, tm);
                        addMark(tm, ctm, cur);
                    } else if (tok.equals("Tj") || tok.equals("TJ")) {
                        addMark(tm, ctm, cur);
                    } else if (tok.equals("rg") && ops.size() >= 3) {
                        cur = packRgb(num(ops, -3), num(ops, -2), num(ops, -1));
                    } else if (tok.equals("g") && ops.size() >= 1) {
                        cur = grey(num(ops, -1));
                    } else if (tok.equals("k") && ops.size() >= 4) {
                        cur = cmyk(num(ops, -4), num(ops, -3), num(ops, -2), num(ops, -1));
                    } else if (tok.equals("cs")) {
                        space = name;
                    } else if ((tok.equals("sc") || tok.equals("scn")) && !ops.isEmpty()) {
                        // A pattern name instead of components: leave the colour alone.
                        int count = 0;
                        for (Object o : ops) if (o instanceof Float) count++;
                        if (count == 1) cur = grey(num(ops, -1));
                        else if (count == 3) cur = packRgb(num(ops, -3), num(ops, -2), num(ops, -1));
                        else if (count == 4) cur = cmyk(num(ops, -4), num(ops, -3), num(ops, -2), num(ops, -1));
                    } else if (tok.equals("Do")) {
                        draw(name, res, ctm, depth);
                    }
                    ops.clear();
                    continue;
                }
                ops.add(num);
            }
        }

        /** Records the colour in force at the origin of {@code tm}, transformed by {@code ctm}. */
        private void addMark(float[] tm, float[] ctm, int rgb) {
            if (rgb < 0) return;
            float tx = tm[4], ty = tm[5];
            float px = tx * ctm[0] + ty * ctm[2] + ctm[4];
            float py = tx * ctm[1] + ty * ctm[3] + ctm[5];
            float ux = tm[0] * ctm[0] + tm[1] * ctm[2];
            float uy = tm[0] * ctm[1] + tm[1] * ctm[3];
            float len = (float) Math.hypot(ux, uy);
            if (len < 1e-6f) { ux = 1f; uy = 0f; } else { ux /= len; uy /= len; }
            marks.add(new ColourMark(px, py, ux, uy, rgb));
        }

        /** Follows {@code /Name Do} into a Form XObject and reads its stream the same way. */
        private void draw(String name, PDResources res, float[] ctm, int depth) {
            if (depth >= MAX_DEPTH || res == null || name.isEmpty()) return;
            try {
                com.tom_roush.pdfbox.pdmodel.graphics.PDXObject xo =
                        res.getXObject(com.tom_roush.pdfbox.cos.COSName.getPDFName(name));
                if (!(xo instanceof com.tom_roush.pdfbox.pdmodel.graphics.form.PDFormXObject)) return;
                com.tom_roush.pdfbox.pdmodel.graphics.form.PDFormXObject form =
                        (com.tom_roush.pdfbox.pdmodel.graphics.form.PDFormXObject) xo;
                com.tom_roush.pdfbox.pdmodel.common.PDStream stream = form.getStream();
                if (stream == null || !seen.add(stream.getCOSObject())) return;
                float[] m = {1, 0, 0, 1, 0, 0};
                try {
                    com.tom_roush.pdfbox.util.Matrix mm = form.getMatrix();
                    if (mm != null) {
                        m[0] = mm.getValue(0, 0); m[1] = mm.getValue(1, 0);
                        m[2] = mm.getValue(0, 1); m[3] = mm.getValue(1, 1);
                        m[4] = mm.getValue(2, 0); m[5] = mm.getValue(2, 1);
                    }
                } catch (Throwable ignored) {
                }
                PDResources inner = form.getResources();
                if (inner == null) inner = res;
                walk(readAll(stream.createInputStream()), inner, mul(m, ctm), depth + 1);
            } catch (Throwable ignored) {
            }
        }
    }

    /** {@code m} applied first, then {@code n}. */
    private static float[] mul(float[] m, float[] n) {
        return new float[]{
                m[0] * n[0] + m[1] * n[2],
                m[0] * n[1] + m[1] * n[3],
                m[2] * n[0] + m[3] * n[2],
                m[2] * n[1] + m[3] * n[3],
                m[4] * n[0] + m[5] * n[2] + n[4],
                m[4] * n[1] + m[5] * n[3] + n[5]};
    }

    private static float num(List<Object> ops, int fromEnd) {
        int i = ops.size() + fromEnd;
        if (i < 0 || i >= ops.size()) return 0f;
        Object o = ops.get(i);
        return o instanceof Float ? (Float) o : 0f;
    }

    private static boolean isWs(char c) {
        return c == ' ' || c == '\n' || c == '\r' || c == '\t' || c == '\f' || c == '\0';
    }

    private static boolean isDelim(char c) {
        return isWs(c) || c == '(' || c == ')' || c == '<' || c == '>' || c == '['
                || c == ']' || c == '{' || c == '}' || c == '/' || c == '%';
    }

    /** Skips a literal string, honouring backslash escapes and nested parentheses. */
    private static int skipString(String s, int i) {
        int depth = 0;
        while (i < s.length()) {
            char c = s.charAt(i);
            if (c == '\\') { i += 2; continue; }
            if (c == '(') depth++;
            else if (c == ')') { depth--; if (depth == 0) return i + 1; }
            i++;
        }
        return i;
    }

    private static int skipDict(String s, int i) {
        int depth = 0;
        while (i < s.length()) {
            char c = s.charAt(i);
            if (c == '<' && i + 1 < s.length() && s.charAt(i + 1) == '<') { depth++; i += 2; continue; }
            if (c == '>' && i + 1 < s.length() && s.charAt(i + 1) == '>') {
                depth--;
                i += 2;
                if (depth == 0) return i;
                continue;
            }
            i++;
        }
        return i;
    }

    private static int skipArray(String s, int i) {
        int depth = 0;
        while (i < s.length()) {
            char c = s.charAt(i);
            if (c == '[') depth++;
            else if (c == ']') { depth--; if (depth == 0) return i + 1; }
            i++;
        }
        return i;
    }

    /** Skips the binary payload of an inline image: {@code BI ... ID <bytes> EI}. */
    private static int skipInlineImage(String s, int i) {
        int id = s.indexOf("ID", i);
        if (id < 0) return s.length();
        int p = id + 2;
        while (p < s.length() - 1) {
            if (s.charAt(p) == 'E' && s.charAt(p + 1) == 'I'
                    && isWs(s.charAt(p - 1)) && (p + 2 >= s.length() || isDelim(s.charAt(p + 2)))) {
                return p + 2;
            }
            p++;
        }
        return s.length();
    }

    private static String readAll(java.io.InputStream in) throws java.io.IOException {
        java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int n;
        while ((n = in.read(buf)) > 0) bo.write(buf, 0, n);
        in.close();
        return new String(bo.toByteArray(), java.nio.charset.StandardCharsets.ISO_8859_1);
    }

    private static int grey(float v) {
        int c = Math.round(Math.max(0f, Math.min(1f, v)) * 255f);
        return (c << 16) | (c << 8) | c;
    }

    private static int cmyk(float c, float m, float y, float k) {
        int r = Math.round(255f * (1f - Math.min(1f, c + k)));
        int g2 = Math.round(255f * (1f - Math.min(1f, m + k)));
        int b = Math.round(255f * (1f - Math.min(1f, y + k)));
        return ((r & 0xFF) << 16) | ((g2 & 0xFF) << 8) | (b & 0xFF);
    }

    private static float f(String s) {
        try { return Float.parseFloat(s); } catch (Exception e) { return 0f; }
    }

    private static int packRgb(float r, float g, float b) {
        int ri = Math.round(Math.max(0f, Math.min(1f, r)) * 255f);
        int gi = Math.round(Math.max(0f, Math.min(1f, g)) * 255f);
        int bi = Math.round(Math.max(0f, Math.min(1f, b)) * 255f);
        return ((ri & 0xFF) << 16) | ((gi & 0xFF) << 8) | (bi & 0xFF);
    }

    private static List<Glyph> glyphsOf(PDDocument doc, int index) {
        try {
            GlyphCollector gc = new GlyphCollector();
            gc.setStartPage(index + 1);
            gc.setEndPage(index + 1);
            gc.getText(doc);
            List<Glyph> out = dedupe(gc.out);
            applyColours(doc, index, out);
            return out;
        } catch (Throwable t) {
            return new ArrayList<>();
        }
    }

    /**
     * How far apart, in points, two copies of the same character may be and still be one
     * character drawn twice.
     *
     * <p>An OCR overlay re-draws the page's text at exactly the position the scanner saw it,
     * so the two copies are the same cell: measured over the 80-document batch, all 23
     * genuinely doubled glyphs sat at the identical x and y. A character that is merely
     * NEARBY is a different character, and the old 1.2 pt window was wider than the advance
     * of the letters it merged: at 8.5 pt an 'e' is 3.77 pt wide and the 'e' of "preventive"
     * (x 364.03) swallowed the 'e' of the unit cell "Year" (x 362.88, 1.15 pt away, in the
     * next column of the same baseline) - file 28 lost a letter and read "Y ar". At 1 pt a
     * capital is 0.89 pt wide, so the second 'M' of "COMMERCE" went the same way on file 39
     * ("COM ERCE"). Half a point is below the narrowest advance the batch contains, so two
     * different characters can no longer be mistaken for one.
     */
    private static final float DUPLICATE_TOL = 0.5f;

    /** Drops the second copy of text that sits on top of the first, as OCR overlays do. */
    private static List<Glyph> dedupe(List<Glyph> in) {
        List<Glyph> out = new ArrayList<>(in.size());
        for (Glyph g : in) {
            boolean duplicate = false;
            for (int i = out.size() - 1; i >= 0 && i >= out.size() - 40; i--) {
                Glyph p = out.get(i);
                if (Math.abs(p.x - g.x) < DUPLICATE_TOL && Math.abs(p.y - g.y) < DUPLICATE_TOL
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
        /**
         * Which vertical slice of the page this line belongs to. A full-width element - a
         * masthead, a chart, a table across both columns - ends the slice above it and starts a
         * new one, because the flow resets there: the text above the element is read column by
         * column, then the element, then the columns below it. Ordering a whole page by column
         * first is not a reading order once such an element exists.
         */
        int segment;
        boolean consumed;
        /**
         * The fields that stand on this line's own baseline in ANOTHER column.
         *
         * <p>A page places text at an absolute x and y, so an invoice's title and its company
         * name are two runs at the same y and nothing more. A DOCX has flow: the writer can put
         * both on one line with a tab stop at the measured x, but only if the model hands them
         * over together. The column order separates them - every line of column 0, then every
         * line of column 1 - so the title arrived after the whole left block and took a line of
         * its own, pushing everything below it down the sheet.
         *
         * <p>Measured on gst-invoice-3line-items: 'TAX INVOICE' is at y=43.54 and the company
         * name at y=42.38 on the same page, and the render put the title 50.1 pt lower.
         * gst-invoice-multipage-item-table 107.1 pt, delivery-challan 107.1 pt, and
         * itr-computation-with-slab-table 111.1 pt, all the same cause.
         */
        List<Line> rowMates;
        /** True when this line was attached to another line's row and must not start one. */
        boolean mate;
        /** True when this line was cut out of a longer one at a wide gap: it is its own line
         *  and must never be merged back into the paragraph above it. */
        boolean hardEnd;
        /**
         * True when every glyph on this line sits on a non-horizontal baseline - a rotated
         * stamp, a seal, a watermark.
         *
         * <p>A stamp is drawn over the page, not in its grid. When its characters were offered
         * to the table builder along with everything else, a stamp lying across the lower rows
         * broke the cell structure badly enough that the table was not emitted at all: measured
         * on the 39 documents carrying a stamp or a table, 8 of 25 tables were missing and
         * every one of those 8 was a stamped document. The line still appears in the output -
         * it is only kept out of the grid.
         */
        boolean rotated;
        /** True when this line is one character of a seal drawn as a ring. */
        boolean ring;
        /**
         * How long the line is ALONG its own baseline, in points.
         *
         * <p>{@link #right} minus {@link #x} is the line's width across the page, which on a
         * vertical stamp is the height of the text, not its length. A text box sized from that
         * width is 22 pt wide for a 50 pt date, so the date wrapped and the second half was
         * clipped away.
         */
        float length;
        /** The baseline's angle in degrees, clockwise, 0 for upright text. */
        float angle;
        /** Bottom edge of the line's box on the page, y down. */
        float bottom;

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

    /** Zero-coverage x-ranges of the glyphs in these lines, keeping only gaps with real
     *  columns on both sides. Used by the whole-page pass and by the per-band pass. */
    /**
     * How many newspaper columns this page is set in, decided from the page's own lines.
     *
     * <p>The writer cannot answer this. `asBands` cuts a four-point slice out of every line at the
     * gutter, so a line crossing it arrives as two fragments and every band is half a page wide by
     * construction - which is why three documents that are not multi-column at all were being
     * divided: their "gutter" measured 4-12 pt and their "columns" were page halves.
     *
     * <p>A band is a column only if it is filled with prose. Spanning lines are dropped first
     * (wider than 62 % of the content span - the rule `keep0` already uses), the rest are clustered
     * by left edge, and each band must hold at least three lines whose width is half the widest
     * band's ink width. Measured on the corpus: the worst false positive has one such line, the
     * best genuine two-column page has five, most have eight to twenty-three.
     */
    private static int proseColumns(List<Line> rawLines, float pageWidth) {
        if (rawLines == null || rawLines.size() < 6 || pageWidth <= 0f) return 1;
        float minX = Float.MAX_VALUE, maxX = -Float.MAX_VALUE;
        for (Line l : rawLines) { minX = Math.min(minX, l.x); maxX = Math.max(maxX, l.right); }
        float span = maxX - minX;
        if (span <= 0f) return 1;
        java.util.List<Line> prose = new java.util.ArrayList<>();
        for (Line l : rawLines) {
            if (l.rotated) continue;
            if (l.right - l.x > span * 0.62f) continue;
            prose.add(l);
        }
        if (prose.size() < 6) return 1;
        java.util.Collections.sort(prose, new java.util.Comparator<Line>() {
            public int compare(Line a, Line b) { return Float.compare(a.x, b.x); }
        });
        // Cluster the left edges. A gutter is a run of x values with nothing in it.
        java.util.List<float[]> bands = new java.util.ArrayList<>();   // {left, right, ink}
        float curLeft = prose.get(0).x, curRight = prose.get(0).right;
        for (int i = 1; i < prose.size(); i++) {
            Line l = prose.get(i);
            if (l.x - curRight > 8f) {
                bands.add(new float[]{curLeft, curRight, 0f});
                curLeft = l.x; curRight = l.right;
            } else {
                curRight = Math.max(curRight, l.right);
            }
        }
        bands.add(new float[]{curLeft, curRight, 0f});
        if (bands.size() < 2 || bands.size() > 4) return 1;
        // Ink width of the widest band, and how many prose lines each band really holds.
        float widest = 0f;
        for (float[] b : bands) widest = Math.max(widest, b[1] - b[0]);
        if (widest <= 0f) return 1;
        int[] qualifying = new int[bands.size()];
        for (Line l : prose) {
            for (int b = 0; b < bands.size(); b++) {
                if (l.x >= bands.get(b)[0] - 2f && l.right <= bands.get(b)[1] + 2f) {
                    if (l.right - l.x >= widest * 0.5f) qualifying[b]++;
                    break;
                }
            }
        }
        for (int q : qualifying) if (q < 3) return 1;
        // Newspaper columns are about the same width as each other, and the gutter is narrow.
        float widestBand = 0f, thinnestBand = Float.MAX_VALUE;
        for (float[] b : bands) {
            float w2 = b[1] - b[0];
            widestBand = Math.max(widestBand, w2);
            thinnestBand = Math.min(thinnestBand, w2);
        }
        if (thinnestBand < widestBand * 0.7f) return 1;
        float gap = 0f;
        for (int b = 1; b < bands.size(); b++) gap = Math.max(gap, bands.get(b)[0] - bands.get(b - 1)[1]);
        if (gap > 30f) return 1;
        return bands.size();
    }

    private static List<Float> keep0(List<Line> rawLines, float fullWidth) {
        List<float[]> iv = new ArrayList<>();
        float lo = Float.MAX_VALUE, hi = -Float.MAX_VALUE;
        for (Line l : rawLines) {
            if (l.text.trim().isEmpty() || l.right - l.x > fullWidth) continue;
            for (Glyph g : l.glyphs) {
                if (g.width <= 0 || g.text == null || g.text.trim().isEmpty()) continue;
                iv.add(new float[]{g.x, g.x + g.width});
                lo = Math.min(lo, g.x);
                hi = Math.max(hi, g.x + g.width);
            }
        }
        List<Float> keep = new ArrayList<>();
        if (iv.size() < 40 || hi <= lo) return keep;
        Collections.sort(iv, new Comparator<float[]>() {
            @Override
            public int compare(float[] a, float[] b) { return Float.compare(a[0], b[0]); }
        });
        float span = hi - lo;
        List<float[]> gaps = new ArrayList<>();
        float reach = iv.get(0)[1];
        for (int i = 1; i < iv.size(); i++) {
            float gs = iv.get(i)[0];
            if (gs - reach > span * 0.015f) gaps.add(new float[]{reach, gs});
            reach = Math.max(reach, iv.get(i)[1]);
        }
        for (float[] gp : gaps) {
            float mid = (gp[0] + gp[1]) / 2f;
            int left = 0, right = 0;
            for (float[] v : iv) {
                if (v[1] <= mid) left++;
                else if (v[0] >= mid) right++;
            }
            if (left >= iv.size() * 0.10f && right >= iv.size() * 0.10f) keep.add(mid);
        }
        return keep;
    }

    /** True when every glyph in this run is drawn on a non-horizontal baseline. */
    private static boolean allRotated(List<Glyph> run) {
        if (run.isEmpty()) return false;
        for (Glyph g : run) if (!g.rotated) return false;
        return true;
    }

    /**
     * The rotated glyphs of a page, one line per stamp.
     *
     * <p>A rotated line does not advance along x: every glyph sits a fraction of a point
     * further down than the one before, and the baseline tolerance that separates two lines is
     * a fraction of the font size. On a 15-degree stamp in a 14 pt face the step is 2.5 pt
     * against a 2.52 pt tolerance, so the two are the same size and the comparison comes out
     * either way glyph by glyph: "SUNRISE FASTENERS" reached the output as twenty fragments
     * ("S U", "E T", "A O", "S SIG"). On a stamp in a 44 pt face the tolerance is 7.9 pt and
     * the step 3.7 pt, so the stamp's glyphs were instead swallowed by whatever upright line
     * happened to cross them: "PAID" put P inside the body line at y=398, A and I inside the
     * amount at y=389, and left a lone "D" behind. Neither stamp string appeared anywhere in
     * either .docx.
     *
     * <p>So a rotated glyph is clustered by the direction it was drawn in, not by raw y.
     * Glyphs that share a direction are separated by their offset perpendicular to it, which
     * is what tells two crossing stamp lines apart - on file 01 the two baselines are 17.5 pt
     * apart against a 2.52 pt tolerance, though their y ranges overlap completely. Within one
     * line the glyphs are then ordered along the direction, which is reading order whatever
     * the angle.
     *
     * <p>The direction is each glyph's own, from the text rendering matrix (see
     * {@link Glyph#tx}); a slope estimated for the page as a whole was tried before and
     * reverted, because it was applied to text that was not rotated. Nothing here can touch
     * upright text: a glyph enters this pass only if it is already flagged rotated <em>and</em>
     * its own direction is more than about 2.9 degrees off horizontal, and the pass stands
     * down entirely on a page where nearly everything is rotated - that is a rotated page,
     * not a stamp, and the ordinary clustering handles it.
     */
    private static List<Line> stampLines(List<Glyph> glyphs) {
        List<Line> out = new ArrayList<>();
        if (glyphs.isEmpty()) return out;
        List<Glyph> rot = new ArrayList<>();
        for (Glyph g : glyphs) {
            if (!g.rotated) continue;
            if (Math.abs(g.ty) <= 0.05f) continue;          // horizontal to within 2.9 degrees
            rot.add(g);
        }
        if (rot.size() < 2) return out;
        if (rot.size() > glyphs.size() * 0.85f) return out;  // a rotated page, not a stamp

        // One group per direction: two stamps at different angles must not share a line.
        List<List<Glyph>> byDir = new ArrayList<>();
        for (Glyph g : rot) {
            List<Glyph> target = null;
            for (List<Glyph> grp : byDir) {
                Glyph s = grp.get(0);
                if (s.tx * g.tx + s.ty * g.ty > 0.996f) {    // within 5 degrees
                    target = grp;
                    break;
                }
            }
            if (target == null) {
                target = new ArrayList<>();
                byDir.add(target);
            }
            target.add(g);
        }

        for (List<Glyph> grp : byDir) {
            final Glyph seed = grp.get(0);
            final float dx = seed.tx, dy = seed.ty;
            final float nx = -dy, ny = dx;
            List<Glyph> byPerp = new ArrayList<>(grp);
            Collections.sort(byPerp, new Comparator<Glyph>() {
                @Override
                public int compare(Glyph a, Glyph b) {
                    return Float.compare(perpOf(a, seed, nx, ny), perpOf(b, seed, nx, ny));
                }
            });

            List<List<Glyph>> rows = new ArrayList<>();
            List<Glyph> row = new ArrayList<>();
            float ref = 0;
            for (Glyph g : byPerp) {
                float perp = perpOf(g, seed, nx, ny);
                float tol = Math.max(0.9f, g.size * 0.18f);
                if (row.isEmpty() || Math.abs(perp - ref) > tol) {
                    if (!row.isEmpty()) rows.add(row);
                    row = new ArrayList<>();
                    ref = perp;
                }
                row.add(g);
            }
            if (!row.isEmpty()) rows.add(row);

            for (List<Glyph> r : rows) {
                Collections.sort(r, new Comparator<Glyph>() {
                    @Override
                    public int compare(Glyph a, Glyph b) {
                        return Float.compare(alongOf(a, seed, dx, dy), alongOf(b, seed, dx, dy));
                    }
                });
                // A gap no letter advance makes is two fields, not one line - the same rule the
                // upright pass applies to a gutter, measured along the stamp's own baseline.
                List<Glyph> seg = new ArrayList<>();
                Glyph prev = null;
                for (Glyph g : r) {
                    if (prev != null) {
                        float gap = alongOf(g, seed, dx, dy)
                                - (alongOf(prev, seed, dx, dy) + prev.width);
                        if (gap > Math.max(9f, g.size * 1.6f)) {
                            out.add(stampLineOf(seg));
                            seg = new ArrayList<>();
                        }
                    }
                    seg.add(g);
                    prev = g;
                }
                if (!seg.isEmpty()) out.add(stampLineOf(seg));
            }
        }
        return out;
    }

    /**
     * Distance of a glyph from the stamp's baseline, measured across it.
     *
     * <p>Measured in page coordinates ({@link Glyph#px}/{@link Glyph#py}), not in the
     * direction-adjusted {@link Glyph#x}/{@link Glyph#y}: those are rotated into the text's own
     * frame, so on a 90-degree stamp they run along the baseline and cannot say which of two
     * parallel baselines a glyph is on. Measured that way, the vertical stamp on file 03 came
     * out one character per line - every glyph of a line shares an x, and the line's own
     * direction is not in the numbers.
     */
    private static float perpOf(Glyph g, Glyph seed, float nx, float ny) {
        return (g.px - seed.px) * nx + (g.py - seed.py) * ny;
    }

    /** Distance of a glyph along the stamp's baseline, measured from the first glyph. */
    private static float alongOf(Glyph g, Glyph seed, float dx, float dy) {
        return (g.px - seed.px) * dx + (g.py - seed.py) * dy;
    }

    /**
     * One stamp line, with the extent the writer needs to place it.
     *
     * <p>The extent is the stamp's own, in page points: {@link Glyph#x} is measured along the
     * baseline, so on the 90-degree stamp it is the distance up the page and on the 180-degree
     * one it runs backwards - anchoring a text box at that value put "CANCELLED" at x=151 on a
     * page where it is drawn at x=444.
     */
    private static Line stampLineOf(List<Glyph> seg) {
        Line line = new Line();
        line.glyphs.addAll(seg);
        line.text = textOf(seg);
        float totalSize = 0;
        float left = Float.MAX_VALUE, right = -Float.MAX_VALUE;
        float top = Float.MAX_VALUE;
        float widest = 0;
        for (Glyph g : seg) {
            totalSize += g.size;
            if (g.px < left) {
                left = g.px;
                top = g.py;
            }
            right = Math.max(right, g.px);
            widest = Math.max(widest, g.size);
        }
        line.size = totalSize / seg.size();
        line.x = left;
        line.left = left;
        line.right = Math.max(right, left) + widest;
        line.y = top;
        line.rotated = true;
        float bottom = -Float.MAX_VALUE;
        for (Glyph g : seg) bottom = Math.max(bottom, g.py + g.size);
        line.bottom = bottom;
        // The extent along the baseline, and the angle it runs at. Both come from the
        // direction the glyphs were really drawn in: a stamp's rotation lives in the form's
        // own cm, so the text matrix is the only place that knows it.
        Glyph seed = seg.get(0);
        float dx = seed.tx == 0f && seed.ty == 0f ? 1f : seed.tx;
        float dy = seed.tx == 0f && seed.ty == 0f ? 0f : seed.ty;
        float minA = Float.MAX_VALUE, maxA = -Float.MAX_VALUE;
        for (Glyph g : seg) {
            float along = alongOf(g, seed, dx, dy);
            minA = Math.min(minA, along);
            maxA = Math.max(maxA, along);
        }
        line.length = Math.max(maxA - minA + widest, widest);
        line.angle = (float) Math.toDegrees(Math.atan2(dy, dx));
        return line;
    }

    /**
     * Clears the rotated flag when the WHOLE page is drawn upside down.
     *
     * <p>A page printed the wrong way up is not a page of stamps. Every glyph on it is turned
     * 180 degrees, which {@code TextPosition.getDir()} reports as a non-zero direction, so every
     * glyph was flagged {@link Glyph#rotated}: {@code sameRow} then refused all 112 pairs of
     * fields that stood on a shared baseline, and the page's 15 baselines came out as 61
     * paragraphs - one per field, stacked one above the other, which is the flow that runs off
     * the sheet. A reader turns the sheet, not each word, and the baseline is horizontal either
     * way, so the page's text is offered as upright.
     *
     * <p>Only when nothing on the page is upright: a 180-degree stamp laid over an ordinary page
     * (04_stamp_180deg_upside_down, 08_two_overlapping_stamps) is still an overlay and keeps its
     * flag, and so does any page whose text does not run along a horizontal baseline.
     */
    private static void uprightIfPageIsUpsideDown(List<Glyph> glyphs) {
        int turned = 0;
        for (Glyph g : glyphs) {
            if (g.text == null || g.text.trim().isEmpty()) continue;
            if (!g.rotated) return;                     // an upright glyph: an ordinary page
            if (Math.abs(g.diry) > 0.25f) return;       // the baseline is not horizontal
            if (g.dirx >= 0f) return;                   // not turned round
            turned++;
        }
        if (turned == 0) return;
        for (Glyph g : glyphs) g.rotated = false;
    }

    private static List<Line> toLines(List<Glyph> glyphs, List<float[]> gutters) {
        // A seal drawn as a ring of characters is not a block of text and has no baseline to
        // cluster on: every character sits on its own tangent. It is taken out of the page's
        // text here and handed back as one character per line, in the order the page drew
        // them - which is the order a reader follows round the ring.
        List<Line> ring = ringLines(glyphs);
        if (!ring.isEmpty()) {
            java.util.IdentityHashMap<Glyph, Boolean> inRing =
                    new java.util.IdentityHashMap<>();
            for (Line rl : ring) for (Glyph g : rl.glyphs) inRing.put(g, Boolean.TRUE);
            List<Glyph> rest = new ArrayList<>(glyphs.size());
            for (Glyph g : glyphs) if (!inRing.containsKey(g)) rest.add(g);
            glyphs = rest;
        }
        // A stamp has no baseline to find by y - it advances down the page as it goes across
        // it - so its glyphs are taken out here and clustered by their own direction instead.
        // Left in, they both fragmented and were swallowed by the upright lines they cross.
        List<Line> stamp = stampLines(glyphs);
        if (!stamp.isEmpty()) {
            java.util.IdentityHashMap<Glyph, Boolean> inStamp = new java.util.IdentityHashMap<>();
            for (Line sl : stamp) for (Glyph g : sl.glyphs) inStamp.put(g, Boolean.TRUE);
            List<Glyph> rest = new ArrayList<>(glyphs.size());
            for (Glyph g : glyphs) if (!inStamp.containsKey(g)) rest.add(g);
            glyphs = rest;
        }
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
        float prevY = 0;
        for (Glyph g : sorted) {
            // 30% of the font size merges two PDF lines whenever the leading is tight, and a
            // superscript with its body. PyMuPDF keeps them apart, so a merged line is a line
            // the reference has that we do not - the largest single cause of lines present in
            // the output but not on a line of their own.
            float tol = Math.max(0.9f, g.size * 0.18f);
            // Compare against the PREVIOUS glyph, not the first one on the line. A stamp is
            // often drawn very slightly rotated, so each character sits a fraction of a point
            // lower than the one before: 'P' 547.91, 'M' 548.50, 'C' 549.25. Measured from the
            // first glyph the drift passes the 0.96 pt tolerance by the third character, and
            // "PMC" came out as P / M / C on three lines - the vertical smear the user saw.
            // Comparing to the previous glyph keeps a gradual drift together while a real line
            // break, which is several points, still starts a new line.
            // Along a rotated run the part of the step that is the baseline's own slope is
            // geometry, not a fault. It is only excused when the run advances forwards: a new
            // line of a rotated block starts back at its left edge, where the step is the
            // leading and nothing is excused.
            if (current == null || Math.abs(g.y - prevY) > tol) {
                current = new Line();
                current.glyphs.add(g);
                baseY = g.y;
                lines.add(current);
            } else {
                current.glyphs.add(g);
            }
            prevY = g.y;
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
            int pageNoAt = pageNumberSplit(raw.glyphs);
            int gi = -1;
            // A justified line is full of wide word gaps, so a plain "gap is big" test cut
            // sentences in half. The gap that separates two real fields is an outlier on its
            // own line - far wider than the gaps between the words around it.
            java.util.List<Float> gaps = new java.util.ArrayList<>();
            for (int k = 1; k < raw.glyphs.size(); k++) {
                Glyph a = raw.glyphs.get(k - 1), b = raw.glyphs.get(k);
                gaps.add(b.x - (a.x + a.width));
            }
            java.util.Collections.sort(gaps);
            float median = gaps.isEmpty() ? 0f : gaps.get(gaps.size() / 2);
            // Measured: 1.15 -> 87.55 hit, 1.6 -> 86.77, 0.85 -> 89.06, 0.75 -> 88.65, 0.6 -> 87.72.
            // The best of five settings tried on the full corpus. A split costs one space and
            // gains a line break, so the line metrics rise faster than char volume falls.
            float outlier = Math.max(6f, median * 0.85f);
            boolean splitBefore = false;
            for (Glyph g : raw.glyphs) {
                gi++;
                if (prev != null && gi == pageNoAt) {
                    segments.add(run);
                    run = new ArrayList<>();
                }
                // A gap counts however it is signed: a baseline cluster holds glyphs that are
                // not in x order, and on file 46 the chart's "57.3" (x=226) and "56.9" (x=304)
                // sit 1 pt apart in y, so they clustered into one line whose second half lay
                // 66 pt to the LEFT. The gap then read as -78 and only the positive test saw
                // it, so the line was never cut: the box kept the first label's width, the
                // second was clipped away, and the reader lost a number off the chart.
                float gapPts = prev == null ? 0f : g.x - (prev.x + prev.width);
                // Signed, not positive. The comment above has described this for a while and
                // the code did not do it: a baseline cluster does not hold its glyphs in x
                // order, so on 350_question_paper the marks column "[08]" (x=551.9) came
                // first and the question (x=50) second, the gap read -520, the positive test
                // saw nothing, and the two became one line reading "[08] Write SQL queries".
                boolean wideGap = prev != null && gapPts > outlier;
                boolean overlap = OS && prev != null && !g.rotated && !prev.rotated
                        && Math.abs(g.y - prev.y) <= 0.5f
                        && (g.x - (prev.x + prev.width)) < -Math.max(2f, g.size * OVF);
                if (prev != null && (wideGap || overlap
                        || crossesGutter(gutters, prev.x + prev.width, g.x))) {
                    segments.add(run);
                    run = new ArrayList<>();
                    splitBefore = wideGap;
                }
                run.add(g);
                prev = g;
            }
            if (!run.isEmpty()) segments.add(run);

            // A right-to-left baseline reads from its right edge, so the fields standing on it
            // are ordered from the right as well. Sorting them left to right mirrored every
            // table row on the Arabic document - the amount before the item number, and the
            // header read "المبلغ السعر الكمية الوصف البند" against "البند الوصف الكمية السعر المبلغ".
            if (segments.size() > 1 && rtlDominant(raw.glyphs)) Collections.reverse(segments);

            // A baseline cut into more than one segment is several fields, not one sentence.
            // None of those segments may be merged back into the line above it - that is what
            // turned a question and its marks column into "[08] Explain the concept ...".
            boolean cutHere = segments.size() > 1;
            for (List<Glyph> segment : segments) {
                // A segment can be empty when a cut lands exactly on a boundary. Reading its
                // first glyph threw IndexOutOfBounds and took the whole conversion down - 41
                // files in the corpus died this way before this guard existed.
                if (segment.isEmpty()) continue;
                Line line = new Line();
                line.hardEnd = cutHere;
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
                line.rotated = allRotated(segment);
                split.add(line);
            }
        }
        // A baseline that holds nothing but vowel signs is not a line of text. Arabic sets a
        // tanween a few points off the baseline of the letter it decorates, so it clustered on
        // its own and the Arabic document gained three lines that are a bare "ً" - and, worse,
        // pushed every line after them one place out of step with the reference.
        List<Line> kept = new ArrayList<>(split.size());
        for (Line ln : split) if (!markOnly(ln.text)) kept.add(ln);
        split = kept;
        split.addAll(ring);
        split.addAll(stamp);
        return split;
    }

    /** True when a string carries nothing a reader would see: spaces and combining marks only. */
    private static boolean markOnly(String s) {
        if (s == null) return false;
        boolean sawMark = false;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (Character.isWhitespace(c)) continue;
            int t = Character.getType(c);
            if (t != Character.NON_SPACING_MARK && t != Character.COMBINING_SPACING_MARK
                    && t != Character.ENCLOSING_MARK) return false;
            sawMark = true;
        }
        return sawMark;
    }

    /**
     * The characters of a seal drawn as a ring, one line each, in drawing order.
     *
     * <p>A round seal sets every character on its own tangent, so the left of the ring runs
     * one way along its baseline and the right side runs the opposite way: on the certificate
     * page "S" has direction (0, 1) and "G" has (0, -1). A line of text cannot do that - a
     * line has one direction - so two opposing baselines among the rotated glyphs is proof
     * that the page draws a ring. A stamp, however many of them a page carries, is rotated one
     * way only, and is left to the ordinary clustering.
     *
     * <p>Clustered by baseline instead, the ring came out as pairs of unrelated letters welded
     * together - "G NA", "O Y", "L I V" - because the two sides of the ring meet at the same
     * height: file 60 read 35.40 on line order and lost 15 of its 64 lines.
     */
    private static List<Line> ringLines(List<Glyph> glyphs) {
        List<Line> out = new ArrayList<>();
        List<Glyph> rot = new ArrayList<>();
        for (Glyph g : glyphs) if (g.rotated) rot.add(g);
        if (rot.size() < 8) return out;
        boolean ring = false;
        for (int i = 0; i < rot.size() && !ring; i++) {
            Glyph a = rot.get(i);
            for (int j = i + 1; j < rot.size(); j++) {
                Glyph b = rot.get(j);
                if (a.dirx * b.dirx + a.diry * b.diry <= -0.5f) { ring = true; break; }
            }
        }
        if (!ring) return out;
        for (Glyph g : rot) {
            if (g.text == null || g.text.trim().isEmpty()) continue;
            Line line = new Line();
            line.glyphs.add(g);
            line.text = g.text;
            line.size = g.size;
            // Page coordinates: x and y are measured along a rotated glyph's own baseline and
            // are not comparable between two characters of a ring.
            line.x = g.px;
            line.y = g.py;
            line.left = g.px;
            line.right = g.px + Math.max(g.width, 1f);
            line.bottom = g.py + g.size;
            line.length = Math.max(g.width, 1f);
            line.rotated = true;
            line.ring = true;
            line.hardEnd = true;
            out.add(line);
        }
        return out;
    }

    /**
     * One paragraph holding every character of the ring, one per line, in drawing order.
     *
     * <p>One paragraph, not forty: a .txt writes a paragraph's lines as they come, so this is
     * what keeps the ring's characters together and in the order the page drew them instead of
     * scattering them through the body by their heights.
     */
    private static Para ringPara(List<Line> ring) {
        Para p = new Para();
        float l = Float.MAX_VALUE, r = -Float.MAX_VALUE, top = Float.MAX_VALUE;
        StringBuilder sb = new StringBuilder();
        for (Line ln : ring) {
            l = Math.min(l, ln.x);
            r = Math.max(r, ln.right);
            top = Math.min(top, ln.y);
            String t = ln.text.trim();
            if (t.isEmpty()) continue;
            p.lines.add(t);
            sb.append(t);
        }
        p.left = l == Float.MAX_VALUE ? 0f : l;
        p.right = r == -Float.MAX_VALUE ? 0f : r;
        p.top = top == Float.MAX_VALUE ? 0f : top;
        p.column = 0;
        Glyph lead = ring.get(0).glyphs.isEmpty() ? null : ring.get(0).glyphs.get(0);
        if (!p.lines.isEmpty()) {
            p.runs.add(new Run(sb.toString(), false, false, ring.get(0).size,
                    lead == null || lead.font == null ? "" : lead.font,
                    lead == null ? -1 : lead.color));
        }
        for (Line ln : ring) {
            if (ln.text.trim().isEmpty()) continue;
            Box box = new Box();
            box.x = ln.x;
            box.y = ln.y;
            box.right = ln.right;
            box.size = ln.size;
            box.bottom = ln.bottom;
            box.length = ln.length;
            box.rotated = ln.rotated;
            box.angle = ln.angle;
            box.runs.addAll(runsOf(ln));
            p.boxes.add(box);
        }
        return p;
    }

    private static String textOf(List<Glyph> glyphs) {
        StringBuilder sb = new StringBuilder();
        Glyph prev = null;
        for (Glyph g : glyphs) {
            if (prev != null) {
                float gap = g.x - (prev.x + prev.width);
                // A gap is a space. A negative gap means the next run starts inside the last
                // one - text that ran past its cell - and the two must not be welded together.
                //
                // A glyph with no advance of its own is not a word boundary. A Devanagari vowel
                // sign is drawn as a zero-width mark placed BACK over the consonant it belongs
                // to and the next consonant then starts forward of it, so the gap measured
                // after the mark is a real distance that means nothing: the pair was one
                // cluster. Measured on file 40, "ke" + "TT/2025/4471" was cut into
                // "ke TT/2025/4471" - a space inside a word - because the mark "e" carries
                // width 0 and the following "TT" sat 2.39 pt (0.217 em) past it. The same
                // split hit the Devanagari table (76) and the mixed-script line (78).
                // The word-boundary test uses the size to a whole point, not the exact size.
                // A page that letterspaces its capitals by about a fifth of an em sits exactly
                // on this threshold, and reading the size more precisely (5.8 instead of 5)
                // moved the boundary under it: on 39_small_caps_letter_spacing the same line
                // came out "E L E C T ION OF T HE MANAGING" where it had been every letter
                // apart. The threshold decides where a word ENDS, which is a coarser question
                // than how tall the glyph is; rounding it keeps the grouping stable.
                float gs = g.sizePt > 0f ? g.sizePt : Math.max(1f, Math.round(g.size));
                boolean prevAdvances = prev.width > prev.size * 0.05f;
                if (prevAdvances
                        && (gap > gs * 0.18f || gap < -gs * 0.6f)
                        && !endsWithSpace(sb)) {
                    sb.append(' ');
                }
            }
            sb.append(g.text);
            prev = g;
        }
        return logicalOrder(sb.toString());
    }


    /**
     * Where a running head should be cut, or -1.
     *
     * <p>A running head puts the title and the page number on one baseline with most of the
     * page between them, and they came out as one line: "Meridian Consulting - Internal Page 1".
     * Splitting every wide gap also fixed that, but it cut a question paper's heading in half,
     * so the gap alone is not the test. The cut happens only where the tail is a page number -
     * "Page 12", "12", "12 of 30", "- 12 -" - which is what a running head always ends with.
     */
    private static int pageNumberSplit(List<Glyph> line) {
        if (line == null || line.size() < 2) return -1;
        for (int i = 1; i < line.size(); i++) {
            Glyph prev = line.get(i - 1);
            Glyph g = line.get(i);
            float gap = g.x - (prev.x + prev.width);
            if (gap < 24f) continue;
            StringBuilder tail = new StringBuilder();
            for (int k = i; k < line.size(); k++) tail.append(line.get(k).text);
            String t = tail.toString().trim();
            // A page number, an author line and a marks column all sit far from what comes
            // before them on the same baseline. Each is a short standalone token, so each is
            // cut away rather than glued on - the reference keeps them on their own lines.
            if (t.matches("(Page\\s+)?\\d{1,4}(\\s+of\\s+\\d{1,4})?")
                    || t.matches("-\\s*\\d{1,4}\\s*-")
                    || t.matches("\\[\\d{1,3}\\]")
                    || t.matches("[A-Z]\\.\\s*[A-Z][\\p{L}\\-]{1,20}")) {
                return i;
            }
        }
        return -1;
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
        xyCut(items, out, minGap, 0);
    }

    /**
     * @param depth how many cuts deep we already are. Each cut can shave a single item off, so
     *              a page with thousands of blocks would recurse thousands of frames deep and
     *              take the stack with it. Past the limit the rest is read top to bottom, which
     *              is what the uncut branch does anyway.
     */
    private static void xyCut(List<Object> items, List<Object> out, float minGap, int depth) {
        if (items.size() <= 1 || depth > 40) {
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
            xyCut(new ArrayList<>(byX.subList(0, bestVi)), out, minGap, depth + 1);
            xyCut(new ArrayList<>(byX.subList(bestVi, byX.size())), out, minGap, depth + 1);
        } else if (hValid && bestH >= horizontalFloor && bestHi > 0) {
            xyCut(new ArrayList<>(byY.subList(0, bestHi)), out, minGap, depth + 1);
            xyCut(new ArrayList<>(byY.subList(bestHi, byY.size())), out, minGap, depth + 1);
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
        // A quarter of the page is far too strict. On a three-column newspaper only the lines
        // that span a gutter carry a gap at that x, so the evidence for a real column came from
        // a minority of lines and the page came out with no columns at all - the two columns
        // then interleaved line by line. A tenth is enough to be a column and still too many to
        // be a wide space inside one cell.
        int need = Math.max(3, Math.round(lines.size() * 0.10f));
        List<Float> kept = new ArrayList<>();
        for (Float c : candidates) {
            int key = Math.round(c);
            int seen = 0;
            // Ragged column starts drift a few points from line to line, so the window has to
            // be wider than the rounding error of one glyph.
            for (int dx = -6; dx <= 6; dx++) {
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
     * True when this page's columns are fields on a row, not text in a column.
     *
     * <p>A claim form puts a label at x=60 and its value at x=300, and both sit on the same
     * baseline. Reading it column by column gives every label and then every value, which is
     * not the page: measured on the 80-document batch, six form pages scored 52.6 to 84.0 % on
     * line order and reached 100 % when the columns were ignored. A two-column newspaper is the
     * opposite - its columns are independent flows - and ignoring its columns costs it up to
     * 56 points, so the two cannot be told apart by "is there a column start".
     *
     * <p>Two measurements separate them, and both are read off the page itself:
     *
     * <p>1. A drawn rule is a real column boundary. A journal sets its text flush against a
     * gutter rule, and on such a page the two columns share a baseline grid - the abstract-
     * spanning page pairs 91 % of its right-hand lines with a left-hand line and is still two
     * columns. Every page in the batch that has a rule gutter at the split (63, 66, 65, 61, 27,
     * 69, 54, 62) is a column page. Every page that reads row-major has none.
     *
     * <p>2. Paired baselines. A form's value sits on the same baseline as its label, so nearly
     * every right-hand segment has a left-hand neighbour on its own line. Prose columns drift:
     * each column flows on its own, and only a handful of baselines happen to coincide. Measured
     * over the 84 pages of the batch, the row-major pages pair 0.93 to 1.00 of their right-hand
     * segments and the column pages pair 0.24 to 0.88. The threshold sits in the gap.
     */
    private static boolean rowMajor(List<Line> body, List<Float> starts, Rules rules,
                                    float pageHeight) {
        if (starts.isEmpty()) return false;
        for (Float s : starts) {
            for (float[] v : rules.vertical) {
                if (Math.abs(v[0] - s) <= 3f && Math.abs(v[2] - v[1]) >= pageHeight * 0.30f) {
                    return false;
                }
            }
        }
        float splitX = starts.get(0);
        int right = 0, paired = 0;
        List<Line> base = new ArrayList<>();
        for (Line l : body) {
            if (l.text.trim().isEmpty()) continue;
            base.add(l);
        }
        Collections.sort(base, new Comparator<Line>() {
            @Override
            public int compare(Line a, Line b) {
                int c = Float.compare(a.y, b.y);
                return c != 0 ? c : Float.compare(a.x, b.x);
            }
        });
        int i = 0;
        while (i < base.size()) {
            int j = i;
            while (j < base.size() && base.get(j).y - base.get(i).y <= 2.5f) j++;
            if (j - i > 1) {
                for (int k = i; k < j; k++) {
                    if (base.get(k).x >= splitX - 2f) { right++; paired++; }
                }
            } else if (base.get(i).x >= splitX - 2f) {
                right++;
            }
            i = j;
        }
        if (right == 0) return false;
        return paired / (float) right >= 0.90f;
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

    /**
     * Numbers the vertical slices of a page, split at every full-width line.
     *
     * <p>A line wider than 62 % of the content span is one the page drew across the measure - the
     * same rule keep0 uses to spot a spanning line. Each such line ends the slice above it and is
     * a slice of its own, so the order becomes: columns above, the spanning element, columns
     * below. Measured need: 21 of the 24 multi-column documents in the corpus carry a spanning
     * element, 69 of them in all, and ordering by column first put every one of those elements
     * after the columns instead of between them.
     */
    private static void assignSegments(List<Line> lines) {
        if (lines.isEmpty()) return;
        float minX = Float.MAX_VALUE, maxX = -Float.MAX_VALUE;
        for (Line l : lines) { minX = Math.min(minX, l.x); maxX = Math.max(maxX, l.right); }
        float span = maxX - minX;
        if (span <= 0f) return;
        java.util.List<Line> byY = new java.util.ArrayList<>(lines);
        java.util.Collections.sort(byY, new java.util.Comparator<Line>() {
            public int compare(Line a, Line b) { return Float.compare(a.y, b.y); }
        });
        int seg = 0;
        boolean prevWasSpan = false;
        for (Line l : byY) {
            boolean spans = !l.rotated && l.right - l.x > span * 0.62f;
            if (spans) {
                seg++;
                l.segment = seg;
                seg++;
                prevWasSpan = true;
            } else {
                l.segment = seg;
                prevWasSpan = false;
            }
        }
    }

    private static List<Para> toParagraphs(List<Line> lines, float pageWidth, int bands) {
        return toParagraphs(lines, pageWidth, bands, false);
    }

    private static List<Para> toParagraphs(List<Line> lines, float pageWidth, int bands,
                                           final boolean row) {
        List<Para> out = new ArrayList<>();
        if (lines.isEmpty()) return out;

        // Fields on one baseline, before the column order can separate them. A row is a row
        // whichever column its fields were put in, and the sort below is by column first, so
        // without this the title of a page arrives after the whole left block instead of on
        // the line the page drew it. Only a line in a DIFFERENT column is attached, and only
        // when sameRow() already accepts the pair - that predicate holds the rule for what
        // makes two fields one row (a wide gap, no rule between them, no paper between them),
        // and it is the same predicate the grouping below uses, so nothing new is decided here.
        if (!row) {
            for (Line a : lines) {
                if (a.rotated || a.mate) continue;
                for (Line b : lines) {
                    if (b == a || b.rotated || b.mate) continue;
                    if (b.column == a.column) continue;
                    if (b.x < a.x) continue;
                    if (!sameRow(a, b, pageWidth, 0)) continue;
                    if (a.rowMates == null) a.rowMates = new ArrayList<>();
                    a.rowMates.add(b);
                    b.mate = true;
                }
            }
        }

        if (!row) assignSegments(lines);
        Collections.sort(lines, new Comparator<Line>() {
            @Override
            public int compare(Line a, Line b) {
                if (row) {
                    int c0 = Float.compare(a.y, b.y);
                    return c0 != 0 ? c0 : Float.compare(a.x, b.x);
                }
                int seg = Integer.compare(a.segment, b.segment);
                if (seg != 0) return seg;
                int c = Integer.compare(a.column, b.column);
                return c != 0 ? c : Float.compare(a.y, b.y);
            }
        });

        // The right edge of the text block, not of the line: contentRight() used to be built
        // from the line itself, so "the line reached the margin" was always true and no
        // paragraph ever ended.
        float blockRight = -Float.MAX_VALUE;
        for (Line ln : lines) if (!ln.text.trim().isEmpty()) blockRight = Math.max(blockRight, ln.right);

        List<Line> group = new ArrayList<>();
        for (Line line : lines) {
            if (line.text.trim().isEmpty()) continue;
            if (line.mate) continue;
            if (group.isEmpty()) {
                group.add(line);
                addRowMates(group, line);
                continue;
            }
            Line last = group.get(group.size() - 1);
            // A row is measured against its own field on this baseline; prose is measured
            // against the line above it, which is what sameParagraph() is about. Using the
            // row's field for both stopped a paragraph continuing: the line above and the
            // field beside it share a baseline, so the y-gap a paragraph needs was zero.
            if (sameRow(prevOnBaseline(group, line), line, pageWidth, rowWidth(group, line))) {
                group.add(line);
            } else if (sameParagraph(last, line, pageWidth, blockRight)) {
                group.add(line);
            } else {
                out.add(buildPara(group, pageWidth, bands));
                group = new ArrayList<>();
                group.add(line);
                addRowMates(group, line);
            }
        }
        if (!group.isEmpty()) out.add(buildPara(group, pageWidth, bands));
        return out;
    }

    /**
     * The line of {@code group} that a new line should be measured against.
     *
     * <p>Usually the last line added, and that is what this returns when the group holds no
     * field to the left of the new line on its baseline. The exception is a row: once a field
     * from another column has been attached to it, the group's last line is that field, and
     * {@link #sameRow} rejects a field that begins to the LEFT of the one it is compared with.
     * So a row whose left-hand fields came later in the column order - the "Account holder /
     * NIRVAAN PACKAGING INDUSTRIES / Account no. 50100234567890" of a bank statement, the
     * "NAV (GROWTH) / AUM / EXPENSE RATIO / FUND MANAGER" header of a fund factsheet - was cut
     * in two, one row plus its own tail, one pair of paragraphs per baseline. Measuring the new
     * line against the group's last field that stands on its baseline and ends before it begins
     * lets a row grow to the right whatever order its fields were offered in.
     *
     * <p>Measured on the 208-document corpus: 16520 paragraphs with text became 16467, 10
     * documents lost paragraphs, none gained one (bank-statement-5-pages 560 -> 545,
     * 63_three_column_brochure 29 -> 16, brochure-3col-with-sidebar-box 57 -> 44,
     * 322_mutual_fund_factsheet 82 -> 80). {@code sameRow} still decides what a row is;
     * nothing here widens it.
     */
    private static Line prevOnBaseline(List<Line> group, Line next) {
        Line last = group.get(group.size() - 1);
        Line best = null;
        for (Line g : group) {
            if (g.x > next.x) continue;
            float size = Math.max(g.size, next.size);
            if (Math.abs(g.y - next.y) > Math.max(1.2f, size * 0.25f)) continue;
            if (best == null || g.x > best.x) best = g;
        }
        return best == null ? last : best;
    }

    /**
     * Puts the fields standing on {@code line}'s baseline into the paragraph it starts.
     *
     * <p>Only a paragraph of one line takes mates: a paragraph that already flows over several
     * baselines is prose, and a field from another column belongs beside its own line, not at
     * the end of a sentence. That distinction is what D-07 lost when the fields were joined
     * with a space - "Certificate under section 203 ... PART B" - instead of being written as
     * a row. Here they stay separate lines of one group, so {@code buildPara} sorts them by x
     * and the writer sets each at its own measured x with a tab stop.
     */
    private static void addRowMates(List<Line> group, Line line) {
        if (group.size() != 1 || line.rowMates == null) return;
        List<Line> mates = new ArrayList<>(line.rowMates);
        Collections.sort(mates, new Comparator<Line>() {
            @Override
            public int compare(Line a, Line b) {
                return Float.compare(a.x, b.x);
            }
        });
        for (Line m : mates) {
            m.mate = true;
            group.add(m);
        }
    }

    /** True when every line of the group stands on the same baseline. */
    private static boolean isRow(List<Line> group) {
        Line first = group.get(0);
        for (Line ln : group) {
            float size = Math.max(first.size, ln.size);
            if (Math.abs(ln.y - first.y) > Math.max(1.2f, size * 0.25f)) return false;
        }
        return true;
    }

    /**
     * How many fields of one row are allowed to become tab stops.
     *
     * <p>This is a runaway guard, not a column limit. A row that has more fields than this
     * loses its tail to a paragraph of its own, and because the paragraph carries the y the
     * page measured for it while the row above is spaced to its own height, the orphan is
     * laid over the row beneath - two rows of a job-work statement printed on top of each
     * other. Seven fields is an ordinary accounting line (month, quantity, rate, amount, tax,
     * total, invoice value), so the guard sits above that. It still stops a page-wide line of
     * prose being chopped into a dozen tab stops.
     */
    private static final int MAX_ROW_FIELDS = 9;
    /**
     * How much larger one field of a row may be than another before they stop being one row.
     *
     * <p>Two fields on one baseline are one row whatever size they are set at: a masthead and
     * the date beside it, a letterhead and its strapline, a price list's heading and its note.
     * The test used to be 30 % - near enough to demand the two be set at the same size - so the
     * smaller field was never joined to the row. It became a paragraph of its own and landed a
     * whole line box below where the page drew it, taking every line after it with it: 62 +28 pt,
     * 63 +29 pt, 70 +13 pt. What makes a row is a shared baseline, and that is tested above;
     * size is not what makes a row. The bound stays because a row's tab stops are measured from
     * its first box, and a caption three times the height of the heading beside it is a different
     * kind of page - a poster, not a letterhead.
     */
    private static final float ROW_SIZE_RATIO = 2.5f;
    /** Above this ratio the two fields must be separated by ROW_FIELD_GAP_PT, not cell padding. */
    private static final float ROW_SIZE_SAME = 1.3f;
    /** The smallest white space that separates two fields rather than two cells of a table. */
    private static final float ROW_FIELD_GAP_PT = 12f;

    /**
     * True when {@code next} is another field drawn on the same baseline as {@code prev} - the
     * "Member Name" / ":" / "Ananya Rangappa" of a form, the four headings of a table.
     *
     * <p>These are one line of the document, not three. {@link #toLines} has to cut a baseline
     * into segments so that two newspaper columns do not weld together, and the paragraph
     * builder then treated each segment as its own paragraph. Word writes one paragraph per
     * line, so a 22-row form became 66 paragraphs and ran onto a second sheet - file 21's
     * one-page claim form spilled to two pages, with the value stranded far below its label.
     *
     * <p>The two segments are rejoined here, and only here, so that the writer can put them on
     * one line with a tab stop at the x the page measured. Nothing is dropped, reordered or
     * restyled: the fragments stay separate {@link Box}es and keep their own x and y.
     */
    private static boolean sameRow(Line prev, Line next, float pageWidth, int sofar) {
        if (sofar >= MAX_ROW_FIELDS) return false;
        // A rotated line has no horizontal baseline to share, and a stamp is an overlay.
        if (prev.rotated || next.rotated) return false;
        float size = Math.max(prev.size, next.size);
        if (Math.abs(prev.y - next.y) > Math.max(1.2f, size * 0.25f)) return false;
        // Size is not what makes a row - the shared baseline above is. See ROW_SIZE_RATIO.
        if (size > Math.min(prev.size, next.size) * ROW_SIZE_RATIO) return false;
        if (startsWithBullet(next.text)) return false;
        if (prev.column != next.column) {
            // A label and its value can stand either side of a detected gutter: file 21 puts
            // every label in column 0 and every value in column 1, so the column test alone
            // kept them apart and the form still had two lines per row. They are one line.
            //
            // What tells that apart from two columns of running text is the white space: a
            // label ends far short of the gutter and leaves 180 pt of nothing before its
            // value, while a gutter between two columns of prose is 20-30 pt and the line on
            // the left runs right up to it. Only the wide gap may cross a column boundary.
            float across = next.x - prev.right;
            if (across < Math.max(40f, size * 3f)) return false;
        }
        // A fragment that starts to the LEFT of where the previous one began is not a field of
        // this row; leave it where it is.
        if (next.x < prev.x - 0.5f) return false;
        // A fragment that begins inside the field before it and ends inside it too is part of
        // that field, not a new column: file 21 draws its colon at x=65 while "Member Name"
        // runs 60..117, so the colon is painted over the label and the reader never sees it.
        // It belongs on the row, but it must not become a tab stop - a stop behind the text is
        // skipped by Word and the next field would jump.
        boolean inside = next.x < prev.right - 0.5f && next.right <= prev.right + size;
        if (inside) return true;
        // Otherwise there has to be white space between the two fields, or the tab stop has
        // nothing to move the text to.
        float gap = next.x - prev.right;
        if (gap < Math.max(1.5f, size * 0.15f)) return false;
        // A tab stop past the paper is not a tab stop. Word would push the value onto the next
        // line, which is the defect this merge exists to remove.
        if (next.right > pageWidth + 1f) return false;
        // A row whose fields are set at DIFFERENT sizes needs a real gap between them: a masthead
        // and the date beside it, a letterhead and its strapline. Two cells of a table are set at
        // different sizes too, but a rule separates them and the gap is 2-6 pt of cell padding -
        // joining those changed the row heights of table-with-rotated-header and moved two of its
        // rows 6.7 and 11.6 pt off the page. The gap is what tells a field from a cell.
        if (size > Math.min(prev.size, next.size) * ROW_SIZE_SAME && gap < ROW_FIELD_GAP_PT) {
            return false;
        }
        return true;
    }

    /** How many lines of {@code group} already stand on {@code next}'s baseline. */
    private static int rowWidth(List<Line> group, Line next) {
        int n = 0;
        for (int i = group.size() - 1; i >= 0; i--) {
            Line ln = group.get(i);
            if (Math.abs(ln.y - next.y) > Math.max(1.2f, Math.max(ln.size, next.size) * 0.25f)) {
                break;
            }
            n++;
        }
        return n;
    }

    /** Characters that begin a list item. */
    private static boolean startsWithBullet(String text) {
        String t = text.trim();
        if (t.isEmpty()) return false;
        char c = t.charAt(0);
        return c == '\u2022' || c == '\u25e6' || c == '\u25aa' || c == '\u25ab'
                || c == '\u2023' || c == '\u00b7' || c == '\u2043';
    }

    private static boolean sameParagraph(Line prev, Line next, float pageWidth, float blockRight) {
        if (prev.column != next.column) return false;
        // A bullet starts its own item. Its glyph is often set larger than the words beside
        // it, which made the alignment test pass and swallowed three advice lines into one.
        if (startsWithBullet(next.text)) return false;
        float gap = next.y - prev.y;
        float size = Math.max(prev.size, next.size);
        if (gap <= 0 || gap > size * 1.75f) return false;
        if (Math.abs(prev.size - next.size) > size * 0.18f) return false;

        // A paragraph continues only if the line above ran on to the margin. Left alignment
        // alone is not enough: an invoice header has six left-aligned lines that are six
        // different fields, and merging them put the whole header into one paragraph.
        // A line that was cut out of a longer one at a wide gap is its own field, so the line
        // after it never joins it.
        if (prev.hardEnd) return false;
        boolean continues = prev.right >= blockRight - size * 2.5f;
        boolean indented = next.x > prev.x + size * 1.2f;
        return continues && !indented;
    }

    private static Para buildPara(List<Line> group, float pageWidth, int bands) {
        // Fields on one baseline read left to right, whatever order the page drew them in. The
        // row's tab stops are measured from its first box, so the box order IS the line.
        if (group.size() > 1 && isRow(group)) {
            List<Line> byX = new ArrayList<>(group);
            Collections.sort(byX, new Comparator<Line>() {
                @Override
                public int compare(Line a, Line b) {
                    return Float.compare(a.x, b.x);
                }
            });
            group = byX;
        }
        float l = Float.MAX_VALUE, r = -Float.MAX_VALUE;
        for (Line ln : group) { l = Math.min(l, ln.x); r = Math.max(r, ln.right); }
        Para p = new Para();
        p.left = l;
        p.right = r;
        p.top = group.get(0).y;
        p.column = group.get(0).column;
        p.stamp = true;
        for (Line ln : group) if (!ln.rotated) { p.stamp = false; break; }

        StringBuilder sb = new StringBuilder();
        String prevText = null;
        for (Line line : group) {
            String t = line.text.trim();
            if (t.isEmpty()) continue;
            // The raw line and the coordinates it was drawn at. Turning x into leading spaces
            // used to happen here, relative to the paragraph's own left - so a paragraph that
            // was one line long always got zero indent and its position was lost. The padding
            // is now worked out in writeTxt() against the page, which is the only consumer.
            p.lines.add(t);
            p.lineX.add(line.x);
            p.lineY.add(line.y);
            p.lineSize.add(line.size);
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
        if (text.length() > 0) {
            // carry the typeface and the colour of the run's first glyph
            Glyph lead = first.glyphs.isEmpty() ? null : first.glyphs.get(0);
            String face = (lead == null || lead.font == null) ? "" : lead.font;
            int col = lead == null ? -1 : lead.color;
            p.runs.add(new Run(text, bold, italic, size, face, col));
        }

        // The same words again, line by line, carrying the page's own coordinates and each
        // line's own styling. This is what lets the writer put a value back at x=300 instead
        // of at "indent 4".
        boolean rowGroup = group.size() > 1 && isRow(group);
        for (Line line : group) {
            if (line.text.trim().isEmpty()) continue;
            Box box = new Box();
            box.x = line.x;
            box.y = line.y;
            box.right = line.right;
            box.size = line.size;
            box.bottom = line.bottom;
            box.length = line.length;
            box.rotated = line.rotated;
            box.angle = line.angle;
            List<Run> lineRuns = coalesceRuns(runsOf(line));
            // A fragment that opens with a combining mark is not a line of its own - it is the
            // tail of the word the previous fragment began. The page draws "केवल" as one line,
            // but the converter cuts a line wherever the typeface changes, and the cut can land
            // inside a cluster: "क" then "ेवल", "पंजीक" then "ृत". Each fragment became its
            // own anchored text box, so Word opened the second one with a lone vowel sign and
            // drew the dotted circle a missing consonant gets - file 78 reached Word as
            // "के◌वल" and "पंजीकृ◌त". Joining the tail back onto the box it belongs to keeps the
            // cluster in one paragraph, where a shaping engine can see it whole.
            Box prevBox = p.boxes.isEmpty() ? null : p.boxes.get(p.boxes.size() - 1);
            if (prevBox != null && startsWithCombiningMark(line.text)
                    && Math.abs(prevBox.y - line.y) <= Math.max(2f, line.size * 0.5f)) {
                prevBox.runs.addAll(lineRuns);
                prevBox.right = Math.max(prevBox.right, line.right);
                prevBox.bottom = Math.max(prevBox.bottom, line.bottom);
                prevBox.length = prevBox.right - prevBox.x;
                continue;
            }
            // A fragment of a row that starts inside the field before it is that field's own
            // tail, not a new column: it gets no tab stop of its own, it joins the field. The
            // space is what keeps the two words apart for a reader that only sees text - file
            // 21's label and its colon would otherwise weld into "Member Name:".
            if (rowGroup && prevBox != null
                    && Math.abs(prevBox.y - line.y) <= Math.max(1.2f, size * 0.25f)
                    && line.x < prevBox.right - 0.5f) {
                Run leadRun = lineRuns.get(0);
                prevBox.runs.add(new Run(" ", leadRun.bold, leadRun.italic, leadRun.sizePt,
                        leadRun.font, leadRun.color));
                prevBox.runs.addAll(lineRuns);
                prevBox.right = Math.max(prevBox.right, line.right);
                prevBox.bottom = Math.max(prevBox.bottom, line.bottom);
                prevBox.length = prevBox.right - prevBox.x;
                continue;
            }
            box.runs.addAll(lineRuns);
            p.boxes.add(box);
        }

        p.heading = headingLevel(group, text);
        p.align = alignment(group, pageWidth, bands);
        int indent = Math.max(0, Math.round((first.x - leftMargin(group)) / Math.max(8f, size * 1.6f)));
        p.indent = Math.min(indent, 4);
        p.bullet = bulletOf(text);
        if (p.bullet != null) p.indent = Math.max(1, p.indent);
        return p;
    }

    /**
     * True when the first character that is not a space is a combining mark - a Devanagari
     * matra, an Arabic harakah, a Thai vowel sign. Such a character has no base of its own and
     * a renderer that starts a paragraph with one draws a dotted circle in front of it.
     */
    private static boolean startsWithCombiningMark(String s) {
        if (s == null) return false;
        for (int i = 0; i < s.length(); ) {
            int cp = s.codePointAt(i);
            if (!Character.isWhitespace(cp) && cp != ' ') {
                int type = Character.getType(cp);
                return type == Character.NON_SPACING_MARK
                        || type == Character.COMBINING_SPACING_MARK
                        || type == Character.ENCLOSING_MARK;
            }
            i += Character.charCount(cp);
        }
        return false;
    }

    /**
     * Joins neighbouring runs that share every character property.
     *
     * <p>A run boundary inside a word is invisible in Latin text and fatal in a shaped script:
     * a renderer that shapes one run at a time cannot see that "क" and "ेवल" are one cluster.
     * Only runs whose bold, italic, size, typeface and colour all match are joined, so nothing
     * a reader can see changes.
     */
    private static List<Run> coalesceRuns(List<Run> in) {
        List<Run> out = new ArrayList<>(in.size());
        for (Run r : in) {
            if (r.text.isEmpty()) continue;
            if (!out.isEmpty()) {
                Run p = out.get(out.size() - 1);
                if (p.bold == r.bold && p.italic == r.italic && p.color == r.color
                        && Math.abs(p.sizePt - r.sizePt) < 0.01f && p.font.equals(r.font)) {
                    out.set(out.size() - 1, new Run(p.text + r.text, p.bold, p.italic,
                            p.sizePt, p.font, p.color));
                    continue;
                }
            }
            out.add(r);
        }
        return out;
    }

    /**
     * Splits one drawn line into runs by bold / italic / size / typeface / colour, putting
     * back the spaces the line's own gaps imply - the same rule {@link #textOf} uses.
     *
     * <p>When the rebuild does not reproduce the line's text character for character - bidi
     * reordering on an Arabic page, a ligature the page drew as two glyphs - the line is
     * emitted as a single run holding {@code line.text}. Losing the styling is recoverable;
     * losing or reordering a character is not.
     */
    private static List<Run> runsOf(Line line) {
        List<Run> out = new ArrayList<>();
        StringBuilder cur = new StringBuilder();
        String curKey = null;
        Glyph first = null, prev = null;
        char lastOut = 0;
        for (Glyph g : line.glyphs) {
            String key = g.bold + "|" + g.italic + "|" + Math.round(g.size * 4f) + "|"
                    + g.font + "|" + g.color;
            if (curKey == null) {
                curKey = key;
                first = g;
            } else if (!key.equals(curKey)) {
                out.add(new Run(cur.toString(), first.bold, first.italic, first.size,
                        first.font, first.color));
                cur.setLength(0);
                curKey = key;
                first = g;
            }
            if (prev != null) {
                float gap = g.x - (prev.x + prev.width);
                float gs = g.sizePt > 0f ? g.sizePt : Math.max(1f, Math.round(g.size));
                if ((gap > gs * 0.18f || gap < -gs * 0.6f) && lastOut != ' ') {
                    cur.append(' ');
                    lastOut = ' ';
                }
            }
            cur.append(g.text);
            if (g.text != null && !g.text.isEmpty()) lastOut = g.text.charAt(g.text.length() - 1);
            prev = g;
        }
        if (first != null) {
            out.add(new Run(cur.toString(), first.bold, first.italic, first.size,
                    first.font, first.color));
        }
        StringBuilder all = new StringBuilder();
        for (Run r : out) all.append(r.text);
        if (!all.toString().equals(line.text)) {
            Glyph lead = line.glyphs.isEmpty() ? null : line.glyphs.get(0);
            List<Run> one = new ArrayList<>();
            one.add(new Run(line.text,
                    lead != null && lead.bold,
                    lead != null && lead.italic,
                    line.size,
                    lead == null ? "" : lead.font,
                    lead == null ? -1 : lead.color));
            return one;
        }
        return out;
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
        /**
         * The stroke each horizontal rule was drawn with: {@code {widthPt, rgb, alpha}}, at the
         * SAME index as its rule in {@link #horizontal}.
         *
         * <p>D-22: a rule's weight and opacity are the page's own, and the model had nowhere to
         * keep them - a rule was three floats of geometry, so every table border downstream was
         * written at one constant weight and one constant colour however the page drew it.
         *
         * <p>These are PARALLEL lists, not wider arrays. Widening {@code {y, x1, x2}} to six
         * floats would silently misread at every existing reader of {@code rules.horizontal}
         * (there are eleven of them, in the column pass, the table passes and the row pass), and
         * a reader that does not know about the extra elements reads index 1 and 2 as the
         * segment's ends - a wrong answer, not a compile error. A list nobody reads yet cannot
         * break anybody. Add through {@link #addH} / {@link #addV} so the two lists stay in step.
         */
        final List<float[]> hStroke = new ArrayList<>();
        /** The stroke each vertical rule was drawn with, at the same index as {@link #vertical}. */
        final List<float[]> vStroke = new ArrayList<>();

        /** Records a horizontal rule and the stroke it was drawn with, index for index. */
        void addH(float[] rule, float[] stroke) {
            horizontal.add(rule);
            hStroke.add(stroke);
        }

        /** Records a vertical rule and the stroke it was drawn with, index for index. */
        void addV(float[] rule, float[] stroke) {
            vertical.add(rule);
            vStroke.add(stroke);
        }

        /** The stroke at a horizontal rule's index, or null when the lists have parted. */
        float[] hStrokeAt(int i) {
            return i >= 0 && i < hStroke.size() ? hStroke.get(i) : null;
        }

        /** The stroke at a vertical rule's index, or null when the lists have parted. */
        float[] vStrokeAt(int i) {
            return i >= 0 && i < vStroke.size() ? vStroke.get(i) : null;
        }

        int images;
        /**
         * The raster images the page draws, in draw order, with the rectangle each one covers.
         *
         * <p>Nothing used to read these: {@code images} was counted for the report and the
         * pixels were thrown away, so a scanned page converted to a blank Word page and a
         * stamped PDF lost its stamp. The rectangle is the image's own unit square put
         * through the transform in force when it was drawn, in PDF user space (y up).
         */
        final List<DocxWriter.Picture> pictures = new ArrayList<>();
        /**
         * The rectangles the page paints - bands, blocks, table header strips, sidebars,
         * drawn rules, page borders - in draw order, in PDF user space (y up).
         *
         * <p>These were never read: the collector kept only the straight edges it needed to
         * find tables, and every filled rectangle on every page was thrown away. A masthead
         * band is the clearest cost - file 54's title is white text on navy, so without the
         * band the document's own name converted to white on white.
         */
        final List<DocxWriter.Shape> shapes = new ArrayList<>();
    }

    private static final class RuleCollector extends PDFGraphicsStreamEngine {
        final Rules rules = new Rules();
        private final android.graphics.Path path = new android.graphics.Path();
        private float startX, startY, lastX, lastY;

        /**
         * The bounding box of the path being built, in PDF user space.
         *
         * <p>NaN, not 0, is the empty value. Seeding these at 0.0 made every first path
         * include the page origin, so a 64 pt masthead band came out as a rectangle from
         * (0,0) to the band's far corner and the page was painted solid.
         */
        private float pxMin = Float.NaN, pyMin = Float.NaN;
        private float pxMax = Float.NaN, pyMax = Float.NaN;
        /** What the path is made of - a rectangle, one straight line, or something curved. */
        private int pMoves, pLines, pCurves, pRects;
        /** How many rules the lists held when the current path started (see stampPathRules). */
        private int pathRulesH, pathRulesV;
        /** The single segment's own end points, for the axis-aligned line case. */
        private float segX0 = Float.NaN, segY0 = Float.NaN, segX1 = Float.NaN, segY1 = Float.NaN;
        /**
         * The path itself, one entry per operator, in PDF user space.
         *
         * <p>{@code {0,x,y}} move, {@code {1,x,y}} line, {@code {2,x1,y1,x2,y2,x3,y3}} cubic.
         * A path that is neither a rectangle nor an ellipse used to go out as its bounding box
         * - a triangle became a block, an arrowhead became a slab - or, when it was stroked
         * only, was dropped. The vertices are what lets the writer draw the shape the page drew.
         */
        private java.util.ArrayList<float[]> cmds = new java.util.ArrayList<>();
        /** Set once a path is too long to carry; it then falls back to its box as before. */
        private boolean cmdsOverflow;
        private boolean pathClosed;
        /** A path longer than this is a rasterised picture, not a shape worth a freeform. */
        private static final int MAX_CMDS = 512;
        /**
         * A path can begin without the previous one ever being closed, so the flags are reset
         * lazily at the first operator that adds geometry rather than trusted to be clean.
         * Trusting them dropped the first rule on a page.
         */
        private boolean pathStarted;
        /** The clip in force, as axis-aligned boxes. Bottom is the whole page. */
        private final java.util.ArrayDeque<float[]> clips = new java.util.ArrayDeque<>();
        /** The box a pending {@code W} asks for, applied when its path is painted. */
        private float[] pendingClip;

        RuleCollector(PDPage page) {
            super(page);
            PDRectangle box = page.getMediaBox();
            clips.push(new float[]{0f, 0f, box.getWidth(), box.getHeight()});
        }

        /**
         * {@code q} and {@code Q} save and restore the clip as part of the graphics state.
         *
         * <p>They have no callback on this engine, so the stack is kept here. Without it a
         * page that fills the whole sheet and clips it to a band kept the whole sheet.
         */
        @Override
        protected void processOperator(Operator operator, List<COSBase> arguments)
                throws IOException {
            String op = operator.getName();
            if ("q".equals(op)) {
                clips.push(clips.peek().clone());
            } else if ("Q".equals(op)) {
                if (clips.size() > 1) clips.pop();
            }
            super.processOperator(operator, arguments);
        }

        /** Forgets the path. Called whenever one is finished, and before a new one starts. */
        private void resetPath() {
            pxMin = pyMin = pxMax = pyMax = Float.NaN;
            segX0 = segY0 = segX1 = segY1 = Float.NaN;
            pMoves = pLines = pCurves = pRects = 0;
            cmds = new java.util.ArrayList<>();
            cmdsOverflow = false;
            pathClosed = false;
            // The rule lists' sizes at the start of this path: the rules this path adds are the
            // ones the paint operator will be told about when it arrives.
            pathRulesH = rules.horizontal.size();
            pathRulesV = rules.vertical.size();
        }

        /** Records one path operator, unless the path has grown past what a shape can carry. */
        private void cmd(float[] c) {
            if (cmdsOverflow) return;
            if (cmds.size() >= MAX_CMDS) {
                cmdsOverflow = true;
                cmds = new java.util.ArrayList<>();
                return;
            }
            cmds.add(c);
        }

        private void beginPath() {
            if (!pathStarted) {
                resetPath();
                pathStarted = true;
            }
        }

        private void grow(float x, float y) {
            if (Float.isNaN(pxMin)) {
                pxMin = pxMax = x;
                pyMin = pyMax = y;
                return;
            }
            if (x < pxMin) pxMin = x;
            if (x > pxMax) pxMax = x;
            if (y < pyMin) pyMin = y;
            if (y > pyMax) pyMax = y;
        }

        private boolean pathEmpty() {
            return Float.isNaN(pxMin) || Float.isNaN(pxMax);
        }

        /** The path's box, or null when it has no geometry. */
        private float[] pathBox() {
            return pathEmpty() ? null : new float[]{pxMin, pyMin, pxMax, pyMax};
        }

        /** The part of {@code r} that survives the clip, or null when none of it does. */
        private float[] clipped(float[] r) {
            if (r == null) return null;
            float[] c = clips.peek();
            float x0 = Math.max(r[0], c[0]), y0 = Math.max(r[1], c[1]);
            float x1 = Math.min(r[2], c[2]), y1 = Math.min(r[3], c[3]);
            if (x1 <= x0 || y1 <= y0) return null;
            return new float[]{x0, y0, x1, y1};
        }

        /** Applies a {@code W} that is waiting for its painting operator. */
        private void commitClip() {
            if (pendingClip == null) return;
            float[] c = clips.peek();
            float x0 = Math.max(pendingClip[0], c[0]), y0 = Math.max(pendingClip[1], c[1]);
            float x1 = Math.min(pendingClip[2], c[2]), y1 = Math.min(pendingClip[3], c[3]);
            pendingClip = null;
            if (x1 > x0 && y1 > y0) clips.push(new float[]{x0, y0, x1, y1});
        }

        /** A PDF colour as 0xRRGGBB, or -1 when it is a pattern or cannot be read. */
        private static int rgbOf(PDColor colour) {
            if (colour == null || colour.isPattern()) return -1;
            try {
                return colour.toRGB() & 0xFFFFFF;
            } catch (Throwable t) {
                return -1;
            }
        }

        /** True when the current transformation matrix rotates or skews, so a rect is not a rect. */
        private boolean ctmRotated() {
            com.tom_roush.pdfbox.util.Matrix m = getGraphicsState().getCurrentTransformationMatrix();
            if (m == null) return false;
            // PDFBox's Matrix is row-major with getValue(row, col). The translation lives at
            // (2,0)/(2,1) - NOT (0,2)/(1,2), which returns the wrong row - so the rotation and
            // shear terms are (0,1) and (1,0).
            return Math.abs(m.getValue(0, 1)) > 0.01f || Math.abs(m.getValue(1, 0)) > 0.01f;
        }

        /**
         * True when the path being built is one closed ellipse.
         *
         * <p>A circle or an ellipse is four Bezier curves that start and end on the same point;
         * a rounded rectangle adds the four straight sides between them, so the line count tells
         * the two apart. The box of such a path is the ellipse's own extent, because a quarter
         * arc's control points sit exactly on the extremes - so the extent needs no correction,
         * only the outline drawn inside it.
         */
        private boolean pathIsEllipse() {
            return pMoves == 1 && pCurves == 4 && pLines == 0 && pRects == 0
                    && Math.abs(lastX - startX) < 1.5f && Math.abs(lastY - startY) < 1.5f
                    && pxMax - pxMin > 2f && pyMax - pyMin > 2f;
        }

        /**
         * True when the path is an axis-aligned rectangle.
         *
         * <p>Four straight lines are a rectangle only when each of them runs along the page's
         * own axes. A diamond - a GHS hazard pictogram, a rotated tag - is also four lines, and
         * treating it as a rectangle drew its bounding box instead: the diamond became a square
         * outline, or was lost altogether when the outline fell on the table's own rules.
         */
        private boolean pathIsAxisRect() {
            if (pCurves != 0 || pMoves != 1) return false;
            if (cmdsOverflow || cmds.size() < 4 || cmds.size() > 5) return false;
            if (cmds.get(0)[0] != 0) return false;
            float sx = cmds.get(0)[1], sy = cmds.get(0)[2], px = sx, py = sy;
            for (int i = 1; i < cmds.size(); i++) {
                float[] c = cmds.get(i);
                boolean horizontal = Math.abs(c[2] - py) <= 0.8f;
                boolean vertical = Math.abs(c[1] - px) <= 0.8f;
                if (!horizontal && !vertical) return false;
                px = c[1];
                py = c[2];
            }
            return Math.abs(px - sx) <= 1.5f && Math.abs(py - sy) <= 1.5f;
        }

        /** Adds a shape to the page, in PDF space, after the clip has had its say. */
        private void addShape(float[] r, int fill, float alpha, int line, float lineWidth) {
            addShape(r, fill, alpha, line, lineWidth, 0);
        }

        /**
         * Adds a shape that has already been built.
         *
         * <p>A preset box cannot survive a rotated matrix - its bounding box is not the shape,
         * and drawing the box painted solid slabs over the page - so those are still dropped.
         * A freeform is the page's own points, already through the matrix, so it is exact and
         * is kept: a diamond hazard pictogram is a square drawn under a 45-degree matrix, and
         * dropping it lost every GHS pictogram in the corpus.
         */
        private void addShape(DocxWriter.Shape sh) {
            if (sh == null) return;
            if (ctmRotated() && sh.kind != 2) return;
            rules.shapes.add(sh);
        }

        /** As above, with the preset geometry: 0 a rectangle, 1 an ellipse. */
        private void addShape(float[] r, int fill, float alpha, int line, float lineWidth, int kind) {
            if (r == null) return;
            if (r[2] - r[0] <= 0.01f && r[3] - r[1] <= 0.01f) return;
            // A shape can only be an axis-aligned wps:wsp rect. Under a rotated CTM the path's
            // bounding box is NOT the path: a stamp drawn as `re` inside a 15-degree matrix
            // measures 207 x 106 pt on the page, and emitting that box paints a solid block over
            // the invoice. Measured on file 01 of the corpus, which came back from the user with
            // two red 207x106 slabs and a grey 240x75 one covering the text. Drop it instead;
            // a rotated rectangle cannot be represented, and a wrong block is worse than nothing.
            if (ctmRotated()) return;
            DocxWriter.Shape sh = new DocxWriter.Shape(r[0], -r[3], r[2] - r[0], r[3] - r[1]);
            sh.kind = kind;
            sh.fillRgb = fill;
            sh.fillAlpha = alpha;
            sh.lineRgb = line;
            sh.lineWidthPt = lineWidth;
            sh.lineAlpha = (float) getGraphicsState().getAlphaConstant();
            rules.shapes.add(sh);
        }

        /**
         * A filled path becomes its bounding rectangle.
         *
         * <p>Every filled path in the 80-file batch is drawn with {@code re}, so the box is
         * the path exactly. A curved fill would become its box; measured over the batch there
         * is not one larger than 4 pt square, so nothing a reader sees is mis-shaped.
         */
        private void emitFill(boolean alsoStroke) {
            if (pathEmpty()) return;
            int fill = rgbOf(getGraphicsState().getNonStrokingColor());
            if (fill < 0) return;
            float alpha = (float) getGraphicsState().getNonStrokeAlphaConstant();
            int line = -1;
            float lw = 0f;
            if (alsoStroke) {
                line = rgbOf(getGraphicsState().getStrokingColor());
                lw = Math.max(0.1f, getGraphicsState().getLineWidth());
            }
            float[] box = pathBox();
            float[] cl = clipped(box);
            boolean plainRect = pathIsAxisRect();
            // A triangle, an arrowhead, a diamond, a glyph outline: the box is not the shape.
            // Draw the path the page drew. A clipped path keeps the old box behaviour, because
            // the clip is an axis-aligned box and the geometry is not.
            if (!plainRect && !pathIsEllipse() && same(cl, box)) {
                DocxWriter.Shape ff = freeform(cl, fill, alpha, line, lw);
                if (ff != null) {
                    addShape(ff);
                    return;
                }
            }
            addShape(cl, fill, alpha, line, lw, pathIsEllipse() ? 1 : 0);
        }

        /**
         * The stroke in force right now, as {@code {widthPt, rgb, alpha}} - the weight, the
         * colour and the constant alpha the page will paint the current path with.
         *
         * <p>The same three values the shape path already reads (4039, 4102 and
         * {@code addShape}). A rule was recorded as geometry alone, so the page's 0.4 pt grey
         * grid rule and its 2 pt black frame arrived at the writer as the same thing.
         */
        private float[] strokeOf() {
            int rgb = rgbOf(getGraphicsState().getStrokingColor());
            // No stroke colour in force means there is no stroke to describe. A `re` that the
            // page only FILLS is still a table-border candidate here, and its four edges used to
            // be recorded with the PDF's default line width (1 pt) and no colour at all - which
            // is how a 0.5 pt grey grid rule came out as a 1 pt black border. Record nothing and
            // the side falls back to the table's own stroke instead.
            if (rgb < 0) return null;
            float w = Math.max(0.1f, getGraphicsState().getLineWidth());
            float a = (float) getGraphicsState().getAlphaConstant();
            return new float[]{w, rgb, a};
        }

        /**
         * Gives the rules this path added the stroke the path is actually painted with.
         *
         * <p>A rule is recorded while the path is being BUILT, and the paint operator comes
         * after it: {@code re ... S} strokes, {@code re ... f} fills and paints no line at all.
         * The graphics state during construction is usually the one that paints, but not when a
         * page draws a filled band and leaves a stroking colour set from earlier - 07_stamp_
         * over_table then reported a 1.5 pt green column separator inside a table the page rules
         * in 0.7 pt black. So the stroke is stamped here, at the operator, where it is known.
         *
         * <p>A fill-only path that is a thin band IS a hairline: the band's thickness is the
         * weight and its fill colour is the colour, which is how most generators draw a rule. Any
         * other fill-only path paints no rule, and its edges keep no stroke at all - the table
         * border then falls back to the table's own stroke rather than to a colour nothing on the
         * page uses.
         */
        private void stampPathRules(boolean stroked) {
            float[] stroke = stroked ? strokeOf() : bandFillStroke();
            for (int i = Math.max(0, pathRulesH); i < rules.horizontal.size(); i++) {
                if (i < rules.hStroke.size()) rules.hStroke.set(i, stroke);
            }
            for (int i = Math.max(0, pathRulesV); i < rules.vertical.size(); i++) {
                if (i < rules.vStroke.size()) rules.vStroke.set(i, stroke);
            }
        }

        /** The stroke a fill-only path implies: a thin band is a hairline, anything else none. */
        private float[] bandFillStroke() {
            if (Float.isNaN(pxMin)) return null;
            if (pCurves != 0) return null;
            boolean rect = pRects == 1 && pLines == 0;
            boolean quad = pLines == 4 && pRects == 0;
            if (!rect && !quad) return null;
            int fill = rgbOf(getGraphicsState().getNonStrokingColor());
            if (fill < 0) return null;
            float alpha = (float) getGraphicsState().getNonStrokeAlphaConstant();
            float hgt = pyMax - pyMin, wid = pxMax - pxMin;
            if (hgt <= 1.5f && wid > 2f) return new float[]{Math.max(0.1f, hgt), fill, alpha};
            if (wid <= 1.5f && hgt > 2f) return new float[]{Math.max(0.1f, wid), fill, alpha};
            return null;
        }

        /** True when two boxes are the same to a hundredth of a point. */
        private static boolean same(float[] a, float[] b) {
            if (a == null || b == null) return a == b;
            for (int i = 0; i < 4; i++) if (Math.abs(a[i] - b[i]) > 0.01f) return false;
            return true;
        }

        /**
         * The path as a freeform shape, or null when there is no path worth carrying.
         *
         * <p>The vertices are the ones the page drew, so a triangle is a triangle and a hatch
         * stroke is a line at its own angle rather than a dropped operator. A path with no
         * drawn segment - a bare {@code m} - has no shape and falls back to the box.
         */
        private DocxWriter.Shape freeform(float[] box, int fill, float alpha, int line, float lw) {
            if (cmdsOverflow || cmds.isEmpty() || box == null) return null;
            int drawn = 0;
            for (float[] c : cmds) if (c[0] != 0) drawn++;
            if (drawn == 0) return null;
            DocxWriter.Shape sh = new DocxWriter.Shape(box[0], -box[3], box[2] - box[0], box[3] - box[1]);
            sh.kind = 2;
            sh.freeform = cmds;
            sh.freeformClosed = pathClosed;
            sh.fillRgb = fill;
            sh.fillAlpha = alpha;
            sh.lineRgb = line;
            sh.lineWidthPt = lw;
            sh.lineAlpha = (float) getGraphicsState().getAlphaConstant();
            return sh;
        }

        /**
         * A stroked path becomes an outline when it is a rectangle and a solid band when it
         * is a single axis-aligned line.
         *
         * <p>A stroke sits astride the path, so the rectangle a reader sees is the path grown
         * by half the line width - that is why file 60's 2.4 pt border measures 22.8,22.8
         * rather than 24,24. A thin rule is written as a filled band rather than as the
         * outline of a hairline rectangle: an outline that thin lands on fractional device
         * pixels and all but disappears, and a 0.4 pt column rule must survive.
         */
        private void emitStroke() {
            if (pathEmpty()) return;
            int line = rgbOf(getGraphicsState().getStrokingColor());
            if (line < 0) return;
            float w = Math.max(0.1f, getGraphicsState().getLineWidth());
            boolean rectangle = pathIsAxisRect();
            // A stroke-only circle used to be dropped: it is neither a rectangle nor a single
            // line, and its box would have put a square where a ring belongs. It is an ellipse,
            // so it is drawn as one.
            boolean ellipse = pathIsEllipse();
            if (rectangle || ellipse) {
                float[] grownRing = clipped(new float[]{pxMin - w / 2f, pyMin - w / 2f,
                        pxMax + w / 2f, pyMax + w / 2f});
                // A ring drawn under a rotated matrix - the two circles of a "PAID" stamp are
                // set inside a 0.99/-0.14 cm - cannot be a preset ellipse: addShape drops every
                // preset shape when the CTM is rotated, because the box is not the shape. The
                // path's own curve points are already through that matrix, so carry them as a
                // freeform and the ring survives. Nothing that drew before changes: this branch
                // is only reached where the ellipse was being dropped.
                if (ellipse && ctmRotated()) {
                    DocxWriter.Shape ring = freeform(grownRing, -1, 1f, line, w);
                    if (ring != null) {
                        addShape(ring);
                        return;
                    }
                }
                addShape(grownRing, -1, 1f, line, w, ellipse ? 1 : 0);
                return;
            }
            if (pCurves == 0 && pLines == 1 && pRects == 0) {
                if (Math.abs(segY1 - segY0) <= 0.8f) {
                    float x0 = Math.min(segX0, segX1), x1 = Math.max(segX0, segX1);
                    addShape(clipped(new float[]{x0, segY0 - w / 2f, x1, segY0 + w / 2f}),
                            line, 1f, -1, 0f);
                    return;
                } else if (Math.abs(segX1 - segX0) <= 0.8f) {
                    float y0 = Math.min(segY0, segY1), y1 = Math.max(segY0, segY1);
                    addShape(clipped(new float[]{segX0 - w / 2f, y0, segX0 + w / 2f, y1}),
                            line, 1f, -1, 0f);
                    return;
                }
            }
            // Everything else the page strokes - a triangle, a bowtie, a hatch stroke at an
            // angle, a leader line, a partial arc - used to be dropped rather than drawn as
            // its box. It is drawn as its own path. The box is grown by half the stroke so a
            // path on the edge still has its line inside the shape.
            float[] grown = new float[]{pxMin - w / 2f, pyMin - w / 2f,
                    pxMax + w / 2f, pyMax + w / 2f};
            float[] cl = clipped(grown);
            if (same(cl, grown)) {
                DocxWriter.Shape ff = freeform(grown, -1, 1f, line, w);
                if (ff != null) {
                    addShape(ff);
                    return;
                }
            }
            // A path the clip cuts, or one too long to carry, keeps the behaviour it had: four
            // straight sides still read as a box, and a rotated stamp box that runs off the page
            // edge is still drawn as the box it was before.
            if (pCurves == 0 && (pRects > 0 || pLines == 4)) addShape(cl, -1, 1f, line, w, 0);
        }

        @Override
        public void appendRectangle(android.graphics.PointF p0, android.graphics.PointF p1,
                                    android.graphics.PointF p2, android.graphics.PointF p3) {
            beginPath();
            pRects++;
            grow(p0.x, p0.y); grow(p1.x, p1.y); grow(p2.x, p2.y); grow(p3.x, p3.y);
            float minX = Math.min(Math.min(p0.x, p1.x), Math.min(p2.x, p3.x));
            float maxX = Math.max(Math.max(p0.x, p1.x), Math.max(p2.x, p3.x));
            float minY = Math.min(Math.min(p0.y, p1.y), Math.min(p2.y, p3.y));
            float maxY = Math.max(Math.max(p0.y, p1.y), Math.max(p2.y, p3.y));
            // A rectangle is a table border candidate: keep all four edges, each with the
            // stroke the page is drawing the path with right now. The width, the colour and
            // the alpha are all in the graphics state at this point, and they are the ones a
            // `S` after this `re` will paint with. (A `re` that is only filled, never stroked,
            // records the fill-only stroke it did not use; see D-22's note in the report - a
            // path's own paint operator is not visible here.)
            float[] stroke = strokeOf();
            if (maxX - minX > 2) {
                rules.addH(new float[]{minY, minX, maxX}, stroke);
                rules.addH(new float[]{maxY, minX, maxX}, stroke);
            }
            if (maxY - minY > 2) {
                rules.addV(new float[]{minX, minY, maxY}, stroke);
                rules.addV(new float[]{maxX, minY, maxY}, stroke);
            }
            // A path may mix a `re` with other segments - a hatch region clips a rectangle and
            // then draws lines in the same path object - so the rectangle is part of the path
            // the freeform carries. Leaving it out drew the lines but kept the rectangle's
            // corners in the box, which put the whole path in the wrong frame.
            cmd(new float[]{0, p0.x, p0.y});
            cmd(new float[]{1, p1.x, p1.y});
            cmd(new float[]{1, p2.x, p2.y});
            cmd(new float[]{1, p3.x, p3.y});
            pathClosed = true;
        }

        @Override
        public void drawImage(PDImage pdImage) {
            rules.images++;
            collectImage(pdImage);
        }

        /**
         * Folds a mask image into the picture as its alpha channel.
         *
         * <p>The mask is usually a different size from the image it protects - a soft mask is
         * often a quarter of it - so it is sampled by proportion rather than by index.
         */
        private android.graphics.Bitmap withMask(android.graphics.Bitmap src,
                                                 android.graphics.Bitmap mask) {
            int w = src.getWidth(), h = src.getHeight();
            int mw = mask.getWidth(), mh = mask.getHeight();
            if (w <= 0 || h <= 0 || mw <= 0 || mh <= 0) return src;
            int[] px = new int[w * h];
            src.getPixels(px, 0, w, 0, 0, w, h);
            int[] mp = new int[mw * mh];
            mask.getPixels(mp, 0, mw, 0, 0, mw, mh);
            for (int y = 0; y < h; y++) {
                int my = mh > 1 ? Math.min(mh - 1, y * mh / h) : 0;
                for (int x = 0; x < w; x++) {
                    int mx = mw > 1 ? Math.min(mw - 1, x * mw / w) : 0;
                    int a = (mp[my * mw + mx] >> 16) & 0xFF;
                    int c = px[y * w + x];
                    px[y * w + x] = (a << 24) | (c & 0x00FFFFFF);
                }
            }
            return android.graphics.Bitmap.createBitmap(px, w, h,
                    android.graphics.Bitmap.Config.ARGB_8888);
        }

        /**
         * Lifts one drawn image out, with the rectangle it covers on the page.
         *
         * <p>A PDF draws an image into the unit square and lets the transform in force stretch
         * it, so the placement is that square's four corners through the current matrix -
         * never the image's pixel size, which says nothing about where it lands.
         */
        private void collectImage(PDImage pdImage) {
            if (pdImage == null || pdImage.isStencil()) return;
            try {
                com.tom_roush.pdfbox.util.Matrix ctm =
                        getGraphicsState().getCurrentTransformationMatrix();
                if (ctm == null) return;
                float[] xs = new float[4];
                float[] ys = new float[4];
                float[][] corner = {{0, 0}, {1, 0}, {0, 1}, {1, 1}};
                for (int i = 0; i < 4; i++) {
                    android.graphics.PointF pt = ctm.transformPoint(corner[i][0], corner[i][1]);
                    xs[i] = pt.x;
                    ys[i] = pt.y;
                }
                float minX = xs[0], maxX = xs[0], minY = ys[0], maxY = ys[0];
                for (int i = 1; i < 4; i++) {
                    minX = Math.min(minX, xs[i]);
                    maxX = Math.max(maxX, xs[i]);
                    minY = Math.min(minY, ys[i]);
                    maxY = Math.max(maxY, ys[i]);
                }
                // A hairline is a rule the page draws with an image, not a picture a reader
                // would miss. Only something with area on the page is worth carrying over.
                if (maxX - minX < 2f || maxY - minY < 2f) return;
                android.graphics.Bitmap bmp = pdImage.getImage();
                if (bmp == null) return;
                // A scanned signature or a stamp with soft edges keeps its shape in an /SMask,
                // not in the image's own samples. getImage() returns the colour plane alone, so
                // the mask has to be folded in here or every transparent part of the picture
                // arrives as an opaque black box over the words underneath it.
                if (pdImage instanceof PDImageXObject) {
                    android.graphics.Bitmap mask = null;
                    try {
                        PDImageXObject xo = (PDImageXObject) pdImage;
                        PDImageXObject soft = xo.getSoftMask();
                        if (soft != null) mask = soft.getImage();
                        if (mask == null) {
                            PDImageXObject hard = xo.getMask();
                            if (hard != null) mask = hard.getImage();
                        }
                    } catch (Throwable ignored) {
                    }
                    if (mask != null) bmp = withMask(bmp, mask);
                }
                java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
                if (!bmp.compress(android.graphics.Bitmap.CompressFormat.PNG, 100, bos)) return;
                byte[] png = bos.toByteArray();
                if (png.length < 64) return;
                DocxWriter.Picture pic = new DocxWriter.Picture(png, 0f, 0f,
                        maxX - minX, maxY - minY);
                // PDF user space has y up from the bottom of the page; the .docx anchor is
                // measured down from the top, so the top edge is the page height minus maxY.
                pic.topPt = -maxY;
                pic.xPt = minX;
                rules.pictures.add(pic);
            } catch (Throwable ignored) {
                // One unreadable image must not cost the page its text.
            }
        }

        @Override
        public void clip(android.graphics.Path.FillType fillType) {
            // A W sets the clip from the path that is still being built; it takes effect when
            // that path is painted, which is what commitClip() waits for.
            pendingClip = pathBox();
        }

        @Override
        public void moveTo(float x, float y) {
            beginPath();
            pMoves++;
            grow(x, y);
            segX0 = segX1 = x;
            segY0 = segY1 = y;
            startX = lastX = x;
            startY = lastY = y;
            cmd(new float[]{0, x, y});
        }

        @Override
        public void lineTo(float x, float y) {
            beginPath();
            pLines++;
            grow(x, y);
            segX0 = lastX; segY0 = lastY; segX1 = x; segY1 = y;
            float dx = Math.abs(x - lastX), dy = Math.abs(y - lastY);
            // The stroke this segment will be painted with: the same three values the shape
            // path reads at 4039 and 4102, taken here so a rule keeps the page's own weight.
            float[] stroke = null;
            if (dx <= 0.8f && dy > 2f) {
                stroke = strokeOf();
                rules.addV(new float[]{lastX, Math.min(lastY, y), Math.max(lastY, y)}, stroke);
            } else if (dy <= 0.8f && dx > 2f) {
                stroke = strokeOf();
                rules.addH(new float[]{lastY, Math.min(lastX, x), Math.max(lastX, x)}, stroke);
            }
            lastX = x;
            lastY = y;
            cmd(new float[]{1, x, y});
        }

        @Override
        public void curveTo(float x1, float y1, float x2, float y2, float x3, float y3) {
            beginPath();
            pCurves++;
            grow(x1, y1); grow(x2, y2); grow(x3, y3);
            lastX = x3;
            lastY = y3;
            cmd(new float[]{2, x1, y1, x2, y2, x3, y3});
        }

        @Override
        public android.graphics.PointF getCurrentPoint() {
            return new android.graphics.PointF(lastX, lastY);
        }

        @Override
        public void closePath() {
            lastX = startX;
            lastY = startY;
            pathClosed = true;
        }

        @Override
        public void endPath() {
            commitClip();
            resetPath();
            pathStarted = false;
        }

        @Override
        public void strokePath() {
            stampPathRules(true);
            emitStroke();
            commitClip();
            resetPath();
            pathStarted = false;
        }

        @Override
        public void fillPath(android.graphics.Path.FillType fillType) {
            stampPathRules(false);
            emitFill(false);
            commitClip();
            resetPath();
            pathStarted = false;
        }

        @Override
        public void fillAndStrokePath(android.graphics.Path.FillType fillType) {
            stampPathRules(true);
            emitFill(true);
            commitClip();
            resetPath();
            pathStarted = false;
        }

        @Override
        public void shadingFill(COSName shadingName) {
        }
    }

    /**
     * Puts the page's images on the page, pinned where they were drawn.
     *
     * <p>The y a PDF draws at counts up from the bottom of the page and a .docx anchor counts
     * down from the top, so the top edge of the image is the page height minus its top in PDF
     * space. An image drawn off the page is dropped: a picture pinned outside the paper is
     * invisible in Word and only adds weight to the file.
     */

    private static void attachPictures(Page page, Rules rules, float pageHeight) {
        if (rules == null || rules.pictures.isEmpty()) return;
        for (DocxWriter.Picture pic : rules.pictures) {
            pic.topPt = pageHeight + pic.topPt;
            if (pic.topPt > pageHeight || pic.topPt + pic.hPt < 0) continue;
            if (pic.xPt > page.width || pic.xPt + pic.wPt < 0) continue;
            page.blocks.add(pic);
        }
    }

    /**
     * Puts the page's rectangles on the page, behind its words.
     *
     * <p>Two things are deliberately not carried. A shape that falls entirely off the paper is
     * dropped - it is invisible in Word and only makes the file heavier. And a stroke drawn
     * inside a table is dropped, because Word lays a table out itself: the page's row rules
     * then run across the table's own rows at the wrong y and cut through every one of them,
     * which is worse than the table having no rules at all. A filled strip inside a table is
     * kept - that is the header's shading, and Word does not invent one.
     */
    private static void attachShapes(Page page, Rules rules, float pageHeight,
                                     List<Table> tables) {
        if (rules == null || rules.shapes.isEmpty()) return;
        for (DocxWriter.Shape s : rules.shapes) {
            // A table's own box is measured down from the top of the page, so the test is
            // made in that space - the shape is converted to it here and stored afterwards.
            float topDown = pageHeight + s.topPt;
            // Only a HAIRLINE is a rule. An outline-only shape used to count as one too, which
            // threw away every bordered box that encloses a table - the BILL TO / SHIP TO frames
            // on the invoices are exactly that, a stroked rectangle around a detected table, and
            // they vanished. A box is not a rule: Word draws the table's grid itself, but the
            // frame around it belongs to the page.
            boolean rule = Math.min(s.wPt, s.hPt) < 3f;
            if (rule && inTable(s.xPt, s.wPt, topDown, topDown + s.hPt, tables)) continue;
            s.topPt = topDown;
            // A freeform's points are in the page's own frame, where y counts up from the
            // bottom; the shape now lives in the frame that counts down, so its points are
            // moved into that frame with it. Without this the path was drawn mirrored about
            // the shape's top edge and every hatch stroke collapsed onto one line.
            if (s.freeform != null) {
                for (float[] c : s.freeform) {
                    for (int i = 2; i < c.length; i += 2) c[i] = pageHeight - c[i];
                }
            }
            if (s.topPt + s.hPt <= 0f || s.topPt >= pageHeight) continue;
            if (s.xPt + s.wPt <= 0f || s.xPt >= page.width) continue;
            page.blocks.add(s);
        }
    }

    /**
     * True when a drawn stroke belongs to one of the page's tables.
     *
     * <p>A table is drawn twice over and both drawings have to go. Word lays the table out
     * itself, so a rule left at the PDF's y lands at a row boundary Word chose, not the one
     * the PDF meant, and cuts through the row. Measured on file 50, seven row rules across a
     * seven-row table; on file 42, eight.
     *
     * <p>Three cases, because the drawn rule and the detected cell box do not have the same
     * extent. The cell box is the text area: it is inset from the drawn frame by the cell
     * padding, and its last column can stop short of a rule that runs past the final cell
     * (file 56's rules are 36 pt wider than the cells they close). So a hairline is matched
     * on where it lies and how much of the table it spans, not on strict containment; a box
     * is matched either inside the cell box or around it.
     */
    private static boolean inTable(float x, float w, float top, float bottom, List<Table> tables) {
        if (tables == null || tables.isEmpty()) return false;
        boolean thin = Math.min(w, bottom - top) < 3f;
        for (Table t : tables) {
            float tw = t.right - t.left, th = t.bottom - t.top;
            if (tw <= 0 || th <= 0) continue;
            if (thin) {
                float pad = 16f;
                if (w >= bottom - top) {                       // a horizontal rule
                    if (top < t.top - pad || top > t.bottom + pad) continue;
                    if (overlap(x, x + w, t.left, t.right) >= 0.5f * tw) return true;
                } else {                                       // a vertical rule
                    if (x < t.left - pad || x > t.right + pad) continue;
                    if (overlap(top, bottom, t.top, t.bottom) >= 0.5f * th) return true;
                }
                continue;
            }
            float pad = 2f;
            boolean inside = x >= t.left - pad && x + w <= t.right + pad
                    && top >= t.top - pad && bottom <= t.bottom + pad;
            boolean frame = t.left >= x - pad && t.right <= x + w + pad
                    && t.top >= top - pad && t.bottom <= bottom + pad;
            if (inside || frame) return true;
        }
        return false;
    }

    private static float overlap(float a0, float a1, float b0, float b1) {
        return Math.max(0f, Math.min(a1, b1) - Math.max(a0, b0));
    }

    private static Rules rulesOf(PDDocument doc, int index) {
        Rules out = new Rules();
        try {
            PDPage page = doc.getPage(index);
            RuleCollector collector = new RuleCollector(page);
            collector.processPage(page);
            out.horizontal.addAll(collector.rules.horizontal);
            out.vertical.addAll(collector.rules.vertical);
            // The strokes travel with their rules or the parallel lists part here, and every
            // index after this point reads another rule's weight. D-22.
            out.hStroke.addAll(collector.rules.hStroke);
            out.vStroke.addAll(collector.rules.vStroke);
            out.images = collector.rules.images;
            out.pictures.addAll(collector.rules.pictures);
            out.shapes.addAll(collector.rules.shapes);
        } catch (Throwable ignored) {
        }
        return out;
    }

    /**
     * Reads, from the rules the page drew, whether it drew the separators inside this table.
     *
     * <p>Only the whitespace pass needs this: its tables carry ink bounds rather than the
     * rectangle the page strokes, so the writer can see the frame around them but not what the
     * page drew across them. A rule counts when it runs inside the table's band - not along its
     * own top or bottom - and covers at least half the table's width (or height, for a column
     * separator). One rule of either kind is enough to say the page drew a grid rather than a
     * panel.
     */
    private static void markInnerRules(Table t, Rules rules) {
        if (rules == null) return;
        float w = t.right - t.left, h = t.bottom - t.top;
        if (w <= 0f || h <= 0f) return;
        for (float[] r : rules.horizontal) {                       // {y, x1, x2}
            if (r[0] <= t.top + 1f || r[0] >= t.bottom - 1f) continue;
            if (Math.min(r[2], t.right) - Math.max(r[1], t.left) >= w * 0.5f) {
                t.innerH = true;
                break;
            }
        }
        for (float[] r : rules.vertical) {                          // {x, y1, y2}
            if (r[0] <= t.left + 1f || r[0] >= t.right - 1f) continue;
            if (Math.min(r[2], t.bottom) - Math.max(r[1], t.top) >= h * 0.5f) {
                t.innerV = true;
                break;
            }
        }
    }

    /** How far off a table's own edge a rule may sit and still be that side's rule. */
    private static final float SIDE_TOL = 2.5f;
    /**
     * How far off it may sit when the table's bounds are its TEXT's ink rather than the
     * rectangle the page strokes - the whitespace pass measures ink, so the frame the page
     * draws round a table can stand 8 to 15 pt outside it (04_stamp_180deg: 8.3 pt left of the
     * first character, 14.3 pt above the first row).
     */
    private static final float SIDE_FRAME_TOL = 24f;

    /**
     * Records, on the table, the stroke the page drew along each of its six sides (D-22).
     *
     * <p>Called where the page's own rule list is in hand - the same place
     * {@link #markInnerRules} is called, and in the lines' own frame (y down). Each side is
     * matched on its own: the outer four against the rules that lie along that edge, the two
     * inner sides against the rules that run across the table's band.
     *
     * <p>Which rule wins when several lie on one side. On an outer edge the NEAREST rule wins -
     * a table whose top edge is also the bottom edge of the band above it has two rules within
     * tolerance and the one the table's own line is the nearer. Across an inner side the rule
     * that covers the most length wins, so a 12-row grid reports the weight it is ruled at
     * twelve times rather than the one odd rule some generator drew once. Both are a real rule
     * on that side; neither is a median over the page, which is what the earlier attempt
     * computed and why its numbers matched no drawn line anywhere.
     */
    private static void markSideStrokes(Table t, Rules rules) {
        if (rules == null) return;
        float w = t.right - t.left, h = t.bottom - t.top;
        if (w <= 0f || h <= 0f) return;
        t.sideStroke[0] = edgeStroke(rules, true, t.top, t.left, t.right, w);      // top
        t.sideStroke[2] = edgeStroke(rules, true, t.bottom, t.left, t.right, w);   // bottom
        t.sideStroke[1] = edgeStroke(rules, false, t.left, t.top, t.bottom, h);    // left
        t.sideStroke[3] = edgeStroke(rules, false, t.right, t.top, t.bottom, h);   // right
        t.sideStroke[4] = insideStroke(rules, true, t.top, t.bottom, t.left, t.right, w);   // insideH
        t.sideStroke[5] = insideStroke(rules, false, t.left, t.right, t.top, t.bottom, h);  // insideV
        // A side the page drew no rule along still gets a weight, because the side is written
        // either way. It takes the table's own stroke rather than the writer's old constant.
        float[] tableStroke = bandStroke(rules, t);
        if (tableStroke != null) {
            for (int i = 0; i < 6; i++) if (t.sideStroke[i] == null) t.sideStroke[i] = tableStroke;
        }
    }

    /**
     * The stroke of the rule lying along one outer edge of a table, or null.
     *
     * @param horizontal true for a rule that runs across the page, matched on its y
     * @param at         the edge's coordinate in the rules' own frame
     * @param a0,a1      the extent the rule has to cover, along the table's other axis
     * @param span       the table's size along that axis, for the half-coverage test
     */
    private static float[] edgeStroke(Rules rules, boolean horizontal, float at,
                                      float a0, float a1, float span) {
        List<float[]> geom = horizontal ? rules.horizontal : rules.vertical;
        float[] best = null;
        float bestDistance = Float.MAX_VALUE;
        for (int i = 0; i < geom.size(); i++) {
            float[] g = geom.get(i);
            float distance = Math.abs(g[0] - at);
            if (distance > SIDE_FRAME_TOL) continue;
            // Half the table's width has to lie on the rule: a 3 pt tick beside the corner is
            // not the table's edge, and neither is the page frame.
            if (Math.min(g[2], a1) - Math.max(g[1], a0) < span * 0.5f) continue;
            float[] stroke = horizontal ? rules.hStrokeAt(i) : rules.vStrokeAt(i);
            if (stroke == null) continue;
            // Exact beats frame, then the nearest wins; a tie goes to the heavier rule, which
            // is the one a reader sees as the edge.
            boolean exact = distance <= SIDE_TOL;
            if (best == null) {
                best = stroke;
                bestDistance = distance;
                continue;
            }
            boolean bestExact = bestDistance <= SIDE_TOL;
            if (exact != bestExact) {
                if (exact) { best = stroke; bestDistance = distance; }
                continue;
            }
            if (distance < bestDistance - 0.01f) {
                best = stroke;
                bestDistance = distance;
            } else if (Math.abs(distance - bestDistance) <= 0.01f && stroke[0] > best[0]) {
                best = stroke;
            }
        }
        return best;
    }

    /**
     * The stroke the page rules one inner side of a table at, or null.
     *
     * <p>An inner side is one element in {@code w:tblBorders} for every separator of that
     * direction, so the rules inside the band have to be reduced to one answer: the stroke
     * carrying the most length wins. A row separator that is 0.4 pt grey for twelve rows and a
     * single 2 pt black line under the header row report 0.4 pt grey, which is what the table
     * is ruled at.
     */
    private static float[] insideStroke(Rules rules, boolean horizontal, float lo, float hi,
                                        float a0, float a1, float span) {
        java.util.LinkedHashMap<String, float[]> byStroke = new java.util.LinkedHashMap<>();
        tally(byStroke, rules, horizontal, lo + 1f, hi - 1f, a0, a1, span);
        return dominant(byStroke);
    }

    /**
     * The stroke this table's own rules are drawn at, for a side that has no rule of its own.
     *
     * <p>A table the page rules only across (303_discharge_summary draws 35 horizontal rules at
     * 0.4 pt and not one vertical rule) still has six sides in {@code w:tblBorders}, because the
     * ruled pass put its bounds on the grid. Two of those sides have no rule to read a weight
     * off. The constant that stood in for them was 1 pt black against a table ruled at 0.4 pt
     * black - a side visibly heavier than every other side of the same table, which is the very
     * thing D-22 is about. So a side with no rule of its own takes the stroke the table's rules
     * ARE drawn at: the stroke carrying the most length among the rules that lie anywhere on or
     * inside the table. It is the table's own ink, not a median over the page.
     */
    private static float[] bandStroke(Rules rules, Table t) {
        float w = t.right - t.left, h = t.bottom - t.top;
        java.util.LinkedHashMap<String, float[]> byStroke = new java.util.LinkedHashMap<>();
        // The frame tolerance, not the side tolerance: a whitespace table's bounds are its ink,
        // so the rules round it stand up to 15 pt outside its own band (see SIDE_FRAME_TOL).
        tally(byStroke, rules, true, t.top - SIDE_FRAME_TOL, t.bottom + SIDE_FRAME_TOL,
                t.left, t.right, w);
        tally(byStroke, rules, false, t.left - SIDE_FRAME_TOL, t.right + SIDE_FRAME_TOL,
                t.top, t.bottom, h);
        return dominant(byStroke);
    }

    /**
     * Adds the rules that cross one band to a per-stroke running total of covered length.
     *
     * @param lo,hi the band's edges, in the rules' own frame, exclusive
     * @param a0,a1 the extent a rule has to cover, along the table's other axis
     * @param span  the table's size along that axis, for the half-coverage test
     */
    private static void tally(java.util.LinkedHashMap<String, float[]> byStroke, Rules rules,
                              boolean horizontal, float lo, float hi,
                              float a0, float a1, float span) {
        List<float[]> geom = horizontal ? rules.horizontal : rules.vertical;
        for (int i = 0; i < geom.size(); i++) {
            float[] g = geom.get(i);
            if (g[0] <= lo || g[0] >= hi) continue;
            float cover = Math.min(g[2], a1) - Math.max(g[1], a0);
            if (cover < span * 0.5f) continue;
            float[] stroke = horizontal ? rules.hStrokeAt(i) : rules.vStrokeAt(i);
            if (stroke == null) continue;
            String key = Math.round(stroke[0] * 8f) + "|" + (int) stroke[1] + "|"
                    + Math.round(stroke[2] * 20f);
            float[] acc = byStroke.get(key);
            // {rules, covered length, widthPt, rgb, alpha} - the rule COUNT decides, because one
            // long rule that crosses the band is as likely a stamp's edge or a band's outline as
            // a separator, while the twelve rules a grid is ruled with are the grid.
            if (acc == null) byStroke.put(key, new float[]{1f, cover, stroke[0], stroke[1], stroke[2]});
            else { acc[0] += 1f; acc[1] += cover; }
        }
    }

    /**
     * The stroke the most rules in a {@link #tally} are drawn with, or null when it is empty.
     *
     * <p>Most rules, then most covered length. Counting the rules rather than summing their
     * length is what keeps a stamp's green outline - one 1.5 pt rule lying inside a table's band
     * on 07_stamp_over_table - from being read as the weight the table's column separators are
     * ruled at. The length is the tie-break, so two strokes used equally often resolve to the one
     * that covers more of the table.
     */
    private static float[] dominant(java.util.LinkedHashMap<String, float[]> byStroke) {
        float[] best = null;
        for (float[] acc : byStroke.values()) {
            if (best == null || acc[0] > best[0]
                    || (acc[0] == best[0] && acc[1] > best[1])) best = acc;
        }
        return best == null ? null : new float[]{best[2], best[3], best[4]};
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

        // A column narrower than a character is not a column. Two vertical rules three points
        // apart are the edge of a stamp's own frame, not a table's cell separator: on file 01
        // the stamp draws rules at x=356, 367 and 370 across the invoice totals, the 3 pt
        // "column" between 367 and 370 cut "TOTAL PAYABLE" into "T", "O" and "TAL PAYABLE",
        // and the table then owned the line - so the words appeared in no paragraph of the
        // .docx at all. Rejecting the grid hands the totals block back as text.
        float widest = 0;
        for (float[] c : group) widest = Math.max(widest, c[2]);
        for (int c = 0; c < ncol; c++) {
            float nextX = c + 1 < ncol ? C.get(c + 1) : widest;
            if (nextX - C.get(c) < 6f) return null;
        }

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
        // The page's own row edges, so a row can be given its own height instead of the average.
        //
        // These cells come from intersectionsToCells, which emits each one as
        // {left, top, right, bottom} - a rectangle bounded by the four rules that close it. So a
        // cell's y IS the rule ABOVE its row: the first cell's y is the table's own top edge and
        // the lowest cell's bottom is its foot. (The comment here used to claim the opposite -
        // that a cell's y was the rule BELOW its row - and derived the table's top as one pitch
        // above the first cell. Nothing was below that invented edge, so the top rule landed one
        // row-pitch too high and the header row was handed its neighbour's pitch: on
        // 23_timetable_grid_txtpos the page draws its rules at y=140,166,206,...,406 with the
        // header 26 pt tall and every day row 40 pt, and the model came out 114,140,166,...,366 -
        // a grid starting 26 pt high, with two 26 pt rows where the page has 26 and 40, and 14 pt
        // short by the foot, so every row below the header drifted further up the sheet.)
        float[] rowEdge = new float[nrow + 1];
        for (int r = 0; r < nrow; r++) rowEdge[r] = R.get(r);
        rowEdge[nrow] = Math.max(R.get(nrow - 1) + 1f, bottom);
        t.rowEdge = rowEdge;
        t.rowTopPt = rowEdge[0];
        float[] cx = new float[ncol + 1];
        for (int i = 0; i < ncol; i++) cx[i] = C.get(i);
        cx[ncol] = right;
        t.colX = cx;
        t.header = nrow > 1;
        int filled = 0;
        for (int r = 0; r < nrow; r++) {
            List<String> row = new ArrayList<>();
            List<String> rowFonts = new ArrayList<>();
            List<Float> rowSizes = new ArrayList<>();
            List<Float> rowXs = new ArrayList<>();
            List<Float> rowRs = new ArrayList<>();
            List<Integer> rowCols = new ArrayList<>();
            for (int c = 0; c < ncol; c++) {
                String str = glyphText(buckets.get(r).get(c));
                if (!str.isEmpty()) filled++;
                row.add(str);
                rowFonts.add(fontOf(buckets.get(r).get(c)));
                rowSizes.add(sizeOf(buckets.get(r).get(c)));
                rowXs.add(glyphFirstX(buckets.get(r).get(c)));
                rowRs.add(glyphLastRight(buckets.get(r).get(c)));
                rowCols.add(colorOf(buckets.get(r).get(c)));
            }
            t.rows.add(row);
            t.fonts.add(rowFonts);
            t.sizes.add(rowSizes);
            t.cellX.add(rowXs);
            t.cellR.add(rowRs);
            t.colors.add(rowCols);
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

    /**
     * The x of the glyph the cell's text starts with, in the order {@link #glyphText} reads
     * them - topmost line first, then left to right. That glyph is the first word of the cell
     * in the .docx too, so its x is where the .docx has to put the cell's text.
     *
     * <p>A space is not a glyph a reader sees. The balance sheet indents "(a) Share capital"
     * by drawing the spaces in front of it: the first glyph is at x=56 and the first letter at
     * 73.4, and measuring the space put the cell 348 twips out. Whitespace is skipped.
     */
    private static Float glyphFirstX(List<Glyph> gs) {
        if (gs == null || gs.isEmpty()) return Float.NaN;
        List<Glyph> sorted = new ArrayList<>(gs);
        Collections.sort(sorted, new Comparator<Glyph>() {
            @Override
            public int compare(Glyph a, Glyph b) {
                if (Math.abs(a.y - b.y) > 2f) return Float.compare(a.y, b.y);
                return Float.compare(a.x, b.x);
            }
        });
        for (Glyph g : sorted) if (visible(g)) return g.x;
        return sorted.get(0).x;
    }

    /**
     * Orders a cell's glyphs by the strings the page drew, or returns null when the page drew
     * them in one straight run and the plain left-to-right sort is right.
     *
     * <p>A value that overruns its column is drawn over the label it runs into: on the FIR form
     * the address ends "560067" while "Mobile" starts 19 pt before the address finishes. Sorting
     * the two strings together by x interleaves their letters into "6M0o0b6i7le". Where x steps
     * backwards the page began a new string, so each string is kept whole and the strings are
     * ordered by where each one starts.
     */
    private static List<Glyph> orderedByRun(List<Glyph> gs) {
        List<List<Glyph>> runs = new ArrayList<>();
        List<Glyph> run = new ArrayList<>();
        Glyph prev = null;
        for (Glyph g : gs) {
            if (prev != null && (g.x < prev.x - 0.5f || Math.abs(g.y - prev.y) > 2f)) {
                runs.add(run);
                run = new ArrayList<>();
            }
            run.add(g);
            prev = g;
        }
        runs.add(run);
        if (runs.size() < 2) return null;
        Collections.sort(runs, new Comparator<List<Glyph>>() {
            @Override
            public int compare(List<Glyph> a, List<Glyph> b) {
                float ay = a.get(0).y, by = b.get(0).y;
                if (Math.abs(ay - by) > 2f) return Float.compare(ay, by);
                return Float.compare(a.get(0).x, b.get(0).x);
            }
        });
        List<Glyph> out = new ArrayList<>(gs.size());
        for (List<Glyph> r : runs) out.addAll(r);
        return out;
    }

    /** A glyph that puts ink on the page - not a space. */
    private static boolean visible(Glyph g) {
        return g != null && g.text != null && !g.text.trim().isEmpty();
    }

    /**
     * The x of the leftmost glyph of a line that puts ink on the page, or {@code fallback} when
     * the line is only whitespace.
     */
    private static float visibleX(List<Glyph> gs, float fallback) {
        if (gs == null) return fallback;
        float best = Float.MAX_VALUE;
        for (Glyph g : gs) if (visible(g) && g.x < best) best = g.x;
        return best == Float.MAX_VALUE ? fallback : best;
    }

    /** The typeface the first drawn glyph of a cell carries; empty when the page did not say. */
    /** The colour of the first glyph that draws something, or -1 for the default black. */
    private static int colorOf(List<Glyph> gs) {
        for (Glyph g : gs) {
            if (g.text != null && !g.text.trim().isEmpty()) return g.color;
        }
        return -1;
    }

    private static String fontOf(List<Glyph> gs) {
        for (Glyph g : gs) if (g.font != null && !g.font.isEmpty()) return g.font;
        return "";
    }

    /**
     * The size a cell's text was drawn at: the size of the glyphs that carry the words, not of
     * an empty or zero-width one a marked-content sequence left behind.
     */
    private static float sizeOf(List<Glyph> gs) {
        float best = Float.NaN;
        for (Glyph g : gs) {
            if (g.text == null || g.text.trim().isEmpty()) continue;
            if (g.size <= 0f) continue;
            if (Float.isNaN(best) || g.size > best) best = g.size;
        }
        return best;
    }

    /** Join a cell's glyphs into one string, in reading order. */
    private static String glyphText(List<Glyph> gs) {
        if (gs.isEmpty()) return "";
        List<Glyph> sorted = orderedByRun(gs);
        if (sorted == null) {
            sorted = new ArrayList<>(gs);
            Collections.sort(sorted, new Comparator<Glyph>() {
                @Override
                public int compare(Glyph a, Glyph b) {
                    if (Math.abs(a.y - b.y) > 2f) return Float.compare(a.y, b.y);
                    return Float.compare(a.x, b.x);
                }
            });
        }
        java.util.List<Float> cg = new java.util.ArrayList<>();
        for (int k = 1; k < sorted.size(); k++) {
            Glyph a = sorted.get(k - 1), b = sorted.get(k);
            if (Math.abs(a.y - b.y) <= 2f) cg.add(b.x - (a.x + a.width));
        }
        java.util.Collections.sort(cg);
        float cellMedian = cg.isEmpty() ? 3f : cg.get(cg.size() / 2);
        StringBuilder sb = new StringBuilder();
        Glyph prev = null;
        for (Glyph g : sorted) {
            if (prev != null) {
                // A cell that holds several lines of text holds several lines. Joining them
                // with a space invented a line that appears nowhere in the document, and the
                // bank statement lost 232 of its 362 lines to exactly that. The newline is kept
                // and the .txt writer puts each one on its own line; a Word cell shows them as
                // line breaks, which is what the document has.
                if (Math.abs(g.y - prev.y) > Math.max(2f, prev.size * 0.5f)) {
                    if (sb.length() > 0 && sb.charAt(sb.length() - 1) != '\n') sb.append('\n');
                    sb.append(g.text);
                    prev = g;
                    continue;
                }
                float gap = g.x - (prev.x + prev.width);
                // Two blocks of text side by side on one baseline inside a cell are two lines,
                // not one. The newspaper's body text did exactly this and came out as
                // "and inline formatting while Headers, footers and page". A gap several times
                // the cell's own median gap is a break, not a space.
                if (gap > Math.max(24f, cellMedian * 2.5f)) {
                    if (sb.length() > 0 && sb.charAt(sb.length() - 1) != '\n') sb.append('\n');
                    sb.append(g.text);
                    prev = g;
                    continue;
                }
                // A glyph with no advance of its own is not a word boundary. A Devanagari
                // vowel sign is drawn as a zero-width mark laid back over its consonant, so
                // the next consonant starts forward of it and the gap measured after the mark
                // means nothing - the pair was one cluster. This is the same rule
                // textOf() already applies to a whole line; the cell path did not have it, so
                // the Devanagari table's total row reached Word as "कु ल योग" out of the
                // page's "कुल योग" - a space inside a word.
                boolean prevAdvances = prev.width > prev.size * 0.05f;
                if (prevAdvances && gap > Math.max(1.5f, prev.size * 0.18f) && sb.length() > 0
                        && sb.charAt(sb.length() - 1) != ' ') sb.append(' ');
            }
            sb.append(g.text);
            prev = g;
        }
        // Each line of the cell is turned into logical order on its own. Turning the whole
        // cell at once reversed the order of the lines with the letters inside them, so a
        // cell holding "،قهوة عربية مغسولة" over "غربال17" came out as "،غربال" over
        // "17 قهوة عربية مغسولة" - the two lines swapped their first and last words, and a
        // two-line cell read bottom-up.
        String[] parts = sb.toString().split("\n", -1);
        StringBuilder outSb = new StringBuilder(sb.length());
        for (String part : parts) {
            if (outSb.length() > 0) outSb.append('\n');
            outSb.append(logicalOrder(part.trim()));
        }
        return outSb.toString().trim();
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
            out.add(t);
        }
        return out;
    }

    /** The same rules with y measured down from the top, the way a line carries it. */
    private static Rules flipY(Rules in, float pageHeight) {
        Rules out = new Rules();
        for (float[] h : in.horizontal) out.horizontal.add(new float[]{pageHeight - h[0], h[1], h[2]});
        for (float[] v : in.vertical) out.vertical.add(new float[]{v[0], pageHeight - v[2], pageHeight - v[1]});
        // A stroke is a weight and a colour, not a coordinate: it is the same in either frame,
        // so the parallel lists are copied across unchanged and keep their indices.
        out.hStroke.addAll(in.hStroke);
        out.vStroke.addAll(in.vStroke);
        out.images = in.images;
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
        // A stamp is not a table row. Its characters are drawn over the grid, not in it.
        List<Line> uprightLines = new ArrayList<>(lines.size());
        for (Line ln : lines) if (!ln.rotated) uprightLines.add(ln);
        lines = uprightLines;

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
            String[][] faces = new String[rows][cols];
            float[][] sizes = new float[rows][cols];
            for (float[] rowSize : sizes) java.util.Arrays.fill(rowSize, Float.NaN);
            // Where the first line written into each cell actually starts. A cell's text is not
            // at its rule: it is wherever the page drew it, centred, right-aligned or padded.
            float[][] firstX = new float[rows][cols];
            for (float[] rowX : firstX) java.util.Arrays.fill(rowX, Float.NaN);
            for (Line line : lines) {
                float cx = (line.x + line.right) / 2f;
                int r = band(ys, line.y);
                int c = band(xs, cx);
                if (r < 0 || c < 0) continue;
                cells[r][c] = cells[r][c] == null
                        ? line.text.trim() : cells[r][c] + " " + line.text.trim();
                if (faces[r][c] == null) faces[r][c] = fontOf(line.glyphs);
                if (Float.isNaN(sizes[r][c])) sizes[r][c] = sizeOf(line.glyphs);
                if (Float.isNaN(firstX[r][c])) firstX[r][c] = visibleX(line.glyphs, line.x);
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
                String[][] trimmedFaces = new String[rows][keep.size()];
                float[][] trimmedX = new float[rows][keep.size()];
                for (int r = 0; r < rows; r++) {
                    for (int k = 0; k < keep.size(); k++) {
                        trimmed[r][k] = cells[r][keep.get(k)];
                        trimmedFaces[r][k] = faces[r][keep.get(k)];
                        trimmedX[r][k] = firstX[r][keep.get(k)];
                    }
                }
                cells = trimmed;
                faces = trimmedFaces;
                firstX = trimmedX;
                cols = keep.size();
            }

            Table t = new Table();
            t.top = top;
            t.bottom = bottom;
            t.left = left;
            t.right = right;
            // The grid's own row rules: rows = ys.size() - 1 and row r is ys[r]..ys[r+1]. A rule
            // is a row's top edge, so the first one is the table's top.
            float[] rowEdge = new float[rows + 1];
            for (int r = 0; r <= rows; r++) rowEdge[r] = ys.get(r);
            t.rowEdge = rowEdge;
            t.rowTopPt = rowEdge[0];
            // The rule positions the columns were cut at, so the .docx can use the same widths
            // instead of five equal ones.
            float[] colX = new float[cols + 1];
            for (int c = 0; c < cols; c++) {
                int src = c < keep.size() ? keep.get(c) : c;
                colX[c] = xs.get(Math.min(src, xs.size() - 1));
            }
            colX[cols] = right;
            t.colX = colX;
            t.header = rows > 1;
            for (int r = 0; r < rows; r++) {
                List<String> row = new ArrayList<>();
                List<String> rowFonts = new ArrayList<>();
                List<Float> rowSizes = new ArrayList<>();
                List<Float> rowXs = new ArrayList<>();
                for (int c = 0; c < cols; c++) {
                    row.add(cells[r][c] == null ? "" : cells[r][c]);
                    rowFonts.add(faces[r][c] == null ? "" : faces[r][c]);
                    rowSizes.add(sizes[r][c]);
                    rowXs.add(firstX[r][c]);
                }
                t.rows.add(row);
                t.fonts.add(rowFonts);
                t.sizes.add(rowSizes);
                t.cellX.add(rowXs);
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
        List<Line> keep = new ArrayList<>(rawLines.size());
        for (Line ln : rawLines) if (!ln.rotated) keep.add(ln);
        rawLines = keep;
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
            // End the run at a loose pair instead of rejecting the whole run. tightRows asked
            // the spacing question of the entire run, so on a fee receipt - where the key/value
            // fields sit 26 pt and 32 pt above an 18 pt item grid - the page was one run and one
            // loose pair above the grid discarded the invoice with it.
            while (j < rows.size() && rows.get(j).size() >= 2
                    && alignedStart(rows.get(i), rows.get(j))
                    && rowGapOk(rows, j - 1, j)) j++;
            if (j - i >= 3 && shortCells(rows, i, j)) {
                Table t = keyValuePanels(buildRowTable(rows, i, j));
                // Every word of the lines the table covers must survive in its cells. A false
                // table claims lines and then does not write them - the one failure mode a
                // percentage guard cannot see. Measured: a genuine space-aligned invoice loses
                // 0 of 216 tokens, while two false tables lost 5 of 223 and 36 of 760.
                if (t != null && wordsSurvive(t, coveredLines(rows, i, j))) out.add(t);
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
        t.ruled = false;
        t.top = rows.get(from).get(0).y;
        float bottom = t.top, left = Float.MAX_VALUE, right = 0;
        // The baseline each row was drawn on, so the row can be given the height the page gave
        // it rather than the table's average (D-26, cause 2).
        List<Float> rowTops = new ArrayList<>();
        for (int r = from; r < to; r++) {
            String[] line = new String[columns.size()];
            String[] lineFonts = new String[columns.size()];
            float[] lineSizes = new float[columns.size()];
            java.util.Arrays.fill(lineSizes, Float.NaN);
            int[] lineCols = new int[columns.size()];
            java.util.Arrays.fill(lineCols, -1);
            float[] lineX = new float[columns.size()];
            java.util.Arrays.fill(lineX, Float.NaN);
            float[] lineR = new float[columns.size()];
            java.util.Arrays.fill(lineR, Float.NaN);
            // The baseline the first piece in each column was drawn on, so a second piece can
            // be told apart: beside it on the same line, or under it on the next one.
            float[] lineY = new float[columns.size()];
            java.util.Arrays.fill(lineY, Float.NaN);
            for (Line cell : rows.get(r)) {
                int best = 0;
                float bestDistance = Float.MAX_VALUE;
                for (int c = 0; c < columns.size(); c++) {
                    float d = Math.abs(columns.get(c) - cell.x);
                    if (d < bestDistance) { bestDistance = d; best = c; }
                }
                if (Float.isNaN(lineX[best])) lineX[best] = visibleX(cell.glyphs, cell.x);
                if (Float.isNaN(lineY[best])) lineY[best] = cell.y;
                if (Float.isNaN(lineR[best]) || cell.right > lineR[best]) lineR[best] = cell.right;
                String piece = cell.text.trim();
                // A numbered item's marker is not part of the name: the page drew "1." at x=64
                // and "SUNRISE FASTENERS PVT LTD" at x=80, eight points apart, under the gap
                // that starts a new cell. Whether the name belongs on the next line of the cell
                // or beside the marker on the same one is decided by the baselines, not by the
                // wording: on file 80 the two sit 0.5 pt apart and read "1. SUNRISE FASTENERS
                // PVT LTD" on one line, while the depot report's marker really is eight points
                // above its name and has to keep its own line.
                if (line[best] == null) {
                    line[best] = piece;
                } else if (isListMarker(line[best]) && !isListMarker(piece)
                        && Math.abs(cell.y - lineY[best]) > 3f) {
                    line[best] = line[best] + "\n" + piece;
                } else {
                    line[best] = line[best] + " " + piece;
                }
                if (lineFonts[best] == null) {
                    lineFonts[best] = fontOf(cell.glyphs);
                    lineSizes[best] = sizeOf(cell.glyphs);
                    lineCols[best] = colorOf(cell.glyphs);
                }
                bottom = Math.max(bottom, cell.y);
                left = Math.min(left, cell.x);
                right = Math.max(right, cell.right);
                cell.consumed = true;
            }
            List<String> texts = new ArrayList<>();
            List<String> textFonts = new ArrayList<>();
            List<Float> textSizes = new ArrayList<>();
            List<Float> textXs = new ArrayList<>();
            List<Float> textRs = new ArrayList<>();
            List<Integer> textCols = new ArrayList<>();
            for (String cell : line) texts.add(cell == null ? "" : cell);
            for (String f : lineFonts) textFonts.add(f == null ? "" : f);
            for (float sz : lineSizes) textSizes.add(sz);
            for (float x : lineX) textXs.add(x);
            for (float rr : lineR) textRs.add(rr);
            for (int c = 0; c < lineCols.length; c++) textCols.add(lineCols[c]);
            t.rows.add(texts);
            t.fonts.add(textFonts);
            t.sizes.add(textSizes);
            t.cellX.add(textXs);
            t.cellR.add(textRs);
            t.colors.add(textCols);
            float rowY = Float.MAX_VALUE;
            for (Line cell : rows.get(r)) rowY = Math.min(rowY, cell.y);
            rowTops.add(rowY == Float.MAX_VALUE ? (rowTops.isEmpty() ? t.top : rowTops.get(rowTops.size() - 1)) : rowY);
        }
        t.bottom = bottom;
        // One more entry than there are rows: the last row's bottom edge is one row pitch below
        // its own top, because the last baseline the page drew is a baseline and not an edge.
        float[] rowEdge = new float[rowTops.size() + 1];
        for (int i = 0; i < rowTops.size(); i++) rowEdge[i] = rowTops.get(i);
        float lastPitch = rowTops.size() >= 2
                ? Math.max(1f, rowEdge[rowTops.size() - 1] - rowEdge[rowTops.size() - 2])
                : Math.max(1f, bottom - (rowTops.isEmpty() ? t.top : rowEdge[0]));
        rowEdge[rowTops.size()] = (rowTops.isEmpty() ? t.top : rowEdge[rowTops.size() - 1]) + lastPitch;
        t.rowEdge = rowEdge;
        // These edges are baselines, so the table's top edge is one ascent (DocxWriter.LINE_BASE
        // of the row's own pitch) above the first one.
        t.rowTopPt = rowEdge[0] - 0.8f * lastPitch;
        float[] cx2 = new float[columns.size() + 1];
        for (int i = 0; i < columns.size(); i++) cx2[i] = columns.get(i);
        cx2[columns.size()] = Math.max(right, columns.get(columns.size() - 1));
        t.colX = cx2;
        t.left = left;
        t.right = right;
        t.header = true;
        t.column = rows.get(from).get(0).column;
        return t;
    }

    /**
     * True when a cell holds nothing but a list marker: "1.", "2)", "(a)", "b.".
     *
     * <p>Only digits, or a single letter, may precede the punctuation. A label that ends in a
     * dot - a form field called "No." - is a word, not a number, and must not start a line of
     * its own.
     */
    private static boolean isListMarker(String s) {
        String t = s.trim();
        if (t.isEmpty() || t.length() > 5) return false;
        int i = 0;
        if (t.charAt(0) == '(') i = 1;
        int digits = 0, letters = 0;
        while (i < t.length()) {
            char c = t.charAt(i);
            if (Character.isDigit(c)) digits++;
            else if (Character.isLetter(c)) letters++;
            else break;
            i++;
        }
        if (i == 0 || i != t.length() - 1) return false;
        char end = t.charAt(i);
        if (end != '.' && end != ')' && end != ':') return false;
        return digits > 0 || letters == 1;
    }

    /**
     * True when a cell reads as a form field's name rather than as a value.
     *
     * <p>Short, no digits, and made of the letters and punctuation a label is made of. A
     * value - an amount, a code, a date, a sentence - fails at least one of those.
     */
    private static boolean isFieldLabel(String s) {
        String t = s.trim();
        if (t.isEmpty() || t.length() > 14) return false;
        boolean letter = false;
        for (int i = 0; i < t.length(); i++) {
            char c = t.charAt(i);
            if (Character.isDigit(c)) return false;
            if (Character.isLetter(c)) { letter = true; continue; }
            if (" .&/()'-:,".indexOf(c) < 0) return false;
        }
        return letter;
    }

    /**
     * How many rows of a column group are a label followed by its value, or 0 when the group
     * holds something that is not a label/value pair at all.
     */
    private static int pairRows(Table t, int from, int to) {
        int n = 0;
        for (List<String> row : t.rows) {
            List<Integer> filled = new ArrayList<>();
            for (int c = from; c < to && c < row.size(); c++) {
                String s = row.get(c);
                if (s != null && !s.trim().isEmpty()) filled.add(c);
            }
            if (filled.size() < 2) continue;                       // a title line, not a pair
            if (!isFieldLabel(row.get(filled.get(0)))) return 0;
            n++;
        }
        return n;
    }

    /**
     * Reads a two-panel key/value form panel by panel instead of row by row.
     *
     * <p>A record laid out as two blocks of labels and values side by side - registration
     * identifiers on the left, bank and address on the right - has no rows that mean anything.
     * Its four columns are two independent (label, value) pairs, and the reference text reads
     * the whole left panel and then the whole right panel. Read row by row, the output
     * interleaved the two panels and sent the reader's eye back and forth across the page on
     * every line: file 80 of the batch scored 43.97 on line order for exactly this.
     *
     * <p>Four tests keep this off a real table, and each is a property of the form rather than
     * of the page:
     * <ul>
     *   <li>the widest gap between two column starts is at least 90 pt - a panel gutter, not
     *       the padding between an invoice's Quantity and its Rate;</li>
     *   <li>that gap falls in the middle, so each side has at least two columns of its own;</li>
     *   <li>on both sides, at least two rows are a pair whose first cell reads as a field
     *       name. An invoice's Date/Amount rows start with "01-04-2025" and fail here, and so
     *       does a marksheet's "BCO-401";</li>
     *   <li>no row on either side breaks that pattern - one pair of prose and the "form" is a
     *       table with a wide column, which must keep reading row by row.</li>
     * </ul>
     * The result is a two-column label/value table. Every cell keeps its own typeface, colour
     * and x, so the .docx puts each one back where the page had it.
     */
    private static Table keyValuePanels(Table t) {
        if (t == null || t.colX == null || t.rows.size() < 3) return t;
        int cols = 0;
        for (List<String> row : t.rows) cols = Math.max(cols, row.size());
        if (cols < 4 || t.colX.length != cols + 1) return t;

        int split = -1;
        float widest = 0;
        for (int c = 1; c < cols; c++) {
            float gap = t.colX[c] - t.colX[c - 1];
            if (gap > widest) { widest = gap; split = c; }
        }
        if (split < 2 || split > cols - 2) return t;
        if (widest < 90f) return t;
        if (pairRows(t, 0, split) < 2 || pairRows(t, split, cols) < 2) return t;
        // A label/value pair on BOTH sides of the same baseline is not a form listed down the
        // page: the two panels stand side by side, as they do on file 80, where "GSTIN" and
        // "IFSC" share y=147.7. Collapsing that grid into one label column and one value
        // column puts the right panel's label 232 pt into a 52 pt column, the indent is
        // clamped to the column, and "IFSC" comes out one letter per line - measured as
        // I/F/S/C stacked vertically in the .docx. The grid keeps its four columns instead.
        for (int r = 0; r < t.rows.size(); r++) {
            List<String> row = t.rows.get(r);
            if (isPair(row, 0, split) && isPair(row, split, cols)) return t;
        }

        Table out = new Table();
        out.ruled = t.ruled;
        // The rebuilt record stands where the old one stood, so it keeps the page's strokes.
        for (int i = 0; i < 6; i++) out.sideStroke[i] = t.sideStroke[i];
        // The record's own heading - the numbered line that is not a label/value pair - keeps
        // its place at the top, because it introduces both panels.
        for (int r = 0; r < t.rows.size(); r++) {
            List<String> row = t.rows.get(r);
            if (isPair(row, 0, split) || isPair(row, split, cols)) continue;
            int c = firstFilled(row, 0, cols);
            if (c < 0) continue;
            out.rows.add(new ArrayList<>(java.util.Arrays.asList(cellOf(t, r, c), "")));
            out.fonts.add(new ArrayList<>(java.util.Arrays.asList(fontOf(t, r, c), "")));
            out.sizes.add(new ArrayList<>(java.util.Arrays.asList(sizeOf(t, r, c), Float.NaN)));
            out.cellX.add(new ArrayList<>(java.util.Arrays.asList(xOf(t, r, c), Float.NaN)));
            out.cellR.add(new ArrayList<>(java.util.Arrays.asList(rOf(t, r, c), Float.NaN)));
            out.colors.add(new ArrayList<>(java.util.Arrays.asList(colorOf(t, r, c), -1)));
        }
        for (int side = 0; side < 2; side++) {
            int from = side == 0 ? 0 : split;
            int to = side == 0 ? split : cols;
            for (int r = 0; r < t.rows.size(); r++) {
                List<String> row = t.rows.get(r);
                if (!isPair(row, from, to)) continue;
                int a = firstFilled(row, from, to);
                int b = nextFilled(row, a + 1, to);
                out.rows.add(new ArrayList<>(java.util.Arrays.asList(
                        cellOf(t, r, a), b < 0 ? "" : cellOf(t, r, b))));
                out.fonts.add(new ArrayList<>(java.util.Arrays.asList(
                        fontOf(t, r, a), b < 0 ? "" : fontOf(t, r, b))));
                out.sizes.add(new ArrayList<>(java.util.Arrays.asList(
                        sizeOf(t, r, a), b < 0 ? Float.NaN : sizeOf(t, r, b))));
                out.cellX.add(new ArrayList<>(java.util.Arrays.asList(
                        xOf(t, r, a), b < 0 ? Float.NaN : xOf(t, r, b))));
                out.cellR.add(new ArrayList<>(java.util.Arrays.asList(
                        rOf(t, r, a), b < 0 ? Float.NaN : rOf(t, r, b))));
                out.colors.add(new ArrayList<>(java.util.Arrays.asList(
                        colorOf(t, r, a), b < 0 ? -1 : colorOf(t, r, b))));
            }
        }
        // The label column is as wide as the left panel's label column was; the value column
        // takes the rest of the table. Each cell still carries its own x, so a right panel's
        // value lands where the page drew it.
        float edge = Math.max(t.colX[1], t.colX[0] + 1f);
        out.colX = new float[]{t.colX[0], edge, Math.max(edge + 1f, t.right)};
        out.header = t.header;
        out.top = t.top;
        out.bottom = t.bottom;
        out.left = t.left;
        out.right = t.right;
        out.column = t.column;
        return out;
    }

    /** True when this row holds at least two filled cells in the given column group. */
    private static boolean isPair(List<String> row, int from, int to) {
        int a = firstFilled(row, from, to);
        return a >= 0 && nextFilled(row, a + 1, to) >= 0;
    }

    private static int firstFilled(List<String> row, int from, int to) {
        for (int c = from; c < to && c < row.size(); c++) {
            String s = row.get(c);
            if (s != null && !s.trim().isEmpty()) return c;
        }
        return -1;
    }

    private static int nextFilled(List<String> row, int from, int to) {
        return firstFilled(row, from, to);
    }

    private static String cellOf(Table t, int r, int c) {
        List<String> row = t.rows.get(r);
        return c < row.size() && row.get(c) != null ? row.get(c) : "";
    }

    private static String fontOf(Table t, int r, int c) {
        if (r >= t.fonts.size()) return "";
        List<String> row = t.fonts.get(r);
        return c < row.size() && row.get(c) != null ? row.get(c) : "";
    }

    private static float sizeOf(Table t, int r, int c) {
        if (r >= t.sizes.size()) return Float.NaN;
        List<Float> row = t.sizes.get(r);
        return c < row.size() && row.get(c) != null ? row.get(c) : Float.NaN;
    }

    private static int colorOf(Table t, int r, int c) {
        if (r >= t.colors.size()) return -1;
        List<Integer> row = t.colors.get(r);
        return c < row.size() && row.get(c) != null ? row.get(c) : -1;
    }

    private static float rOf(Table t, int r, int c) {
        if (r >= t.cellR.size()) return Float.NaN;
        List<Float> row = t.cellR.get(r);
        return c < row.size() && row.get(c) != null ? row.get(c) : Float.NaN;
    }

    private static float xOf(Table t, int r, int c) {
        if (r >= t.cellX.size()) return Float.NaN;
        List<Float> row = t.cellX.get(r);
        return c < row.size() && row.get(c) != null ? row.get(c) : Float.NaN;
    }

    /** The x of the right edge of the last glyph in the run, or NaN when it is empty. */
    private static float glyphLastRight(List<Glyph> glyphs) {
        float r = Float.NaN;
        for (Glyph g : glyphs) {
            float e = g.x + g.width;
            if (Float.isNaN(r) || e > r) r = e;
        }
        return r;
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
    /** True when the vertical gap between two neighbouring rows is a table's, not a page's. */
    private static boolean rowGapOk(List<List<Line>> rows, int a, int b) {
        float gap = rows.get(b).get(0).y - rows.get(a).get(0).y;
        float size = rows.get(a).get(0).size;
        return gap <= Math.max(size * 2.4f, 16f);
    }

    /** Every line the rows from..to cover, for the word-survival check. */
    private static List<Line> coveredLines(List<List<Line>> rows, int from, int to) {
        List<Line> out = new ArrayList<>();
        for (int r = from; r < to; r++) out.addAll(rows.get(r));
        return out;
    }

    /**
     * True when every word of the given lines survives somewhere in the table's cells.
     *
     * <p>A multiset, not an order check: cutting a line at its gaps, joining pieces, a list
     * marker on its own line and a panel read key by key all survive it. Only a word that is
     * genuinely lost rejects the table.
     */
    private static boolean wordsSurvive(Table t, List<Line> lines) {
        java.util.Map<String, Integer> want = new java.util.HashMap<>();
        for (Line l : lines) { if (!l.rotated) addWords(want, l.text); }
        if (want.isEmpty()) return true;
        java.util.Map<String, Integer> got = new java.util.HashMap<>();
        for (List<String> row : t.rows) for (String cell : row) addWords(got, cell);
        for (java.util.Map.Entry<String, Integer> e : want.entrySet()) {
            Integer have = got.get(e.getKey());
            if (have == null || have < e.getValue()) return false;
        }
        return true;
    }

    private static void addWords(java.util.Map<String, Integer> into, String text) {
        if (text == null) return;
        for (String w : text.trim().split("\\s+")) {
            if (!w.isEmpty()) into.put(w, into.getOrDefault(w, 0) + 1);
        }
    }

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



    /**
     * True for a character whose own bidi class is right-to-left.
     *
     * <p>The bidi class is the authority, not a code-point range. A range test counted the
     * Arabic comma U+060C and the Arabic full stop as letters, so they were reversed along
     * with the words and a line that ends "..., وشهادة الفحص" came back with its punctuation
     * at the wrong end. They are separators (class CS), and the Unicode rule puts a
     * separator that stands at the edge of a right-to-left line at that edge.
     */
    private static boolean isRtl(char c) {
        // Digits are numbers, not letters: ١٢٠ is 120 and must not be mirrored into ٠٢١.
        if ((c >= 0x0660 && c <= 0x0669) || (c >= 0x06F0 && c <= 0x06F9)) return false;
        int d = Character.getDirectionality(c);
        return d == Character.DIRECTIONALITY_RIGHT_TO_LEFT
                || d == Character.DIRECTIONALITY_RIGHT_TO_LEFT_ARABIC;
    }

    /**
     * A right-to-left line comes out of the PDF in visual order - the last letter first - which
     * reads as mirror writing. Reversing the whole line gives logical order, and each run of
     * Latin letters or digits is then turned back so numbers still read left to right.
     *
     * <p>Punctuation standing at the very edge of the line is not reversed with the words.
     * "رقم الفاتورة:" is drawn right to left, so its colon sits at the visual right edge;
     * reversing the whole line carried it to the front and the label came out ": رقم الفاتورة".
     * The edge runs are lifted off before the reversal and put back afterwards, which is the
     * Unicode rule for a separator at the boundary of a right-to-left run. Measured on the
     * Arabic document: it is the difference between 26.5 % and the figure in the report.
     */
    private static String logicalOrder(String text) {
        int rtl = 0, ltr = 0;
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (isRtl(c)) rtl++;
            else if (Character.isLetter(c)) ltr++;
        }
        if (rtl <= ltr || rtl == 0) return text;          // not an RTL line

        // Only punctuation and spaces are peeled. A Latin word or a number at the edge is
        // content: it has to travel with the line and be turned back as a run below.
        int lo = 0, hi = text.length();
        while (lo < hi && !isRtl(text.charAt(lo)) && !Character.isLetterOrDigit(text.charAt(lo))) lo++;
        while (hi > lo && !isRtl(text.charAt(hi - 1)) && !Character.isLetterOrDigit(text.charAt(hi - 1))) hi--;
        if (lo >= hi) return text;

        StringBuilder sb = new StringBuilder(text.substring(lo, hi)).reverse();
        int i = 0;
        while (i < sb.length()) {
            if (isRtl(sb.charAt(i))) { i++; continue; }
            int j = i;
            while (j < sb.length() && !isRtl(sb.charAt(j))) j++;
            String run = sb.substring(i, j);
            if (run.trim().length() > 0) {
                // A run of letters or digits is turned back so "2024" stays "2024".
                // A run of nothing but punctuation and spaces is not turned: reversing " : "
                // returns " : " unchanged, which left the colon on the wrong side of its
                // space - "المشتري :شركة" against a document that prints "المشتري: شركة".
                // In a right-to-left line punctuation closes the word before it, so the
                // punctuation comes first and the spaces after it.
                boolean punct = true;
                for (int k = 0; k < run.length(); k++) {
                    char c = run.charAt(k);
                    if (!Character.isWhitespace(c) && !isPunct(c)) { punct = false; break; }
                }
                sb.replace(i, j, punct ? punctFirst(run)
                        : new StringBuilder(run).reverse().toString());
            }
            i = j;
        }
        return text.substring(0, lo) + sb + text.substring(hi);
    }

    /** True for the marks that close a word: comma, full stop, colon, and their kin. */
    private static boolean isPunct(char c) {
        int t = Character.getType(c);
        return t == Character.CONNECTOR_PUNCTUATION || t == Character.DASH_PUNCTUATION
                || t == Character.START_PUNCTUATION || t == Character.END_PUNCTUATION
                || t == Character.INITIAL_QUOTE_PUNCTUATION || t == Character.FINAL_QUOTE_PUNCTUATION
                || t == Character.OTHER_PUNCTUATION;
    }

    /** The punctuation of a run first, its spaces after - same length, new order. */
    private static String punctFirst(String run) {
        StringBuilder marks = new StringBuilder(run.length());
        StringBuilder spaces = new StringBuilder(run.length());
        for (int i = 0; i < run.length(); i++) {
            char c = run.charAt(i);
            if (Character.isWhitespace(c)) spaces.append(c);
            else marks.append(c);
        }
        return marks.append(spaces).toString();
    }

    /**
     * True when the glyphs on one baseline are mostly right-to-left letters.
     *
     * <p>Such a line reads from its right edge, so the fields that sit on it are ordered from
     * the right too. Ordering them left to right mirrored every table row on the Arabic
     * document: the amount column came before the item number and the header read
     * "المبلغ السعر الكمية الوصف البند" against a document that says "البند الوصف الكمية السعر المبلغ".
     */
    private static boolean rtlDominant(List<Glyph> glyphs) {
        int rtl = 0, ltr = 0;
        for (Glyph g : glyphs) {
            if (g.text == null) continue;
            for (int i = 0; i < g.text.length(); i++) {
                char c = g.text.charAt(i);
                if (isRtl(c)) rtl++;
                else if (Character.isLetter(c)) ltr++;
            }
        }
        return rtl > ltr && rtl > 0;
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
        TxtWriter.write(result, out);
    }
}
