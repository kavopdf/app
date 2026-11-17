# The wrap charge at corpus scale - 47 of 213 change, 40 of 46 worse

Run: 17 Nov 2026, fixer slot, carry-over item 1 from the previous run's HANDOFF.

## What was asked
"Re-convert all 213 documents with the wrap charge, diff the .docx entry by entry and write down
HOW MANY change before measuring a single one - the answer decides whether this fits in a slot at
all. If it is most of the corpus, that is a ratchet job for a run with the whole hour."

## What was built
`DocxWriter.table(...)`, the real-table path:
- `wrapLinesHelv(cv, sz, bold, spanTw, insetTw)` - PDType1Font.HELVETICA / HELVETICA_BOLD
  `getStringWidth` / 1000 x sz; the cell's text split on its own `\n`; each paragraph
  `ceil(textWidth / avail)`; a paragraph that fits charges one line.
- the row charged `max(rowHeightTw, wrappedLines x rowLineTw)`, written into `w:trHeight`, which
  is `hRule="atLeast"` on this path.
- `writtenRowsTw` (the flow's budget after the table) follows `rowHeightTw`, so a row laid out
  taller is taller for what follows it.
- a spanning cell is charged the sum of the columns it covers (`spanCAt`), which removed an
  849 pt row on 041122 that the first build produced.

## The diff (the number that was asked for)
213 documents converted twice from the same corpus, same JDK, same classpath: HEAD engine ->
`/scratch/work/diff/A`, charged engine -> `/scratch/work/diff/B`. Compared every zip entry.

| | |
|---|---|
| documents | 213 |
| changed | **47 (22 %)** |
| entries that differ | word/document.xml only, all 47 |
| rows that grew | 350 |
| rows that shrank (squeeze) | 65 |
| largest single row | +161.1 pt, 360_restaurant_menu |

22 % is not "most of the corpus", so the answer to the slot question is: it fits.

## The measurement (the 47 are the only documents that can move)
Each changed document measured against itself, both engines, same instrument (`p2w.measure_doc`,
scipy EDT). 46 of 47 comparable; `01_stamp_rotated_15deg_upright` fails to render on both.

| | |
|---|---|
| improved | **0** |
| worse | **40** |
| flat | 6 |
| mean share@5px loss | **10.66 % -> 32.63 %** (lower is better) |
| 041122-Account_Opening_Form | 99.02 -> 99.02, 11 pages -> 11 pages (no change) |

Worst movers: price-list-right-aligned-amounts 1.79 -> 81.15; price-list-2col-dense-right-aligned
2.69 -> 81.69; 41_coloured_headings_white_bg 0.00 -> 70.84; 80_gstin_pan_cin_ifsc_table
2.01 -> 58.03; 59_landscape_mixed_portrait 0.00 -> 42.12.

## Why - the width the charge reads is not the width the renderer uses
`41_coloured_headings_white_bg` is written with a 6-column grid
(8876,570,8876,570,8876,570 tw = 1416 pt of grid on a 595 pt page) holding two cells per row.
The price column therefore reads 28.5 pt wide for the 30.6 pt text "340.00", every row is charged
two lines, and every trHeight goes 360 -> 500. In the render the page doubles its leading while
the source is a tight one-page price list - a number that moved up and a page that looks worse.

Two structural guards were built and measured: (1) the grid's columns must add up to the table's
own width within 5 %, and (2) no row may carry fewer cells than the grid has columns unless a span
table says which cells cover which. Neither fires on this document, because the table's own
bounds are wrong in the same way the grid is and `spanC` exists (so the cell-count test passes).
A corrupt grid cannot be caught by comparing it with itself.

## What the next run should do
Do not re-land this charge against `w:tblGrid`. The width it needs is the width the RENDERER gives
the cell - the `w:tcW` after spans, or better, the page's own cell rectangle
(`t.cellX` / `t.spanC`), which is where the PDF says the text was drawn. Calibrate that width on
`41_coloured_headings_white_bg` (must stay at 360 tw rows) and on `041122`'s instruction row (must
grow) BEFORE converting the corpus again; the two documents disagree in exactly the way that
separates a real column width from a grid artefact.
