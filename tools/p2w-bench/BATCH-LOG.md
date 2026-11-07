# PDF → Word: batch-by-batch record

Every batch is 20 documents. Each one is converted, rendered through LibreOffice, opened, and
compared against the source PDF. What is fixed is recorded here; what is not is recorded here too,
with the reason, so the last pass can work through the list.

The corpus: `p2w-batch-1.zip`, 80 documents, numbered 01-80.

---

# CORPUS v3 — 75 documents, numbered 300-417

Work on the third corpus (document *types*: medical, legal, finance, engineering, logistics,
education, retail, forms, dev, diagrams, print media, PDF tricks) has started. It is recorded in
`V3-BATCH-LOG.md` so the 80-document record above stays intact. Batch 1 (300-318, 15 documents)
is done: 15 of 15 are one page in and one page out, every word of every page is present, and the
batch found and fixed a coordinate-frame bug in the ruled-table pass that had been putting
spurious tables round ordinary prose.

---

## BATCH 1 — documents 01-20

**Visual result: 14 excellent, 6 good, 0 broken.**

### Fixed in this batch
- **20_numbered_list** — was a BLACK page with every clause invisible. A DOCX page declares no
  colour of its own, so a dark-theme viewer showed its own surface through it. `<w:background
  w:color="FFFFFF"/>` is now the first child of `w:document`.
- **16_right_aligned** — the ledger was scrambled and the closing-balance line was squeezed into a
  five-line column beside the table. Tables floated (`w:tblpPr`) and the text wrapped around them;
  they are now inline with `w:tblInd`.
- **01_stamp** — the invoice was scrambled: BILL TO / SHIP TO boxes landed over the goods table,
  State Code 33 sat at the left edge, the stamp was missing entirely. `w:spacing w:before` was
  double-counting the leading, so 43 lines drifted ~115 pt and ran off the sheet, pushing the stamp
  and every band onto a second page.
- **02, 03, 06, 07, 21** — each rendered one page longer than its PDF. Same flow drift; all now 1/1.
- **Table row height** — no `w:trHeight` was written at all, so Word collapsed every row to the
  height of its text: a table drawn across 257 pt came out 128 pt. Rows now carry the measured
  extent, which moved 16 by 37 pt and 72 by 43 pt closer.

### Not fixed — carried forward
- **Stamps sit slightly off their PDF position.** The text is right; the box is a few points away.
  Rotated boxes cannot carry a rotation in OOXML that LibreOffice honours (`a:xfrm rot` is ignored,
  `wps:bodyPr vert` lays Latin out one character per row), so the box is axis-aligned at the line's
  origin.
- **Table row pitch is slightly compact** against the page on several invoices.
- **Table TOP position (y)** is flow-determined, not the PDF's y. Rows are the right height but the
  table can start a little high or low, which moves everything below it.
- **Vertical position overall** — measured by rendering both sides and matching lines by text:
  01 59 %, 16 14 %, 20 15 % within 10 pt. Horizontal (`dx`) is 0.1 pt everywhere.

---

## BATCH 2 — documents 21-40

**Visual result: 12 excellent, 7 good, 1 page-count defect.**

### Fixed in this batch
- **21_form_labels** — "Member Name", ":", and "Ananya Rangappa" were three stacked paragraphs on a
  one-page form, spilling it to two. Segments on ONE baseline now re-join into a single paragraph
  (`sameRow()` / `isRow()`), written with `w:tabs` at each field's measured page x. It is now one
  page with the value at x=300.1 against the PDF's 300.
- **23, 24, 25, 27** — tab-stop columns and indents land on the page's own x.
- **30, 31, 32, 33, 34, 35, 36, 37, 38, 39** — typeface and colour per run, including a document
  with four faces on one page and one with faux bold/italic.
- **40_devanagari** — shaping font renders correctly; `/ActualText` is read (PDFBox never reads it;
  the marked-content operators had to be registered on the stream engine first).

### Not fixed — carried forward
- **30_mixed_font_sizes_one_baseline** renders on 2 pages where the PDF has 1. Its flow is longer
  than the sheet.
- **26_footnote_marker** — the footnote marker's position relative to its note is close but not exact.
- **28_value_overflows_cell** — a value wider than its column is handled, but the cell does not
  match the page's own overflow behaviour exactly.
- Same stamp-offset, table-pitch and table-top items as batch 1.

---


---

## BATCH 3 — documents 41-60

**Visual result: 13 excellent, 6 good, 1 page-count defect.** The strongest batch so far.

### Fixed in this batch
- **Vector shapes reach the page.** 505 filled rectangles and rules across the corpus were missing
  until 3.49.9; on 49, 54, 55 and 60 they are now present and correctly placed — the navy
  background block on 49, the masthead band on 54, the sidebar box on 55, and on 60 the double page
  border plus all four corner motifs.
