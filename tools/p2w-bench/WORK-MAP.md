# Where the work is, split by benchmark

Every row is a measured number, not an estimate. The gap column is what a user loses.
Work top to bottom: the first two rows are worth more than everything below them.

| # | Benchmark | Now | Target | Gap | What the gap means to a user | Work item | Size |
|---|---|---|---|---|---|---|---|
| 1 | table count match | 84.62 % | 95 % | **10.4** | a whole table missing, has to be rebuilt by hand | see below | 1 fix |
| 2 | table row accuracy | 90.98 % | 95 % | **4.0** | rows missing from tables that did convert | same fix | — |
| 3 | line order accuracy | 79.58 % | 90 % | **10.4** | document reads in the wrong order | column detection | hard |
| 4 | line count match | 93.86 % | 96 % | 2.1 | lines merged or split | follows 3 | — |
| 5 | exact line hit | 89.06 % | 95 % | 5.9 | lines differ from the original | follows 1 and 3 | — |
| 6 | word recall | 95.95 % | 98 % | 2.1 | words missing | font/encoding cases | medium |
| 7 | table cell accuracy | 95.90 % | 98 % | 2.1 | cell text wrong | follows 1 | — |
| 8 | doc pass @98 % | 65.52 % | 80 % | 14.5 | two in three documents need editing | all of the above | — |
| 9 | doc pass @95 % | 71.92 % | 85 % | 13.1 | three in ten documents need editing | all of the above | — |
| 10 | global line hit | 95.85 % | 98 % | 2.2 | lines missing across the corpus | follows 3 | — |
| 11 | char volume | 97.44 % | 98 % | 0.6 | characters missing | not worth chasing | — |
| 12 | garbage rate | 0.02 % | — | 0 | nothing | already clean | — |
| 13 | median per-file | 100.00 % | — | 0 | typical document is perfect | already clean | — |

## Rows 1 and 2 are one bug

The bill of quantities on `314_tender_rfp_boq` is detected, survives both filters, and
reaches `page.blocks` with `top=1003` on a page 842 pt tall. Its cells are empty because
no glyph falls inside them, and `DocxWriter` silently skips a table with no columns.

Clamping the edge y into the page did **not** fix it, so the bad value is produced
somewhere else. The next step is to print the actual cell rectangles for that table -
`c0..c3` of each cell in the second group - and compare them against the glyphs on the
page. Two numbers will show whether the y is wrong, the x is wrong, or the cell list is
from a different page.

Everything else in the table column follows from this one fix, because the missing tables
are the same failure everywhere.

## Row 3 is the hardest and the least understood

Four approaches tried and reverted, all written up in README.md. The blocker is that
column detection returns nothing for the four worst files, and their line starts are
fragmented (ten x-clusters, not three columns). Two candidate approaches remain: a
recursive XY-cut on glyphs per vertical band, or detecting the fragmented layout and
keeping the original order instead of guessing wrong.

## What is already done and should not be touched

    median per-file        100.00 %   typical document is perfect
    garbage rate             0.02 %   no mojibake
    48.3 % of files         100 %     perfect line reproduction
    table cell accuracy     95.90 %   cells that exist are right
    char volume             97.44 %   close enough that no user notices

## How to use this file

Run both scorers before and after every change:

    python3 tools/p2w-bench/score.py <out>          # 13 text metrics
    python3 tools/p2w-bench/score_tables.py <out>   # table metrics

A change ships only if no row above goes down. Two or three rows may dip 0.5 % and no
more. The floor in this file is the reference; update it only when a change ships.

## Shipped in 3.46.6 — rows 1, 2 and 7 together

`rowTables` used to run only when the ruled pass found nothing. A page with one ruled
table and one unruled table therefore lost the second without a word: the tender document
came out with its summary table and no bill of quantities. It now always runs, and any
table it finds that the ruled pass did not is added.

    table ROW accuracy   90.98 -> 95.55   +4.57
    table CELL accuracy  95.90 -> 98.75   +2.85
    table count match    84.62 -> 86.54   +1.92
    line order           79.58 -> 79.82   +0.24

    char volume          97.44 -> 97.38   -0.06   within the 0.5 allowance
    line count match     93.86 -> 93.75   -0.11   within the 0.5 allowance

Everything else flat. Rows 1, 2 and 7 of the table above are one fix, as predicted.
