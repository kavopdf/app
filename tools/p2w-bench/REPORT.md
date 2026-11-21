# Fixer report - 2026-11-21 23:57

```
# P2W Fixer - Run Report

**22 Nov 2026 · slot 23:57 → running IST · 14 min**

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
| 00:12 | **lead** | 0/192 | Corpus-wide: 0 of 76 documents whose rules are carried only as floating <w:drawing> pass 32 in Google; the only 2 with source rules that pass carry the rule as a table-cell border. The drawing carrier |

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
| Slot window | 23:57 → running · 14 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 10 |
| Longest silence | **10.1 min** — from 23:57:48, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2 min** | `###` |
| measure or build - a conversion, screen or compile writes no beacon | **11 min** | `##################` |
| other - not attributed to a tool | **0 min** | `#` |
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
