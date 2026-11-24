# P2W Fixer - Run Report

**24 Nov 2026 · slot 05:59 → 06:40 IST · 2 min**

> No change was kept this run. The numbers below say what was tried, and the last section says why the next run must not try it again.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 3 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **29** of the **186** re-measured on this engine - **4** of the 190 scored are still on an older engine, and **29** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 06:38 | **lead** | 0/None | Second pass: measured 11 documents of the 85 the guard fires on, baseline against patched on the LibreOffice proxy. Seven are unchanged at share@5 (16_right_aligned_amounts, 351_omr_answer_sheet, 341_ |
| 06:40 | **lead** | 0/None | Third pass: the largest table in the corpus, 324_loan_amortisation_schedule (6 tables, 41 rows each, 246 rows, 7 pages) - the document where a per-row redistribution would accumulate the most. LibreOf |

## What the run did

`18_displacement` was the class, on the strength of the 04:52 handoff: Google lays a table row out on
whole CSS pixels and truncates the fraction, so a 168-twip row renders at 11 px instead of 11.2 and
loses 0.15 pt. Carrying the remainder across rows takes the document to 42/42 in Google. That run
measured it, could not land it (17 documents worse in the proxy) and left one question: **the guard**.

**The guard is built.** `DocxWriter.java` cannot take a true pre-pass - `rowHeightTw` depends on
`recutTopPt`, a running sum of the rows above it - so the patch buffers each row's `w:trHeight` and
rewrites the digits back-to-front once every height is known. Nothing but the digits changes:
`rowHeightTw` itself is untouched, so the flow charge, the table's own bottom edge and everything
after it are bit-identical.

It emits, on the real engine, from `word/document.xml`:

| | `w:trHeight` | n | sum |
|---|---|---:|---:|
| before | `[240, 168 x 28]` | 29 | 4944 |
| after | `[240, 165, 165, 180, ... 174]` | 29 | **4944** |

That is the distribution that measured 42/42 in Google, with the total held. The 04:52 array summed
to 4950 from a source that sums to 4944; this one does not move the table's bottom edge.

**The guard question is answered with a census, not an argument.** All 211 corpus PDFs were converted
on the baseline engine and every table's `atLeast` heights read back:

| guard | rule | fires on |
|---|---|---:|
| A (in the patch) | one fractional height repeating ≥3 times | **85** |
| B (line grid) | as A, and every whole-pixel row is a header or footer | **54** |
| old, refuted | `ruleTwHere == 0` | 17 documents worse |

The literal "all rows equal" test the 04:52 run proposed **skips the target** - `362` is a 240-twip
header over 28 rows at 168. Guard B exists because `electricity-bill` alternates 360/380: one
fractional height, but two heights interleaved, so it is not a pitch.

## Why it is not committed

The LibreOffice proxy, `p2w.py`'s own instrument, each document measured twice:

| document | guard | share@5 before | after | verdict |
|---|:--:|---:|---:|---|
| `362_price_list_dense` | A, B | 0.03 | **0.04** | **worse** |
| `electricity-bill` | A only | 1.33 | **1.40** | **worse** |
| `16_right_aligned_amounts_txtpos` | A, B | 0.00 | 0.00 | unchanged |
| `351_omr_answer_sheet` | A, B | 0.00 | 0.00 | unchanged |
| `341_shipping_manifest` | A, B | 0.00 | 0.00 | unchanged |
| `390_wide_data_appendix` | A, B | 0.03 | 0.03 | unchanged |
| `320_balance_sheet_statutory` | A, B | 0.00 | 0.00 | unchanged |
| `323_credit_card_statement` | A, B | 0.00 | 0.00 | unchanged |
| `375_attendance_register` | A, B | 0.01 | 0.01 | unchanged |
| `324_loan_amortisation_schedule` (246 rows) | A, B | 0.00 | 0.00 | unchanged |
| `03_stamp_vertical_90deg` | A, B | 16.98 | **17.20** | **worse** |
| `68_journal_wide_table_spanning` | A, B | 12.09 | **12.34** | **worse** |

**Twelve documents measured: eight unchanged at share@5, four worse.** The largest table in the
corpus - 246 rows across six tables - does not move at all, so the cost does not grow with the row
count, which is what a cumulative snap is for. The four that move are the
target itself and three documents already displaced by 12-17 share points; the eight that hold are
the clean ones. The largest cost found anywhere is **+0.25 share@5**, on a document whose share@5 is
12.09. A 12-document sample is not the corpus and is not offered as one - it bounds the cost, it does
not clear it, because the bar is zero movement.

Both readings repeat exactly on a second run, so neither is noise. `regress.py` refuses any rise in
share@5, so the gate refuses this patch **on the one document the class exists for**, before any
other document is considered. `330_cad_drawing_sheet`, named as a cost in the 04:52 table, is
untouched by both guards - its `.docx` is byte-identical between the two engines.

**No guard can fix this.** The redistribution is forced: Google truncates each row to a whole pixel,
so 168 twips can never be kept, and the minimum-movement cycle is `165, 165, 165, 165, 180` - four
rows 0.15 pt short, one 0.6 pt long. LibreOffice places 168 correctly, so every one of those rows is
a loss there. The cost is the definition of the fix, not a guard defect.

The engine was reverted; the patch is kept at
`FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch` and the full measurement at
`FINDINGS/18_displacement-UNIFORM-PITCH-GUARD-MEASURED-0559-fixer.md`.

## What the next run should do

**Do not rebuild this.** Do not look for a better guard. The decision to make is about the bar: either
`18_displacement` tolerates one pixel of accumulated quantisation per page - a waiver for a measured
Google gain with a bounded proxy cost, or a share@5 floor below which a movement is not a regression -
or the class is **closed** and the slot goes to a class whose two renderers agree. Working it a third
time will produce this same finding.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

Two, both deployed before the run's own attempt, both returned inside the turn.

| agent | what it was given | what it returned |
|:--|:--|:--|
| row-height pre-pass | `DocxWriter.java` and the 04:52 finding | the buffer-and-rewrite patch that is now in FINDINGS, plus the catch that an all-equal test would skip the target document |
| row-pitch census | the mechanism and the corpus brief | **no corpus was copied into its sandbox** - it built and validated the census tool against four synthetic PDFs with known pitch (8.40 pt → 11.2 px, 4.5 pt lost over 30 rows) and reported zero documents rather than inventing numbers. The census was then run here, on the 211 real `.docx`, and is in the table above |

## Gates

Three attempts are recorded in `ATTEMPTS.json` (46, 47, 48), but the row above counts **1**: every
`round.py --heartbeat` rewrites `fixer_started`, so report.py's window kept moving and two of the
three fell outside it. That is the pending blocker of 2026-11-21 - a beat must not restart the run
window - now with a second run's evidence, and it is also why `--release-fixer` refused three times
before `--force`: the gate could not see the attempts it had itself timestamped out of range.

Not blocked. `regress.py --check` PASS on the reverted tree, `measure_gate.py` READY with 212 of 212
scored and one engine on both sides. The pipeline was healthy; the attempt is what did not land.

## Timing

| | |
|:--|:--|
| Slot window | 05:59 → 06:40 · 2 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 16 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **0 min** | `########` |
| other - not attributed to a tool | **1 min** | `##############` |
