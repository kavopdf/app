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

## Second build: the metric's own error was manufacturing lines
The first build charged a cell whenever its text was wider than its column. Helvetica's advances
are only within a few per cent of DejaVu Sans, and the commonest cell in this corpus sits AT its
column width, so the estimate's error alone turned one-line cells into two: 41_coloured_headings'
price cell is 28.5 pt wide for 30.6 pt of text (7 % over), and every row doubled.

Rebuilt with the error budget named - avail x 1.08 - and the grid guards kept:

| | first build | with 8 % allowance |
|---|---|---|
| documents changed | 47 (22 %) | **32 (15 %)** |
| 41_coloured_headings rows | 360 -> 500 tw (wrong) | 360 tw (right) |
| 041122 rows moved | 0 | 6, largest +12.2 pt |
| improved / worse / flat (measured) | 0 / 40 / 6 | **0 / 28 / 4** |
| mean share@5px loss | 10.66 -> 32.63 | 13.85 -> 30.36 |

The allowance did what it was meant to do and the verdict did not change: **charging rows their
wrapped height, as a charge, loses on this corpus.** Worst movers in the second build:
80_gstin_pan_cin_ifsc_table 2.01 -> 61.11, 77_arabic_rtl_document 17.14 -> 58.55,
72_bank_statement_no_rules_right_amounts 0.00 -> 41.02.

## Third build: the differential charge, and the verdict
Charging only the EXCESS over the page's own row height (`pageLines = round(rowHeightTw /
rowLineTw)`; charge only when the Helvetica estimate needs more), with the 8 % allowance kept:

| | v1 flat | v2 + allowance | v3 differential |
|---|---|---|---|
| documents changed | 47 (22 %) | 32 (15 %) | **24 (11 %)** |
| 41_coloured_headings | rows doubled | right | **untouched (0/12 rows)** |
| 041122 rows moved | 0 | 6 (+12.2 pt) | **7 (+24.9 pt)** |
| improved / worse / flat | 0 / 40 / 6 | 0 / 28 / 4 | **0 / 18 / 5** |
| mean share@5px loss | 10.66 -> 32.63 | 13.85 -> 30.36 | 16.08 -> 31.52 |

v3 is the best calibration of the three - it leaves the correct tables alone and it grows the row
it was aimed at by almost exactly the 45 pt the earlier run measured - and it still loses. Worst:
80_gstin_pan_cin_ifsc_table 2.01 -> 61.11, 77_arabic_rtl_document 17.14 -> 62.35,
76_devanagari_table 19.54 -> 57.90, 64_newspaper_uneven_columns_ad_boxes 9.11 -> 39.50.

**The verdict, after three builds and 124 document-measurements: raising a ruled table's rows is
not a corpus-wide lever on this engine.** The mechanism is real (041122 charges 111 pt for 156 pt
of content) but the fix is not a row height. Growing a row lengthens the page instead of closing
it, and the flow after the table is then wrong by exactly what was added.

## What the next run should do
Do not re-land any of the three row-height builds. The numbers are in the tables above and the
code is gone from the tree.

What is left is not a row height. `041122`'s page is 111 pt of charged table against 156 pt of
laid-out content, and charging the difference does not close the page - it lengthens it, and the
page break is decided by the whole sequence of rows, not by the row that overflows. The next
experiment is a PAGE-layout one: after a table's rows are charged, the bands that follow it must
be re-flowed onto the page's remaining height (the same number the charge added, subtracted from
what the page has left) rather than allowed to overflow. That is a bigger change than a fixer
slot and should be planned as one.

If it is attempted, the calibration pair is already chosen and costs two conversions:
`41_coloured_headings_white_bg` must keep its 360 tw rows and `041122-Account_Opening_Form`'s
instruction row must grow. The corpus diff is cheap - 2 x 71 s to convert, ~7 s a document to
measure - and the 213-document answer is the only thing that decides it.
