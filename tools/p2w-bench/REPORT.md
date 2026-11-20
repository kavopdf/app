# Fixer report - 2026-11-20 10:51

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 10:51 → running IST · 1h 10m**

> **bank-statement-horizontal-rules-only** improved — 1.00 → 0.00. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **12** — 3 attempt(s), 2 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7** of 192 measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t13_amount_columns` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 10:52 | **error** | None/None | claimed. .txt half. PATCH-t13 (row-per-line) was rejected 19 Nov: it breaks t04_structure line-count drift, 101 worse 0 better. Working the other direction: keep one cell per line, fix only where an a |
| 11:51 | **kept** | 10/18 | KEPT. One end column per TABLE column in TxtWriter.appendTable, instead of one per cell. The old aim at each cell's own right edge was thrown away by 'if (startCol > col)' because the 0.6em ruler over |
| 11:59 | **kept** | 2/18 | KEPT (second construct, same slot). paraEndSnap(): per page, an end column whose immediate neighbour is also an end column of the page's numeric paragraph lines merges into it transitively and keeps t |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **179** (84.0%) |
| Failing at least one check | **34** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 12 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t13_A-01` | which writer path emits the misaligned amounts, prov | 12:00 | - | - |
| `t13_B-01` | census of the 18 documents: table path vs paragraph  | 12:00 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 10:51 → running · 1h 10m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **58.6 min** — from 10:52:49, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **1h 07m** | `#####################` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

18_displacement: the page-top gap is PROVEN to be the cause (Google drops w:before there; a trHeight-exact 1x1 table row is honoured to 0.97 pt). Applying it by hand to bank-statement-5-pages fixes the displacement itself (dy median -53.8 -> +0.8) but the document goes 6 pages -> 10 with a blank after each, because (a) the break paragraph already emits a blank page 1 in Google and (b) the 55 pt gap is not charged to the page fill budget. So it is NOT a construct swap: make the gap real AND charge it to the page capacity, and fix the blank page. Engine work, needs a full corpus ratchet. See FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md, second section.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
