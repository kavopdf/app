# Fixer report - 2026-11-22 04:18

```
# P2W Fixer - Run Report

**22 Nov 2026 · slot 04:18 → 04:50 IST · 31 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 04:49 | **lead** | 0/None | Measured the two things the last two runs left open, on committed evidence and two independent measurements: (1) the prescribed cell guard cannot fire - no Shape is ever routed into a w:tc, guard buil |

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
| `32_sA-03` | can the emitter tell its drawing anchor is inside a  | 04:49 | 23:19 | 0 min |
| `32_sB-02` | is the 54-document carrier regression cell nesting o | 04:49 | 23:19 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 04:18 → 04:50 · 31 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **29.6 min** — from 04:18:54, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **29 min** | `#####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Apply tools/p2w-bench/patches/rule-carrier-horizontal-only-2008.patch, build, run the corpus pass and take the exact LO regressions. The 16 documents already measured in Google under this patch are in benchmarks/gverify-carrier-2008/: 13 reach 42/42, 3 reach 41/42, none regress, all 16 clear 05_chars_extra. regress.py already exempts a LibreOffice regression when Google improved on the same document - it needs benchmarks/gverify/<doc>.json in the working tree. So run gverify --plan 60 over the regressed documents that have no carrier result, and land the patch with those results in the same push. Do NOT build the cell guard the last report asked for: no Shape is ever routed into a w:tc (max tc-depth 0 across 156 carriers in 22 docs) and the guard built byte-identical output on five PDFs.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
