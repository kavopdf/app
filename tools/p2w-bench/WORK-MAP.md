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

## Which fixes lift more than one benchmark for free

This is the useful half of splitting by benchmark. A fix is worth far more when it lands
on a number that several benchmarks are computed from, and some fixes are nearly free
because they are already half-done.

### One fix, four benchmarks

`line order`, `line count match`, `exact line hit` and `global line hit` are all computed
from the same thing: **the list of lines**. Any fix that gets a line right moves all four.

    line order accuracy   79.82 %      exact line hit   89.06 %
    line count match      93.75 %      global line hit  95.85 %

This is why the column work is worth so much even though it is hard: it is the only thing
that moves four numbers at once.

### One fix, three benchmarks

`table count match`, `table row accuracy` and `table cell accuracy` all come from the same
list of tables. That is what 3.46.6 proved - one line in the detector moved all three:

    table rows  90.98 -> 95.55      cells  95.90 -> 98.75      count  84.62 -> 86.54

### One fix, two benchmarks

`doc pass @95 %` and `doc pass @98 %` are thresholds over per-file exact line hit. Every
improvement anywhere that lifts a file past 95 % or 98 % moves these two as well. They are
the cheapest numbers to move late, and the most honest: they count documents, not lines.

### Already free, do not spend time here

    median per-file   100.00 %   half the corpus is perfect already
    garbage rate        0.02 %   nothing to fix
    char volume        97.38 %   0.6 from target, and no user notices

### The multiplier nobody expects

A fix that removes lines the reference does **not** have is worth double. `350_question_paper`
produces 117 lines where the reference has 104. Thirteen of those are ours alone, and each
one costs line count match, exact line hit and global line hit at the same time. Removing an
invented line is worth more than adding a correct one.

### Where the remaining work actually is

    line order 79.82 %   4 benchmarks, hard, 5 approaches already reverted
    table count 86.54 %  1 real miss left (a table rotated inside an upright page)
    exact hit 89.06 %    follows line order, plus ~230 misses from text held twice in the file

## Three more attempts, all reverted, all measured

Recorded so they are not tried again blind.

### Deduplicate lines with the same text and baseline

`350_question_paper` emits 60 lines the reference does not have, and they are only three
unique strings repeated twenty times each. Deduplicating them looked like the highest-value
fix in the file - four benchmarks from one change.

    char volume      97.38 -> 97.11   -0.27
    word recall      95.95 -> 95.59   -0.36
    line count match 93.75 -> 93.39   -0.36
    line order       79.82 -> 79.62   -0.20

Reverted. The repeats are real content the reference also carries; the words still have to
be there. Removing a duplicate removes words the metric counts.

**And a trap worth naming:** the 60 "extra" lines were counted against a `set` of reference
lines. A set hides duplicates, so 60 extra looked like duplication when the reference had
the same words on different lines. Always count against the **list**, not the set.

### Split any field that starts past 90 % of the line width

The marks column sits at x=551.9 with the question running to x=549, so the gap is 3 pt and
the outlier test never fires. Splitting at 90 % of the line width looked exact.

    global line hit  95.85 -> 93.26   -2.59
    doc pass @95 %   71.92 -> 68.47   -3.45
    exact line hit   89.06 -> 88.62

Reverted. Justified text puts its last word past 90 % constantly, so the rule split
sentences everywhere.

### Run the XY-cut always instead of gating it on bands > 1

    line order 79.82 -> 79.29

Reverted. The gate exists for a reason.

## What this says about the remaining work

Three plausible, well-reasoned fixes in one session, all measured, all negative. The two
remaining failures are not threshold problems:

- the marks column is welded on because the **question text runs into it** - the split has
  to be decided on the glyph level with the column geometry, not on the gap
- the multi-column pages fail because column detection returns nothing for fragmented
  layouts

That is why Group A and Group B in TEST-CORPUS-REQUEST.md matter: more examples of these
two shapes are the only way to tell a fix from a coincidence.
