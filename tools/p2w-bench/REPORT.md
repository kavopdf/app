# Fixer report - 2026-11-22 07:14

```
# P2W Fixer - Run Report

**22 Nov 2026 · slot 07:14 → running IST · 12 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Improved in LibreOffice | **61** of the 212 compared (corpus 213) — a proxy, not the goal |
| &nbsp;&nbsp;— of those, clean in Google | **3** — and **57** still open there |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 07:25 | **lead** | 0/213 | page-top gap: 1x1 trHeight row REFUTED through Google (bs5 37->33/42, 5->6 pages, page emptied); w:pgMar w:top PROVEN (bs5 37->40/42, 5 pages held, dy -59.5->-4.3 on pages 1-4, 3 checks recovered); al |

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
| Slot window | 07:14 → running · 12 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 16 |
| Longest silence | **5.0 min** — from 07:14:12, after `gaps.py: reading the timeline` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **Both scheduled slots between the last release and this claim produced no run at all.** `gaps.py` records `GA |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **5 min** | `#########` |
| fix - diagnose and change the engine | **2 min** | `#####` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| other - not attributed to a tool | **3 min** | `#######` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Do NOT take the page top for the 16 documents that fail 18_displacement alone: all 16 are single-page PDFs and their converted .docx carries zero page breaks, so the page-top construct (proven this run) cannot make one of them clean. Their displacement is row/line pitch inside one dense table or form - start from the -4.3 pt median / -12.8..+2.9 pt spread on page 1 of bank-statement-5-pages, which is the residual after the page-top fix and sits on a page that was never broken. Land the section margin (w:pgMar w:top) as a separate build on multi-page documents: DocxWriter.java:1053-1075 already emits a sectPr with nextPage, so it is that path plus beforeTw=0 in the two ctx.newPage branches (3395-3401, 4277-4283) plus the same twips out of ctx.budgetTw (1116) and out of what pageFits is asked - the first two alone double the gap in LibreOffice, the third is what holds the page count. Do NOT retry the 1x1 trHeight row: measured this run, it takes bank-statement-5-pages from 5 pages to 6 and 37/42 to 33/42. Numbers: FINDINGS/18_displacement-page-top-gap-sectmargin-PROVEN-075600-f1x.md.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
