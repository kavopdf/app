# P2W Fixer - Run Report

**24 Nov 2026 · slot 07:00 → running IST · 13 min**

> **`25_invisible_text` was a check that read the paper.** A Google PDF export opens with a page-sized
> white rectangle and rasterises our bands into images, so white type on an orange band counted as
> invisible text. 48 documents failed it and LibreOffice passed all 48. Fixed, measured live in Google:
> **5 of the 5 documents that failed nothing else are now 42/42**, corpus **29 -> 34** clean.

## Progress

| | |
|:--|:--|
| Document-moves this run | **7** — 2 attempt(s), 2 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **34** of the **186** re-measured on this engine - **4** of the 190 scored are still on an older engine, and **34** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `25_invisible_text` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 07:11 | **kept** | 2/5 | check read the page-white sheet instead of the band behind the run; 2 of the 5 single-check documents re-measured 42/42 in Google, at-risk document unchanged at 40/42 |
| 07:12 | **kept** | 5/5 | all five single-check documents re-measured 42/42 in Google on this engine after the check fix |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 07:00 → running · 13 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 14 |
| Longest silence | **5.6 min** — from 07:05:54, after `building the engine (build-engine.sh)` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **5 min** | `#########` |
| measure or build - a conversion, screen or compile writes no beacon | **5 min** | `#########` |
| record - attempt, handoff, class rows | **2 min** | `####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

NEXT RUN: (1) THE PREVIOUS PAIR IS REFUTED - do not spend a slot on it. content+rule==pitch and hRule=atLeast make a trHeight-only change a no-op, and a cell-level gap escapes fitPage/shaveToFit (FINDINGS/18_displacement-STEP-IS-THE-UNSPENDABLE-SPACER-0323.md). (2) The class is two disjoint halves: a spacer half (the step at each table top = 0.784 x the declared w:line of an unspendable spacer, confirmed on 4 of 4 documents) and a row half (+0.75 pt per row, 21.75 pt over 362_price_list_dense's 29 rows). (3) FIRST MOVE: one Google round trip on 362_price_list_dense with trHeight = max(content, line-15) on rows where line > content only - LO-invariant by construction, and it tells you whether Google lays trHeight+rule or max(trHeight, content+rule). (4) The 4 ratchet rows need one corpus pass (~40 min) - start the slot with it, do not end with it. (5) The 9 REOPEN rows in PENDING-AUDIT.md are decisions with evidence attached.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

## Next run

**(1) THE CHECK WAS THE DEFECT, AND ONLY ON 5 OF THE 48.** The five documents that failed nothing but
`25_invisible_text` are now 42/42 in Google. The other 43 still fail it, and whether they are the same
false positive is **not measured** - the stamp case was proven by eye (band present, white on orange),
the rest were not looked at. One export each is the whole test; the band arriving as an **image** in a
Google export (15 images, 2 drawings where the source has 1 and 14) is a separate real defect that
belongs to whoever owns rasterised shapes.

**(2) `18_displacement` IS STILL 101 DOCUMENTS AND STILL THE CLASS.** Unchanged by this run, and the
two halves are now separated by measurement, not inference: A = the unspendable spacer
(`w:before="0"`, whole gap in `w:line`, Google draws `w:line` at 0.216 -> 0.784 of the gap lost at each
table top, 4 of 4 documents); B = the +0.75 pt/row ramp on documents with no unspendable spacer.
**A cannot be spent on a page that has no slack, and the slack was eaten by B** - so B is the lever for
A, and `362_price_list_dense` (29 rows, 21.75 pt, zero spacers) is the cleanest falsifier of B.

**(3) 14 documents fail nothing but `18_displacement`.** They are the largest single-check group in the
corpus and the next slot's best target. `60_text_column_right_edge` (5) and `25_invisible_text` (43, of
which 5 were this run) are the others.

**(4) The gates are clean.** `regress.py --check` PASS before and after, `measure_gate.py` READY,
`google_safe` could not check (no `.docx` output directory in this pod) - the change touches no
emitted byte, only how a PDF is read.
