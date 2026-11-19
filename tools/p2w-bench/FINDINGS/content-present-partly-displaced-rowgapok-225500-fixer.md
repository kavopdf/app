# SUPERSEDED - rowTables was gated out by a 2.4 em floor; `13518ff` fixed the same document by another route

Fixer, 19 Nov 22:59. Class `content-present-partly-displaced`.
**Read the last section first: this patch is parked, not recommended.** It moved its target document
6.89 -> 0.14 when it was measured, and by the time the run finished that document was already clean
(0.10) on `main` because a different change landed first. Nothing is committed to the engine.

## The one question

Why does `bank-statement-horizontal-rules-only` emit no table at all, when the page is a ruled
ledger with 16 rows of label-left / amount-right?

## Short answer

`rowTables` - the pass written for exactly this page - never runs its body, because one numeric gate
rejects every row pair:

    PdfToWord.java:9701   rowGapOk(rows, a, b):
                          gap <= Math.max(size * 2.4f, 16f)

The page's rows are 18.400 pt apart on 6.6 pt type, so the bound is `max(15.84, 16) = 16.0` and
`18.399963 > 16.0` holds on **every** pair. With the first pair rejected, `j - i >= 3` (line 9231)
never holds, `rowTables` returns nothing, and the page falls back to flowing text - where the row
pitch drifts +0.45 pt per split row (bounded at +5.847 pt) and the body ends 5.8 pt low.

**A ledger's row pitch is set by the page, not by the type size.** 18.4 pt rows under 6.6 pt figures
are the normal shape of a bank statement, an invoice, a BOQ, and a bound expressed in ems cannot see
that, because the em is the type's size and the pitch is the page's.

## What I measured

Screen (`tools/p2w-bench/screen.py`, baseline = the `RANKING.csv` of that moment, engine
`4147d54+7e133ec9e7` = `3abfa85` plus this patch):

| document | share5 before | after | moved |
|:--|--:|--:|--:|
| bank-statement-horizontal-rules-only | 6.89 | **0.14** | **-6.75** |
| 75_merged_header_cell_three_columns | 27.31 | 27.31 | 0.00 |
| 27_two_column_left_short_txtpos | 1.62 | 1.62 | 0.00 |
| 315_gazette_notification | 1.96 | 1.96 | 0.00 |
| 330_cad_drawing_sheet | 4.91 | 4.91 | 0.00 |
| 374_org_chart | 5.92 | 5.92 | 0.00 |
| 304_package_insert_small_print | 2.47 | 2.47 | 0.00 |

Seven documents measured: 1 better, 6 unchanged, 0 worse, text_recall 100.0 throughout.

An independent agent reached the same number from the other end (`FINDINGS/...bankpitch-164453-4aa4.md`):
it found that 12 of the 16 rows arrive as two paragraphs, and that the second paragraph is written
`before=0 line=9` while `before` is solved from `ctx.lastBaseline` and never from `ctx.flowY`, so
0.4554 pt is added per split row and never reclaimed: `(4x368 + 12x377)/16 = 18.7375 pt`.

## The change, and why it is a condition rather than a bigger number

Raising `16f` to `24f` works on this page and is a threshold. The condition that separates a table
from a page's furniture is that **a table's rows follow one another at one pitch, and that pitch is
the run's own**:

    if (gap <= Math.max(size * 2.4f, 16f)) return true;      // unchanged fast path
    if (gap > Math.max(size * 3.0f, 20f)) return false;      // absolute ceiling
    if (a <= from) return true;                              // the opening pair sets the pitch
    float pitch = rows.get(a).get(0).y - rows.get(a - 1).get(0).y;
    return Math.abs(gap - pitch) <= Math.max(1.5f, pitch * 0.2f);

Spread-out boxes also line up in a grid, but not at one constant pitch, which is what the tail of
the function rejects. It is `patches/rowgapok-run-pitch.patch`, 40 lines, `PdfToWord.java` only, and
it still applies cleanly to the engine at `a1a70b3`.

## What was ruled out, with the numbers

1. **The ruled pass / `recutColumnBands`.** The page draws 39 horizontal strokes and 0 vertical
   rules, so `ncol < 2` at 7805 and the cell path cannot build anything. Not the fault.
2. **`trHeight` / row height.** The .docx contains 0 `<w:tbl>` and 0 `<w:tr>`; there is no table to
   have a height. The drift is a consequence of the fallback, not its cause.
3. **The em bound being "slightly too small".** `rowGapOk` is asked of every pair, so one rejection
   kills the whole run, not one row - it is not a matter of degree.
4. **`shortCells` / `alignedStart` / `wordsSurvive` blocking it.** Not reached; the run never gets
   past `rowGapOk`.
5. **This mechanism explaining `75_merged_header_cell_three_columns`.** It does not: that document is
   byte-for-byte unchanged by this patch. Its defect is that `spanR` is computed at
   `PdfToWord:7950` and read by nothing, so no `w:vMerge` is ever written, and a glyph's row is
   taken from the cell's top edge at `7846`.

## Why this is parked, not applied

The engine moved while this run was measuring. Commit `13518ff` - *"a row split into two paragraphs
no longer drags the page down with it"* - landed the other end of this defect, and
`bank-statement-horizontal-rules-only` is now **clean at share5 0.10 on `main`** (`RANKING.csv`
row 112) without a table being built at all. The drift was the user-visible defect; the missing
table was the cause, and the landed fix treats the symptom well enough that the document scores
0.10.

So this patch would now replace a working flow path with a table path on a document that is already
clean, and it has never been measured on the current engine or across the corpus. **Do not apply it
on the strength of the table above** - that table belongs to the previous engine. If a later run
wants the table (a real table is better than 16 absolute-positioned paragraphs for a reader who
edits the .docx), it must re-screen from zero and expect the bank statement to get *worse* before it
gets better.

The corpus pass was also not affordable here: conversion ran at **4.2 s per document** (49 of 213 in
205 s), and the brief is explicit that a pass must not be started that cannot be finished. The
engine was reverted to `3abfa85`; `main` has since moved on to `a1a70b3`.

## What would prove the mechanism wrong

* If `rowGapOk` returned true at gap 18.4 with size 6.6 on the unpatched engine, the gate would not
  be the cause. Instrumented: `rowGapOk=false gap=18.399963 size=6.5999994`.
* If the patched build still emitted 0 `<w:tbl>` for the bank statement, the mechanism would be
  elsewhere. It emitted one table, `trHeight 368` = 18.400 pt, pitch 18.400 on every interval.
