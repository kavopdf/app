
  written to tools/p2w-bench/REPORT.md - commit it, so the report survives the run
# P2W Fixer - Run Report

**19 Nov 2026 · slot 01:52 → running IST · 1h 49m**

> **64_newspaper_uneven_columns_ad_boxes** improved — 9.11 → 3.46. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **1** — 2 attempt(s), 2 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.44%** — mean 6.15 → 3.72 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **32** of 213 — the rest are still off |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` |
| Committed | **20** files in 2 commit(s) from `97e2e1f` — ...esent-partly-displaced-newspaper-033000-a7d1.md, ...tent-present-partly-displaced-newspaper-033000-a7d1.md, ARCHIVE.json, ATTEMPTS.json, CLASS-HISTORY.jsonl, DEFECT-CLASSES.md, ENGINE-STAMP.json, HANDOFF.json, HANDOFF |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 02:25 | **kept** | 1/23 | recutColumnBands: the column row's top edge is the MINIMUM over the columns, not the first non-empty one. 64_newspaper_uneven_columns_ad_boxes share5 9.11 -> 3.46, max_pt 11.04 -> 6.72, text_recall 10 |
| 03:40 | **kept** | 1/23 | recutColumnBands: the column row's top edge is the MINIMUM over the columns, not the first non-empty one (the 'break' at PdfToWord:8666). 64_newspaper_uneven_columns_ad_boxes share5 9.11 -> 3.46, max_ |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **167** (78.4%) |
| Failing at least one check | **46** |
| Most common failure | `t13_amount_columns` - 18 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 01:52 → running · 1h 49m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 18 |
| Longest silence | **75.2 min** — from 02:25:21, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 1 need a human |
| Still a wall | The count is inflated by a timezone mismatch. `_attempts_recent()` parses `at` with `time.mktime(time.strptime |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **4 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **1h 43m** | `#####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
