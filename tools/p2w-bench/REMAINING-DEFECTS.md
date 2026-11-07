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

**Tries: 0 of 3.**

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
