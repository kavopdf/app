# Remaining defects — to be worked at the very end

## v3 corpus — batch 1 (300-318), found this pass

These are new, from the document-type corpus. Recorded here so the final sweep works through
them along with the rest.

| Doc | Problem |
|---|---|
| **315_gazette_notification** | Three columns stack into one flow; the page reads down instead of across. Page count still 1/1. |
| **311_fir_police_form** | The address cell overruns its column in the PDF itself, so its tail lands in the next cell; row pitch compressed by ~31 pt median. |
| **314_tender_rfp_boq** | "8,39,69,600" renders as "8,39,69,60" — the last column is exactly as wide as the page's own text and the substituted face is wider. Needs a point or two of slack when a cell's drawn right edge sits on its text. |
| **300, 302, 306, 314** | Vertical drift 22-42 pt median — the same flow-determined spacing class as below. |

Fixed this pass and no longer open: the false table round prose on 316 (a rule's y was compared
in the wrong frame), and the interleaved cell text on 311 ("6M0o0b6i7le").


## v3 corpus — batch 3 (342-371), found this pass

| Doc | Problem |
|---|---|
| **350_question_paper** | 1 page in, 2 out: the MCQ block overflows. Pre-existing, unchanged by this pass. The .txt also fails TABLE CELLS and NO DUPLICATION. |
| **353_admit_card** | The label/value block is emitted as a four-column table with the labels as header cells and "Aadhaar ending 4471" in a row of its own; the page sets each label above its value in a two-column band. |
| **361_product_catalogue_grid** | Each card's text is drawn at the top of the card over its photograph instead of below it, and the second row of cards loses its text entirely. 108.4 pt median drift. |
| **364_event_ticket** | "WS24-4471-0082" is drawn twice on the page and appears once in the .docx. |
| **352_certificate_ornate_border, 371_experience_certificate** | .txt position 30.0 % and 36.4 %: rotated round seals whose text the page draws one character per baseline. A .txt has no rotation; body text on both is 100 %. |
| **343_air_waybill** | 28.8 pt median vertical drift, the flow-determined spacing class. |

Closed this pass: every document in all three corpora was re-converted and compared on page count,
words, images and tables — no document got worse. The size a glyph is set at is now read exactly
(it was rounded to a whole point), a table cell's exact line height is the row's own pitch instead
of a constant 10 pt, and a size that is not a whole half-point rounds down so a column that was
exactly wide enough does not start wrapping.

Everything here was found by rendering the .docx through LibreOffice and comparing it against the
source PDF page by page, in batches of 20 over the 80-document corpus. Each entry names the batch,
the document, what is wrong, and what was already tried.

Work through this only after the other corpora are processed.

---

## v3 corpus — batch 4 (372-394), found this pass

| Doc | Problem | Tries |
|---|---|---|
| **393_spectrum_peak_table, 394_map_with_legend, 382_architecture_diagram** | Text drawn under a drawing lands too high: the table under 393's chart by 141.6 pt, 394's legend by 227.1 pt, 382's first label by 77 pt. A chart, a map's roads and a diagram's boxes are anchored shapes — they draw where the page drew them and take **no room in the flow** — so the text beneath them closes the gap they left. The gap ceiling is now 120 pt instead of 72 pt, which fixed 393 and 394's row order; 382's first gap is 212 pt and is still lost. | 1 of 3 — see the anchor attempt below |
| **The flow-anchor attempt (all three, above)** | Placing every flowed line at its own measured y instead of one pitch below the line before it. Measured over 208 documents: **0 documents worse on G2**, and 380 goes to 100 % of lines in tolerance, 394 to 93.3 %, 392 to 95.2 %, 382 to 72.4 %. But 390_wide_data_appendix fell from 57.8 % to 0.5 % and 373 and 390 both went from one page to two, because a table's real height exceeds the model's, so a target y adds that error a second time. A hybrid (anchor only until a table has been through the page) gave 11.6 % and left 390 at 0.5 %. **Blocked on the table height below** — not on the idea. | 2 of 3 used |
| **Table height (the blocker above)** | Rows are emitted `w:trHeight hRule="atLeast"`, so a cell whose text wraps grows the row and the table is taller than `t.bottom - t.top`. On 373 two tables are short by ~186 pt in the flow's accounting; on 375 (459 lines, all in one table) only 0.4 % of lines land within tolerance, on 390 57.8 %. Until the model's table height matches the render's, no absolute-y placement can be trusted after a table. | 0 of 3 |
| **373_leave_application_form** | The page draws "Employee signature \| Manager signature \| HR use" as ONE row; the .docx has it as two paragraphs 3 pt apart, because the model splits the line into two paragraphs at the wide x gap and Word cannot put two paragraphs on one line. Merging them in the writer would be the fix, but it lowers the leaf-paragraph count that G2 reads as "lines", which the gate defines as a regression. Also fails G3 reflow (fails identically on the pre-change build — pre-existing, not caused here). | 1 of 3 |
| **375_attendance_register, 390_wide_data_appendix** | Row pitch: a 13-19 row table is taller in the render than on the page, so every row after the first drifts. Same root as the table height entry above. | 0 of 3 |

