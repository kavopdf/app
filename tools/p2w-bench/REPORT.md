# Fixer report - 2026-11-20 20:01

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 20:01 → running IST · 44 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `47_margins` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 20:28 | **reverted** | 0/14 | claimed. 47_margins (.docx, 14 in LO / 26 in Google). MECHANISM FOUND for the one document with a real 12 pt column error: 360_restaurant_menu's menu body is a TABLE, not a flow block (writer=table tw |
| 20:44 | **reverted** | 0/14 | SECOND ATTEMPT, different construct: WIDEN THE CELL OVER ITS LEADER-DOT COLUMN instead of selling its indent. DocxWriter tableBody's widening loop could only take room from EMPTY neighbours; a menu/in |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **182** (85.4%) |
| Failing at least one check | **31** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 12 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `47maanchor trace-01` | which writer construct puts 360_restaurant_menu's bo | 20:45 | 15:15 | 0 min |
| `47maclass census-01` | which clause of 47_margins each document fails, grou | 20:45 | 15:15 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 20:01 → running · 44 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 19 |
| Longest silence | **26.4 min** — from 20:02:06, after `archive.py: housekeeping` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **42 min** | `#####################` |
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

47_margins: re-measure the class against a fresh render, not the tables - 392_statistical_console_output already reads 0.06 and passes all 42 checks on this engine while RANKING.csv says 1.61 and both gverify tables say 47_margins FAIL, so the class is at most 25 documents. Then pull the thread FINDINGS/47_margins-REACH-140500.md leaves open: 360_restaurant_menu's body column was 12 pt left (source 52, render 40) and 9 runs are still 11.9 pt out; the leading-space indent and the centred-line constructs are both capped under the 25% bar and must not be retried.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
