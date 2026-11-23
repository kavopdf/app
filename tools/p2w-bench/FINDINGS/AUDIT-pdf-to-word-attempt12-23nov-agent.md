# PDF-to-Word — deep audit, attempt 12 of 15

Agent, 23 Nov 2026. Read-only. Second of five focused on `DocxWriter`. It was meant to be the tables — the "biggest
single class" I had been telling the user about. **It is not, and this attempt corrects me.**

---

## L1 — the table writer is a geometry container, by design

`DocxWriter` at 2170 writes:

    <w:tbl><w:tblPr>
      <w:tblW w:w="…" w:type="dxa"/>
      <w:tblInd w:w="…" w:type="dxa"/>
      <w:tblBorders>  all six sides: w:val="none"  </w:tblBorders>
      <w:tblLayout w:type="fixed"/>
      <w:tblCellMar>  top/left/bottom/right all 0  </w:tblCellMar>
    </w:tblPr><w:tblGrid>…

**`fixed` layout with explicit widths and zero cell margin, and every border set to `none`.** The table carries
geometry and nothing else: the rules a reader sees are drawn separately as shapes. That is a coherent choice —
it keeps the table's cell boundaries exactly where the PDF had them, and stops Word from adding the hairline
borders it would otherwise draw.

No finding here. Recorded because the next section is about what the checks say about it.

---

## L2 — CORRECTION: tables are the strongest area, not the weakest

I have been telling the user, across three attempts, that "62 documents fail checks 62-66" and that tables are
the biggest single class. **Both halves of that are wrong.** Measured:

    documents by check-count      : {42: 126, 47: 62, 44: 2}
    documents that RUN the table
    checks (total = 47)           : 62
    total table-check FAILURES
    across all 62 of them         : 12

       66_table_cell_width    4 documents
       62_table_columns       3
       63_table_rows          3
       64_table_span_across   1
       65_table_span_down     1

**62 is the number of documents that *run* the table checks. Twelve failures exist in total.** That is roughly a
4% failure rate on tables across five checks — **the best-performing area in the corpus, not the worst.**

The error is mine and it is worth naming precisely: I read "62 documents with total=47" as "62 documents failing
the table checks", and then repeated it as a priority without re-deriving it. Attempts 13-15 would have gone to
the wrong place.

---

## L3 — the real ranking, so the next three attempts go where they matter

Every scored document's `failed` list, counted by documents affected:

    check                        documents
    18_displacement                  100
    04_chars_missing                  65
    60_text_column_right_edge         56
    25_invisible_text                 48
    32_stroke_lines                   47
    59_shape_anchor                   45
    05_chars_extra                    43
    45_char_accuracy                  37
    13_text_colours                   32
    44_header_footer                  31
    17_matched_runs                   30
    47_margins                        25

**`18_displacement` alone touches 100 of the 190 scored documents — over half the corpus.** And it is about
position, which is the property the user names first every time.

**So the real shape of the tool's weakness is not tables, and not colour, and not fonts. It is displacement —
text that arrives in the right document but not at the right place — and it accounts for more documents than the
next two checks combined.**

---

## L4 — what this means for attempts 13-15

The five-attempt plan I set at the start was: document body, tables, positioner, styles, the rest.

**Tables are done and are not a problem (L2).** The remaining three should be:

- **13 — the positioner (4198) against `18_displacement` (100 documents).** This is the highest-value read in the
  whole codebase and it has not been opened.
- **14 — `04_chars_missing` (65) and `05_chars_extra` (43).** Character accounting: what the writer drops and what
  it invents. Attempt 8's surrogate finding (H2) is one mechanism for the first of these.
- **15 — `60_text_column_right_edge` (56) and `25_invisible_text` (48).** Column geometry and text that is written
  but not visible.

**Styles (4941) and the anchor section (4741) drop off the list**, because `13_text_colours` is 32 documents and
`59_shape_anchor` is 45 — real, but behind displacement, and the anchor section is where attempt 5's stamp
history already lives.

---

## For the fixer

**L2 is the finding: do not spend a run on tables.** If a class list has been built that ranks the table checks
high, it is built on the same misreading I made, and it should be rebuilt from the `failed` lists rather than
from `total`.

**L3 is the ranking to work from**, and it is reproducible in five lines against `benchmarks/gverify/*.json`.

Verify before changing. This attempt read code and counted verdicts; it ran nothing.
