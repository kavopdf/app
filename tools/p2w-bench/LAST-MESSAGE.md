# Fixer report - 2026-11-25 01:24

```
# P2W Fixer - Run Report

**25 Nov 2026 · slot 01:24 → 02:01 IST · 37 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 6 vs ATTEMPTS.json history 1; subagents: 3 deployed vs no FINDINGS file for gap--01, zero-01 |
| Document-moves this run | **0** — 6 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **36** of the **187** re-measured on this engine - **4** of the 191 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **22** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `04_chars_missing` - taken from the pending list (19 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `04_chars_missing` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 02:00 | **lead** | 0/None | row-pitch dither alone: ditherOn true, trHeight moves onto the 0.75pt grid (mobile-bill 360/380 -> 345/360/375); page result unmeasured because p2w.py --force measured stale docx (mtime 19:57 vs patch |

## The txt

| | |
|:--|:--|
| Measured | **52 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `gap--01` | gap-cap patch: traced DocxWriter, produced spendWide | 02:59 | - | - |
| `zero-01` | zero-gap census: the latch is 655 lines/24920 chars  | 02:59 | - | - |
| `Goog-01` | Google verification: 69_two_col_legal 35/42 -> 39/42 | 03:12 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 01:24 → 02:01 · 37 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 19 |
| Longest silence | **5.3 min** — from 01:54:39, after `measuring the corpus after the dither (chunk 5 retry)` |
| Silences over 2 min | 6 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **0 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **10 min** | `#######` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **19 min** | `#############` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 18 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 18 item(s) you can close - run pending.py and take them in its order before the class below. Add the look-ahead guard to spendWideGap: spend the gap only when no line remaining on this page targets a baseline BELOW this one. The engine has the page in hand, so it is a comparison, not a pass. Target: keep 39/42 on 69_two_col_legal_numbered_clauses and drive 26_text_overlap back to 0. Then re-measure 330_cad_drawing_sheet (spend-everywhere cost it 3.14 -> 16.77 pt median) and the 47 stamp documents that carry <200 boxed chars - those will not close by any writer change.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.

---

## THIS RUN IN DETAIL (written by the fixer, 02:20-03:35)

report.py's "What was tried" and "Subagents" rows above are read from the ledger and did not pick up this
slot; the facts they miss: **2 sub-agents were deployed**, and two attempts were recorded this run, both
`04_chars_missing -> lead`.

### PROVEN IN GOOGLE: 69_two_col_legal_numbered_clauses 35/42 -> 39/42

Build: `spendWideGap()` (`FINDINGS/04_chars_missing-GAPCAP-PATCH-0225-agent.patch`) with `FOOT_BAND = 0.0f`
and `-Dp2w.pagepos=0 -Dp2w.anchorkeep=0 -Dp2w.zganchor=false`. The emitted .docx goes from **36 anchored
text boxes / 1358 characters to 0 / 0**, page count unchanged. Uploaded to `KavoPDF-Verify`, converted on
import, exported as PDF, deleted; `verify_google.py <source> <export> --docx`.

| | recorded HEAD (`b7699196`) | this build |
|---|---|---|
| score | **35/42** | **39/42** |
| failing | 04_chars_missing, 10_font_sizes, 13_text_colours, 17_matched_runs, 38_list_markers, 44_header_footer, 45_char_accuracy | 18_displacement, 26_text_overlap (**render=11**), 60_text_column_right_edge |

**Six of the brief's named classes pass on this document now:** 04_chars_missing, 45_char_accuracy,
13_text_colours, 44_header_footer, 17_matched_runs, plus 10_font_sizes and 38_list_markers.

**The price is `26_text_overlap` at 11 rendered overlaps.** That is the foot-band guard's job: dropping it
to 0 lets a mid-page gap be spent, and three lines land on content the page already drew. The guard the
patch needs is not a band, it is a look-ahead - spend only when no line remaining on the page targets a
lower baseline.

The engine was **reverted**: the gate refuses an unmeasured engine and `26_text_overlap = 11` is a real
regression on a real document. Nothing was committed to it.

### The correction this run establishes

The brief calls the 120 pt `gapCapTw` threshold "the largest engine defect anyone has found" at ~166
document-failures. Measured over all 213: the cap carries 1,469 characters; the page-local latch
`ctx.positioned` (`DocxWriter.java:3126-3144`, read in exactly three places, all in `para()`) carries
**24,920 characters over 655 lines**, because once one line on a page is anchored every later line on that
page is. And **47 of the 64 documents failing 04_chars_missing carry fewer than 200 boxed characters** -
their box is a stamp, not body text, so emptying boxes cannot clean them.

### Written and not kept

`spendWideGap()` at `FOOT_BAND = 0.90` is a no-op on 69, 323 and 311 - its guard never fires on them.
`-Dp2w.pagepos=0 -Dp2w.anchorkeep=0` alone cuts 69 from 1358 to 367 boxed characters, academic-paper from
2942 to 181, 323 from 222 to 35, 311 from 206 to 30, and changes nothing on 47 of the 64.

### Next run

Add the look-ahead guard to `spendWideGap`: spend only when no remaining line on the page targets a lower
baseline. Target: keep 39/42 on 69 and drive `26_text_overlap` back to 0. Then re-measure
`330_cad_drawing_sheet` (spend-everywhere cost it 3.14 -> 16.77 pt median) and accept that the 47 stamp
documents need a rule about what kind of text a box may carry, not a writer change.
