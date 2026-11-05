# PDF → Word: batch-by-batch record

Every batch is 20 documents. Each one is converted, rendered through LibreOffice, opened, and
compared against the source PDF. What is fixed is recorded here; what is not is recorded here too,
with the reason, so the last pass can work through the list.

The corpus: `p2w-batch-1.zip`, 80 documents, numbered 01-80.

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
