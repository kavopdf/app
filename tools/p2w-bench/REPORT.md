# Fixer report - 2026-11-21 21:53

```
# P2W Fixer - Run Report

**21 Nov 2026 · slot 21:53 → running IST · 1h 00m**

> **041122-Account_Opening_Form** improved — 4.00 → 3.00. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **9** — 1 attempt(s), 1 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t08_line_order` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 22:38 | **kept** | 9/10 | t08 ground truth was PyMuPDF paint order, not reading order: sort each page's upright lines by (round(y,1),x) in the t08 block only. All 213 .txt rescored with the same engine: clean 190->197, t08 fai |

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
| `t08_A-01` | does t08 measure line order or drawing order, decide | 22:39 | - | - |
| `32_sA-02` | a census of every rule in the failing documents by p | 22:39 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 21:53 → running · 1h 00m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 16 |
| Longest silence | **24.3 min** — from 21:53:34, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 5 |
| Obstacles | 1 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **13 min** | `#####` |
| measure or build - a conversion, screen or compile writes no beacon | **30 min** | `###########` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **14 min** | `#####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Judge the t08 verifier question before touching the engine: is t08_line_order measuring line order or drawing order? FINDINGS/t08_line_order-DRAWING-ORDER-1740.md has the numbers (10 of 10 rows clear when only our own line sequence is put into drawing order). The agent's proposed one-line sort of _src_pages is NOT obviously right - it would compare sorted-vs-sorted. Decide with a falsification: construct a .txt whose lines are deliberately swapped in y and confirm t08 still fires after the change. Then take t01_word_accuracy's .docx half or 32_stroke_lines' cell-border construct.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
