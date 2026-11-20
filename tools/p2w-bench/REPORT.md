# Fixer report - 2026-11-20 17:59

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 17:59 → running IST · 1h 32m**

> **itr-computation-with-slab-table** improved — 2.00 → 1.00. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **1** — 4 attempt(s), 1 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t12_word_invention` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 18:00 | **reverted** | 0/6 | claimed. .txt half. 6 documents still fail t13 per DEFECT-CLASSES-TXT: 22_invoice_four_columns_txtpos, 29_dot_leaders_txtpos, 74_balance_sheet_indented_subitems, balance-sheet-two-columns-of-figures, |
| 19:24 | **kept** | 1/0 | KEPT - the class is CLOSED, not parked: 0 of 213 documents fail t13_amount_columns (was 1). itr-computation-with-slab-table was not table geometry as the previous run concluded, it was a WELDED CELL: |
| 19:27 | **reverted** | 0/12 | claimed (second attempt, same slot). t12_word_invention, 12 documents, the biggest .txt class after t13 closed. Plan: read the check, census the invented tokens per document, group by mechanism (furni |
| 19:29 | **reverted** | 0/12 | NO ENGINE CHANGE LANDED - a measured census, which is the result. t12_word_invention is NOT one construct: the twelve documents carry at least five different faults. 21 of the words on 600_reviewed_in |

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
| `t13column census-01` | which of the six t13 documents still fail at head, t | 18:01 | 18:10 | 9 min |
| `t13itr weld fix-01` | implement and measure the TxtWriter change that clea | 18:11 | 18:34 | 23 min |

## Timing

| | |
|:--|:--|
| Slot window | 17:59 → running · 1h 32m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 25 |
| Longest silence | **55.3 min** — from 18:28:39, after `report.py: building the report` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 4 need a human |
| Still a wall | The fixer run 15:55-17:12 released its slot and its report was committed at 17:24 IST; `RUN-LOG.md` has no cla |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **58 min** | `##############` |
| record - attempt, handoff, class rows | **5 min** | `#` |
| report - the report and the chain | **29 min** | `#######` |
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