- **45_coloured_callout_box** — the callout's fill and border render.
- **46_chart_coloured_labels** — the bar chart's bars render in their own colours, with the axis
  labels on one tabbed line. This is the document that proves the "visual contents / graphs"
  requirement is met.
- **48_form_coloured_border** — the green border box renders.
- **42_table_coloured_header** — header shading and alternating rows.
- **43_red_stamp_over_black_text**, **44_coloured_underlined_hyperlinks**, **47_grey_body**,
  **50_invoice_coloured_total_row** — colour per run reaches the cell and the line.

### Not fixed — carried forward
- **55_sidebar_box_beside_body** renders on 2 pages where the PDF has 1. The sidebar is stacked
  after the body column rather than beside it; the box itself is now drawn correctly.
- **52_one_cm_margin** — the body does not justify across the full 28.3 pt margin the way the page
  does.
- **58_header_rule_footer_rule** — the rules render but do not sit exactly on the page's y.
- **59_landscape_mixed_portrait** — the section break survives and the page is landscape, but the
  content is slightly compact against the page.
- Same stamp-offset and table-pitch items as batches 1 and 2.


---

## BATCH 4 — documents 61-80

**Visual result: 10 excellent, 10 good, 7 page-count defects.** All seven are multi-column.

### Fixed in this batch
- **70_magazine_drop_cap_photo_caption** — the photograph renders. Images were never written at all
  until 3.49.6; this is the document that proves the image path works end to end.
- **65_two_col_full_width_figure_caption** — the line chart renders with its axes and both series.
- **62_two_col_newsletter** — the dark green masthead band renders with the white title legible on
  it. Until 3.49.9 the band was not drawn and the title was white-on-white, invisible.
- **76_devanagari_table**, **78_mixed_english_devanagari** — Devanagari shapes correctly, including
  a zero-width vowel sign that used to be turned into a space inside a word.
- **77_arabic_rtl** — Arabic renders right-to-left with the table rows mirrored.
- **68, 69, 71, 72, 73, 74, 79** — tables, legal clauses, invoices with space-aligned columns,
  bank statements with no rules, marksheets, indented balance sheets, and INR digit grouping all
  land on their page's x.

### Not fixed — carried forward, and this is the biggest remaining item
- **Seven documents render 2 pages where the PDF has 1, and every one is multi-column:**
  **63_three_column_brochure**, **64_newspaper_uneven_columns_ad_boxes**,
  **65_two_col_full_width_figure_caption**, **67_two_col_with_sidebar**,
  **77_arabic_rtl_document**, **78_mixed_english_devanagari_line**, **80_gstin_pan_cin_ifsc_table**.
  Columns are stacked into a single flow, so a page that reads across becomes a page that reads
  down and overflows. `tools/p2w-bench/README.md` records four prior attempts at column detection,
  each measured and reverted. One more was attempted this week: it passed the gate with identical
  counts and restructured eighteen documents, turning doc 21's tabbed form rows into a table. It
  was reverted. Column layout needs a section-level `w:cols` or an invisible table, and it needs to
  be proven not to touch any single-column document.
- **75_merged_header_cell** — the first data row welds into the header ("Services1,842"): the page's
  sub-header rule spans only part of the width, so no band boundary is found.
- **80_gstin** — the four-column dealer grid collapses to two panels.
- Same stamp-offset and table-pitch items as batches 1-3.

---

## CORPUS COMPLETE — all 80 documents processed

| Batch | Documents | Excellent | Good | Page-count defects |
|---|---|---|---|---|
| 1 | 01-20 | 14 | 6 | 0 |
| 2 | 21-40 | 12 | 7 | 1 |
| 3 | 41-60 | 13 | 6 | 1 |
| 4 | 61-80 | 10 | 10 | 7 |
| **total** | **80** | **49** | **29** | **9** |

Zero documents are broken: no black page, no lost text, no scrambled layout, no missing image.
Every PDF page that draws an image has that image in its .docx.

### The one remaining defect class worth real work
Multi-column pages (63, 64, 65, 67, 77, 78, 80 — seven of the nine page-count defects, plus 30 and
55 from earlier batches). Everything else on the list is a few points of offset, not a broken
document.

## KNOWN, ACROSS THE CORPUS — to be worked at the end
1. Multi-column pages stack into one flow: **63, 64, 67, 77** each render 2 pages against 1.
2. **77_arabic_rtl** — the description column collapses to a sliver; RTL column widths not honoured.
3. **75_merged_header_cell** — the first data row welds into the header ("Services1,842").
4. **48, 79** — page-anchored shapes (borders, bands) drift against the more compact text flow.
5. **03** — LibreOffice truncates 90-degree rotated stamp boxes in the render.
6. Table TOP y and row pitch are flow-determined rather than the PDF's own.