Fixed this pass and no longer open: 393 and 394's reading order (the 120 pt gap ceiling), and the
three `visual.py` measurement bugs that had been reporting defects that were not there — line-index
pairing in question 1, box-top instead of baseline for grouping a row, and U+0000 from a soft hyphen
kept on one side of the comparison only.

## A. Multi-column pages still overflow to a second sheet — 3 documents

Fixed this pass: 63, 67, 78, 80 and 55 now render 1 page against 1 (they were 2). Sections now carry
`w:cols w:num` from the engine's own column bands, with a section break when the column count
changes. These three did not follow:

| Doc | Batch | Problem |
|---|---|---|
| **64_newspaper_uneven_columns_ad_boxes** | 4 | Uneven columns plus three ad boxes; still 2 pages. The ad boxes are drawn but stack below the body. |
| **65_two_col_full_width_figure_caption** | 4 | A full-width figure spanning both columns; the chart renders but the spanning band is not modelled, so the flow breaks into two pages. |
| **77_arabic_rtl_document** | 4 | The description column collapses to a sliver: `colX` is [57,152,246,340,434,528] while `cellR` for the description column reports 428.2, so the writer wraps the cell into a 17 pt column. RTL column widths are not honoured. |

## B. Table geometry — 3 documents

| Doc | Batch | Problem |
|---|---|---|
| **75_merged_header_cell_three_columns** | 4 | The first data row welds into the header ("Services1,842"). The page's sub-header rule at y=143 spans only part of the width, so no band boundary is found and header + value land in one cell. |
| **80_gstin_pan_cin_ifsc_table** | 4 | The four-column dealer grid collapses to two panels. Page count is now correct; the panel split is not. |
| **28_value_overflows_cell** | 2 | A value wider than its column is handled, but not with the page's own overflow behaviour. |

## C. Vertical position — every document, small offsets

Horizontal position is 0.1 pt everywhere, measured by rendering both sides and matching lines by
text. Vertical is not: 93 % of lines land within 10 pt on 21 and 79, 59 % on 01, and lower on the
table-heavy documents.

Causes still open:
- **Table TOP y** is flow-determined, not the PDF's y. Rows are the right height but the table can
  start a little high or low, moving everything below it.
- **Table row pitch** is slightly compact against the page on several invoices.
- **Page-anchored shapes drift** against the more compact text flow — 48's green border box starts
  below "Father's/husband's name" and its bottom edge cuts through "K. Ramesh, Clerk"; 79's rules
  and pink header band no longer line up with the rows.
- **Stamps sit a few points off** their PDF position. A rotated box cannot carry a rotation that
  LibreOffice honours (`a:xfrm rot` is ignored, `wps:bodyPr vert` lays Latin out one character per
  row), so the box is axis-aligned at the line's origin.

## D. Individual documents

| Doc | Batch | Problem |
|---|---|---|
| **30_mixed_font_sizes_one_baseline** | 2 | Renders 2 pages against 1. Its flow is longer than the sheet. |
| **26_footnote_marker_bottom_note** | 2 | The footnote marker's position relative to its note is close but not exact. |
| **52_one_cm_margin_wide_body** | 3 | The body does not justify across the full 28.3 pt margin the page uses. |
| **58_header_rule_footer_rule** | 3 | The rules render but do not sit exactly on the page's y. |
| **59_landscape_mixed_portrait** | 3 | The section break survives and the page is landscape, but the content is slightly compact. |
| **03_stamp_vertical_90deg** | 1 | LibreOffice truncates the 90-degree rotated stamp boxes in the render. |

---

## What is NOT on this list, and should not come back

Verified across all 80 documents:
- no black page — every .docx declares `<w:background w:color="FFFFFF"/>`
- no lost text — the gate reports 0 missing across the corpus for the batches it covers
- no missing image — every PDF page that draws an image has it in `word/media/`
- no scrambled layout — body text flows as real paragraphs, tables are real `w:tbl`
- no floating text boxes except for genuinely rotated lines
- no heading autospacing stacking on explicit spacing
- no `w:trHeight` missing, so tables no longer collapse to text height

---

## v3 corpus — batch 2 (320-341), found this pass

Worked with the same method as batch 1: convert, render both sides at 130 dpi, put PDF page and
DOCX page side by side, and measure. Page counts are 15/15 correct and .txt position is 78.8 % or
better everywhere, so what is left is content and drawing fidelity, not layout collapse.

