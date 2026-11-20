# t13_amount_columns is closed: the last document was a welded cell, not table geometry

20 Nov 2026, fixer. Engine before `0fc8b7e`, after this commit. Check `t13_amount_columns` of
`tools/p2w-bench/verify_txt.py` (unmodified). Measurement: the whole corpus re-converted with the
new engine and re-scored with `restamp_txt.py --run --force`.

## The starting premise was stale, and the first thing this run did was disprove it

`DEFECT-CLASSES-TXT.md` said six documents failed `t13`. They did not. Converting all six with the
head engine and scoring them with the live verifier gave:

| document | head | failed |
|---|---|---|
| 22_invoice_four_columns_txtpos | 10/10 | - |
| 29_dot_leaders_txtpos | 10/10 | - |
| 74_balance_sheet_indented_subitems | 9/10 | t02_position |
| balance-sheet-two-columns-of-figures | 10/10 | - |
| gst-invoice-multipage-item-table | 11/12 | t09_page_furniture |
| itr-computation-with-slab-table | 8/10 | t08_line_order, **t13_amount_columns** |

`tools/p2w-bench/txt/RANKING-TXT.csv` agreed with that: exactly one row carried `t13`. The
`DEFECT-CLASSES-TXT.md` beside it was generated from a snapshot before `0fc8b7e` and was never
regenerated. **A class table that is one engine behind sends the next run at five documents that
already pass.** `classify_txt.py` is the fix and it was not run after the last keep.

## The wall was real but it was not geometry

The previous run wrote this document off as "table geometry, needs a .docx measurement". It is not.
It is a **welded cell**, and the model already carried the number needed to fix it.

`Table.rows` holds one string per cell, so a cell the page drew two lines in arrives as those two
lines joined by `\n`, and `Table.cellX` is the cell's BOX - the x of the FIRST line in it. On
itr-computation-with-slab-table, cell [7,1] of the slab table holds the running head `Page 1 of 1`
at x 517.18 above the figure `10,000.00` at x 502.66. The 14.5 pt difference is 3.4 columns on that
document's 4.2 pt ruler. Measured from the box, the figure's base column is 123; measured from its
own line it is 120. `Table.paras` (the per-line model) records both x values, so the figure can be
measured where the page drew it.

Two things had to change, and the second is the one that moved the number:

1. `tableEndSnap` and both passes of `appendTable` now take a numeric part's base column and right
   edge from `Table.paras` for that part, falling back to the cell box when the cell recorded no
   paragraphs (which is nearly every cell - `paras` is empty for single-line cells by design).
2. **The numeric part's own base column replaces the cell box as the floor for where it starts.**
   With the box kept as the floor, a target of 130 asked for a start of 121, the guard
   `if (startCol > col)` kept 123, and the figure still ended at 132. That is why the first version
   of this change moved nothing: it fixed the count and left the emit pass measured from the box.

`target` is a max over cells that include this one, so it is never less than this line's own base
plus its length, and nothing can move left of where the page drew it. Line counts do not change -
only the padding in front of a figure - so `t04_structure` cannot drift.

## What the corpus says

    before (published table)   181 of 213 clean, itr fails t08 + t13
    after                      182 of 213 clean, itr fails t08 only
    1 newly clean, 0 newly failing, 210 unchanged (211 re-converted + 2 carried)

The published `RANKING-TXT.csv` diff is one line. `regress.py --check`: PASS, txt scope, no document
worse than baseline.

## Two things the next run must not have to rediscover

* **`p2w.py` measures origin's head, not your working tree.** Its `engine()` does
  `git checkout -q -f FETCH_HEAD` into `/scratch/work/p2w/repo`, so `p2w.py --force` after a local
  edit converts the PUBLISHED engine and reports it as your change. A working-tree measurement has
  to run `tools/engine-verify/ConvertOne` out of the clone (`build-engine.sh` compiles the tree into
  `tools/engine-verify/out`). A full corpus re-conversion that way is ~211 documents at ~10 s each,
  two JVMs at a time on this pod's 2 cores, so about 20 minutes across five calls.
* **`restamp_txt.py --apply` cannot run in a fresh sandbox.** Two rows of the 213 -
  `041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled` - have no PDF in any
  corpus-v1 release zip and none in `benchmarks/corpus-extra/`, so they score
  `{"error": "missing pdf or txt"}` and `apply()` refuses on the first error. Their last committed
  records were appended to `RESTAMP-TXT.jsonl` after the error records, so `done()` keeps the real
  numbers and the table could be written. **They are carried, not re-measured, and their row in the
  table is unchanged.** Neither fails `t13`, and this change cannot reach a document with no numeric
  table cell, so the carry cannot hide a regression from this change - but it is a carry and it is
  recorded here rather than in a footnote.

## Status

`t13_amount_columns` has 0 documents failing it. The class is closed, not parked. Do not re-open it
without a document that fails the check.