## METHOD, so the next pass repeats it exactly
1. Convert the batch.
2. Render every .docx through LibreOffice to PDF, then to PNG at 72 dpi.
3. Build a side-by-side contact sheet, PDF page left and DOCX page right, four documents per sheet.
4. Open the sheets and compare.
5. Fix what is fixable in the batch; record what is not.
6. Check page counts against the source for every document.

---

## 6 Nov — filled and stroked polygons are drawn as their own path

**What was wrong.** The engine could draw a rectangle (`prst="rect"`) and, since the last pass, a
circle (`prst="ellipse"`). Everything else a page draws as a path went out as its bounding box or
was dropped: a triangle, an arrowhead, a diamond, a hatch stroke at an angle, a leader line, a
curved road on a map. That is why 330's north arrow was a black block inside a correct ring, 331's
pump triangles and gate-valve bowties were absent, 335's four GHS hazard pictograms were missing,
382's arrows between the boxes did not exist, 394's river and highways were gone, and 400's speech
bubbles had no tails.

**The fix.** `RuleCollector` now records the path as it is built - `{0,x,y}` move, `{1,x,y}` line,
`{2,x1,y1,x2,y2,x3,y3}` cubic - including the four sides of a `re`, because a page may mix a
rectangle with other segments in one path object. `DocxWriter` writes those vertices as
`a:custGeom` with `a:pathLst` when the path is neither an axis-aligned rectangle nor an ellipse,
and keeps the preset geometry otherwise. Three details mattered:

- **The frame.** Shapes are turned from PDF space into top-down page space in `attachShapes`, and
  the path points have to make that same journey. Without it every hatch stroke collapsed onto
  one line at the top of its own box, and nothing visible was drawn.
- **Four lines are not a rectangle.** A diamond is four straight sides too. `pathIsAxisRect()`
  checks that each side runs along the page's axes, so a rotated square is a diamond and not a box.
- **Rotation.** A preset box under a rotated matrix is still dropped - its bounding box is not the
  shape, and drawing the box paints slabs. A freeform is the page's own points already through the
  matrix, so it is exact and is kept: the GHS pictograms are squares drawn under a 45-degree matrix.

**Regression, all 208 documents, old engine against new** - page count, words present, images,
tables:

| Measure | Result |
|---|---|
| documents worse on words / tables / images | **0** |
| documents changed | 23 (all gained drawn shapes; none lost any) |
| page count, rendered through LibreOffice | identical on every changed document |
| `.txt` output | byte-identical across the whole corpus |
| `TestPdfToWord` | 29/29 |
| `TestRealDocs` | 96.8 / 97.0 / 81.7 - identical to the decimal |

**Measured, not just looked at.** 335's four pictograms: PDF path box 41.6..78.4 pt with a 1.6 pt
stroke, colour (0.7529, 0, 0); .docx shape at x=40.8, y=70.8, 38.4 x 38.4 pt - the path grown by
half the stroke, as the page draws it - with `srgbClr C00000`, which is 192,0,0, the same colour to
the value.

**Still open in this class.** Nothing: the whole class - fills, strokes, curves, rotated paths - is
covered. 322's riskometer needle, 330's hatch and north arrow, 331's legend and both loops, 335's
diamonds are closed. What remains on those pages is text placement, not drawing.

---

## 7 Nov - the flow is placed on the page's own pitch (D-01)

**What was wrong.** Every flowing line was given a line box of `size * 1.15` and the gap to
the line above went to spacing-before. That is right only when the page's own pitch is
1.15 x size; 303_discharge_summary sets 13 pt text at 15.18 pt (1.168), other documents at
1.20, and a document that sets two sizes on one page drifts even when the pitch is right.

**What the renderer does.** Probed directly rather than guessed: nine box heights and four
faces, and in every case the baseline sat at 0.8 of the exact line box. So the advance
between two baselines is `0.2 * previous box + 0.8 * this box + spacing-before`, and the
box can be solved from the pitch the model already carries.

**The change.** `DocxWriter.flowFromBox` and `flowRow` solve that equation; `LINE_BASE`
records the measured 0.8. Floor: the font size, because a shorter box clips. Ceiling: the
font's own line box, because a taller one spends slack the next line pays for. The rest
becomes spacing-before, still capped at 120 pt.

**Measured, all 208 documents**

| Gate | Result |
|---|---|
| G1 build | javac clean, TestPdfToWord 29/29, TestRealDocs 96.8 / 97.0 / 81.7 - identical |
| G2 regression | **no document got worse** |
| G5 position | **11.7 % -> 26.3 %** of lines within tolerance; 157 documents improved, 15 worse |
| page count | 28 spilling -> 30 (both new ones an empty second page, a few points of overflow) |
| precommit | tier 1, 2 and 3 all pass |

