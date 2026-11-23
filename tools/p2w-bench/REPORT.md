# Fixer report - 2026-11-23 13:20

```
# P2W Fixer - Run Report

**23 Nov 2026 · slot 13:20 → running IST · 1h 48m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **0** of the **0** re-measured on this engine - **190** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 190 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 14:02 | **reverted** | 0/None | partial spend of the table-gap spacer: Google 68_journal 41/42 -> 40/42, adds 59_shape_anchor, fixes nothing; flow-invariant so LibreOffice could not have caught it |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `A118_displacement-01` | writer-construct | 13:21 | - | - |
| `B160_text_column_right_edge-01` | right-edge+shape_anchor | 13:21 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 13:20 → running · 1h 48m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 23 |
| Longest silence | **52.3 min** — from 14:16:06, after `relay: fixer claimed the slot (the :50/:10 slot, found free)` |
| Silences over 2 min | 7 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **7 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **35 min** | `#######` |
| report - the report and the chain | **54 min** | `###########` |
| other - not attributed to a tool | **11 min** | `##` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

00_page_count: mechanism MEASURED, fix not landed. FINDINGS/00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md. Google rasterises each page-positioned floating shape and keeps the paragraph that carries it, and that empty paragraph costs ~0.83 pt of flow (w:line="1" exact is NOT honoured for it): 108 of them = 89.9 pt on 301_lab_report_panel against 44.5 pt of free page, so a 1-page source renders 2 pages. Deleting all 108 -> 1 page at the same text y (the control). 22 of the 23 refused documents emit ALL their drawing-only paragraphs AFTER the last text paragraph; counts 7..2464. 350_question_paper has 1 and is NOT explained by this. Refuted and measured, do not retry: drop-last, prstGeom-rect, wrapSquare, framePr. VOID (my probe bug, never measured): merge-into-one-paragraph and attach-to-text. NEXT LEVER, cheapest in the writer: merge the drawing-only paragraphs of a page into ONE (DocxWriter.shape(), DocxWriter.java:2726) - saves 107 x 0.83 = 88.8 pt against 89.9 pt needed here, a one-point margin, so measure it; then w:tcBorders through the table writer. This is the same construct as 32_stroke_lines and 05_chars_extra: one mechanism, three check families.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
