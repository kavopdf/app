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
| **322_mutual_fund_factsheet** | The **riskometer** — the circular gauge with its needle — is absent. Only the scattered labels "Low", "Moderately low", "Moderate", "High", "very high risk" remain, at the wrong y. | Vector class, below. |
| **330_cad_drawing_sheet** | The hatched floor area renders as a **solid black rectangle**, and the circled "(A)" revision marker becomes a black blob. | Vector class: a path fill is emitted at full black instead of its own colour and pattern. |
| **331_pid_diagram** | The legend's four symbol icons and the circled "P" markers on the drawing are missing; only the text labels survive. | Vector class: stroke-only paths with no fill are dropped. |
| **335_msds_safety_data_sheet** | The three GHS hazard **pictograms** (red diamonds) are reduced to faint red fragments. | Vector class. |
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
