# Fixer report - 2026-11-21 23:19

```
# P2W Fixer - Run Report

**21 Nov 2026 · slot 23:19 → running IST · 30 min**

> **11 document(s)** improved this run, but the run did not commit benchmarks/RANKING.csv, so the report cannot name them.

## Progress

| | |
|:--|:--|
| Documents improved this run | **11** — 1 attempt(s), 1 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `05_chars_extra` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 23:37 | **kept** | 11/192 | 05_chars_extra counted one U+200B per w:tab - Google's export marks every tab advance with a zero-width space. Full-corpus separation 141/141 vs 51/51, causal on 17 (23 tabs -> 23 extras, 0 tabs -> 0) |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 23:19 → running · 30 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 15 |
| Longest silence | **10.5 min** — from 23:39:23, after `report.py: building the report` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | round.py --claim-fixer sets ROUND.json fixer_started but never starts RUN.json, so a slot that claims after an |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **10 min** | `########` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **11 min** | `#########` |
| other - not attributed to a tool | **7 min** | `#####` |
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
