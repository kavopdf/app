# P2W Fixer - Run Report

**23 Nov 2026 · slot 04:56 → running IST**

> No change was kept this run. One class was opened, its mechanism was measured through Google eight
> times, and the fix it needs is named with a number. The numbers below say what was tried.

## The class, and why this one

`00_page_count` - 23 documents, 23.0 clean-document leverage, and **not one FINDINGS file had ever
explained a single one of them**. The tool suggested `47_margins` on the strength of an open lead, but
that lead's own note says "next run: the .txt half", and the .txt half is a separate slot's question.
`00_page_count` is the second-biggest prize in the leverage table, every document under it fails exactly
one thing, and it is invisible to every local instrument: LibreOffice renders these documents on the
right number of pages, so `screen.py`, `gate.py` and `p2w.py` cannot see the defect at all. Only a Google
round trip can, and nobody had made one.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **28**, out of the 190 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `00_page_count` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 05:09 | **lead** | 0/23 | The mechanism of `page_count_refused`, measured on eight Google renders. See below; the stored reason in ATTEMPTS.json was corrected after an independent re-measurement. |

## What this run established

1. **Google does not drop a floating shape.** It rasterises it at its page coordinates: 108 vector rules
   in the source become 108 image placements, 58 on page 1 and 50 on page 2.
2. **The flow cost is the empty paragraph that carries each shape, ~0.83 pt.** `w:line="1" exact` is not
   honoured for it. Measured: deleting one of those paragraphs moved the page-2 block 40.7 -> 39.9 pt.
3. **The arithmetic closes on `301_lab_report_panel`:** 108 such paragraphs cost 89.9 pt, page 1 has
   44.5 pt free, the last text line already sits 9.5 pt low. Delete all of them and it renders **one
   page** with the text at the same y - the control that proves the cause is the paragraphs, not the text.
4. **22 of the 23 refused documents carry these paragraphs and emit every one of them after the last
   text paragraph** - 7 to 2464 of them. `350_question_paper` has one and is not explained by this.
5. **Four candidate fixes measured and refuted** (drop the last paragraph, `prstGeom` rect,
   `wrapSquare`, `w:framePr`) - each still 2 pages, each with its number in the finding. Two more
   (merge into one paragraph, attach to text paragraphs) are recorded **void, not refuted**: my probe
   builder had a slicing bug and never measured what the row claims.
6. **The same construct is `32_stroke_lines` and `05_chars_extra`.** One mechanism, three check families.

## An instrument that lied, and was caught

The first write-up of this finding said "Google inlines the shape and each costs 0.79 pt". A second agent
re-measured every claim from the exported files alone: the page counts, image counts and paragraph counts
held, but the images are **not** inline - they keep their page positions, and the 0.83 pt is the empty
paragraph. Two of my six probes were built by a loop that never removed the originals. The finding and
the stored attempt reason were both corrected; nothing here claims a measurement I do not have.

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
| Slot window | 04:56 → running · 16 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 17 |
| Longest silence | **9.1 min** — from 05:00:24, after `agent B landed: 12 docs fail 18_displacement alone; fetching corpus` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **9 min** | `############` |
| record - attempt, handoff, class rows | **5 min** | `#######` |
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

`00_page_count`: the mechanism is measured; the fix is one change in the writer. Cheapest lever first -
merge a page's drawing-only paragraphs into ONE (`DocxWriter.shape()`, DocxWriter.java:2726): 107 x 0.83 =
88.8 pt saved against 89.9 pt needed on `301_lab_report_panel`, a one-point margin, so measure it rather
than assume it; then route a rule that belongs to a table cell through the table writer as `w:tcBorders`.
Do not retry drop-last, prstGeom-rect, wrapSquare or framePr - each is a measured dead end. Build probes
by REMOVING the originals (my bug), and check `</w:body>` survives.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
