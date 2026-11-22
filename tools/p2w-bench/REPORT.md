# Fixer report - 2026-11-22 23:54

```
# P2W Fixer - Run Report

**23 Nov 2026 · slot 23:54 → running IST · 18 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 00:11 | **lead** | 0/3 | Row-height dither refuted (trHeight stored not laid); census of the 11 non-ruled docs = 3 faults; spacer needs a scope guard, handed to next run |

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
| Slot window | 23:54 → running · 18 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **9.4 min** — from 23:54:49, after `reading state: handoff, leverage, pending` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **16 min** | `#####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

DO NOT apply patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch - measured LO-regressive by 21.5 points on two-tables-stacked-with-no-gap (FINDINGS/18_displacement-RELAY-PATCH-REGRESSES-LIBREOFFICE-1930-f1x.md). Start from FINDINGS/18_displacement-RULES-AS-PBDR-PITCH-FIXED-PLACEMENT-BROKEN-2330-fixer.md: the Google row-pitch charge is the row's OWN RULE and a paragraph border is not charged (Google mean 18.25-18.33 vs 19.08 with cell borders, source 18.40; LibreOffice identical to 0.05 pt). The bottom-border build fixes the pitch and breaks text placement (median dy -4.66 -> -10.70, n_out 55 -> 69). Next round trip: pBdr TOP per row AND nil the table's own top side (the C build drew 18 rules vs 15 because the table top was still drawn), then re-run the A/B on two-tables-stacked-with-no-gap. Census first: only five of the sixteen documents that fail 18_displacement and nothing else are ruled tables with a sub-point pitch - the other eleven are a different term.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
