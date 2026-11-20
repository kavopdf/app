# Fixer report - 2026-11-20 15:55

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 15:55 → running IST · 1h 15m**

> **22_invoice_four_columns_txtpos** improved — 1.00 → 0.00. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **5** — 3 attempt(s), 1 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t13_amount_columns` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 16:14 | **reverted** | 0/26 | IN PROGRESS - claiming the class: per-Table endCol is not per-page; the six remaining t13 docs differ only by which Table set the column. Will be corrected in place with the real measurement. |
| 17:06 | **kept** | 5/6 | TxtWriter: hoist the table amount end column from per-Table to one set per page column of the cell's right edge, pooled over every table in the document and marked in paraEndSnap so paragraph and tabl |
| 17:08 | **reverted** | 0/1 | itr-computation-with-slab-table is not a padding fault. Its failing source amount column (7 rows, end column 130) arrives as 1 row at 130 and 6 at 132, because 61,000.00 is in a different Table whose |

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
| `t13_A-02` | per-document map of every offending t13 line: source | 17:09 | 11:39 | 0 min |
| `t13_B-02` | reach of a per-page end column across the whole .txt | 17:09 | 11:39 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 15:55 → running · 1h 15m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 25 |
| Longest silence | **51.9 min** — from 16:14:08, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **1h 13m** | `#####################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
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

47_margins: re-measure the class against a fresh render, not the tables - 392_statistical_console_output already reads 0.06 and passes all 42 checks on this engine while RANKING.csv says 1.61 and both gverify tables say 47_margins FAIL, so the class is at most 25 documents. Then pull the thread FINDINGS/47_margins-REACH-140500.md leaves open: 360_restaurant_menu's body column was 12 pt left (source 52, render 40) and 9 runs are still 11.9 pt out; the leading-space indent and the centred-line constructs are both capped under the 25% bar and must not be retried.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
