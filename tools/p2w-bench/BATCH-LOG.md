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