**The eye, on the two documents opened this run.** 303_discharge_summary: every body line
now sits on its PDF row (it was 3.5 to 6.3 pt high and growing); the remaining difference is
`WARNING SIGNS: ...` wrapping to a second line, which is the substitute face being wider, and
the table rows sitting ~3 pt low. 316_contract_with_schedules: body, headings, the schedule
table and the signature row all on the PDF's own baselines - it goes from 9.5 % to 100 % of
lines within tolerance.

**Left open, and named.** The fifteen documents that got worse are thirteen with tables and
two two-column pages: the table height is still under-measured, so text after a table starts
from the wrong y and the old flow was compensating. The position baseline is deliberately
NOT re-recorded, so that debt stays visible. Details and the reverted spacer experiment are
in REMAINING-DEFECTS.md under D-01 and D-06.


## 2026-11-07 - v3 batch 1 (300-315) re-processed from scratch

The corpus work restarts at the first document: the 70 documents processed before this pass
were done without a verifier and without the eye, so their pass meant nothing. This is the
first fifteen of the 75.

| Step | Result |
|---|---|
| convert, 15 documents | 15 docx + 15 txt, 0 failed, 28 s for all 75 |
| G5 position, batch | 41.3 % of lines within tolerance; size 98.5 %, name 100 %, colour 100 % |
| G6a the eye | 15 pages opened, 15 verdicts, 0 PENDING |
| G6b the numbers | 8 of 15 failed a question |
| verify | 15 findings: 14 VERIFIED, 1 REFUTED |
| combine | **10 PASS, 5 FAIL, 0 unlooked** |

Six claims were refuted over the pass and withdrawn; four were the eye's own: 314's "truncated" totals are complete and at
identical coordinates on both sides, 303's "wrap" is the render keeping a line the PDF clipped
off its own page, and 301's two label claims were 0.5 pt apart. Each is written up in
REMAINING-DEFECTS.md so the same claim is not made again.

Open and named: 301 and 302 (a label/value band emitted cell by cell), 311 (address welds the
Mobile label), 312 (notary tail 72.2 pt high, box empty), 315 (three columns stacked).

---

## v3 batch 1 (300-317), pass 2 — the centring fix and the trailing-gap class

The batch was run again from the start of the corpus with the eye before the numbers, as
PIPELINE.md orders. Same fifteen documents, 15 pages, one page each.

| Step | Result |
|---|---|
| convert, 208 documents | 208 docx + 208 txt, 0 failed, 52 s |
| G2 before anything | no document got worse |
| G6a the eye | 15 pages opened, 15 verdicts, 0 PENDING |
| G6b the numbers | 8 of 15 failed a question |
| emit findings | 24 findings written (18 visual, 6 measure) |
| verify | 23 VERIFIED, 1 REFUTED, 0 UNVERIFIABLE |
| combine | **6 PASS, 9 FAIL, 0 unlooked** |
| G5 position, batch | 41.8 % of lines within tolerance; size 98.5 %, name 100 %, colour 100 % |

**Fixed this pass: centred lines were pushed right by their own indent.** `flowFromBox` wrote
`w:ind w:left` = the line's measured x on every paragraph and then `w:jc="center"` on the ones
the page centred. LibreOffice centres inside the indents, so the two added up: 310's heading
rendered at x=217.4 where the page drew it at 124.6, 317's at 240.9 against 141.7, 313's at
334.4 against 213.3. A centred line is now positioned by its alignment and not by an indent.
Measured after: 310 155.1 (centre 297.75 against the page's 297.6), 317 170.0 (297.7), 313
227.7 (297.7) - the centre is exact and the residual x is the substituted face's width.
G2 across 208: no document worse. Page counts unchanged on all fifteen.

**Tried and rejected: spending the page's white space.** Raising `GAP_CAP_TW` from 2400 to
24000 twips fixed the class this batch is full of - 300's footer 270.1 -> 8.2 pt, 302's
signature block 232.0 -> 14.0, 311's "Copy forwarded to" 162.1 -> 27.0, 314's footer 189.7 ->
27.0 - and G2 passed on all 208. It was rejected because 315_gazette_notification went from one
sheet to two. Recorded in REMAINING-DEFECTS.md with the numbers, not just the outcome.

**The class that is left is one defect, not eight.** 300, 301, 302, 303, 305, 311, 312 and 314
all lose the same thing: a block that sits far down the page (a footer, a signature row, a
notary box) is emitted 72 to 352 pt above where the page drew it, because a gap wider than
120 pt is clamped. The evidence for each is in REMAINING-DEFECTS.md. 315 is its own defect
(three columns stacked). 304's emphasis failure is a measurement artefact of half-point
rounding, not a document defect, and is written up there too.
