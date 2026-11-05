# Strict visual findings — 80-corpus, batch 1 (documents 01-20)

Found by rendering both sides at 110 dpi and comparing them side by side.

## Fixed
- BILL TO / SHIP TO borders (file 01) and CONSIGNEE / DELIVERY ADDRESS borders (file 02).
  `inTable()` classified an outline-only shape as a rule, so every bordered box that ENCLOSES a
  table was suppressed along with the table's own grid. Only a hairline is a rule now.

## Not fixed — all ten are stamp or box placement, not text

| Doc | What differs |
|---|---|
| 01 | "State Code 33" sits above the goods table; the PDF has it inside the BILL TO box. The AUTHORISED SIGNATORY stamp overlaps the IFSC line. |
| 02 | The GOODS RECEIVED stamp overlaps the "Total quantity" line. |
| 03 | The INTERNAL AUDIT CELL box is horizontal; the PDF draws it vertically. |
| 04 | The DUPLICATE ISSUED / CANCELLED box has no border, and its words overlap the table edge. |
| 05 | The round seal renders smaller than the PDF's and lower on the page. |
| 06 | The table's alternating row bands are darker than the PDF's. |
| 07 | The QUALITY APPROVED stamp is offset from where the PDF puts it. |
| 08 | PAID and DUPLICATE sit apart where the PDF has them overlapping at different angles. |
| 09 | The FY 2024-25 AUDITED stamp is smaller and lower than the PDF's. |
| 10 | The ORDER CONFIRMED stamp has a different rotation from the PDF's. |

## Why the stamps are not fixable by box placement

OOXML has no text rotation that a LibreOffice render honours. Measured:
    a:xfrm rot="16200000"      written, ignored — text stays horizontal at the same place
    wps:bodyPr vert="vert270"  honoured, but LibreOffice lays Latin out as CJK vertical text,
                               one character per row, dropping most of the string
    a:bodyPr rot               ignored

Tried and reverted: placing the box on the line's own bounding area instead of its first glyph.
File 01 moved to a different wrong place, file 02 was unchanged, and file 08 got worse — its two
stamps moved apart where the PDF has them overlapping.

The honest options are to leave it, or to rasterise the stamp region into an image, which loses the
selectable text.

## Also not fixed
- File 06's alternating row bands: there is no `w:shd` and no `tblStyle` in the XML, so the bands
  come from the PDF's own shapes; the .docx fill is simply stronger than the page's.
- File 03's vertical box: the same rotation limitation.
