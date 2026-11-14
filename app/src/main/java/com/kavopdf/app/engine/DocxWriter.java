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
    private static final float ASCENT =
            Float.parseFloat(System.getProperty("p2w.ascent", "0.92"));
    private static final boolean ANCHOR_KEEPS_FLOW =
            !"0".equals(System.getProperty("p2w.anchorkeep"));
    /** docPr ids for shapes start above the picture ids so the two never collide. */
    private static final int SHAPE_ID_BASE = 100000;
    /** Line box height as a multiple of the font size. Generous: a tight exact height clips. */
    private static final float LINE_FACTOR = 1.15f;
    /**
     * The line box a flow line is written with, as a multiple of its font size: a HAIRLINE.
     *
     * <p>Google Docs and Word read {@code w:line} differently, and only one value of it means
     * the same thing to both. Word (and LibreOffice) advance by {@code w:before + w:line/20}.
     * Google advances by {@code w:before + max((w:line/240) * lineHeight(face, size), 0.069 *
     * size)} - a MULTIPLE OF THE SUBSTITUTE FACE'S LINE HEIGHT with a floor at 0.069 em
     * (calibrate.py: 0.9583 at 10 pt Arial, 1.049 Courier New, 1.170 Times, 1.223 Helvetica,
     * 1.277 Liberation Serif). So an {@code w:line} written as a fraction of the em - the
     * {@link #LINE_FACTOR} box this file used to emit - is charged {@code r} times over by
     * Google for a face whose {@code r} is not 1.15, and the error is
     * {@code size * (0.0958 * r * size - 1.15)} per line: -2.2 pt at 7.4 pt (the corpus
     * median run size), 0.0 at 10 pt, +1.25 at 11 pt. One sign, every line, so it accumulates
     * down the page: 20_line_placement measures that sum, and a page of uniform body text
     * exceeds one pitch within about five lines whatever its layout is.
     *
     * <p>The floor is the only part of Google's charge that does not follow the face. Put the
     * box inside the floor and BOTH renderers charge exactly 0.069 em:
     * {@code (w:line/240) * r * size <= 0.069 * size} for every measured {@code r} while
     * {@code w:line <= 16.56/1.277 = 12.97} twips, and {@code w:line/20 = 0.069 * size} when
     * {@code w:line = 1.38 * size}. So {@code w:line = 1.38 * size} is the one box that makes
     * the two agree, and the gap ({@code w:before}) carries the rest of the pitch.
     *
     * <p>NOT A CONSTANT 12 TWIPS. A constant box is exact for Google at every size and wrong
     * for Word/LO by {@code 0.6 - 0.069 * size} per line, which is what made an earlier
     * attempt at this class worse under LibreOffice (median |dy| 1.22 -> 2.09 pitch). Scaling
     * the box with the type is what makes it right in both.
     *
     * <p>Above {@code size = 12/r} the floor stops binding and Google's charge becomes
     * quadratic in the size, so the two cannot be made to agree there; the residue is
     * {@code 0.069 * size * (r * size / 12 - 1)}, 0.17 pt a line at 12 pt, and it is BOUNDED
     * rather than cumulative because the type size is.
     */
    private static final float HAIRLINE_EM = 0.069f;
    /**
     * WHICH LINE BOX A PARAGRAPH IS WRITTEN WITH - the one knob this experiment turns.
     *
     * <p>Two constructs place a flow line, and they are not the same question:
     * <ul>
     *   <li>{@code w:line = 1.38*size} + {@code lineRule="exact"} - the hairline above. Word and
     *       LibreOffice honour it exactly; Google Docs does not implement "exact" and reads
     *       {@code w:line} as 240ths of the face's line height, so it charges
     *       {@code (1.38*size/240) * r * size} - quadratic in the type size.</li>
     *   <li>{@code w:line="240"} + {@code lineRule="auto"} - the reader's own single line
     *       height, {@code r * size}, with the remainder of the pitch in {@code w:before}.
     *       Linear in the size, so it cannot compound by size; but {@code r} is the SUBSTITUTE
     *       face's ratio, so it is only right for the face the reader actually picks.</li>
     * </ul>
     *
     * <p>The transform is exact and intent-preserving: the engine solves a gap so that
     * {@code before + line/20} is the pitch the page drew. Auto keeps that advance and only
     * moves the remainder into {@code w:before}:
     * {@code before' = before + line/20 - AUTO_LINE_EM*size}. The engine's own accounting
     * (resync, fitPage) is left on the exact model, so the only variable between the two
     * builds is the construct - not the placement.
     *
     * <p>Modes: {@code -Dp2w.lineRule=exact} (default, HEAD), {@code auto} (flow AND cells),
     * {@code autoflow} (flow only; cells and anchored text boxes keep exact).
     */
    private static final int LINE_MODE = lineMode();
    private static int lineMode() {
        String v = System.getProperty("p2w.lineRule", "exact");
        if ("auto".equals(v)) return 2;
        if ("autoflow".equals(v)) return 1;
        return 0;
    }
    /** The reader's own single line height, in em, for the face it substitutes. */
    private static final float AUTO_LINE_EM =
            Float.parseFloat(System.getProperty("p2w.autoEm", "1.15"));
    /** Paragraphs whose auto remainder had to be floored at zero: leading tighter than 1.15 em. */
    private static int autoFloorHits = 0;
    private static boolean autoFlowLines() { return LINE_MODE != 0; }
    private static boolean autoCellBoxes() { return LINE_MODE == 2; }

    /** One paragraph's {@code w:spacing}, in the construct the mode selects. */
    private static String spacing(int beforeTw, int lineTw, float size, boolean auto, boolean pageFirst) {
        if (!auto) {
            return "<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\""
                    + beforeTw + "\" w:after=\"0\" w:line=\"" + lineTw
                    + "\" w:lineRule=\"exact\"/>";
        }
        int boxTw = (int) Math.round(AUTO_LINE_EM * Math.max(1f, size) * TWIPS_PER_PT);
        long b = (long) beforeTw + lineTw - boxTw;
        // The PAGE'S FIRST LINE is the one line whose baseline is not carried by the pitch
        // above it: it is placed absolutely, at `before` + LINE_BASE * box. Auto's box is
        // 1.15 em against the hairline's 0.069 em, so at the same `before` its baseline
        // lands LINE_BASE * (box - line) lower - measured on the 211-document corpus as a
        // -3.1 pt median shift of the first line of every page and a -1.9 pt median on the
        // lines below it, which is what 18_displacement was reading. Give it back here so
        // the first line stays on its own y; the pitch below it is set by the NEXT
        // paragraph's own before, so nothing else moves.
        if (pageFirst) b += Math.round((1f - LINE_BASE) * (boxTw - lineTw));
        if (b < 0) { b = 0; autoFloorHits++; }
        return "<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\""
                + b + "\" w:after=\"0\" w:line=\"240\" w:lineRule=\"auto\"/>";
    }

    /** How many paragraphs the auto construct could not place without a floor. */
    public static int autoFloorHits() { return autoFloorHits; }

    /** Anchored boxes whose offset was pulled back onto the page this write. See anchorShape. */
    private static int anchorClamped;

    public static int anchorClampedHits() { return anchorClamped; }

    /**
     * How far a shape's fill may sit from the page it is painted on and still BE the page.
     *
     * <p>Measured as the largest per-channel distance from white paper, 0..255. A fill inside
     * this tolerance is a white patch on a dark canvas and paints nothing a reader can see on a
     * light one, so omitting it costs nothing in either mode - that is the whole of the D-23
     * device fix and it is kept.
     *
     * <p>It replaces an HSL-lightness test at 0.72, which asked the wrong question. Lightness
     * says how light a colour is, not how close to the page: C9C9C9 is L=0.788, i.e. deep inside
     * the old rule, and sits 54 levels off the page - a mid-grey table band, not a white patch.
     * Measured over corpus-v1's 3,192 shape fills, the old rule dropped 402 fills in 87
     * documents, and 202 of those 402 are pale tints that carry a word inside them - a cell's
     * shading or a highlight, never a decorative band. Every one of the 402 at 9 levels or more
     * from the page carries text; 178 of the 200 pure-white ones carry nothing. The two classes
     * are disjoint on "does this fill do a job", and distance from the page is the axis that
     * separates them.
     *
     * <p>8 is the just-noticeable distance for a flat area of this size: #F7F7F7 against #FFFFFF
     * is dE00 1.1, below the threshold at which a reader sees an edge.
     */
    private static final int PAGE_TOL = 8;
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
     * How far the centre of a glyph's INK sits from its own baseline, in em.
     *
     * <p>The counterpart of {@link #LINE_BASE} for the perpendicular axis, and the one number
     * a turned line needs that a horizontal one does not: an upright run's ink is a fixed
     * distance ABOVE its baseline, so a run copied from a line the page drew at another angle
     * has to be lifted by the difference between the two frames' perpendiculars (see
     * {@code stampBox}). It is a property of the face, not of the size: a face's ascent less
     * its descent, halved.
     *
     * <p>Calibrated on the two turned cases where the answer is not mixed up with the tilt.
     * 04's upside-down stamp needs exactly twice this - its ink hangs below the baseline where
     * the copy's sits above - and measures 10.90 pt at 17 pt, so k = 0.320. 03's 90-degree
     * stamp needs it once and measures 45.60 against a half-length of 45.2, so k = 0.32. The
     * glyph-box figure is the same number from the other side: 04's own upright heading at
     * 13 pt has its ink centre 4.45 pt above its baseline, 0.342 em, and the substituted face
     * LibreOffice renders the copy in measures 0.30 em. A stamp that the page draws
     * horizontally is unaffected at any k - the term is multiplied by (1 - cos 0) = 0.
     */
    private static final float INK_MID_EM = 0.32f;

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
     * Whether a line the page put ABOVE the flow is anchored at its own y instead of being
     * written with no gap at all.
     *
     * <p>This is the same rule the file already applies to a gap WIDER than the cap: a gap the
     * flow cannot hold is not a gap, it is a position, and the line is anchored where the page
     * drew it. A NEGATIVE gap is the same statement with the sign reversed, and it used to be
     * written as {@code w:before="0"} - the line then landed wherever the flow happened to be,
     * low by the overshoot, and took the next line with it. On
     * 69_two_col_legal_numbered_clauses one line landed 16.9 pt low and dragged four more with
     * it, and again at 41.1 pt.
     *
     * <p>An anchored line is a text box, so it is not free: it does not reflow and Google Docs
     * will not let it be edited in place. That is why it is the fallback rather than the rule,
     * why a line inside a column cell is left alone (a page-anchored box written from inside a
     * cell lands outside it), and why the miss has to reach {@link #ZERO_GAP_FLOOR_PT} before a
     * box is worth writing: below that the two placements are the same place.
     */
    static final boolean ZERO_GAP_ANCHOR = !"false".equals(System.getProperty("p2w.zganchor"));

    /**
     * The miss, in points, that makes a text box worth writing.
     *
     * <p>Measured, not guessed. A line anchored in a text box is placed from the box's top edge,
     * so it lands a little over a point from where the flow would have put it (measured on
     * 69_two_col_legal_numbered_clauses: 155.0 -> 153.7 pt and 306.8 -> 305.4 pt), and the box
     * does not advance the flow. Below this miss the two placements are the same place and the
     * box buys nothing: at 1.0 pt, five lines of 78_mixed_english_devanagari_line - whose worst
     * miss is 3.6 pt - became text boxes and four of them landed on the line above, which is a
     * NEW 26_text_overlap failure paid for 3 pt of position. At 6 pt that document is untouched.
     * 6 pt is about half a line box for the 10-12 pt text this corpus is written in, which is
     * where a miss stops being rounding and starts being a line in the wrong place.
     */
    static final float ZERO_GAP_FLOOR_PT =
            Float.parseFloat(System.getProperty("p2w.zgfloor", "6.0"));

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

    /**
     * The line height written into a table cell that holds no text - one point, which is
     * enough for the paragraph OOXML requires a cell to contain and nothing more.
     *
     * <p>Such a cell used to be given the WHOLE row height as its line
     * ({@code cellBoxTw = rowLineTw}). That writes the row's {@code w:trHeight} a second
     * time, inside the cell, and the renderer then takes the row as
     * {@code max(trHeight, cell content)} - so the duplicate is charged as content on top
     * of the height the row already declares. Measured on
     * {@code itr-computation-with-slab-table}, whose 20-row slab table is the only table in
     * the 211 with empty cells carrying a real line: every one of its 20 rows came back
     * 0.475 pt taller than its own {@code w:trHeight} - 9.50 pt on a page that is 9.7 pt
     * over - and the page's measured line pitch read 18.7 pt against the source's 18.4.
     * With this constant the same document renders 922.30 -> 912.80 pt and its rows land
     * on their declared heights. The row is still held by its own {@code w:trHeight}, so
     * no row collapses: 43 rows still occupy 735.05 pt of the page.
     */
    private static final int EMPTY_CELL_LINE_TW = 20;

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
    /** The tokens {@link #flowTwOf} needs to tell a nested table's own height from its cells'. */
    private static final String TBL_OPEN = "<w:tbl>";
    private static final String TBL_CLOSE = "</w:tbl>";
    private static final String TRHEIGHT = "w:trHeight w:val=\"";
    private static int spacingTw(CharSequence xml) {
        int sum = 0;
        int depth = 0;              // inside a w:tbl
        int i = 0;
        int n = xml.length();
        while (i < n) {
            if (startsWith(xml, "<w:tbl>", i)) {
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
                if (depth == 0) sum += digits(xml, j);
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

    /**
     * Takes {@code excessTw} out of the page's own gaps, largest first, so the page ends where
     * the paper does.
     *
     * <p>The budget guard in {@link #fitPage} already gives up the gap of a line it cannot place,
     * then shortens that line's box, and only then lets the page overrun. That leaves a residue
     * the guard cannot reach: once {@code flowTw} has arrived at the budget, every further line
     * on the page has {@code before = 0} already, so there is nothing left for it to give up -
     * and the page is written one or two twips too tall, which a renderer answers with a page
     * break. On {@code bank-statement-5-pages} that residue was 24 twips (1.2 pt) on a 841.9 pt
     * sheet, and LibreOffice turned each of its five pages into two: 5 pages in, 10 out, and
     * nine checks lost (01_page_count, 24_page_breaks, 27_text_off_page, 55_orientation_mix,
     * 04_chars_missing, 17_matched_runs, 32_stroke_lines, 59_shape_anchor,
     * 60_text_column_right_edge).
     *
     * <p>Shaving the residue off the page's LARGEST gap is the cheapest way to end at the paper's
     * edge: the gap it comes out of is white space the page left (on bank-statement, 278 pt
     * between the transaction table and the closing-balance line), so 1.2 pt of it is invisible,
     * where a page break is a whole sheet. Cell paragraphs and text boxes are skipped for the
     * same reason {@link #spacingTw} skips them: a row carries its own height and a text box is
     * placed at a y, so neither is the page's flow.
     *
     * @return the twips still over the paper, 0 when the page now fits
     */
    private static int shaveToFit(StringBuilder xml, int excessTw) {
        while (excessTw > 0) {
            int best = -1, bestVal = 0, depth = 0, i = 0, n = xml.length();
            while (i < n) {
                if (startsWith(xml, "<w:tbl>", i)) {
                    depth++;
                    i += 7;
                } else if (startsWith(xml, "</w:tbl>", i)) {
                    if (depth > 0) depth--;
                    i += 8;
                } else if (startsWith(xml, "<w:txbxContent>", i)) {
                    depth++;
                    i += 15;
                } else if (startsWith(xml, "</w:txbxContent>", i)) {
                    if (depth > 0) depth--;
                    i += 16;
                } else if (startsWith(xml, BEFORE, i)) {
                    int j = i + BEFORE.length();
                    if (depth == 0) {
                        int v = digits(xml, j);
                        if (v > bestVal) {
                            bestVal = v;
                            best = j;
                        }
                    }
                    i = j;
                } else {
                    i++;
                }
            }
            if (best < 0 || bestVal <= 0) break;
            int take = Math.min(excessTw, bestVal);
            int left = bestVal - take;
            String was = Integer.toString(bestVal), now = Integer.toString(left);
            if (was.length() != now.length()) {
                xml.replace(best, best + was.length(), now);
            } else {
                for (int k = 0; k < was.length(); k++) xml.setCharAt(best + k, now.charAt(k));
            }
            excessTw -= take;
        }
        return Math.max(0, excessTw);
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
            //
            // AND THE CELL IS NOT CHARGED TO THE PAGE AT ALL. It used to be: every cell line
            // added its own height to ctx.flowTw, and then table() closed with
            // flowTw = max(flowTw, rowEndPt) - so the page was charged the SUM of a row's
            // cells and then had the row's real height taken out of the same ledger. The
            // columns of a row stand SIDE BY SIDE; only the tallest of them advances the page,
            // and that is exactly what rowTw already is (flowTwOf over each cell's XML, maxed).
            // Charging them as well put the page's flow below the table by the sum of the
            // other columns, and every line after the table was then placed against a page
            // that was further down than it really was.
            //
            // Measured on the two documents where a footer follows a layout table:
            // 12_stamp_across_page_break page 2 charged 12594 twips against a table whose last
            // row ends at 490.1 pt (9802 twips) - 139.6 pt of other-column height - and the
            // footer's gap to its own y (798.8) was clamped by fitPage from 6341 twips to 4231,
            // landing it at 693.3. mutual-fund-statement page 2 charged 13510 against a row
            // ending at 411.8 (8236) - 263.7 pt - and its footer landed at 548.8 instead of
            // 811.4. Neither is a placement defect: the gap was correct and the budget was
            // wrong.
            int b2 = twScale(beforeTw, ctx.squeeze);
            int l2 = twScale(lineTw, ctx.squeeze);
            if ("1".equals(System.getProperty("p2w.colcharge"))) ctx.flowTw += b2 + l2;
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
        // What the flow could not express, carried out where the pipeline can see it. A gap
        // that could not be written is not a rendering detail: the line lands somewhere the
        // page never put it, and nothing in the .docx says so.
        result.report.zeroGap = ctx.zeroGap;
        result.report.zeroGapAnchored = ctx.zeroGapAnchored;
        result.report.zeroGapInCol = ctx.zeroGapInCol;
        result.report.zeroGapWorstPt = ctx.zeroGapWorstPt;
        result.report.zeroGapNoRoom = ctx.zeroGapNoRoom;
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
        /**
         * Lines this document wrote with NO gap above them because the page put them above
         * where the flow already was - the gap would have been negative and a flow cannot go
         * backwards. Counted so the pipeline can see the class instead of inferring it from a
         * render: a zero gap is invisible in the .docx, it is a missing number.
         */
        int zeroGap;
        /** How far above the flow those lines were, summed and worst-case, in points. */
        float zeroGapPt;
        float zeroGapWorstPt;
        /** How many of them were inside a column cell, where a text box cannot reach. */
        int zeroGapInCol;
        /** How many were anchored at their own y by the rule this replaces the zero with. */
        int zeroGapAnchored;
        /**
         * Lines that miss their own y by more than the floor but could not be anchored, because
         * the page left no room between them and the line above - that line is itself low, so a
         * box here would land on top of it. Counted, so what the rule still cannot reach is a
         * number rather than an impression.
         */
        int zeroGapNoRoom;
        /** Cell paragraphs the renderer will wrap, i.e. that were charged more than one box. */
        int cellWrapHits;
        /** The shapes on the page being written, so a stamp can find its own outline. */
        java.util.List<Shape> curShapes;
        /**
         * The lines of each stamp, keyed by the shape that carries that stamp's frame.
         *
         * <p>A stamp is written as ONE object - its frame and every line of its text inside one
         * text box - so the writer has to know, when it meets the first of those lines, which
         * other lines belong with it. That is what this map answers, and it is rebuilt for every
         * page and every pass (see {@link #groupStamps}).
         */
        java.util.Map<Shape, java.util.List<PdfToWord.Box>> stampText =
                new java.util.HashMap<>();
        /** The stamps already written on this pass, so a stamp is written once. */
        java.util.Set<Shape> stampWritten = new java.util.HashSet<>();
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
         * How far AHEAD of the model the renderer already is inside the cell being written, in
         * twips, because it wrapped paragraphs the model budgeted one line box for.
         *
         * <p>A cell is a fixed-width rectangle and the page's line may be wider than it, so the
         * renderer breaks that one paragraph into N lines and charges N line boxes. The model
         * charges one ({@code w:line} is the hairline - see {@link #hairlinePt}). The excess is
         * permanent and it is CUMULATIVE down the cell, because each paragraph's gap is solved
         * from the page's own pitch ({@code b.y - lastBaseline}) and so cannot see it. Paying it
         * out of the next paragraph's gap is what puts that paragraph back on its own y.
         *
         * <p>This is the same fault {@link #table} already counts with {@code wrapsAt} (:5266);
         * the layout table {@link #columnPage} builds never did, and it is where every
         * para-in-column displacement in corpus-v1 comes from.
         */
        int wrapDebtTw;
        /** The same debt, summed over the cell, so the row can be as tall as what it writes. */
        int wrapDebtTotalTw;
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
        /**
         * True when the block about to be written is followed by a paragraph of the page's own.
         *
         * <p>A table needs a carrier paragraph after it only when the next thing is NOT a
         * paragraph - another table, or the end of the page, where Word would otherwise insert
         * one it did not place. Where the page's own next block IS a paragraph, that paragraph
         * already is the carrier Word wants, and writing a second one charges the page 4 pt of
         * nothing (see {@link #POST_TABLE_TW}).
         */
        boolean nextIsPara;
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
                // THE MEASURING PASS IS THE FIRST CANDIDATE, not the fallback. It used to be
                // bestXml = null, and null meant "no attempt beat the measuring pass", so pg
                // kept whatever the LAST attempt wrote - while writtenTw still held the
                // measuring pass's height. The two are not the same page: an attempt is written
                // to pageBudgetTw - overheadTw, the measuring pass to pageBudgetTw, and they
                // give up different gaps. Measured on bank-statement-5-pages: writtenTw 16860,
                // the page actually in pg 16902 - the writer believed a page 42 twips shorter
                // than the one it emitted, so the guard could never see the overrun it was
                // supposed to remove and the renderer answered with a page break.
                String bestXml = pg.toString();
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
            // THE FIT RESERVE IS ONLY SPENT BY A PAGE THAT CANNOT FIT.
            //
            // A reserve taken off every page's budget was the first attempt, and it is wrong:
            // it clamps the gap of any page that comes within the reserve of the paper, whether
            // or not that page would have overrun, and that cost two documents a check each
            // (341_shipping_manifest 18_displacement, academic-paper-ieee-2col-abstract
            // 26_text_overlap) for pages that were never in danger. A page whose flow ends below
            // pageBudgetTw - FIT_RESERVE_TW is written exactly as it was before; only a page that
            // has to be made to fit pays for the reserve.
            //
            // 300 twips (15 pt) is measured, not guessed. With the column charge corrected,
            // bank-statement-5-pages ends 24 twips over the paper and LibreOffice answers with a
            // page break on all five sheets (5 pages in, 10 out). Swept on that document with
            // the reserve applied to every page: 2, 12, 24, 48, 96 and 144 twips all still
            // render 10 pages, 300 renders 5. So the renderer needs more than 7.2 pt of slack on
            // a sheet the model calls full, and 15 pt is the first value that holds.
            int fitReserveTw = Integer.parseInt(System.getProperty("p2w.fitreserve", "0"));
            if (writtenTw > pageBudgetTw - fitReserveTw
                    && !"1".equals(System.getProperty("p2w.noshave"))) {
                // Still over the paper after squeezing: the residue is the part of the flow the
                // guard could not give up, because it had already spent every gap it was allowed
                // to. Take it out of the page's own largest gaps instead of letting a renderer
                // answer with a page break.
                int over = writtenTw - (pageBudgetTw - fitReserveTw);
                int left = shaveToFit(pg, over);
                writtenTw = spacingTw(pg);
                if (System.getProperty("p2w.debugFlow") != null) {
                    System.err.println("SHAVE over=" + over + " left=" + left
                            + " writtenTw=" + writtenTw);
                }
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
        // Which of the page's turned lines belong to one stamp, and which shape carries its
        // frame. Rebuilt here rather than once per page because the page is written several
        // times by the budget guard, and each pass must write every stamp again.
        groupStamps(page, ctx.curShapes, ctx);
        if (columnPage(sb, page, ctx, pw)) return;
        // Which of this page's short lines are drawn beside a table rather than in its text, and
        // so must not charge the flow. Decided from the page's own geometry before anything is
        // written, so both of the budget guard's passes see the same answer (see pinShortParas).
        pinShortParas(page);
        for (int bi = 0; bi < page.blocks.size(); bi++) {
            Object block = page.blocks.get(bi);
            ctx.nextIsPara = bi + 1 < page.blocks.size()
                    && page.blocks.get(bi + 1) instanceof PdfToWord.Para;
            emitBlock(sb, block, ctx);
        }
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

        // A CONTENT TABLE INSIDE A COLUMN IS COLUMN CONTENT, NOT A BAND ABOVE THE COLUMNS.
        //
        // The band's top is the first baseline on which TWO columns are both set, and a table
        // contributes no baseline to that test: it is one block, not a paragraph, so its rows
        // never appear in `shared`. On table-inside-two-column-page the right column's content
        // table starts 110 pt ABOVE the first line where the two columns agree, so the band read
        // as beginning below the table, the table fell into `before` as though it were a
        // full-width band, and it was written at page level ahead of the layout table. Its 111 pt
        // of rows were then charged to the single body flow and pushed every line after it down
        // by 103.4 pt: measured, the first line after the table has its baseline at 243.50 in the
        // render against 139.85 in the source, and 31 lines carry the shift.
        //
        // The column pass has ALREADY placed such a table in a column - home[] is computed from
        // the table's own left and right - so the only thing wrong is that the band's extent was
        // measured without it. Extend the band up to cover it. A table drawn across the gutter
        // has home == -1 and is left alone: that one really is a full-width band, and the
        // refusal below still fires for a full-width block that lands inside the band.
        //
        // GUARDED BY A FIT TEST, because home[] is a coarse tag: it asks which edge the block's
        // LEFT starts at, not whether the block is inside the column. Without the test the rule
        // also fires on 06_rect_paid_stamp_red_transparent, whose invoice table (x 64-515 on a
        // 595 pt page) is tagged column 0 of a two-cell split at x=387 that it does not fit in -
        // measured 34/43 -> 28/43, six checks lost. A table that really does fit its column is
        // the case this is for; one that does not is the page's own mis-tagging and is left
        // exactly where it was.
        for (int i = 0; i < nb; i++) {
            if (!(page.blocks.get(i) instanceof PdfToWord.Table) || home[i] < 0) continue;
            float t = bTop[i], bt = blockBottom(page.blocks.get(i));
            if (t < 0f || bt <= 0f) continue;
            PdfToWord.Table q = (PdfToWord.Table) page.blocks.get(i);
            int c = home[i];
            if (q.left < edge[c] - 2f || q.right > edge[c + 1] + 2f) continue;
            if (t < colTop) colTop = t;
        }

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

        // The bands must hold columns of text, not a column of labels beside a column of
        // values. Every test up to here asks only "is there an x that recurs and that nothing
        // crosses" - rowColumnEdges() reads the page's rows and clusters the fragments' left
        // edges, and a form's labels recur at one x and its values at another, so every row of
        // a form passes it. bank-statement-5-pages was written as a two-column layout table on
        // all five of its pages that way, over a page with no columns at all: three label rows
        // in a 36 pt band at the top of a sheet whose body is a ruled five-column table.
        {
            java.util.List<float[]> seg = new ArrayList<>();
            for (int c = 0; c < n; c++) {
                for (Object b : cells[c]) {
                    if (!(b instanceof PdfToWord.Para)) continue;
                    for (PdfToWord.Box z : ((PdfToWord.Para) b).boxes) {
                        if (z.runs.isEmpty() || z.right <= z.x) continue;
                        seg.add(new float[]{z.x, z.right});
                    }
                }
            }
            if (!PdfToWord.bandsAreColumns(seg, edge, colBottom - colTop, page.height)) {
                return false;
            }
        }

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
        // w:tblInd is measured from the text margin - the page margin at body level, and the
        // CELL's left edge when this table is written inside one. The page's x is only the same
        // number at body level; subtracting the cell keeps the field in the frame the renderer
        // reads it in (see the Table path, which had this wrong at 4561).
        int indTw = (int) Math.max(0L,
                Math.round((edge[0] - (ctx.inColumn ? ctx.cellLeftPt : 0f)) * TWIPS_PER_PT));

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
                // A new cell is a new rectangle: its first line is measured from the row's own
                // top edge, so no debt from the previous cell may follow it in.
                ctx.wrapDebtTw = 0;
                ctx.wrapDebtTotalTw = 0;
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
                // The row is as tall as what the cell WRITES, and the renderer charges one line
                // box per wrapped line while flowTwOf can only see the one w:line the paragraph
                // carries. The debt is the difference, already summed over the cell.
                cellTw[c] = flowTwOf(cellXml[c]) + ctx.wrapDebtTotalTw;
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
        // HOW DEEP INSIDE A NESTED TABLE THIS POSITION IS.
        //
        // A cell can hold a nested w:tbl - a real content table inside one column of a layout
        // table - and every paragraph of that nested table carries its own w:before and w:line.
        // Summing those charges the nested table once per CELL rather than once per ROW: a row
        // of five option cells contributed five lines' worth of height to a row that renders as
        // one. Measured on the two documents that nest, cell height as written against what the
        // rows really occupy: 401_trifold_brochure 5583 tw against 4783 (1.6x), and
        // 350_question_paper 21644 tw against 17596 (2.9x) - a 1082 pt row on a 842 pt page,
        // which is why that document comes out as three pages.
        //
        // Inside a nested table the height is carried by its own w:trHeight, exactly as the
        // paragraph rule is for a plain cell (see the note above). So skip w:before/w:line in
        // there and take the row heights instead.
        int depth = 0;
        while (i < xml.length()) {
            if (startsWith(xml, TBL_OPEN, i)) {
                depth++;
                i += TBL_OPEN.length();
            } else if (startsWith(xml, TBL_CLOSE, i)) {
                if (depth > 0) depth--;
                i += TBL_CLOSE.length();
            } else if (depth > 0) {
                if (startsWith(xml, TRHEIGHT, i)) {
                    sum += digits(xml, i + TRHEIGHT.length());
                    i += TRHEIGHT.length();
                } else {
                    i++;
                }
            } else if (startsWith(xml, BEFORE, i)) {
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
            Shape s = (Shape) block;
            // A stamp whose frame is carried by its own text box is drawn BY that box, once,
            // with both rules from the one geometry (see stampBox). Drawing the rule here as
            // well would put a second copy of the frame on the page.
            if (s.stampFrame
                    && ctx.stampText.containsKey(s.mergedHost == null ? s : s.mergedHost)) {
                return;
            }
            if (!s.consumed) shape(sb, s, ctx);
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
    /**
     * Is this line drawn on a quarter turn - within a degree of 90 or 270?
     *
     * <p>The band is a degree wide because that is the width of the claim: a line at 90.4
     * degrees is a vertical column of text as far as a reader is concerned, and the construct
     * below turns it by exactly 90. A line at 89 is still 89 and gets the picture-free path
     * every other angle gets.
     */
    private static boolean quarterTurn(float deg) {
        float a = ((deg % 360f) + 360f) % 360f;
        return Math.abs(a - 90f) <= 1f || Math.abs(a - 270f) <= 1f;
    }

    /** The quarter turn that reads bottom-to-top, i.e. the PDF's -90. */
    private static boolean readsUp(float deg) {
        float a = ((deg % 360f) + 360f) % 360f;
        return Math.abs(a - 270f) <= 1f;
    }

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
            // A hairline with no line is painted by its fill and by nothing else. Suppressing a
            // light fill (see fillXml) then leaves a shape with neither a fill nor a line, and
            // a rule the page drew comes out as blank paper - the largest remaining class,
            // 32_stroke_lines. So a fill-only hairline keeps its fill whatever its lightness;
            // the dark-mode white patch fillXml exists to avoid is a BAND, which has an area,
            // and a 0.3 pt rule has none. Same 1.5 pt / 2 pt test as PdfToWord.bandFillStroke
            // and verify_google._strokes.
            fillXml(sb, s.fillRgb, s.fillAlpha, s.lineRgb < 0 && isHairline(s));
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
     * True when a 0xRRGGBB fill is the page's own colour to within {@link #PAGE_TOL}.
     *
     * <p>The largest per-channel distance from white, which is what a reader sees as the edge
     * of a band: 0 for FFFFFF, 26 for E5EBF5, 54 for C9C9C9. Only the first of those is a fill
     * a reader cannot tell from the paper, and only that one is dropped.
     */
    private static boolean isPageColour(int rgb) {
        int r = (rgb >> 16) & 0xFF, g = (rgb >> 8) & 0xFF, b = rgb & 0xFF;
        return 255 - Math.min(r, Math.min(g, b)) <= PAGE_TOL;
    }

    /**
     * Is this shape a rule - a thin band whose only paint is its fill?
     *
     * <p>One side at or under 1.5 pt and the other over 2 pt. The same test
     * {@code PdfToWord.bandFillStroke} uses to call a fill-only path a hairline, and the one
     * {@code verify_google._strokes} uses to count it.
     */
    private static boolean isHairline(Shape s) {
        float lo = Math.min(s.wPt, s.hPt), hi = Math.max(s.wPt, s.hPt);
        return lo <= 1.5f && hi > 2f;
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
     * <p>Only a fill that IS the page is dropped. A dark band carries white text - the FFFFFF
     * headings in 01, 02, 04 and 62 sit on one - and must stay dark in light mode, and a pale
     * tint is a cell's shading, so both keep their absolute hex. See {@link #PAGE_TOL} for the
     * measurement that separates them: 202 of the 402 fills the old lightness rule dropped were
     * cell fills with a word inside them, and every one of them sat 9 levels or more off the page.
     */
    private static void fillXml(StringBuilder sb, int rgb, float alpha) {
        fillXml(sb, rgb, alpha, false);
    }

    /**
     * @param mustPaint the fill is the only thing painting this shape, so it is written even
     *                  when it is light. See {@link #isHairline} and {@link #shape}.
     */
    private static void fillXml(StringBuilder sb, int rgb, float alpha, boolean mustPaint) {
        if (isPageColour(rgb) && !mustPaint) {
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
        // top - is pushed down by exactly that. It is anchored at the point the page drew it
        // instead, and charges the flow nothing. See pinShortParas().
        if (p.pinned && !anyRotated && !ctx.positioned) {
            pinnedBoxes(sb, p, ctx);
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
                // IS THIS LINE ONE OF A STAMP'S? The one authority on that question is
                // groupStamps(): it decides which of a page's turned lines belong to one stamp,
                // and it does so from the page's geometry alone. The writer therefore asks it
                // back - is this box in the group it built - instead of asking the weaker
                // question "is there a rectangle near this line", which is what it used to do.
                //
                // WHY THAT DISTINCTION IS THE WHOLE DEFECT. frameOf() accepts a frame that
                // groupStamps() deliberately rejected, and the old fallback branch wrote those
                // lines as w:framePr paragraphs. Exactly two documents in the 208 still reached
                // it: 08's "02-09-2025", a 9-degree line whose nearest stroked box is the
                // axis-aligned table border it lies across (frameIsRect says no - the shape is
                // not a rectangle at the line's angle, so binding the line to it would rewrite
                // the table's border as a rotated rectangle the page never drew), and 352's
                // seal, whose letters are placed one by one round a ring and each sit on the
                // certificate's own border (ring characters are never grouped - doing so
                // collapsed the roundel and lost three words). Google Docs ignores w:framePr
                // positioning outright, so on a phone those paragraphs rendered as ordinary
                // body text at the left margin. There is no third construct to give them: what
                // they are is a rotated label on a drawing, which is the case below.
                Shape host = frame == null ? null
                        : (frame.shape.mergedHost == null ? frame.shape : frame.shape.mergedHost);
                java.util.List<PdfToWord.Box> stampLines =
                        host == null ? null : ctx.stampText.get(host);
                if (stampLines != null && stampLines.contains(b)) {
                    // T02-B: a line the page drew inside a stamp's frame goes into that stamp's
                    // ONE object - a rotated text box that carries the frame and the text
                    // together (see stampBox). It is written once, where the first of the
                    // stamp's lines falls in the page's order, so the box is at the point in
                    // the document a reader would expect and the lines after it are unchanged.
                    //
                    // WHY A TEXT BOX AGAIN. ae72de3 wrote each line as a w:framePr paragraph,
                    // which LibreOffice honours and Google Docs does not: on a phone the words
                    // came out black and upright at the LEFT MARGIN and the frame landed alone
                    // on a second, empty page. The construct before it - wps:wsp with
                    // <a:xfrm rot> - renders tilted and in place in Google Docs (v3.53.4's
                    // device screenshot), so the stamp is that construct again. What ae72de3
                    // fixed is kept: the frame's rules are still one geometry (stampFrames),
                    // the stamp's place in the page's order is still its own y (orderStamps),
                    // and a stamp still charges the page nothing (pageFits, spacingTw).
                    if (ctx.stampWritten.add(host)) {
                        stampBox(sb, stampLines, frame, lineAngle, ctx);
                    }
                } else {
                    // Not a stamp line: no rectangle around this line, or a rectangle that is
                    // not this line's own frame (see above) - the per-glyph text of a round
                    // seal, a rotated label on a drawing, a label lying across a table rule.
                    // There is no frame to bind to, so the line is placed on its own origin with
                    // no rotation: the run starts at the left end of what the page drew, and a
                    // line drawn right-to-left (file 04) starts at the other end because that
                    // is where its left end is.
                    double dirX = Math.cos(Math.toRadians(lineAngle));
                    float startX = px;
                    if (dirX <= -0.5) startX = px - b.length;
                    else if (Math.abs(dirX) < 0.5) startX = px - b.length / 2f;
                    // WHERE IN THE BOX THE BASELINE SITS. A line that had a rectangle but is not
                    // a stamp line used to be placed by a frame, and a frame puts the top of
                    // the line's box {@link #LINE_BASE} of its height above the baseline. The
                    // exact inset reproduces that placement exactly - {@code LINE_BASE *
                    // LINE_FACTOR} em puts the baseline on {@code b.y}, which is where the page
                    // drew it (see the second {@link #anchorBox}) - so swapping the construct
                    // moves nothing: measured on 352, dy is 0.8 pt median and 23.0 pt worst,
                    // against the frame's 0.6 and 23.0. A line with no rectangle at all keeps
                    // the {@link #ASCENT} it has always had, because every other such line in
                    // the corpus is measured against that.
                    float topEm = frame != null ? LINE_BASE * LINE_FACTOR : ASCENT;
                    if (b.ring) {
                        // ONE CHARACTER OF A RING: ONE BOX, ONE ANGLE.
                        //
                        // A ring is the one place where a line's angle is not a property of
                        // the document's flow at all: each character sits on its own tangent
                        // (05's arc runs -55.2, -51.8, -48.1 ... and 305's runs -110.0,
                        // -102.4, -94.8), so there is no single frame a ring could be
                        // written into and no way to make one turned line of it.
                        //
                        // OOXML has no per-RUN angle: {@code a:xfrm rot} is an attribute of a
                        // SHAPE. The smallest thing that can carry an angle is therefore one
                        // shape, and that is exactly the grain a ring character already
                        // arrives at - ringLines() makes one Box per character. So the ring
                        // is written as N anchored boxes, each with its own rot, which is
                        // per-glyph rotation expressed in the only way the format has.
                        //
                        // WHY px AND NOT startX. Everywhere else on this path x/y come from
                        // getXDirAdj()/getYDirAdj(), measured in a frame turned with the text,
                        // which is why the level case needs startX = px - length/2 (the box is
                        // centred on a rotated origin) and why a 180-degree line is mirrored
                        // back. A ring character carries the page point it was drawn at, so
                        // the box's baseline origin IS (px, py) and any of those adjustments
                        // would move it by the amount it is correcting for elsewhere.
                        //
                        // AND NOT THE QUARTER-TURN CONSTRUCT. vert + a swapped extent is the
                        // construct LibreOffice turns, but it has four states, not 360: a
                        // character at -55.2 degrees cannot be written with it, and using it
                        // for the ones that happen to land on 90 would put one character of a
                        // seal in a different construct from its neighbours.
                        //
                        // AND THE BOX IS ONE CHARACTER WIDE, NOT 1.5 em WIDER. wPt above is
                        // sized for a line that may wrap; a ring character cannot wrap. More to
                        // the point, anchorAt turns the box about its CENTRE, so the box's
                        // half-width is the lever a reader that ignores a:xfrm rot swings the
                        // character by: ((cos - 1) . -w/2, ...). Measured on 05 with the angle
                        // in place: at length + 1.5 em the render loses 12 of its 83 matched
                        // runs (71/83, 17_matched_runs fails); at length + 0.6 em it loses
                        // none and 05 scores 41/43. Nothing about the file's own correctness
                        // depends on the width, so the width is chosen by what the render can
                        // still place.
                        float ringW = Math.max(b.length, 2f) + b.size * 0.6f;
                        anchorAt(sb, ctx, px, py, 0f, topEm * b.size,
                                ringW, hPt, inner.toString(), lineAngle, -1, 0.6f, 0f, 0f);
                    } else if (quarterTurn(lineAngle)) {
                        // A quarter-turn line with no frame to sit in still gets the one
                        // construct that turns: swapped extent, vert, no a:xfrm rot. The
                        // box's local (0,0) is the frame's far corner along the baseline
                        // (vert270 reads up, so it starts at the bottom) and the baseline
                        // falls at LINE_BASE * lineHeight on its own.
                        double c2 = Math.cos(Math.toRadians(lineAngle));
                        double s2 = Math.sin(Math.toRadians(lineAngle));
                        boolean up2 = readsUp(lineAngle);
                        float ax = 0f, ay = topEm * b.size;
                        float lu = up2 ? wPt : 0f, lv = up2 ? 0f : hPt;
                        float du = lu - ax, dv = lv - ay;
                        // THE BASELINE ORIGIN, NOT THE CENTRED BOX. startX is px - length/2
                        // because the horizontal construct centres a rotated box on the
                        // origin; a vertical frame starts its text AT the origin, so the
                        // half-length offset would move the text by exactly length/2 -
                        // measured on table-with-rotated-header: -12.5 pt on "Month" and
                        // -32.9 pt on "Cost per piece (Rs)", which are their half-lengths.
                        anchorAt(sb, ctx,
                                (float) (px + c2 * du - s2 * dv),
                                (float) (py + s2 * du + c2 * dv),
                                0f, 0f, hPt, wPt, inner.toString(), 0f, -1, 0.6f, 0f, 0f,
                                up2 ? "vert270" : "vert");
                    } else {
                    anchorAt(sb, ctx, startX, py, 0f, topEm * b.size, wPt, hPt,
                            inner.toString(), lineAngle, -1, 0.6f, 0f, 0f);
                    }
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
     * A pinned paragraph: each of its lines anchored where the page drew it, as the text box
     * {@link #anchorBox} writes.
     *
     * <p>WHY THIS IS NO LONGER THE FRAME A STAMP USES. These lines were written as
     * {@code w:framePr} paragraphs, exactly as a stamp line was, and the frame
     * did what it was added for: LibreOffice honoured it and admit-card's median dy fell from
     * 17.2 pt to 2.4 pt. On a real phone in Google Docs the words were nowhere near the photo
     * box - they rendered clipped at the left margin, across "Name of candidate". Google Docs
     * ignores {@code w:framePr} positioning outright and draws the paragraph as ordinary body
     * text, so a property only some readers implement is not a fix; it is a measurement of
     * LibreOffice. The flow must not be charged for these lines, and the reader that would not
     * honour the frame must still be able to place them.
     *
     * <p>WHY A TEXT BOX IS RIGHT HERE THOUGH IT IS WRONG FOR A STAMP. A stamp is the document's
     * own words and the user edits them, so a stamp line has to stay a paragraph (D-25). This
     * line is the LABEL OF A DRAWN RECTANGLE - "AFFIX PHOTOGRAPH" inside the photo box - and
     * the writer already places that kind of label with {@link #anchorBox}: a label the page drew
     * inside a closed outline belongs to the outline rather than to the flow (see
     * {@link #containerOf}). A drawing's page-relative offset is the one positioning construct
     * Google Docs honours, so the words land on the rectangle there, in Word and in LibreOffice
     * alike. Each line is its own drawing, so no two of them can drift against each other.
     *
     * <p>AND IT STILL COSTS THE FLOW NOTHING. The wrapper paragraph is one twip tall
     * ({@code w:line="1" w:lineRule="exact"}), so the table that follows is placed from the
     * flow's position exactly as it was while the frame held the flow still - the 19.4 pt step
     * does not come back.
     */
    private static void pinnedBoxes(StringBuilder sb, PdfToWord.Para p, Ctx ctx) {
        for (PdfToWord.Box b : p.boxes) {
            if (b.runs.isEmpty() || b.text().trim().isEmpty()) continue;
            anchorBox(sb, p, b, ctx);
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
        // The hairline box, the same one flowFromBox writes: a row of fields is a line of the
        // same flow, and two boxes for one flow is two rulers on one page.
        float linePt = hairlinePt(size);
        int beforeTw = 0;
        float placeTopPt = flowTopPt(ctx);        // see flowFromBox: the edge is the placement
        if (ctx.afterTablePt >= 0f) {
            // Same rule as flowFromBox: the row is placed against the table's measured edge
            // rather than spaced from a baseline that the table replaced.
            float topPt = first.y - LINE_BASE * linePt;
            float edgeGap = topPt - ctx.afterTablePt;
            placeTopPt = ctx.afterTablePt;
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
                beforeTw = (int) Math.min((long) firstGapCapTw(ctx), Math.round(topGap * TWIPS_PER_PT));
            } else if (first.y > 0f) {
                linePt = Math.min(linePt, Math.max(size, first.y / LINE_BASE));
            }
        } else if (pitch > 0f) {
            float extra = pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt;
            if (extra > 0f) {
                // A gap wider than the flow may spend is not a gap, it is a position - the same
                // rule flowFromBox applies to a single line, and this branch used to CLAMP
                // instead. A running footer is a row (its label and its folio are one baseline),
                // so it took this path: on 27_two_column_left_short_txtpos the footer's 272.8 pt
                // gap was written as 120 pt - 152 pt short of the gap the page drew, and the
                // footer landed 130.6 pt above its own baseline. flowFromBox anchors the same
                // gap rather than truncating it.
                if (!ctx.inColumn && extra * TWIPS_PER_PT > gapCapTw(ctx)) {
                    ctx.positioned = true;
                    for (PdfToWord.Box ab : cols) anchorBox(sb, p, ab, ctx);
                    return;
                }
                beforeTw = (int) Math.round(extra * TWIPS_PER_PT);
            }
        }
        // The same rule flowFromBox applies, for a row of fields: a gap that would be NEGATIVE
        // is a position, not a gap, and the row is anchored where the page drew it instead of
        // being written with no gap and landing wherever the flow happens to be. A row has no
        // absolute fallback of its own - it was the one writer with no way out of the zero.
        {
            float rowTop = first.y - LINE_BASE * linePt;
            if (beforeTw == 0 && ctx.flowY >= 0f && !ctx.newPage && ctx.afterTablePt < 0f
                    && rowTop < ctx.flowY) {
                ctx.zeroGap++;
                float miss = ctx.flowY - rowTop;
                ctx.zeroGapPt += miss;
                if (miss > ctx.zeroGapWorstPt) ctx.zeroGapWorstPt = miss;
                if (ctx.inColumn) ctx.zeroGapInCol++;
            }
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
            placeTopPt = flowTopPt(ctx);
            float topGap = first.y - LINE_BASE * linePt;
            if (topGap > 0f) {
                beforeTw = (int) Math.min((long) firstGapCapTw(ctx), Math.round(topGap * TWIPS_PER_PT));
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
        // Same anchor rule as flowFromBox, for a row of fields: a row the flow cannot put on
        // its own baseline is anchored there, field by field at the x the page drew each one.
        // A row is where the miss is worst, because a row has no absolute fallback of its own -
        // on 69_two_col_legal_numbered_clauses "binding." was written 18 pt low here and the
        // row that followed it, correctly anchored, landed on top of it.
        if (ZERO_GAP_ANCHOR && !ctx.inColumn && !ctx.newPage) {
            float topNow = flowTopPt(ctx) + beforeTw / (float) TWIPS_PER_PT;
            float landY = topNow + LINE_BASE * (lineTw / (float) TWIPS_PER_PT);
            // The anchored box must FIT above the line before it, or it trades a position for a
            // collision. Measured on 69_two_col_legal_numbered_clauses: anchoring
            // "This agreement..." at its own y (306.8) put it 2.6 pt into the line above, which
            // is itself 18 pt low, and that is a NEW 26_text_overlap failure bought with a
            // position the page never left room for. Where the room is not there the line stays
            // in the flow and is counted in zeroGapNoRoom instead.
            float prevBoxTop = flowTopPt(ctx) - ctx.flowBoxPt;
            float thisBoxBottom = first.y + (1f - LINE_BASE) * linePt;
            if (landY - first.y >= ZERO_GAP_FLOOR_PT && thisBoxBottom <= prevBoxTop) {
                ctx.zeroGapAnchored++;
                for (PdfToWord.Box ab : cols) anchorBox(sb, p, ab, ctx);
                ctx.lastLinePt = linePt;
                ctx.lastBaseline = first.y;
                ctx.lastSize = size;
                ctx.flowY = first.y;
                ctx.flowBoxPt = Math.max(4f, size * LINE_FACTOR);
                return;
            }
            if (landY - first.y >= ZERO_GAP_FLOOR_PT) ctx.zeroGapNoRoom++;
        }
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
        resync(ctx, placeTopPt, beforeTw, lineTw);

        // A tab stop's position is measured from the page margin, NOT from the paragraph's own
        // indent - the section has zero margins, so the page margin is x=0 and a stop is the
        // page's own x. Subtracting the indent put every value one indent too far left (file
        // 21's value landed at 240 pt instead of 300), and on file 16 it put the stop behind the
        // text before it, so Word skipped it for the next one and the four column headings
        // marched right across the page.
        StringBuilder tabs = new StringBuilder();
        for (int i = 1; i < cols.size(); i++) {
            PdfToWord.Box b = cols.get(i), before = cols.get(i - 1);
            // A tab stop is measured from the paragraph's TEXT MARGIN. Outside a cell that is
            // the page margin, and the section's margins are zero, so a stop is the page's own
            // x. Inside a layout-table cell the text margin is the CELL's left edge, so a page
            // x written there is one column-edge too far right: on 403_crossword_puzzle the
            // stop (157.5 pt) fell outside a 7 pt cell, LibreOffice dropped it and the number
            // landed on the cell's edge at 157.6 pt where the page drew it at 113.5, and on
            // 401_trifold_brochure every field of the third panel came back at page x plus the
            // panel's own left edge. The indent on the same paragraph already comes off
            // (bandLeftTw), so the stop is the only field still in the page's frame.
            float frameX = ctx.inColumn ? ctx.cellLeftPt : 0f;
            float pos = b.x - frameX;
            // The embedded face's advance is not the substituted face's: at the same point size
            // Word's face can be a few per cent wider, and a tab stop that lands inside the text
            // before it is skipped for the next one. Only ever push the stop clear, never left.
            //
            // The clearance is ONE EM OF THE TYPE BEFORE IT, not a percentage of an absolute x.
            // It was `before.right * 1.06f`, and 6 % of an absolute x grows with how far right
            // the field sits: 3.2 pt at x=56 and 21 pt at x=350, so a row in the right-hand
            // column of a form had its stop pushed 21 pt past the x the page drew it at and the
            // field then ran past the column's right edge (60) and out of its 10 pt window (43).
            // Measured on the 211-document corpus, this term with the cell-frame fix above and
            // the w:tblInd fix below: 60 25 -> 23, 43 13 -> 12, 47 49 -> 41, total 8461 -> 8475,
            // no document worse. 47 is where the term itself shows: it is a left-edge statistic
            // and the push was the largest single move on it (8 documents).
            // ...and the clearance is in the SAME FRAME as the stop it is compared with.
            //
            // `before.right` is a PAGE x and `pos` is a CELL x (frameX came off above), so
            // `clear > pos` was a page coordinate tested against a cell coordinate. Inside a
            // cell the page x always wins, and the stop was written at the page's own x - a
            // value that is outside the cell by construction. Measured on
            // brochure-3col-with-sidebar-box: "Founded" ends at page x 427.76, size 7, so
            // clear = 430.56 pt = 8611 twips, and 8611 is exactly what was written; the field
            // it precedes was drawn at page x 508.18 in a cell whose left edge is 395.33, so
            // the stop the page needs is 112.85 pt = 2257 twips. The renderer clamped the
            // 430 pt stop to the cell's right edge, "1994, Pune" no longer fitted after it,
            // and it wrapped to a second line 1.0 pt under the first - 20 overlaps on that
            // document, and 53 across the five it appears on.
            //
            // Only inside a cell: outside one frameX is 0 and this is the identical number.
            float clear = (before.right - frameX) + before.size * 0.4f;
            boolean last = i == cols.size() - 1;
            if (last && b.right > ctx.pageWidthPt - 2f && (b.right - frameX) > clear) {
                // A field that ends at the paper's edge is right-aligned there. A right tab keeps
                // its RIGHT edge where the page drew it, so a wider substitute grows inwards
                // instead of wrapping the last word onto the next line.
                int posTw = (int) Math.round((b.right - frameX) * TWIPS_PER_PT);
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
                .append(spacing(beforeTw, lineTw, size, autoFlowLines(), ctx.newPage))
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
            runXml(sb, run, p.heading > 0);
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
    /**
     * The largest gap the first line of a sheet may be given, in twips.
     *
     * <p>This used to be a constant 2000 twips (100 pt). A page whose first baseline sits
     * further down than that - a title page, a letterhead, a page whose first text follows a
     * logo block - was written with a 100 pt gap and every line on the sheet landed high by
     * the difference: 57_centred_title_page_left_body_pages asks for 4516 twips and is
     * written with 2000, which is 125.8 pt, and all fifteen of its runs are out by it.
     *
     * <p>The page's own height is the only bound this needs. The gap is a position, and a
     * position beyond the paper is caught by 27_text_off_page wherever it lands.
     */
    private static int firstGapCapTw(Ctx ctx) {
        return Math.max(2000, Math.round(ctx.pageHeightPt * (float) TWIPS_PER_PT));
    }

    /**
     * How many lines the renderer will draw for one paragraph inside a cell.
     *
     * <p>A cell is a fixed rectangle. The page's line was drawn at the page's width, so when the
     * column pass puts it in a narrower cell the renderer breaks it up and charges one line box
     * per piece - and the model charges one for the whole paragraph. This is the count that
     * closes the gap, and it is the same question {@link #wrapsAt} answers for a real table
     * (:5266), asked of a paragraph instead of a cell string.
     *
     * <p>TWO THINGS KEEP IT HONEST, and both are measurements rather than guesses.
     *
     * <p>The first is the gate. Whether the paragraph wraps at all is not a matter of opinion:
     * the page drew the line {@code b.right - b.x} wide and the cell is {@code avail} wide, so a
     * line that fits cannot wrap and is left exactly alone. That gate is what keeps this off
     * the documents whose columns are wide enough - an ungated version of this counted wraps in
     * every two-column layout and moved five of them.
     *
     * <p>The second is the advance. A character average (0.5 em, what {@link #wrapsAt} uses)
     * misreads a 43 pt cell badly, because what decides the count there is the WORDS, not the
     * characters: 350's marks cell breaks "SQL queries" across two lines that both fit in 11
     * characters. The line's own width over its own character count is the advance of THIS line
     * in THIS face, measured from the page, and it makes the total text width exact; only the
     * word boundaries are then left to estimate.
     *
     * <p>The count is the larger of that greedy fill and the plain {@code srcW / avail}, so a
     * line of few long words - where greedy is at its worst - is still charged what its own
     * width demands.
     */
    private static int cellWrapLines(PdfToWord.Box b, Ctx ctx, int indTw, int rightTw) {
        if (b == null || b.rotated) return 1;
        String text = b.text();
        if (text == null) return 1;
        float avail = (ctx.cellRightPt - ctx.cellLeftPt)
                - indTw / (float) TWIPS_PER_PT - rightTw / (float) TWIPS_PER_PT;
        if (avail <= 1f) return 1;
        int n = 0;
        for (int i = 0; i < text.length(); i++) if (text.charAt(i) > ' ') n++;
        if (n <= 0) return 1;
        // HOW WIDE IS THE TEXT, when the box cannot say? A Box's own extent is the extent of the
        // FIRST span on the line: on 350 the marks paragraph reports x=551.88 right=567.28 - the
        // width of "[08]" - while its runs carry all 105 characters of the question. So the box
        // is a lower bound and the character count is the other one; take the larger.
        float textW = Math.max(b.right - b.x, n * 0.5f * Math.max(1f, b.size));
        // THE GATE: a line the cell can hold is not wrapped, whatever its words look like.
        //
        // 3.0 rather than 1.0, and it is a budget argument rather than a tolerance. Below three
        // times the cell width the paragraph wraps into one or two lines, the whole of the debt
        // is under a point, and the estimate's own error is the same size - so the correction
        // buys nothing and can cost a line. At 3.0 and above the cell is not a column the page
        // ever drew the text in, the debt is several points a paragraph and it accumulates.
        // Measured: at 1.02 the gate lets 06_rect_paid_stamp_red_transparent through and costs
        // it 47_margins; at 3.0 that document is untouched and 350 keeps its gain.
        if (textW <= avail * Float.parseFloat(System.getProperty("p2w.wrapgate", "3.0"))) return 1;
        float em = textW / n;
        int lines = 1;
        float w = 0f;
        int i = 0, len = text.length();
        while (i < len) {
            while (i < len && text.charAt(i) <= ' ') i++;
            int j = i;
            while (j < len && text.charAt(j) > ' ') j++;
            if (j > i) {
                float ww = (j - i) * em;
                if (w > 0f && w + em + ww > avail) { lines++; w = 0f; }
                if (ww > avail) {
                    int pieces = (int) Math.ceil(ww / avail);
                    lines += pieces - 1;
                    w = ww - (pieces - 1) * avail;
                } else {
                    w += (w > 0f ? em : 0f) + ww;
                }
            }
            i = j;
        }
        int floor = (int) Math.ceil(textW / avail);
        return Math.max(1, Math.max(lines, floor));
    }

    /** The hairline line box a flow line is written with: {@code w:line = 1.38 * size} twips. */
    private static float hairlinePt(float size) {
        // Google's floor is 0.069 em of the RUN, so the box only lands inside it while
        // 0.069 * size twips-of-points is below 16.56 / r twips - 12.97 twips for the widest
        // measured face (Liberation Serif, r = 1.277). Above that the floor stops binding and
        // Google charges (w:line/240) * r * size, which is quadratic in the size: at 24 pt the
        // box is charged 3.86 pt where Word charges 1.66, and the difference accumulates down
        // the page. Clamping the box at the floor keeps the two readers exact for every size
        // the floor still covers (12 / r = 10.3 pt for DejaVu, 9.4 pt for Liberation Serif)
        // and bounds the residue above it at 0.069 * size - 0.6485 pt a line instead of
        // 0.0067 * size^2 - 0.069 * size: 1.01 pt against 2.20 at 24 pt, 1.70 against 5.41
        // at 34 pt.
        return Math.min(HAIRLINE_EM * Math.max(1f, size), 0.6485f);
    }

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
                return new float[]{Math.min((float) firstGapCapTw(ctx), topGap * (float) TWIPS_PER_PT), linePt};
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
        // The box is a hairline, not a fraction of the em: see HAIRLINE_EM. It is the same
        // number for every renderer, so the gap below is the whole of the pitch and nothing
        // accumulates down the page.
        float linePt = hairlinePt(b.size);
        int beforeTw = 0;
        // WHERE THIS PARAGRAPH IS ACTUALLY PUT, as an absolute y from the top of the sheet.
        //
        // The flow's own advance places a paragraph at flowTopPt(); the afterTablePt branch
        // below places it at the table's or the row's measured edge instead. resync() used to be
        // handed flowTopPt() in both cases, so after a line placed at an edge it recorded a
        // position that the page never took: on 27_two_column_left_short_txtpos the second cell
        // of the row left flowY 67.6 pt below the line it had just written, and every flowed
        // line in that cell was then written 67.6 pt low. The edge is the placement, so it is
        // what resync() is given.
        float placeTopPt = flowTopPt(ctx);
        if (ctx.afterTablePt >= 0f) {
            // The box above this one is a layout table - or the top of a column cell - and a
            // table's height is decided by the renderer from its own line boxes, not by the
            // page's baselines. So this line is placed against the measured edge: the gap is
            // exactly what the page left between that edge and this line's box top.
            float topPt = b.y - LINE_BASE * linePt;
            float edgeGap = topPt - ctx.afterTablePt;
            placeTopPt = ctx.afterTablePt;
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
                beforeTw = (int) Math.min((long) firstGapCapTw(ctx), Math.round(topGap * TWIPS_PER_PT));
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
        float absTop = b.y - LINE_BASE * linePt;
        if (ctx.flowY >= 0f) {
            absBeforeTw = (int) Math.max(0L,
                    Math.round(Math.min(absTop - ctx.flowY, gapCapTw(ctx) / TWIPS_PER_PT) * TWIPS_PER_PT));
        }
        // ZERO-GAP MEASUREMENT. A gap is white space the flow spends going down, so it cannot
        // be negative: when the page puts this line ABOVE where the flow already is, the gap
        // is written as 0 and the line lands wherever the flow happens to be - low by the
        // overshoot - and the next line is measured from there. Counted here, before the fit
        // clamp below, because that clamp can zero a gap that was real.
        if (beforeTw == 0 && ctx.flowY >= 0f && !ctx.newPage && ctx.afterTablePt < 0f
                && absTop < ctx.flowY) {
            ctx.zeroGap++;
            float miss = ctx.flowY - absTop;
            ctx.zeroGapPt += miss;
            if (miss > ctx.zeroGapWorstPt) ctx.zeroGapWorstPt = miss;
            if (ctx.inColumn) ctx.zeroGapInCol++;
            // THE ANCHOR RULE, applied to the case the cap rule above could not reach. A gap
            // wider than the cap is already treated as a position rather than a gap; a gap that
            // came out NEGATIVE is the same statement in the other direction - the page put the
            // line somewhere the flow cannot walk to - and it was written as zero, which puts
            // the line wherever the flow happens to be. So the line is anchored at its own y
            // and the running position is re-synced to it, which is what stops the next line
            // being dragged down with it.
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
            placeTopPt = flowTopPt(ctx);          // the new sheet starts at its own top
            float topGap = b.y - LINE_BASE * linePt;
            if (topGap > 0f) {
                beforeTw = (int) Math.min((long) firstGapCapTw(ctx), Math.round(topGap * TWIPS_PER_PT));
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
        // THE ANCHOR RULE, in the general form: a line the flow cannot put on its own y is
        // placed on its own y instead. The file already does this for a gap WIDER than the cap
        // (a footer 340 pt below the columns, a diagram's labels); a gap that came out
        // NEGATIVE is the same statement with the sign reversed and used to be written as
        // w:before="0", which put the line wherever the flow happened to be. It is checked
        // here, AFTER the fit clamp, because that clamp is the other thing that can stop a
        // line reaching its own y - on 69_two_col_legal_numbered_clauses one line landed
        // 16.9 pt low and dragged four more with it, and again at 41.1 pt.
        if (ZERO_GAP_ANCHOR && !ctx.inColumn && !ctx.newPage) {
            float topNow = flowTopPt(ctx) + beforeTw / (float) TWIPS_PER_PT;
            float landY = topNow + LINE_BASE * (lineTw / (float) TWIPS_PER_PT);
            float err = landY - b.y;
            // The anchored box must FIT above the line before it. A line the flow put low has
            // its own y somewhere above the flow, and where the line above it is ALSO low there
            // may be no room left: anchoring there puts the text on top of the line above and
            // trades a few points of position for a real collision. Measured on
            // 69_two_col_legal_numbered_clauses - anchoring "This agreement..." at its own y
            // (306.8) put it 2.6 pt into the line above, which is itself 18 pt low, and that is
            // a NEW 26_text_overlap failure. So the box is placed only where the page left room
            // for it; where it did not, the line stays in the flow and is counted in
            // {@code zeroGapNoRoom} instead of being moved somewhere it cannot go.
            float prevBoxTop = flowTopPt(ctx) - ctx.flowBoxPt;
            float thisBoxBottom = b.y + (1f - LINE_BASE) * linePt;
            if (err >= ZERO_GAP_FLOOR_PT && thisBoxBottom <= prevBoxTop) {
                ctx.zeroGapAnchored++;
                anchorBox(sb, p, b, ctx);
                // The anchored box's baseline IS b.y, so that is where the flow now is.
                ctx.lastLinePt = linePt;
                ctx.lastBaseline = b.y;
                ctx.lastSize = b.size;
                if (ANCHOR_KEEPS_FLOW) {
                    ctx.flowY = flowTopPt(ctx) + beforeTw / (float) TWIPS_PER_PT
                            + LINE_BASE * (lineTw / (float) TWIPS_PER_PT);
                    ctx.flowBoxPt = lineTw / (float) TWIPS_PER_PT;
                } else {
                    ctx.flowY = b.y;
                    ctx.flowBoxPt = Math.max(4f, b.size * LINE_FACTOR);
                }
                return;
            }
            if (err >= ZERO_GAP_FLOOR_PT) ctx.zeroGapNoRoom++;
        }
        // The box the pitch solver compares next time is the page's own, not the squeezed one.
        ctx.lastLinePt = linePt;
        ctx.lastBaseline = b.y;
        ctx.lastSize = b.size;
        ctx.newPage = false;
        // Re-sync to what was written, so the next paragraph is measured from the reader's
        // position rather than from the PDF's (D-26) - and to the position this paragraph was
        // really placed at, which is the table/row edge when the branch above used one.
        resync(ctx, placeTopPt, beforeTw, lineTw);
        sb.append("<w:p><w:pPr>");
        if (p.heading > 0) {
            sb.append("<w:pStyle w:val=\"Heading").append(Math.min(p.heading, 3)).append("\"/>");
        }
        sb.append("<w:snapToGrid w:val=\"0\"/>")
                .append(spacing(beforeTw, lineTw, b.size, autoFlowLines(), ctx.newPage))
                .append("<w:ind w:left=\"").append(Math.max(0, leftTw - bandLeftTw(ctx, p.column)))
                .append("\" w:right=\"").append(rightTw).append("\" w:firstLine=\"0\"/>");
        if (p.align == 1) sb.append("<w:jc w:val=\"center\"/>");
        else if (p.align == 2) sb.append("<w:jc w:val=\"right\"/>");
        sb.append("</w:pPr>");
        for (PdfToWord.Run run : b.runs) {
            if (run.text.isEmpty()) continue;
            runXml(sb, run, p.heading > 0);
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
            runXml(sb, run, p.heading > 0);
        }
        sb.append("</w:p>");
    }

    /** One run with the properties the PDF drew it with. */
    private static void runXml(StringBuilder sb, PdfToWord.Run run) {
        runXml(sb, run, false);
    }

    /**
     * One run, with {@code styleBold} telling it that the paragraph style it is written into
     * already says bold.
     *
     * <p>THE HEADING STYLES SAY BOLD, so every run inside a heading inherited it. The style
     * definition is {@code <w:rPr><w:b/>...} (see {@link #heading}) and a run that carries no
     * {@code w:b} of its own takes the style's - which is correct DOCX, and wrong for a page
     * whose heading is drawn in a regular face. Measured on the 211-document corpus, this is
     * the whole of 34c's two failures: 39_small_caps_letter_spacing draws "THE MYSORE CHAMBER
     * OF COMMERCE AND INDUSTRY" in Liberation Serif Regular at 15/11.7 pt, the engine marked
     * the line a Heading3 because it is 1.43x the body size, and 12 of 74 matched spans came
     * back bold (LiberationSerif-Bold, flags 20); product-catalogue-code-left-price-right does
     * the same to the rupee sign of every price line, which the engine marked Heading2 - 20 of
     * 126 spans, and 34c read 84 % on both documents.
     *
     * <p>The style's bold is not removed - it is what makes the heading a heading in Word's
     * outline - it is switched OFF per run, which is how DOCX expresses "this run is not the
     * style's weight".
     */
    private static void runXml(StringBuilder sb, PdfToWord.Run run, boolean styleBold) {
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
        else if (styleBold) sb.append("<w:b w:val=\"0\"/>");
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
        // A 180-DEGREE LINE IS ASKED FOR, NOT ASSUMED FROM A MISSING ANGLE.
        //
        // This test used to read "rotated, and its angle is about 0", which is what a 180-degree
        // line's x/y look like (PDFBox reports a turned line's origin in a frame turned with it,
        // so both coordinates come back mirrored about the page). But 0 is also the DEFAULT of
        // Line.angle, so every rotated line whose builder never set an angle - the ordinary
        // line path, see PdfToWord.toLines - was read as a 180-degree line and had its origin
        // mirrored about the page. Measured on 15_stamp_on_scanned_page: two +9-degree stamp
        // lines went out at rot="10800000" and in the opposite corner of the sheet. Now that
        // every rotated line records its angle, 180 is asked for by name, and a line drawn at
        // 9 degrees cannot answer yes. 04_stamp_180deg_upside_down's CANCELLED lines are
        // unaffected: their angle is 180.0, so this still fires for them.
        return b.rotated && Math.abs(Math.abs(b.angle) - 180f) < 1f && !b.ring;
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
                // A RING CHARACTER IS NOT A STAMP LINE - the same exclusion groupStamps()
                // makes, for the same reason. Once ringLines() started carrying each
                // character's own angle, frameOfLine() began finding the seal's own border
                // round those characters, so a ring paragraph answered "yes" here and was
                // moved to the place in the page's order where its y falls. That reorders
                // page.blocks itself, which both outputs read: on 318 and 60 the seal's
                // block moved from the end of the sheet to the middle of it and the .txt
                // changed with it (318: 81 -> 90 lines). A ring is placed by its own page
                // coordinates in every character and has nothing to gain from being moved.
                if (bx.ring) break;
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
     * Which of a page's turned lines belong to one stamp, keyed by the shape that carries its
     * frame.
     *
     * <p>The lines of a stamp are not marked as a group by the engine: they arrive as separate
     * paragraphs, read after the page's own words. What ties them together is the geometry they
     * share - each line's baseline falls inside the SAME rectangle, which is what
     * {@link #frameOfLine} answers - so the grouping is that answer and nothing else. A rotated
     * line with no rectangle round it (a ring's per-glyph text, a label on a drawing) is not a
     * stamp line and is left out, so it keeps the placement it had.
     *
     * <p>The map is rebuilt for every page and every pass, and the "already written" set is
     * cleared with it: the budget guard writes a page up to three times, and each pass has to
     * write every stamp again.
     */
    private static void groupStamps(PdfToWord.Page page, java.util.List<Shape> outlines, Ctx ctx) {
        ctx.stampText.clear();
        ctx.stampWritten.clear();
        if (outlines == null || outlines.isEmpty()) return;
        for (Object o : page.blocks) {
            if (!(o instanceof PdfToWord.Para)) continue;
            for (PdfToWord.Box b : ((PdfToWord.Para) o).boxes) {
                if (!b.rotated || b.runs.isEmpty() || b.text().trim().isEmpty()) continue;
                // A ring character is not a stamp line. A seal's letters are placed one by one
                // round a circle, each with its own angle (see ringLines), and the box they sit
                // nearest to is the document's own border - so grouping them would put a
                // certificate's whole roundel into one text box and rewrite its text. They keep
                // the placement they had.
                if (b.ring) continue;
                Frame f = frameOfLine(outlines, b, ctx);
                if (f == null) continue;
                // AND IS IT REALLY A RECTANGLE AT THIS LINE'S ANGLE? The box this method builds
                // carries its path expressed in the line's own axes, which is only faithful when
                // the shape IS that rectangle. It is not always: 08's "02-09-2025" is a 9-degree
                // line whose nearest stroked box is the axis-aligned table border it sits over,
                // and frameOf accepts it because 9 degrees is close to a whole quarter turn. Fed
                // to the box, those corners are re-read in a 9-degree frame and the table's
                // border comes out as a rotated rectangle that the page never drew. A shape whose
                // corners do not land on the frame's own corners is not this line's frame, and
                // the line is left exactly as it was.
                if (!frameIsRect(f, mirrored(b) ? 180f : b.angle)) continue;
                Shape host = f.shape.mergedHost == null ? f.shape : f.shape.mergedHost;
                java.util.List<PdfToWord.Box> lines = ctx.stampText.get(host);
                if (lines == null) {
                    lines = new ArrayList<>();
                    ctx.stampText.put(host, lines);
                }
                lines.add(b);
            }
        }
    }

    /**
     * Do the frame's own corners land on the corners of the rectangle {@link #frameOf} measured?
     *
     * <p>That is the same question as "is this shape a rectangle turned to this line's angle",
     * asked in the coordinates the stamp's box is written in. A rectangle at the line's angle maps
     * onto the frame's own (0,0)-(w,h) box exactly; anything else - an axis-aligned rule a few
     * degrees off the line, a path that is not a rectangle at all - lands somewhere inside it, and
     * writing THAT into the box would move the page's own geometry.
     */
    private static boolean frameIsRect(Frame f, float lineAngle) {
        float[][] c = rectCorners(f.shape);
        if (c == null) return false;
        double th = Math.toRadians(lineAngle);
        double ux = Math.cos(th), uy = Math.sin(th), vx = -Math.sin(th), vy = Math.cos(th);
        float p0x = (float) (f.cx - (f.w / 2.0) * ux - (f.h / 2.0) * vx);
        float p0y = (float) (f.cy - (f.w / 2.0) * uy - (f.h / 2.0) * vy);
        float tol = Math.max(1.5f, 0.02f * Math.min(f.w, f.h));
        for (float[] p : c) {
            float lx = (float) ((p[0] - p0x) * ux + (p[1] - p0y) * uy);
            float ly = (float) ((p[0] - p0x) * vx + (p[1] - p0y) * vy);
            if (Math.min(Math.abs(lx), Math.abs(lx - f.w)) > tol) return false;
            if (Math.min(Math.abs(ly), Math.abs(ly - f.h)) > tol) return false;
        }
        return true;
    }

    /**
     * A stamp as ONE object: its frame and every line of its text, in a single rotated text box.
     *
     * <p>WHAT THIS REPLACES, AND WHY. ae72de3 wrote each line of a stamp as a {@code w:framePr}
     * paragraph and the frame as separate shapes, because LibreOffice honours a frame and a
     * paragraph is editable. Google Docs does not honour {@code w:framePr}: the defect this
     * method answers was confirmed on a real phone - "IN ORDER" and "GOODS RECEIVED" arrived as
     * plain black upright text at the LEFT MARGIN and the green frame landed alone on a second,
     * otherwise empty page. The construct before ae72de3 was a {@code wps:wsp} text box with
     * {@code <a:xfrm rot>}, and v3.53.4's device screenshot shows that one working: the stamp
     * green, tilted about 15 degrees, inside its frame, on one page.
     *
     * <p>So the stamp is that construct again, and it is still ONE object. The box carries
     * <ul>
     *   <li>both of the page's rules, as closed sub-paths of one {@code a:custGeom} - so the two
     *       rules cannot drift against each other, which is what D-25 asked for and what
     *       {@link #stampFrames}/{@link #mergedFrame} still produce;</li>
     *   <li>every line of the stamp's text in {@code w:txbxContent}, placed inside the box at
     *       its own measured position;</li>
     *   <li>and one {@code <a:xfrm rot>}, so the frame AND the words turn together.</li>
     * </ul>
     * There is no second object to move against the first, and no {@code w:framePr} anywhere in
     * a stamp.
     *
     * <p>THE GEOMETRY, AND WHY THE BOX IS THE FRAME'S BOUNDING BOX. A renderer that will not
     * turn glyphs lays a text box's paragraphs out in the box's AXIS-ALIGNED BOUNDING BOX: it
     * applies {@code w:ind/@w:left} horizontally and {@code w:spacing/@w:before} vertically.
     * The previous construction wrote those two numbers as the line's offset ALONG and ACROSS
     * the reading direction inside a box turned by {@code <a:xfrm rot>}, so the renderer applied
     * both to the wrong axis and measured the across-offset from the bounding box's corner
     * rather than from the frame's - a 26.5 pt error on 08's blue stamp at 14 degrees, and on a
     * 90-degree stamp a complete transposition: 03's three lines came out at the top of the
     * strip running right, two of them off the page.
     *
     * <p>Expressing the box in page axes removes both errors, because the box and the bounding
     * box are then the same frame and the writer, not the renderer, decides where each run
     * starts. The frame is unaffected: its rules are still the page's own corners, projected
     * into the box's frame, so the outline is drawn exactly where the page drew it and the two
     * rules still cannot drift against each other.
     *
     * <p>WHERE EACH RUN STARTS. A run shorter than the strip goes where the page put it,
     * clamped into the strip, with the ink edge - not the baseline origin - aligned to the
     * page's, because a tilted line's glyphs overhang their origin by {@code size*sin(angle)}.
     * A run longer than the strip cannot be contained by any start point, so it is centred:
     * that is the placement that keeps the most of it on the paper (56.2 % of 03's ink lands
     * inside the outline against 30.1 % from the page's own line origin) and splits the
     * overflow instead of piling it on one side. That case is the 90-degree stamp, and it is
     * the one residual this patch does not remove - see the patch notes.
     *
     * <p>NOTHING IS CHARGED TO THE PAGE. The drawing is anchored in a zero-height carrier
     * paragraph and its text lives in {@code w:txbxContent}, which {@link #spacingTw} does not
     * count - so a stamp cannot lengthen the page it is drawn on and cannot send a line to a
     * second sheet.
     */
    private static void stampBox(StringBuilder sb, java.util.List<PdfToWord.Box> lines,
                                 Frame frame, float lineAngle, Ctx ctx) {
        double th = Math.toRadians(lineAngle);
        double ux = Math.cos(th), uy = Math.sin(th);
        double vx = -Math.sin(th), vy = Math.cos(th);
        float p0x = (float) (frame.cx - (frame.w / 2.0) * ux - (frame.h / 2.0) * vx);
        float p0y = (float) (frame.cy - (frame.w / 2.0) * uy - (frame.h / 2.0) * vy);
        // the frame's axis-aligned bounding box, which is the frame this renderer uses
        float bx0 = Float.MAX_VALUE, by0 = Float.MAX_VALUE;
        float bx1 = -Float.MAX_VALUE, by1 = -Float.MAX_VALUE;
        double[][] corners = {
                {p0x, p0y},
                {p0x + frame.w * ux, p0y + frame.w * uy},
                {p0x + frame.w * ux + frame.h * vx, p0y + frame.w * uy + frame.h * vy},
                {p0x + frame.h * vx, p0y + frame.h * vy}};
        for (double[] c : corners) {
            bx0 = (float) Math.min(bx0, c[0]); bx1 = (float) Math.max(bx1, c[0]);
            by0 = (float) Math.min(by0, c[1]); by1 = (float) Math.max(by1, c[1]);
        }
        int n = lines.size();
        float[] lx = new float[n], ly = new float[n], lpt = new float[n], Lr = new float[n];
        for (int i = 0; i < n; i++) {
            PdfToWord.Box b = lines.get(i);
            float px = b.x, py = b.y;
            if (mirrored(b)) {
                px = ctx.pageWidthPt - b.x;
                py = ctx.pageHeightPt - b.y;
            }
            // The run is upright, so its advance is horizontal: L is the length it will
            // occupy along x, which is what the placement below needs.
            float L = b.length > 0f ? b.length : Math.abs(b.right - b.x);
            if (L <= 0f) L = 1f;
            Lr[i] = L;
            float fw = bx1 - bx0;
            double dirX = Math.cos(th);
            if (L > fw) {
                // The run is longer than the strip can hold, so no start point inside it
                // contains any more of the run than another: centring it is the placement
                // that puts the overflow on both sides instead of all on one.
                lx[i] = (bx0 + bx1) / 2f - L / 2f;
            } else {
                // A tilted line's INK starts before its baseline origin: a run drawn at
                // 15 degrees has its glyph boxes reaching size*sin(15) to the left of the
                // point the page calls the line's start. An upright run has no such
                // overhang, so placing it on the origin puts its ink that far RIGHT of the
                // page's - 3.4 pt on 01, which is over the 2 pt a line is allowed before
                // it reads as unregistered. Taking the overhang off aligns ink with ink,
                // and the origin is then 3.4 pt out, which is inside the displacement
                // tolerance (clamp(0.35*size, 1.5, 4.5)).
                float over = Math.abs(dirX) >= 0.5
                        ? b.size * Math.abs((float) Math.sin(th)) : 0f;
                if (dirX <= -0.5) lx[i] = px - L + over;   // drawn right to left
                else if (Math.abs(dirX) < 0.5) lx[i] = (bx0 + bx1) / 2f - L / 2f;
                else lx[i] = px - over;                    // drawn left to right
                lx[i] = Math.max(bx0, Math.min(bx1 - L, lx[i]));
            }
            // WHERE THE INK GOES ON THE VERTICAL AXIS, NOT WHERE THE BASELINE GOES.
            //
            // The horizontal placement above is already ink-to-ink: it takes the page's
            // baseline origin, subtracts the overhang the tilted glyph boxes put before it
            // and lands the run's ink edge on the page's. The vertical placement was not,
            // and that asymmetry is the whole of the stamp displacement: the run's
            // baseline origin was copied straight off the page (`ly[i] = py`), while the
            // glyphs are written on a HORIZONTAL baseline. A page glyph's ink does not sit
            // on its baseline - it sits a fixed distance to one SIDE of it, in the text's
            // own frame - so an upright copy of a turned line lands one perpendicular
            // offset away from the ink it is copying:
            //
            //   the page's ink centre  = P + (L/2).u + k.n,  u = (cos, sin), n = (sin, -cos)
            //   the copy's ink centre  = R + (L/2).(1,0) + k.(0,-1)
            //
            // Setting the two equal and keeping the x axis as it is gives
            //
            //   R.y = P.y + (L/2).sin(theta) + k.(1 - cos(theta))
            //
            // which is exactly zero for an upright line (sin 0 = 0, cos 0 = 1) - so a
            // stamp whose text the page draws horizontally does not move by a thousandth
            // of a point - and is the full lift for the two turned cases that can be
            // measured without a tilted font:
            //
            //   theta = 180:  R.y = P.y + 2k. An upside-down glyph's ink hangs BELOW the
            //     baseline, an upright one's sits above it, so an upright copy placed on
            //     the page's baseline is one full em-rise too high. Measured on 04: the
            //     baseline is already exact there (0.06 pt, see the pen origins), and the
            //     word still read 10.90 pt off, which is 2k at 17 pt with k = 0.32 em.
            //   theta = 90:   R.y = P.y + L/2 + k. The line runs UP the page, so its ink
            //     is centred half its own length above its start. Measured on 03: 45.60 pt
            //     off on "VERIFIED FOR AUDIT", whose L/2 is 45.2.
            //
            // For a shallow tilt this is the same half-length term: a 15-degree line of
            // 166 pt has its ink centre 21.5 pt above its start, which is 01's 24.0. The
            // copy cannot be turned - Writer has no arbitrary text rotation - so what is
            // placed here is the horizontal run whose ink is centred on the page's ink,
            // which is the placement that splits the unavoidable residual over both ends
            // instead of piling all of it on the far one.
            //
            // NOTHING IS ROTATED AND NOTHING MOVES BUT THE TEXT. The outline is the same
            // freeform at the same page coordinates; this is the run's baseline inside it.
            ly[i] = py + (float) (L / 2.0 * uy) + INK_MID_EM * b.size * (1f - (float) ux);
            lpt[i] = flowLinePt(-1f, b.size, 0f);
        }
        // The box has to hold every run, and a centred run starts LEFT of the frame - so the
        // box is the union of the frame and the runs, not the frame alone. An indent cannot be
        // negative, so a box that only covered the frame would clamp the run back to its edge
        // and put the centred variant exactly where the left-aligned one is.
        float ux0 = bx0, uy0 = by0, ux1 = bx1, uy1 = by1;
        for (int i = 0; i < n; i++) {
            ux0 = Math.min(ux0, lx[i]);
            ux1 = Math.max(ux1, lx[i] + Lr[i]);
            uy0 = Math.min(uy0, ly[i] - LINE_BASE * lpt[i]);
            uy1 = Math.max(uy1, ly[i] + lpt[i]);
        }
        for (int i = 0; i < n; i++) { lx[i] -= ux0; ly[i] -= uy0; }
        bx0 = ux0; by0 = uy0;
        float bw = ux1 - ux0, bh = uy1 - uy0;
        Integer[] order = new Integer[n];
        for (int i = 0; i < n; i++) order[i] = i;
        final float[] sortKey = ly;
        java.util.Arrays.sort(order, new java.util.Comparator<Integer>() {
            public int compare(Integer a, Integer b) {
                return Float.compare(sortKey[a], sortKey[b]);
            }
        });

        Shape local = new Shape(0f, 0f, Math.max(0.1f, bw), Math.max(0.1f, bh));
        local.kind = 2;
        java.util.List<float[]> cmds = new ArrayList<>();
        Shape merged = frame.shape.mergedShape;
        if (merged != null && merged.freeform != null && !merged.freeform.isEmpty()) {
            for (float[] c : merged.freeform) {
                int type = (int) c[0];
                if (type == 3) { cmds.add(new float[]{3f}); continue; }
                cmds.add(new float[]{type, c[1] - bx0, c[2] - by0});
            }
        } else {
            cmds.add(new float[]{0f, 0f, 0f});
            cmds.add(new float[]{1f, bw, 0f});
            cmds.add(new float[]{1f, bw, bh});
            cmds.add(new float[]{1f, 0f, bh});
            cmds.add(new float[]{3f});
        }
        local.freeform = cmds;
        local.freeformClosed = false;
        long cx = Math.max(1, Math.round(bw * EMU_PER_PT));
        long cy = Math.max(1, Math.round(bh * EMU_PER_PT));
        String geomXml = geom(local, cx, cy);
        long lw = Math.max(0, Math.round(frame.shape.lineWidthPt * EMU_PER_PT));
        String lnXml = "<a:ln w=\"" + lw + "\"><a:solidFill><a:srgbClr val=\""
                + hex(frame.shape.lineRgb) + "\">" + alphaXml(frame.shape.lineAlpha)
                + "</a:srgbClr></a:solidFill></a:ln>";

        StringBuilder inner = new StringBuilder(256);
        float cursor = 0f;
        for (int k = 0; k < n; k++) {
            int i = order[k];
            float top = ly[i] - LINE_BASE * lpt[i];
            float before = Math.max(0f, top - cursor);
            cursor = cursor + before + lpt[i];
            int beforeTw = (int) Math.round(before * TWIPS_PER_PT);
            int lineTw = (int) Math.max(1L, Math.round(lpt[i] * TWIPS_PER_PT));
            int indTw = (int) Math.max(0L, Math.round(lx[i] * TWIPS_PER_PT));
            inner.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                    .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"")
                    .append(beforeTw).append("\" w:after=\"0\" w:line=\"").append(lineTw)
                    .append("\" w:lineRule=\"exact\"/>")
                    .append("<w:ind w:left=\"").append(indTw)
                    .append("\" w:right=\"0\" w:firstLine=\"0\"/></w:pPr>");
            for (PdfToWord.Run run : lines.get(i).runs) {
                if (run.text.isEmpty()) continue;
                runXml(inner, run);
            }
            inner.append("</w:p>");
        }
        anchorShape(sb, ctx, bx0, by0, 0f, 0f, bw, bh, 0f,
                geomXml, lnXml, inner.toString(), 0f, 0f);
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
        anchorAt(sb, ctx, pageX, pageY, lx, ly, wPt, hPt, inner, rotDeg, borderRgb, borderWpt,
                lInsPt, tInsPt, null);
    }

    /** The same, with the text frame turned inside an upright box - see {@link #anchorShape}. */
    private static void anchorAt(StringBuilder sb, Ctx ctx, float pageX, float pageY,
                                 float lx, float ly, float wPt, float hPt, String inner,
                                 float rotDeg, int borderRgb, float borderWpt,
                                 float lInsPt, float tInsPt, String vert) {
        String ln;
        if (borderRgb >= 0) {
            ln = "<a:ln w=\"" + Math.max(6350, Math.round(borderWpt * EMU_PER_PT))
                    + "\"><a:solidFill><a:srgbClr val=\""
                    + String.format("%06X", borderRgb & 0xFFFFFF)
                    + "\"/></a:solidFill></a:ln>";
        } else {
            ln = "<a:ln><a:noFill/></a:ln>";
        }
        anchorShape(sb, ctx, pageX, pageY, lx, ly, wPt, hPt, rotDeg,
                "<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom>", ln, inner,
                lInsPt, tInsPt, vert);
    }

    /**
     * The anchor itself, with the box's geometry and stroke given rather than assumed.
     *
     * <p>Split out of {@link #anchorAt} so that a stamp can bring its own {@code a:custGeom} -
     * both of its rules in one path - without a second copy of this element order. Everything
     * here is the schema's: simplePos, positionH, positionV, extent, effectExtent, wrap, docPr,
     * cNvGraphicFramePr, graphic. A reader that sees them out of order refuses the file.
     */
    private static void anchorShape(StringBuilder sb, Ctx ctx, float pageX, float pageY,
                                    float lx, float ly, float wPt, float hPt, float rotDeg,
                                    String geomXml, String lnXml, String inner,
                                    float lInsPt, float tInsPt) {
        anchorShape(sb, ctx, pageX, pageY, lx, ly, wPt, hPt, rotDeg, geomXml, lnXml, inner,
                lInsPt, tInsPt, null);
    }

    /**
     * The same, with the text frame turned inside an upright box.
     *
     * <p>{@code vert} is "vert270" or "vert", or null for a box whose text lies flat. It is
     * the one construct LibreOffice turns, and it needs the box's extent swapped by the
     * caller - a vertical frame wraps along its height. See {@link #stampBox}.
     */
    private static void anchorShape(StringBuilder sb, Ctx ctx, float pageX, float pageY,
                                    float lx, float ly, float wPt, float hPt, float rotDeg,
                                    String geomXml, String lnXml, String inner,
                                    float lInsPt, float tInsPt, String vert) {
        double th = Math.toRadians(rotDeg);
        double cos = Math.cos(th), sin = Math.sin(th);
        double dx = lx - wPt / 2.0, dy = ly - hPt / 2.0;
        float offXpt = (float) (pageX - wPt / 2.0 - (cos * dx - sin * dy));
        float offYpt = (float) (pageY - hPt / 2.0 - (sin * dx + cos * dy));
        // THE BOX HAS TO LAND ON THE PAPER, AND NOTHING ELSE IN THIS WRITER ASKS.
        //
        // The offset above is the page's own coordinate, written straight through. A line the
        // page drew near its right edge gets a box 12 % wider than the line plus 1.5 em (see
        // para()), and a line whose baseline origin is the END of the text - every 180-degree
        // line, whose origin comes back mirrored - gets a box that starts where the text STOPS.
        // Either way the box runs off the sheet, and a renderer that clips at the page edge does
        // not clip the box's text to a few points: it drops it. Measured at 23ffa25 by moving
        // only this offset back onto the page and changing nothing else - 401_trifold_brochure
        // 104 characters back (262 -> 366), 364_event_ticket 15,
        // 411_nested_xobject_transforms 3, 03_stamp_vertical_90deg 1: 123 characters the .docx
        // carried and the page never drew. Clamping moves nothing that already fits.
        //
        // HORIZONTALLY ONLY. The vertical analogue is the same fault - 12_stamp_across_page_break
        // writes its "12 AUG 2025" box at y = -14.8 pt, 5 characters above the top edge - but
        // pulling it down lands it ON the table it was drawn clear of, and 26_text_overlap fails
        // the document for it. A box that leaves the sheet vertically is a stamp the page put
        // outside itself; that is a placement decision, not a width the writer got wrong.
        if (rotDeg == 0f && wPt < ctx.pageWidthPt) {
            float fitX = Math.max(0f, Math.min(offXpt, ctx.pageWidthPt - wPt));
            if (fitX != offXpt) {
                anchorClamped++;
                if (System.getProperty("p2w.debugAnchors") != null) {
                    System.err.println("ANCHOR clamp x " + Math.round(offXpt) + " -> " + Math.round(fitX)
                            + " box " + Math.round(wPt) + " page " + Math.round(ctx.pageWidthPt));
                }
                offXpt = fitX;
            }
        }
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
                .append(geomXml)
                .append("<a:noFill/>")
                .append(lnXml);
        sb.append("</wps:spPr>")
                .append("<wps:txbx><w:txbxContent>").append(inner).append("</w:txbxContent></wps:txbx>")
                // wrap="none": the box must not re-wrap the line it holds, or a long line
                // would break at the box width and the second half would land under the first.
                .append("<wps:bodyPr wrap=\"none\" lIns=\"")
                .append(Math.round(lInsPt * EMU_PER_PT)).append("\" tIns=\"")
                .append(Math.round(tInsPt * EMU_PER_PT))
                .append("\" rIns=\"0\" bIns=\"0\"")
                .append(vert == null ? "" : " vert=\"" + vert + "\"")
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
    private static String borders(int[] sideSz, String[] sideColour, boolean[] sideDrawn) {
        StringBuilder b = new StringBuilder("<w:tblBorders>");
        for (int i = 0; i < TABLE_SIDES.length; i++) {
            String side = TABLE_SIDES[i];
            // One flag per side, and it is the page's own answer (PdfToWord.Table#sideDrawn):
            // the page drew a rule on this side, so this side is drawn - at that rule's weight
            // and colour - and the rule itself is dropped from the shape pass at the same time.
            // Where the page drew nothing this is "nil", and the hairline the page did draw
            // stays a shape at its own position. No side is left without an owner.
            boolean drawn = sideDrawn[i];
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
            // THE ENCLOSING-FRAME BRANCH THAT USED TO BE HERE IS GONE, AND IT WAS DRAWING THE
            // FRAME TWICE.
            //
            // It read: a stroke-only box that encloses the table, and is at least half covered
            // by it, means the page drew this table a grid, so give the table borders. The
            // reading is wrong on its own terms. Every shape in `shapes` is a Shape block on
            // the page (DocxWriter.java:850-853, `ctx.curShapes = outlines`), and the shape
            // pass draws all of them. So the frame is already on the page as its own outline
            // before this table is written. Saying "this table is ruled" does not add the
            // frame the page drew - it adds a SECOND rectangle, and a smaller one: w:tblBorders
            // is stroked on the cell grid, and the whitespace pass measures that grid from the
            // table's TEXT, while the frame the page drew sits outside the text (pageDrewRule's
            // own docstring measures that gap on 04_stamp_180deg as 8.3 pt left, 14.3 pt above,
            // 96.1 pt right). Two nested rectangles where the page had one.
            //
            // Measured, and it is the largest single cause of 59_shape_anchor's failures: on
            // 80_gstin_pan_cin_ifsc_table the page draws five 483.3x84.0 row-group frames and
            // no interior rules at all. The engine reproduced all five exactly - and then
            // wrote six tables whose outer borders trace the text extents at 64.1..484.5 x
            // 58.5 tall. The render therefore holds both, and 59's smallest-enclosing-box
            // anchors onto the invented 58.5 pt box instead of the page's 84 pt one; the text
            // sits 5 pt nearer its top inside it and every cell in the table fails. 65 runs on
            // that one document, 671 "moved" runs across the 51 non-stamp documents.
            //
            // Nothing is lost by removing it: the frame the page drew is still drawn, by the
            // shape pass, at the page's own coordinates. What goes away is the duplicate.
        }
        return false;
    }

    /**
     * How many lines the renderer will draw this cell's text on, at the cell's own width.
     *
     * <p>The width is the estimate this file already uses for a line's own advance -
     * {@code 0.5 em a character} (see {@code para()}'s {@code chars * b.size * 0.5f}) -
     * measured against the column the cell was given. It answers ONE question: does this
     * cell hold one line or several. It sets no row height, no column width and no
     * {@code w:before}, so a table it decides "wraps" is laid out at exactly the height the
     * page gave it; only the box the cell's lines advance by changes.
     *
     * <p>That is why a wrong answer here is cheap. A cell called "wraps" that does not is
     * written with the row's own line advance instead of the hairline, and since both forms
     * put the first baseline at {@code 0.8 * rowLineTw}, a one-line cell renders identically
     * either way. A cell called "one line" that wraps is the defect this exists to stop.
     */
    private static int wrapsAt(String cv, int q, int r, PdfToWord.Table t,
                               int[] colTw, int cols) {
        if (cv == null || cv.isEmpty() || q >= cols || colTw == null || q >= colTw.length) {
            return 1;
        }
        float sz = r < t.sizes.size() && q < t.sizes.get(r).size()
                && t.sizes.get(r).get(q) != null ? t.sizes.get(r).get(q) : 0f;
        if (sz <= 0f) return 1;
        int availTw = colTw[q];
        if (availTw <= 0) return 1;
        int maxChars = (int) Math.floor(availTw / (0.5f * sz * TWIPS_PER_PT));
        if (maxChars < 1) maxChars = 1;
        int best = 1;
        int from = 0;
        for (int i = 0; i <= cv.length(); i++) {
            if (i == cv.length() || cv.charAt(i) == '\n') {
                int len = i - from;
                int n = len <= 0 ? 1 : (len + maxChars - 1) / maxChars;
                if (n > best) best = n;
                from = i + 1;
            }
        }
        return best;
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
        // WHO DRAWS EACH SIDE, and it is no longer one flag for all six.
        //
        // It used to be `t.ruled || pageDrewRule(t, ctx.curShapes)`: one answer for the four
        // outer sides and, through innerH/innerV, for the two inner ones. pageDrewRule scanned
        // the shapes that had SURVIVED the shape pass - and the shape pass drops every hairline
        // that lies on or inside a table, on the claim that this writer draws it. The writer's
        // only evidence was the shapes its own input had already removed: on
        // 16_right_aligned_amounts, 13 row rules the page draws, 13 shapes dropped by
        // attachShapes, and all six sides written nil. The rule was measured, attributed and
        // thrown away - on 11 of 32_stroke_lines' 13 failing documents.
        //
        // The sides now come from PdfToWord.Table#sideDrawn, filled from the page's own rule
        // list (PdfToWord.markSideStrokes) before any shape is discarded and already reconciled
        // with the frame shapes attachShapes kept. One rule, one owner, decided by where the
        // page drew it.
        boolean ruledTable = t.ruled;
        boolean[] sideDrawn = new boolean[6];
        for (int i = 0; i < 6; i++) sideDrawn[i] = ruledTable || t.sideDrawn[i];
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
                // w:tblInd IS CELL-RELATIVE. The page's x belongs here only at body level: inside
                // a layout-table cell the renderer adds the cell's own left edge to this number,
                // so writing the page's x put the table one column-edge to the right of where
                // the page drew it. Measured on 401_trifold_brochure, whose SPECIFICATIONS table
                // sits in the third panel at page x 300.65: tblInd was 6013 twips (300.65 pt),
                // every cell of it landed at page x + 300.8 (dx +300.8 on all 10 pairs of 43,
                // which read 47 %), and 350_question_paper's nested table was 28 pt out the
                // same way. A table outside a cell subtracts nothing and is unchanged.
                .append("<w:tblInd w:w=\"")
                .append(tw(x0 - (ctx.inColumn ? ctx.cellLeftPt : 0f)))
                .append("\" w:type=\"dxa\"/>")
                // A named table style, so the table carries a style of its own rather than
                // falling back on a reader's default. It draws no borders and sets no colour.
                .append("<w:tblStyle w:val=\"KavoTable\"/>")
                // Each side on its own evidence. The ruled pass reads the grid itself, so its
                // tables are ruled all over; a whitespace table has a frame round it (the four
                // outer sides) and separators inside it only where the page drew them. A table
                // with no frame at all keeps all six undrawn even when a rule crosses its band:
                // that rule is as likely the edge of a filled band as a drawn separator, and a
                // line the page did not draw is the defect 403 and 406 came back with.
                .append(borders(sideSz, sideColour, sideDrawn))
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
        // NOT SUBTRACTED. A ruled row was written TABLE_BORDER_TW (0.75 pt) short of the page's
        // own pitch, on the theory that the renderer adds that rule to the row. Measured, it does
        // not: a row whose height is set by w:trHeight renders at that height with or without its
        // borders (trHeight=260 -> 13.0 pt either way), and only a row whose height is decided by
        // its own CONTENT pays the rule (content 21.0 -> 21.7 bordered, 21.0 without). So the
        // subtraction made every w:trHeight-driven row 0.75 pt short - and because it was applied
        // to every row of every ruled table, the error was one sign and cumulative: on
        // 324_loan_amortisation_schedule, 13.0 pt rows written as 245 twips (12.25 pt) put the
        // rows out by +1.3, +0.5, -0.2, -1.0 ... -5.5 pt down one table, and six pages of that
        // document failed 18_displacement for it. With the subtraction gone the same document's
        // rows land on the page's pitch and 18_displacement passes 6 pages of 6.
        //
        // The border is therefore a rendering artefact the page must not pay for, in the row
        // height or in the budget: the row is written at the page's pitch, and the flow charge
        // after the loop reads the same number these rows are written at.
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
        // THE RULE IS ADDED TO THE ROW, NOT INCLUDED IN IT - and that is the whole of the
        // +2 pt-a-row ramp inside a table.
        //
        // The comment above ("NOT SUBTRACTED") is right about the case it measured and wrong
        // about this one. What the renderer does, measured on 404_sudoku_grid by rewriting only
        // the table's own numbers and rendering each form (LibreOffice 7.4.7.2):
        //
        //   row border-box = max(w:trHeight, cell content height + horizontal rule width)
        //
        // so a row is NOT "at that height with or without its borders" - it is at that height
        // only while its CONTENT is smaller than trHeight. The earlier probe compared a row
        // whose content was far below trHeight, where the rule cannot show; and its second
        // measurement (content 21.0 -> 21.7 bordered) is the same rule seen from the other
        // side. Here the cell's own w:line IS the row's pitch (see cellLineHere below), so the
        // content is exactly the pitch, the rule is charged on top of it, and every row comes
        // out one rule too tall.
        //
        // Measured, same document, one number changed at a time:
        //   trHeight 880 + cell line 880 + sz 16 (2 pt)   -> 46.0 pt rows  (the engine's form)
        //   trHeight 840 + cell line 840 + sz 16          -> 44.0 pt rows
        //   trHeight 880 + cell line 840 + sz 16          -> 44.0 pt rows  (trHeight is a FLOOR)
        //   trHeight 880 + cell line 880 + sz 6 (0.75)    -> 44.8 pt rows
        //   trHeight 840 + cell line 840 + sz 0           -> 42.8 pt rows
        // and the page's own pitch for that table is 44.0 pt, its rules 0.5 pt. So the page's
        // 44 pt rows are laid out 46 pt apart, each row's text sits at a constant 15.6 pt below
        // its own row's top rule - the placement is right - and every row down the table is
        // 2.00 pt lower than the page drew it. That is the ramp: tdy = 1.28, 3.28, 5.28 ... 17.28
        // over 404_sudoku_grid's nine rows, with the box identical on both sides, because the
        // box the check reads is the cell frame, which the renderer still draws at trHeight.
        //
        // It is NOT the font's line height. A font-driven row would be 28.5 + 20.95 = 49.45 pt
        // of content and 51.5 pt with its rule, and it would move when w:before moves: measured
        // 51.5 for w:line="13" hRule="atLeast" (the renderer expands "atLeast" to the face's
        // 1.164 em) and 51.5 for w:line="419" exact, while w:before 570 / 310 / 0 all lay out
        // 46.0. The 46 is 44 + 2, and 2 is the rule.
        //
        // So the row is written a rule short, in BOTH places the pitch appears: the w:trHeight
        // floor and the cell's own w:line. Reducing only trHeight does nothing here (the cell's
        // line is the binding content), and reducing only the line leaves the floor high.
        // A side the page did not draw adds nothing, so the widths come from the same
        // drawn-ness the w:tblBorders element is written from, and are halved per row because
        // half of each rule lies inside the row above and half inside the row below.
        boolean hRuleTop = ruledTable;
        boolean hRuleBottom = ruledTable;
        boolean hRuleInside = ruledTable && (t.ruled || t.innerH);
        int szRuleTop = hRuleTop ? sideSz[0] : 0;        // TABLE_SIDES: top
        int szRuleBottom = hRuleBottom ? sideSz[2] : 0;  // bottom
        int szRuleInside = hRuleInside ? sideSz[4] : 0;  // insideH
        // The height this table is really written at: the sum of the row heights below. It is
        // what the page budget must read (see the flow charge after the loop).
        int writtenRowsTw = 0;
        // WHAT THE LAST ROW LEAVES UNDER ITS OWN TEXT - see the flow anchor after the table.
        // Only the last row can be seen by the flow, because it is the only one the next
        // paragraph is spaced from.
        int lastRowHeightTw = 0;
        int lastRowContentTw = 0;
        float lastRowTopPagePt = Float.NaN;
        // The running top edge of a re-cut table's rows, in points from the page top: its rows
        // are stacked from the table's own top, so row 2 starts one WRITTEN row below row 1.
        float recutTopPt = Float.NaN;
        float rowTopPagePtHere = Float.NaN;
        for (int r = 0; r < t.rows.size(); r++) {
            List<String> row = t.rows.get(r);
            // This row's own pitch. A ruled table's rule lies inside the row's box, so it comes
            // off here exactly as it comes off the average above.
            int rowTwHere = rowTw;
            if (exactRows) {
                float pitchPt = rowEdge[r + 1] - rowEdge[r];
                if (pitchPt > 0.5f && pitchPt < 2000f) {
                    rowTwHere = (int) Math.round(pitchPt * TWIPS_PER_PT);
                }
            }
            // The rule this row pays: half of the rule above it plus half of the rule below it.
            int szAbove = r == 0 ? szRuleTop : szRuleInside;
            int szBelow = r == t.rows.size() - 1 ? szRuleBottom : szRuleInside;
            int ruleTwHere = (int) Math.round((szAbove + szBelow) * TWIPS_PER_PT / 16.0);
            // THE PITCH STAYS THE PAGE'S PITCH; THE CELL'S CONTENT IS WHAT COMES OFF.
            // The renderer lays a row out at max(w:trHeight, cell content + rule). Two different
            // rows need two different answers from that, and only one form satisfies both:
            //   a row whose content is the pitch      content + rule = pitch + rule  -> too tall
            //   a row whose content is below it       the trHeight floor binds    -> already right
            // So w:trHeight keeps the page's pitch (the floor is what a short row needs) and the
            // cell's own w:line is capped a rule below it. Then content + rule <= pitch for every
            // row, the floor is never exceeded, and the row is laid out at the page's pitch
            // whichever of the two was binding. Subtracting from w:trHeight instead was measured
            // and is wrong: it shortens every row whose content was already below the pitch, and
            // on electricity-bill's 18.4 pt rows (0.5 pt rules) that turned an 18.0/19.0
            // alternation into 17.5/18.5 - 18_displacement gained more documents than it fixed.
            int pitchTwHere = rowTwHere;
            int contentTwHere = rowTwHere > 0 && ruleTwHere > 0
                    ? Math.max(1, rowTwHere - ruleTwHere) : rowTwHere;
            // The line inside the cell follows the row it is in: a cell's text is drawn at the
            // foot of its own row on most of this corpus, so the line height is the row's pitch.
            int cellLineHere = contentTwHere > 0 ? contentTwHere : 200;
            int naturalLineHere = contentTwHere > 0 ? Math.min(contentTwHere, 200) : 200;
            // Does any cell of this row hold more than one line of the page? A numbered item's
            // marker, a calendar's holiday name under its date, a two-line address in a box.
            int rowParts = 1;
            int nlParts = 1;
            int wrapParts = 1;
            for (int q = 0; q < row.size() && q < cols; q++) {
                String cv = row.get(q);
                if (cv == null) continue;
                int n = 1;
                for (int i = 0; i < cv.length(); i++) if (cv.charAt(i) == '\n') n++;
                // A CELL THE RENDERER WILL WRAP IS A CELL THAT HOLDS SEVERAL LINES.
                //
                // rowParts used to count only the '\n' the model carries, so a cell the
                // page drew on one line - and that the engine then put text into that is
                // wider than the cell - kept rowParts == 1 and was written with the
                // HAIRLINE box (0.069 em, 0.4 pt at 8 pt). Every line the renderer wrapped
                // out of that one paragraph was then charged 0.4 pt, so line 2 landed on
                // line 1 and so on: 26_text_overlap's BOX class, one w:p holding N lines.
                // Counting the wrap here is what routes such a cell to the rowParts > 1
                // branch, whose box IS the line advance.
                int w = wrapsAt(cv, q, r, t, colTw, cols);
                if (n > nlParts) nlParts = n;
                if (w > wrapParts) wrapParts = w;
                int m = Math.max(n, w);
                if (m > rowParts) rowParts = m;
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
            // The budget is charged what the renderer will LAY OUT, which is the content plus
            // the rule - not the content alone. Charging the content alone under-measures every
            // ruled table by one rule a row, and this is the number the flow after the table is
            // placed from.
            writtenRowsTw += Math.max(0, Math.max(pitchTwHere,
                    Math.max(rowTwHere, rowLineTw) + ruleTwHere));
            // THE ROW'S OWN TOP EDGE IN THE PAGE'S COORDINATES, when the pass that built the
            // table measured the row edges. The cells below are placed from it.
            //
            // From the PAGE's edges, not from the flow's position. Placing them from the flow
            // was built and measured first and it costs a document: on
            // 64_newspaper_uneven_columns_ad_boxes the flow's own position is 15 pt high, so
            // every cell inherited that 15 pt and the ad grid came back at 102.4 where the page
            // has it at 122.0 - 07_table_rows 6 -> 12 and 46_text_crossing_rule 0 -> 17. The
            // page's row edges carry no flow error at all, and a cell's distance below its own
            // row's top is exactly what this is asking for.
            //
            // The two passes record their edges differently: the ruled pass's rowEdge are the
            // rules the page drew, while the whitespace pass's are the rows' first BASELINES
            // (see PdfToWord, where rowTopPt is rowEdge[0] less LINE_BASE of a pitch). Reading
            // a baseline as an edge would put every cell of a whitespace table on its row's top
            // rule, so the baseline is converted back to an edge here.
            // A CELL THAT CARRIES THE PAGE'S OWN PARAGRAPHS OCCUPIES WHAT THEY ADD UP TO.
            //
            // A re-cut band grid's rows are not the page's rules any more: row 0 is a spanning
            // band and row 1 is the whole of the columns. The page's own extent cannot describe
            // either of them, so the CONTENT does - every line's box plus every gap between the
            // baselines the page drew. Declaring the row at the grid's extent instead put
            // 64_newspaper_uneven_columns_ad_boxes' row at 726.1 pt against the 723.89 the sheet
            // had left, and the renderer took the larger of the two and broke the page.
            int paraContentTw = 0;
            if (t.recut) {
                for (int q = 0; q < cols; q++) {
                    paraContentTw = Math.max(paraContentTw,
                            cellParasTw(t, r, q, recutTopPt, rowLineTw));
                }
            }
            if (paraContentTw > 0) {
                // A FLOOR, never a cap: the page's own row extent stays the geometry, so the
                // table's frame closes where the page drew it, and the content only matters
                // when it is TALLER than that - which is the case that used to overflow.
                // The rule is added because the renderer lays a row out at content + rule
                // (see the note above on 404_sudoku_grid).
                rowHeightTw = Math.max(rowHeightTw, paraContentTw + ruleTwHere);
            }
            // WHERE THIS ROW REALLY STARTS. A re-cut table's rows are stacked from its own top
            // edge, so the second row starts one WRITTEN row below the first - not at the rule
            // the page drew, which is 44 pt down on 64_newspaper_uneven_columns_ad_boxes while
            // its spanning band is written 32 pt tall. Placing the cells from the rule put every
            // column of that page 13.5 pt low.
            if (t.recut) {
                if (Float.isNaN(recutTopPt)) recutTopPt = t.rowTopPt;
                rowTopPagePtHere = recutTopPt;
                recutTopPt += rowHeightTw / (float) TWIPS_PER_PT;
            }
            float rowTopPagePt = Float.NaN;
            if (exactRows) {
                float edgePt = rowEdge[r];
                if (!t.ruled) {
                    float pitchHere = rowEdge[r + 1] - rowEdge[r];
                    if (pitchHere > 0.5f && pitchHere < 2000f) edgePt -= LINE_BASE * pitchHere;
                }
                rowTopPagePt = edgePt;
            }
            if (!Float.isNaN(rowTopPagePtHere)) rowTopPagePt = rowTopPagePtHere;
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
                // The style the page drew this cell in. `faceName` below strips the style word
                // out of the name, so the name is not a description of the cell's style any
                // more; these two flags are the model's own record of it.
                boolean cellBold = boldOf(t, r, c);
                boolean cellItalic = italicOf(t, r, c);
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
                // THE CELL'S LINE BOX IS THE SAME QUESTION AS THE FLOW'S. A cell that holds one
                // line of the page is charged that row's pitch, and the two renderers read the
                // w:line that carries it differently (see HAIRLINE_EM): Google charges a
                // multiple of the substitute face's line height, so a 10 pt row pitch written as
                // w:line=200 puts a 7 pt cell's text 0.8 * 5.5 = 4.4 pt lower in Google than in
                // Word. The row height is w:trHeight's business, so the box may be a hairline
                // here too: the gap carries the rest of the pitch and both renderers charge
                // 0.069 em. A cell the page drew on SEVERAL lines keeps the old box - there the
                // box IS the line advance, and a hairline would collapse the cell.
                //
                // WHY THE TWO ENGINES CANNOT BE MADE TO AGREE HERE - THE PROOF, kept because
                // it is the reason this path is "the closest emission there is" rather than an
                // exact one, and because a later attempt will otherwise be made.
                //
                // w:before is the one vertical length both engines honour exactly and
                // identically - Google returned 20/40/80/120/160 pt as 20/40/80/120/160
                // (REMAINING-DEFECTS.md, "The model, measured", point 2). So w:before moves
                // BOTH baselines by the same amount and can never close the gap between them.
                // The gap is the box, and the box is read two ways (see HAIRLINE_EM):
                //   LibreOffice  charges LINE_BASE of the box
                //   Google       charges max((w:line/240) * lineHeight(face, size), 0.069 * size)
                // Cut the box to a twip and put the whole pitch in w:before and the two read
                //     LibreOffice  before + 0.05
                //     Google       before + 0.069 * size
                // so the residual is 0.069 * size - 0.05 pt, zero only at size = 0.72 pt.
                // Asking instead for Google's baseline to sit at the FOOT of the row - the
                // place this corpus draws its cell text - needs 0.069 * size = LINE_BASE *
                // pitch, i.e. 0.8 * 18 / 0.069 = 208.7 pt for an 18 pt row. Both are absurd,
                // so no (w:line, w:before) pair is exact for a cell. Measured over the corpus,
                // that pair's residual is a median 0.44 pt against 3.70 pt for the old box -
                // better, and still not zero.
                //
                // WHAT THIS CODE DOES WITH IT. Keeping part of the pitch in the BOX buys
                // accuracy, because LibreOffice charges 0.8 of the box while Google floors at
                // 0.069 em: the residual becomes 0.069 * size - 0.8 * box, i.e.
                // 0.2 * 0.069 * size = 0.12 pt at 8.5 pt for the box written below, against
                // 0.54 pt for a one-twip box with the whole pitch in w:before. On a 12-cell
                // 18 pt table this file emits before=266 line=12 where that form emits
                // before=276 line=1. The 0.069 em charge only holds while the box stays inside
                // Google's floor - w:line <= 16.56/r twips, 12.97 at Liberation Serif's
                // r = 1.277 - which is why hairlinePt is 0.069 em and why the agreement
                // degrades above 12/r = 9.4 pt.
                //
                // AND IT IS A WASH WHERE IT WAS MEASURED, so do not re-open it as a fix: the
                // one-twip form was built and measured in LibreOffice over the corpus and
                // moved 10,770 -> 10,760 of 12,027 checks, 24 documents better and 16 worse.
                // LibreOffice was never the engine at fault. What is left is the bound above,
                // not a bug.
                float cellSz = r < t.sizes.size() && c < t.sizes.get(r).size()
                        && t.sizes.get(r).get(c) != null ? t.sizes.get(r).get(c) : 0f;
                // The page's own baseline for this cell, when the pass that built the table
                // measured it. This is the fix for the offset REMAINING-DEFECTS.md records as
                // unfixed: the writer put EVERY cell at LINE_BASE of the row's pitch, so a page
                // that drew its cell text at 0.65 of the pitch came back 0.15 * pitch low on
                // every row - a constant +2.75 pt on 318_court_summons_form's 18 pt rows, over a
                // 2.6 pt tolerance. Measured over 2,343 table runs whose row the page bounds with
                // rules: the page's own fraction spans 0.0-0.9, quartiles 0.53/0.576/0.67, and
                // 95 of 2,343 are at the 0.8 the writer assumed.
                //
                // The row must not grow, so the request is clamped to the row's own written
                // height: before + box is the cell's content height, and w:trHeight is "atLeast".
                //
                // AND THE BASELINE MUST BE AT LEAST ONE ASCENT BELOW THE ROW'S TOP EDGE. A
                // baseline nearer than the text is tall puts the glyphs above the row's top rule,
                // which is not something a page draws: where the measurement says that, the
                // model's row edge is wrong and not the placement. On
                // 64_newspaper_uneven_columns_ad_boxes the ad grid's rows are 56 pt tall and the
                // measured baseline sits 2.9 pt below one of them - 46_text_crossing_rule went
                // 0 -> 15 and 07_table_rows 6 -> 10. Those cells keep the old foot-of-the-row
                // placement; the page's fraction is used only where it is a placement at all.
                float cellBaseY = yOf(t, r, c);
                boolean cellPlaced = false;
                int cellBoxTw = cell.isEmpty() ? EMPTY_CELL_LINE_TW : rowLineTw;
                int cellBeforeTw = 0;
                // The box this cell's lines advance by. One line: the hairline, and the
                // baseline is placed at the page's own fraction of the row. Several lines:
                // the line advance, and the FIRST line keeps that same placement.
                int boxHere = rowParts > 1
                        ? (int) Math.max(1L, Math.round(rowLineTw))
                        : (int) Math.max(1L, Math.round(hairlinePt(cellSz) * TWIPS_PER_PT));
                // WHEN THE WRAP IS WHAT MADE THE ROW MULTI-LINE, the N lines SPLIT the space
                // below the row's own first baseline instead of each taking min(pitch, 10 pt).
                if (wrapParts > nlParts && wrapParts > 1 && rowTwHere > 0) {
                    int split = (int) Math.round((double) rowTwHere / wrapParts);
                    if (split > 0) boxHere = Math.min(boxHere, split);
                }
                if (cellSz > 0f && !Float.isNaN(cellBaseY)
                        && !Float.isNaN(rowTopPagePt)) {
                    float wantPt = cellBaseY - rowTopPagePt;
                    // A cell is PLACED from its own measured baseline as long as that baseline is
                    // anywhere in the row - the acceptance test reads the row, not the content, so
                    // a cell drawn at the foot of its row keeps its measurement and is clamped by
                    // the cap below rather than thrown back to the fallback. Reading the cap here
                    // instead pushed 9 cells of mutual-fund-statement 3.8 pt up: their measured
                    // baseline was 18.5 pt into a 19 pt row, which is inside the row and outside
                    // the row less its rule.
                    float roomPt = rowHeightTw / (float) TWIPS_PER_PT;
                    if (wantPt >= LINE_BASE * cellSz && wantPt <= roomPt) {
                        int boxTw = boxHere;
                        int beforeTw = (int) Math.round(
                                (wantPt - LINE_BASE * boxTw / (float) TWIPS_PER_PT) * TWIPS_PER_PT);
                        int capTw = Math.max(0, Math.min(rowHeightTw, contentTwHere) - boxTw);
                        cellBoxTw = boxTw;
                        cellBeforeTw = Math.max(0, Math.min(beforeTw, capTw));
                        cellPlaced = true;
                    }
                }
                if (!cellPlaced && cellSz > 0f) {
                    cellBoxTw = boxHere;
                    // The baseline inside a box sits LINE_BASE of the box below its top, and the
                    // old pair (before=0, box=rowLineTw) put it at LINE_BASE * rowLineTw - the
                    // foot of the row, which is where this corpus draws its cell text. Keep that
                    // foot: before = LINE_BASE * (rowLineTw - box), so
                    // before + LINE_BASE * box = LINE_BASE * rowLineTw, unchanged. Writing
                    // before = rowLineTw - box instead moved every cell 0.2 * row pitch lower
                    // and 18_median_dy went 64 -> 100 documents.
                    cellBeforeTw = Math.max(0,
                            Math.round(LINE_BASE * (rowLineTw - cellBoxTw)));
                }
                // AN EMPTY CELL CARRIES NO LINE, so its box must not be the row's pitch.
                //
                // Both branches above are keyed on cellSz > 0f, which is the size of the text
                // the page drew in the cell. An empty cell has no text, so cellSz is 0, so
                // neither branch runs and the box stays at rowLineTw - the row's whole pitch -
                // with before = 0. That is a paragraph one full pitch tall inside a row whose
                // w:trHeight is the same pitch, and LibreOffice renders such a row 0.35 pt
                // TALLER than the pitch the page drew (measured below).
                //
                // The row's height is already carried by w:trHeight w:hRule="atLeast", which
                // is written from rowHeightTw >= rowLineTw, so the empty cell's own box adds
                // nothing but this overhang. A hairline box adds nothing at all: the row is
                // the page's own pitch and every row below it starts where the page put it.
                //
                // MEASURED, 320_balance_sheet_statutory, one 16-row table on a 14 pt pitch,
                // the empty-cell box set to each value in turn and the document re-rendered:
                //     box =   1 tw   14.0 14.0 14.0 14.0 14.0   (pitches between baselines)
                //     box = 140 tw   14.0 14.0 14.0 14.0 14.0
                //     box = 200 tw   14.0 14.0 14.0 14.0 14.0
                //     box = 280 tw   14.0 14.0 14.0 14.4 14.3   <- the pitch itself
                // The overhang appears only when the empty paragraph's box reaches the row's
                // own trHeight, and it is charged to EVERY row that has an empty cell: that
                // document's seven such rows drifted +0.35 pt each, the table's last row
                // finished 4.25 pt low and the signature block under it 4.61 pt, and
                // 18_displacement read 14 runs out on a page where no text had been moved.
                // With the hairline the same page reads 0 runs out, max |dy| 0.45 pt.
                //
                // Guarded on rowTwHere > 0: that is exactly when w:trHeight is written and
                // the row's height is therefore not the cells' business. Where the table has
                // no row pitch at all (rowTwHere == 0, no trPr) a row of empty cells IS sized
                // by its content, and a hairline there would collapse the row to nothing.
                if (cell.isEmpty() && rowTwHere > 0) {
                    cellBoxTw = 1;
                    cellBeforeTw = 0;
                }
                // ONE CELL, SEVERAL PARAGRAPHS.
                //
                // Everything above places ONE paragraph in the cell: one w:before, one w:line,
                // one face, one size, one colour. That is the model's limit - `rows` is a
                // string - and it is why a cell the page drew five lines in was written as one
                // welded run at a single box. Where the model carries the page's own lines
                // (Table#paras) each one is written as its own paragraph, at its own leading,
                // with the page's own gap above it and its own face, size, colour and weight.
                java.util.List<PdfToWord.Table.CellPara> cps = t.parasAt(r, c);
                if (cps.size() >= 2) {
                    int box0 = paraBoxTw(cps, 0, rowLineTw);
                    int before0 = cellBeforeTw;
                    if (!Float.isNaN(cellBaseY) && !Float.isNaN(rowTopPagePt)
                            && cps.get(0).size > 0f) {
                        float wantPt = cellBaseY - rowTopPagePt;
                        if (wantPt >= LINE_BASE * cps.get(0).size) {
                            before0 = (int) Math.max(0L, Math.round(
                                    (wantPt - LINE_BASE * box0 / (float) TWIPS_PER_PT)
                                            * TWIPS_PER_PT));
                        }
                    }
                    int stackTw = before0;
                    // TOP-ALIGNED, because every line in this cell is placed at an ABSOLUTE y:
                    // w:before carries the page's own distance from the row's top edge. A cell
                    // that is centred instead is a cell whose content is shifted by half the
                    // slack between the row's trHeight and what it holds - measured on
                    // 64_newspaper_uneven_columns_ad_boxes as a flat +2.2 pt on all 77 lines,
                    // which is half of the 3.8 pt its spanning row had spare.
                    inner.append("<w:vAlign w:val=\"top\"/></w:tcPr>");
                    for (int q = 0; q < cps.size(); q++) {
                        PdfToWord.Table.CellPara cp = cps.get(q);
                        // THE LINE ADVANCE IS THE BOX, and it is the page's own leading: a
                        // cell's paragraphs are the lines the page drew, so the distance to the
                        // next one IS the advance. w:before then carries only a paragraph gap.
                        int boxTw = paraBoxTw(cps, q, rowLineTw);
                        int beforeTw = q == 0 ? before0 : paraBeforeTw(cps, q, rowLineTw);
                        stackTw += (q == 0 ? 0 : beforeTw) + boxTw;
                        int pInset = Float.isNaN(cp.indentPt) ? insetTw
                                : (int) Math.max(0L, Math.round(cp.indentPt * TWIPS_PER_PT));
                        cellParaXml(inner, cp, beforeTw, boxTw, pInset, cellSz);
                    }
                    if (r == t.rows.size() - 1) {
                        lastRowContentTw = Math.max(lastRowContentTw, stackTw);
                    }
                    inner.append("</w:tc>");
                    c += span;
                    continue;
                }
                inner.append("</w:tcPr>")
                        .append("<w:p><w:pPr><w:pStyle w:val=\"TableText\"/>")
                        .append("<w:snapToGrid w:val=\"0\"/>")
                        .append(spacing(cellBeforeTw, cellBoxTw, cellSz, autoCellBoxes(), false));
                if (insetTw > 0) inner.append("<w:ind w:left=\"").append(insetTw).append("\"/>");
                inner.append("</w:pPr>");
                if (!cell.isEmpty()) {
                    inner.append("<w:r><w:rPr>");
                    // Written in schema order - rFonts, b, i, color, sz, szCs. It was sz, szCs,
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
                    // The flag the table model now carries is the FIRST evidence: it is what the
                    // page drew, where `isBoldFace` is a guess about a face NAME that
                    // `faceName` has already stripped. 34c's own note records 23 documents on
                    // which the name test and the flag disagree, and the flag is the right one
                    // there. The name stays as the fallback for a pass that recorded no flag.
                    if (cellBold || isBoldFace(face) || (r == 0 && t.header && face.isEmpty())) {
                        inner.append("<w:b/>");
                    }
                    // Italic. Nothing wrote it before: a paragraph run has carried `w:i` from
                    // Run#italic all along (runXml, line 3452), but a cell is not a run, so the
                    // face name's "Italic" was stripped by faceName and no `w:i` replaced it -
                    // 64_newspaper_uneven_columns_ad_boxes draws two italic spans and the .docx
                    // carried none. Written after w:b because that is the schema's order.
                    if (cellItalic) {
                        inner.append("<w:i/>");
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
                        if (q > 0) {
                            // The break must carry a SPACE with it. A cell holds two lines of
                            // the page, and a line break is a word boundary to a reader but
                            // nothing at all to a text extractor: the words either side of a
                            // bare <w:br/> come out welded. Measured on 77_arabic_rtl_document,
                            // whose item cells hold "،قهوة عربية مغسولة" over "غربال17",
                            // "قهوة روبوستا، غربال" over "15" and "شحن إلى ميناء" over
                            // "نيوبورت": the docx read "مغسولةغربال17", "غربال15" and
                            // "ميناءنيوبورت", so four words a reader sees on two lines counted
                            // as none of them.
                            if (!parts[q - 1].isEmpty() && !parts[q - 1].endsWith(" ")) {
                                inner.append("<w:t xml:space=\"preserve\"> </w:t>");
                            }
                            inner.append("<w:br/>");
                        }
                        inner.append("<w:t xml:space=\"preserve\">").append(esc(parts[q]))
                                .append("</w:t>");
                    }
                    inner.append("</w:r>");
                }
                inner.append("</w:p></w:tc>");
                // The depth this cell's own text occupies: its w:before plus one exact line box
                // per line the cell holds. It is the number the renderer lays the cell out
                // with, and the row is w:trHeight tall whatever this says - the difference is
                // the slack the flow anchor after the table is about.
                if (r == t.rows.size() - 1) {
                    int lines = Math.max(1, cell.split("\n", -1).length);
                    lastRowContentTw = Math.max(lastRowContentTw,
                            cellBeforeTw + lines * cellBoxTw);
                }
                c += span;
            }
            if (r == t.rows.size() - 1) {
                lastRowHeightTw = rowHeightTw;
                lastRowTopPagePt = rowTopPagePt;
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
        boolean carrier = !ctx.nextIsPara;
        if (carrier) {
            sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                    .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"")
                    .append(POST_TABLE_TW).append("\" w:lineRule=\"exact\"/>")
                    .append("<w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr></w:p>");
        }
        // The table is part of the flow too. Left out of the accounting, the paragraph after it
        // was spaced from the last line BEFORE the table, so a table's whole height was added
        // on top of the next paragraph's gap and the flow ran long.
        // Charged as the page will write it: the extent through the squeeze, because the rows
        // above were written through it too. A charge that ignores the squeeze is a page that
        // believes it has room it does not have.
        ctx.flowTw += (writtenRowsTw > 0
                ? twScale(writtenRowsTw, ctx.squeeze)
                : twScale((int) Math.round(Math.max(0f, extentPt) * TWIPS_PER_PT), ctx.squeeze))
                + (carrier ? POST_TABLE_TW : 0);
        // THE FLOW CONTINUES FROM THE LAST ROW'S BOX BOTTOM, NOT FROM ITS TEXT.
        //
        // This is the ~4 pt step at a table-to-flow boundary. A row is written
        // w:trHeight="atLeast" at the page's own pitch, and its cell's text is placed at
        // LINE_BASE (0.8) of that pitch - the foot of the row, which is where this corpus
        // draws its cell text. The cell's text therefore stops short of the row's box bottom,
        // and the renderer measures the NEXT paragraph's w:before from the BOX. Anchoring the
        // flow to the text loses that difference, and every paragraph after the table lands
        // that much too low - a flat constant for the rest of the flow, which is the shape
        // 18_displacement reads.
        //
        // WHERE THE ANCHOR WAS WRONG, AND WHERE IT WAS ONLY WRONG BY LUCK. t.bottom does not
        // mean one thing: the ruled pass sets it to the grid's last rule, which IS the last
        // row's bottom edge, and the whitespace pass sets it to the last row's BASELINE
        // (PdfToWord: `bottom = Math.max(bottom, cell.y)`). Measured on the corpus with the
        // engine's own numbers printed at the boundary: 42_table_coloured_header_alternating
        // _rows has t.bottom 293.30 against rowEdge[8] 313.30 - a baseline, one pitch above
        // the box - while electricity-bill's ruled table has t.bottom 169.00 and rowEdge[5]
        // 169.00 - the edge itself. So the ruled pass closed and the whitespace pass did not,
        // which is why the step is in the whitespace-found tables.
        //
        // MEASURED, not reasoned. Synthetic single-row tables rendered through LibreOffice,
        // cell content 16.1 pt, after-paragraph before+line 24.8 pt: row 20.0 pt -> the render
        // advances 28.70 = 24.8 + 3.9, and 3.9 is exactly trHeight - content; row 40.0 ->
        // 48.70 (+23.9); content 10.6 in a 20 pt row -> +9.40; content 25.6 in a 20 pt row
        // (the row grows to its content) -> +0.00. The excess is max(0, trHeight - content) to
        // 0.02 pt over five configurations, and it is the same whether the row is ruled or
        // not, because the renderer sees only the row's box. The borders the writer emits add
        // a further 0.20 pt (the bottom rule less the top rule), which is left unmodelled and
        // is the residual quoted in the patch note.
        //
        // So the anchor is the last row's box bottom, built from the same row edge the cells
        // were placed from - which is the edge for a ruled table and the converted edge for a
        // whitespace one - and falling back to the written row height less the written cell
        // content where the page's row edges were not measured.
        float rowBottomPt = t.bottom;
        if (!Float.isNaN(lastRowTopPagePt) && lastRowHeightTw > 0) {
            rowBottomPt = lastRowTopPagePt + lastRowHeightTw / (float) TWIPS_PER_PT;
        } else {
            rowBottomPt = t.bottom
                    + Math.max(0, lastRowHeightTw - lastRowContentTw) / (float) TWIPS_PER_PT;
        }
        ctx.lastBaseline = rowBottomPt;
        ctx.lastSize = 0f;
        // The box under the cell's text is the row's, and it is charged here rather than
        // carried as a line box: lastLinePt stays 0 and the whole of it is in the anchor above.
        ctx.lastLinePt = 0f;
        // The flow's real position after a table is the row's box bottom plus the 4 pt carrier
        // Word requires after it, because that carrier is a line the next paragraph starts under
        // (D-26: the position is where the reader is, not where the PDF drew).
        ctx.flowY = rowBottomPt
                + (carrier ? POST_TABLE_TW / (float) TWIPS_PER_PT : 0f);
        ctx.flowBoxPt = 0f;
        ctx.newPage = false;
        ctx.lastWasTable = true;
    }

    /**
     * The advance of one line of paragraph {@code q} of a cell, in twips.
     *
     * <p>A cell's paragraphs are the lines the page drew, so the distance to the NEXT paragraph
     * is the leading the page used - the one number a welded cell could never carry. Where the
     * next paragraph is not a line below (a gap, a different block) the leading is 1.2 em of
     * this paragraph's own size, which is the face's own box and not the row's tallest type.
     */
    private static int paraBoxTw(java.util.List<PdfToWord.Table.CellPara> cps, int q,
                                 int fallbackTw) {
        PdfToWord.Table.CellPara cp = cps.get(q);
        float sz = cp.size > 0f ? cp.size : 0f;
        if (q + 1 < cps.size()) {
            float dy = cps.get(q + 1).baseY - cp.baseY;
            // A LINE is at most 1.4 em away; anything further is a PARAGRAPH GAP, and a gap
            // belongs in the next paragraph's w:before, not in this one's box. Reading the gap
            // as the box put the first baseline of every paragraph that follows a gap half a
            // gap too low - measured on 64_newspaper_uneven_columns_ad_boxes as a flat +63.6 pt
            // on the middle column, where the 15 pt headline above it sits 30 pt above its
            // body.
            if (dy > 0f && (sz <= 0f || dy <= 1.4f * sz)) {
                return (int) Math.max(1L, Math.round(dy * TWIPS_PER_PT));
            }
        }
        if (sz > 0f) return (int) Math.max(1L, Math.round(1.2f * sz * TWIPS_PER_PT));
        return Math.max(1, fallbackTw);
    }

    /**
     * The gap above paragraph {@code q}, in twips, from the two baselines.
     *
     * <p>A baseline sits LINE_BASE of its own box below the box's top, so the distance between
     * two baselines is 0.2 of the first box, plus the gap, plus 0.8 of the second. Asking for
     * the page's own baselines therefore means solving for the gap, not subtracting the box -
     * which is right only when the two boxes are the same, and a 15 pt headline over 9 pt body
     * text is exactly the case where they are not.
     */
    private static int paraBeforeTw(java.util.List<PdfToWord.Table.CellPara> cps, int q,
                                    int rowLineTw) {
        int boxPrev = paraBoxTw(cps, q - 1, rowLineTw);
        int boxHere = paraBoxTw(cps, q, rowLineTw);
        float dy = cps.get(q).baseY - cps.get(q - 1).baseY;
        long want = Math.round(dy * TWIPS_PER_PT)
                - Math.round(0.2f * boxPrev) - Math.round(LINE_BASE * boxHere);
        return (int) Math.max(0L, want);
    }

    /** What a paragraph-carrying cell occupies, in twips: its first line's placement plus every line. */
    private static int cellParasTw(PdfToWord.Table t, int r, int c, float rowTopPagePt,
                                   int rowLineTw) {
        java.util.List<PdfToWord.Table.CellPara> cps = t.parasAt(r, c);
        if (cps.size() < 2) return 0;
        int box0 = paraBoxTw(cps, 0, rowLineTw);
        int total = box0;
        float first = cps.get(0).baseY;
        if (!Float.isNaN(first) && !Float.isNaN(rowTopPagePt) && cps.get(0).size > 0f) {
            float wantPt = first - rowTopPagePt;
            if (wantPt >= LINE_BASE * cps.get(0).size) {
                total += Math.max(0, Math.round(
                        (wantPt - LINE_BASE * box0 / (float) TWIPS_PER_PT) * TWIPS_PER_PT));
            }
        }
        for (int q = 1; q < cps.size(); q++) {
            total += paraBeforeTw(cps, q, rowLineTw);
            total += paraBoxTw(cps, q, rowLineTw);
        }
        return total;
    }

    /**
     * One paragraph of a cell, with its own spacing, indent and run properties.
     *
     * <p>This is the emission the string-based cell could not make: a cell was one {@code w:p}
     * with one {@code w:rPr}, so a column holding a 15 pt bold headline over 8.4 pt italic body
     * text could carry exactly one of them.
     */
    private static void cellParaXml(StringBuilder inner, PdfToWord.Table.CellPara cp,
                                    int beforeTw, int boxTw, int insetTw, float cellSz) {
        float sz = cp.size > 0f ? cp.size : cellSz;
        inner.append("<w:p><w:pPr><w:pStyle w:val=\"TableText\"/>")
                .append("<w:snapToGrid w:val=\"0\"/>")
                .append(spacing(beforeTw, boxTw, sz, autoCellBoxes(), false));
        if (insetTw > 0) inner.append("<w:ind w:left=\"").append(insetTw).append("\"/>");
        inner.append("</w:pPr>");
        if (!cp.text.isEmpty()) {
            inner.append("<w:r><w:rPr>");
            if (cp.face != null && !cp.face.isEmpty()) {
                String f = esc(faceName(cp.face));
                inner.append("<w:rFonts w:ascii=\"").append(f)
                        .append("\" w:hAnsi=\"").append(f)
                        .append("\" w:cs=\"").append(f).append("\"/>");
            }
            if (cp.bold) inner.append("<w:b/>");
            if (cp.italic) inner.append("<w:i/>");
            if (cp.colour >= 0) {
                inner.append(String.format("<w:color w:val=\"%06X\"/>", cp.colour & 0xFFFFFF));
            }
            if (!Float.isNaN(sz) && sz > 0f) {
                int half = Math.max(2, halfPointsDown(sz));
                inner.append("<w:sz w:val=\"").append(half)
                        .append("\"/><w:szCs w:val=\"").append(half).append("\"/>");
            }
            inner.append("</w:rPr>");
            String[] parts = cp.text.split("\n");
            for (int q = 0; q < parts.length; q++) {
                if (q > 0) {
                    if (!parts[q - 1].isEmpty() && !parts[q - 1].endsWith(" ")) {
                        inner.append("<w:t xml:space=\"preserve\"> </w:t>");
                    }
                    inner.append("<w:br/>");
                }
                inner.append("<w:t xml:space=\"preserve\">").append(esc(parts[q]))
                        .append("</w:t>");
            }
            inner.append("</w:r>");
        }
        inner.append("</w:p>");
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

    /** Was cell (r, c) drawn bold, or false when the pass that built the table did not say. */
    private static boolean boldOf(PdfToWord.Table t, int r, int c) {
        if (r >= t.bolds.size()) return false;
        List<Boolean> row = t.bolds.get(r);
        return c < row.size() && Boolean.TRUE.equals(row.get(c));
    }

    /** Was cell (r, c) drawn italic, or false when the pass did not say. */
    private static boolean italicOf(PdfToWord.Table t, int r, int c) {
        if (r >= t.italics.size()) return false;
        List<Boolean> row = t.italics.get(r);
        return c < row.size() && Boolean.TRUE.equals(row.get(c));
    }

    /** The text of cell (r, c), or "" when the row does not reach that far. */
    private static String cellAt(PdfToWord.Table t, int r, int c) {
        if (r >= t.rows.size()) return "";
        List<String> row = t.rows.get(r);
        if (c >= row.size()) return "";
        String s = row.get(c);
        return s == null ? "" : s;
    }

    /** The page y of this cell's first baseline, or NaN when the pass did not measure it. */
    private static float yOf(PdfToWord.Table t, int r, int c) {
        if (r >= t.cellY.size()) return Float.NaN;
        List<Float> ys = t.cellY.get(r);
        if (c >= ys.size()) return Float.NaN;
        Float y = ys.get(c);
        return y == null ? Float.NaN : y;
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
        // MT and PSMT are PostScript foundry suffixes and they sit AFTER the style, so they
        // have to come off the whole name first: Arial-BoldMT is arial+bold+mt, not a bold
        // family called "arial-bold". Without this the engine wrote "ArialMT" and
        // "TimesNewRomanPSMT" into w:rFonts whole - names no reader has, so every one of those
        // runs was substituted. The bench's own checker has always stripped these
        // (verify_google.py), which is why the two sides disagreed about what a face is called.
        for (String suf : new String[]{"PSMT", "PS", "MT"}) {
            if (f.length() > suf.length() && f.toUpperCase(Locale.ROOT).endsWith(suf)) {
                f = f.substring(0, f.length() - suf.length());
                break;
            }
        }
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
                // " Roman" was in this list and it turned "Times New Roman" - a FAMILY name,
                // the commonest face in any Word-produced PDF - into "Times New", which no
                // reader has. The hyphen form "-Roman" below is the PostScript style suffix and
                // stays; the space form is a family.
                " Bold", " Regular", " Normal",
                "-BoldItalic", "-BoldOblique", "-Bold", "-Italic", "-Oblique",
                "-Regular", "-Roman", "-Normal", ",Bold", ",Italic", ",BoldItalic"};
        for (String suf : suffixes) {
            if (f.length() > suf.length() && f.endsWith(suf)) {
                String stripped = f.substring(0, f.length() - suf.length());
                String mapped = BASE14.get(stripped.toLowerCase(Locale.ROOT));
                return mapped != null ? mapped : stripped;
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
        // Identity entries, so the strip above has somewhere to land. "TimesNewRomanPSMT" is
        // how Google and Word both name the face; after PSMT comes off it reads
        // "TimesNewRoman", which no reader has either - the family is "Times New Roman".
        BASE14.put("arial", "Arial");
        BASE14.put("timesnewroman", "Times New Roman");
        BASE14.put("couriernew", "Courier New");
        BASE14.put("liberationsans", "Arial");
        BASE14.put("liberation sans", "Arial");
        BASE14.put("liberationserif", "Times New Roman");
        BASE14.put("liberation serif", "Times New Roman");
        BASE14.put("liberationmono", "Courier New");
        BASE14.put("liberation mono", "Courier New");
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
