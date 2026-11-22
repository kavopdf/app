# Fixer report - 2026-11-22 13:18

```
# P2W Fixer - Run Report

**22 Nov 2026 · slot 13:18 → running IST · 12 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 13:29 | **lead** | 0/1 | Declared-to-laid row-pitch law measured on a real-shaped ruled row in Google, 3 round trips: declared 360/380 atLeast lays 19.1 pt, declared 368 (the source 18.40) with hRule=exact lays 19.5 and REGRE |

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
| Slot window | 13:18 → running · 12 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 10 |
| Longest silence | **4.7 min** — from 13:18:54, after `gaps.py: reading the timeline` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **4 min** | `########` |
| fix - diagnose and change the engine | **4 min** | `########` |
| record - attempt, handoff, class rows | **0 min** | `##` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **1 min** | `##` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

DO NOT build the 0.9634 row scale or the hairline cell box for single-line cells - both measured inert. Build against rowParts>1: raise the row floor to the true 368 twips (the floor is quantised 8 twips low at 360) OR take w:before off the continuation paragraphs inside a wrapped cell. Google grows 360-twip rows to 19.0/20.0; source pitch is 18.40; mobile-bill rows 5-12 hold 6 w:p on 3 columns and render at 20.0 = 2.0 pt of growth. Prove on mobile-bill and insurance-policy-schedule FIRST - they are the only two documents blocking a spacer construct already measured to take 6 documents clean (68_journal 42/42 this run). Then land the spacer (w:before + hairline w:line=1 at 5868-5875, cap 2880->4320 at 5852,5866) with it.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
