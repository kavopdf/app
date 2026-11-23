# P2W Fixer - Run Report

**23 Nov 2026 · slot 08:55 → 09:56 IST · 1h 01m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **0**, out of the 2 measured on THIS engine (all engines: 30 of 190) |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `00_page_count` |
| Committed | **11** files in 5 commit(s) from `8f87185` — ...18_displacement-PAGE-SHIFT-CENSUS-1015-agent.md, ENGINE-STAMP.json, LAST-MESSAGE.md, RANKING.csv, REPORT.md, ROTATION.json, ROUND.json, RUN.json, TIMELINE.jsonl, TRACE.md, UNMEASURED.json |

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

## What this run proved - 00_page_count, measured in Google

Class picked: `00_page_count`, second in `classpick.py --leverage` at **23.0** clean documents and the
largest class whose mechanism was already measured. The 0530 finding named `DocxWriter.shape()` as the
lever; that was half right, and the wrong half is why the previous attempt came back empty. `pageBody()`
**already** appends every shape as a bare run to the page's last paragraph with one carrier paragraph per
page, so a merge in `shape()` is a no-op for 301, 375, 341, 390, 403, 405, 351, 333, 305 and the rest.
The path still emitting one paragraph per shape is `shape()` reached through `emitBlock()` from inside the
column pass, `columnPage()`. The patch (+47/-5: a `shapeCarrier` StringBuilder, `flushShapes()` at both
exits of `pageBody()`, and a cell that held only a shape still gets a paragraph) changes that.

Before arm = HEAD, after arm = HEAD plus the patch, both converted in this sandbox and both rendered by
Drive into `KavoPDF-Test-Outputs`:

| document | source pages | HEAD | + patch | 42 checks (Google, after) |
|---|--:|--:|--:|:--|
| `361_product_catalogue_grid` | 1 | **2** | **1** | 41/42 - only `25_invisible_text` |
| `401_trifold_brochure` | 1 | 2 | 2 | still refused |

`361` was one of the 23 documents gverify refuses to score; with the patch it is scorable for the first
time and reads 41/42. `401` was the coin flip the 0530 finding predicted - 20 x 0.83 = 16.6 pt saved
against ~0 pt of slack - and it came up short. Nothing got worse: LibreOffice page count identical on all
21 changed documents with all 42 checks unchanged (it honours `w:line="1"` exact, Google does not), the
`.txt` byte-identical on 213/213 and re-scored by `restamp_txt.py` as "213 scored, 0 newly clean, 0 newly
failing, 213 unchanged", `document.xml` byte-identical on 192 of 213.

## Why it is not landed, and the order that lands it

    ENGINE CHANGED (docx): table measured on 4a607e4b793fb348, the tree is 3e7f7c4475343a35
    ENGINE CHANGED (txt):  table measured on d20930229132b191, the tree is b97d8172ce642eb0

The `.txt` half re-measured in 47 s. The `.docx` half is `benchmarks/gate.py --budget 250` and it did not
finish inside one 290 s call - no output, neither `RANKING.csv` nor `STATE.json` written. That is the
whole gap: the measurement outlives the call limit, not the evidence. `regress.py --stamp` also refuses
until the table is committed at or after the engine, so engine and table must travel in one commit.

So the engine edit was reverted, `regress.py --check` re-run on the committed tree (**PASS - nothing got
worse in both formats, and the table matches this engine**), and the patch committed beside its finding
so no run derives it again:

    tools/p2w-bench/FINDINGS/00_page_count-MERGE-SHAPE-PARAGRAPHS.patch
    tools/p2w-bench/FINDINGS/00_page_count-MERGE-IN-COLUMN-PAGE-MEASURED-IN-GOOGLE.md

Next run, in this order: apply the patch, `build-engine.sh`, then `benchmarks/gate.py --budget 250`
**across two or three calls with a beat between them**, then commit engine + `RANKING.csv` + `STATE.json`
together, `regress.py --stamp`, commit the stamp, `regress.py --check`, push.

## Subagents and an instrument defect

One subagent, deployed in the first ten minutes with the merge as its problem and 361/401 as the
documents to prove it on. It returned the patch, the corpus-wide byte comparison and the LibreOffice
table, and it found that `pageBody()` already carried the merge - the correction above is its work plus
this run's Google measurement. It ran inline (21 min) rather than in the background, which is where a
third of the slot went; the second agent was never deployed, which is the shortfall the release guard
correctly refused.

`GOOGLEDRIVE_DOWNLOAD_FILE` no longer returns `downloaded_file_content.s3url`; it returns
`artifacts[0].workspace_path`, a local path. `gverify.py --collect <name> <s3url>` expects a URL, so
`--collect` cannot be called with what the tool now hands back; the page counts and the 42 checks above
were run directly with `verify_google.py <src> <render> --docx <docx>`. That mismatch will block the next
gverify run.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
