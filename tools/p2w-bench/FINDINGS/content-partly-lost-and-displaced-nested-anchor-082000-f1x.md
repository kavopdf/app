# content-partly-lost-and-displaced / nested table — the cell's afterTablePt survives the nested table

Run: 20 Nov 2026, fixer slot claimed 06:53 IST. Engine `4e61dfd`. Class: content-partly-lost-and-displaced.

## The mechanism (measured, not reasoned)

`columnPage()` sets `ctx.afterTablePt = rowEndPt` — the LAYOUT ROW's top edge — for each cell, so the
cell's first line is placed against that edge. When the cell's content contains a **nested `w:tbl`**,
`table()` writes the nested table and its 4 pt carrier paragraph, and the carrier is raw XML: it never
passes through the paragraph path, so nothing clears `afterTablePt`. The first paragraph AFTER the
nested table therefore hits the `afterTablePt` branch in `flowFromBox()` and is placed at
`topPt - afterTablePt` = the distance from the **layout row's top**, not from the nested table's bottom.

Instrumented on `table-inside-two-column-page` (temporary `System.err` prints, since removed):

    NESTED top=117.0 bottom=228.0 rowBottom=228.0 flowY=-1.0 afterTbl=107.4 carrier=true carrierTw=80
    BIGBEFORE before=2600 absTop=237.37903 flowY=232.0 inCol=true newPage=false y=237.7544

`flowY` was already right (232.0 = row bottom 228 + 4 pt carrier). The paragraph was placed from
107.4 instead, so its `w:before` came out 2600 twips (130 pt) where the page drew 4.2 pt. The caption
under the metrics table and the three paragraphs below it sat **115.4 pt too low** — 78.4 % of that
document's whole share@5 deficit.

## The change

In `table()`, where the row-bottom anchor is written: when `ctx.inColumn`, clear
`ctx.afterTablePt = -1f` as well as the existing `cenCellFlowY++`. The paragraph after a nested table
is then placed from `flowY`, which is the row's bottom edge plus the carrier — where the reader is.

Patch: `patches/PATCH-nested-table-clears-cell-anchor-082000-f1x.patch` (one hunk, DocxWriter.java).

## What it measures

    table-inside-two-column-page   38.11 -> 35.87   (-2.24)
      share@10  29.13 -> 9.70     max_pt 82.08 -> 21.60    p90 64.32 -> 6.24   median 3.84 -> 2.88

Class screen (`content-partly-lost-and-displaced`, 6 documents): **1 better, 5 same, 0 worse.**

The share@5 gain is small because what is left on that page is a uniform ~2.9 pt offset (median
2.88 pt = 6 px), not the 115 pt outlier — the outlier is gone, and share@10 and p90 say so. The
nested table itself is still 9.7 pt high, and `itr-computation-with-slab-table` is untouched: its
rows are written at `w:trHeight` 351/370 tw against the page's uniform 368 tw, a different mechanism
(`DocxWriter.java:6182`, `:6271-6273`).

## What was ruled out

* Not content loss: `text_recall 100`, `chars_src == chars_ours` on both documents.
* Not the nested table being dropped or emptied: 2 `w:tbl`, 6 rows x 4 cells, 0 empty cells.
* Not a gap/arithmetic error: `flowY` was correct at the boundary; the anchor was the wrong edge.
* Not the rule class: this is unrelated to `w:pBdr` and touches no drawing.

## Next

`itr-computation-with-slab-table` (share@5 42.33, share@10 27.40, share@20 7.85) is a table row
pitch problem: rows at 351/370 tw against 368. The corpus pass for this patch was run by the same
slot; see ATTEMPTS.json.
