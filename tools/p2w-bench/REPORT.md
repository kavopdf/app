# Fixer report - 2026-11-22 13:56

```
# P2W Fixer - Run Report

**22 Nov 2026 · slot 13:56 → running IST · 49 min**

> **1 document(s)** improved this run, but the run did not commit benchmarks/RANKING.csv, so the report cannot name them.

## Progress

| | |
|:--|:--|
| Document-moves this run | **1** — 2 attempt(s), 1 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |
| Committed | **16** files in 4 commit(s) from `f3157f6` — ...isplacement-ROWHEIGHT-CODE-MAP-142000-agentA.md, ...lacement-LADDER-IS-WHOLE-POINTS-152000-fixer.md, 18-row-pitch-error-diffused.patch, 18_displacement-LADDER-IS-WHOLE-POINTS-152000-fixer.md, 18_displacement-SOLO-DOCS |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 14:19 | **lead** | 0/16 | swept 13 declarations in one Google round trip: laid row pitch is WHOLE points (18/19/20), so the 18.5 ladder the relay left is void; laid = round(declared_pt + 0.875). Error-diffused the declaration |
| 14:45 | **kept** | 1/16 | table spacer moved from w:line to w:before (was a no-op in Google, tables started ~10pt high) + row pitch diffused onto Google's measured 0.75pt grid; two-tables-stacked-with-no-gap 41/42 -> 42/42 PAS |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-06` | static map of every writer that emits w:trHeight and | 13:57 | - | - |
| `18_dB-05` | from the three measured declared->laid points comput | 13:57 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 13:56 → running · 49 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 25 |
| Longest silence | **22.3 min** — from 14:23:17, after `report.py: building the report` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **22 min** | `##########` |
| measure or build - a conversion, screen or compile writes no beacon | **20 min** | `#########` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **2 min** | `#` |
| other - not attributed to a tool | **2 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

APPLY patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch and ratchet it corpus-wide - measured clean on two-tables-stacked-with-no-gap (42/42 PASS, n_out 0) and it moves EVERY ruled table, so the gate refuses it unratcheted. The row grid is 0.75 pt, NOT whole points: nine identical rows per page read 18.00/18.75/19.50, and the law laid=0.75*(round(h/0.75)+1) reproduces the 13-declaration sweep exactly when its readings are rounded. Then close the small-spacer over-charge the patch exposes: mobile-bill's 128/124 tw spacers are now charged in full where Google previously charged ~0, leaving that page +2..+5 pt low. Evidence: FINDINGS/18_displacement-ROW-GRID-AND-SPACER-1518-relay.md

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
