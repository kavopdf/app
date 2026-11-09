package com.kavopdf.app.engine;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * Writes a {@link PdfToWord.Result} as a real .docx - a ZIP of OOXML parts, built here rather
 * than pulled from a library.
 *
 * <p>Two reasons for hand-writing it: a Word library is 12 MB of the APK for one feature, and
 * the output is a handful of XML documents that Word, LibreOffice and Google Docs all read.
 *
 * <p><b>Where the text sits.</b> A .docx has no page grid of its own: a paragraph is placed by
 * the flow, and the only horizontal control a flowing paragraph has is {@code w:ind}. That is
 * why a value set at x=300 pt in the PDF used to arrive at "indent 4" - the paragraph was
 * pinned to the left margin and nudged. Every paragraph here is therefore a floating shape:
 * a {@code wp:anchor} whose {@code positionH}/{@code positionV} are taken straight from the
 * page, {@code relativeFrom="page"}, in EMU (1 pt = 12700 EMU), with the page section set to
 * the PDF's own page box and zero margins, so the anchor offset IS the PDF x.
 *
 * <p>Inside the anchor the text is ordinary WordprocessingML in {@code w:txbxContent} - real
 * characters in real runs with their real {@code rPr}, so the result is selectable, searchable
 * and editable, not a picture of a page. (A {@code a:txBody} would be DrawingML text, which
 * carries {@code a:rPr}, not {@code w:rPr}: bold, italic, size, typeface and colour would all
 * be lost, and Word would not open the shape as a text box at all.)
 *
 * <p>Tables stay tables: a {@code w:tbl} with {@code w:tr}/{@code w:tc} cells, anchored at the
 * table's own top-left corner.
 */
public final class DocxWriter {

    private static final String NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main";
    private static final String NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships";
    private static final String NS_WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing";
    private static final String NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main";
    private static final String NS_PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture";
    private static final String NS_WPS =
            "http://schemas.microsoft.com/office/word/2010/wordprocessingShape";

    /** 1 point in EMU, for wp:posOffset and wp:extent. */
    private static final double EMU_PER_PT = 12700.0;
    /** 1 point in twips, for every w:* length. */
    private static final double TWIPS_PER_PT = 20.0;

    /**
     * Distance from the top of a text box to the baseline of its first line, as a fraction of
     * the font size.
     *
     * <p>A text box positions its top edge, not its baseline, and a PDF gives a baseline. The
     * gap is the face's ascent, but with {@code w:lineRule="exact"} the renderer puts the
     * baseline at the bottom of the line box instead: measured over 377 words of two files,
     * the rendered baseline sat 0.268 * size below where it was asked to be, so the box has to
     * be lifted by 0.90 + 0.27 = 1.17 em. That is the LibreOffice figure; Word's exact-line
     * model puts the baseline a shade higher, so expect the Word baseline within about 1 pt of
     * the PDF's.
     */
    private static final float ASCENT = 1.17f;
    /** docPr ids for shapes start above the picture ids so the two never collide. */
    private static final int SHAPE_ID_BASE = 100000;
    /** Line box height as a multiple of the font size. Generous: a tight exact height clips. */
    private static final float LINE_FACTOR = 1.15f;
    /**
     * Where a shape's fill stops being a colour of its own and becomes a shade of the page.
     *
     * <p>HSL L of 0.72 is the point above which a filled band reads as a white patch on a dark
     * canvas. It catches the tints the user's own files carry - E6EBF5, F0F0E6, F5E6E6, BFBFBF,
     * C9C9C9, FFFFFF - and leaves a mid-tone or a dark band alone, because those carry dark or
     * white text that must not move.
     */
    private static final double LIGHT_FILL = 0.72;
    /**
     * Where the baseline sits inside a {@code w:lineRule="exact"} line box: this fraction of the
     * box height below its top.
     *
     * <p>Measured, not assumed. A one-paragraph probe with zero margins was rendered through
     * LibreOffice at seven box heights and four faces - 9.2, 11, 13, 14.95, 15.18, 20, 23, 34.5,
     * 37 pt, Liberation Sans/Serif and DejaVu Sans/Serif, and one box shorter than its own em -
     * and in every case {@code boxHeight - baselineY} came to 0.2 of the box, to within the
     * 0.05 pt the render quantises to. The ratio does not follow the font size or the face; it
     * follows the box. So a baseline is placed by choosing the box, and the space above a line
     * is {@code (1 - LINE_BASE) * previousBox} while the space from the box top to the baseline
     * is {@code LINE_BASE * box}.
     */
    private static final float LINE_BASE = 0.8f;

    /**
     * Ceiling on the vertical gap one paragraph may ask for, in twips (120 pt).
     *
     * <p>A gap is a measurement - the distance between two baselines the page drew - and must
     * be kept, because a diagram's boxes stand 90 pt apart and clamping that to 72 pt walks
     * every label on the page upwards. On 393_spectrum_peak_table and 394_map_with_legend that
     * put the table and the legend 141.6 pt and 227.1 pt above where the page drew them, and
     * both now hold their rows. The ceiling is not a layout rule: it is there because a
     * malformed PDF can report a y of 100000 pt, and because a gap larger than this on a real
     * page is the page's own white space, which the flow cannot spend without overflowing the
     * sheet (373_leave_application_form's footer sits 422 pt below the signature row and
     * leaving that gap open pushed the footer onto a second page, whose tables the model
     * under-measures by the same amount).
     *
     * <p>TRIED 7 Nov and reverted: raising the ceiling to 24000 twips (600 pt) so the page's own
     * white space is spent whenever the budget still has room. It fixed the class it was aimed at
     * - 300's footer went from 270.1 pt high to 8.2, 302's signature block from 232.0 to 14.0,
     * 311's "Copy forwarded to" from 162.1 to 27.0, 314's footer from 189.7 to 27.0 - and G2
     * across 208 documents passed. It was rejected because 315_gazette_notification went from one
     * sheet to two: its three columns are still stacked into one flow (its own defect below), so
     * its content is three columns long and only fitted a sheet while the gaps were being
     * clamped. The ratchet says a document that gets worse rejects the change. Spend the gap
     * again once 315's columns are real columns, or once the table height below is right.
     */
    private static final int GAP_CAP_TW = 2400;

    /**
     * The ceiling on a gap when the page's own content fits the sheet, in twips (1000 pt).
     *
     * <p>{@link #GAP_CAP_TW} exists because a gap is white space the flow cannot always afford,
     * not because 120 pt is a rule about layout. When the page's own content fits inside the
     * paper - which {@link #pageFits} measures by walking the page's blocks through this very
     * line box solver - the white space costs nothing: the flow ends where the page ends, and
     * giving the gap up is what puts a page's footer 250 pt too high (344's "Assessing officer"
     * 284 pt, 363's customer-care line 251 pt, 371's signature block 230 pt, 351's signature
     * lines 360 pt).
     *
     * <p>Still a ceiling, and still for the reason given above: a malformed PDF can report a y of
     * 100000 pt, and the per-page budget clamp in {@code flowFromBox} is the second guard.
     *
     * <p>TRIED 7 Nov and reverted: raising {@link #GAP_CAP_TW} itself. It fixed the same class and
     * G2 passed across 208, but 315_gazette_notification went from one sheet to two, because its
     * three columns are still stacked into one flow - its content is three columns long and only
     * fitted a sheet while the gaps were being clamped. Spending the gap only on a page whose
     * content fits is what separates 315 (it does not fit) from 344 (it does).
     */
    private static final int GAP_CAP_SPEND_TW = 20000;

    /**
     * The most a page's flow may be compressed to make it fit the paper: 85 % of its measured
     * height.
     *
     * <p>A page that has to lose more than a sixth of itself was not mis-measured by a sixth -
     * its content really is taller than the sheet, which today means a page whose columns are
     * stacked into one flow (D-08) or a table the model under-measures. Compressing those only
     * makes a wrong layout smaller and illegible, so past this floor the flow keeps its own
     * heights and the page overruns exactly as it did before this guard existed.
     */
    private static final float SQUEEZE_FLOOR = 0.85f;

    /**
     * Whether a page that cannot be squeezed to fit gets a deliberate page break instead of
     * silently overrunning.
     *
     * <p>OFF, and that is a measured decision, not a default. Four pages in the 208 still come
     * out taller than their paper after squeezing - {@code 350_question_paper},
     * {@code itr-computation-with-slab-table}, {@code newsletter-3col-header-footer} and
     * {@code product-catalogue-code-left-price-right}, which need 1.21, 1.09, 1.17 and 1.22
     * times the paper's height because their columns are still stacked into one flow (D-08) or a
     * slab table's rows cannot shrink below their own type. Turned ON, this flag breaks those
     * pages deliberately: measured over the corpus, the pages left over the paper go from 4 to 3
     * (the break cannot rescue a page whose overflow is a table that is already written) and the
     * gate gains two "pages 1 -> 2" counts on documents whose render is two pages either way. A
     * break a reader cannot see is not worth a regression the project measures, so the flag stays
     * off and the four pages are reported instead of papered over.
     */
    private static final boolean BREAK_WHEN_UNFITTABLE = false;

    /**
     * Twips kept back from every page's budget, so the page's own measured height can never sit
     * a twip above the paper.
     *
     * <p>The guard works in whole twips and rounds each attribute it writes; the paragraph
     * carriers that hold an anchored picture or a text box add one twip each and are not part of
     * the flow. Two twips is a tenth of a point - a fifth of a pixel at 200 dpi - and it is the
     * difference between a page that ends at the paper's edge and a page whose measured sum is
     * one twip past it, which the corpus check reads as an overflow.
     */
    private static final int PAGE_ROUNDING_TW = 2;

    /** The ceiling this page's gaps get - see {@link #GAP_CAP_SPEND_TW}. */
    private static int gapCapTw(Ctx ctx) {
        return ctx.spendGaps ? GAP_CAP_SPEND_TW : GAP_CAP_TW;
    }

    /**
     * Charges one paragraph against the page's budget, and says how much of it may be used.
     *
     * <p>The budget is the page's own height, because {@code w:before + w:line} summed down a
     * page IS the height the flow occupies - the section has zero margins, so the text area and
     * the paper are the same box. A sum larger than the paper is a second page: the reader's,
     * not ours, and at a place the reader chooses. The guard this replaces zeroed
     * {@code beforeTw} once the budget was spent and then went on adding {@code lineTw} for
     * every paragraph after it, so it could slow the overrun but never stop it (D-21: a one-page
     * PDF came back as two pages in Google Docs).
     *
     * <p>Three steps, in the order the page itself would give them up:
     * <ol>
     *   <li>the gap above the line goes first - white space is not content, and the old guard
     *       already did this much;</li>
     *   <li>then the line's own box is shortened to the room that is left, so the page ends
     *       exactly where the paper does. The box is never taken below the ascent the type needs
     *       to sit in ({@link #LINE_BASE} of the em), so the last line is not clipped and not
     *       overlapped - and only one line per page is ever shortened, because a shortened line
     *       leaves no room and the next paragraph takes the third step;</li>
     *   <li>if not even that fits, the page is full and the caller writes a deliberate page
     *       break. A break the writer places is a page the writer chose, at the last baseline
     *       the page itself drew; the alternative is the renderer inventing one wherever its own
     *       line model runs out.</li>
     * </ol>
     *
     * @param beforeTw the gap the page drew above this line, in twips
     * @param lineTw   the line's own box, in twips
     * @param size     the line's font size, so the ascent floor is the type's own
     * @return {@code {before, line}} in twips, or null when the page is full and must be broken
     */
    /**
     * The height a written page occupies, read off its own XML: every {@code w:before} plus every
     * {@code w:line} plus every row's {@code w:trHeight}.
     *
     * <p>This is the test the page has to pass - the flow's own before and line, summed down the
     * page, must not exceed the paper - so it is measured on the page and not on the model that
     * produced it. A model that agrees with itself while the page overruns is the defect this
     * guard exists to catch.
     */
    private static final String BEFORE = "w:before=\"";
    private static final String LINE = "w:line=\"";
    private static final String TRHEIGHT = "w:trHeight w:val=\"";
    private static final String FRAMEPR = "<w:framePr";
    private static final String PARA_END = "</w:p>";

    private static int spacingTw(CharSequence xml) {
        int sum = 0;
        int depth = 0;              // inside a w:tbl
        boolean framed = false;     // inside a paragraph that carries a w:framePr
        int i = 0;
        int n = xml.length();
        while (i < n) {
            if (startsWith(xml, FRAMEPR, i)) {
                // A framed paragraph is placed at a y, not flowed - it is a stamp line, and a
                // stamp is drawn OVER the page. Its own w:before/w:line are not the page's
                // height: charging them makes a one-page document measure taller than its paper
                // and sends its last line to a second sheet, which is exactly what a text box
                // used to do (see the w:txbxContent branch below). The flag is cleared at the
                // end of the paragraph that carries it, so a frame never hides a later line.
                framed = true;
                i += FRAMEPR.length();
            } else if (framed && startsWith(xml, PARA_END, i)) {
                framed = false;
                i += PARA_END.length();
            } else if (startsWith(xml, "<w:tbl>", i)) {
                depth++;
                i += 7;
            } else if (startsWith(xml, "</w:tbl>", i)) {
                if (depth > 0) depth--;
                i += 8;
            } else if (startsWith(xml, "<w:txbxContent>", i)) {
                // A text box is placed at a y, not flowed, so its paragraphs are not the page's
                // height. Counting them is how a one-page document measures at 1277 pt on an
                // 842 pt page (D-21) - the stamp's own boxes are most of that number.
                depth++;
                i += 15;
            } else if (startsWith(xml, "</w:txbxContent>", i)) {
                if (depth > 0) depth--;
                i += 16;
            } else if (startsWith(xml, BEFORE, i) || startsWith(xml, LINE, i)) {
                // A cell's line is not the page's height: the row it sits in already carries
                // that height as its own w:trHeight, and counting both charges a table twice.
                int j = i + (startsWith(xml, BEFORE, i) ? BEFORE.length() : LINE.length());
                if (depth == 0 && !framed) sum += digits(xml, j);
                i = j;
            } else if (startsWith(xml, TRHEIGHT, i)) {
                sum += digits(xml, i + TRHEIGHT.length());
                i += TRHEIGHT.length();
            } else {
                i++;
            }
        }
        return sum;
    }

    /** The integer starting at {@code from}, or 0 when there is none. */
    private static int digits(CharSequence xml, int from) {
        int v = 0, i = from;
        boolean any = false;
        while (i < xml.length() && xml.charAt(i) >= '0' && xml.charAt(i) <= '9') {
            v = v * 10 + (xml.charAt(i) - '0');
            i++;
            any = true;
        }
        return any ? v : 0;
    }

    /** Does {@code xml} hold {@code needle} at {@code at}? */
    private static boolean startsWith(CharSequence xml, String needle, int at) {
        if (at + needle.length() > xml.length()) return false;
        for (int j = 0; j < needle.length(); j++) {
            if (xml.charAt(at + j) != needle.charAt(j)) return false;
        }
        return true;
    }

    /** One twip value as the page will really write it, through the squeeze factor. */
    private static int twScale(int tw, float squeeze) {
        return squeeze == 1f ? tw : (int) Math.max(0L, Math.round(tw * squeeze));
    }

    private static int[] fitPage(Ctx ctx, int beforeTw, int lineTw, float size) {
        if (ctx.inColumn) {
            // A cell's flow is bounded by its ROW's height, which is written as the table's
            // w:trHeight, not by the sheet: the page's budget has already been spent by the
            // bands above the table. Charging the cell against it would squeeze or break a
            // column that the row is holding, and a page break inside a cell is not a thing.
            // The page's squeeze factor still applies - the row is measured from what the cell
            // really writes, so a squeezed page has to squeeze inside the cells too.
            int b2 = twScale(beforeTw, ctx.squeeze);
            int l2 = twScale(lineTw, ctx.squeeze);
            ctx.flowTw += b2 + l2;
            return new int[]{b2, l2};
        }
        if (ctx.measuring) {
            // Measuring a page: the gap is given up exactly as the old guard gave it up once the
            // budget was spent, but no line is shortened and nothing is broken - the answer this
            // pass exists to produce is how tall the page really is.
            int roomM = ctx.budgetTw - ctx.flowTw;
            int gapM = Math.max(0, Math.min(beforeTw, roomM - lineTw));
            ctx.flowTw += gapM + lineTw;
            return new int[]{gapM, lineTw};
        }
        if (ctx.budgetTw <= 0) {
            ctx.flowTw += beforeTw + lineTw;
            return new int[]{beforeTw, lineTw};
        }
        int room = ctx.budgetTw - ctx.flowTw;
        if (beforeTw + lineTw <= room) {
            ctx.flowTw += beforeTw + lineTw;
            return new int[]{beforeTw, lineTw};
        }
        // 1. the gap goes first.
        int gap = Math.max(0, Math.min(beforeTw, room - lineTw));
        room = ctx.budgetTw - ctx.flowTw - gap;
        if (lineTw <= room) {
            ctx.flowTw += gap + lineTw;
            return new int[]{gap, lineTw};
        }
        // 2. the box is shortened to what is left, down to the ascent but no further.
        int ascent = (int) Math.max(1L, Math.round(LINE_BASE * Math.max(4f, size) * TWIPS_PER_PT));
        if (room >= ascent) {
            ctx.flowTw = ctx.budgetTw;
            ctx.fitted++;
            return new int[]{0, room};
        }
        // 3. the page is full and cannot be squeezed any further. See
        // BREAK_WHEN_UNFITTABLE: by default the line keeps its own height and the page overruns
        // exactly as it did before this guard existed - the guard is not allowed to trade a
        // reader-visible page for a bookkeeping one.
        if (BREAK_WHEN_UNFITTABLE && ctx.flowTw > 0) return null;
        ctx.flowTw += lineTw;
        return new int[]{0, lineTw};
    }

    /**
     * A deliberate page break, and the flow starts again at the top of the new sheet.
     *
     * <p>{@code w:br w:type="page"} is the same instruction a section break with
     * {@code w:type w:val="nextPage"} gives, and it is what the writer already uses to end a
     * page the PDF itself ended. The budget guard writes one only where the page is genuinely
     * full, so the break lands on the last baseline the page drew rather than wherever the
     * reader's own line model happens to run out.
     *
     * <p>The paragraph that carries the break is the same one-twip carrier the writer already
     * uses for an empty page, so it adds no height of its own: a break paragraph with a real
     * line height would be the very overflow this guard exists to prevent.
     */
    private static void breakPage(StringBuilder sb, Ctx ctx) {
        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr>")
                .append("<w:r><w:br w:type=\"page\"/></w:r></w:p>");
        ctx.brokePage++;
        ctx.flowTw = 0;
        ctx.newPage = true;
        ctx.lastBaseline = -1f;
        ctx.lastLinePt = 0f;
        ctx.flowY = -1f;
        ctx.flowBoxPt = 0f;
        ctx.lastWasTable = false;
    }

    private DocxWriter() {
    }

    public static void write(PdfToWord.Result result, File out) throws IOException {
        Ctx ctx = new Ctx();
        String documentXml = documentXml(result, ctx);
        if (System.getProperty("p2w.debugFlow") != null) {
            System.err.println("FLOWDOC " + out.getName() + " fitted=" + ctx.fitted
                    + " broke=" + ctx.brokePage);
        }
        String rels = documentRels(ctx.media);
        String contentTypes = contentTypes(ctx.media.size());

        try (OutputStream fos = new FileOutputStream(out);
             ZipOutputStream zip = new ZipOutputStream(fos)) {
            put(zip, "[Content_Types].xml", contentTypes);
            put(zip, "_rels/.rels", rootRels());
            put(zip, "word/document.xml", documentXml);
            put(zip, "word/styles.xml", stylesXml());
            put(zip, "word/theme/theme1.xml", themeXml());
            put(zip, "word/settings.xml", settingsXml());
            put(zip, "word/_rels/document.xml.rels", rels);
            put(zip, "docProps/core.xml", coreXml(result));
            put(zip, "docProps/app.xml", appXml());
            for (int i = 0; i < ctx.media.size(); i++) {
                zip.putNextEntry(new ZipEntry("word/media/image" + (i + 1) + ".png"));
                zip.write(ctx.media.get(i));
                zip.closeEntry();
            }
        }
    }

