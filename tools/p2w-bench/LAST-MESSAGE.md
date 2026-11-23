# P2W Fixer - Run Report

**23 Nov 2026 · slot 08:55 → 09:56 IST · 1h 01m**

The pipeline was not slow this run, it was dead: every commit, including the fixer's own claim, was
refused by the gate because `benchmarks/RANKING.csv` still described the engine from before `5beb8b9d`,
and the docx stamp had been correctly deleted when it was found to be a lie. Two fixer slots died on it -
the 08:11 run claimed, could not push the claim, and vanished.

So this slot went to the gate. I built the engine (no `java` on the image; `build-engine.sh` fetches a
JDK from Adoptium in 38 s), fetched the corpus from the public `corpus-v1` release, and ran
`benchmarks/p2w.py` to completion in nine calls: 213 `.docx` converted and every measurable document
scored on engine `4a607e4b793fb348`. I published the table, restored the exempt row `rank()` still drops,
committed the measurement, and stamped docx only after that commit - in that order, because the stamp's
own precondition is that the table was committed after the engine. `regress.py --check` now prints PASS
for both formats and `measure_gate.py` prints READY.

No document moved: with the commit gate shut, a measured fix could not have been recorded, and
`attempt.py` refuses a moved count against an uncommitted tree. The next run can claim, measure and
commit, which no run since `5beb8b9d` could do.

The one subagent came back with a measured mechanism worth the next slot: Google honours `w:before` at
the top of the body but **drops it at the top of a page opened by a page break** - a probe page carrying
`w:before="1097"` after a break reads 54.85 pt high plus its own 1.35 pt residual, agreeing to 0.01 pt.
It also refuted the obvious guess: the 13 documents that fail `18_displacement` and nothing else are all
single-page with no page breaks, so the margin is not their mechanism. The writer value it names is
`w:pgMar w:top`, the literal `"0"` at `DocxWriter.java:2391`.

I deployed one agent, not two. The second would have run inline for another 13 minutes against a slot
with a corpus pass still to pay for. Recorded, not hidden.

---

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **0**, out of the 2 measured on THIS engine (all engines: 30 of 190) |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` |
| Committed | **10** files in 3 commit(s) from `e87f223` — ...18_displacement-PAGE-SHIFT-CENSUS-1015-agent.md, ENGINE-STAMP.json, LAST-MESSAGE.md, RANKING.csv, REPORT.md, ROTATION.json, ROUND.json, TIMELINE.jsonl, TRACE.md, UNMEASURED.json |

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
| Slot window | 08:55 → 09:56 · 1h 01m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 18 |
| Longest silence | **14.9 min** — from 08:55:53, after `claimed, reading findings` |
| Silences over 2 min | 11 |
| Obstacles | 0 cleared · 4 parked, with the evidence to re-open them |
| Still a wall | **The fixer's claim is 55 min old against a 45-min stale window and no run has beaconed since it claimed at 08 |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **1 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **29 min** | `###########` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **29 min** | `###########` |
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
