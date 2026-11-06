# Strict visual findings — 80-corpus, batch 1 (documents 01-20)

Rendered both sides at 110 dpi and compared them side by side. Ranked by how hard each one is to
fix, so the easy ones are taken first and the rest are on record.

## FIXED
- **BILL TO / SHIP TO borders** (01) and **CONSIGNEE / DELIVERY ADDRESS borders** (02).
  `inTable()` classified an outline-only shape as a rule, so every bordered box that ENCLOSES a
  table was suppressed along with the table's own grid. Only a hairline is a rule now. 3.52.0.

---

## EASY — not yet fixed, worth one attempt each

**1. "State Code 33" sits above the goods table on file 01** where the PDF has it as the last line
inside the BILL TO box.
   Cause: the BILL TO box became a table, and this line fell outside the detected cell band, so it
   flowed as its own paragraph above the table. A line whose y is inside a table's vertical extent
   but whose x is inside its horizontal extent should join that table's nearest row.

**2. The DUPLICATE ISSUED / CANCELLED box on file 04 has no border.**
   The 3.52.0 fix stopped suppressing outline-only shapes, so this one should now come through. It
   was measured before that fix, not after. Re-check before doing anything.

**3. File 06's alternating row bands are darker than the PDF's.**
   There is no `w:shd` and no `tblStyle` in the XML, so the bands come from the PDF's own shapes.
   Either the fill is being emitted at full opacity where the page uses a lighter one, or the page
   draws the band more than once. Check the shape's `fillAlpha` against the PDF's ExtGState.

---

## HARD — an OOXML limitation, not a code bug

**4. Stamp and vertical-box placement — eight documents (01, 02, 03, 05, 07, 08, 09, 10).**
   What differs in each:
   | Doc | Difference |
   |---|---|
   | 01 | AUTHORISED SIGNATORY overlaps the IFSC line |
   | 02 | GOODS RECEIVED overlaps the "Total quantity" line |
   | 03 | INTERNAL AUDIT CELL box is horizontal; the PDF draws it vertically |
   | 05 | round seal renders smaller than the PDF's and lower |
   | 07 | QUALITY APPROVED stamp is offset |
   | 08 | PAID and DUPLICATE sit apart; the PDF has them overlapping at different angles |
   | 09 | FY 2024-25 AUDITED stamp is smaller and lower |
   | 10 | ORDER CONFIRMED stamp has a different rotation |

   **Why it cannot be fixed by placing the box better.** OOXML has no text rotation a LibreOffice
   render honours. Measured:
   ```
   a:xfrm rot="16200000"      written, IGNORED — text stays horizontal at the same place
   wps:bodyPr vert="vert270"  honoured, but LibreOffice lays Latin out as CJK vertical text,
                              one character per row, dropping most of the string
   a:bodyPr rot               IGNORED
   ```
   Tried and reverted: placing the box on the line's own bounding area instead of its first glyph.
   File 01 moved to a different wrong place, file 02 was unchanged, and file 08 got WORSE — its two
   stamps moved apart where the PDF has them overlapping.

   **The two honest options:**
   - leave it, and the words stay selectable but sit in the wrong place (current behaviour)
   - rasterise the stamp region into an image, and the page looks right but the words are no longer
     text — which defeats the point of a PDF-to-Word tool

   Recorded, not fixed. A decision is needed before either is done.

---

# Strict visual findings — v3 corpus, batch 2 (documents 320-341)

Rendered both sides at 130 dpi and compared them side by side, one document per sheet, then
measured every line matched by its text.

## FIXED

- **A table's start y, the paragraph under it, and a cell's bold** (`DocxWriter`, this pass).
  The spacer, the 4 pt paragraph and the face-driven bold are described in `V3-BATCH-LOG.md`.
  Effect on median vertical error: 324 goes 33.7 -> 10.7 pt, 322 85.2 -> 46.0 pt, 323 unchanged
  at 17.9 pt. Horizontal error is 0.1 pt on all three.

## EASY — one attempt each, worth taking

**1. 320 — the notes table's header row is a paragraph, not the table's first row.**
   "Note 12 - Revenue from operations" sits above the table it belongs in. The same band-boundary
   miss as `75_merged_header_cell`.

**2. 324 — the tables have no `colX`, so every column is an even split.**
   Rows, row pitch and page count are already exact; only the column edges are wrong. The row-based
   pass that found these tables has the cell x values — it is not passing them on.

**3. 322 — headings beside and above a table are claimed by the table's band.**
   Five headings become empty-celled rows. This is the batch's most repeated defect and the most
   damaging to how the document reads.

## HARD — a drawing problem, not a layout problem

**4. Vector paths. Four documents: 322 (riskometer), 330 (hatch, revision marker), 331 (legend
   icons, circled P), 335 (GHS pictograms).**
   Rasters are correct everywhere — every barcode and QR code in this batch renders. Paths are not:
   a patterned fill becomes solid black (330), a stroke-only path disappears (331, 322), and a
   coloured fill with a thin outline is partly lost (335). This belongs in `PdfEngine` and needs its
   own before/after plus a whole-corpus gate, because a shape pass that goes wrong is how a page
   turns black.

## CHECKED AND CLEAN

- **340_bill_of_lading** — a full form: header band, two-column shipper/consignee blocks, a
  six-column goods table, three signature boxes and a Code-128 barcode. Every field lands, the
  barcode renders, and the page count is 1/1.
- **341_shipping_manifest** — 304 .txt lines at 100 % position accuracy, 378 of 378 words.
- **326_itr_computation** — the QR code renders; the three tax tables keep their own column edges.
- **333_datasheet_spec_tables**, **334_patent_document**, **325_demat_holdings_statement**,
  **321_auditors_report**, **332_bom_on_drawing** — no visible difference from the page beyond a
  few points of vertical drift.