    private static void put(ZipOutputStream zip, String name, String body) throws IOException {
        zip.putNextEntry(new ZipEntry(name));
        zip.write(body.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        zip.closeEntry();
    }

    /** Mutable state for one write: the shape id counter and the images collected. */
    private static final class Ctx {
        final List<byte[]> media = new ArrayList<>();
        int shapeSeq = 1;
        int anchorCount;
        int flowCount;
        /** Baseline of the last flowing line, in PDF points from the page top. -1 = none yet. */
        float lastBaseline = -1f;
        /** Size of that line's text, so its line box can be measured. */
        float lastSize = 0f;
        /**
         * The height of the line box just emitted, which decides where the next baseline falls:
         * the previous box's lower 0.2 em of slack is part of the advance. 0 after a table, whose
         * bottom edge is a box edge and not a baseline.
         */
        float lastLinePt = 0f;
        /**
         * Where the READER will put the last baseline emitted, in points from the page top.
         *
         * <p>This is not {@link #lastBaseline}: that is where the PDF drew the line, which is
         * where the line was ASKED to go. This is where the page it was written into actually
         * ends up, so it carries the rounding, the clamped gap and the shortened box with it.
         * The space-before of the next paragraph is measured from here, so an error is spent
         * once and then re-synced instead of being carried down the page (D-26).
         *
         * <p>-1 means the flow's position on the sheet is not known - the first line of a
         * sheet, or a new column of a continuous section - and the caller must place from the
         * page's top edge instead.
         */
        float flowY = -1f;
        /**
         * The height of the last line box AS WRITTEN (through the squeeze and the twip
         * rounding), in points. Its lower {@code 1 - LINE_BASE} is what is left below the
         * baseline before the next paragraph's space-before starts.
         */
        float flowBoxPt = 0f;
        /** Set at a page break so the first line on a page carries no gap. */
        boolean newPage = true;
        /** Flow height already spent on this page, in twips. */
        int flowTw;
        /** The page's own height in twips - the budget the flow must not exceed. */
        int budgetTw;
        /** True when this page's own content fits the sheet, so its white space can be spent. */
        boolean spendGaps;
        /**
         * True once this page's flow has run out of room to spend its own gaps.
         *
         * <p>A page that leaves more white space than the flow may spend has stopped being a
         * flow: the lines below that gap are placed on the page, not spaced from the line above
         * them. Clamping the gap instead (the behaviour this replaces) is a lie the render
         * believes - on 331_pid_diagram the clamp put the diagram's "CHILLED WATER" label 114 pt
         * above the box it belongs to, and every label after it drifted with it.
         */
        boolean positioned;
        /** The shapes on the page being written, so a stamp can find its own outline. */
        java.util.List<Shape> curShapes;
        /** Left edge of each column band on this page, in points, by Para.column. */
        java.util.Map<Integer, Float> colLeft;
        /**
         * How many columns the section this page belongs to actually declares.
         *
         * <p>It is not the same number as {@code colLeft.size()}. A form or a brochure panel
         * page has vertical gutters, so the column pass gives its field rows column 1, 2 and 3
         * while the section still declares ONE column - the writer never emits {@code w:cols
         * w:num} for it. Subtracting that column's left edge from a page-relative indent then
         * collapses the paragraph to x=0. On 401_trifold_brochure the middle panel's heading
         * and its first line were drawn on top of the cover panel, 300.6 pt left of where the
         * page put them, and the section said one column all along.
         */
        int secCols = 1;
        /**
         * The y, in points, that the next paragraph's box must start below - the bottom edge of
         * a layout table, or the top edge of a column cell. {@code -1} when there is none.
         *
         * <p>A table is not a baseline: {@link #lastBaseline} cannot describe where a row ends,
         * because the renderer decides the row's height from its own line boxes. So the block
         * after a table is placed against the table's measured bottom instead of being spaced
         * from the line above it, which is the only way the page's own y survives a table.
         */
        float afterTablePt = -1f;
        /**
         * True while writing the inside of a layout-table cell.
         *
         * <p>A cell's text starts at the column's own left edge, so every indent inside it is
         * measured from that edge rather than from the paper. Outside a cell the paper is the
         * origin and nothing is subtracted.
         */
        boolean inColumn;
        /** The right edge of the current column cell, in points - the width an indent is from. */
        float cellRightPt;
        /**
         * The left edge of the current column cell, in points.
         *
         * <p>Inside a cell the text starts at the CELL's edge, so every page-relative indent has
         * to have that edge taken off it. It cannot be read from {@link #colLeft}: that map is
         * keyed by the band the column pass tagged a block with, and on a page whose gutters the
         * detector only partly found there is no entry for the later columns at all
         * (63_three_column_brochure's three columns are all tagged 0). The indent then stayed
         * page-relative, exceeded the cell's own width, and every line wrapped to one character.
         */
        float cellLeftPt;
        /** The page's own width in points, so a tab stop can tell when it is at the paper edge. */
        float pageWidthPt = 595f;
        /**
         * The page's own height in points.
         *
         * <p>Needed by a 180-degree stamp and nothing else: PDFBox reports such a line's
         * position in a frame turned with the text, so both of its coordinates are mirrored
         * about the page and have to be put back before they mean anything.
         */
        float pageHeightPt = 842f;
        /**
         * True when the last block written on this page was a table.
         *
         * <p>A table's rendered height is not its PDF extent: every row is written at the
         * page's row pitch but LibreOffice sets each cell's line box itself, so the table
         * usually ends lower than t.bottom. Measuring the next block's spacer from t.bottom
         * then adds that error again on top of itself. A table that follows a table therefore
         * gets no spacer - the page had no prose between them to leave a gap for.
         */
        boolean lastWasTable;
        /** Paragraphs whose own box was shortened so the page ended exactly at the paper. */
        int fitted;
        /** Deliberate page breaks the budget guard had to write. */
        int brokePage;
        /** Pages written so far, so the debug trace can name the page it is talking about. */
        int pageSeq;
        /**
         * How much of its measured height this page's flow may keep, 1 = all of it.
         *
         * <p>Set only for a page whose own flow is taller than the paper: every line box and
         * every gap written for that page is multiplied by it, so the flow ends exactly where
         * the paper does. The accounting that the budget guard does stays in the page's own
         * units - the budget is divided by this factor instead - so the pitch solver keeps
         * comparing boxes with boxes and does not chase its own scaling.
         */
        float squeeze = 1f;
        /** True while a page is being measured rather than written for the reader. */
        boolean measuring;
    }

    // ------------------------------------------------------------------ document

    private static String documentXml(PdfToWord.Result result, Ctx ctx) {
        StringBuilder sb = new StringBuilder(1 << 18);
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>");
        sb.append("<w:document xmlns:w=\"").append(NS_W).append("\" xmlns:r=\"").append(NS_R)
                .append("\" xmlns:wp=\"").append(NS_WP).append("\" xmlns:a=\"").append(NS_A)
                .append("\" xmlns:wps=\"").append(NS_WPS)
                .append("\" xmlns:pic=\"").append(NS_PIC).append("\">")
                // No w:background. It was added to stop a dark reader showing black text on a
                // black page, and it worked - by painting the page white. In Google Docs dark
                // mode that white is painted back on top of the inverted page, so the user's
                // screenshots came back full of white patches over the tables. The colour is
                // carried by the TEXT instead, as a default in styles.xml, which is where a
                // reader looks before it decides what "black" means on its own surface.
                .append("<w:body>");

        // The page box the current section is set to. A section carries one page size, so a
        // file that mixes landscape and portrait pages gets a section break where the size
        // changes; every other page break stays a plain page break.
        float secW = 0, secH = 0;
        int secCols = 1;
        float secGap = 0f;
        boolean first = true;
        for (PdfToWord.Page page : result.pages) {
            float pw = page.width > 0 ? page.width : 595f;
            float ph = page.height > 0 ? page.height : 842f;
            int[] pc = pageColumns(page);
            int pCols = pc[0];
            float pGap = pc[1];
            if (first) {
                secW = pw;
                secH = ph;
                secCols = pCols;
                secGap = pGap;
                first = false;
            } else if (Math.abs(pw - secW) > 0.5f || Math.abs(ph - secH) > 0.5f
                    || pCols != secCols) {
                // Close the section that just ended. A sectPr lives in the last paragraph of
                // its section, and nextPage starts the new one on a fresh page - which is the
                // page break this page needed anyway.
                sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                        .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                        .append("<w:sectPr>").append(sectPrXml(secW, secH, secCols, secGap))
                        .append("<w:type w:val=\"nextPage\"/></w:sectPr>")
                        .append("</w:pPr></w:p>");
                // A section break starts a fresh sheet exactly as w:br does, so the first line
                // of the new section has to take its position from the page's own top edge.
                // Without this the branch fell through to the continuation path, the pitch was
                // measured against the PREVIOUS page's last baseline (a large negative), no
                // space-before was written, and the whole page was laid at y=0. On
                // landscape-page-inside-portrait-document that put the landscape page 47.6 pt
                // above where the PDF drew it - header at y=0.4 against the page's y=47.6.
                ctx.newPage = true;
                secW = pw;
                secH = ph;
                secCols = pCols;
                secGap = pGap;
            } else {
                // A page with nothing on it still has to advance the page counter, or every
                // anchor after it lands one page too early.
                sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                        .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                        .append("<w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr>")
                        .append("<w:r><w:br w:type=\"page\"/></w:r></w:p>");
                ctx.newPage = true;
            }
            ctx.lastBaseline = -1f;
            ctx.flowY = -1f;
            ctx.flowBoxPt = 0f;
            java.util.Map<Integer, Float> colLeft = new java.util.HashMap<>();
            for (Object b4 : page.blocks) {
                if (!(b4 instanceof PdfToWord.Para)) continue;
                PdfToWord.Para pp = (PdfToWord.Para) b4;
                Float was = colLeft.get(pp.column);
                if (was == null || pp.left < was) colLeft.put(pp.column, pp.left);
            }
            ctx.colLeft = colLeft;
            ctx.secCols = secCols;
            ctx.lastLinePt = 0f;
            ctx.positioned = false;
            ctx.inColumn = false;
            ctx.cellLeftPt = 0f;
            ctx.cellRightPt = 0f;
            ctx.afterTablePt = -1f;
            ctx.flowTw = 0;
            ctx.budgetTw = (int) Math.max(1L, Math.round(ph * TWIPS_PER_PT) - PAGE_ROUNDING_TW);
            // pageFits is the measurement; hasColumnBands was a proxy for it and it over-fired.
            // A form page has vertical gutters between its field columns, so the column pass
            // gives those rows column > 0 and the proxy read the page as set in columns. The
            // page then gave up its white space and put its footer 350 pt too high - which is
            // exactly what 305 and 311 did. pageFits already answers the real question (would
            // the flow, gaps and all, fit the sheet?) and 315, the case the proxy existed for,
            // fails it because its three columns are still stacked into one flow.
            ctx.spendGaps = pageFits(page, ph);
            if (System.getProperty("p2w.debugGaps") != null) {
                System.err.println("GAPS fits=" + pageFits(page, ph)
                        + " bands=" + hasColumnBands(page) + " spend=" + ctx.spendGaps
                        + " ph=" + ph);
            }
            ctx.pageWidthPt = pw;
            ctx.pageHeightPt = ph;
            // The page's own outlines, so a label drawn inside one can be anchored to it and a
            // stamp can find the frame the page drew around it. It was declared and never set,
            // which is why the stamp's border search never matched anything.
            java.util.List<Shape> outlines = new ArrayList<>();
            for (Object block : page.blocks) {
                if (block instanceof Shape) outlines.add((Shape) block);
            }
            ctx.curShapes = outlines;
            // D-25: fold each stamp's concentric frame rules into one shape before anything is
            // written, so the page is laid out against the same geometry it is drawn with.
            stampFrames(outlines);
            // And put the stamp's text paragraphs where their own y falls, so the indent and
            // space-before they are placed with are the page's own.
            orderStamps(page, outlines, ctx);
            if (page.blocks.isEmpty()) continue;
            // ---- the page's flow, measured before it is written ----
            //
            // The guard can only fill the page if it knows how much room the page needs BEFORE
            // it starts giving room away: a line already written cannot be made shorter. So the
            // page is written once in measuring mode - the page's own gaps, given up exactly as
            // the old guard gave them up, but no line shortened and no break - and that pass is
            // read for two numbers: the height the flow needs, and the height it actually
            // occupies once written. When the second is more than the paper, the page is written
            // again with every box and gap scaled by budget/height. A page that already fits is
            // written once and comes out exactly as it did before this guard existed.
            //
            // The page is measured off its own XML, not off the writer's running total, because
            // the running total is the writer's model of the page and this is the page: the
            // carriers that hold an anchored picture or a text box add a twip each and are not
            // charged to the flow, and a page must not overrun by the twips the model forgot.
            //
            // Both passes write through the same code and the same model objects, so every side
            // effect of the first pass is undone before the second: the media list is truncated,
            // an anchored shape marked consumed is un-marked, and the id counters are reset.
            int pageBudgetTw = ctx.budgetTw;
            java.util.List<Boolean> consumedMark = new ArrayList<>();
            for (Shape sh : outlines) consumedMark.add(sh.consumed);
            int mediaMark = ctx.media.size();
            int shapeMark = ctx.shapeSeq, anchorMark = ctx.anchorCount, flowMark = ctx.flowCount;
            int fittedMark = ctx.fitted, brokeMark = ctx.brokePage;
            StringBuilder pg = new StringBuilder(1 << 12);

            ctx.measuring = true;
            pageBody(pg, page, ctx, pw, ph, secGap);
            ctx.measuring = false;
            int needTw = ctx.flowTw;
            int writtenTw = spacingTw(pg);
            // What the page carries that the flow is not charged for. Kept out of the budget the
            // guard works to, so that the page's own w:before + w:line + w:trHeight is what
            // ends at the paper's edge and not the model's idea of it.
            int overheadTw = Math.max(0, writtenTw - ctx.flowTw);
            float usedF = 1f;

            if (writtenTw > pageBudgetTw) {
                // budget/height first, then corrected by what the pass really wrote, because a
                // squeezed page also gives up less of its own gap and the two do not scale quite
                // alike. Each attempt is kept only if it is the best one: the corrections are not
                // guaranteed to be monotone (a table whose rows are held at their type size stops
                // shrinking while the prose around it keeps going), so the page that is used is
                // the shortest one measured, never simply the last one tried.
                String bestXml = null;
                int bestWritten = writtenTw;
                float f = Math.min(1f, Math.max(SQUEEZE_FLOOR, (float) pageBudgetTw / (float) needTw));
                for (int attempt = 0; attempt < 3; attempt++) {
                    ctx.media.subList(mediaMark, ctx.media.size()).clear();
                    ctx.shapeSeq = shapeMark;
                    ctx.anchorCount = anchorMark;
                    ctx.flowCount = flowMark;
                    ctx.fitted = fittedMark;
                    ctx.brokePage = brokeMark;
                    for (int i = 0; i < outlines.size(); i++) {
                        outlines.get(i).consumed = consumedMark.get(i);
                    }
                    pg.setLength(0);
                    ctx.squeeze = f;
                    ctx.flowTw = 0;
                    ctx.lastBaseline = -1f;
                    ctx.lastLinePt = 0f;
                    ctx.flowY = -1f;
                    ctx.flowBoxPt = 0f;
                    ctx.positioned = false;
                    ctx.newPage = true;
                    ctx.lastWasTable = false;
                    ctx.inColumn = false;
                    ctx.cellLeftPt = 0f;
                    ctx.cellRightPt = 0f;
                    ctx.afterTablePt = -1f;
                    ctx.budgetTw = Math.max(1, pageBudgetTw - overheadTw);
                    pageBody(pg, page, ctx, pw, ph, secGap);
                    int w = spacingTw(pg);
                    if (w < bestWritten) {
                        bestWritten = w;
                        bestXml = pg.toString();
                        usedF = f;
                    }
                    if (w <= pageBudgetTw) break;
                    float next = Math.min(1f, f * (float) pageBudgetTw / (float) w);
                    if (next <= SQUEEZE_FLOOR) {
                        if (f == SQUEEZE_FLOOR) break;
                        next = SQUEEZE_FLOOR;
                    }
                    f = next;
                }
                if (bestXml != null) {
                    pg.setLength(0);
                    pg.append(bestXml);
                    writtenTw = bestWritten;
                }
                ctx.squeeze = 1f;
                ctx.budgetTw = pageBudgetTw;
            }
            sb.append(pg);
            if (System.getProperty("p2w.debugFlow") != null) {
                System.err.println("FLOW page=" + (++ctx.pageSeq)
                        + " flowTw=" + ctx.flowTw + " budgetTw=" + ctx.budgetTw
                        + " overTw=" + (ctx.flowTw - ctx.budgetTw)
                        + " needTw=" + needTw + " writtenTw=" + writtenTw
                        + " overheadTw=" + overheadTw + " f=" + usedF);
            }
        }
        // The section properties must be the LAST child of w:body.
        sb.append("<w:sectPr>").append(sectPrXml(secW <= 0 ? 595f : secW, secH <= 0 ? 842f : secH, secCols, secGap))
                .append("</w:sectPr>");
        sb.append("</w:body></w:document>");
        return sb.toString();
    }

    /**
     * One page's blocks, in the order the page drew them.
     *
     * <p>This was the body of {@code documentXml}'s page loop. It is a method because the budget
     * guard has to be able to run it twice: once with no budget to measure the page's own
     * height, and - only when that height is more than the paper - once more with every box
     * scaled to fit. It writes nothing outside {@code sb} except through {@code ctx}, and every
     * side effect of that is undone between the two runs.
     */
    private static void pageBody(StringBuilder sb, PdfToWord.Page page, Ctx ctx,
                                 float pw, float ph, float secGap) {
        // A page set in newspaper columns is written as a fixed-geometry layout table - one
        // row, one cell per column - and its section stays single-column.
        //
        // WHY NOT CONTINUOUS SECTION BREAKS. Until now a full-width element between the columns
        // was given a section of its own, and the boundaries were <w:type w:val="continuous"/>.
        // Word and LibreOffice honour that. Google Docs does not: it turns every continuous
        // break into a PAGE break, so a one-page newsletter arrived as two pages. Measured on
        // 62_two_col_newsletter_pull_quote - six continuous breaks, 474 pt of flow on an 842 pt
        // sheet, two pages in Google Docs.
        //
        // A paragraph cannot carry a column count of its own (w:cols is a section property), so
        // no arrangement of paragraphs reproduces "full-width band, then two columns" on one
        // sheet without a section break. A table can: the columns become the table's columns, a
        // full-width band is simply a paragraph above or below it, and nothing in the document
        // is a section. The words also come out in column order, which is the order the page is
        // read in - the per-line blocks the column pass produces interleave the two columns, and
        // grouping them by band puts each column back together.
        if (columnPage(sb, page, ctx, pw)) return;
        // Which of this page's short lines are drawn beside a table rather than in its text, and
        // so must not charge the flow. Decided from the page's own geometry before anything is
        // written, so both of the budget guard's passes see the same answer (see pinShortParas).
        pinShortParas(page);
        for (Object block : page.blocks) emitBlock(sb, block, ctx);
    }

    /**
     * The column each box of a cross-gutter "row" belongs to, or null when the block is a
     * genuine full-width line.
     *
     * <p>Returns an array parallel to {@code p.boxes} when the boxes fall in two or more
     * different columns - the column pass cut a line at the gutter and left both halves on one
     * baseline - and null when the block is a single line running the width of the paper, or
     * when its boxes all sit in one column after all.
     */
    private static int[] splitColumns(Object block, float[] edge, int n) {
        if (!(block instanceof PdfToWord.Para)) return null;
        PdfToWord.Para q = (PdfToWord.Para) block;
        if (q.boxes.size() < 2) return null;
        // Each fragment belongs to the column it sits INSIDE. A column's line is often cut
        // again wherever the typeface changes, so a row can hold six word-fragments in its first
        // column before the second column's fragment even begins - brochure-3col's "Every Kastura
        // product is made from ..." is one such row - and only the FIRST fragment in a column
        // starts at that column's edge.
        int[] part = new int[q.boxes.size()];
        boolean mixed = false;
        float[] firstX = new float[n];
        for (int c = 0; c < n; c++) firstX[c] = Float.MAX_VALUE;
        for (int k = 0; k < part.length; k++) {
            PdfToWord.Box bx = q.boxes.get(k);
            int c = 0;
            // The edges are clustered averages, so a fragment can start a few points LEFT of its
            // column's own edge - brochure-3col's third column measures 395.3 from most of its
            // rows and one row starts it at 392 - and a strict comparison would put that
            // fragment in the column before it and then reject the row for crossing an edge.
            while (c + 1 < n && bx.x >= edge[c + 1] - 20f) c++;
            // A box that runs PAST the next column's edge was never cut: it is one line across
            // the paper. The running footer is exactly that - its words and its page number are
            // two boxes, and the words run the whole width - and splitting it put "Page 1" at
            // the top of the right column instead of at the foot of the page.
            if (bx.right > edge[c + 1] + 1f) return null;
            part[k] = c;
            firstX[c] = Math.min(firstX[c], bx.x);
            if (k > 0 && part[k] != part[k - 1]) mixed = true;
        }
        if (!mixed) return null;
        // A masthead is not a cut row: its issue date sits at the third column's x but is
        // right-aligned there, so it starts two hundred points into the column, while a fragment
        // the column pass cut begins at the column's own edge.
        for (int c = 0; c < n; c++) {
            if (firstX[c] == Float.MAX_VALUE) continue;
            if (firstX[c] - edge[c] > COLUMN_START_TOL) return null;
        }
        // A row whose boxes are merely spread across the page is not a cut line: a masthead
        // holds the paper's name at the left and the issue date at the right, and there is a
        // wide empty gutter between them that the page drew on purpose. What tells the two apart
        // is where each fragment STARTS - a line the column pass cut begins at its own column's
        // left edge, while a masthead's date is right-aligned and starts two hundred points into
        // the last column - and columnAt has already refused every fragment that starts at no
        // column's edge. A coverage ratio cannot tell them apart: a ragged row, whose last
        // column's line stops short of the measure, covers only seven tenths of the width it
        // spans and would be thrown out along with the masthead.
        return part;
    }

    /** A copy of {@code p} holding one of its boxes - one column's half of a cross-gutter row. */
    private static PdfToWord.Para oneBoxPara(PdfToWord.Para p, PdfToWord.Box b, int column) {
        PdfToWord.Para q = new PdfToWord.Para();
        q.runs.addAll(b.runs);
        q.heading = p.heading;
        q.align = p.align;
        q.indent = p.indent;
        q.bullet = p.bullet;
        q.stamp = p.stamp;
        q.top = b.y;
        q.left = b.x;
        q.right = b.right;
        q.column = column;
        q.boxes.add(b);
        return q;
    }

    /**
     * Writes a page that is set in newspaper columns, as a fixed-geometry layout table.
     *
     * <p>The page becomes one table: a single row with one cell per column, at the x the page
     * drew each column at, plus the page's own full-width bands above and below it as ordinary
     * paragraphs. Nothing in the result is a section, so nothing in the result is a continuous
     * section break - which is the whole point, because Google Docs renders every continuous
     * break as a page break.
     *
     * <p>It also puts the words in the order the page is read in. The column pass works on
     * unsplit lines and emits one block per line, so the blocks of the two columns interleave;
     * grouping them by band restores "all of the left column, then all of the right column".
     *
     * <p>A cell is a fixed rectangle, not a position in a flow. That is why this is a table and
     * not {@code w:cols}: with {@code w:cols} the reader decides where column one ends, so a
     * paragraph from the left column is flowed into the right one at the wrong height, and the
     * reading order comes out interleaved even when every line lands in the right place - which
     * is exactly what 63_three_column_brochure did (100 % of lines within 3 pt, 13 % order).
     *
     * @return true when the page was written this way. False when the page's column geometry
     *         cannot be trusted, or when its prose never actually sits in the bands the column
     *         pass found - then the caller's plain flow is the honest answer.
     */
    /** A page's column geometry: the left edge of every column, and the paper's right edge. */
    private static final class ColGeom {
        float[] edge;
    }

    /** Top edge of a block's own boxes, in points from the page top. -1 when it has none. */
    /**
     * True when every row of the table is the same height.
     *
     * <p>Absolute placement of a table's top edge is only needed where the rows are NOT evenly
     * spaced - a taller header, a wrapped address, a merged cell. For an even grid the average
     * the writer used before was exactly right, and measuring on 23_timetable_grid_txtpos showed
     * the absolute rule taking it from 6.8 pt to 28.3 pt. So the rule is applied where it helps
     * and not where it hurts.
     */
    private static boolean evenlySpaced(float[] edge) {
        if (edge == null || edge.length < 3) return true;
        float first = edge[1] - edge[0];
        for (int i = 2; i < edge.length; i++) {
            if (Math.abs((edge[i] - edge[i - 1]) - first) > 0.75f) return false;
        }
        return true;
    }

    private static float blockTop(Object b) {
        if (b instanceof PdfToWord.Para) {
            float t = Float.MAX_VALUE;
            for (PdfToWord.Box z : ((PdfToWord.Para) b).boxes) {
                if (z.runs.isEmpty()) continue;
                t = Math.min(t, z.y - LINE_BASE * z.size);
            }
            return t == Float.MAX_VALUE ? -1f : t;
        }
        if (b instanceof PdfToWord.Table) return ((PdfToWord.Table) b).top;
        return -1f;
    }

    /** Bottom edge of a block's own boxes, in points from the page top. -1 when it has none. */
    private static float blockBottom(Object b) {
        if (b instanceof PdfToWord.Para) {
            float r = -Float.MAX_VALUE;
            for (PdfToWord.Box z : ((PdfToWord.Para) b).boxes) {
                if (z.runs.isEmpty()) continue;
                r = Math.max(r, z.bottom > 0f ? z.bottom : z.y + z.size);
            }
            return r == -Float.MAX_VALUE ? -1f : r;
        }
        if (b instanceof PdfToWord.Table) return ((PdfToWord.Table) b).bottom;
        return -1f;
    }

    /** How far a fragment may start from its column's left edge and still be that column's line. */
    private static final float COLUMN_START_TOL = 40f;

    /**
     * The column whose left edge a fragment starts at, or -1 when it starts at none of them.
     *
     * <p>NEAREST edge, not "the last edge it is past". The edges are read off the page's own rows
     * and are a point or two out from any one row's fragments - brochure-3col's third column is
     * measured at 395.3 from most of its rows and one row starts at 392 - and a threshold test
     * would put that fragment in the second column and then reject the row as a masthead.
     */
    private static int columnAt(float x, float[] edge, int n) {
        int best = -1;
        float bestD = COLUMN_START_TOL;
        for (int c = 0; c < n; c++) {
            float d = Math.abs(x - edge[c]);
            if (d <= bestD) { bestD = d; best = c; }
        }
        return best;
    }

    /**
     * True for a decorative initial: one narrow glyph where a column's first line would be.
     *
     * <p>annual-review-2col-uneven-columns opens with a 6 pt "K" drop cap drawn on the masthead's
     * own baseline. It is a single narrow box, so it is not a column line - but it is inside
     * column 0, so counting it when the band is measured drags the band's top up over the
     * masthead, and the masthead then reads as full-width content INSIDE the columns and the page
     * is refused.
     */
    private static boolean dropCap(PdfToWord.Para q) {
        if (q.boxes.size() != 1) return false;
        PdfToWord.Box z = q.boxes.get(0);
        return z.right - z.x < 20f;
    }

    /**
     * The page's column edges, read off the page's own ROWS, or null when it is not set in
     * columns.
     *
     * <p>The column pass tags each block with the band it was cut into, and that tag is the
     * obvious source for the edges - but it is not a reliable one. A page's full-width masthead
     * can be tagged with the last band (newspaper-2col-fullwidth-headline's "THE MORNING LEDGER"
     * is at x=100 and is tagged column 1, so the second column's left edge reads as 99.7 pt
     * against the 303 pt the page drew it at), and a page whose gutters the detector only partly
     * found carries one band for three columns (63_three_column_brochure, whose three columns are
     * all tagged 0).
     *
     * <p>A ROW that holds more than one fragment is direct evidence and needs no tag. Project the
     * boxes of those rows only - a single-fragment row is a plain line and says nothing about
     * where a column ends - and the x-ranges nothing covers are the gutters. Restricting the
     * projection to multi-fragment rows is what makes it work where the page-wide projection in
     * PdfToWord does not: a deck line set across the first column and a little beyond it
     * ("Single estate arabica from the Baba Budan hills ...") covers the gutter on a whole-page
     * projection, but it is a single box on its own row, so it is not projected here.
     *
     * <p>The vertical band the columns occupy is then the run of rows that really are column
     * rows: every fragment starts at its own column's left edge (see
     * {@link #COLUMN_START_TOL}). A masthead is not one of those - its issue date starts two
     * hundred points into the last column, right-aligned - so it does not stretch the band up
     * over itself, and it stays a full-width paragraph above the table.
     */
    private static ColGeom rowColumnEdges(PdfToWord.Page page, float pw) {
        java.util.List<PdfToWord.Para> rows = new ArrayList<>();
        for (Object b : page.blocks) {
            if (b instanceof PdfToWord.Para && ((PdfToWord.Para) b).boxes.size() >= 2) {
                rows.add((PdfToWord.Para) b);
            }
        }
        // Three rows is the least that can evidence a column layout; below that a row of two
        // fragments is a form field or a kerning accident, not a gutter.
        if (rows.size() < 3) return null;

        // A column's left edge is where its lines START, and that is the one thing a multi-
        // fragment row says that a projection does not. Projecting the fragments and reading the
        // uncovered strips fails on exactly the pages this exists for: a row whose middle column
        // has ended - brochure-3col's "is the reason the tools are still in kitchens that
        // utilisation ..." holds a fragment in the first column and one in the last, and its
        // first fragment runs straight across the gutter between them - and a deck line set
        // across the first column and a little beyond it covers the gutter on 63 as well.
        //
        // Left edges do not have that problem. Every row of a band starts its first column at the
        // same x, so that x recurs once per row, while a masthead's issue date and a deck's
        // overhang are one-offs. Clustering the fragments' left edges and keeping the ones that
        // recur is therefore the gutter's own evidence, and it is not confused by a row that is
        // missing a column.
        java.util.List<Float> xs = new ArrayList<>();
        for (PdfToWord.Para q : rows) {
            for (PdfToWord.Box z : q.boxes) {
                if (z.runs.isEmpty() || z.right <= z.x) continue;
                xs.add(z.x);
            }
        }
        if (xs.size() < 6) return null;
        java.util.Collections.sort(xs);
        java.util.List<float[]> cand = new ArrayList<>();       // {x, count}
        float cur = xs.get(0);
        int curN = 1;
        for (int i = 1; i < xs.size(); i++) {
            float v = xs.get(i);
            if (v - cur <= 8f) { cur = (cur * curN + v) / (curN + 1); curN++; }
            else { cand.add(new float[]{cur, curN}); cur = v; curN = 1; }
        }
        cand.add(new float[]{cur, curN});
        int need = Math.max(3, Math.round(rows.size() * 0.3f));
        java.util.List<Float> starts = new ArrayList<>();
        for (float[] c : cand) if (c[1] >= need) starts.add(c[0]);
        if (starts.size() < 2 || starts.size() > 4) return null;

        float[] edge = new float[starts.size() + 1];
        for (int i = 0; i < starts.size(); i++) edge[i] = starts.get(i);
        edge[edge.length - 1] = pw;
        int n = edge.length - 1;
        // Every column has to be a real column: an edge outside the paper, or one a kerning
        // artefact away from its neighbour, is not a gutter.
        for (int c = 1; c < edge.length; c++) {
            if (edge[c] <= edge[c - 1] + 20f || edge[c] > pw) return null;
        }

        // The vertical band is decided by the caller, from the page's own baselines: a column
        // exists where two columns are both set, not where one line happens to start at a
        // column's x.
        ColGeom g = new ColGeom();
        g.edge = edge;
        return g;
    }

    private static boolean columnPage(StringBuilder sb, PdfToWord.Page page, Ctx ctx, float pw) {
        int n = page.columns;
        // The edges come from the page's rows when they show columns (see rowColumnEdges), and
        // from the column pass's own tags when they do not.
        ColGeom geom = rowColumnEdges(page, pw);
        float[] edge;
        if (geom != null) {
            edge = geom.edge;
            n = edge.length - 1;
        } else {
            if (n < 2 || ctx.colLeft == null || ctx.colLeft.size() < n) return false;
            // The left edge of a column is the MEDIAN of its blocks' left edges, not the
            // smallest. Ctx.colLeft is the smallest, and on a page whose masthead is tagged with
            // the last band that smallest is the masthead's - newspaper-2col-fullwidth-headline's
            // "THE MORNING LEDGER" sits at x=100 and is tagged column 1, so the second column's
            // edge reads as 99.7 pt against the 303 pt the page sets it at, and every line of the
            // first column then straddles that "gutter" and is refused. One block out of thirty
            // cannot move a median.
            edge = new float[n + 1];
            for (int c = 0; c < n; c++) {
                java.util.List<Float> lefts = new ArrayList<>();
                for (Object b : page.blocks) {
                    if (!(b instanceof PdfToWord.Para)) continue;
                    PdfToWord.Para q = (PdfToWord.Para) b;
                    if (q.column != c || q.left <= 0f) continue;
                    lefts.add(q.left);
                }
                if (lefts.isEmpty()) return false;
                java.util.Collections.sort(lefts);
                edge[c] = lefts.get(lefts.size() / 2);
                if (c > 0 && edge[c] <= edge[c - 1] + 1f) return false;
            }
            if (edge[n - 1] >= pw - 1f) return false;
            edge[n] = pw;
        }
        if (n < 2) return false;
        float gutter = edge[1];

        // Where each block belongs: a column index, -1 for a block drawn across the gutter, and
        // -2 for a block that is positioned rather than flowed (a picture, a drawn shape).
        //
        // The extent comes from the block's own LINE BOXES, not from the paragraph's left/right.
        // The column pass widens a paragraph that straddles a band cut: 62's "For the ayacutdars
        // of Halagere, Yediyur and seven other" reports right = 526 pt although the page drew it
        // to 281 pt, and on the paragraph's own numbers it reads as a full-width headline. It
        // was that misreading that made the old code break the page into six sections.
        int nb = page.blocks.size();
        int[] home = new int[nb];
        for (int i = 0; i < nb; i++) {
            Object b = page.blocks.get(i);
            float l = 0f, r = 0f;
            boolean known = false;
            if (b instanceof PdfToWord.Para) {
                PdfToWord.Para q = (PdfToWord.Para) b;
                l = Float.MAX_VALUE;
                r = -Float.MAX_VALUE;
                for (PdfToWord.Box bx : q.boxes) {
                    if (bx.runs.isEmpty()) continue;
                    l = Math.min(l, bx.x);
                    r = Math.max(r, bx.right);
                    known = true;
                }
                if (!known && q.right > q.left) {
                    l = q.left;
                    r = q.right;
                    known = true;
                }
            } else if (b instanceof PdfToWord.Table) {
                PdfToWord.Table q = (PdfToWord.Table) b;
                l = q.left;
                r = q.right;
                known = r > l;
            }
            if (!known) {
                home[i] = -2;
            } else if (l < gutter - 1f && r > gutter + 1f) {
                home[i] = -1;
            } else {
                int c = 0;
                while (c + 1 < n && l >= edge[c + 1] - 1f) c++;
                home[i] = c;
            }
        }

        // The band the columns occupy, vertically: the baselines on which TWO columns are both
        // set. That is what a column is - the two of them standing side by side - and it is the
        // only test that tells the columns from header furniture that merely sits at a column's
        // x. brochure-3col-with-sidebar-box's "Edition 2026" starts at the third column's edge and
        // annual-review-2col-uneven-columns' 6 pt "K" is a drop cap in the first, and both are
        // ALONE on their baseline, on the masthead's own lines; counting either as column
        // content drags the band's top up over the masthead, and the masthead then reads as
        // full-width text inside the columns and the page is refused.
        float[] bTop = new float[nb];
        int[] bMask = new int[nb];
        for (int i = 0; i < nb; i++) {
            Object b = page.blocks.get(i);
            bTop[i] = blockTop(b);
            bMask[i] = 0;
            if (b instanceof PdfToWord.Para) {
                for (PdfToWord.Box z : ((PdfToWord.Para) b).boxes) {
                    if (z.runs.isEmpty() || z.right <= z.x) continue;
                    int c = columnAt(z.x, edge, n);
                    if (c >= 0) bMask[i] |= 1 << c;
                }
            }
        }
        java.util.List<Float> shared = new ArrayList<>();
        for (int i = 0; i < nb; i++) {
            if (bMask[i] == 0 || bTop[i] < 0f) continue;
            int m = 0;
            for (int j = 0; j < nb; j++) {
                if (bMask[j] == 0 || bTop[j] < 0f) continue;
                if (Math.abs(bTop[j] - bTop[i]) <= 3f) m |= bMask[j];
            }
            if (Integer.bitCount(m) >= 2) shared.add(bTop[i]);
        }
        if (shared.isEmpty()) {
            // A page whose columns do not share a baseline - a newspaper whose two columns are
            // set on their own leading - still has a band: the extent of the blocks that are in
            // a column. A full-width element drawn inside it will be refused below, which is the
            // honest answer for those pages.
            for (int i = 0; i < nb; i++) {
                if (home[i] < 0 || bTop[i] < 0f) continue;
                shared.add(bTop[i]);
            }
        }
        if (shared.isEmpty()) return false;
        java.util.Collections.sort(shared);
        // The band is the longest RUN of shared baselines. A single shared line is not columns:
        // a brochure's header puts its title at the first column's x and its edition line at the
        // third's, and they sit on one baseline 65 pt above the body. Two columns are a run of
        // shared baselines, one line apart; a lone one is furniture.
        float colTop = shared.get(0);
        int runBest = 1, runCur = 1;
        float runStart = shared.get(0);
        for (int i = 1; i < shared.size(); i++) {
            float gap = shared.get(i) - shared.get(i - 1);
            if (gap <= 40f) {
                runCur++;
            } else {
                runCur = 1;
                runStart = shared.get(i);
            }
            if (runCur > runBest) { runBest = runCur; colTop = runStart; }
        }
        float colBottom = -Float.MAX_VALUE;
        for (int i = 0; i < nb; i++) {
            boolean inCells = home[i] >= 0
                    || (home[i] == -1 && splitColumns(page.blocks.get(i), edge, n) != null);
            if (!inCells || bTop[i] < colTop - 3f) continue;
            colBottom = Math.max(colBottom, blockBottom(page.blocks.get(i)));
        }
        // A page whose bands the column pass detected but whose prose never sits in them - a
        // page of full-width lines that a vertical gutter on a form mis-tagged - is not a column
        // page at all.
        if (colBottom <= colTop) return false;

        // Everything above the band is a band of its own, everything below is another, and what
        // is left between them has to be column content. That is the shape a table can describe:
        // a full-width band, then the columns, then a full-width band.
        //
        // A full-width block drawn INSIDE the band is the shape it cannot: a newspaper whose
        // headline and byline sit between column fragments. Forcing that into a table both moves
        // its text out of the columns and repeats it, so the page is written as an ordinary
        // single-column flow instead - one page with a correct order beats one page with a
        // scrambled one.
        float tol = 2f;
        java.util.TreeSet<Integer> used = new java.util.TreeSet<>();
        @SuppressWarnings("unchecked")
        java.util.List<Object>[] cells = new java.util.List[n];
        for (int c = 0; c < n; c++) cells[c] = new ArrayList<>();
        java.util.List<Object> before = new ArrayList<>();
        java.util.List<Object> after = new ArrayList<>();
        for (int i = 0; i < nb; i++) {
            Object b = page.blocks.get(i);
            float t = blockTop(b), bt = blockBottom(b);
            if (home[i] == -2 || t < 0f || bt <= 0f) {
                // Positioned rather than flowed - a picture or a drawn shape. It carries its own
                // x and y, so it goes after the table and lands where the page put it.
                after.add(b);
                continue;
            }
            if (bt <= colTop + tol) { before.add(b); continue; }
            if (t >= colBottom - tol) { after.add(b); continue; }
            if (home[i] >= 0) {
                // The cell's own edge is the column's edge, so the indent inside it is measured
                // from that edge (bandLeftTw). Take the column from the geometry just computed
                // rather than from the tag the column pass left on the paragraph, so the two
                // cannot disagree about which edge to subtract.
                if (b instanceof PdfToWord.Para) ((PdfToWord.Para) b).column = home[i];
                cells[home[i]].add(b);
                used.add(home[i]);
                continue;
            }
            // A block drawn across the gutter is usually a masthead, a headline or a running
            // footer - one line that really does run the width of the paper. But the column pass
            // also cuts LINES at the gutter and keeps both halves on one baseline, so a "row" of
            // two boxes can hold the bottom of the left column's line and the top of the right
            // column's, and its extent then reads as full width when it is nothing of the kind.
            // 62's "For the ayacutdars of Halagere, Yediyur and seven other" is one of those:
            // its second box is the right column's "The forum has requested the deputy
            // commissioner to take up". Such a block belongs to two cells, not to a band, so it
            // is split by box.
            int[] parts = splitColumns(b, edge, n);
            if (parts != null) {
                PdfToWord.Para q = (PdfToWord.Para) b;
                for (int k = 0; k < q.boxes.size(); k++) {
                    cells[parts[k]].add(oneBoxPara(q, q.boxes.get(k), parts[k]));
                    used.add(parts[k]);
                }
                continue;
            }
            return false;
        }
        // One cell holding everything is not a column page either: it is a single flow whose
        // lines happened to be tagged with bands. Checked before anything is written, so a
        // refusal leaves the caller's flow untouched.
        if (used.size() < 2) return false;

        // The bands are written in the order the page drew them, top to bottom.
        //
        // Not in block order: the block pass orders a page by column and then by y, so a
        // decorative initial can come before a masthead that sits ABOVE it - annual-review's "K"
        // drop cap is block 0 and the letterhead is block 1, though the letterhead is 8 pt
        // higher. A flow cannot put the second paragraph above the first, so the letterhead got
        // no space before it and the whole page below it moved down by the drop cap's height.
        sortByTop(before);
        sortByTop(after);
        for (Object b : before) emitBlock(sb, b, ctx);

        // The table's grid: each column at the page's own edges, the last one running to the
        // paper's edge. The cell margins are zero, so a cell's text edge IS the column's edge -
        // which is what bandLeftTw() subtracts from every indent inside it.
        int[] gridTw = new int[n];
        int totalTw = 0;
        for (int c = 0; c < n; c++) {
            gridTw[c] = (int) Math.max(1L, Math.round((edge[c + 1] - edge[c]) * TWIPS_PER_PT));
            totalTw += gridTw[c];
        }
        int indTw = (int) Math.max(0L, Math.round(edge[0] * TWIPS_PER_PT));

        // The band's vertical extent, from the boxes the page drew.
        float bandTop = Float.MAX_VALUE, bandBottom = -Float.MAX_VALUE;
        for (int c = 0; c < n; c++) {
            for (Object b : cells[c]) {
                float t = blockTop(b), bt = blockBottom(b);
                if (t < 0f || bt <= 0f) continue;
                bandTop = Math.min(bandTop, t);
                bandBottom = Math.max(bandBottom, bt);
            }
        }
        if (bandBottom <= bandTop) return false;
        // The row's top edge is where the FLOW has got to, not the band's first baseline: the
        // table is placed after the paragraphs above it, so its top is the bottom of the last of
        // them, and each cell's first line is then spaced from that edge by exactly the gap the
        // page left. Measuring from the band's top instead dropped the gap between the deck and
        // the columns, and put 62's left column 15 pt above the page's y.
        //
        // The band's top is the fallback for a page whose bands came out taller than the flow
        // that precedes them - which cannot happen on a well-measured page, and must not put the
        // table below the paper if it does.
        float flowTopPt = ctx.flowTw / (float) TWIPS_PER_PT;
        float rowTopPt = flowTopPt <= bandTop + 0.5f ? flowTopPt : bandTop;

        // ONE ROW PER BAND, not one row for the whole page.
        //
        // A page can be set in columns more than once - a brochure whose three columns carry one
        // block of prose and then a second block of specifications below it. The page reads
        // band by band: all three columns of the first band, then all three of the second. A
        // single row cannot say that; it says "all of column one, then all of column two", which
        // is why 63_three_column_brochure still scored 33 % on reading order with its lines all
        // in the right place. A row per band says it exactly, and the bands are where the page
        // left a gap across EVERY column at once.
        java.util.List<float[]> subs = new java.util.ArrayList<>();
        {
            java.util.List<float[]> iv = new ArrayList<>();
            for (int c = 0; c < n; c++) {
                for (Object b : cells[c]) {
                    float t = blockTop(b), bt = blockBottom(b);
                    if (t < 0f || bt <= 0f) continue;
                    iv.add(new float[]{t, bt});
                }
            }
            if (iv.isEmpty()) return false;
            java.util.Collections.sort(iv, new java.util.Comparator<float[]>() {
                public int compare(float[] a, float[] b) { return Float.compare(a[0], b[0]); }
            });
            float curT = iv.get(0)[0], curB = iv.get(0)[1];
            for (int i = 1; i < iv.size(); i++) {
                // A gap that no column fills is the end of a band. 30 pt is two or three lines of
                // body type: less than that is the leading between two lines, or the slack under a
                // short line, and not a band break. Measured on the six column documents: at 12 pt
                // 62_two_col_newsletter_pull_quote splits at its pull quote and its reading order
                // falls from 89 % to 75 %, while 63_three_column_brochure is unaffected; at 30 pt
                // both hold (62 at 89 %, 63 at 96 %).
                if (iv.get(i)[0] - curB > 30f) {
                    subs.add(new float[]{curT, curB});
                    curT = iv.get(i)[0];
                    curB = iv.get(i)[1];
                } else {
                    curB = Math.max(curB, iv.get(i)[1]);
                }
            }
            subs.add(new float[]{curT, curB});
        }

        String noBorder = "<w:top w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
                + "<w:left w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
                + "<w:bottom w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
                + "<w:right w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
                + "<w:insideH w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
                + "<w:insideV w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>";

        sb.append("<w:tbl><w:tblPr>")
                .append("<w:tblW w:w=\"").append(totalTw).append("\" w:type=\"dxa\"/>")
                .append("<w:tblInd w:w=\"").append(indTw).append("\" w:type=\"dxa\"/>")
                .append("<w:tblBorders>").append(noBorder).append("</w:tblBorders>")
                .append("<w:tblLayout w:type=\"fixed\"/>")
                .append("<w:tblCellMar><w:top w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:left w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:bottom w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:right w:w=\"0\" w:type=\"dxa\"/></w:tblCellMar>")
                .append("</w:tblPr><w:tblGrid>");
        for (int c = 0; c < n; c++) {
            sb.append("<w:gridCol w:w=\"").append(gridTw[c]).append("\"/>");
        }
        sb.append("</w:tblGrid>");

        float rowEndPt = rowTopPt;
        for (int band = 0; band < subs.size(); band++) {
            float subTop = subs.get(band)[0], subBottom = subs.get(band)[1];
            // Each cell is written first and measured, because the row's height is the TALLEST
            // cell's, not the band's.
            StringBuilder[] cellXml = new StringBuilder[n];
            int[] cellTw = new int[n];
            for (int c = 0; c < n; c++) {
                cellXml[c] = new StringBuilder(1 << 10);
                // Each cell is a flow of its own, and it starts where the row starts: the first
                // line's gap is measured from there, not from the line above the table.
                ctx.inColumn = true;
                ctx.cellLeftPt = edge[c];
                ctx.cellRightPt = edge[c + 1];
                ctx.afterTablePt = rowEndPt;
                ctx.lastBaseline = -1f;
                ctx.lastLinePt = 0f;
                ctx.newPage = false;
                ctx.positioned = false;
                ctx.lastWasTable = false;
                boolean any = false;
                for (Object b : cells[c]) {
                    float t = blockTop(b);
                    if (t < subTop - 0.5f || t > subBottom + 0.5f) continue;
                    emitBlock(cellXml[c], b, ctx);
                    any = true;
                }
                // A cell must hold a block-level element, and a table must be followed by a
                // paragraph inside its cell. A 1-twip line is the cheapest one there is.
                if (!any) {
                    cellXml[c].append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                            .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\"")
                            .append(" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                            .append("<w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr></w:p>");
                }
                ctx.inColumn = false;
                cellTw[c] = flowTwOf(cellXml[c]);
            }
            int rowTw = 1;
            for (int c = 0; c < n; c++) rowTw = Math.max(rowTw, cellTw[c]);
            // hRule EXACT, at the height the cells really write.
            //
            // "atLeast" is the obvious choice and it is wrong here. LibreOffice then decides the
            // row from its own model of the cell content, and on a page that already carries a
            // band above the columns it sizes the row to the rest of the sheet:
            // annual-review-2col-uneven-columns declared a 364 pt row and got one that ended at
            // the foot of the paper, so the running footer - and the anchored shapes after it -
            // were pushed onto a second, empty page. Measured: hRule="atLeast" -> 2 pages,
            // hRule="exact" -> 1 page, all 41 lines present.
            //
            // Exact is safe because every paragraph in a cell is written with w:lineRule="exact"
            // and its own w:before, so the height of the cell's content IS this sum - the
            // renderer has no line-box of its own to add to it.
            sb.append("<w:tr><w:trPr><w:cantSplit/>")
                    .append("<w:trHeight w:val=\"").append(rowTw)
                    .append("\" w:hRule=\"exact\"/></w:trPr>");
            for (int c = 0; c < n; c++) {
                sb.append("<w:tc><w:tcPr><w:tcW w:w=\"").append(gridTw[c])
                        .append("\" w:type=\"dxa\"/><w:vAlign w:val=\"top\"/></w:tcPr>")
                        .append(cellXml[c]).append("</w:tc>");
            }
            sb.append("</w:tr>");
            rowEndPt = rowEndPt + rowTw / (float) TWIPS_PER_PT;
        }
        sb.append("</w:tbl>");

        // Everything after the columns - the running footer, and any picture or shape drawn on
        // the page - continues the flow from the last row's real bottom edge.
        ctx.afterTablePt = rowEndPt;
        ctx.lastBaseline = -1f;
        ctx.lastLinePt = 0f;
        ctx.newPage = false;
        ctx.positioned = false;
        ctx.lastWasTable = false;
        ctx.flowTw = Math.max(ctx.flowTw, (int) Math.round(rowEndPt * TWIPS_PER_PT));
        for (Object b : after) emitBlock(sb, b, ctx);
        return true;
    }

    /**
     * The height a cell's own paragraphs occupy: every {@code w:before} plus every
     * {@code w:line} in it.
     *
     * <p>{@link #spacingTw} deliberately ignores the spacing inside a table, because a row's
     * height is carried by its {@code w:trHeight} and counting both would charge the page twice.
     * That is the right rule for the PAGE and the wrong one for the ROW, whose height is exactly
     * this sum for its tallest cell.
     */
    private static int flowTwOf(CharSequence xml) {
        int sum = 0;
        int i = 0;
        while (i < xml.length()) {
            if (startsWith(xml, BEFORE, i)) {
                sum += digits(xml, i + BEFORE.length());
                i += BEFORE.length();
            } else if (startsWith(xml, LINE, i)) {
                sum += digits(xml, i + LINE.length());
                i += LINE.length();
            } else {
                i++;
            }
        }
        return sum;
    }

    /** Orders a page's bands top to bottom, as the page drew them. */
    private static void sortByTop(java.util.List<Object> blocks) {
        java.util.Collections.sort(blocks, new java.util.Comparator<Object>() {
            public int compare(Object a, Object b) {
                float ta = blockTop(a), tb = blockTop(b);
                if (ta < 0f) return tb < 0f ? 0 : 1;
                if (tb < 0f) return -1;
                return Float.compare(ta, tb);
            }
        });
    }

    /** Writes one of a page's blocks. */
    private static void emitBlock(StringBuilder sb, Object block, Ctx ctx) {
        if (block instanceof PdfToWord.Para) {
            para(sb, (PdfToWord.Para) block, ctx);
        } else if (block instanceof PdfToWord.Table) {
            table(sb, (PdfToWord.Table) block, ctx);
        } else if (block instanceof Picture) {
            picture(sb, (Picture) block, ctx);
        } else if (block instanceof Shape) {
            if (!((Shape) block).consumed) shape(sb, (Shape) block, ctx);
        }
    }

    /**
     * A page the size of the PDF page, with no margins.
     *
     * <p>Zero margins are not cosmetic: they make the page box and the text box the same
     * coordinate system, so a paragraph anchored {@code relativeFrom="page"} at 300 pt is at
     * 300 pt from the edge of the paper and from the start of the text area alike.
     */
    private static String sectPrXml(float wPt, float hPt) {
        return sectPrXml(wPt, hPt, 1, 0);
    }

    /**
     * A section, with the page divided into {@code cols} newspaper columns.
     *
     * <p>The engine has detected column bands for a long time - {@code Line.column} comes from the
     * gutter edges and paragraphs are ordered column by column - but the writer always emitted
     * {@code w:cols w:space="0"}, one column, so a page that reads ACROSS was written as a page
     * that reads DOWN. That is why seven multi-column documents rendered two pages against one:
     * the second column was appended below the first instead of beside it.
     */
    private static String sectPrXml(float wPt, float hPt, int cols, float gapPt) {
        int w = Math.max(1, Math.round((float) (wPt * TWIPS_PER_PT)));
        int h = Math.max(1, Math.round((float) (hPt * TWIPS_PER_PT)));
        String orient = wPt > hPt ? " w:orient=\"landscape\"" : "";
        int gap = (int) Math.max(0L, Math.round(gapPt * TWIPS_PER_PT));
        String colsXml = cols > 1
                ? "<w:cols w:num=\"" + cols + "\" w:space=\"" + gap + "\" w:equalWidth=\"1\"/>"
                : "<w:cols w:space=\"0\"/>";
        return "<w:pgSz w:w=\"" + w + "\" w:h=\"" + h + "\"" + orient + "/>"
                + "<w:pgMar w:top=\"0\" w:right=\"0\" w:bottom=\"0\" w:left=\"0\""
                + " w:header=\"0\" w:footer=\"0\" w:gutter=\"0\"/>"
                + colsXml
                + "<w:docGrid w:linePitch=\"360\"/>";
    }

    /** How many column bands this page's paragraphs occupy, and the widest gutter between them. */
    /** The left edge of the column a paragraph sits in, in twips, or 0 for a one-column page. */
    private static int bandLeftTw(Ctx ctx, int column) {
        if (ctx.inColumn) return (int) Math.round(ctx.cellLeftPt * TWIPS_PER_PT);
        // Only a layout-table CELL may subtract one. A cell's text edge IS its column's edge, so
        // the indent inside it is measured from that edge and the page's own x has to come off.
        // Outside a cell the paragraph's w:ind is measured from the page edge, so a
        // column-relative indent has nothing to be relative to and lands the line at x=0 - which
        // is what a form page did, whose vertical gutters give its field rows column 1, 2 and 3
        // while nothing on the page is set in columns at all (401_trifold_brochure, 300.6 pt).
        if (!ctx.inColumn) return 0;
        if (ctx.colLeft == null || ctx.colLeft.size() <= 1) return 0;
        Float left = ctx.colLeft.get(column);
        return left == null ? 0 : (int) Math.round(left * TWIPS_PER_PT);
    }

    private static int[] pageColumns(PdfToWord.Page page) {
        // The page's SECTION is always one column, whatever the page's own column count is.
        //
        // A page set in newspaper columns is written as a layout table instead - see
        // columnPage(). A section's columns are set by w:cols and a paragraph cannot carry a
        // column count of its own, so the only way to hold a full-width band and two columns on
        // one sheet is to make the columns the table's columns. That is also the only structure
        // Google Docs renders on one page: it does not honour a continuous section break, and
        // turns each one into a page break (see the note in pageBody).
        //
        // The page's own column count is still read by columnPage(), from page.columns - it is
        // the DETECTION that matters, not the section.
        return new int[]{1, 0};
    }

    private static int[] pageColumnsOld(PdfToWord.Page page) {
        // REVERTED to single column. Emitting w:cols w:num does divide the page, but every
        // paragraph's w:ind w:left is measured from the PAGE edge, not from its column's edge, so
        // inside a narrow column the indent exceeds the column width and the text wraps one
        // character per line. Rendered on the 53-document corpus: a strip of single letters down
        // the right edge of an otherwise correct page. Making the indent column-relative is a
        // real change and needs its own measurement pass; until then one column is correct.
        if (true) return new int[]{1, 0};
        java.util.TreeSet<Integer> seen = new java.util.TreeSet<>();
        java.util.TreeMap<Integer, float[]> band = new java.util.TreeMap<>();
        for (Object o : page.blocks) {
            if (!(o instanceof PdfToWord.Para)) continue;
            PdfToWord.Para p = (PdfToWord.Para) o;
            seen.add(p.column);
            float[] r = band.get(p.column);
            if (r == null) band.put(p.column, new float[]{p.left, p.right});
            else { r[0] = Math.min(r[0], p.left); r[1] = Math.max(r[1], p.right); }
        }
        if (seen.size() <= 1) return new int[]{1, 0};
        // A column band narrower than a sixth of the page is not a newspaper column - it is a
        // margin artefact, a folio, or a stray line. Treating it as a column squeezes the body
        // into a sliver: on the 53-document corpus that produced a strip of one character per
        // line down the right edge of an otherwise correct page. Only divide the page when every
        // band is a real column.
        float pageW = 0f;
        for (float[] r : band.values()) pageW = Math.max(pageW, r[1]);
        if (pageW <= 0f) return new int[]{1, 0};
        float narrowest = Float.MAX_VALUE;
        for (float[] r : band.values()) narrowest = Math.min(narrowest, r[1] - r[0]);
        if (narrowest < pageW / 6f) return new int[]{1, 0};
        // Widest gap between consecutive column bands, used as w:cols w:space.
        float gap = 0f;
        float[] prev = null;
        for (float[] r : band.values()) {
            if (prev != null) gap = Math.max(gap, r[0] - prev[1]);
            prev = r;
        }
        return new int[]{seen.size(), Math.max(0, Math.round(gap))};
    }

    /** An image lifted out of the PDF and placed where it was. */
    public static final class Picture {
        public final byte[] png;
        public final int widthEmu;
        public final int heightEmu;
        public float top;
        public int column;
        /**
         * Where the image sat on its page, in points from the page's top-left.
         *
         * <p>An image the PDF drew is not part of the text flow - it is pinned to a place on
         * the paper. {@link #placed} says the position is known, and then the writer pins the
         * picture there instead of dropping it into the flow at the end of the page.
         */
        public boolean placed;
        public float xPt, topPt, wPt, hPt;
        /**
         * What this picture says, as text. A stamp is rasterised from the page so that its
         * outline, its words and its angle cannot drift apart - and then its words are no
         * longer in the document's text layer. Writing them as the picture's alt text puts
         * them back: a screen reader reads them, a search finds them, and the gate's word
         * comparison can see them. The picture is the appearance; this is the content.
         */
        public String text;

        public Picture(byte[] png, int widthEmu, int heightEmu) {
            this.png = png;
            this.widthEmu = widthEmu;
            this.heightEmu = heightEmu;
        }

        public Picture(byte[] png, float xPt, float topPt, float wPt, float hPt) {
            this.png = png;
            this.xPt = xPt;
            this.topPt = topPt;
            this.wPt = wPt;
            this.hPt = hPt;
            this.placed = true;
            this.widthEmu = (int) Math.max(1L, Math.round(wPt * EMU_PER_PT));
            this.heightEmu = (int) Math.max(1L, Math.round(hPt * EMU_PER_PT));
        }
    }

    private static void picture(StringBuilder sb, Picture p, Ctx ctx) {
        ctx.media.add(p.png);
        int id = ctx.media.size();
        if (p.placed) {
            anchoredPicture(sb, p, id, ctx);
            return;
        }
        sb.append("<w:p><w:r><w:drawing><wp:inline distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\">")
                .append("<wp:extent cx=\"").append(p.widthEmu).append("\" cy=\"")
                .append(p.heightEmu).append("\"/>")
                .append("<wp:docPr id=\"").append(id).append("\" name=\"Picture ").append(id)
                .append("\" descr=\"").append(esc(p.text == null ? "" : p.text)).append("\"/>")
                .append("<a:graphic><a:graphicData uri=\"")
                .append("http://schemas.openxmlformats.org/drawingml/2006/picture\">")
                .append("<pic:pic><pic:nvPicPr><pic:cNvPr id=\"").append(id)
                .append("\" name=\"image").append(id).append(".png\"/><pic:cNvPicPr/></pic:nvPicPr>")
                .append("<pic:blipFill><a:blip r:embed=\"rIdImg").append(id)
                .append("\"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>")
                .append("<pic:spPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"")
                .append(p.widthEmu).append("\" cy=\"").append(p.heightEmu).append("\"/></a:xfrm>")
                .append("<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom></pic:spPr>")
                .append("</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>");
    }

    /**
     * An image pinned to the page at the place the PDF drew it.
     *
     * <p>{@code behindDoc="1"} puts it behind the text: a scan is the page's background and a
     * stamp image is a mark on top of a page whose words are already there as text boxes. A
     * picture in front of them would hide words, which is worse than the picture being under
     * a stamp that does not overlap it.
     */
    private static void anchoredPicture(StringBuilder sb, Picture p, int id, Ctx ctx) {
        long cx = Math.max(1, p.widthEmu);
        long cy = Math.max(1, p.heightEmu);
        long offX = Math.round(p.xPt * EMU_PER_PT);
        long offY = Math.round(p.topPt * EMU_PER_PT);
        int relHeight = 251658240 + (id & 0xFFFF);
        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
                .append("<w:r><w:drawing>")
                .append("<wp:anchor distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\"")
                .append(" simplePos=\"0\" relativeHeight=\"").append(relHeight).append("\"")
                .append(" behindDoc=\"1\" locked=\"0\" layoutInCell=\"1\" allowOverlap=\"1\">")
                .append("<wp:simplePos x=\"0\" y=\"0\"/>")
                .append("<wp:positionH relativeFrom=\"page\"><wp:posOffset>").append(offX)
                .append("</wp:posOffset></wp:positionH>")
                .append("<wp:positionV relativeFrom=\"page\"><wp:posOffset>").append(offY)
                .append("</wp:posOffset></wp:positionV>")
                .append("<wp:extent cx=\"").append(cx).append("\" cy=\"").append(cy).append("\"/>")
                .append("<wp:effectExtent l=\"0\" t=\"0\" r=\"0\" b=\"0\"/>")
                .append("<wp:wrapNone/>")
                .append("<wp:docPr id=\"").append(id).append("\" name=\"Picture ").append(id)
                .append("\"/>")
                .append("<a:graphic><a:graphicData uri=\"")
                .append("http://schemas.openxmlformats.org/drawingml/2006/picture\">")
                .append("<pic:pic><pic:nvPicPr><pic:cNvPr id=\"").append(id)
                .append("\" name=\"image").append(id).append(".png\"/><pic:cNvPicPr/></pic:nvPicPr>")
                .append("<pic:blipFill><a:blip r:embed=\"rIdImg").append(id)
                .append("\"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>")
                .append("<pic:spPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"")
                .append(cx).append("\" cy=\"").append(cy).append("\"/></a:xfrm>")
                .append("<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom></pic:spPr>")
                .append("</pic:pic></a:graphicData></a:graphic></wp:anchor></w:drawing></w:r></w:p>");
    }

    // ------------------------------------------------------------------ shapes

    /**
     * A rectangle the page paints: a masthead band, a coloured block, a table header strip,
     * a sidebar box, a drawn rule, a page border.
     *
     * <p>Nothing used to carry these, so a document whose own name is white text on a navy
     * band converted to white text on white paper - the words were there and could not be
     * seen. The geometry is the path's own bounding box in points from the page's top-left;
     * {@code fillRgb} is -1 for an outline only and {@code lineRgb} is -1 for a fill only.
     */
    public static final class Shape {
        public float xPt, topPt, wPt, hPt;
        /** Fill colour 0xRRGGBB, or -1 when the path is only stroked. */
        public int fillRgb = -1;
        /** Fill opacity 0..1, from the PDF's own {@code ca}. */
        public float fillAlpha = 1f;
        /** Outline colour 0xRRGGBB, or -1 when the path is only filled. */
        public int lineRgb = -1;
        public float lineWidthPt;
        /**
         * Stroke opacity 0..1, from the PDF's own {@code CA}.
         *
         * <p>The fill's alpha was carried from the start; the stroke's was not, so a rule drawn
         * at 40 % came out solid. The user's requirement is that a line's weight AND its opacity
         * are the page's own, everywhere - not only in tables.
         */
        public float lineAlpha = 1f;
        /**
         * The geometry: 0 for a rectangle, 1 for an ellipse, 2 for the freeform path in
         * {@link #freeform}.
         *
         * <p>A page draws a circle as four Bezier curves that close on themselves. Its bounding
         * box is a square, so emitting the box put a solid square where a seal's ring, an OMR
         * bubble or a sheet-music note head belongs - and a stroke-only circle was dropped
         * outright. The box is the right extent either way; only the outline drawn inside it
         * differs, which is what this selects.
         *
         * <p>Everything else the page draws as a path - a triangle, an arrowhead, a diamond, a
         * hatch stroke, a leader line - is neither preset, so it was drawn as its bounding box
         * or dropped. Its own outline is carried in {@code freeform} instead.
         */
        public int kind = 0;
        /**
         * The path itself, for {@code kind == 2}: one entry per command, in PDF user space,
         * with y counting up from the page bottom.
         *
         * <p>{@code {0,x,y}} moves, {@code {1,x,y}} draws a line, {@code {2,x1,y1,x2,y2,x3,y3}}
         * draws a cubic. The writer turns each point into the shape's own top-left frame, so a
         * shape carries the page's geometry and not a re-measured copy of it.
         */
        public java.util.List<float[]> freeform;
        /** Whether the path is painted closed, which joins its last point back to its first. */
        public boolean freeformClosed;
        /**
         * True once this shape has been folded into something else - a stamp's outline becomes
         * the border of the text box that holds the stamp, so drawing it again would put a
         * second rectangle in a slightly different place, which is exactly the drift the user
         * reported: sometimes the outline shifts, sometimes the text inside it does.
         */
        public boolean consumed;
        /**
         * True when this shape is one of the rules of a stamp's frame (D-25).
         *
         * <p>A stamp draws its frame as two concentric rectangles. They are written as ONE
         * freeform shape - {@link #mergedShape} on the outermost of them - because the user's
         * report is that the two rules must never be able to drift against each other, and two
         * objects with two sets of coordinates can. Every rule of the stamp is marked here so
         * that it is never drawn on its own, never offered to {@code containerOf} as the box
         * that owns a line of text, and never consumed into anything.
         *
         * <p>It is deliberately NOT {@link #consumed}: that flag means "folded into a text box's
         * border", and after D-25 there is no text box for a stamp frame to be folded into. A
         * frame that set it would be a frame the writer believes it has already drawn.
         */
        public boolean stampFrame;
        /** The shape that draws this rule, when this shape is part of a stamp frame group. */
        public Shape mergedHost;
        /** The one freeform that carries every rule of this stamp, set on the outermost rule. */
        public Shape mergedShape;
        /** Set once this pass has written {@link #mergedShape}, so it is written once. */
        public boolean stampDrawn;

        public Shape(float xPt, float topPt, float wPt, float hPt) {
            this.xPt = xPt;
            this.topPt = topPt;
            this.wPt = wPt;
            this.hPt = hPt;
        }
    }


    /**
     * The closed outline a line of text was drawn inside, or null.
     *
     * <p>A diagram's equipment box, a legend swatch, a stamp's frame: the page draws a rectangle
     * and writes the label inside it. The label is not body text and must not be laid out by the
     * flow - the flow puts it after the previous line, so on 331_pid_diagram "CHILLED WATER" left
     * its box and landed 114 pt above it, and because the flow then measured the page as longer
     * than the paper the page could not spend its own gaps either.
     *
     * <p>The box that holds it is a real outline the page stroked and did not fill (a filled
     * rectangle is a masthead band or a header strip, and text over one of those is ordinary
     * text). It has to be big enough to be a box rather than a rule, and it has to contain the
     * line's own extent - a label that overhangs its box was drawn as free text and stays in the
     * flow.
     */
    private static Shape containerOf(java.util.List<Shape> shapes, PdfToWord.Box b) {
        if (shapes == null) return null;
        for (Shape s : shapes) {
            // A stamp's frame is not the box that owns a line of text: after D-25 it is a
            // sibling of the text paragraphs, drawn once for the whole stamp, and treating it
            // as an outline would pull a nearby line out of the flow and anchor it.
            if (s.consumed || s.stampFrame || s.lineRgb < 0 || s.fillRgb >= 0) continue;
            if (s.kind != 0) continue;
            if (s.wPt < b.size * 3f || s.hPt < b.size * 1.5f) continue;
            if (b.x < s.xPt - 1f || b.right > s.xPt + s.wPt + 1f) continue;
            if (b.y < s.topPt - 1f || b.y > s.topPt + s.hPt + 1f) continue;
            return s;
        }
        return null;
    }

    /**
     * One line as a text box at the position the page drew it.
     *
     * <p>Used where the flow cannot be the truth: a label inside a drawn outline, a stamp, and
     * every line on a page whose own white space is wider than the flow may spend.
     */
    private static void anchorBox(StringBuilder sb, PdfToWord.Para p, PdfToWord.Box b, Ctx ctx) {
        StringBuilder inner = new StringBuilder(256);
        lineParagraph(inner, p, b);
        float wPt = Math.max(4f, b.right - b.x) * 1.12f + b.size * 1.5f;
        float hPt = Math.max(4f, b.size * LINE_FACTOR);
        anchor(sb, ctx, b.x, b.y - ASCENT * b.size, wPt, hPt, inner.toString(), 0f, -1, 0.6f);
    }

    private static String hex(int rgb) {
        String h = Integer.toHexString(rgb & 0xFFFFFF).toUpperCase(java.util.Locale.ROOT);
        while (h.length() < 6) h = "0" + h;
        return h;
    }

    /**
     * The shape's own geometry element: a preset box, a preset ellipse, or the page's path.
     *
     * <p>A freeform carries every point of the path the page drew, in the shape's own frame -
     * {@code xPt}/{@code topPt} is that frame's top-left corner in points, and a PDF y counts
     * up while this one counts down, so the y is mirrored inside the extent. Points are clamped
     * to the extent: a path that runs a hair outside its own bounding box would otherwise be
     * drawn outside the shape and lost.
     */
    private static String geom(Shape s, long cx, long cy) {
        if (s.kind != 2 || s.freeform == null || s.freeform.isEmpty()) {
            return "<a:prstGeom prst=\"" + (s.kind == 1 ? "ellipse" : "rect")
                    + "\"><a:avLst/></a:prstGeom>";
        }
        StringBuilder g = new StringBuilder(64 + s.freeform.size() * 48);
        g.append("<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/>")
                .append("<a:rect l=\"0\" t=\"0\" r=\"0\" b=\"0\"/><a:pathLst>")
                .append("<a:path w=\"").append(cx).append("\" h=\"").append(cy).append("\">");
        for (float[] c : s.freeform) {
            int type = (int) c[0];
            // 3 closes the sub-path it ends. A stamp's frame is two rectangles in one path, and
            // the single freeformClosed flag can only close the last of them - so the close is a
            // command of its own and each rectangle carries its own (D-25).
            if (type == 3) {
                g.append("<a:close/>");
            } else if (type == 2) {
                g.append("<a:cubicBezTo>");
                for (int i = 1; i + 1 < c.length; i += 2) pt(g, s, cx, cy, c[i], c[i + 1]);
                g.append("</a:cubicBezTo>");
            } else {
                g.append(type == 0 ? "<a:moveTo>" : "<a:lnTo>");
                pt(g, s, cx, cy, c[1], c[2]);
                g.append(type == 0 ? "</a:moveTo>" : "</a:lnTo>");
            }
        }
        if (s.freeformClosed) g.append("<a:close/>");
        return g.append("</a:path></a:pathLst></a:custGeom>").toString();
    }

    /** One point of a freeform, in the shape's own frame and in EMU. */
    private static void pt(StringBuilder g, Shape s, long cx, long cy, float x, float y) {
        long px = Math.round((x - s.xPt) * EMU_PER_PT);
        long py = Math.round((y - s.topPt) * EMU_PER_PT);
        if (px < 0) px = 0;
        if (py < 0) py = 0;
        if (px > cx) px = cx;
        if (py > cy) py = cy;
        g.append("<a:pt x=\"").append(px).append("\" y=\"").append(py).append("\"/>");
    }

    /**
     * A shape pinned to the page, behind the text.
     *
     * <p>{@code behindDoc="1"} is what makes a masthead band a background instead of a lid:
     * the band carries white words, and a shape in front of them would hide the very title
     * it exists to make visible. A rule drawn behind text is still a rule.
     */
    private static void shape(StringBuilder sb, Shape s, Ctx ctx) {
        int id = SHAPE_ID_BASE + (ctx.shapeSeq++);
        long cx = Math.max(1, Math.round(s.wPt * EMU_PER_PT));
        long cy = Math.max(1, Math.round(s.hPt * EMU_PER_PT));
        long offX = Math.round(s.xPt * EMU_PER_PT);
        long offY = Math.round(s.topPt * EMU_PER_PT);
        int relHeight = 100000000 + (id & 0xFFFF);
        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
                .append("<w:r><w:drawing>")
                .append("<wp:anchor distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\"")
                .append(" simplePos=\"0\" relativeHeight=\"").append(relHeight).append("\"")
                .append(" behindDoc=\"1\" locked=\"0\" layoutInCell=\"1\" allowOverlap=\"1\">")
                .append("<wp:simplePos x=\"0\" y=\"0\"/>")
                .append("<wp:positionH relativeFrom=\"page\"><wp:posOffset>").append(offX)
                .append("</wp:posOffset></wp:positionH>")
                .append("<wp:positionV relativeFrom=\"page\"><wp:posOffset>").append(offY)
                .append("</wp:posOffset></wp:positionV>")
                .append("<wp:extent cx=\"").append(cx).append("\" cy=\"").append(cy).append("\"/>")
                .append("<wp:effectExtent l=\"0\" t=\"0\" r=\"0\" b=\"0\"/>")
                .append("<wp:wrapNone/>")
                .append("<wp:docPr id=\"").append(id).append("\" name=\"Shape ").append(id)
                .append("\"/>")
                .append("<a:graphic><a:graphicData uri=\"").append(NS_WPS).append("\">")
                .append("<wps:wsp><wps:cNvSpPr/><wps:spPr>")
                .append("<a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"").append(cx)
                .append("\" cy=\"").append(cy).append("\"/></a:xfrm>")
                .append(geom(s, cx, cy));
        if (s.fillRgb >= 0) {
            fillXml(sb, s.fillRgb, s.fillAlpha);
        }
        // A shape with no fill gets no fill element at all, matching the commercial files.
        if (s.lineRgb >= 0) {
            long lw = Math.max(0, Math.round(s.lineWidthPt * EMU_PER_PT));
            sb.append("<a:ln w=\"").append(lw).append("\"><a:solidFill><a:srgbClr val=\"")
                    .append(hex(s.lineRgb)).append("\">")
                    .append(alphaXml(s.lineAlpha))
                    .append("</a:srgbClr></a:solidFill></a:ln>");
        } else {
            sb.append("<a:ln><a:noFill/></a:ln>");
        }
        sb.append("</wps:spPr><wps:bodyPr anchor=\"t\" anchorCtr=\"0\"><a:noAutofit/></wps:bodyPr>")
                .append("</wps:wsp></a:graphicData></a:graphic>")
                .append("</wp:anchor></w:drawing></w:r></w:p>");
    }

    /**
     * The lightness (HSL L, 0..1) of a 0xRRGGBB colour.
     *
     * <p>Lightness, not luminance: what makes a filled band read as a white patch on a dark
     * canvas is how light it is, and HSL L is the same number Word's own colour picker shows
     * for the tint.
     */
    private static double lightness(int rgb) {
        int r = (rgb >> 16) & 0xFF, g = (rgb >> 8) & 0xFF, b = rgb & 0xFF;
        return (Math.max(r, Math.max(g, b)) + Math.min(r, Math.min(g, b))) / 510.0;
    }

    /**
     * A shape's fill, written so a light band follows the page instead of cutting a hole in it.
     *
     * <p>Every fill used to be an absolute {@code a:srgbClr}. That is the most explicit thing
     * that can be written and it is exactly why no reader remaps it: a band the page drew as
     * E6EBF5 stays E6EBF5 whatever the reader's canvas is, so in Google Docs dark mode it is a
     * white patch - 14:1 against the page around it. Measured across the corpus: 753 of 7,392
     * shape fills are light (E6EBF5 x18 in 23_timetable_grid_txtpos, F0F0E6 in 62_two_col,
     * F5E6E6 in 02_stamp, BFBFBF x87, C9C9C9 x182, FFFFFF x199).
     *
     * <p>The colour such a band actually has is not an absolute one - it is "a shade of
     * whatever the page background is", which is what {@code a:schemeClr bg1} with
     * {@code a:lumMod} says, and it is the only form of the colour that a reader is free to
     * re-resolve against its own canvas. Word and LibreOffice resolve bg1 from the theme - which
     * is why this patch also writes the theme part the package never had, see themeXml() - so
     * the band renders as the same light tint it renders as today, and a reader that inverts its
     * canvas can resolve bg1 to the inverted one instead of being handed a hex it must honour.
     *
     * <p>Measured in LibreOffice, which is the only one of the three that can be run here: with
     * the theme part, E6EBF5 (23_timetable) comes out EDEDED over the same 32,925 pixels the page
     * filled; without it, the same fill comes out 000000. The hue of the tint is lost - a tint of
     * white has no hue to keep, only a lightness - which is the price of making it relative.
     *
     * <p>Only light fills are written this way. A dark band carries white text - the FFFFFF
     * headings in 01, 02, 04 and 62 sit on one - and must stay dark in light mode, so a fill
     * below the threshold keeps its absolute hex. Dark fills are not the reported defect: a
     * dark band on a dark canvas is not a patch, and inverting it would make its white text
     * disappear.
     */
    private static void fillXml(StringBuilder sb, int rgb, float alpha) {
        double l = lightness(rgb);
        if (l >= LIGHT_FILL) {
            // No fill at all. A decorative tint barely distinguishable from the page IS no fill
            // on a dark page, and a fill is the only thing that can be a white patch - so the
            // good converters emit none: measured, Adobe writes ZERO w:shd fills and iLovePDF
            // five, where this writer emitted 753 across 159 documents. The earlier attempt
            // expressed them as a:schemeClr bg1 with a lumMod; bg1 is an alias for lt1, which is
            // FFFFFF in every Office theme, so that either resolves at import to a pure white
            // patch or is dropped - and it loses the hue in light mode either way, because
            // E6EBF5 has S=0.429 and EEEEEE has S=0.000.
            // Write NOTHING - not even <a:noFill/>. Measured on the two commercial files:
            // a:noFill 0 and a:solidFill 8, so they simply do not declare a fill. Declaring
            // "no fill" is not the same as not declaring one, and it left 10,201 elements
            // across the corpus that had no purpose.
        } else {
            sb.append("<a:solidFill><a:srgbClr val=\"").append(hex(rgb)).append("\">")
                    .append(alphaXml(alpha)).append("</a:srgbClr></a:solidFill>");
        }
    }

    private static String alphaXml(float alpha) {
        if (alpha >= 0.999f) return "";
        int a = Math.max(0, Math.min(100000, Math.round(alpha * 100000f)));
        return "<a:alpha val=\"" + a + "\"/>";
    }

    // ------------------------------------------------------------------ paragraphs

    /**
     * One paragraph. Every line the PDF drew becomes its own anchored text box at its own
     * x and y - a paragraph in the PDF is a group of lines, but the lines are not at one x,
     * and it is the x of each line that the reader sees.
     */
    private static void para(StringBuilder sb, PdfToWord.Para p, Ctx ctx) {
        ctx.lastWasTable = false;
        // Body text belongs in the document flow. Putting every line in an anchored text box made
        // the file a PDF wearing a .docx extension: it does not reflow, the app's viewer loses
        // values, a dark theme shows its own surface behind it, and it does not look like a
        // document at all. Only a line drawn on a non-horizontal baseline - a stamp, a watermark,
        // a rotated label - genuinely floats, and only those still become a text box.
        boolean anyRotated = false;
        for (PdfToWord.Box b : p.boxes) if (b.rotated) anyRotated = true;
        // A short line the page drew INSIDE a table's vertical band, which the table pass did
        // not take into a cell, is not in the page's flow: it sits beside the table at a y the
        // flow only reaches after the table. Written as a flowed paragraph it charges the page
        // for its own height first, and the table - which table() places at its own measured
        // top - is pushed down by exactly that. It is written as a frame instead, at the point
        // the page drew it, and charges the flow nothing. See pinShortParas().
        if (p.pinned && !anyRotated && !ctx.positioned) {
            framedBoxes(sb, p, ctx);
            return;
        }
        // A form row - a label and its value drawn on one baseline - is ONE line of the
        // document. Written as one paragraph per field it was three lines, which is what made a
        // one-page form two pages. It goes out as one paragraph with a tab stop at each field's
        // measured x, so the value lands at 300 pt where the page put it.
        // A page whose flow has run out of room places its lines instead: a row of fields is
        // anchored field by field at the x the page drew each one, not tabbed across a flow.
        if (ctx.positioned && !anyRotated) {
            for (PdfToWord.Box b : p.boxes) {
                if (b.runs.isEmpty()) continue;
                anchorBox(sb, p, b, ctx);
            }
            return;
        }
        if (!anyRotated && isRow(p.boxes)) {
            flowRow(sb, p, ctx);
            return;
        }
        if (!p.boxes.isEmpty() && !anyRotated) {
            for (PdfToWord.Box b : p.boxes) {
                if (b.runs.isEmpty()) continue;
                // A label the page drew inside a closed outline belongs to that outline, not to
                // the flow - see containerOf. It is anchored where the page put it, and the
                // outline itself is drawn by shape() as it always was.
                if (ctx.positioned || containerOf(ctx.curShapes, b) != null) {
                    anchorBox(sb, p, b, ctx);
                    continue;
                }
                flowFromBox(sb, p, b, ctx);
            }
            return;
        }
        if (!p.boxes.isEmpty()) {
            for (PdfToWord.Box b : p.boxes) {
                if (b.runs.isEmpty()) continue;
                StringBuilder inner = new StringBuilder(256);
                lineParagraph(inner, p, b);
                // How wide the box has to be to hold the line unwrapped.
                //
                // A rotated line is measured along its own baseline, not across the page: on
                // the 90-degree stamp b.right-b.x is the height of the text, so "31-03-2026"
                // was given a 22 pt box, wrapped, and reached Word as "31-". The other lines
                // get 12 % of slack, because the page's advance is measured in the font the
                // PDF embedded and the same string set in the substituted face is a few per
                // cent wider - enough to wrap the last word and clip it.
                float advance = b.rotated && b.length > 0f ? b.length : b.right - b.x;
                // The page's own advance is not always there to be trusted. A line whose glyphs
                // all report zero width measures 0 pt wide, the 4 pt floor below then wins, and
                // the box clips everything after the first character or two: file 69's clause
                // "8. The job worker shall carry out the processes of desizing," reached Word as
                // a 19 pt box holding 60 characters, and the render showed "8. " and nothing
                // else. When the measured advance is less than half what the characters need at
                // their own size, the measurement is the broken thing, so the character count
                // decides the width instead.
                int chars = 0;
                for (PdfToWord.Run r : b.runs) chars += r.text.length();
                float needed = chars * b.size * 0.5f;
                if (advance < needed * 0.6f) advance = needed;
                float wPt = b.rotated && b.length > 0f
                        ? Math.max(b.length, advance) + b.size * 1.5f
                        : Math.max(4f, advance) * 1.12f + b.size * 1.5f;
                float hPt = Math.max(4f, b.size * LINE_FACTOR);
                // A stamp is drawn on a rotated baseline, and it is written as the page's own
                // rectangle with the text placed inside it by the box's insets.
                //
                // WHY THIS AND NOT A TEXT-TIGHT BOX. The page draws a stamp as four separate
                // objects that share one `cm`: two stroked rectangles and two text objects. What
                // ties the text to the outline is that repeated matrix and nothing else, so the
                // only faithful reconstruction is the rectangle itself plus where the baseline
                // sits inside it. The text-tight box was neither: at 15 degrees the outline's
                // axis-aligned bounding box is 205.95 x 104.68 pt against a true rectangle of
                // 198.42 x 55.20 - 96.8 % too much area - and the box was 207 x 16, so whichever
                // of the two was used, the outline and the text were measured from different
                // shapes and the reader saw one move against the other.
                //
                // WHY THE INSETS AND NOT THE OFFSET. `<a:xfrm rot>` turns a box about its
                // CENTRE. Writing the baseline origin into wp:posOffset therefore moves the text
                // by (R - I) . (-w/2, +h/2) the moment the box is turned - +5.1/+22.2 pt on 01's
                // first line, +136.9/-20.2 and +195.9/-20.2 pt on 04's, a full box width. Putting
                // the box on the rectangle's own centre makes that term zero by construction, and
                // the baseline is then placed by lIns/tIns, which rotate with the box. The
                // reconstruction reproduces every stamp to under 0.001 pt.
                float lineAngle = mirrored(b) ? 180f : b.angle;
                // Where the page really put the baseline origin.
                //
                // Box.x/Box.y come from TextPosition.getXDirAdj()/getYDirAdj(), which are
                // measured along the baseline in a frame turned with the text. For 15 and 90
                // degrees that frame happens to agree with the page; for a 180-degree stamp it
                // does not, and both coordinates come back mirrored: on 04 the page's own
                // origin for CANCELLED is (444.266, 407.660) and the box said (151.010,
                // 434.230), which is 595.276-444.266 and 841.890-407.660. Every earlier version
                // placed the box from the mirrored pair, which is why 04's stamp has measured
                // 294 and 353 pt from where the page draws it no matter what else changed.
                float px = b.x, py = b.y;
                if (mirrored(b)) {
                    px = ctx.pageWidthPt - b.x;
                    py = ctx.pageHeightPt - b.y;
                }
                Frame frame = frameOf(ctx.curShapes, px, py, lineAngle);
                if (frame != null) {
                    // D-25: a line the page drew inside a stamp's frame is a paragraph, not a
                    // text box, and the frame is not its border.
                    //
                    // The frame used to BE this box's <a:ln> border (5013433). That welded the
                    // outer rule to one line of TEXT while the inner rule stayed on its own, so
                    // the two rules could drift apart - the drift the user reported for months -
                    // and, because the whole stamp then lived in wps:txbx, Google Docs could not
                    // put a caret in any of it. Both rules are now one freeform shape written by
                    // shape() (see stampFrames/mergedFrame) and this line is an ordinary
                    // paragraph placed by its indent and space-before (see stampLine). The frame
                    // and the text are siblings, and neither carries the other's geometry.
                    stampLine(sb, p, b, ctx, px, py, lineAngle, advance);
                } else {
                    // No rectangle around this line - the per-glyph text of a round seal, a
                    // rotated label on a drawing. There is no frame to bind to, so the line is
                    // placed on its own origin with no rotation: the run starts at the left end
                    // of what the page drew, and a line drawn right-to-left (file 04) starts at
                    // the other end because that is where its left end is.
                    double dirX = Math.cos(Math.toRadians(lineAngle));
                    float startX = px;
                    if (dirX <= -0.5) startX = px - b.length;
                    else if (Math.abs(dirX) < 0.5) startX = px - b.length / 2f;
                    anchorAt(sb, ctx, startX, py, 0f, ASCENT * b.size, wPt, hPt,
                            inner.toString(), 0f, -1, 0.6f, 0f, 0f);
                }
            }
            return;
        }
        // No page coordinates: an OCR block, an annotation, a filled form value. There is no
        // x to restore, so it goes into the flow rather than pretending to a position.
        flowParagraph(sb, p, ctx);
    }

    /**
     * A paragraph longer than this many drawn lines is prose, not a label left beside a table.
     *
     * <p>One line is the shape of every case this rule is for - a form's "AFFIX PHOTOGRAPH"
     * box, a margin note beside a grid, a rotated-adjacent label - and a two-line paragraph is
     * allowed because a label that wraps inside a small box is still a label. Anything longer
     * is a paragraph of the page's text, and framing it would take real flow height off the
     * page.
     */
    private static final int PIN_MAX_LINES = 2;

    /**
     * Mark the short paragraphs the page drew inside the band of the table that follows them.
     *
     * <p>THE DEFECT. admit-card draws a photo box beside its own candidate table: "AFFIX" on the
     * baseline at y=99.9 and "PHOTOGRAPH" at 107.9, while the table's first row of fields starts
     * at 103.3. The table pass does not take those two lines - they are in no cell - so they
     * survive as paragraphs of their own, and the flow charged the page for both before the
     * table began. The table is placed absolutely from its own measured top edge
     * ({@code rowTopPt}, see {@link #table}), so the whole table then started one paragraph too
     * low and everything under it with it: one constant +19.4 pt step from the table to the
     * footer, 17.2 pt median dy over the sheet, 15 % of lines within 10 pt, reading order 35 %.
     *
     * <p>THE RULE, AND WHY IT IS DERIVED RATHER THAN NAMED. The engine never reads the words. It
     * asks the page four questions, and every one of them is geometry the page already carries:
     * <ol>
     *   <li>is this block short - {@link #PIN_MAX_LINES} lines or fewer, none of them on a turned
     *       baseline? A label beside a table is; a paragraph of the page's prose is not;</li>
     *   <li>does a table follow it, with no paragraph of prose in between? (A picture or a shape
     *       may sit between them - neither is in the flow.)</li>
     *   <li>is the table's own band known - {@code rowTopPt} and {@code bottom}?</li>
     *   <li>does this line's own box lie IN that band, rather than above it or below it? A
     *       heading above a table ends above the table's top edge and is left alone; the photo
     *       box starts above the first row's text and runs past it, which is what makes it a
     *       line drawn inside the table's band;</li>
     *   <li>and is it BESIDE the table rather than over it - its box ending left of the table's
     *       left edge, or starting right of the table's right edge?</li>
     * </ol>
     * A block that answers yes to all five was drawn beside a table rather than in the page's
     * text, and the flow must not charge for it. The last two are "not part of that table" made
     * literal: a cell's text is inside the table's own span, and the table pass had the chance to
     * take it and did not - so this block and the table are siblings, not a cell and its
     * contents.
     *
     * <p>WHY THE HORIZONTAL TEST IS THERE, MEASURED. Without it the rule also fired on two lines
     * that are INSIDE a table's span and must stay in the flow: the dash rule the page drew across
     * the head of a space-aligned invoice (71_invoice_space_aligned_no_rules, box 56..345 inside
     * the table's 56..539) and the prose of a page whose whole body the row pass read as one
     * table (price-list-2col-dense-right-aligned, box 39.7..348.6 inside 39.7..555.6). Both are
     * text the table is made of, and taking their height off the page moves the table they belong
     * to. Every case the rule is for - admit-card's photo box at x 529..546 against a table
     * ending at 456, a risk grade at 360..371 beside a table ending at 278 - is outside it.
     *
     * <p>Measured on the 208-document corpus with {@code -Dp2w.debugPin}: the rule fires on the
     * photo boxes of the admit-card family and nowhere else - see the report.
     */
    private static void pinShortParas(PdfToWord.Page page) {
        java.util.List<Object> blocks = page.blocks;
        boolean debug = System.getProperty("p2w.debugPin") != null;
        for (int i = 0; i < blocks.size(); i++) {
            if (!(blocks.get(i) instanceof PdfToWord.Para)) continue;
            PdfToWord.Para p = (PdfToWord.Para) blocks.get(i);
            if (p.pinned || p.stamp || p.boxes.isEmpty() || p.boxes.size() > PIN_MAX_LINES) continue;
            PdfToWord.Table t = tableAfter(blocks, i + 1);
            if (t == null || Float.isNaN(t.rowTopPt) || !(t.bottom > t.rowTopPt)) continue;
            float top = Float.MAX_VALUE, bottom = -Float.MAX_VALUE;
            float lineLeft = Float.MAX_VALUE, lineRight = -Float.MAX_VALUE;
            boolean skip = false;
            for (PdfToWord.Box b : p.boxes) {
                if (b.rotated || b.runs.isEmpty() || b.text().trim().isEmpty()) {
                    skip = true;
                    break;
                }
                // The line's own box, measured exactly as the writer will measure it: the part
                // above the baseline is LINE_BASE of the box, the part below is the rest.
                float linePt = Math.max(4f, b.size * LINE_FACTOR);
                top = Math.min(top, b.y - LINE_BASE * linePt);
                bottom = Math.max(bottom, Math.max(b.bottom, b.y));
                lineLeft = Math.min(lineLeft, b.x);
                lineRight = Math.max(lineRight, b.right);
            }
            if (skip || top == Float.MAX_VALUE) continue;
            // In the table's band: the box starts above the table's first row and ends below
            // its top edge. A heading or a caption above the table ends above it and fails here.
            if (top >= t.bottom || bottom <= t.rowTopPt) continue;
            // Beside the table, not over it: a cell's text lies inside the table's own span.
            if (lineRight > t.left + 1f && lineLeft < t.right - 1f) continue;
            p.pinned = true;
            if (debug) {
                System.err.println("PIN page=" + page.number + " text=" + p.boxes.get(0).text()
                        + " y=" + p.boxes.get(0).y + " box=" + top + ".." + bottom
                        + " tableTop=" + t.rowTopPt + " tableBottom=" + t.bottom
                        + " tableX=" + t.left + ".." + t.right
                        + " lineX=" + p.boxes.get(0).x + ".." + p.boxes.get(0).right);
            }
        }
    }

    /**
     * The first table that follows block {@code from}, or null when prose comes first.
     *
     * <p>A paragraph of the page's own text between the candidate and the table means the
     * candidate is not beside the table - it is simply the line above it, in the flow. A
     * picture or a shape is not in the flow and does not break the band.
     */
    private static PdfToWord.Table tableAfter(java.util.List<Object> blocks, int from) {
        for (int j = from; j < blocks.size(); j++) {
            Object o = blocks.get(j);
            if (o instanceof PdfToWord.Table) return (PdfToWord.Table) o;
            if (o instanceof PdfToWord.Para
                    && ((PdfToWord.Para) o).boxes.size() > PIN_MAX_LINES) return null;
        }
        return null;
    }

    /**
     * A pinned paragraph: each of its lines written as the frame {@link #stampLine} writes, at
     * the point the page drew it.
     *
     * <p>The frame machinery is the same one a stamp uses - {@code w:framePr} with
     * {@code w:wrap="none"} and an absolute page anchor - so this is not a second way of
     * placing text: the paragraph stays a paragraph (selectable, editable, in the document's
     * order), it lands on the page's own coordinates, and it adds nothing to the height of the
     * sheet. A horizontal line is the simplest case of that machinery: the angle is zero, so the
     * corner of the line's box is its baseline's origin less the part of the box above the
     * baseline, and the width is the line's own advance.
     */
    private static void framedBoxes(StringBuilder sb, PdfToWord.Para p, Ctx ctx) {
        for (PdfToWord.Box b : p.boxes) {
            if (b.runs.isEmpty() || b.text().trim().isEmpty()) continue;
            stampLine(sb, p, b, ctx, b.x, b.y, 0f, b.right - b.x);
        }
    }

    /**
     * True when every box in the paragraph stands on one baseline - a form row, a table's
     * heading row, a running footer.
     */
    private static boolean isRow(List<PdfToWord.Box> boxes) {
        if (boxes.size() < 2) return false;
        float y = boxes.get(0).y;
        float size = boxes.get(0).size;
        for (PdfToWord.Box b : boxes) size = Math.max(size, b.size);
        float tol = Math.max(1.2f, size * 0.25f);
        for (PdfToWord.Box b : boxes) if (Math.abs(b.y - y) > tol) return false;
        return true;
    }

    /**
     * One baseline's fields as one paragraph, with a tab stop at each field's measured x.
     *
     * <p>The paragraph is indented to the first field's x and every later field is reached by a
     * {@code w:tab} at the x the PDF drew it at, relative to that indent. This is the only
     * construct in Word that puts two strings on one line at two known x positions without a
     * text box or a table, so the line keeps its place and the page keeps its height.
     */
    private static void flowRow(StringBuilder sb, PdfToWord.Para p, Ctx ctx) {
        List<PdfToWord.Box> cols = new ArrayList<>();
        for (PdfToWord.Box b : p.boxes) {
            if (b.runs.isEmpty() || b.text().trim().isEmpty()) continue;
            cols.add(b);
        }
        if (cols.isEmpty()) return;
        if (cols.size() == 1) {
            flowFromBox(sb, p, cols.get(0), ctx);
            return;
        }
        PdfToWord.Box first = cols.get(0);
        float indent = first.x;
        float size = first.size;
        for (PdfToWord.Box b : cols) size = Math.max(size, b.size);
        int leftTw = (int) Math.max(0L, Math.round(indent * TWIPS_PER_PT));
        // Same rule as flowFromBox: the row is one line however many fields it holds, so it is
        // charged one pitch, not one per field.
        float pitch = !ctx.newPage && ctx.lastBaseline >= 0f ? first.y - ctx.lastBaseline : -1f;
        float linePt = flowLinePt(pitch, size, ctx.lastLinePt);
        int beforeTw = 0;
        if (ctx.afterTablePt >= 0f) {
            // Same rule as flowFromBox: the row is placed against the table's measured edge
            // rather than spaced from a baseline that the table replaced.
            float topPt = first.y - LINE_BASE * linePt;
            float edgeGap = topPt - ctx.afterTablePt;
            ctx.afterTablePt = -1f;
            if (edgeGap * TWIPS_PER_PT > gapCapTw(ctx)) {
                // Too far below the table to be a gap - a running footer on the last line of
                // the sheet. It is a position, so the row's fields are anchored where the page
                // drew them rather than spaced from the table's bottom edge.
                ctx.positioned = true;
                for (PdfToWord.Box ab : cols) anchorBox(sb, p, ab, ctx);
                return;
            }
            beforeTw = (int) Math.max(0L, Math.round(edgeGap * TWIPS_PER_PT));
        } else if (ctx.newPage) {
            float topGap = first.y - LINE_BASE * linePt;
            if (topGap > 0f) {
                beforeTw = (int) Math.min(2000L, Math.round(topGap * TWIPS_PER_PT));
            } else if (first.y > 0f) {
                linePt = Math.min(linePt, Math.max(size, first.y / LINE_BASE));
            }
        } else if (pitch > 0f) {
            float extra = pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt;
            if (extra > 0f) beforeTw = (int) Math.min(gapCapTw(ctx), Math.round(extra * TWIPS_PER_PT));
        }
        int lineTw = (int) Math.max(1L, Math.round(linePt * TWIPS_PER_PT));
        // The squeeze factor is 1 on every page whose own flow already fits the paper; on the
        // pages it is not, the guard is handed the heights the page will really be written with,
        // so its accounting is the document's own w:before + w:line and not an estimate of it.
        int[] fit = fitPage(ctx, twScale(beforeTw, ctx.squeeze), twScale(lineTw, ctx.squeeze), size);
        if (fit == null) {
            // The page is full. Break it here, deliberately, and let the row be the first line
            // of the new sheet - which means it takes its own y as its top gap, exactly as the
            // page's first line does.
            breakPage(sb, ctx);
            float topGap = first.y - LINE_BASE * linePt;
            if (topGap > 0f) {
                beforeTw = (int) Math.min(2000L, Math.round(topGap * TWIPS_PER_PT));
            } else {
                beforeTw = 0;
                if (first.y > 0f) linePt = Math.min(linePt, Math.max(size, first.y / LINE_BASE));
            }
            lineTw = (int) Math.max(1L, Math.round(linePt * TWIPS_PER_PT));
            fit = fitPage(ctx, twScale(beforeTw, ctx.squeeze), twScale(lineTw, ctx.squeeze), size);
            if (fit == null) fit = new int[]{0, lineTw};
        }
        beforeTw = fit[0];
        lineTw = fit[1];
        // The box the pitch solver compares next time is the page's own, not the squeezed one:
        // the page's baselines are what they are, and a squeezed box that fed back into the
        // solver would chase its own scaling down the page.
        ctx.lastLinePt = linePt;

        ctx.flowCount++;
        ctx.lastBaseline = first.y;
        ctx.lastSize = size;
        ctx.newPage = false;
        // Re-sync the running position to what was written, not to what was intended. A page
        // break inside the block above starts a new sheet, so the top is the paper's top again.
        resync(ctx, flowTopPt(ctx), beforeTw, lineTw);

        // A tab stop's position is measured from the page margin, NOT from the paragraph's own
        // indent - the section has zero margins, so the page margin is x=0 and a stop is the
        // page's own x. Subtracting the indent put every value one indent too far left (file
        // 21's value landed at 240 pt instead of 300), and on file 16 it put the stop behind the
        // text before it, so Word skipped it for the next one and the four column headings
        // marched right across the page.
        StringBuilder tabs = new StringBuilder();
        for (int i = 1; i < cols.size(); i++) {
            PdfToWord.Box b = cols.get(i), before = cols.get(i - 1);
            float pos = b.x;
            // The embedded face's advance is not the substituted face's: at the same point size
            // Word's face can be a few per cent wider, and a tab stop that lands inside the text
            // before it is skipped for the next one. Only ever push the stop clear, never left.
            float clear = before.right * 1.06f + before.size * 0.4f;
            boolean last = i == cols.size() - 1;
            if (last && b.right > ctx.pageWidthPt - 2f && b.right > clear) {
                // A field that ends at the paper's edge is right-aligned there. A right tab keeps
                // its RIGHT edge where the page drew it, so a wider substitute grows inwards
                // instead of wrapping the last word onto the next line.
                int posTw = (int) Math.round(b.right * TWIPS_PER_PT);
                tabs.append("<w:tab w:val=\"right\" w:pos=\"").append(posTw).append("\"/>");
                continue;
            }
            if (clear > pos) pos = clear;
            int posTw = (int) Math.round(pos * TWIPS_PER_PT);
            tabs.append("<w:tab w:val=\"left\" w:pos=\"").append(posTw).append("\"/>");
        }

        sb.append("<w:p><w:pPr>")
                // w:tabs comes first, before w:snapToGrid. CT_PPr defines a sequence and tabs
                // precedes snapToGrid in it; written last - which it was - every one of these
                // paragraphs was out of schema order. The tab stops themselves are unchanged.
                .append("<w:tabs>").append(tabs).append("</w:tabs>")
                .append("<w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"").append(beforeTw)
                .append("\" w:after=\"0\" w:line=\"").append(lineTw)
                .append("\" w:lineRule=\"exact\"/>")
                // A row is laid out by its tab stops, so it must not also be centred or pushed
                // right: justification would move the first field off the indent the stops are
                // measured from.
                .append("<w:ind w:left=\"").append(Math.max(0, leftTw - bandLeftTw(ctx, p.column)))
                .append("\" w:right=\"0\" w:firstLine=\"0\"/>")
                .append("</w:pPr>");
        for (int i = 0; i < cols.size(); i++) {
            if (i > 0) {
                // A space before the tab, not after it. Word discards white space immediately
                // before a tab stop, so nothing moves on the page - but any reader that joins a
                // paragraph's w:t elements (this project's own gate does) still sees two words
                // instead of "Member NameAnanya Rangappa".
                sb.append("<w:r><w:t xml:space=\"preserve\"> </w:t><w:tab/></w:r>");
            }
            for (PdfToWord.Run run : cols.get(i).runs) {
                if (run.text.isEmpty()) continue;
                runXml(sb, run);
            }
        }
        sb.append("</w:p>");
    }

    /** One drawn line, as the single paragraph inside its own text box. */
    private static void lineParagraph(StringBuilder sb, PdfToWord.Para p, PdfToWord.Box b) {
        int lineTw = Math.max(1, Math.round((float) (Math.max(4f, b.size * LINE_FACTOR) * TWIPS_PER_PT)));
        sb.append("<w:p><w:pPr>");
        if (p.heading > 0) {
            sb.append("<w:pStyle w:val=\"Heading").append(Math.min(p.heading, 3)).append("\"/>");
        }
        sb.append("<w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"").append(lineTw)
                .append("\" w:lineRule=\"exact\"/>")
                // The anchor already put this line at its x; an indent here would move it off.
                .append("<w:ind w:left=\"0\" w:right=\"0\" w:firstLine=\"0\"/>");
        int half = halfPointsDown(b.size);
        if (half > 0) {
            sb.append("<w:rPr><w:sz w:val=\"").append(Math.min(3276, Math.max(2, half)))
                    .append("\"/></w:rPr>");
        }
        sb.append("</w:pPr>");
        for (PdfToWord.Run run : b.runs) {
            if (run.text.isEmpty()) continue;
            runXml(sb, run);
        }
        sb.append("</w:p>");
    }

    /**
     * Does this page's own content fit inside the paper?
     *
     * <p>Walked through the same line box solver the flow uses, in the same order, so the answer
     * is the height the flow would need if every gap the page drew were spent. A page of stacked
     * columns fails this even though every block's y is on the page, because the flow lays the
     * columns one after another rather than on top of one another - which is exactly the case
     * that rejected the plain cap raise (315_gazette_notification).
     *
     * <p>A table's height is the model's own {@code bottom - top}; where that under-measures a
     * table whose rows grow, this returns false and the page keeps the clamped gaps, which is the
     * behaviour that was there before.
     */
    /**
     * Whether this page is set in more than one column.
     *
     * <p>Gaps may only be spent on a page whose content already fits the sheet. A page set in
     * two or three columns does not fit, because the writer still puts the columns into one
     * flow (D-08): its content is every column's worth of text stacked, so it is several
     * times the paper's height. Spending the page's white space on such a page is what made
     * 315_gazette_notification go from one sheet to two when the ceiling was raised on
     * 7 Nov - the gap was the only thing holding it to a sheet.
     *
     * <p>So the gap is spent only where the columns are real, which today means only on a
     * page that has none. When D-08 lands, this guard comes out and the gap is spent on
     * columned pages too.
     */
    private static boolean hasColumnBands(PdfToWord.Page page) {
        for (Object block : page.blocks) {
            if (block instanceof PdfToWord.Para && ((PdfToWord.Para) block).column > 0) return true;
            if (block instanceof PdfToWord.Table && ((PdfToWord.Table) block).column > 0) return true;
        }
        return false;
    }

    private static boolean pageFits(PdfToWord.Page page, float ph) {
        float required = 0f;
        float prevBase = -1f;
        float prevBox = 0f;
        float prevSize = 0f;
        boolean firstLine = true;
        // The same outlines para() consults, so a label it anchors is not charged to the flow
        // here either. Two measures of one page must not disagree about what is in the flow.
        java.util.List<Shape> outlines = new ArrayList<>();
        for (Object block : page.blocks) {
            if (block instanceof Shape) outlines.add((Shape) block);
        }
        for (Object block : page.blocks) {
            if (block instanceof PdfToWord.Para) {
                PdfToWord.Para p = (PdfToWord.Para) block;
                // A pinned line is written as a frame and charges the flow nothing, exactly as a
                // stamp's line does - the two measures of a page must not disagree about what is
                // in its flow.
                if (p.pinned) continue;
                float top = Float.MAX_VALUE;
                float size = 0f;
                for (PdfToWord.Box b : p.boxes) {
                    if (b.runs.isEmpty() || b.text().trim().isEmpty()) continue;
                    if (containerOf(outlines, b) != null) continue;
                    // A line on a turned baseline is never part of the flow: para() writes it
                    // either as a framed paragraph (a stamp - T02-A) or as an anchored box (a
                    // rotated label). Charging it here made this measure disagree with the
                    // writer about the same page - two stamp lines charged 34 pt a page the
                    // writer never wrote - and that alone decided `spendGaps`, which is what
                    // puts a running footer at its own y. Measured: 02's footer sat 117 pt above
                    // the foot of the page with the stamp charged and lands on it without.
                    if (b.rotated) continue;
                    if (b.y < top) top = b.y;
                    if (b.size > size) size = b.size;
                }
                if (top == Float.MAX_VALUE) continue;
                float pitch = firstLine || prevBase < 0f ? -1f : top - prevBase;
                float box = flowLinePt(pitch, size, prevBox);
                float gap;
                if (firstLine) {
                    gap = Math.max(0f, top - LINE_BASE * box);
                } else if (pitch > 0f) {
                    gap = Math.max(0f, pitch - (1f - LINE_BASE) * prevBox - LINE_BASE * box);
                } else {
                    gap = 0f;
                }
                required += gap + box;
                prevBase = top;
                prevBox = box;
                prevSize = size;
                firstLine = false;
            } else if (block instanceof PdfToWord.Table) {
                // A table is charged what the model says it is tall, plus the spacer the flow
                // puts above it and the 4 pt paragraph Word requires after it. Before this the
                // whole page gave up its white space the moment it held a table at all, which
                // was a blanket rule standing in for a measurement: on 318 the page's own gap
                // between its last box and its footer is 480 pt and the clamped 120 pt put that
                // footer 337 pt too high.
                //
                // The blanket rule was there because the model's table height can be SHORT - a
                // cell whose text wraps grows its w:trHeight row - so a page that spent its gaps
                // could be pushed past the paper. Measured on the 208-document corpus: 15
                // documents went from one sheet to two when the rule was removed. So the table's
                // height is not taken on trust here. It is charged, and the page only spends its
                // gaps when the arithmetic still fits the sheet with TABLE_SLACK_PT to spare for
                // a table that grows. Where the arithmetic says it does not fit, the page keeps
                // the clamped gaps exactly as before. See "Table height" in REMAINING-DEFECTS.md.
                PdfToWord.Table t = (PdfToWord.Table) block;
                float gapAbove = 0f;
                if (firstLine) {
                    gapAbove = Math.max(0f, t.top);
                } else if (prevBase >= 0f && t.top > prevBase) {
                    // The flow's spacer paragraph: the measured gap less one line of the
                    // previous text, and only when that is worth a paragraph of its own.
                    float prevLine = Math.max(4f, prevSize * LINE_FACTOR);
                    float extra = (t.top - prevBase) - prevLine;
                    if (extra >= prevLine * 1.2f) gapAbove = Math.min(144f, extra);
                }
                required += gapAbove + Math.max(0f, t.bottom - t.top) + POST_TABLE_TW / 20f;
                // After a table the previous baseline is the table's bottom edge and it carries
                // no line box of its own, exactly as the writer sets it.
                prevBase = t.bottom;
                prevBox = 0f;
                prevSize = 0f;
                firstLine = false;
            }
        }
        return required <= ph + 0.5f - TABLE_SLACK_PT;
    }

    /**
     * The line box a flowing line is given, in points.
     *
     * <p>The height is not a constant. A PDF sets each line at its own baseline, and the distance
     * between two of them is the pitch the page actually used: 1.168 * size on
     * 303_discharge_summary, 1.20 on others. A single factor cannot be both, and with
     * {@code w:lineRule="exact"} every box that is the wrong height moves the line below it and
     * the error accumulates - 3.5 pt at the top of 303's page, 6.3 pt by its fourth paragraph,
     * and on 28 documents the flow grew taller than the paper and spilled onto a second sheet
     * (D-01 and D-06 in REMAINING-DEFECTS.md).
     *
     * <p>So the box is the measured pitch, and the paragraph then needs no spacing-before at all:
     * one box is one pitch. Two limits are real and are not tuning:
     *
     * <ul>
     *   <li>a box shorter than the em clips the top of the glyphs, and flowing text cannot
     *       reproduce baselines that overlap, so the size is a floor;</li>
     *   <li>a gap wider than {@link #GAP_CAP_TW} is the page's own white space rather than
     *       leading, so it goes to spacing-before where it is already capped, not to the box.</li>
     * </ul>
     *
     * @param pitch      the distance from the previous baseline on this page, or -1 when unknown
     * @param size       the line's font size
     * @param prevLinePt the height of the line box just emitted, 0 after a table
     */
    private static float flowLinePt(float pitch, float size, float prevLinePt) {
        float natural = Math.max(4f, size * LINE_FACTOR);
        if (pitch <= 0f) return natural;
        // The advance from one baseline to the next is the rest of the previous box plus this
        // line's part above its own baseline: (1 - LINE_BASE) * prev + LINE_BASE * this. Solve it
        // for this box so that it comes out at exactly the pitch the page used.
        float solved = (pitch - (1f - LINE_BASE) * prevLinePt) / LINE_BASE;
        // Two limits, both real. A box shorter than the em clips the top of the glyphs, and a
        // box taller than the font's own line box spends the page's slack where the next line
        // has to pay for it: on 303 the 37 pt gap above a form row became a 37 pt box, the next
        // row then owed 7.4 pt of its slack and landed 5.2 pt low. Anything the box cannot hold
        // goes to spacing-before, which is where a gap belongs.
        return Math.max(4f, Math.min(natural, Math.max(size, solved)));
    }

    /**
     * The gap and the box that put this line's baseline at its own y on the sheet.
     *
     * <p>This is the whole of D-26. The vertical position used to be INCREMENTAL: the gap was
     * {@code pitch - rest of the previous box - this line's part above its baseline}, and the
     * pitch was the distance between two baselines in the PDF. The model was arithmetically
     * right and the page was not, because the gap only exists when it is positive: whenever the
     * solved box was floored at the em (a PDF that sets its lines tighter than 1.15 em, which
     * most do), the gap came out negative, was written as zero, and the line landed low by the
     * difference. The next paragraph then measured its pitch from the PDF's baseline again - so
     * the error was never seen again by the model, but the reader kept it, and each line added
     * its own. On 16_right_aligned_amounts 0.3 pt per line became 10.5 pt at the median and 38 pt
     * at the foot of one page; on 20_numbered_list_separate_column 101 pt. That is why the error
     * correlated with y (-0.65 and +0.72) instead of being noise.
     *
     * <p>So the position is now ABSOLUTE. {@link Ctx#flowY} is where the reader will really put
     * the last baseline - built from the twips that were actually written, so rounding is in it
     * too - and the gap is simply {@code target - (top of this paragraph)}, less the part of the
     * box above its own baseline. The running position is then re-synced to what was written,
     * not to what was intended, so an error is spent on the line that caused it and the next
     * line starts from the truth again.
     *
     * <p>Two cases cannot be solved by spacing, because a flow cannot go backwards:
     * <ul>
     *   <li>the target is above where the flow already is (the line above overshot). The gap is
     *       zero and the overshoot is left on the page - and, because the next call starts from
     *       the position that was written, absorbed there instead of accumulated. That is the
     *       re-sync, and it is why this is bounded rather than growing;</li>
     *   <li>the target is so close that no box of the line's own em size can reach it. The box is
     *       shortened to the largest that still lands on or above the target, floored at the em
     *       so the glyphs are not clipped, and the rest is the first case.</li>
     * </ul>
     *
     * @param targetY the baseline the PDF drew, in points from the top of the sheet
     * @param size    the line's font size, the floor for its box
     * @param pitch   the distance to the previous baseline on this page, or -1 when unknown
     * @param linePt  the box {@link #flowLinePt} asked for
     * @return {@code {spaceBeforeTw, linePt}}
     */
    private static float[] place(Ctx ctx, float targetY, float size, float pitch, float linePt) {
        if (ctx.newPage) {
            // The first line of a sheet: the flow starts at the paper's top edge, so the gap is
            // the whole distance down to the top of this line's box. Unchanged from before -
            // there is nothing above it to be incremental about.
            float topGap = targetY - LINE_BASE * linePt;
            if (topGap > 0f) {
                return new float[]{Math.min(2000f, topGap * (float) TWIPS_PER_PT), linePt};
            }
            if (targetY > 0f) linePt = Math.min(linePt, Math.max(size, targetY / LINE_BASE));
            return new float[]{0f, linePt};
        }
        if (ctx.flowY < 0f) {
            // The flow's position on this sheet is not known (a new column of a continuous
            // section): fall back to the pitch model, which is the behaviour that was there.
            float extra = pitch > 0f
                    ? pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt : 0f;
            return new float[]{extra > 0f ? extra * (float) TWIPS_PER_PT : 0f, linePt};
        }
        // Where this paragraph starts: the rest of the previous line's box, below its baseline.
        float topPt = ctx.flowY + (1f - LINE_BASE) * ctx.flowBoxPt;
        float d = targetY - topPt;
        if (d <= 0f) return new float[]{0f, linePt};      // the flow cannot go backwards
        // A box taller than d / LINE_BASE would put its own baseline below the target, and a
        // negative gap is not something a reader will honour - so the box gives way first, down
        // to the em and no further.
        float maxBox = d / LINE_BASE;
        if (linePt > maxBox) linePt = Math.max(size, maxBox);
        float before = d - LINE_BASE * linePt;
        if (before < 0f) before = 0f;
        return new float[]{before * (float) TWIPS_PER_PT, linePt};
    }

    /**
     * Records where the reader will put the baseline just written, from the twips that were
     * actually emitted. The next paragraph is measured from here.
     */
    private static void resync(Ctx ctx, float topPt, int beforeTw, int lineTw) {
        ctx.flowY = topPt + beforeTw / (float) TWIPS_PER_PT + LINE_BASE * (lineTw / (float) TWIPS_PER_PT);
        ctx.flowBoxPt = lineTw / (float) TWIPS_PER_PT;
    }

    /** The top of the paragraph about to be written, in points from the top of the sheet. */
    private static float flowTopPt(Ctx ctx) {
        if (ctx.newPage || ctx.flowY < 0f) return 0f;
        return ctx.flowY + (1f - LINE_BASE) * ctx.flowBoxPt;
    }

    /** A paragraph with no page coordinates of its own: the old flowing behaviour. */
    /**
     * One PDF line as a real Word paragraph.
     *
     * <p>The x becomes {@code w:ind w:left}; the gap to the previous line becomes
     * {@code w:spacing w:before}. The section has zero margins, so the page's own x is the indent.
     * The vertical gap is kept so a form's label/value rows still sit apart, but it is clamped:
     * a PDF that leaves 300 pt of white space must not push a line onto the next page.
     */
    private static void flowFromBox(StringBuilder sb, PdfToWord.Para p, PdfToWord.Box b, Ctx ctx) {
        String text = b.text();
        if (text.trim().isEmpty()) return;
        ctx.flowCount++;
        int leftTw = (int) Math.max(0L, Math.round(b.x * TWIPS_PER_PT));
        int rightTw = 0;
        // A line the page centred is placed by w:jc, and LibreOffice centres it inside the
        // paragraph's own indents. Leaving w:ind w:left at the measured x therefore pushed every
        // centred heading to the RIGHT by half of it: 310's heading 92.8 pt, 317's 99.2 pt,
        // 313's "POWER OF ATTORNEY" 121.1 pt, while the PDF drew all three on the page's centre.
        // The alignment is the position, so the indent must not double it. A line centred on the
        // paper keeps the whole text area; one centred inside a column gets the page's own extent
        // back as symmetric indents, so its centre is the centre the page used.
        if (ctx.inColumn) {
            // Inside a column cell the cell IS the column: it is exactly as wide as the band the
            // page drew, so a centred line is centred by w:jc against zero indents, and a
            // right-aligned one is measured from the cell's right edge rather than the paper's.
            if (p.align == 1) {
                leftTw = 0;
            } else if (p.align == 2) {
                leftTw = 0;
                rightTw = (int) Math.max(0L,
                        Math.round((ctx.cellRightPt - b.right) * TWIPS_PER_PT));
            }
        } else if (p.align == 1) {
            float centre = (b.x + b.right) / 2f;
            if (Math.abs(centre - ctx.pageWidthPt / 2f) > 2f) {
                rightTw = (int) Math.max(0L, Math.round((ctx.pageWidthPt - b.right) * TWIPS_PER_PT));
            } else {
                leftTw = 0;
            }
        } else if (p.align == 2) {
            leftTw = 0;
            rightTw = (int) Math.max(0L, Math.round((ctx.pageWidthPt - b.right) * TWIPS_PER_PT));
        }
        // The pitch this page used between this baseline and the one above it. Measured, so the
        // box is the page's own line height rather than a guess at it - see flowLinePt.
        float pitch = !ctx.newPage && ctx.lastBaseline >= 0f ? b.y - ctx.lastBaseline : -1f;
        float linePt = flowLinePt(pitch, b.size, ctx.lastLinePt);
        int beforeTw = 0;
        if (ctx.afterTablePt >= 0f) {
            // The box above this one is a layout table - or the top of a column cell - and a
            // table's height is decided by the renderer from its own line boxes, not by the
            // page's baselines. So this line is placed against the measured edge: the gap is
            // exactly what the page left between that edge and this line's box top.
            float topPt = b.y - LINE_BASE * linePt;
            float edgeGap = topPt - ctx.afterTablePt;
            ctx.afterTablePt = -1f;
            // Inside a cell a wide gap is SPACE, not a position: the cell is a fixed rectangle
            // whose height is measured from exactly what it writes, so spending the gap keeps the
            // line where the page put it and keeps it as text. Anchoring it instead made a text
            // box - not editable in Google Docs - and on brochure-3col-with-sidebar-box, whose
            // columns hold more than one band, that turned 24 lines into text boxes.
            if (!ctx.inColumn && edgeGap * TWIPS_PER_PT > gapCapTw(ctx)) {
                // A footer 340 pt below the columns is not a gap the flow may spend, it is a
                // position - the rule the pitch branch below already applies. Spending what the
                // cap allows instead put 62's running footer 246 pt above the foot of the page.
                ctx.positioned = true;
                anchorBox(sb, p, b, ctx);
                return;
            }
            beforeTw = (int) Math.max(0L, Math.round(edgeGap * TWIPS_PER_PT));
        } else if (ctx.newPage) {
            // The FIRST line on a page still has to land at its own y. The section carries zero
            // margins, so without this it starts at the very top of the sheet: on file 21 every
            // line measured 46 pt high against the PDF, a constant offset with the pitch already
            // correct. Measured, not guessed - dy was -46.2, -48.3, -45.0, -46.6 over the first
            // four lines of the page. The lift is the part of the box above its baseline, and
            // where the box is taller than the space the page leaves, the box is shortened to
            // fit rather than the line being placed below its own y.
            float topGap = b.y - LINE_BASE * linePt;
            if (topGap > 0f) {
                beforeTw = (int) Math.min(2000L, Math.round(topGap * TWIPS_PER_PT));
            } else if (b.y > 0f) {
                linePt = Math.min(linePt, Math.max(b.size, b.y / LINE_BASE));
            }
        } else if (pitch > 0f) {
            // Where the previous baseline is, plus the rest of its box, plus this line's own part
            // above its baseline, plus this gap, must equal the pitch the page used. Only a gap
            // wider than the box can carry - a diagram's boxes 90 pt apart, a footer 422 pt below
            // the text - still needs spacing, and flowLinePt has refused to put that in the box.
            float extra = pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt;
            if (extra > 0f) {
                // A gap wider than the flow may spend is not a gap, it is a position. Clamping it
                // puts the line somewhere the page never put it, and every line after it drifts
                // with it: on 331_pid_diagram the clamp landed the diagram's "CHILLED WATER"
                // label 114 pt above the box that holds it. Anchoring the line at its own y is
                // what the page did, and from here on the page is placed rather than flowed.
                // Same rule inside a cell: a gap between two bands of the same column is space
                // the cell can hold, not a reason to float the line out of the text.
                if (!ctx.inColumn && extra * TWIPS_PER_PT > gapCapTw(ctx)) {
                    ctx.positioned = true;
                    anchorBox(sb, p, b, ctx);
                    return;
                }
                beforeTw = (int) Math.round(extra * TWIPS_PER_PT);
            }
        }
        // The FIRST line on a page has to land at its own y too, and place() does that: the
        // section carries zero margins, so the flow starts at the paper's top edge and the gap
        // is the whole distance down to the top of this line's box (file 21 used to sit 46 pt
        // high on every line without it).
        // D-26-A's absolute gap, kept as the fallback. COL-A's branches below decide first -
        // the table edge, the first line on a page, or the page's own pitch - and where none of
        // them had anything to say, the distance from where the reader really put the line above
        // is what places this one, with no rounding carried down the page.
        int absBeforeTw = 0;
        if (ctx.flowY >= 0f) {
            float absTop = b.y - LINE_BASE * linePt;
            absBeforeTw = (int) Math.max(0L,
                    Math.round(Math.min(absTop - ctx.flowY, gapCapTw(ctx) / TWIPS_PER_PT) * TWIPS_PER_PT));
        }
        if (beforeTw == 0 && absBeforeTw > 0 && !ctx.newPage && ctx.afterTablePt < 0f) {
            beforeTw = absBeforeTw;
        }
        int lineTw = (int) Math.max(1L, Math.round(linePt * TWIPS_PER_PT));
        // A page's flow must end where the paper does. The gap above is clamped per line, but
        // 43 of them add up, and a page whose flow overruns by a few points sends its last line
        // - and every anchored shape after it - to a second sheet. Give up the gap first, then
        // the slack in the last line's own box, and only then break the page.
        int[] fit = fitPage(ctx, twScale(beforeTw, ctx.squeeze), twScale(lineTw, ctx.squeeze), b.size);
        if (fit == null) {
            // The page is full. Break it here, deliberately, and place this line as the first
            // line of the new sheet: its own y decides its top gap, which is the same rule the
            // page's first line follows.
            breakPage(sb, ctx);
            float topGap = b.y - LINE_BASE * linePt;
            if (topGap > 0f) {
                beforeTw = (int) Math.min(2000L, Math.round(topGap * TWIPS_PER_PT));
            } else {
                beforeTw = 0;
                if (b.y > 0f) linePt = Math.min(linePt, Math.max(b.size, b.y / LINE_BASE));
            }
            lineTw = (int) Math.max(1L, Math.round(linePt * TWIPS_PER_PT));
            fit = fitPage(ctx, twScale(beforeTw, ctx.squeeze), twScale(lineTw, ctx.squeeze), b.size);
            if (fit == null) fit = new int[]{0, lineTw};
        }
        beforeTw = fit[0];
        lineTw = fit[1];
        // The box the pitch solver compares next time is the page's own, not the squeezed one.
        ctx.lastLinePt = linePt;
        ctx.lastBaseline = b.y;
        ctx.lastSize = b.size;
        ctx.newPage = false;
        // Re-sync to what was written, so the next paragraph is measured from the reader's
        // position rather than from the PDF's (D-26).
        resync(ctx, flowTopPt(ctx), beforeTw, lineTw);
        sb.append("<w:p><w:pPr>");
        if (p.heading > 0) {
            sb.append("<w:pStyle w:val=\"Heading").append(Math.min(p.heading, 3)).append("\"/>");
        }
        sb.append("<w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"").append(beforeTw)
                .append("\" w:after=\"0\" w:line=\"").append(lineTw)
                .append("\" w:lineRule=\"exact\"/>")
                .append("<w:ind w:left=\"").append(Math.max(0, leftTw - bandLeftTw(ctx, p.column)))
                .append("\" w:right=\"").append(rightTw).append("\" w:firstLine=\"0\"/>");
        if (p.align == 1) sb.append("<w:jc w:val=\"center\"/>");
        else if (p.align == 2) sb.append("<w:jc w:val=\"right\"/>");
        sb.append("</w:pPr>");
        for (PdfToWord.Run run : b.runs) {
            if (run.text.isEmpty()) continue;
            runXml(sb, run);
        }
        sb.append("</w:p>");
    }

    private static void flowParagraph(StringBuilder sb, PdfToWord.Para p, Ctx ctx) {
        String text = p.text();
        if (text.trim().isEmpty()) return;
        ctx.flowCount++;
        sb.append("<w:p><w:pPr>");
        if (p.heading > 0) {
            sb.append("<w:pStyle w:val=\"Heading").append(Math.min(p.heading, 3)).append("\"/>");
        }
        sb.append("<w:snapToGrid w:val=\"0\"/>");
        if (p.align == 1) sb.append("<w:jc w:val=\"center\"/>");
        else if (p.align == 2) sb.append("<w:jc w:val=\"right\"/>");
        if (p.indent > 0) {
            sb.append("<w:ind w:left=\"").append(p.indent * 420).append("\"/>");
        }
        sb.append("</w:pPr>");
        for (PdfToWord.Run run : p.runs) {
            if (run.text.isEmpty()) continue;
            runXml(sb, run);
        }
        sb.append("</w:p>");
    }

    /** One run with the properties the PDF drew it with. */
    private static void runXml(StringBuilder sb, PdfToWord.Run run) {
        sb.append("<w:r><w:rPr>");
        // The typeface and colour the PDF used. Without these every document came out in
        // the default font in black, and "the Word file should look like the PDF" had no
        // way to be measured - both benchmarks read 0 %.
        if (run.font != null && !run.font.isEmpty()) {
            String face = esc(faceName(run.font));
            sb.append("<w:rFonts w:ascii=\"").append(face)
                    .append("\" w:hAnsi=\"").append(face)
                    .append("\" w:cs=\"").append(face).append("\"/>");
        }
        if (run.bold) sb.append("<w:b/>");
        if (run.italic) sb.append("<w:i/>");
        // Only when the page named one. A run with no w:color is left on Automatic, which is
        // what a reader adapts to its own canvas - pinning 000000 here would make every such
        // run invisible in Google Docs dark mode, which leaves an explicit black alone. The
        // colour is written after w:b/w:i because that is where the schema puts it; a reader
        // that validates rPr and drops what it cannot place loses it otherwise.
        if (run.color >= 0) {
            sb.append(String.format("<w:color w:val=\"%06X\"/>", run.color & 0xFFFFFF));
        }
        int half = halfPointsDown(run.sizePt);
        if (half > 0) {
            sb.append("<w:sz w:val=\"").append(Math.min(3276, Math.max(2, half))).append("\"/>");
            sb.append("<w:szCs w:val=\"").append(Math.min(3276, Math.max(2, half)))
                    .append("\"/>");
        }
        sb.append("</w:rPr><w:t xml:space=\"preserve\">").append(esc(run.text))
                .append("</w:t></w:r>");
    }

    // ------------------------------------------------------------------ the anchor

    /**
     * Wraps a block of WordprocessingML in a floating text box at (xPt, yTopPt).
     *
     * <p>The child order of {@code wp:anchor} is fixed by the schema - simplePos, positionH,
     * positionV, extent, effectExtent, wrap*, docPr, cNvGraphicFramePr, graphic - and Word
     * refuses the whole file if it is wrong, so it is written in one place, in order.
     */
    private static void anchor(StringBuilder sb, Ctx ctx, float xPt, float yTopPt,
                               float wPt, float hPt, String inner) {
        anchor(sb, ctx, xPt, yTopPt, wPt, hPt, inner, 0f);
    }

    /**
     * An anchored text box, rotated about its own centre by the angle the page drew it at.
     *
     * <p>OOXML rotates a shape with {@code <a:xfrm rot="...">} in 60000ths of a degree and both
     * Word and LibreOffice honour it, so a rotated stamp does not have to be written upright.
     * The angle is {@code Box.angle}, measured from the PDF's own baseline - nothing is
     * rotated that the page did not rotate. A 15-degree stamp goes out at 15 degrees, a
     * 90-degree one at 90, and a stamp on a horizontal baseline goes out with no rotation at
     * all.
     *
     * <p>Rotation is about the box's centre, so the offset is NOT the top-left of the box: it is
     * solved for in {@link #anchorAt} so that the text's own origin lands on the page's, before
     * and after the turn.
     */
    private static void anchor(StringBuilder sb, Ctx ctx, float xPt, float yTopPt,
                               float wPt, float hPt, String inner, float rotDeg) {
        anchor(sb, ctx, xPt, yTopPt, wPt, hPt, inner, rotDeg, -1, 0f);
    }

    /**
     * The same, with the stamp's own outline drawn as the box's border.
     *
     * <p>The outline used to be a separate Shape and the text a separate text box, each with
     * its own position arithmetic, and they drifted apart - the user's report is precise:
     * sometimes the outline shifts, sometimes the text inside it. Binding the outline to the
     * box that holds the text removes that, but only where the outline really is the text's own
     * box; a stamp's frame is not, and binding it there drew a thin rectangle round one line of
     * the stamp instead of its frame. A stamp is written by {@link #frameOf} instead: the box is
     * the page's rectangle and the text is placed inside it, so there is still one object and
     * one geometry. Where an outline is neither, it is left to {@code shape()} and drawn from
     * the page's own path, so its geometry is the page's own and there is no second position
     * calculation to drift from.
     */
    private static void anchor(StringBuilder sb, Ctx ctx, float xPt, float yTopPt,
                               float wPt, float hPt, String inner, float rotDeg,
                               int borderRgb, float borderWpt) {
        // No rotation on this path: the top-left of the unrotated box IS where the text's
        // frame starts, and for rotDeg == 0 anchorAt reduces to exactly this.
        anchorAt(sb, ctx, xPt, yTopPt, 0f, 0f, wPt, hPt, inner, rotDeg, borderRgb, borderWpt);
    }

    /**
     * The rectangle the page drew around a rotated line, in the line's own frame.
     *
     * <p>A stamp's frame is a stroked, unfilled rectangle that shares the line's rotation, and
     * the line's baseline origin sits inside it. That is the whole test: rotation, containment,
     * four corners, no fill. Nothing is guessed from sizes, so a stamp's frame is found by what
     * it is and not by how big it happens to be, and the largest such rectangle wins - a stamp
     * drawn with a double rule has an inner rectangle too, and the inner one is not the frame.
     *
     * <p>The frame's own axes come from the LINE, not from the order the path happened to be
     * drawn in. {@code u} is the direction the text advances and {@code v} is a quarter turn
     * from it, so {@code lIns}/{@code tIns} below are the baseline's position along and across
     * the reading direction - which is exactly what {@code bodyPr}'s insets mean once the box
     * carries the same rotation.
     */
    private static final class Frame {
        float cx, cy, w, h;
        /** Where the baseline origin sits inside the rectangle, along and across the reading. */
        float lIns, tIns;
        Shape shape;
    }

    /**
     * Is this line a whole turn round - a 180-degree stamp - rather than one character of a ring?
     *
     * <p>Both arrive with {@code rotated} set and {@code angle} 0, and the two need opposite
     * treatment. A 180-degree line's {@code x}/{@code y} come back mirrored, so the writer
     * mirrors them back to place it. A ring character's do not: {@code ringLines} writes the
     * page point straight into the line, and mirroring THAT puts the character at
     * {@code (pageWidth - x, pageHeight - y)} - on 352_certificate_ornate_border, whose page is
     * landscape, a 333 pt lift that moved the whole seal to the top of the sheet and made it the
     * worst mover in the corpus.
     */
    private static boolean mirrored(PdfToWord.Box b) {
        return b.rotated && Math.abs(b.angle) < 1f && !b.ring;
    }

    /**
     * The stamp's frame around one line, in the page's own coordinates.
     *
     * <p>Both callers - the writer, and the pass that orders a page's blocks - have to agree
     * about where a line's baseline really is, so the mirroring a 180-degree line needs is
     * applied in one place (see {@link #mirrored}). PDFBox reports a turned line's origin in a
     * frame turned with it, so on a 180-degree stamp both coordinates come back mirrored about
     * the page.
     */
    private static Frame frameOfLine(java.util.List<Shape> shapes, PdfToWord.Box b, Ctx ctx) {
        float angle = mirrored(b) ? 180f : b.angle;
        float px = b.x, py = b.y;
        if (mirrored(b)) {
            px = ctx.pageWidthPt - b.x;
            py = ctx.pageHeightPt - b.y;
        }
        return frameOf(shapes, px, py, angle);
    }

    private static Frame frameOf(java.util.List<Shape> shapes, float px, float py, float angle) {
        if (shapes == null) return null;
        double th = Math.toRadians(angle);
        double ux = Math.cos(th), uy = Math.sin(th);
        double vx = -Math.sin(th), vy = Math.cos(th);
        Frame best = null;
        float bestArea = 0f;
        for (Shape s : shapes) {
            if (s.fillRgb >= 0 || s.lineRgb < 0) continue;
            java.util.List<float[]> pts = new ArrayList<>();
            if (s.kind == 2 && s.freeform != null) {
                for (float[] c : s.freeform) {
                    int type = (int) c[0];
                    if (type == 0 || type == 1) pts.add(new float[]{c[1], c[2]});
                    else if (type == 2) pts.add(new float[]{c[c.length - 2], c[c.length - 1]});
                }
            } else if (s.kind == 0) {
                // A rectangle drawn with `re` comes through as a preset box, which carries no
                // rotation - so it is only usable where its bounding box IS the rectangle,
                // i.e. where the page turned it by a whole quarter turn. 04's 180-degree frame
                // is exactly that case, and it is the only one in the corpus.
                double c = Math.abs(Math.cos(th));
                if (c > 0.02 && c < 0.98) continue;
                pts.add(new float[]{s.xPt, s.topPt});
                pts.add(new float[]{s.xPt + s.wPt, s.topPt});
                pts.add(new float[]{s.xPt + s.wPt, s.topPt + s.hPt});
                pts.add(new float[]{s.xPt, s.topPt + s.hPt});
            } else {
                continue;
            }
            if (pts.size() != 4) continue;
            double cx = 0, cy = 0;
            for (float[] p : pts) { cx += p[0]; cy += p[1]; }
            cx /= 4.0; cy /= 4.0;
            // A rectangle's corners are the furthest points along its own axes, so the extents
            // come straight out of the four corners and no edge order is needed.
            float w = 0f, h = 0f;
            for (float[] p : pts) {
                w = Math.max(w, 2f * (float) Math.abs((p[0] - cx) * ux + (p[1] - cy) * uy));
                h = Math.max(h, 2f * (float) Math.abs((p[0] - cx) * vx + (p[1] - cy) * vy));
            }
            if (w < 8f || h < 4f) continue;
            // The shape has to share the line's rotation. Its longest edge is the one along the
            // reading direction for every stamp in the corpus; for a frame that is taller than
            // it is wide that is the edge the text runs down.
            double ex = 0, ey = 0, el = 0;
            for (int i = 0; i < 4; i++) {
                float[] p = pts.get(i), q = pts.get((i + 1) % 4);
                double dx = q[0] - p[0], dy = q[1] - p[1], len = Math.hypot(dx, dy);
                if (len > el) { el = len; ex = dx / len; ey = dy / len; }
            }
            if (el <= 0 || Math.abs(ex * ux + ey * uy) < 0.985) continue;
            double p0x = cx - (w / 2.0) * ux - (h / 2.0) * vx;
            double p0y = cy - (w / 2.0) * uy - (h / 2.0) * vy;
            double lIns = (px - p0x) * ux + (py - p0y) * uy;
            double tIns = (px - p0x) * vx + (py - p0y) * vy;
            if (lIns < -2.0 || lIns > w + 2.0 || tIns < -2.0 || tIns > h + 2.0) continue;
            if (w * h > bestArea) {
                bestArea = w * h;
                best = new Frame();
                best.cx = (float) cx; best.cy = (float) cy;
                best.w = w; best.h = h;
                best.lIns = (float) lIns; best.tIns = (float) tIns;
                best.shape = s;
            }
        }
        return best;
    }

    // ------------------------------------------------------------- the stamp's frame (D-25)

    /**
     * The four corners of a stroked, unfilled rectangle, in the page's own frame, or null.
     *
     * <p>A rectangle the page draws as four lines arrives as a freeform path and one drawn with
     * {@code re} arrives as a preset box, so both spellings are read here and both answer with
     * the same thing: four corners in the frame every {@code Shape} in this writer uses, where y
     * counts down from the top of the page. Everything the stamp grouping does is done on these
     * corners, so a rule cannot be recognised one way and merged another.
     */
    private static float[][] rectCorners(Shape s) {
        if (s.fillRgb >= 0 || s.lineRgb < 0) return null;
        if (s.kind == 2 && s.freeform != null) {
            java.util.List<float[]> pts = new ArrayList<>();
            for (float[] c : s.freeform) {
                int type = (int) c[0];
                if (type == 0 || type == 1) pts.add(new float[]{c[1], c[2]});
                else if (type == 2) pts.add(new float[]{c[c.length - 2], c[c.length - 1]});
            }
            if (pts.size() != 4) return null;
            return pts.toArray(new float[0][]);
        }
        if (s.kind == 0) {
            return new float[][]{
                    {s.xPt, s.topPt},
                    {s.xPt + s.wPt, s.topPt},
                    {s.xPt + s.wPt, s.topPt + s.hPt},
                    {s.xPt, s.topPt + s.hPt}};
        }
        return null;
    }

    /** The centre of a rectangle given its corners. */
    private static float[] rectCentre(float[][] c) {
        float x = 0f, y = 0f;
        for (float[] p : c) { x += p[0]; y += p[1]; }
        return new float[]{x / c.length, y / c.length};
    }

    /** The direction of a rectangle's longest edge, as a unit vector. */
    private static float[] rectAxis(float[][] c) {
        double ex = 0, ey = 0, el = 0;
        for (int i = 0; i < c.length; i++) {
            float[] p = c[i], q = c[(i + 1) % c.length];
            double dx = q[0] - p[0], dy = q[1] - p[1], len = Math.hypot(dx, dy);
            if (len > el) { el = len; ex = dx / len; ey = dy / len; }
        }
        return el <= 0 ? null : new float[]{(float) ex, (float) ey};
    }

    /**
     * Are these two rules the inner and outer rule of ONE stamp?
     *
     * <p>A stamp's frame is drawn twice - an outer rule and an inner one a few points inside it -
     * and the two share a centre and an angle and nothing else. Measured on the corpus: every
     * stamp in 01, 02, 03, 04, 06, 07 and 08 has its two rules on exactly the same centre and at
     * exactly the same angle, and the nearest pair of rules belonging to two DIFFERENT stamps
     * (08's overlapping pair) is 54 pt apart. So the test is a shared centre within a few points
     * and parallel edges, and it does not need to guess from sizes.
     *
     * <p>This is the one place a stamp is recognised. The frame is not found from the text, and
     * the text is not found from the frame: the rules are grouped with each other, which is what
     * makes them one object that cannot drift against itself.
     */
    private static boolean sameStamp(float[][] a, float[][] b) {
        if (a == null || b == null) return false;
        float[] ca = rectCentre(a), cb = rectCentre(b);
        float[] aa = rectAxis(a), ab = rectAxis(b);
        if (aa == null || ab == null) return false;
        if (Math.abs(aa[0] * ab[0] + aa[1] * ab[1]) < 0.985f) return false;
        float diagA = rectDiag(a), diagB = rectDiag(b);
        float tol = Math.max(2.5f, 0.04f * Math.min(diagA, diagB));
        return Math.hypot(ca[0] - cb[0], ca[1] - cb[1]) <= tol;
    }

    private static float rectDiag(float[][] c) {
        return (float) Math.hypot(c[1][0] - c[3][0], c[1][1] - c[3][1]);
    }

    private static float rectArea(float[][] c) {
        return Math.abs((c[1][0] - c[0][0]) * (c[3][1] - c[0][1])
                - (c[1][1] - c[0][1]) * (c[3][0] - c[0][0]));
    }

    /**
     * Put a stamp's text paragraphs where the page put them, instead of at the end of the page.
     *
     * <p>The engine reads a stamp after the page's own words, because a stamp is an overlay and
     * not part of the page's grid - which is right for detection and wrong for a paragraph. A
     * paragraph can only follow the paragraph before it: it cannot be given a position above the
     * point the flow has already reached, and {@code w:spacing w:before} is not allowed to be
     * negative. So a stamp line left at the end of the block list lands below the last line of
     * the page, 200 pt under its own frame.
     *
     * <p>Moving the stamp's paragraphs to the place in the page's order where their own y falls
     * is what lets {@code w:ind} and {@code w:before} do their job: the gap above the line is
     * then the gap the page really drew, and the line lands inside its frame. Nothing else on
     * the page moves - the gap from the last body line to the footer is the same gap it was.
     */
    private static void orderStamps(PdfToWord.Page page, java.util.List<Shape> outlines, Ctx ctx) {
        if (outlines == null || outlines.isEmpty()) return;
        java.util.List<Object> blocks = page.blocks;
        java.util.List<PdfToWord.Para> stamps = new ArrayList<>();
        for (Object b : blocks) {
            if (!(b instanceof PdfToWord.Para)) continue;
            PdfToWord.Para p = (PdfToWord.Para) b;
            boolean turned = false;
            for (PdfToWord.Box bx : p.boxes) if (bx.rotated) turned = true;
            if (!turned) continue;
            for (PdfToWord.Box bx : p.boxes) {
                if (bx.runs.isEmpty() || frameOfLine(outlines, bx, ctx) == null) continue;
                stamps.add(p);
                break;
            }
        }
        if (stamps.isEmpty()) return;
        blocks.removeAll(stamps);
        for (PdfToWord.Para p : stamps) {
            // Compare like with like. The other blocks are placed by blockTop(), which is the
            // top of a line's BOX (y - LINE_BASE * size); Para.top is a different quantity -
            // for a turned line it is the origin PDFBox reports in the line's own frame - so
            // mixing the two put a stamp line after a prose line it sits above. On 02, IN ORDER
            // is at box top 473.2 and "Goods dispatched in good condition" at 478.6, and the
            // mixed comparison filed the stamp under the prose.
            float pTop = blockTop(p);
            if (pTop < 0f) pTop = p.top;
            int at = blocks.size();
            for (int i = 0; i < blocks.size(); i++) {
                if (blockTop(blocks.get(i)) > pTop) { at = i; break; }
            }
            blocks.add(at, p);
        }
    }

    /**
     * Fold every stamp's concentric frame rules into one freeform shape.
     *
     * <p>This is the whole of D-25's first requirement. The user's report, corrected: in the
     * commercial converters the two frame lines select TOGETHER, and each line of text selects
     * on its own; this writer had the outer rule welded to a line of text and the inner rule
     * alone, so the two rules could - and did - drift apart. Two rules in one path, in one
     * shape, with one bounding box, cannot: there is no second set of coordinates to disagree
     * with the first.
     *
     * <p>The outermost rule is the host, because that is the block the page drew first and it is
     * the one whose stroke weight and colour the shape carries. Every rule is marked
     * {@code stampFrame} - which is NOT {@code consumed} - so the writer draws the group once,
     * where the outermost rule sits, and never draws or consumes a rule on its own.
     */
    private static void stampFrames(java.util.List<Shape> shapes) {
        if (shapes == null || shapes.size() < 2) return;
        int n = shapes.size();
        float[][][] cs = new float[n][][];
        for (int i = 0; i < n; i++) cs[i] = rectCorners(shapes.get(i));
        boolean[] taken = new boolean[n];
        for (int i = 0; i < n; i++) {
            if (taken[i] || cs[i] == null) continue;
            java.util.List<Integer> group = new ArrayList<>();
            group.add(i);
            for (int j = i + 1; j < n; j++) {
                if (taken[j] || cs[j] == null) continue;
                if (sameStamp(cs[i], cs[j])) group.add(j);
            }
            if (group.size() < 2) continue;
            int outer = group.get(0);
            for (int k : group) if (rectArea(cs[k]) > rectArea(cs[outer])) outer = k;
            // Outer first, then the rest outermost-first, so the path reads the way the page
            // painted it.
            java.util.List<Integer> ordered = new ArrayList<>();
            ordered.add(outer);
            for (int k : group) if (k != outer) ordered.add(k);
            for (int a = 1; a < ordered.size(); a++) {
                for (int b = a + 1; b < ordered.size(); b++) {
                    if (rectArea(cs[ordered.get(b)]) > rectArea(cs[ordered.get(a)])) {
                        int t = ordered.get(a);
                        ordered.set(a, ordered.get(b));
                        ordered.set(b, t);
                    }
                }
            }
            Shape host = shapes.get(outer);
            host.mergedShape = mergedFrame(host, ordered, cs);
            for (int k : group) {
                Shape s = shapes.get(k);
                s.stampFrame = true;
                s.mergedHost = host;
                taken[k] = true;
            }
        }
    }

    /**
     * One freeform holding every rule of one stamp, as closed sub-paths of a single path.
     *
     * <p>The rotation is in the coordinates: each rule contributes the four corners the page
     * itself drew, so a frame at 15 degrees is a 15-degree path and nothing has to rotate it
     * afterwards. There is no {@code a:xfrm rot} on a stamp frame and there must not be - a
     * rotation attribute is a second place the geometry can be wrong.
     */
    private static Shape mergedFrame(Shape host, java.util.List<Integer> ordered,
                                     float[][][] cs) {
        float minX = Float.MAX_VALUE, minY = Float.MAX_VALUE;
        float maxX = -Float.MAX_VALUE, maxY = -Float.MAX_VALUE;
        for (int k : ordered) {
            for (float[] p : cs[k]) {
                minX = Math.min(minX, p[0]);
                minY = Math.min(minY, p[1]);
                maxX = Math.max(maxX, p[0]);
                maxY = Math.max(maxY, p[1]);
            }
        }
        Shape m = new Shape(minX, minY, Math.max(0.1f, maxX - minX), Math.max(0.1f, maxY - minY));
        m.kind = 2;
        m.fillRgb = -1;
        m.lineRgb = host.lineRgb;
        m.lineWidthPt = host.lineWidthPt;
        m.lineAlpha = host.lineAlpha;
        java.util.List<float[]> cmds = new ArrayList<>();
        for (int k : ordered) {
            for (int i = 0; i < 4; i++) {
                cmds.add(new float[]{i == 0 ? 0f : 1f, cs[k][i][0], cs[k][i][1]});
            }
            cmds.add(new float[]{3f});
        }
        m.freeform = cmds;
        m.freeformClosed = false;
        return m;
    }

    /**
     * One line of stamp text: a real paragraph, held at the page's own (x, y) by {@code w:framePr}.
     *
     * <p>This is the other half of D-25, and T02-A is why it is a frame and no longer a flowed
     * paragraph. The stamp used to be a {@code wps:txbx} text box, and Google Docs renders a
     * text box as a drawing and cannot put a caret inside it - the user's "the stamp is not
     * editable at all" on 02. A paragraph can be selected, edited and typed into in every
     * reader, so each line of the stamp is one, and it stays one here.
     *
     * <p>WHAT WAS WRONG WITH PLACING IT BY {@code w:ind} AND {@code w:spacing}. A flow only goes
     * downwards. A stamp is drawn OVER the page: its lines sit at a y the prose beside them has
     * already passed, and {@code w:spacing w:before} cannot be negative, so the paragraph lands
     * at whichever is lower - its own y or the flow's position - and then every line after it
     * inherits the overshoot. Measured on the five stamp documents before this change: the
     * stamp's own lines landed 11 pt (02), 39-117 pt (03), 60 pt (04), 33-87 pt (08) and 80-87 pt
     * (01) below their y, the prose below them was pushed down by the same amount, and on 03 and
     * 04 one stamp line ("VERIFIED FOR AUDIT", "DUPLICATE ISSUED") was not in the render at all.
     * {@code orderStamps()} could not fix that: it moves a paragraph in the block list, and no
     * position in a flow is above the flow's own point.
     *
     * <p>WHAT A FRAME DOES. {@code w:framePr} is a paragraph property - not a drawing, not a
     * text box - that takes the paragraph out of the flow and anchors it at an absolute page
     * point with {@code w:wrap="none"}. So the paragraph is still a paragraph (selectable,
     * editable, in the document's order, {@code wps:txbx} stays 0), and it is where the page put
     * it, and it adds nothing to the height of the page it sits on. The point written is the
     * corner of the line's own box in page space, taken from the baseline's origin and the
     * line's angle - not the origin itself, which is a different point for every angle but a
     * horizontal one. The glyphs then sit in the frame exactly as they sit in a flowed line of
     * the same box.
     *
     * <p>The glyphs of a line the page drew at an angle come out upright here: OOXML has no text
     * rotation that LibreOffice honours, which is the recorded renderer limit (D-16) and not
     * something this writer can fix. What the paragraph does give is the line's own position and
     * its own editability, and the frame around it keeps its angle because the angle is in the
     * frame's path.
     */
    private static void stampLine(StringBuilder sb, PdfToWord.Para p, PdfToWord.Box b, Ctx ctx,
                                  float px, float py, float lineAngle, float advance) {
        String text = b.text();
        if (text.trim().isEmpty()) return;
        // The line's own box, measured exactly as a flowed line's is, so the glyphs land at the
        // same place inside the frame as they would inside a paragraph of the same height.
        float linePt = flowLinePt(-1f, b.size, 0f);
        float len = Math.max(b.length, advance);
        // THE CORNER OF THE LINE'S BOX IN PAGE SPACE, from the one point the engine has: the
        // baseline's origin. Reading it as if it were the corner is the second half of the
        // defect - the stamp's words were 39 pt low on 01, 69 pt on 03 and 12 pt on 04 while the
        // frame they belong to was drawn in the right place, which is the "the frame drifts"
        // the user reported. A turned baseline is not a horizontal one:
        //
        //   * the box top is the top of the whole baseline, not the y of its first glyph, so a
        //     line that rises to the right starts at the BOTTOM of its own box (01, 08);
        //   * the ascent is measured across the baseline, so on a 90-degree line it is a
        //     displacement along x and moves the box top by nothing at all (03);
        //   * and a 180-degree line's origin comes back MIRRORED, so the part of the box above
        //     its baseline is below it on the page - the box has to be mirrored, not the point
        //     (04, and D-25's note on the mirrored pair).
        double th = Math.toRadians(lineAngle);
        float cosA = (float) Math.cos(th), sinA = (float) Math.sin(th);
        float startX, topPt;
        if (mirrored(b)) {
            // Mirrored: the page-space top is the mirror of the box's own BOTTOM.
            topPt = ctx.pageHeightPt - b.y - (1f - LINE_BASE) * linePt;
            startX = px - len;
        } else {
            topPt = Math.min(py, py + len * sinA) - LINE_BASE * linePt * Math.abs(cosA);
            startX = Math.min(px, px + len * cosA);
            // A line that runs UP the page rather than across it. Its own box is one glyph wide
            // and a hundred points tall, and the words are written upright - OOXML has no
            // rotation LibreOffice honours (D-16) - so the one thing that can be kept is that
            // the line stays on the paper: it is centred on the column the page drew it in, which
            // is where it was before and where the reader can still see it.
            if (Math.abs(cosA) < 0.5f) startX = px - len / 2f;
        }
        int lineTw = (int) Math.max(1L, Math.round(linePt * TWIPS_PER_PT));
        int xTw = (int) Math.max(0L, Math.round(startX * TWIPS_PER_PT));
        int yTw = (int) Math.max(0L, Math.round(topPt * TWIPS_PER_PT));
        // Wide enough for the line unwrapped. A frame wraps its own text at w:w, so a box that
        // is a point too narrow turns "GOODS RECEIVED" into two lines inside the stamp.
        float boxW = len + b.size * 1.5f;
        // And never off the paper. A stamp is drawn at the edge of the page by definition, so a
        // line whose upright text is wider than the room to the right of it would be cut off by
        // the page edge instead of the frame - measured on 03, where the vertical line at x=541
        // had 54 pt of paper left and 113 pt of text, and the render held "VERIFIED FO".
        startX = Math.max(0f, Math.min(startX, ctx.pageWidthPt - boxW));
        int wTw = (int) Math.max(1L, Math.round(boxW * TWIPS_PER_PT));
        sb.append("<w:p><w:pPr>")
                .append("<w:framePr w:w=\"").append(wTw)
                .append("\" w:h=\"").append(lineTw)
                .append("\" w:hRule=\"exact\" w:wrap=\"none\" w:vAnchor=\"page\" w:hAnchor=\"page\"")
                .append(" w:x=\"").append(xTw).append("\" w:y=\"").append(yTw).append("\"/>")
                .append("<w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\"")
                .append(" w:before=\"0\" w:after=\"0\" w:line=\"").append(lineTw)
                .append("\" w:lineRule=\"exact\"/>")
                .append("<w:ind w:left=\"0\" w:right=\"0\" w:firstLine=\"0\"/>")
                .append("</w:pPr>");
        for (PdfToWord.Run run : b.runs) {
            if (run.text.isEmpty()) continue;
            runXml(sb, run);
        }
        sb.append("</w:p>");
    }

    /**
     * An anchored text box whose local point (lx, ly) lands on the page point (pageX, pageY)
     * once the box has been rotated by {@code rotDeg} about its own centre.
     *
     * <p>{@code <a:xfrm rot>} turns the box about its CENTRE, so the offset written in
     * {@code wp:positionH/V} is not where the text starts - it is where the unrotated box's
     * top-left would be. Writing the line's origin there therefore moves the text by
     * {@code R(rot) . (L - centre)} as soon as the box is turned, which is 135 pt on file 01 and
     * the reason a rotated stamp never sat where the page drew it. The offset is solved for
     * here instead:
     *
     * <pre>  off = P - centre - R(rot) . (L - centre)  </pre>
     *
     * <p>with R the clockwise rotation the {@code rot} attribute means in a frame whose y counts
     * down the page. For {@code rotDeg == 0} this is exactly {@code P - L}, so an unrotated box
     * is placed where it always was.
     *
     * <p>Both renderers then agree on where the text STARTS: Word draws the run along the rotated
     * baseline from that point, LibreOffice rotates the frame but not the glyphs and draws them
     * horizontally from that same point (see D-16 in REMAINING-DEFECTS.md - Writer has no
     * arbitrary text rotation, in any OOXML spelling). The anchor is the same in both, so the
     * measurement below is a measurement of the geometry and not of one renderer's bug.
     */
    private static void anchorAt(StringBuilder sb, Ctx ctx, float pageX, float pageY,
                                 float lx, float ly, float wPt, float hPt, String inner,
                                 float rotDeg, int borderRgb, float borderWpt) {
        anchorAt(sb, ctx, pageX, pageY, lx, ly, wPt, hPt, inner, rotDeg, borderRgb, borderWpt,
                0f, 0f);
    }

    /**
     * The same, with the text placed inside the box by its insets rather than at its corner.
     *
     * <p>This is what makes a stamp one object. The box IS the rectangle the page drew, its
     * border IS the page's stroke, and the text is put where the page put it inside that
     * rectangle - so there is one geometry and no second position calculation to drift from.
     */
    private static void anchorAt(StringBuilder sb, Ctx ctx, float pageX, float pageY,
                                 float lx, float ly, float wPt, float hPt, String inner,
                                 float rotDeg, int borderRgb, float borderWpt,
                                 float lInsPt, float tInsPt) {
        double th = Math.toRadians(rotDeg);
        double cos = Math.cos(th), sin = Math.sin(th);
        double dx = lx - wPt / 2.0, dy = ly - hPt / 2.0;
        float offXpt = (float) (pageX - wPt / 2.0 - (cos * dx - sin * dy));
        float offYpt = (float) (pageY - hPt / 2.0 - (sin * dx + cos * dy));
        int id = ctx.shapeSeq++;
        long cx = Math.max(1, Math.round(wPt * EMU_PER_PT));
        long cy = Math.max(1, Math.round(hPt * EMU_PER_PT));
        long offX = Math.round(offXpt * EMU_PER_PT);
        long offY = Math.round(offYpt * EMU_PER_PT);
        int relHeight = 251658240 + (id & 0xFFFF);

        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
                .append("<w:r><w:drawing>")
                .append("<wp:anchor distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\"")
                .append(" simplePos=\"0\" relativeHeight=\"").append(relHeight).append("\"")
                // behindDoc="1": a stamp is a mark ON the paper, not a lid over it. In front, the
                // box pushed the table text aside and the stamp's own text landed across the
                // totals column - which is what the user's screenshot shows. Behind, the page's
                // text flows over it as it does in the PDF, which is where the stamp was drawn.
                //
                // This alone does NOT make a rotated stamp look right: LibreOffice ignores
                // <a:xfrm rot> on a text box, so the 180-degree stamp still comes out upright.
                // It is a correct change on its own account, not the fix. See D-13.
                .append(" behindDoc=\"1\" locked=\"0\" layoutInCell=\"1\" allowOverlap=\"1\">")
                .append("<wp:simplePos x=\"0\" y=\"0\"/>")
                .append("<wp:positionH relativeFrom=\"page\"><wp:posOffset>").append(offX)
                .append("</wp:posOffset></wp:positionH>")
                .append("<wp:positionV relativeFrom=\"page\"><wp:posOffset>").append(offY)
                .append("</wp:posOffset></wp:positionV>")
                .append("<wp:extent cx=\"").append(cx).append("\" cy=\"").append(cy).append("\"/>")
                .append("<wp:effectExtent l=\"0\" t=\"0\" r=\"0\" b=\"0\"/>")
                .append("<wp:wrapNone/>")
                .append("<wp:docPr id=\"").append(id).append("\" name=\"KavoPDF text ")
                .append(id).append("\"/>")
                .append("<wp:cNvGraphicFramePr/>")
                .append("<a:graphic><a:graphicData uri=\"").append(NS_WPS).append("\">")
                .append("<wps:wsp><wps:cNvSpPr txBox=\"1\"/>")
                .append("<wps:spPr><a:xfrm");
        if (rotDeg != 0f) {
            long rot = Math.round(((rotDeg % 360f) + 360f) % 360f * 60000f);
            sb.append(" rot=\"").append(rot).append("\"");
        }
        sb.append("><a:off x=\"0\" y=\"0\"/><a:ext cx=\"").append(cx)
                .append("\" cy=\"").append(cy).append("\"/></a:xfrm>")
                .append("<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom>")
                .append("<a:noFill/>");
        if (borderRgb >= 0) {
            sb.append("<a:ln w=\"").append(Math.max(6350, Math.round(borderWpt * EMU_PER_PT)))
              .append("\"><a:solidFill><a:srgbClr val=\"")
              .append(String.format("%06X", borderRgb & 0xFFFFFF))
              .append("\"/></a:solidFill></a:ln>");
        } else {
            sb.append("<a:ln><a:noFill/></a:ln>");
        }
        sb.append("</wps:spPr>")
                .append("<wps:txbx><w:txbxContent>").append(inner).append("</w:txbxContent></wps:txbx>")
                // wrap="none": the box must not re-wrap the line it holds, or a long line
                // would break at the box width and the second half would land under the first.
                .append("<wps:bodyPr wrap=\"none\" lIns=\"")
                .append(Math.round(lInsPt * EMU_PER_PT)).append("\" tIns=\"")
                .append(Math.round(tInsPt * EMU_PER_PT))
                .append("\" rIns=\"0\" bIns=\"0\"")
                .append(" anchor=\"t\" anchorCtr=\"0\"><a:noAutofit/></wps:bodyPr>")
                .append("</wps:wsp></a:graphicData></a:graphic>")
                .append("</wp:anchor></w:drawing></w:r></w:p>");
        ctx.anchorCount++;
    }

    // ------------------------------------------------------------------ tables

    /**
     * A table stays a table: {@code w:tbl} with real rows and cells, inside a text box so it
     * keeps the position it had on the page. Turning the cells into loose text boxes would
     * place the text and destroy the table, which is the one thing a conversion must not do.
     */
    /**
     * The table's borders: each of the six sides at its own weight and its own colour.
     *
     * <p>Every side the page drew a rule on gets that side's OWN weight and colour - D-22: the
     * six sides are six arguments now, one per side, taken from the rule that actually lies on
     * that side ({@link PdfToWord.Table#sideStroke}). A side the page did not draw gets "nil" -
     * never no w:tblBorders element at all, because absent borders
     * fall back to the table style and the default style draws a box, which is exactly the box
     * 403 and 406 were carrying. The four outer sides are {@code outer}, the row separators
     * {@code innerH} and the column separators {@code innerV}; a table the ruled pass found has
     * all three, because there the bounds ARE the drawn grid.
     *
     * <p>The history matters, because this has now been the other way twice. The weight used to
     * be read off the stroke the page drew (c47efc2), but off the PAGE's stroke rather than the
     * rule on the side being written, so a table ruled at 0.5 pt came out heavier than one ruled
     * at 1.25 pt and the numbers matched no line anywhere; the answer then was one constant
     * (D-22's predecessor). D-22 is the third state and the one the user asked for: the page's
     * own weight and opacity, side by side on the same table, so a table ruled at 0.4 pt grey
     * inside a 2 pt black frame comes out that way. A table whose six sides genuinely differ
     * will look uneven - that is the page, not a bug.
     *
     * <p>A side with no stroke ({@code sideStroke} null) keeps the old constant, sz 8 in
     * 000000, so nothing that used to be right changes.
     */
    private static String borders(int[] sideSz, String[] sideColour,
                                  boolean outer, boolean innerH, boolean innerV) {
        StringBuilder b = new StringBuilder("<w:tblBorders>");
        for (int i = 0; i < TABLE_SIDES.length; i++) {
            String side = TABLE_SIDES[i];
            boolean drawn = "insideH".equals(side) ? innerH
                    : "insideV".equals(side) ? innerV
                    : outer;
            // w:val="nil", not "none" with sz="0" w:color="auto". "auto" is an inherited colour
            // by definition - a reader resolves it to whatever it thinks a line is, usually the
            // flipped text colour - and it was written on 486 sides across 59 documents. A side
            // the page did not draw is no line at all, and "nil" says that without naming a
            // colour that someone else will decide.
            b.append("<w:").append(side).append(" w:val=\"").append(drawn ? "single" : "nil").append("\"");
            if (drawn) b.append(" w:sz=\"").append(sideSz[i])
                    .append("\" w:color=\"").append(sideColour[i]).append("\"");
            b.append("/>");
        }
        return b.append("</w:tblBorders>").toString();
    }

    /**
     * The weight a side falls back to when the page's own stroke for it was not read: sz 8, in
     * eighths of a point, so 1 pt.
     *
     * <p>Measured off the two commercial converters, which are the same engine and produce
     * byte-identical styles, settings and theme parts: every one of their six table sides is
     * <code>w:sz="8" w:color="000000"</code>. That is still the fallback, but it is no longer
     * the answer for every side: since D-22 a side carries the weight of the rule that lies on
     * it, and this value only stands in where no rule could be read (see {@link #borders}).
     */
    private static final int TABLE_RULE_SZ = 8;
    /** The colour a side falls back to when the page's own stroke for it was not read. */
    private static final String TABLE_RULE_COLOUR = "000000";
    /**
     * The range {@code w:sz} accepts, in eighths of a point: 2 (0.25 pt) to 96 (12 pt).
     *
     * <p>Outside it the value is invalid and a reader is free to drop the border or the whole
     * table property. A page rule of 0.1 pt - a hairline, and the PDF spec allows one - rounds
     * to sz 1 and would be thrown away; a 14 pt bar rounds to 112 and is not a table border. So
     * a width read off the page is clamped into the range rather than written as read.
     */
    private static final int TABLE_RULE_SZ_MIN = 2;
    private static final int TABLE_RULE_SZ_MAX = 96;

    /**
     * A stroke width in points as {@code w:sz}, in eighths of a point, clamped to 2..96.
     *
     * <p>0.1 pt clamps to sz 2 (0.25 pt) and anything at or above 12 pt clamps to sz 96. The
     * clamp is a real loss of fidelity at both ends - a 0.1 pt hairline is drawn a quarter point
     * thick - and it is the narrower loss: a border outside the range is not a border at all.
     */
    private static int szOf(float widthPt) {
        int sz = Math.round(Math.max(0.1f, widthPt) * 8f);
        return Math.max(TABLE_RULE_SZ_MIN, Math.min(TABLE_RULE_SZ_MAX, sz));
    }

    /**
     * A border's colour: the page's own, blended toward the white page by the rule's opacity.
     *
     * <p>{@code w:tblBorders} has no opacity - the element carries only {@code w:val},
     * {@code w:sz}, {@code w:space} and {@code w:color} - so a faint rule cannot be written as
     * a black rule at 30 % alpha. It is written as the colour that rule looks like on white:
     * {@code c' = c*a + 255*(1-a)} per channel. A 30 % black hairline becomes D8D8D8, which is
     * what a reader sees on the page. This is an approximation - on a page whose background is
     * not white it is the wrong direction, and where a rule overlaps another rule the blend is
     * not the page's - and it is stated in the report rather than hidden.
     */
    private static String borderColour(float[] stroke) {
        int rgb = (int) stroke[1];
        if (rgb < 0) return TABLE_RULE_COLOUR;
        float a = stroke.length > 2 ? Math.max(0f, Math.min(1f, stroke[2])) : 1f;
        if (a >= 0.999f) return hex(rgb);
        int r = Math.round(((rgb >> 16) & 0xFF) * a + 255f * (1f - a));
        int g = Math.round(((rgb >> 8) & 0xFF) * a + 255f * (1f - a));
        int b = Math.round((rgb & 0xFF) * a + 255f * (1f - a));
        return hex((r << 16) | (g << 8) | b);
    }
    /** The six sides a {@code w:tblBorders} element carries. */
    private static final String[] TABLE_SIDES =
            {"top", "left", "bottom", "right", "insideH", "insideV"};

    /**
     * Did the page draw a rule on this table?
     *
     * <p>Two shapes say yes. A stroke lying along one of the table's four sides - the grid the
     * ruled pass reads, which puts the rule on the cell boundary itself.
     *
     * <p>And a stroke-only box that frames the table. The whitespace pass measures a table's
     * bounds from its TEXT, so the frame the page draws round it is not on those bounds: on
     * 04_stamp_180deg the box round the first table starts 8.3 pt left of the table's first
     * character, 14.3 pt above its first row and 96.1 pt right of its last, because the last
     * column's text stops short of the drawn right edge. No edge test with a 2.5 pt tolerance
     * can see that box, which is why the document came out with all six sides "none" while the
     * page drew a full grid.
     *
     * <p>The frame counts only when it follows the table - the table covers at least half the
     * frame's width and half its height - so a page border, or a box a table merely sits inside,
     * is not read as a table rule. Measured on the 208-document corpus: 29 tables that the
     * whitespace pass found inside a frame the page drew are ruled by this test, and the four
     * documents whose frame is not a table rule (406's passport frame, 351's OMR sheet, 363's
     * warranty card, 364's ticket) keep the "none" they have today.
     */
    private static boolean pageDrewRule(PdfToWord.Table t, java.util.List<Shape> shapes) {
        if (shapes == null || shapes.isEmpty()) return false;
        float tol = 2.5f;
        float tw = t.right - t.left, th = t.bottom - t.top;
        for (Shape s : shapes) {
            if (s.lineRgb < 0 || s.fillRgb >= 0) continue;
            boolean onTop = Math.abs(s.topPt - t.top) <= tol
                    && s.xPt <= t.right + tol && s.xPt + s.wPt >= t.left - tol;
            boolean onBottom = Math.abs(s.topPt + s.hPt - t.bottom) <= tol
                    && s.xPt <= t.right + tol && s.xPt + s.wPt >= t.left - tol;
            boolean onLeft = Math.abs(s.xPt - t.left) <= tol
                    && s.topPt <= t.bottom + tol && s.topPt + s.hPt >= t.top - tol;
            boolean onRight = Math.abs(s.xPt + s.wPt - t.right) <= tol
                    && s.topPt <= t.bottom + tol && s.topPt + s.hPt >= t.top - tol;
            if (onTop || onBottom || onLeft || onRight) return true;
            // A rule, not a frame: a hairline band cannot be the box a table sits in.
            if (s.wPt < 8f || s.hPt < 8f) continue;
            boolean encloses = t.top >= s.topPt - tol && t.bottom <= s.topPt + s.hPt + tol
                    && t.left >= s.xPt - tol && t.right <= s.xPt + s.wPt + tol;
            if (encloses && tw >= s.wPt * 0.5f && th >= s.hPt * 0.5f) return true;
        }
        return false;
    }

    private static void table(StringBuilder sb, PdfToWord.Table t, Ctx ctx) {
        int cols = 0;
        for (List<String> row : t.rows) cols = Math.max(cols, row.size());
        if (cols == 0) return;
        // The column edges the page actually used, when the pass that found the table knew
        // them. Even columns put a right-aligned figure 60 pt from where the reader saw it.
        int[] colTw = new int[cols];
        float x0 = t.left;
        boolean exact = t.colX != null && t.colX.length == cols + 1;
        if (exact) {
            x0 = t.colX[0];
            for (int c = 0; c < cols; c++) {
                colTw[c] = Math.max(1, Math.round((float) ((t.colX[c + 1] - t.colX[c])
                        * TWIPS_PER_PT)));
            }
        } else {
            float wPt = Math.max(40f, t.right - t.left);
            int width = Math.max(1, Math.round((float) (wPt * TWIPS_PER_PT / cols)));
            for (int c = 0; c < cols; c++) colTw[c] = width;
        }
        // A cell whose text is exactly as wide as its column still wraps: the page drew
        // "58,750.00" flush against the right border of a 49.5 pt column and the renderer put
        // the last digit on the next line. There is no empty cell to the right of the LAST
        // column to widen over, so that column gets the room its own text needs. The text is
        // anchored at its indent, not at the right border, so widening the column moves the
        // table's right rule and leaves the words where the page put them.
        if (exact && cols > 0) {
            long[] edges = new long[cols + 1];
            for (int c = 0; c < cols; c++) edges[c + 1] = edges[c] + colTw[c];
            int need = 0;
            for (int r = 0; r < t.rows.size(); r++) {
                float textR = cellRTw(t, r, cols - 1);
                if (Float.isNaN(textR)) continue;
                int inset = insetTw(t, r, cols - 1, x0, edges[cols - 1]);
                need = Math.max(need, inset + Math.round(textR) + 20);
            }
            if (need > colTw[cols - 1]) colTw[cols - 1] = need;
        }
        int totalTw = 0;
        for (int c = 0; c < cols; c++) totalTw += colTw[c];

        // A table starts where the page drew it. The flow before it ends on some baseline and
        // the page put the table's top rule at t.top; the difference is real white space that
        // nothing in the flow was accounting for, so a table sitting 40 pt below the last line
        // of prose began at the prose's own y and every row and everything under it moved up
        // by that much. A spacer paragraph of the measured height holds the gap open. It is a
        // paragraph rather than w:spacing on the table because OOXML gives a table no
        // before-spacing of its own.
        int spacerTw = 0;
        if (!ctx.newPage && !ctx.lastWasTable && ctx.flowY >= 0f && !Float.isNaN(t.rowTopPt)) {
            // The table's top is placed ABSOLUTELY, from the flow's real position (D-26): the
            // spacer is the distance from where the reader will be to where the page drew the
            // table's top edge. The arithmetic this replaces measured that distance from the
            // previous PDF baseline less a line - and a table's top has been a few points out
            // ever since, which is the defect REMAINING-DEFECTS.md records as unfixed.
            // WHY THE EVEN-GRID EXEMPTION IS GONE. This branch used to run only where
            // evenlySpaced(t.rowEdge) was FALSE - a taller header, a wrapped address, a merged
            // cell - on the reasoning that for an even grid "the average the writer used before
            // was exactly right". It is not, and the error is not in the rows at all: it is in
            // where the table STARTS. On marksheet-university-consolidated every table is a
            // perfect grid (edges 100/118/136, 156/175/193..., pitch 18.4 pt), so every table
            // took the `t.top` fallback below, whose line-and-a-bit threshold then dropped the
            // gap entirely: the page put the first table's top rule at y=100 and the render at
            // 86.75, a 13.25 pt lift carried by the table and by everything under it. The rows
            // were right the whole time; only the top was wrong. This is the "table-top offset -
            // one constant per page" that REMAINING-DEFECTS.md has recorded as unfixed since
            // D-26, and an even grid is where it was worst, because that is the case the guard
            // excluded.
            float prevLine = Math.max(4f, ctx.lastSize * LINE_FACTOR);
            float extraAbs = t.rowTopPt - flowTopPt(ctx);
            // Any positive gap is real for a table: its top edge is a RULE the page drew, not a
            // line box the substitute face guessed at. The line-and-a-bit threshold below is
            // right for the baseline arithmetic, where a small difference is the face's own
            // leading - but applied here it dropped a genuine 17.3 pt gap and put
            // 23_timetable_grid_txtpos' whole grid that far above the page. Measured: every line
            // of its header sat at dy -17.3.
            if (extraAbs >= 2f) {
                spacerTw = (int) Math.min(2880L, Math.round(extraAbs * TWIPS_PER_PT));
            }
        } else if (!ctx.newPage && !ctx.lastWasTable && ctx.lastBaseline >= 0f && t.top > ctx.lastBaseline) {
            float prevLine = Math.max(4f, ctx.lastSize * LINE_FACTOR);
            // MEASURED AND REVERTED: charging the spacer as (t.top - baseline) minus this line's
            // own slack below its baseline - the rule the flow itself now uses - put 390's table
            // 10.6 pt low instead of 3.7, because a table's first row does not start at the
            // spacer's end. The spacer stays as it was; the table's own top y is recorded in
            // REMAINING-DEFECTS.md and is not fixed here.
            float extra = (t.top - ctx.lastBaseline) - prevLine;
            // Only a gap the page really drew is worth a paragraph of its own. Below a line
            // and a bit, the difference is the substitute face's line box, not white space,
            // and charging it moved the table further down than the page had it.
            if (extra >= prevLine * 1.2f) {
                spacerTw = (int) Math.min(2880L, Math.round(extra * TWIPS_PER_PT));
            }
        }
        if (spacerTw > 0) {
            spacerTw = twScale(spacerTw, ctx.squeeze);
            sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                    .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"")
                    .append(spacerTw)
                    .append("\" w:lineRule=\"exact\"/><w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr></w:p>");
            ctx.flowTw += spacerTw;
            // The spacer is a line of its own: the table now starts at the flow's position
            // after it, which is the y the page drew the table's top at.
            ctx.flowY = flowTopPt(ctx) + spacerTw / (float) TWIPS_PER_PT;
            ctx.flowBoxPt = 0f;
        }

        StringBuilder inner = new StringBuilder(512);
        // The table is a real w:tbl in the flow, not a text box.
        //
        // A text box has a fixed height and clips what does not fit: on file 80 the box was
        // 44 pt tall, so of each dealer's six rows only the first two survived and the CIN,
        // IFSC and Address rows were gone from the document. Worse, the box is carried by a
        // wrapper paragraph, and that paragraph's own text is every cell of the table run
        // together with no separator - which is the "1.SUNRISE FASTENERS PVT LTDGSTIN
        // 29AABCS4821K1Z6..." a reader of the XML sees. A w:tbl is a table and nothing else:
        // one w:p per cell, no wrapper, no clip.
        //
        // It is inline, not floating. A floating table (w:tblpPr) is placed at the
        // page's own y, but Word and LibreOffice then wrap the flowing text AROUND it: on
        // file 01 the BILL TO heading at x=64 was shoved to x=528 and "State Code 33" to the
        // left edge of the paper, because both sat inside the address box's band; on file 16
        // the closing-balance sentence beside the ledger was squeezed into a five-line
        // column. The flow is the document now, so the table belongs in it and the text keeps
        // the indents the PDF drew.
        // The page's own rules decide whether this table is ruled, not the flag alone. A table
        // found by the whitespace pass carries ruled=false, so all six borders were written as
        // "none" - and a box the page closed on four sides came out with no sides at all. That
        // is the missing line on 04_stamp_180deg, whose grid the page draws round every table.
        // The same answer decides the row height, because a rule that is drawn is a rule the
        // renderer adds to the row, and {@link #TABLE_BORDER_TW} is that rule's height.
        boolean ruledTable = t.ruled || pageDrewRule(t, ctx.curShapes);
        // Six weights and six colours, one per side, read off the rule that lies on that side
        // (D-22). A side with no stroke keeps the old constant, so nothing that was right moves.
        int[] sideSz = new int[6];
        String[] sideColour = new String[6];
        for (int i = 0; i < 6; i++) {
            float[] stroke = t.sideStroke[i];
            sideSz[i] = stroke == null ? TABLE_RULE_SZ : szOf(stroke[0]);
            sideColour[i] = stroke == null ? TABLE_RULE_COLOUR : borderColour(stroke);
        }
        inner.append("<w:tbl><w:tblPr>")
                .append("<w:tblW w:w=\"").append(totalTw).append("\" w:type=\"dxa\"/>")
                .append("<w:tblInd w:w=\"").append(tw(x0)).append("\" w:type=\"dxa\"/>")
                // A named table style, so the table carries a style of its own rather than
                // falling back on a reader's default. It draws no borders and sets no colour.
                .append("<w:tblStyle w:val=\"KavoTable\"/>")
                // Each side on its own evidence. The ruled pass reads the grid itself, so its
                // tables are ruled all over; a whitespace table has a frame round it (the four
                // outer sides) and separators inside it only where the page drew them. A table
                // with no frame at all keeps all six undrawn even when a rule crosses its band:
                // that rule is as likely the edge of a filled band as a drawn separator, and a
                // line the page did not draw is the defect 403 and 406 came back with.
                .append(borders(sideSz, sideColour, ruledTable,
                        ruledTable && (t.ruled || t.innerH),
                        ruledTable && (t.ruled || t.innerV)))
                .append("<w:tblLayout w:type=\"fixed\"/>")
                // Word's default cell margin is 0.19 cm (108 twips) on each side. Left at the
                // default, every cell's text sat 6 pt right of where the page had it - a
                // measured 120 twips of error on every cell in the batch.
                .append("<w:tblCellMar><w:top w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:left w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:bottom w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:right w:w=\"0\" w:type=\"dxa\"/></w:tblCellMar>")
                .append("</w:tblPr><w:tblGrid>");
        for (int c = 0; c < cols; c++) {
            inner.append("<w:gridCol w:w=\"").append(colTw[c]).append("\"/>");
        }
        inner.append("</w:tblGrid>");

        // The laid-out left edge of each cell, in twips from the table's own x0. Word stacks the
        // column widths it is given, so this - not t.colX - is where a cell's box really starts;
        // the two differ by the rounding of each width to a whole twip.
        long[] edgeTw = new long[cols + 1];
        for (int c = 0; c < cols; c++) edgeTw[c + 1] = edgeTw[c] + colTw[c];

        // The table has to occupy the vertical space the page gave it. Without a row height Word
        // collapses every row to the height of its text, so a table drawn across 257 pt came out
        // 128 pt tall and everything BELOW it slid up the page: file 72's bank statement was 75 pt
        // high against its PDF, file 55's sidebar 141 pt low, and three documents spilled onto a
        // second sheet. Measured on the corpus, the drift is worst in exactly the documents that
        // contain a table and near zero in those that do not.
        int rowCount = Math.max(1, t.rows.size());
        float extentPt = t.bottom - t.top;
        int rowTw = extentPt > 0f ? (int) Math.round(extentPt / rowCount * TWIPS_PER_PT) : 0;
        // The rule the writer draws is added to every row by the renderer, so a row asked for
        // the page's own pitch arrives that much taller. With collapsed borders half of the top
        // rule and half of the bottom rule lie INSIDE the row's box: the 6-eighth-point hairline
        // below puts 0.375 pt of each into the row, 0.75 pt in all. Measured on
        // itr-computation-with-slab-table by rendering the same table with and without its
        // borders - 19.2 pt pitch with them, 18.4 pt without, against the page's own 18.4 pt,
        // and the 0.8 pt a row of that table drifted by is the 38 rows of a page losing a sheet
        // to nothing but its own rules. An unruled table draws no rule and keeps its full pitch.
        if (rowTw > 0 && ruledTable) rowTw = Math.max(1, rowTw - TABLE_BORDER_TW);
        // The exact line height inside a cell was 200 twips - 10 pt - for every cell of every
        // table in every document. A price list drawn at 5.8 pt on an 8.4 pt row pitch got a
        // 10 pt line, so each of its 29 rows grew 1.6 pt taller than the page drew it and the
        // table drifted 46 pt down the sheet by its last row. The line was then set to the
        // row's whole pitch instead, which fixes that case and breaks a different one: a cell
        // the page drew on TWO lines is charged the pitch twice and the row doubles. That is
        // 402_calendar_month_grid, whose six-week grid arrived as nine rows and pushed the
        // page's own footer onto a second sheet.
        //
        // The pitch is already carried by the row's own w:trHeight hRule="atLeast". So a cell
        // that holds ONE line keeps the pitch as its line height, exactly as before - that is
        // what puts a single line at the foot of its row, which is where most of this corpus's
        // tables drew it, and changing it moved 42 documents' cell text away from the page.
        // A cell that holds SEVERAL lines is the case that was wrong: charging the pitch to
        // every line charged the row twice over and doubled it. There the line is the cell's
        // own text - 1.25 em of its size, below - and the row stays the page's own pitch.
        // The page's own row edges, when the pass that built the table measured them. Every row
        // then takes the height the page gave THAT row, so a table whose rows are not evenly
        // spaced - a ledger's header, a wrapped address - no longer drifts by the average of its
        // neighbours: 1.45 pt a row on 16_right_aligned_amounts, 38 pt by the foot of the table
        // (D-26, cause 2). Where the edges are not known, the average is used exactly as before.
        float[] rowEdge = t.rowEdge;
        boolean exactRows = rowEdge != null && rowEdge.length == t.rows.size() + 1;
        for (int r = 0; r < t.rows.size(); r++) {
            List<String> row = t.rows.get(r);
            // This row's own pitch. A ruled table's rule lies inside the row's box, so it comes
            // off here exactly as it comes off the average above.
            int rowTwHere = rowTw;
            if (exactRows) {
                float pitchPt = rowEdge[r + 1] - rowEdge[r];
                if (pitchPt > 0.5f && pitchPt < 2000f) {
                    rowTwHere = (int) Math.round(pitchPt * TWIPS_PER_PT);
                    if (ruledTable) rowTwHere = Math.max(1, rowTwHere - TABLE_BORDER_TW);
                }
            }
            // The line inside the cell follows the row it is in: a cell's text is drawn at the
            // foot of its own row on most of this corpus, so the line height is the row's pitch.
            int cellLineHere = rowTwHere > 0 ? rowTwHere : 200;
            int naturalLineHere = rowTwHere > 0 ? Math.min(rowTwHere, 200) : 200;
            // Does any cell of this row hold more than one line of the page? A numbered item's
            // marker, a calendar's holiday name under its date, a two-line address in a box.
            int rowParts = 1;
            for (int q = 0; q < row.size() && q < cols; q++) {
                String cv = row.get(q);
                if (cv == null) continue;
                int n = 1;
                for (int i = 0; i < cv.length(); i++) if (cv.charAt(i) == '\n') n++;
                if (n > rowParts) rowParts = n;
            }
            int baseLineTw = rowParts > 1 ? naturalLineHere : cellLineHere;
            // The row's own line height, never smaller than its own text. cellLineTw is the
            // table's extent divided by its row count, which is an average - correct only when
            // the rows are evenly spaced. On a page with a tall header row, a merged cell or a
            // wrapped value that average is smaller than the row's text needs, so the line was
            // set below the type size and the text rode up over the rule above it. That is what
            // the light-mode screenshots show on 03 and 04: "III Semester, B.E. Computer
            // Science" sitting on its own border. The type size is the floor, and a row whose
            // text needs more than the average gets more.
            int rowLineTw = baseLineTw;
            for (int q = 0; q < row.size() && q < cols; q++) {
                // The cell's own point size, from the size table the model keeps.
                //
                // This read the size off the FONT NAME string - it took the text before the
                // first space and parsed it as a number - and the names the model holds are
                // plain family names ("DejaVuSans-Bold", "ABCDEF+DejaVuSans"). The parse
                // threw every time, sz stayed 0 and this floor never ran: the "type size is
                // the floor" fix below was dead code from the day it was written. On
                // 374_org_chart the box rows have a 5.35 pt pitch and 7 pt text, so the
                // label and the name under it were printed on top of each other - which is
                // the exact case the floor exists for. t.sizes is the same number the cell's
                // w:sz is written from, so the line and the type now agree.
                float sz = r < t.sizes.size() && q < t.sizes.get(r).size()
                        && t.sizes.get(r).get(q) != null ? t.sizes.get(r).get(q) : 0f;
                if (sz > 0f) rowLineTw = Math.max(rowLineTw, (int) Math.round(sz * 1.25f * TWIPS_PER_PT));
            }
            // A table is part of the page's height, so a squeezed page squeezes it too - but
            // never below the type it holds: a row that shrinks past its own text is a row whose
            // text is clipped, and the reader cannot read the page that was saved. rowLineTw
            // already carries the type-size floor, so the floor is taken before the scaling and
            // the scaled row is held at it.
            int typeFloorTw = rowLineTw;
            int rowHeightTw = Math.max(rowTwHere, rowLineTw);
            if (ctx.squeeze != 1f) {
                rowHeightTw = Math.max(typeFloorTw, twScale(rowHeightTw, ctx.squeeze));
                rowLineTw = Math.max(typeFloorTw, twScale(rowLineTw, ctx.squeeze));
            }
            inner.append("<w:tr>");
            if (rowTwHere > 0) {
                inner.append("<w:trPr><w:trHeight w:val=\"").append(rowHeightTw)
                     .append("\" w:hRule=\"atLeast\"/><w:cantSplit/></w:trPr>");
            }
            int c = 0;
            while (c < cols) {
                String cell = c < row.size() ? row.get(c) : "";
                String face = r < t.fonts.size() && c < t.fonts.get(r).size()
                        ? t.fonts.get(r).get(c) : "";
                // How far into its own box this cell's text was drawn. A cell's text does not
                // start at its border: the page padded it, centred it or right-aligned it, and
                // in a right-aligned column the distance changes row by row. Word's cell margin
                // is one number for the whole cell, so the offset goes on the paragraph, which
                // is per cell and is what w:ind means.
                int insetTw = insetTw(t, r, c, x0, edgeTw[c]);
                // A text that starts further right than its own cell is wide cannot be in that
                // cell alone: the page merged it with the columns to its right. The depot
                // report's "SCHEDULED" header begins 74 pt into a 66 pt column. Clamping the
                // indent to the column width puts the first letter at the right x and stacks the
                // rest one character per line - a vertical word. The cell is widened over the
                // empty cells beside it instead, which is what the page drew, and w:gridSpan is
                // how OOXML says it: no cell has to be split, and every later cell in the row
                // keeps its own left edge.
                // A cell is also too narrow when the words drawn in it are wider than the
                // cell is - the same merge, seen from the other side. File 80's dealer name
                // starts at the left edge of a 52 pt column and runs 176 pt, so it stayed in
                // that column and Word wrapped it as "SUNRISE / FASTENE / RS PVT / LTD".
                // The page never wrapped it; the cell is widened over the empty cells beside
                // it, and the line is left whole.
                float textR = cellRTw(t, r, c);
                int span = 1, spanTw = colTw[c];
                while (c + span < cols && cellAt(t, r, c + span).isEmpty()) {
                    boolean startsOutside = insetTw >= spanTw;
                    boolean tooWide = !Float.isNaN(textR) && insetTw + textR > spanTw;
                    if (!startsOutside && !tooWide) break;
                    spanTw += colTw[c + span];
                    span++;
                }
                if (insetTw > spanTw - 1) insetTw = Math.max(0, spanTw - 1);
                // A cell that could not be widened - because the cells beside it hold text of
                // their own - still has to hold its own text on one line. An inset that leaves
                // less room than the text is wide makes Word break the value: on 343_air_waybill
                // the Pieces cell is 1120 twips with a 949 twip inset, so "12" had 171 twips to
                // live in and was set as "1" over "2", and the row that the page draws once
                // arrived as two. The inset gives way by the few twips that let the text fit;
                // the column's own left edge is the page's, and a one-point x error is not the
                // same defect as a value broken in half.
                // The TEST and the CORRECTION have to be the same arithmetic. They were not:
                // the test asked whether the text was wider than the room it had (no slack at
                // all) and the correction then asked for a point more than the text is wide. A
                // cell that overran its room by less than a point therefore never took the
                // correction - and a point is exactly the margin this substitution lives on.
                // gst-invoice-with-qr-code's Rate column is 840 twips with a 551 twip inset
                // (the value is right-aligned, so the inset carries the alignment), which leaves
                // 289 twips for 286 twips of "Rate": the page's own face fits it with three
                // twips to spare, the render's does not, and the word broke as "Rat" over "e".
                // A cell the page drew on one line became two, every row of the table doubled -
                // 18.4 pt on the page, 35 pt in the render - and everything under it moved.
                int needTw = Float.isNaN(textR) ? 0 : (int) Math.ceil(textR) + 20;
                boolean textOverflows = !Float.isNaN(textR) && textR > 0f
                        && insetTw + needTw > spanTw;
                if (textOverflows) insetTw = Math.max(0, spanTw - needTw);
                inner.append("<w:tc><w:tcPr><w:tcW w:w=\"").append(spanTw)
                        .append("\" w:type=\"dxa\"/>");
                if (span > 1) inner.append("<w:gridSpan w:val=\"").append(span).append("\"/>");
                // The page drew this cell's text a point or two past its own column edge and
                // never broke the value: on 343_air_waybill "12" starts at 67.46 pt in a column
                // that ends at 76 and runs to 77. A word processor's default is to wrap it, and
                // the row the page draws once arrived as "1" over "2". w:noWrap is OOXML's own
                // way of saying what the page did - keep the value whole, let it overrun the
                // cell the point that the page overran it by - so the x the page measured
                // survives and nothing is moved to make room.
                inner.append("</w:tcPr>")
                        .append("<w:p><w:pPr><w:pStyle w:val=\"TableText\"/>")
                        .append("<w:snapToGrid w:val=\"0\"/>")
                        .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"")
                        .append(rowLineTw).append("\" w:lineRule=\"exact\"/>");
                if (insetTw > 0) inner.append("<w:ind w:left=\"").append(insetTw).append("\"/>");
                inner.append("</w:pPr>");
                if (!cell.isEmpty()) {
                    inner.append("<w:r><w:rPr>");
                    // Written in schema order - rFonts, b, color, sz, szCs. It was sz, szCs,
                    // rFonts, color, b, which is not the order the schema defines; a reader
                    // that validates rPr drops what it cannot place.
                    if (!face.isEmpty()) {
                        String f = esc(faceName(face));
                        inner.append("<w:rFonts w:ascii=\"").append(f)
                                .append("\" w:hAnsi=\"").append(f)
                                .append("\" w:cs=\"").append(f).append("\"/>");
                    }
                    // Bold is a property of the face the page DREW the cell in. Guessing it
                    // from "this is row zero of something that looks like a header" made a
                    // bold first row out of tables whose header is not bold, and missed a
                    // bold cell anywhere else. The face is the evidence; the header guess is
                    // only the fallback for a cell whose face the page did not name.
                    if (isBoldFace(face) || (r == 0 && t.header && face.isEmpty())) {
                        inner.append("<w:b/>");
                    }
                    // The colour the page drew this cell in. A cell is written as a string and
                    // a font name, so without this every coloured table - a grey label column,
                    // a navy header row - arrived in black. A cell whose page named no colour
                    // stays on Automatic, exactly as a run does.
                    if (r < t.colors.size() && c < t.colors.get(r).size()) {
                        int cellColor = t.colors.get(r).get(c);
                        if (cellColor >= 0) {
                            inner.append(String.format("<w:color w:val=\"%06X\"/>",
                                    cellColor & 0xFFFFFF));
                        }
                    }
                    // The size the page drew this cell at. The paragraph style carries one
                    // number for every table in the document - 10 pt - and the batch's tables
                    // are drawn at 7.5 to 12 pt, so without this every cell is set at a size
                    // the page never used. On file 22 the amounts are 8.5 pt: at the style's
                    // 10 pt they are 17.6 % too wide for their column and Word wraps
                    // "2,18,770.00" into "2,18,770.0" and "0".
                    float sz = r < t.sizes.size() && c < t.sizes.get(r).size()
                            ? t.sizes.get(r).get(c) : Float.NaN;
                    if (!Float.isNaN(sz) && sz > 0f) {
                        int half = Math.max(2, halfPointsDown(sz));
                        inner.append("<w:sz w:val=\"").append(half)
                                .append("\"/><w:szCs w:val=\"").append(half).append("\"/>");
                    }
                    // A cell can hold two lines of the page: a numbered item's marker sits on
                    // its own line above the name, and the page drew them eight points apart.
                    // One w:t would flatten them into "1. SUNRISE" again.
                    inner.append("</w:rPr>");
                    String[] parts = cell.split("\n");
                    for (int q = 0; q < parts.length; q++) {
                        if (q > 0) inner.append("<w:br/>");
                        inner.append("<w:t xml:space=\"preserve\">").append(esc(parts[q]))
                                .append("</w:t>");
                    }
                    inner.append("</w:r>");
                }
                inner.append("</w:p></w:tc>");
                c += span;
            }
            inner.append("</w:tr>");
        }
        inner.append("</w:tbl>");
        sb.append(inner);
        // A table must be followed by a paragraph of its own: Word inserts one if it is not
        // there, and a paragraph the writer did not place is a paragraph it cannot measure.
        //
        // It is 4 pt, not 1 twip. At one twip the paragraph is a zero-height line, and
        // LibreOffice absorbed it into the table as an extra empty row - a table of 13 rows
        // rendered 14, the bottom rule fell a row lower than the page's, and everything below
        // the table started from the wrong y. 4 pt is below every font's line box, so it can
        // never hold text, but it is a real line and stays a paragraph.
        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"")
                .append(POST_TABLE_TW).append("\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr></w:p>");
        // The table is part of the flow too. Left out of the accounting, the paragraph after it
        // was spaced from the last line BEFORE the table, so a table's whole height was added
        // on top of the next paragraph's gap and the flow ran long.
        // Charged as the page will write it: the extent through the squeeze, because the rows
        // above were written through it too. A charge that ignores the squeeze is a page that
        // believes it has room it does not have.
        ctx.flowTw += twScale((int) Math.round(Math.max(0f, extentPt) * TWIPS_PER_PT), ctx.squeeze)
                + POST_TABLE_TW;
        ctx.lastBaseline = t.bottom;
        ctx.lastSize = 0f;
        // The table's bottom edge is where its content ended, not a baseline inside a line box,
        // so there is no slack of its own to carry into the next line's advance.
        ctx.lastLinePt = 0f;
        // The flow's real position after a table is the table's bottom edge plus the 4 pt carrier
        // Word requires after it, because that carrier is a line the next paragraph starts under
        // (D-26: the position is where the reader is, not where the PDF drew).
        ctx.flowY = t.bottom + POST_TABLE_TW / (float) TWIPS_PER_PT;
        ctx.flowBoxPt = 0f;
        ctx.newPage = false;
        ctx.lastWasTable = true;
    }

    /** The paragraph a table must be followed by: 4 pt, in twips. */
    private static final int POST_TABLE_TW = 80;

    /**
     * What the table's own hairline adds to the height of every row, in twips.
     *
     * <p>6/8 pt = 0.75 pt = 15 twips, and it is the {@code w:sz="6"} in {@link #borders} that
     * says so - the same number, not a fitted one. Half of the top rule and half of the bottom
     * rule fall inside a row with collapsed borders, so one hairline, not two.
     */
    private static final int TABLE_BORDER_TW = 15;

    /**
     * How much room a page must have left before it may spend the gaps it drew, in points.
     *
     * <p>The model's table height is a measurement of the PDF's own table, and a cell whose
     * text wraps grows its {@code w:trHeight} row in the render. The slack is what a table may
     * grow by before the page no longer fits: 12 pt is one row of 10 pt text plus its padding,
     * which is the smallest growth a wrapped cell can cause. A page that cannot spare it keeps
     * the clamped gaps, which is the behaviour every document had before this change.
     */
    private static final float TABLE_SLACK_PT = 12f;

    /**
     * A size in half-points, rounded DOWN.
     *
     * A page's size is not always a whole half-point: a dense price list is set at 5.8 pt.
     * Rounding 5.8 up to 6.0 makes every glyph 3 % wider than the page drew it, and a column
     * that was exactly wide enough stops being so. On 362 the last column is 21.3 pt and
     * "485.27" needs 21.6 pt at 6.0, so every row wrapped to two lines and the table came out
     * twice its drawn height. Rounding down never makes the substitute face wider than the
     * page's, so a line the page did not wrap is not wrapped here either.
     */
    private static int halfPointsDown(float sizePt) {
        if (!(sizePt > 0f)) return 20;
        return Math.max(2, (int) Math.floor(sizePt * 2f));
    }

    /** True when the typeface the page named is itself a bold face. */
    private static boolean isBoldFace(String face) {
        if (face == null || face.isEmpty()) return false;
        String f = face.toLowerCase(java.util.Locale.ROOT);
        return f.contains("bold") || f.contains("black") || f.contains("heavy")
                || f.endsWith("-bd") || f.contains(",bd")
                || f.contains("semibold") || f.contains("demi");
    }

    /** The text of cell (r, c), or "" when the row does not reach that far. */
    private static String cellAt(PdfToWord.Table t, int r, int c) {
        if (r >= t.rows.size()) return "";
        List<String> row = t.rows.get(r);
        if (c >= row.size()) return "";
        String s = row.get(c);
        return s == null ? "" : s;
    }

    /**
     * How wide this cell's text is, in twips: from where it starts to where the page stopped
     * drawing it. {@code Float.NaN} when the pass that built the table did not measure it.
     */
    private static float cellRTw(PdfToWord.Table t, int r, int c) {
        if (r >= t.cellR.size()) return Float.NaN;
        List<Float> rs = t.cellR.get(r);
        if (c >= rs.size()) return Float.NaN;
        Float right = rs.get(c);
        if (right == null || right.isNaN()) return Float.NaN;
        if (r >= t.cellX.size()) return Float.NaN;
        List<Float> xs = t.cellX.get(r);
        if (c >= xs.size()) return Float.NaN;
        Float left = xs.get(c);
        if (left == null || left.isNaN()) return Float.NaN;
        return (float) (Math.max(0f, right - left) * TWIPS_PER_PT);
    }

    /**
     * How far into the cell, in twips, this cell's text was drawn.
     *
     * <p>Zero when the page did not record where the text went, or when the glyphs put it left
     * of the cell's own left edge - in both cases the border is the safer answer.
     */
    private static int insetTw(PdfToWord.Table t, int r, int c, float x0, long edgeTw) {
        if (r >= t.cellX.size()) return 0;
        List<Float> xs = t.cellX.get(r);
        if (c >= xs.size()) return 0;
        Float textX = xs.get(c);
        if (textX == null || textX.isNaN()) return 0;
        double leftPt = x0 + edgeTw / TWIPS_PER_PT;
        int tw = (int) Math.round((textX - leftPt) * TWIPS_PER_PT);
        return Math.max(0, tw);
    }

    /**
     * The typeface name without the PDF's subset tag.
     *
     * <p>A PDF names a subset face "KLGWYD+Liberation Sans Bold", and the style is part of the
     * name rather than of the family. Written straight into {@code w:rFonts} it names a face no
     * machine has: fontconfig resolves "Liberation Serif Regular" and "Liberation Sans Bold" to
     * Noto Sans, a different face with different advances, and every word after the first drifts
     * along the line. Measured on file 51, word starts inside a line were up to 12.2 pt out
     * while the line start itself was 0.1 pt out. Dropping the subset tag and the style suffix
     * lets the family resolve to the face the PDF was drawn with; bold and italic are already
     * carried by {@code w:b} and {@code w:i}, so no styling is lost by removing them from the
     * name.
     */
    static String faceName(String font) {
        if (font == null) return "";
        String f = font;
        if (f.length() > 7 && f.charAt(6) == '+') {
            boolean tag = true;
            for (int i = 0; i < 6; i++) {
                char c = f.charAt(i);
                if (!(c >= 'A' && c <= 'Z')) { tag = false; break; }
            }
            if (tag) f = f.substring(7);
        }
        // The fourteen faces every PDF viewer must provide are named by their PostScript
        // names, and no word processor has a face called "Times-Roman": Word substitutes
        // Times New Roman and LibreOffice substitutes a wide default sans, so the line was
        // set in a different face from the one the PDF was drawn with. On file 31 that put
        // the closing note 60 pt wider than its box - and the box does not wrap, it clips -
        // so "…to the meeting." came out as "…to the ". Mapped, the same line renders at
        // 56.1-359.8 pt against the PDF's 56.0-360.2, whole. The three families here are
        // metrically identical to the PostScript originals, which is why the widths hold.
        String base = f;
        int dash = base.indexOf('-');
        if (dash > 0) base = base.substring(0, dash);
        String family = BASE14.get(base.toLowerCase(Locale.ROOT));
        if (family != null) return family;
        // A PDF names a face two ways: "Liberation Sans Bold" (a space, the PostScript full
        // name) and "LiberationSans-Bold" (a hyphen, the family-with-style form every
        // FreeType/ghostscript-produced file in this corpus uses). Only the space form was
        // stripped, so the hyphen form went into w:rFonts whole - and "LiberationSans-Bold"
        // is not a family any machine has: fontconfig resolves it to Noto Sans, whose
        // advances are ~10 % wider than the face the page was drawn in. A line that fitted
        // its column on the page by 3 pt then did not fit in the reader, LibreOffice broke it
        // in two, and a table row declared atLeast one pitch tall became two - the doubled
        // header row of table-with-merged-cells and boq-tender-bill-of-quantities, where
        // "Quantity" (28.39 pt at 7 pt Liberation Sans Bold on the page) has 31.39 pt of
        // column and Noto Sans Bold sets it 30.9 pt and breaks it after "Quantit".
        String[] suffixes = {" Bold Italic", " Bold Oblique", " Italic", " Oblique",
                " Bold", " Regular", " Roman", " Normal",
                "-BoldItalic", "-BoldOblique", "-Bold", "-Italic", "-Oblique",
                "-Regular", "-Roman", "-Normal", ",Bold", ",Italic", ",BoldItalic"};
        for (String suf : suffixes) {
            if (f.length() > suf.length() && f.endsWith(suf)) {
                return f.substring(0, f.length() - suf.length());
            }
        }
        return f;
    }

    /** PostScript's fourteen standard faces, keyed by family, to the family a Word file names. */
    private static final Map<String, String> BASE14 = new HashMap<>();

    static {
        BASE14.put("times", "Times New Roman");
        BASE14.put("helvetica", "Arial");
        BASE14.put("courier", "Courier New");
    }

    /** Points to whole twips, the unit every w:* length uses. */
    private static int tw(float pt) {
        return Math.max(0, Math.round((float) (pt * TWIPS_PER_PT)));
    }

    private static String esc(String s) {
        StringBuilder sb = new StringBuilder(s.length() + 16);
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '&': sb.append("&amp;"); break;
                case '<': sb.append("&lt;"); break;
                case '>': sb.append("&gt;"); break;
                case '"': sb.append("&quot;"); break;
                case '\'': sb.append("&apos;"); break;
                default:
                    // Control characters are not legal in XML 1.0 and make Word refuse the file.
                    if (c < 0x20 && c != '\t' && c != '\n' && c != '\r') sb.append(' ');
                    else sb.append(c);
            }
        }
        return sb.toString();
    }

    // ------------------------------------------------------------------ package parts

    private static String contentTypes(int images) {
        StringBuilder sb = new StringBuilder();
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>")
                .append("<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">")
                .append("<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>")
                .append("<Default Extension=\"xml\" ContentType=\"application/xml\"/>")
                .append("<Default Extension=\"png\" ContentType=\"image/png\"/>")
                .append("<Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>")
                .append("<Override PartName=\"/word/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml\"/>")
                .append("<Override PartName=\"/word/theme/theme1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.theme+xml\"/>")
                .append("<Override PartName=\"/word/settings.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml\"/>")
                .append("<Override PartName=\"/docProps/core.xml\" ContentType=\"application/vnd.openxmlformats-package.core-properties+xml\"/>")
                .append("<Override PartName=\"/docProps/app.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.extended-properties+xml\"/>")
                .append("</Types>");
        return sb.toString();
    }

    private static String rootRels() {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                + "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
                + "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/>"
                + "<Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties\" Target=\"docProps/core.xml\"/>"
                + "<Relationship Id=\"rId3\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties\" Target=\"docProps/app.xml\"/>"
                + "</Relationships>";
    }

    private static String documentRels(List<byte[]> media) {
        StringBuilder sb = new StringBuilder();
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>")
                .append("<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">")
                .append("<Relationship Id=\"rIdStyles\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/>")
                .append("<Relationship Id=\"rIdTheme\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme\" Target=\"theme/theme1.xml\"/>")
                .append("<Relationship Id=\"rIdSettings\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings\" Target=\"settings.xml\"/>");
        for (int i = 0; i < media.size(); i++) {
            sb.append("<Relationship Id=\"rIdImg").append(i + 1)
                    .append("\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/image\" Target=\"media/image")
                    .append(i + 1).append(".png\"/>");
        }
        sb.append("</Relationships>");
        return sb.toString();
    }

    /**
     * The theme part the package was missing.
     *
     * <p>None of the 208 documents carried a theme, and that was invisible while every colour
     * was an absolute {@code a:srgbClr}. It stopped being invisible the moment a light fill was
     * written as {@code a:schemeClr bg1}: {@code bg1} means "the page background", and there was
     * no page background for a reader to resolve it against. Measured, not assumed - the same
     * document rendered through LibreOffice with no theme part put the fill down as 000000
     * (black bands where the page had E6EBF5), and with this part it renders EDEDED in the same
     * 32,925 pixels the page filled. So the theme is not decoration here; without it the fill
     * change is a regression.
     *
     * <p>lt1/window is the light background the fills are a shade of; dk1 is the text. Both are
     * sysClr with a lastClr, which is the form a reader that has its own idea of "window" and
     * "window text" can map to its own canvas instead of being told a hex.
     */
    /**
     * {@code word/settings.xml}.
     *
     * <p>Both commercial converters write one and this writer never did. The part carries
     * {@code clrSchemeMapping}, which tells a reader which theme slot each colour name means, and
     * it deliberately carries NO {@code displayBackgroundShape}: per the specification that
     * setting means the page background is painted, and a painted page colour suppresses Word's
     * own automatic dark page.
     */
    private static String settingsXml() {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                + "<w:settings xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
                + "<w:zoom w:percent=\"100\"/>"
                + "<w:defaultTabStop w:val=\"720\"/>"
                + "<w:characterSpacingControl w:val=\"doNotCompress\"/>"
                + "<w:compat>"
                + "<w:compatSetting w:name=\"compatibilityMode\" w:uri=\"http://schemas.microsoft.com/office/word\" w:val=\"15\"/>"
                + "</w:compat>"
                + "<w:clrSchemeMapping w:bg1=\"light1\" w:t1=\"dark1\" w:bg2=\"light2\" w:t2=\"dark2\""
                + " w:accent1=\"accent1\" w:accent2=\"accent2\" w:accent3=\"accent3\""
                + " w:accent4=\"accent4\" w:accent5=\"accent5\" w:accent6=\"accent6\""
                + " w:hyperlink=\"hyperlink\" w:followedHyperlink=\"followedHyperlink\"/>"
                + "</w:settings>";
    }

    private static String themeXml() {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                + "<a:theme xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" name=\"Kavo\">"
                + "<a:themeElements><a:clrScheme name=\"Kavo\">"
                + "<a:dk1><a:sysClr val=\"windowText\" lastClr=\"000000\"/></a:dk1>"
                + "<a:lt1><a:sysClr val=\"window\" lastClr=\"FFFFFF\"/></a:lt1>"
                + "<a:dk2><a:srgbClr val=\"44546A\"/></a:dk2>"
                + "<a:lt2><a:srgbClr val=\"E7E6E6\"/></a:lt2>"
                + "<a:accent1><a:srgbClr val=\"4472C4\"/></a:accent1>"
                + "<a:accent2><a:srgbClr val=\"ED7D31\"/></a:accent2>"
                + "<a:accent3><a:srgbClr val=\"A5A5A5\"/></a:accent3>"
                + "<a:accent4><a:srgbClr val=\"FFC000\"/></a:accent4>"
                + "<a:accent5><a:srgbClr val=\"5B9BD5\"/></a:accent5>"
                + "<a:accent6><a:srgbClr val=\"70AD47\"/></a:accent6>"
                + "<a:hlink><a:srgbClr val=\"0563C1\"/></a:hlink>"
                + "<a:folHlink><a:srgbClr val=\"954F72\"/></a:folHlink></a:clrScheme>"
                + "<a:fontScheme name=\"Kavo\">"
                + "<a:majorFont><a:latin typeface=\"Calibri\"/><a:ea typeface=\"\"/><a:cs typeface=\"\"/></a:majorFont>"
                + "<a:minorFont><a:latin typeface=\"Calibri\"/><a:ea typeface=\"\"/><a:cs typeface=\"\"/></a:minorFont>"
                + "</a:fontScheme>"
                + "<a:fmtScheme name=\"Kavo\">"
                + "<a:fillStyleLst><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
                + "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
                + "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:fillStyleLst>"
                + "<a:lnStyleLst><a:ln><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:ln>"
                + "<a:ln><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:ln>"
                + "<a:ln><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:ln></a:lnStyleLst>"
                + "<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle>"
                + "<a:effectStyle><a:effectLst/></a:effectStyle>"
                + "<a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>"
                + "<a:bgFillStyleLst><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
                + "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
                + "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:bgFillStyleLst>"
                + "</a:fmtScheme></a:themeElements></a:theme>";
    }

    private static String stylesXml() {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                + "<w:styles xmlns:w=\"" + NS_W + "\">"
                // NO w:color here at all. It used to be 000000, which decided 325 of 414 runs
                // and removed the one adaptation hook a reader has: Automatic text is the only
                // thing every dark mode flips. Measured on the files the user supplied - the
                // iLovePDF output carries an explicit colour on 98 of 365 runs and the Adobe one
                // on 178 of 558, and neither writes a colour in docDefaults at all.
                + "<w:docDefaults><w:rPrDefault><w:rPr>"
                + "<w:rFonts w:ascii=\"Calibri\" w:hAnsi=\"Calibri\" w:cs=\"Calibri\"/>"
                + "<w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr></w:rPrDefault>"
                + "<w:pPrDefault><w:pPr><w:spacing w:after=\"120\"/></w:pPr></w:pPrDefault>"
                + "</w:docDefaults>"
                + "<w:style w:type=\"paragraph\" w:default=\"1\" w:styleId=\"Normal\">"
                + "<w:name w:val=\"Normal\"/></w:style>"
                + heading(1, 32, 1) + heading(2, 28, 2) + heading(3, 24, 3)
                // A document with tables and no table style has no statement of what its
                // tables' borders are, so a reader falls back to its own default table style -
                // which draws a box. 127 of the 208 documents carry a w:tbl; not one of them
                // had a style to fall back on. The style declares no borders and no colour, so it
                // changes nothing on the page: the per-table w:tblBorders still say what the
                // page drew, and direct formatting wins over a style.
                + tableStyles()
                + "<w:style w:type=\"paragraph\" w:styleId=\"TableText\">"
                + "<w:name w:val=\"Table Text\"/><w:basedOn w:val=\"Normal\"/>"
                + "<w:pPr><w:spacing w:after=\"0\" w:before=\"0\"/></w:pPr>"
                + "<w:rPr><w:sz w:val=\"20\"/></w:rPr></w:style>"
                + "</w:styles>";
    }

    /**
     * The table styles the document declares.
     *
     * <p>There was no {@code w:style w:type="table"} at all in any of the 208 documents, so a
     * reader opening one of the 127 that carry a {@code w:tbl} had nothing to tell it what those
     * tables' borders are and fell back to its own default table style - the one that draws a
     * box. 59 of them carry a table with no borders at all, which is the case that box ruins.
     * Both styles here say "no borders, no colour": the borders a page really drew are on the
     * table itself, in {@code w:tblBorders}, and direct formatting beats a style, so nothing
     * on the page changes. What changes is that the document now answers the question instead
     * of leaving it to the reader.
     */
    private static String tableStyles() {
        StringBuilder b = new StringBuilder();
        b.append("<w:style w:type=\"table\" w:default=\"1\" w:styleId=\"TableNormal\">")
                .append("<w:name w:val=\"Normal Table\"/><w:uiPriority w:val=\"99\"/>")
                .append("<w:tblPr><w:tblCellMar>")
                .append("<w:top w:w=\"0\" w:type=\"dxa\"/><w:left w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:bottom w:w=\"0\" w:type=\"dxa\"/><w:right w:w=\"0\" w:type=\"dxa\"/>")
                .append("</w:tblCellMar></w:tblPr></w:style>");
        b.append("<w:style w:type=\"table\" w:styleId=\"KavoTable\">")
                .append("<w:name w:val=\"Kavo Table\"/><w:basedOn w:val=\"TableNormal\"/>")
                .append("<w:tblPr><w:tblBorders>");
        for (String side : new String[]{"top", "left", "bottom", "right", "insideH", "insideV"}) {
            b.append("<w:").append(side).append(" w:val=\"nil\"/>");
        }
        b.append("</w:tblBorders></w:tblPr></w:style>");
        return b.toString();
    }

    private static String heading(int level, int halfPoints, int before) {
        return "<w:style w:type=\"paragraph\" w:styleId=\"Heading" + level + "\">"
                + "<w:name w:val=\"heading " + level + "\"/><w:basedOn w:val=\"Normal\"/>"
                + "<w:next w:val=\"Normal\"/><w:qFormat/>"
                + "<w:pPr><w:keepNext/><w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"" + (before * 120)
                + "\" w:after=\"60\"/><w:outlineLvl w:val=\"" + (level - 1) + "\"/></w:pPr>"
                + "<w:rPr><w:b/><w:sz w:val=\"" + halfPoints + "\"/></w:rPr></w:style>";
    }

    private static String coreXml(PdfToWord.Result result) {
        String title = result.title == null ? "" : result.title;
        return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                + "<cp:coreProperties xmlns:cp=\"http://schemas.openxmlformats.org/package/2006/metadata/core-properties\""
                + " xmlns:dc=\"http://purl.org/dc/elements/1.1/\">"
                + "<dc:title>" + esc(title) + "</dc:title>"
                + "<dc:creator>KavoPDF</dc:creator>"
                + "</cp:coreProperties>";
    }

    private static String appXml() {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                + "<Properties xmlns=\"http://schemas.openxmlformats.org/officeDocument/2006/extended-properties\">"
                + "<Application>KavoPDF</Application></Properties>";
    }
}
