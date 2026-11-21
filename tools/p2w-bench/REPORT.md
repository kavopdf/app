# Fixer report - 2026-11-21 07:14

```
# P2W Fixer - Run Report

**21 Nov 2026 · slot 07:14 → running IST · 1 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `47_margins` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 07:16 | **partial** | 0/26 | SECOND ATTEMPT, different construct: 365_recipe_card's -2.01 pt is a SPACE's advance, not an indent. The five METHOD steps are w:ind 800 (40 pt, correct: source 40.00 render 40.10) and the run text li |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 07:14 → running · 1 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 7 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| other - not attributed to a tool | **1 min** | `######################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

PUSH FINDINGS/widget-ap-glyph-walk-0436-f1x.patch and measure it: 601 goes 37/42 -> 42/42 docx checks in LibreOffice, blast radius is 2 documents of 213, and p2w builds from origin main so nothing corpus-wide can be measured until the patch is on main. Then measure 601 through Drive before and after (Google is the authority), and watch the Account form's two new fails (42_justification_edges, 63_table_rows). Do not chase t01 to 100% on 601 from the engine: verify_txt double-counts 'General' (glyph_truth appends _ap_stream_text to a page text pymupdf already synthesised the widget into), so only a duplicating engine can reach 100 and that costs 601 five docx checks. That is a person's decision, same as the 01:43 row.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
