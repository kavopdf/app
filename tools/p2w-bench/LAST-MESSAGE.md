# Fixer report - 2026-11-24 08:57

```
# P2W Fixer - Run Report

**24 Nov 2026 · slot 08:57 → running IST · 20 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **35** of the **186** re-measured on this engine - **4** of the 190 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 09:17 | **lead** | 1/10 | The uniform-pitch guard (0559 patch) takes 362_price_list_dense 41/42 -> 42/42 in Google, measured by gverify --collect; electricity-bill and 330_cad_drawing_sheet byte-identical in LibreOffice (guard |

## The txt

| | |
|:--|:--|
| Measured | **20 min ago** |
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
| Slot window | 08:57 → running · 20 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 17 |
| Longest silence | **5.0 min** — from 09:07:46, after `screen pass 2` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 5 parked, with the evidence to re-open them |
| Still a wall | 74_balance_sheet_indented_subitems scores 41/42 in Google on an older engine and the result was never committe |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **5 min** | `######` |
| record - attempt, handoff, class rows | **3 min** | `####` |
| other - not attributed to a tool | **11 min** | `############` |
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

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
