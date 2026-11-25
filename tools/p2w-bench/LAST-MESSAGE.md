# Fixer report - 2026-11-25 20:56

```
# P2W Fixer - Run Report

**25 Nov 2026 · slot 20:56 → running IST · 1h 07m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8702** of 9320 (93.4%) on 213 documents |
| Check-instances still failing | **618** |
| Kept attempts vs documents clean | **15** classes with a kept attempt, **42** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1 |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (16 still open), not a new class |
| Findings vs landing | **71** finding(s) on this class and **0** documents moved - writing is cheaper than landing, and nothing else says so |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 22:01 | **lead** | 0/None | cell carry-on guard clears t12 on 2 txt documents but costs 2-3 real characters on itr-computation-with-slab-table and mutual-fund-statement; reverted, see FINDINGS/25NOV-CELL-CARRY-GUARD-t12-vs-conte |

## The measurement, and what it killed

`t12_word_invention` fails 3 documents. Two are the same form, and the surplus is one `Y`: the
carry-on rule at `PdfToWord.java:7904-7908` pulls a glyph into the previous cell within
`max(9 pt, 1.1 x size)` of the previous glyph **without checking the glyph still belongs to the
table**. On `041122-Account_Opening_Form` the phrase `(Authorised signatory)` starts at x=153.46 and
the table's right edge is x=145.0, so it welds onto the last cell as `(Authorised signatory)Y`.

**The change.** One clause on that condition: the glyph must still start inside the cell it is carried
into. A second variant narrowed it to the table's right edge instead of the cell's.

**Scope, from bytes and not from a guess.** `corpus-changed.py --record` / `--list` after converting
all 213 with the patched engine: **4 documents' `.docx` bytes moved** — the two forms,
`itr-computation-with-slab-table` and `mutual-fund-statement`. The other 209 are byte-identical, so
their scores cannot have moved.

**txt — it worked.** `txt_rank.py --all`, 213 scored against the committed table: t12 failures
**3 -> 1**, documents better **2**, documents worse **0**. Both forms went `t06 t09 t12` -> `t06 t09`.

**docx — it did not survive.** `measure_doc` on the four changed documents against their committed
`RANKING.csv` rows:

| document | share@5px | chars_missing | order_share |
|:--|:--|:--|:--|
| `041122-Account_Opening_Form` | 98.65 -> 98.65 | 127 -> 127 | 79.11 -> 79.11 |
| `Account_Opening_Form_Fillable_filled` | 97.62 -> 97.62 | 131 -> 131 | 78.94 -> 78.94 |
| `itr-computation-with-slab-table` | **42.33 -> 43.01** | **0 -> 2** | 95.50 -> 95.50 |
| `mutual-fund-statement` | 0.21 -> 0.21 | **0 -> 3** | **99.49 -> 99.36** |

The two forms are visually untouched - the invented `Y` was never printed by the source, so removing
it moves no ink. The other two lose 2 and 3 real characters from a baseline of `chars_missing = 0`.
**That is a document getting worse, so the change does not land.** Reverted; `git diff app/` is empty.

**Why the narrowing did not save it.** Restricting the guard to the *table's* right edge instead of the
cell's measured **identical numbers on the same four documents** - the characters lost on `itr` and
`mutual-fund` are also carried from beyond the table edge. The carry-out-of-table behaviour is
load-bearing for those two and is not separable from the t12 fix by geometry alone. The next
discriminator is the glyph's own line, not its position: print the glyph that changes cell with its
`(x, y, size, text)` and the text already in the destination cell, for all four documents.

**`600_reviewed_invoice_with_annotations` is not fixed by this and must not be yet.** Its 83 invented
characters are the annotation `/Contents` hoist at `PdfToWord.java:956-961`; filtering `annotationRuns`
through the dead `annotationContentsOf` (`:2475`, no call site) clears them, and that was measured.
It was **rejected here** because the comment at `:2352-2356` records that `50_annotation_text` - a
Google check - asks for that `/Contents` string exactly, and suppressing the hoist deletes the only
copy of `Approved`. The txt check and the Google check disagree about the same string. That is a
conflict to measure in Google, not a patch to land.

**Nothing was committed to `app/`.** Full detail, both patches verbatim, and the next probe in
`FINDINGS/25NOV-CELL-CARRY-GUARD-t12-vs-content-2005.md`.## The txt

| | |
|:--|:--|
| Measured | **1 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **204** (95.8%) |
| Failing at least one check | **9** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

Two, both on the engine code and both before the first attempt.

- One produced the patch specification for this change: the exact `<w:trHeight>` emitters
  (`DocxWriter.java:2280-2282`, `:6582-6585`) and the finding that **`w:lineRule` is already `exact`
  at all 14 sites** - so the 18_displacement row-snap hypothesis from the last run has no `atLeast`
  to raise on the line axis either, and the only arm that can move a row is a cell `w:line` at 285
  twips (19 x 15), not the literal 15. That is the next run's probe and it is now a number, not a guess.
- One root-caused the three `t12` documents: the check is a character multiset difference
  (`verify_txt.py:1441-1452`), the forms are the carry-on weld above, and the invoice is the
  annotation hoist. It built and measured both patches on the affected documents, which is why this
  run measured four documents instead of guessing at 213.


## Timing

| | |
|:--|:--|
| Slot window | 20:56 → running · 1h 07m |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 28 |
| Longest silence | **27.3 min** — from 21:01:38, after `warm pod confirmed, installing gate` |
| Silences over 2 min | 10 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **0 min** | `#` |
| fix - diagnose and change the engine | **3 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **32 min** | `###########` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **28 min** | `#########` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 9 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. classpick --leverage picks the class; six checks can make a document clean (18_displacement 25, 60_text_column_right_edge 6, 47_margins 3, 59_shape_anchor 3, 32_stroke_lines 2, 17_matched_runs 1) and they are weighted 3x over the 34 that cannot. Read pending.py first, then take the class it gives.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
