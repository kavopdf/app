# 64_newspaper_uneven_columns_ad_boxes: the column row's top edge came from ONE column

Measured, fixed, and kept 20 Nov. `share@5px` **9.11 -> 3.46** (-5.65), `max_pt` 11.04 -> 6.72,
`text_recall` 100.0 before and after, one page.

## The document

Rank 6 in `RANKING.csv`, `content-present-partly-displaced`. Nothing is missing: `src_chars` 2597,
`docx_chars` 2805, `chars_missing` 0, `text_recall` 100.0, `dx_pt` 0.0, `dy_pt` 1.0. The census
signal is `none-identified`, which is correct - the evidence in the census does not name a
mechanism, and the mechanism is geometric.

It is a one-page newspaper with three uneven columns and three classified ad boxes in the third.

## The mechanism

`PdfToWord.recutColumnBands` (PdfToWord.java:8476) recognises the page as a band-major ruled grid
and re-cuts it to ONE row of one cell per column. That row has one top edge, and every cell is
placed from it. The edge was computed like this:

    float colTop = t.rowEdge[0];
    for (int c = 0; c < cols; c++) {
        List<Table.CellPara> ps = u.parasAt(outRow, c);
        if (ps.isEmpty()) continue;
        colTop = Math.max(colTop, ps.get(0).baseY - 0.8f * size);
        break;                       // <-- first non-empty column wins, then stops
    }

On this page that yields 122.77 pt - column 1's box top. The classifieds column starts at 112.4 pt.
`DocxWriter` stacks the re-cut rows from the table top and gives each cell its own `w:before`,
computed as `wantPt = itsBaseY - rowTopPagePt` and **clamped at zero** (nothing can pull a cell up).
Instrumented on this document:

    CELL r=1 c=0 nparas=27 cellBaseY=129.485 rowTopPagePt=122.75 wantPt= 6.735  written
    CELL r=1 c=1 nparas=26 cellBaseY=129.485 rowTopPagePt=122.75 wantPt= 6.735  written
    CELL r=1 c=2 nparas=18 cellBaseY=122.000 rowTopPagePt=122.75 wantPt=-0.750  REJECTED

So the third column - heading, three ad boxes, its last line - was written 10-11 pt low by exactly
`colTop - its own top`, and that is the 9.11% of ink.

## The change

`colTop` is now the **minimum** over the columns' own first-line box tops (each lower column gets
its own `w:before`), falling back to `t.rowEdge[0]` when no column holds text. That is the
flowing-text model: one row, one top, and position carried by spacing.

## What it is worth, honestly

**It is structural but narrow.** The rule is general - one top edge for a whole column row, taken
from one column, with per-cell placement clamped non-negative - and it misplaces every re-cut page
whose columns do not all start at the same height. But `recutColumnBands` fires on **exactly one
document in the corpus**: 64 itself. The eleven other column-layout documents
(`annual-review-2col-uneven-columns`, `newspaper-2col-fullwidth-headline`,
`newsletter-3col-header-footer`, `62_two_col_newsletter_pull_quote`, `61_two_col_abstract_spanning`,
`67_two_col_with_sidebar`, `report-2col-table-spanning-both-columns`,
`table-inside-two-column-page`, `69_two_col_legal_numbered_clauses`,
`27_two_column_left_short_txtpos`, `brochure-3col-with-sidebar-box`) do not take the re-cut at all.
So this moves one document, not a class - and it is recorded as one attempt, not as a class fix.

## The corpus ratchet

Full corpus, this engine: **212 of 212 scored documents measured** (`416_many_tiny_pages` is
exempt by `EXEMPT.json`), **1 better, 0 worse**. The .txt half re-scored over all 213 documents
with the same engine: **0 newly clean, 0 newly failing, 213 unchanged** - the re-cut cannot move
the .txt, and that is now measured rather than asserted. `regress.py --check` PASS.

## What is left on this document

The residual 3.46 is a separate, smaller constant: the two prose columns' own first lines are
~1.2 pt low because their `w:before` is clamped at 0 (6.735 pt wanted, 7.92 pt given by `0.8 x box`).
That is a different construct - the cell's first-line offset - and it was not touched here.

## What would prove this wrong

If a page's columns all start at the same height the minimum equals the first column's top and
nothing moves; if the classifieds cell's own baseline were at or below the computed edge there
would be no offset to correct. Neither holds here, and the measurement moved 5.65 points.

## Do not

* Do not take the maximum again to "keep the row tight" - that is the defect.
* Do not chase the remaining 3.46 with this construct; it is the `w:before` clamp, not the row edge.

## Google, 20 Nov - the renderer the user opens

Measured through `gverify.py` after the fix landed (Google Doc created, exported, scored, deleted):

    64_newspaper_uneven_columns_ad_boxes      GOOGLE 37/42   fail: 05_chars_extra,
                                                            18_displacement, 23_line_pitch,
                                                            26_text_overlap, 59_shape_anchor
                                              LIBRE  41/42   LO fail: 18_displacement

The one check LibreOffice fails is `18_displacement`, the same defect this change reduced - and it
still fails, which is consistent with the 3.46 residual (the `w:before` clamp), not with the row edge.
There is **no earlier Google result for this document** (`gverify/results/` had none), so this is the
first Google measurement of it and no before/after can be claimed through Google. The LibreOffice
before/after (9.11 -> 3.46) is measured; the Google side is a first reading, not an improvement.
