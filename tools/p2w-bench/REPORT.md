# Fixer report - 2026-11-22 13:56

```
# P2W Fixer - Run Report

**22 Nov 2026 · slot 13:56 → running IST · 26 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |
| Committed | **16** files in 3 commit(s) from `e0d4d90` — ...isplacement-ROWHEIGHT-CODE-MAP-142000-agentA.md, ...lacement-LADDER-IS-WHOLE-POINTS-152000-fixer.md, 18-row-pitch-error-diffused.patch, 18_displacement-LADDER-IS-WHOLE-POINTS-152000-fixer.md, 18_displacement-SOLO-DOCS |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 14:19 | **lead** | 0/16 | swept 13 declarations in one Google round trip: laid row pitch is WHOLE points (18/19/20), so the 18.5 ladder the relay left is void; laid = round(declared_pt + 0.875). Error-diffused the declaration |

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
| Slot window | 13:56 → running · 26 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 20 |
| Longest silence | **6.7 min** — from 13:57:47, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **20 min** | `#################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **2 min** | `##` |
| other - not attributed to a tool | **2 min** | `##` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

18_displacement: the pitch ladder is whole points and error-diffusion removes 92% of the drift (patch in patches/). The one remaining run out of tolerance is on the row the diffusion targets at 20 pt, which lays 21.0 - cap that row's cell content to its declaration and re-measure two-tables-stacked-with-no-gap.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