| Doc | Problem | Why it is not fixed yet |
|---|---|---|
| **323_credit_card_statement** | The right-hand **SPEND BY CATEGORY** panel loses its whole label column — "Travel", "Shopping", "Fuel", "Groceries", "Health" are in the PDF and in neither the .docx nor the .txt. Only "Other" survives, and the six amounts come through as loose paragraphs at x≈474 rather than as a table. Word recall 96.9 %, the only .txt check that fails in the batch. | The two summary panels are side by side and overlap vertically (REWARDS SUMMARY x 28-228 y 301-354, SPEND BY CATEGORY x 250-490 y 300-372). The rewards panel is found as a table; the labels at x=250 are 22 pt beyond its right edge, so `Line.inside()` — which tests the line's CENTRE against `t.right + 2` — does not claim them, yet they reach no block at all. The values at x=474 do survive. Needs a trace through the candidate-table passes on this one page. |
| **323_credit_card_statement** | The header block is broken: "CREDIT LIMIT / Rs. 5,00,000 / AVAILABLE / Rs. 4,12,180" is turned into a table with two empty rows and pushed 28-32 pt down, and "Rs. 42,318.40" wraps onto a second line. | Same page, different pass: four short label/value pairs on two baselines read as a table. |
| **322_mutual_fund_factsheet** | "EXPENSE RATIO", "FUND MANAGER", "A. Bose (since 2019)", "PORTFOLIO HOLDINGS (TOP 10)" and "SECTOR ALLOCATION" are swallowed as table rows with empty cells; the scheme-performance table absorbs the holdings table and its rows misalign. | Headings above and beside a table are being claimed by the table's band. This is the batch's most repeated defect and deserves its own pass. |
| **322_mutual_fund_factsheet** | The **riskometer** — the circular gauge with its needle — is absent. Only the scattered labels "Low", "Moderately low", "Moderate", "High", "very high risk" remain, at the wrong y. | **CLOSED 6 Nov** — ring and needle both draw; the needle is a freeform, not its box. The panel's labels are still absorbed by the table pass (separate entry above). |
| **330_cad_drawing_sheet** | The hatched floor area renders as a **solid black rectangle**, and the circled "(A)" revision marker becomes a black blob. | **CLOSED 6 Nov** — the hatch is drawn as its own strokes and the north arrow as its own triangle, via `a:custGeom`. |
| **331_pid_diagram** | The legend's four symbol icons and the circled "P" markers on the drawing are missing; only the text labels survive. | **CLOSED 6 Nov** — rings, pump triangles and gate-valve bowties all draw as freeforms. |
| **335_msds_safety_data_sheet** | The three GHS hazard **pictograms** (red diamonds) are reduced to faint red fragments. | **CLOSED 6 Nov** — four red diamonds, drawn as the rotated squares they are, at the page's own colour C00000 and 1.6 pt stroke. |
| **324_loan_amortisation_schedule** | Column widths are an even split: "Month" is about 78 pt where the page drew it 31 pt, and every amount column is correspondingly narrow. Rows, row pitch and page count are otherwise exact. | The row-based table pass found these tables but left `colX` null, so the writer fell back to even columns. The values are right; only the column edges are missing. |
| **320_balance_sheet_statutory** | "Note 12 - Revenue from operations", the notes table's header row, comes out as a paragraph above the table instead of its first row; the amount column is shifted. | Header-row band boundary, same family as 75_merged_header_cell. |

### The one class worth real work: vector graphics

Four of the eight entries above are one thing. The engine carries raster images correctly — every
PDF page that draws an image has it in `word/media/`, and 340's barcode, 323's barcode and 326's QR
codes all render. What it does not carry is a **path**: a shape drawn with fills and strokes rather
than a bitmap. Three distinct failures, all visible in this batch:

1. a filled path with a pattern (330's hatch) is emitted as solid black
2. a stroke-only path (331's legend icons, 322's riskometer circle and needle) is dropped entirely
3. a path with a non-black fill and a thin outline (335's red diamonds) survives only partially

That is a rendering change in `PdfEngine`, not `DocxWriter`, and it is worth more than any single
document on this list. It should be taken as its own task, with a before/after on 322, 330, 331 and
335 plus a whole-corpus gate, because a shape pass that goes wrong is how a page turns black.

#### Sub-class 2 (stroke-only circles) and the filled-circle half of 1 — FIXED 6 Nov

A page draws a circle or an ellipse as four Bezier curves that close on themselves. Its bounding
box is a square, so the writer put a solid square where a ring belongs, and a stroke-only circle —
being neither a rectangle nor a single line — was dropped before it ever reached the writer.

`RuleCollector.pathIsEllipse()` now recognises that path (one move, four curves, no lines, no
rects, ends on its start point, both extents over 2 pt) and `DocxWriter.Shape.kind` selects
`prst="ellipse"` instead of `prst="rect"`. The extent needs no correction: a quarter arc's control
points sit exactly on the ellipse's extremes, so the box is already right and only the outline
drawn inside it changes.

Measured over all 208 documents, old engine against new, on page count, words present, images and
tables: **0 documents worse on any of the four, 17 documents improved.**

| Doc | Before | After |
|---|---|---|
| **351_omr_answer_sheet** | 320 bubble outlines dropped, 29 filled bubbles were black squares | **349 ellipses drawn**, bubbles read as bubbles |
| **331_pid_diagram** | legend symbols, instrument circles and pump circles absent | **7 ellipses**, the legend and both instrument loops read |
| **405_sheet_music_lyrics** | 54 note heads were 6x4 pt black rectangles | 54 ellipses |
| **360_restaurant_menu** | 20 dietary markers were squares | 20 ellipses |
| **65_two_col_full_width_figure_caption** | 20 chart markers were squares | 20 ellipses |
| **330_cad_drawing_sheet** | the compass was a free-standing black slab | the ring is drawn; the arrow inside is still its box |
| **322_mutual_fund_factsheet** | riskometer ring absent | ring drawn |
| 05, 60, 305, 312, 318, 332, 352, 371, 394, 400 | rings absent or boxed | rings drawn |

Page count was re-rendered through LibreOffice for all 17 and is unchanged on every one.
`TestPdfToWord` 29/29, `TestRealDocs` 96.8 / 97.0 / 81.7 — identical to the decimal.

#### Still open in this class — nothing

**Closed 6 Nov, all of it.** `a:custGeom` now carries every path that is neither an axis-aligned
rectangle nor an ellipse: filled polygons (330's north arrow, 331's pump triangles), stroked
polygons (331's gate-valve bowties, 400's bubble tails), angled one-line strokes (330's hatch),
curves (394's river and highways) and rotated squares (335's four GHS diamonds, drawn under a
45-degree matrix and kept because a freeform's points are already through the matrix).
Measured across all 208 documents: 0 worse on page count, words, images or tables; 23 changed, all
gaining drawn shapes; `.txt` byte-identical.


---

## OPEN - found by the position and visual gates, 7 Nov

These two were invisible to every count-based gate. `gate.py` reported "no document
got worse" on all 208 documents while both were present. They are the reason G5 and
G6 exist.

### D-01  Vertical drift: every line sits higher than the PDF drew it, and the error grows down the page

**Severity: affects most documents. This is the biggest single defect in the corpus.**

Measured on `303_discharge_summary`, PDF page 1 against the rendered docx:

| Line | PDF y | DOCX y | Delta |
|------|-------|--------|-------|
| DISCHARGE SUMMARY | 12.12 | 8.60 | -3.52 |
| Shriram Multispeciality Hospital | 27.30 | 22.90 | -4.40 |
| PATIENT | 63.92 | 57.60 | -6.32 |
| ANANYA RAO, 34/F | 73.78 | 68.10 | -5.68 |

**Root cause, already located.** `DocxWriter.java:70` sets `LINE_FACTOR = 1.15` and
line 669 writes `w:line = size * LINE_FACTOR` with `lineRule="exact"`. The page has
zero margins (`pgMar top="0"`), so the first line starts at whatever the line box
gives it.

The PDF's own pitch on this document is 15.18 pt for 13 pt text - a ratio of **1.168**,
not 1.15. The docx therefore sets each line 0.23 pt too short, and because
`lineRule="exact"` stacks those short boxes, the error accumulates down the page:
3.5 pt at the first line, 6.3 pt by the fourth paragraph.

**The fix to try.** The model already carries the truth: `Para.lineY` holds each
line's real y, and `Para.lineSize` its size. The pitch is therefore *measurable* per
line pair and does not need a constant at all. Set `w:line` from the measured gap
between this line and the previous one, falling back to `size * LINE_FACTOR` only when
there is no previous line on the page.

**Why this is not a one-line change.** `LINE_FACTOR` touches every document, so it
must go through G2 across all 208 before anything is kept, and G5 must be re-measured
afterwards to prove the drift actually fell. A previous attempt to move the constant
"did nothing" - that is expected, because a constant cannot match a document whose
pitch is 1.168 while another's is 1.20. It has to be measured, not tuned.

**Tries: 1 of 3 - see the measurement below.**

### D-01 as measured on 7 Nov: the line box is the page's own pitch

**What the renderer actually does.** A one-paragraph probe with zero margins was rendered
through LibreOffice at nine box heights (9.2 to 37 pt) and four faces (Liberation Sans and
Serif, DejaVu Sans and Serif), including one box shorter than its own em. In every case
`boxHeight - baselineY` came to 0.2 of the box, within the 0.05 pt the render quantises to.
The baseline sits at 0.8 of an exact-height box, whatever the font and whatever the size.
So the advance from one baseline to the next is

    (1 - 0.8) * previous box + 0.8 * this box + spacing-before

and a baseline is placed by choosing the box, not by tuning a constant.

**The change** (`DocxWriter.flowFromBox`, `flowRow`, and the `LINE_BASE` constant). The box
is solved from that equation using the pitch the model already carries - `b.y` minus the
previous baseline - floored at the font size, because a box shorter than the em clips the
glyphs, and capped at the font's own line box, because a box taller than that spends slack
the next line has to pay for (a 37 pt gap above a form row became a 37 pt box, and the next
row then landed 5.2 pt low). Whatever the box cannot hold goes to spacing-before, still
capped at 120 pt. The first line of a page is lifted by 0.8 of its box instead of by a whole
box, and after a table the previous box counts as zero, because a table's bottom edge is not
a baseline.

**Measured across all 208 documents.**

| Measure | Before | After |
|---|---|---|
| lines within tolerance (G5) | 11.7 % | **26.3 %** |
| documents improved / worse on G5 | - | **157 / 15** |
| G2 words, blocks, page fill, overflow | - | **no document got worse** |
| documents spilling onto an extra page | 28 | 30 |
| TestPdfToWord / TestRealDocs | 29/29, 96.8 / 97.0 / 81.7 | identical |

**The fifteen that got worse are one class, not fifteen.** Thirteen of them contain a table
and two are two-column pages: 390_wide_data_appendix, 23_timetable_grid_txtpos,
72_bank_statement_no_rules_right_amounts, 330_cad_drawing_sheet,
38_faux_bold_italic_synthesised, 40_devanagari_shaping_font,
academic-paper-ieee-2col-abstract, balance-sheet-and-profit-loss, 13_stamp_non_english,
annual-review-2col-uneven-columns, 325_demat_holdings_statement, 362_price_list_dense,
333_datasheet_spec_tables, journal-2col-with-footnotes, magazine-2col-pullquote-spanning.
The text is now exactly on the page's own baselines; what is left is the table height below,
which under-measures a table whose rows grow, so everything after a table starts from the
wrong y - and the old, slightly-too-tall flow was accidentally compensating for it.

**Therefore the position baseline is not re-recorded on this run.** `base208-position.json`
still holds the pre-change numbers, so those fifteen show up as debt on every G5 run rather
than being baked into the ratchet. Re-record it when the table height is right.

**Also tried and reverted.** Charging the pre-table spacer as
`(t.top - baseline) - 0.2 * previous box` - the same rule the flow now uses - put 390's
table 10.6 pt low instead of 3.7 pt, because a table's first row does not begin where the
spacer paragraph ends. Reverted; the table's own top y stays open below.

### D-02  Row grouping: cells from different rows merged onto one line

**Severity: affects tables where row baselines differ by a few points.**

Measured on `303_discharge_summary`, PDF page 1 against the rendered docx:

    PDF   PATIENT    y=63.92  |  WARD / BED  y=64.68     <- two cells, one visual row
          ANANYA RAO y=73.78  |  Medical ICU y=73.54     <- two cells, next row

    DOCX  PATIENT    y=57.60  |  WARD / BED  y=57.60  |  CONSULTANT y=60.80
          Medical ICU y=68.10                            <- ANANYA RAO is gone from here

The PDF keeps the cells in two rows because their baselines differ by 0.76 pt. The
docx put three cells on one row - the third cell's baseline is 2.9 pt away from the
other two and was treated as the same row - and the value cell that should sit beside
`ANANYA RAO` ended up somewhere else.

**The fix to try.** The row tolerance in `buildTables` decides this, and it is
currently wide enough to swallow a 2.9 pt difference. It should come from the table's
own measured row pitch (the median gap between row baselines in that table), not from
a constant, so a table set tight and a table set loose each get the tolerance they
actually use.

**Tries: 0 of 3.**

### How to verify either fix

    python3 tools/p2w-bench/gate.py --corpus DIR --out DIR --baseline tools/p2w-bench/base208.json --check
    python3 tools/p2w-bench/position.py --corpus DIR --out DIR --verbose
    python3 tools/p2w-bench/visual.py --corpus DIR --out DIR

G2 must pass across all 208 first. Then G5's "lines within tolerance" must rise and
G6's reading-order share must rise. A fix that passes G2 but does not move G5 or G6
has not fixed either of these.


### D-03  Reading order: every label first, then every value

**Severity: affects the documents the visual gate measured, 3 of 3.**

Measured on `301_lab_report_panel`, PDF page 1 against the rendered docx:

    PDF   metropolis pathology lab
          nabl accredited | lab id mh-4471 | report no. mpl/2024/0318/
          patient
          ananya rao
          age / sex
          34 / female
          referred by
          dr. meera krishnan

    DOCX  metropolis pathology lab
          nabl accredited | lab id mh-4471 | report no. mpl/2024/0318/
          patient
          age / sex
          referred by
          collected
          34 / female
          dr. meera krishnan

The PDF reads label, value, label, value. The docx reads every label, then every value.
Every word is present and at the right coordinates; only the sequence is wrong, which is
why no count-based gate can see it and why `visual.py` question 1 exists.

**The fix to try.** The paragraph order in the body follows the block order in
`Page.blocks`. If the page groups a form's labels before its values, that order is
inherited. The order should come from the page's own reading order - the same
top-to-bottom, left-to-right sequence a reader follows - sorted by the row's baseline
and then by x within a row, which is what `visual.py`'s `_rows()` already computes.

**Tries: 0 of 3.**



### Correction, 7 Nov — the note below was wrong and is withdrawn

I wrote the note below after reading the PDF's lines sorted by raw y, and concluded that
88.5 % on 303_discharge_summary was a false alarm because the PDF's own order put the
patient's name last. That was wrong: `_rows()` does not sort by raw y. It groups lines
into bands and sorts left to right inside a band, so the PDF's rows are already:

    row 1  'PATIENT'  'WARD / BED'  'CONSULTANT'
    row 2  'ANANYA RAO, 34/F'  'Medical ICU-2 / 07'  'Dr. Meera Krishnan'

which is the correct reading order, with the patient's name where it belongs. So the
88.5 % is a real finding: the docx's row order genuinely differs from a reading order the
PDF already has. It is not ambiguous and it is not a false alarm.

The lesson is the one this whole check is about: a finding is verified against the code
that produced it, not against a hand re-derivation that skips that code.

The note below is kept only so the mistake is on the record.

### A note added 7 Nov, after checking the findings against the PDF

The reading-order question compares the docx's row sequence with the PDF's. On a form
with side-by-side fields the PDF's own y order is not the reading order, and the
comparison then penalises a docx that reads the page better than the PDF draws it.

303_discharge_summary, page 1, sorted by y as the PDF holds it:

    y=63.9  x= 28   'PATIENT'
    y=64.7  x=230   'WARD / BED'
    y=64.7  x=380   'CONSULTANT'
    y=73.5  x=230   'Medical ICU-2 / 07'
    y=73.5  x=380   'Dr. Meera Krishnan'
    y=73.8  x= 28   'ANANYA RAO, 34/F'      <- the patient's name, last

`ANANYA RAO` belongs beside `PATIENT`, and a reader would put it there. A docx that
does is scored as out of sequence against a PDF whose raw order is the wrong one. The
88.5 % on that document is therefore not evidence of a defect - it may be evidence of
a better document.

Do not "fix" this by making the docx copy the PDF's y order; that would be worse for a
reader. The question needs to compare against a reading order derived from the page -
fields grouped by band and read left to right within a band - rather than against the
order the PDF happens to store its lines in.

Until then, a reading-order failure on a form or a table page is a question, not a
verdict: open the image and look before recording it as a defect.

### D-04  Body text inside text boxes

**Severity: 2 of the 8 documents the structure gate measured.**

    FAIL 305_vaccination_certificate   48 text boxes
    FAIL 312_affidavit_stamp_paper     27 text boxes

`reflow.py` reports the count. Body text in a text box cannot be edited or reflowed,
and a document built that way measures perfectly while not being a Word document.

The other six documents in that run report zero text boxes and are not affected, so
this is not a whole-corpus problem - it is these documents and any like them.

**The fix to try.** Find what makes these two take the text-box path and give them the
flowing-paragraph path the other six already use. Do not ban text boxes: a watermark or
a sidebar legitimately uses one, and the gate says which document and how many so the
two cases can be told apart.

**Tries: 0 of 3.**


### D-05  The blocks count compares two populations that are not the same thing

**Severity: a measurement defect, not a document defect. It makes one of the seven
G2 numbers untrustworthy.**

`gate.py` scores `blocks` as `big_shapes(docx) - pdf_fills(pdf)`.

    big_shapes   counts solid fills inside wps:wsp shapes in the docx XML
    pdf_fills    counts filled areas from PyMuPDF's get_drawings() in the PDF

Those are not the same population. The writer emits a docx shape for every fill the PDF
draws, and also for things the PDF does not express as a drawing - a table cell
background, a paragraph shading, a shape whose fill comes from a style. So the
difference is positive on almost every document and means nothing.

The 3000 pt2 floor in both functions was hiding this: it dropped the small fills on both
sides, which by luck left the two counts close enough that the difference stayed at 0 on
the corpus. On 7 Nov I removed the floor while replacing the hard-coded 580x820 A4 with
the page's own size, and 179 documents went from blocks 0 to blocks N. The floor was not
protecting anything real - it was masking a metric that does not measure what it claims.

**Do not fix this by tuning the floor.** The fix is to stop counting and start matching:
for each filled region the docx draws, ask whether the PDF drew a filled region at the
same place with the same colour, which is a positional comparison like G5's, and report
how many docx fills have no partner in the PDF. That is a real number, and 0 is the only
correct value.

Until then the floor stays where it was, because a metric that is understood to be weak
is better than a metric that fires on 179 documents for a reason nobody can act on.

**Tries: 0 of 3.**


### D-06  Twenty-eight documents spill onto more pages than the PDF has

**Severity: a page the PDF does not have is the first thing a reader notices.**

Measured with `position.py` on 7 Nov, comparing the docx render's page count with the
PDF's:

    64_newspaper_uneven_columns_ad_boxes    docx 5 pages, PDF 1
    350_question_paper                      docx 2 pages, PDF 1
    63_three_column_brochure                docx 2 pages, PDF 1
    20_numbered_list_separate_column_txtpos docx 2 pages, PDF 1
    332_bom_on_drawing                      docx 2 pages, PDF 1
    402_calendar_month_grid                 docx 2 pages, PDF 1
    55_sidebar_box_beside_body              docx 2 pages, PDF 1
    65_two_col_full_width_figure_caption    docx 2 pages, PDF 1

28 of the 208 documents fail this way. `gate.py` counts page breaks it finds in the
XML and reports 537 against the PDFs' 540, so three documents lose a page while these
28 gain one - the two errors were hiding each other in the total.

The cause is the same one behind D-01: the writer gives every paragraph an exact line
height of size x 1.15 and a spacing-before taken from the measured gap. Both are close
but neither is the page's real pitch, so the content is slightly taller than the page
and the last few lines fall onto a second sheet. On 64_newspaper it is four extra
sheets.

**The fix to try.** The same one as D-01: take the line height from the model's own
lineY gaps instead of a constant, and let the page's real bottom margin decide where
the page ends. Do not shrink the content to fit - the page count is a measurement, and
the only correct number is the PDF's.

**Tries: 1 of 3.** The pitch fix above was the fix this entry asked for, and it did not
move the count: 28 documents spilled before it and 30 after, two of them new
(330_cad_drawing_sheet and journal-2col-with-footnotes, both an EMPTY second page - the
overflow is a few points, not a page's worth). Because the text now sits on the page's own
baselines, the remaining overflow is not the text's height any more: it is the table height
(rows are `atLeast`, so a wrapping cell grows the row and the model's `t.bottom` is short),
the trailing 4 pt placeholder paragraph after a table, and where a multi-column section
breaks its columns. Measured on the two new spills: 330's page 1 ends at 592.0 pt on a 595 pt
sheet, journal-2col's at 840.1 on 842, and neither has any text on page 2.


### D-07  Two fields on one baseline are joined into one sentence

**Severity: a marks column or a right-aligned label becomes part of the sentence beside it.**

Found on 350_question_paper, which came out as `[08] Write SQL queries for the following`,
the marks column in front of the question it belongs to. The PDF has them on one baseline:

    'Write SQL queries for the following: ...'   x= 50.0  y=147.5  x1=493.5
    '[08]'                                       x=551.9  y=148.9

and on form16-part-b:

    'Certificate under section 203 ...'          x=144.3  y= 44.0  x1=451.0
    'PART B'                                     x=519.3  y= 43.5  x1=552.8

**Two separate causes, both confirmed by running the engine.**

1. THE GAP TEST ONLY SEES A POSITIVE GAP. A baseline cluster does not hold its glyphs in
   x order, so `[08]` arrives before `Write`, the gap between them reads -520, and
   `gapPts > outlier` is false. The comment above that line has said "a gap counts however
   it is signed" since file 46 lost a number off a chart for the same reason; the code
   never did it. Changing it to `Math.abs(gapPts) > outlier` is correct and was measured.

2. THE FIELDS ARE THEN PUT BACK IN CLUSTER ORDER, NOT READING ORDER. They are only
   reversed for an RTL baseline, so an LTR baseline keeps whatever order the cluster held
   them in. Sorting the segments by x - ascending LTR, descending RTL - is correct.

**Measured with both changes on the 208-document corpus: 4 documents improved, 1 got worse.**

    350_question_paper                    lines  85 -> 116   (+31)
    417_rotate180_and_mirrored            lines   9 ->  11
    46_chart_coloured_labels_body_text    lines  29 ->  30
    69_two_col_legal_numbered_clauses     lines  51 ->  52
    form16-part-b                         lines 113 -> 112   (-1)  REGRESSION

The regression is real damage, not a count moving. On form16-part-b the old output kept
`PART B` as its own paragraph, in its own place at the right of the page. With both
changes it is joined into the sentence above it - `Certificate under section 203 ... PART B`
- which is worse than either, because the label has lost its position and reads as part of
the sentence. The cause is `sameRow()` in the paragraph grouping: two lines on one baseline
are put in one group and `buildPara` joins their text with a space.

So the changes were reverted, and this entry records them.

**The fix to try.** All three parts together, because any two of them alone leave the
regression or lose the improvement:

    a. `Math.abs(gapPts) > outlier` in the baseline cut.
    b. sort the cut segments by x, ascending for LTR and descending for RTL.
    c. in the paragraph grouping, do not let `sameRow()` hold two lines together when
       either of them is `hardEnd` and no gutter crosses the space between them. A table
       cell has a rule separating it; a page header does not, and that is the difference
       between a row and two fields.

Part (c) is the one that has not been written yet. A first attempt must check the tables
first - 8 of 25 tables were missing on stamped documents once when the grid and the
paragraph grouping disagreed, and a change here can do the same.

**Tries: 1 of 3** - the signed-gap and sort changes were tried and reverted.


---

## OPEN - v3 corpus, batch 1 (300-315), re-processed 7 Nov under the eye + verify pipeline

Fifteen documents converted from the current engine, rendered through LibreOffice, opened one
page at a time, measured, and every finding checked against the PDF by `verify.py` before it
was written down. Twelve findings verified, six refuted - and four of the six refuted were the
eye's or the tool's own mistake, which is the point of the step.

| Doc | Verified finding | Tries |
|---|---|---|
| **301_lab_report_panel** | `moved:ANANYA RAO` 26.2 pt, `moved:COLLECTED` 8.0 pt; reading order 78.7 %, 28 rows in the PDF against 33 in the render. The four-column band (PATIENT / AGE-SEX / REFERRED BY / COLLECTED) is emitted one cell per paragraph, so the row is four baselines that drift left to right instead of one. | 0 of 3 |
| **302_radiology_report** | `moved:PATIENT NAME` -8.6 pt. Same band, same cause: the first label of a label/value band leaves its row. The rest of the page is exact and the reading order is 100 %. | 0 of 3 |
| **311_fir_police_form** | `moved:Mobile` - 2 in the PDF, 1 in the render, worst offset 91.8 pt. The address cell overruns into the Mobile cell on the page itself, and the render welds the two texts into one run, so the label leaves its column. Reading order 90.2 %. | 0 of 3 |
| **312_affidavit_stamp_paper** | `moved:BEFORE ME` and `moved:Note: affidavits`, both exactly -72.2 pt. The notary box is drawn at its own y but empty, the footnote sits inside it, and the BEFORE ME block is pushed above the box. Reading order 58.0 %. The whole tail is 72.2 pt high, which is the spacing-before cap on the ~183 pt gap above the notary block (GAP_CAP_TW 120 pt). | 0 of 3 |
| **315_gazette_notification** | `moved:publication in the Official Gazette` +184.8 pt, `moved:The Gazette of India` +55.9 pt; reading order 29.1 %, 21 rows against 34. The three columns stack into one flow and the masthead drops below PUBLISHED BY AUTHORITY. Column bands are not detected on this page, so no `w:cols` is written. | 0 of 3 |

### Refuted this pass - do not "fix" these

| Claim | What the PDF actually says |
|---|---|
| `missing:8,39,69,600` and `missing:9,90,84,128` on 314 | Both totals are present and identical: x 467.7-513.0 on both sides. The eye misread a 130 dpi image; the last digit is there. |
| `wraps:WARNING SIGNS` on 303 | The PDF's own line runs 28.0 to 596.7 on a 595.28 pt page - it overruns its margin by 1.4 pt and the tail "more than 4 times a day" is drawn off the page and lost. The render wraps it inside the margin and keeps every word. The render is the better page. |
| `moved:AGE / SEX` and `moved:PATIENT` on 301 | Both within 0.5 pt. The band defect is real, but it is not these two labels; the verified claims are the two above. |
| `shapes` on 316 | 1 shape in the PDF, 1 in the render. |

### Two tool alarms to repair, not documents

- **303_discharge_summary, reading order 88.5 %.** The render has 27 rows to the PDF's 25
  because it wrapped the line the PDF clipped. Question 1 counts rows, so a render that keeps
  text the PDF lost is scored as an order error. The comparison should be on the text, not the
  row count.
- **305_vaccination_certificate, reading order 47.1 % and "205 shapes in the PDF, 12 in the
  render".** The seal is rotated text drawn one character per baseline, so the PDF's own rows
  are single characters; the 205 shapes are the QR module squares, which the render carries as
  one image. Both are the known rotated-stamp and image-as-image limits, not defects.
