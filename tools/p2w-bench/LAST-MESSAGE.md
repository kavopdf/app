# P2W Fixer - Run Report

**23 Nov 2026 · slot 20:54 → running IST**

> Nine live Google renders on `table-with-no-header-row` and no document became clean. What the run bought is the mechanism: the row-pitch ramp is the engine's own 360/360/380 alternation being quantised by Google, Google's rendered pitch sits on a whole-point grid that 18.40 pt is not on, and the top-of-block offset the last two runs were chasing does not exist on this engine. No engine change landed.

## Progress


| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **13** of the **63** re-measured on this engine - **127** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **3** run(s) for the 127 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

One attempt, `18_displacement`, on `table-with-no-header-row` (1 page, 26 rows, source rules at a uniform 18.40 pt, table span 478 pt). Nine `.docx` variants of the engine's own output, each uploaded to the `KavoPDF-Verify` folder, converted by Google, exported as PDF and scored with `dy.py` and `verify_google.py`. Every number below is Google, not the LibreOffice proxy.

| # | what changed in the OOXML | pages | table span | n_out | med dy | rms_resid | checks |
|:--|:--|--:|--:|--:|--:|--:|:--|
| HEAD | as the engine emits it | 1 | 495 | **148** | −0.54 | 1.25 | 41/42 |
| V2 | spacer → 1×1 carrier table + rows 368 | **2** | – | – | – | – | refuted |
| V3 | rows `368 exact` | 1 | 507 | 165 | +3.46 | 12.52 | 41/42 |
| V4 | rows `600 exact` | **2** | 738 | – | – | – | probe |
| V5 | rows `346 exact` | 1 | 468 | 196 | −13.04 | 30.09 | 41/42 |
| V6 | rows `352 exact` + spacer height moved `w:line` → `w:before` | 1 | 468 | **132** | −4.36 | **0.67** | 41/42 |
| V7 | rows `356 exact` + same spacer change | 1 | 488 | 172 | +5.39 | 3.12 | 41/42 |
| V8 | rows `354 exact` | 1 | 488 | **136** | −4.04 | 1.04 | 41/42 |
| V9 | rows dithered 352/354, two in five | 1 | **476** | 212 | −9.79 | 29.13 | 41/42 |

The check allows 11 runs out.  The best variant is 132. Nothing is close.

## What the nine renders settle

**Google honours `w:trHeight`.** V4 declared 600 twips on every row and Google laid 30.0/31.0 pt pitches over a 738 pt span and pushed the table onto a second page. A construct a renderer ignores does not double a table when you double the number.

**The ramp is ours.** HEAD declares 360/360/380 twips with `hRule="atLeast"`; Google renders 19/19/19/19/20/18/19/20 and ends at 495 pt against the page's 478. Declare a uniform height and Google renders a uniform pitch — V3, V5 and V6 each came back flat. The 17 pt overshoot is the declared-height variation, not a Google defect and not the `w:spacing` carrier.

**The rendered pitch is on a whole-point grid.** 346 tw → 18.0, 352 tw → 18.0, 354 tw → 19.0, 356 tw → 19.0, 368 tw → 19.5, 600 tw → 30.75. No declared value renders 18.40. That is why tuning a row height has never closed this class: the target is not on the renderer's grid.

**Dithering does reach the geometry.** V9 declares 352 twips on three rows in five and 354 on two, and Google renders `18, 18, 19, 18, 19…` — span **476 against the source's 478**, the only variant that reproduces the page's own table height.

**And dithering loses the baselines.** V9's median dy is −9.79 pt against HEAD's −0.54. Making the table the right height moved every line inside it, because the cell paragraphs carry their position in `w:spacing w:before` computed against the old row height. Span and baseline are two quantities; `18_displacement` charges the baselines.

## Two leads this run retires

