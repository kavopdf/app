# P2W Fixer - Run Report

**23 Nov 2026 · slot 12:14 → 13:03 IST · 48 min**

> No document moved this run. One gate defect was fixed, committed and pushed; the table that lands the page-count patch still cannot be produced inside one call, and this run measured why.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **0** of the **2** re-measured on this engine - **188** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 188 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `00_page_count` |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 12:14 → 13:03 · 48 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 0 |
| Longest silence | **38.2 min** — from 12:24:40, after `lastmessage.py: running a tool for its numbers` |
| Silences over 2 min | 2 |
| Obstacles | 2 cleared · 4 parked, with the evidence to re-open them |
| Still a wall | **The window closed and the relay took it: this is the pair working, and no force release was needed.** Commit |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| report - the report and the chain | **39 min** | `##################` |
| other - not attributed to a tool | **7 min** | `####` |
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

## What this run kept: the gate counted 211 of a 212-document corpus

`_expected_docs()` counts the real documents from four hard-coded paths. `p2w.py` looks at
`HERE/realworld` **first**, and a clone at `/scratch/work/CS` is none of the four — so gate.py found
`real = 0` and expected **211** while p2w.py measured **212**. `complete` was therefore reachable at
211 of 212: gate.py would publish `RANKING.csv` with one document never measured in it, under a verdict
saying the measurement was complete.

Three independent sources agree the corpus is 212: 213 PDFs in the corpus directory, 1 entry in
`EXEMPT.json` (`416_many_tiny_pages`), and `report.py`'s own "212 compared". `_expected_docs()` now
returns **212** from this clone; it returned **211** at HEAD.

The second fix: `measured` was a bare `glob("dist2/*.json")`, which counts p2w.py's
`dist2/<doc>.partial.json` page window as a measurement. That file has no `doc`, no numbers and no
verdict — it is a progress note, and p2w.py's own `results()` excludes it. A probe pair written into
`dist2/` showed the old glob counting **2** files where `_result_files()` correctly saw **1**.

Verified: `py_compile` clean, the one-shot path run end to end (`INCOMPLETE: measured 0 of 212`,
ground truth pass, txt checks available), `benchmarks/STATE.json` restored to the committed run of
record, `regress.py --check` **PASS — nothing got worse in both formats, and the table matches this
engine**.

## Why no document moved, in numbers

The `00_page_count` patch is ready and already measured in Google by the 08:55 run
(`FINDINGS/00_page_count-MERGE-SHAPE-PARAGRAPHS.patch`: `361_product_catalogue_grid` 2 → 1 page,
41 of 42 checks). Landing it needs the docx table re-measured, and the table does not fit one 290 s
call. This run measured the shape of that wall:

| what | measured |
|:--|--:|
| `build-engine.sh`, cold | **38 s** |
| conversion, one JVM per document | **~9–10 s** per document |
| `p2w.py`'s inner group (`CHUNK`) | **12** documents, rendered *then* measured |
| `gate.py --resume --budget 110 --chunk 45` | **0 of 212** measured, p2w exit 124 |
| `gate.py --resume --budget 250 --chunk 200` | **0 of 212** measured, no progress note written |

A `--resume`/`--chunk` patch (165 lines) was written and compiles, and was **not landed**. The reason
is `p2w.py`'s own loop: it prerenders a group of twelve, then abandons the whole group if the clock
runs out before the first document is measured, so a chunk shorter than one group writes nothing —
which is what both chunk sizes above did. Resuming needs chunks of ~200 s, i.e. **one chunk per call**,
and 212 documents at ~12 per call is **~18 calls**, not the 2–3 the previous report planned for.

A second reason it is not in this commit: on one `--resume` invocation whose guard says *do not write
the repository's copy*, `benchmarks/STATE.json` changed anyway (`c0c27d72…` → `54a0dfad…`, an
`INCOMPLETE` record, eight seconds after the run's last log line). Restored with `git checkout`. A
guard that does not hold is worse than no guard.



---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
