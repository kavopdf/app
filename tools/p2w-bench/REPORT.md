# Fixer report - 2026-11-20 06:53

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 06:53 → running IST · 1h 06m**

> **table-inside-two-column-page** improved — 38.11 → 35.87. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **1** — 2 attempt(s), 1 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **32** of 213 — the rest are still off |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-partly-lost-and-displaced` |
| Committed | **16** files in 1 commit(s) from `8ae59eb` — ...-lost-and-displaced-nested-anchor-082000-f1x.md, ...ested-table-clears-cell-anchor-082000-f1x.patch, ATTEMPTS.json, CLASS-HISTORY.jsonl, DocxWriter.java, ENGINE-STAMP.json, HANDOFF.json, HANDOFF.md, HISTORY-TXT.jsonl, |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 07:13 | **partial** | 1/6 | attempt 14: a nested table inside a layout cell no longer leaves the cell's afterTablePt pointing at the layout row's top - it is cleared so the first paragraph after the nested table is placed from f |
| 07:59 | **kept** | 1/6 | ratchet stamp for attempt 14 (the nested-table cell anchor): 212 of 213 documents re-measured on the new engine (416_many_tiny_pages EXEMPT, carried at its previous value), 1 better, 211 same, 0 worse |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **167** (78.4%) |
| Failing at least one check | **46** |
| Most common failure | `t13_amount_columns` - 18 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `contB-07` | why two corpus documents lose ~60% of their ink at 5 | 07:59 | 02:29 | 0 min |
| `contA-07` | is the justified-line spacing fix missing from the e | 07:59 | 02:29 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 06:53 → running · 1h 06m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 23 |
| Longest silence | **45.5 min** — from 07:13:33, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **5 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **59 min** | `####################` |
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

content-partly-lost-and-displaced: itr-computation-with-slab-table (share5 42.33, share@10 27.40, share@20 7.85) - table rows are written at their own w:trHeight of 351/370 tw against the page's uniform 368 tw, so the page compresses by 0.5pt a row and -14.31pt by the last row (DocxWriter.java:6182 and :6271-6273; the arithmetic that yields 351 is NOT verified). The other four OPEN documents in this class are 31_times_body_arial_headings 1.04, 370_offer_letter 2.70, 14_stamp_chars_positioned_td 3.89, 75_merged_header_cell_three_columns 7.62. The rule class stays blocked pending a human.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