**The −10.16 pt top-of-block offset is not there.** HEAD, measured on this engine this run, reads median dy **−0.54 pt**, rms **1.25 pt**, first-line dy −1.36. `HANDOFF.md` and `LAST-MESSAGE.md` both told the next run to spend its budget on that number. Both now say otherwise.

**The carrier-table replacement for the spacer paragraph is refuted.** A 1×1 borderless table at `trHeight 247 exact` moved the block +20.5 pt and, with the rows retuned, opened a second page. Google charges a table's own overhead on top of its row height, so a table is not a transparent substitute for a paragraph's height.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Most common failure | `t12_word_invention` - 8 documents |

No `.txt` change was made or needed: the attempt touched only the `.docx` geometry.

## Subagents

| Agent | Sent to find | Landed |
|:--|:--|:--|
| `18C-01` | which OOXML element actually positions the top of a table block in Google, and what could carry it instead of `w:spacing w:before` | `18-DISPLACEMENT-CARRIER-ANALYSIS.md` |
| `00B-01` | why 23 of 213 documents are refused on page count and whether one construct causes them | `00-PAGE-COUNT-DIAGNOSIS.md` |

Agent A refuted the previous run's premise from the repo's own probe records: `w:before` is honoured 1:1 by Google over 1–4320 twips, and what Google mischarges is the `w:line … exact` box on the table spacer paragraph, at 21.6 % of its declared length. Its arithmetic reconciles the old −10.16 pt to 0.50 pt on the old engine — and the render above shows the offset is no longer present at all. It also produced the carrier-table construct I then refuted.

Agent B found the 23 page-count refusals are **stale, not broken**: `gverify.py::_done()` returns early on a refusal, so a refused document is never re-measured, 21 of the 23 records carry no engine stamp, and 19 of the 23 have never been scored at all. On the current tree 19 of them have a single shape-carrier paragraph and are predicted to fit. That is a re-measure, not a fix — it makes documents measurable, and on the two it could check it produced **0 clean**. Its proposed construct plausibly fixes 3 of the 23.

## Timing

| | |
|:--|:--|
| Slot window | 20:54 → running · 35 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **25.3 min** — from 20:55:15, after `report.py: building the report` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **25 min** | `################` |
| record - attempt, handoff, class rows | **4 min** | `###` |
| other - not attributed to a tool | **5 min** | `###` |
| report - the report and the chain | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

18_displacement: stop spending attempts on row pitch - measure the top of the block. The leading paragraph carries its vertical position in w:spacing w:before=1040 + w:line=13 exact, and the Google column of GVERIFY-BRIEF lists w:spacing as ignored. Build one variant that carries the same position WITHOUT w:spacing (exact-height empty paragraph, or w:ind/w:framePr), round trip table-with-no-header-row, and read the first line's dy: it is -10.16 now, and if it does not move the carrier is not the spacing. Then repeat on mobile-bill (-15.75).

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.


## Next run

18_displacement: stop spending attempts on row pitch - measure the top of the block. The leading paragraph carries its vertical position in w:spacing w:before=1040 + w:line=13 exact, and the Google column of GVERIFY-BRIEF lists w:spacing as ignored. Build one variant that carries the same position WITHOUT w:spacing (exact-height empty paragraph, or w:ind/w:framePr), round trip table-with-no-header-row, and read the first line's dy: it is -10.16 now, and if it does not move the carrier is not the spacing. Then repeat on mobile-bill (-15.75).

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*


## Next run

Take V9's dither and add the half it is missing: rewrite each cell paragraph's `w:before` from the **rendered** row height rather than the declared one, then round trip the same document and read `dy.py`. The target is median dy inside ±1 pt with `n_out` under 11. If the baselines come back, that construct is worth an engine change and a corpus pass; if they do not, the dither is geometry theatre and this class needs a different carrier. Do not re-measure the top of the block — it is already right.

The nine probe Google Docs were created in `KavoPDF-Verify` by this run and deleted by this run. No other Drive file was touched.
