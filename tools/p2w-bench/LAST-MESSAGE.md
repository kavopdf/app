# P2W Fixer - Run Report

**28 Nov 2026 · slot 14:57 → running IST**

> The instrument was charging documents for a bucket boundary, not for a defect. It now files each
> render line under its own source line, and three of the five documents I measured through Google
> moved: `gst-invoice-3line-items` 45/47 → 46/47, `purchase-order` 45/47 → 46/47,
> `delivery-challan` 42/47 → 43/47. Check `60_text_column_right_edge` passes on all three now.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - run window: RUN.json says this run began at 14:57 vs TIMELINE.jsonl records the claim at 13:53, so the window was reset and the duration is short |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **48** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `60_text_column_right_edge` - taken from the pending list (63 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `60_text_column_right_edge` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 14:31 | **lead** | 0 | A subagent measured the table geometry of the three documents the last run flagged. `w:tblGrid`/`w:tcW` against the source's rule positions: worst single column 1.0 pt, table totals within 0.24 pt. The .docx is not 2.4x wide anywhere; check 60 never opens the .docx. |
| 14:41 | **lead** | 0 | A second subagent tested the two "0.00" documents. They are not regressions: 0.00 is `share@5px` from `p2w.py:773`, where lower is better, and SSIM on the same pair is 99.88 and 98.98. Both convert, 1 page, no exception. |
| 15:02 | **lead** | 0 | Google round trip on 5 documents (upload → s3key → CREATE_FILE → export → compare). Reproduced the charge to the digit: `gst-invoice-3line-items` +161.18 pt, `purchase-order` +103.36, `delivery-challan` +77.21, all OVER, all in the instrument. |
| 15:18 | **kept** | 3 | The instrument fix, measured through Google on the same 5 documents before and after. 3 documents moved, 2 unchanged, 0 worse. Falsified twice. |

## Why the charge was not the document

Check 60 built "columns" on each page separately: `columns()` groups body lines by left edge with
`b[0] - seed <= 10`. The source and the render are bucketed **independently**, so a line that moves one
point across that boundary changes column on one side only, and the check then compares one column's
widest line against a different column's.

Measured on `gst-invoice-3line-items`, engine `a05b20eb05fe0fc8`, Google export of 28 Nov: the company
masthead sits at x0 = 73.69 in the source and 73.50 in the render; the item table's Description column
starts at 62.92 and 63.75. In the source 73.69 − 62.92 = 10.77 > 10, so the masthead is its own column.
In the render 73.50 − 63.75 = 9.75 ≤ 10, so it joins Description. Description's widest line then read
174.79 against 335.97 and the check charged **+161.18 pt**, where the widest line had moved **+2.47 pt**
and the page inset +0.75 pt. Every other column on that page was inside 9.3 pt.

The same boundary did the same to the other two: their charges were one cluster absorbing a line that
belongs to another.

## What changed

`tools/p2w-bench/verify_google.py`, check 60 only. `page_lines()` now delegates to `page_lines_t()`,
which returns each run with its text. A render line is filed under the column of the **source line it
is the same line as**, matched on text with the engine's zero-width characters removed and within one
bucket of its left edge. A line whose text matches nothing falls back to the source line it starts
over; a line whose own source line is in no column cannot evidence any column's edge and is left out.
The estimator (widest line), the slack (one measured word) and the page-level `far` net are untouched.

Two things the first version got wrong, both caught by measuring rather than by reading:

- Filing an unmatched line by the **render's** nearest column re-created the original bug: the masthead
  still landed in Description. It now files by the source.
- The word `Total` is a row label at 62.92 and a column head at 536.83 in the same document. A bare text
  match handed the row's 551.28 pt figure to the label's column and charged +376.49 pt. A pair more than
  one bucket apart is not a pair.

## Measured before and after, through Google

| Document | Before | After | Check 60 |
|:--|--:|--:|:--|
| `gst-invoice-3line-items` | 45/47 | 46/47 | fails → **passes** |
| `purchase-order` | 45/47 | 46/47 | fails → **passes** |
| `delivery-challan` | 42/47 | 43/47 | fails → **passes** |
| `28_value_overflows_cell_txtpos` | 39/42 | 39/42 | passed → passes (unchanged) |
| `25_signature_block_underscores_txtpos` | 38/42 | 38/42 | fails → **still fails** |

The last two rows are the reason to believe the first three. `28_value_overflows_cell_txtpos` already
passed 60 and still does - the fix does not fire on a document that had nothing wrong.
`25_signature_block_underscores_txtpos` still fails 60 after the fix: a real overrun is still caught.

**Falsified, not assumed:** the source PDF compared against itself passes 60 (41/42, the one failure
`10_font_sizes`, unrelated). A 44-character run injected at the Description column's left edge into a
copy of the Google export still **fails** 60 - an unpaired line is still charged.

The other checks did not move on any of the five: the only check whose code changed is 60.

## Limits, stated

- Five documents were measured through Google, not 213. The other 56 documents failing 60 were not
  re-measured this run, so the corpus-wide effect of the fix is unmeasured and the Progress table above
  is unchanged from the last run.
- The `0.00` entries in the regression list are not regressions (subagent finding above); the
  `Regressions 82` row is report.py's own count and was not re-derived here.

## The txt

| | |
|:--|:--|
| Measured | **1.2 h ago** |
| Scored | **214** of 214 |
| Clean - every applicable check passes | **209** (97.7%) |
| Failing at least one check | **5** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

Two, both deployed in the first ten minutes and both returning measured numbers, not greps.

1. **Column geometry.** Converted the three flagged documents with the engine and printed, per column,
   the source's rule x-positions against the produced `w:gridCol`/`w:tcW` in points: worst column 1.0 pt,
   totals within 0.24 pt. It also named the code path (`DocxWriter.table()` at
   `DocxWriter.java:6019-6031`, fed by `PdfToWord.java:7962`) and showed the 2.4x exists only in
   `verify_google.py:2736`, the bucketing, which never reads the .docx. That is what told me to look at
   the instrument rather than the converter.
2. **The two zero scores.** Showed `415_inline_images` and `411_nested_xobject_transforms` both convert
   (1 page, no exception, ink 34,954 vs 35,045 px and 5,574 vs 6,119 px), that 0.00 is the *best* value
   of `share@5px` and not SSIM (99.88 and 98.98 on the same pair), and that no commit in the last 40
   touches image or XObject code. It stopped the run chasing a phantom regression.

Neither agent could reach Drive: a subagent's sandbox has no `upload` path, so the s3key route is
closed to them and they would need `UPLOAD_FROM_URL`.

## Timing

| | |
|:--|:--|
| Slot window | 14:57 → running · 1 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 6 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| report - the report and the chain | **0 min** | `######################` |
## Best results this round

## Next run

The instrument is fixed and pushed but the corpus has not been re-scored with it. **The next run should
re-measure the 56 documents failing `60_text_column_right_edge` through Google with this tree** - that
is the number that decides how much of the class was the instrument. If it is the same boundary
mechanism as these three, most of the 56 should clear 60 and only the genuinely over-wide ones should
stay. `edgeprobe.py` prints the per-column numbers this check now compares; run it on the first failing
document to see which of the two shapes it is before changing anything in the engine.

`18_displacement` is still on `gst-invoice-3line-items` and `delivery-challan` and is the next check
standing between those two and clean.
