# P2W Fixer - Run Report

**22 Nov 2026 · slot 07:14 → 07:36 IST · 22 min**

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
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What this slot settled

Two measurements, both through Google Docs on `bank-statement-5-pages`, engine `7112d766`, and both
in `FINDINGS/18_displacement-page-top-gap-sectmargin-PROVEN-075600-f1x.md`.

| variant | pages | score | failing |
|:--|---:|---:|:--|
| BASE (the engine's own output) | 5 | 37/42 | 18, 25, 27_text_off_page, 44, 59 |
| 1x1 `trHeight` row in place of the page-top `w:before` | **6** | **33/42** | 01, 17, 18, 25, 31, 32, 44, 55, 59 |
| `w:pgMar w:top` in place of the page-top `w:before` | 5 | **40/42** | 18, 25 |

The row is **refuted**: it does not merely overflow by a few points, it takes the document from 5
pages to 6, empties a page and drops matched runs from 585 to 220. The margin is **proven**: the
-59.5 pt uniform shift on pages 1-4 collapses to the -4.3 pt the document already carries on page 1,
the page count holds, and three checks recover with nothing new failing. All three probe Google Docs
were deleted; the `KavoPDF-Verify` folder is empty.

And the correction that matters more than either: **all 16 documents that fail `18_displacement`
alone are single-page, with zero page breaks in their `.docx`.** The page top cannot be their cause.

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

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-02` | what makes a single-page dense table drift in Google | 07:36 | 02:06 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 07:14 → 07:36 · 22 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 24 |
| Longest silence | **9.0 min** — from 07:26:45, after `report.py: building the report` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **Both scheduled slots between the last release and this claim produced no run at all.** `gaps.py` records `GA |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **1 min** | `##` |
| fix - diagnose and change the engine | **2 min** | `###` |
| measure or build - a conversion, screen or compile writes no beacon | **9 min** | `#########` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **3 min** | `####` |
| other - not attributed to a tool | **3 min** | `####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

The 16 solo-18 documents: their emitted row pitch ALREADY equals the source (0.00 pt on 11 of 16, -0.10 to -0.40 on the rest), so no constant in the row-height path (DocxWriter.java:6228) can move them closer. The leading candidate is the TABLE-TOP SPACER at DocxWriter.java:5869-5881: the gap above a table is written as w:line on a 1 pt mark, and Google reads w:line as a multiple of the face's line height, so 68_journal_wide_table_spanning's 144.0 pt spacer may render as 13.74 pt (-130.3) or 160.9 (+16.9). One Drive probe settles which: an empty <w:p> with w:sz=2 and w:line=2880 w:lineRule="exact" - does it come back 13.74, 144 or 160.9 pt? The spacer moves 14 of the 16 by 4.2 to 130.3 pt; 71_invoice_space_aligned_no_rules and 31_times_body_arial_headings have no spacer, and 31_times has no table at all, so its failure cannot be pitch. Full numbers in FINDINGS/18_displacement-single-page-row-pitch-EMITTED-PITCH-IS-EXACT-082000-f1x.md. Do NOT take the page top for these 16: they are single-page with zero page breaks.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
