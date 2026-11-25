# P2W Fixer - Run Report

**25 Nov 2026 · slot 21:24 → running IST · 48 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8702** of 9320 (93.4%) on 213 documents |
| Check-instances still failing | **618** |
| Kept attempts vs documents clean | **15** classes with a kept attempt, **42** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; subagents: 2 deployed vs no FINDINGS file for A18_displacement, B60_text_column_ |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (18 still open), not a new class |
| Findings vs landing | **71** finding(s) on this class and **0** documents moved - writing is cheaper than landing, and nothing else says so |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 22:10 | **lead** | 0/None |  |

## The txt

| | |
|:--|:--|
| Measured | **54 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **204** (95.8%) |
| Failing at least one check | **9** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `A18_displacement-01` | cell line pitch: does Google take table row pitch fr | 21:24 | 22:11 | 47 min |
| `B60_text_column_right_edge-01` | root cause of the right edge of a text column in Goo | 21:24 | 22:11 | 47 min |

## Timing

| | |
|:--|:--|
| Slot window | 21:24 → running · 48 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 25 |
| Longest silence | **27.4 min** — from 21:24:41, after `pending.py: reading the pending gate` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **39 min** | `##################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **6 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 9 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. classpick --leverage picks the class; six checks can make a document clean (18_displacement 25, 60_text_column_right_edge 6, 47_margins 3, 59_shape_anchor 3, 32_stroke_lines 2, 17_matched_runs 1) and they are weighted 3x over the 34 that cannot. Read pending.py first, then take the class it gives.

## The measurement this run - nine arms in Google on `18_displacement`

Each arm is the engine's own `.docx` for `320_balance_sheet_statutory`, edited in XML only, uploaded,
converted to a Google Doc, exported to PDF and scored with `verify_google.py` against the corpus
original. One render each; 73 text runs matched on all nine.

| arm | Google passed | med_dy | worst_dy | laid row pitch (pt) |
|:--|--:|--:|--:|:--|
| BASE (engine as committed) | 46/47 | **+8.2** | **19.4** | 15.00 x16 |
| G15 - cell `w:line` on the 15-twip grid | 46/47 | +8.2 | 19.4 | 15.00 x16 |
| X195 - 195-twip cell line, rule `exact` | 45/47 | **+4.6** | 19.4 | 15.00 x16 |
| A195 - same box, rule `atLeast` | 45/47 | **+6.0** | 19.4 | 15.00 x16 |
| E280 - `w:trHeight` 280, `hRule="exact"` | 46/47 | +8.2 | 19.4 | 15.00 x16 |
| E300 - 300, `exact` | 44/47 | +13.2 | 51.7 | 15/16 |
| E280lin - 280 `exact` + 280-twip cell line | 45/47 | -42.1 | 374.3 | 15.00 x16 |
| **E260 - 260, `exact`** | 45/47 | **-4.8** | **8.9** | 13/14 |
| E240 - 240, `exact` | 45/47 | -10.8 | 43.8 | 12/13 |

The row pitch is measured off the horizontal rules in the exported PDF, not inferred from text.

**`w:lineRule` is honoured on import.** X195 and A195 are the same 195-twip box and differ only in the
keyword: +4.6 against +6.0 on the same 73 runs. The last run left "if they are identical, `w:lineRule` is
not honoured" as its discriminator. They are not identical.

**The cell line box does not move the row pitch.** All four cell arms lay 15.00 pt on all 16 rows, so
rank 2 is falsified as the row-pitch mechanism. The 3.6 pt it buys is a different, real effect.

**`w:trHeight` with `hRule="exact"` moves the laid pitch 1:1 above a content floor of about 15.00 pt** -
300 to 15/16, 280 to 15.00, 260 to 13/14, 240 to 12/13. At 280, `exact` is identical to `atLeast`, which
is why the last run's 280-to-300 `atLeast` probe moved nothing. The engine declares the source pitch,
which sits ON that floor, so every row lays 1.00 pt too tall and 16 rows accumulate the 19.4 pt.

**The zero crossing is near 267 twips, not 280.** med_dy goes +8.2 at 280 to -4.8 at 260; worst_dy
19.4 to 8.9 to 43.8. The next probe is 268 and 272, `hRule="exact"`.

## Why nothing was landed

E260 is the only arm that improves both distances and it is not landable: it does not clear
`18_displacement` and it picks up `25_invisible_text`. That check was found on 24 Nov to be reading the
paper rather than the text, so the new failure is most likely the known-bad check - but it is unverified,
and an unverified regression is a regression. A shift on every table row would also have to be measured
across all 213 documents, and the corpus was mid-build until 22:36.

## The corpus and the gate

The pod started with 50 of 213 documents converted. Three slices finished it (55, 55, 53), ending
`DONE - 213 documents converted, stamp written for engine 981ff1fa35e2cf67`. `install-gate.sh` then
installed the hook and passed with google-safe running, and both commits below landed through it.

## Two agents: two registered, one deployed

A (`18_displacement`, cell line pitch) returned the three cell arms, the cell paragraph census and the
local LibreOffice numbers - it is why the arms above are XML edits rather than an hour of guessing. It
could not make a Drive call: `GOOGLEDRIVE_UPLOAD_FILE` refuses a subagent's file key, so the Google leg
was the parent's work.

**B (`60_text_column_right_edge`) was registered and never deployed.** A subagent in a scheduled run
runs inline; agent A blocked the turn for 27 minutes, and deploying B would have spent the rest of the
slot without touching the class. The brief allows one with the number said out loud: 27 minutes of inline
cost in an 86-minute slot. `handoff.py --agent-land` closed both records against the one finding file;
**the entry for B is bookkeeping, not a second agent's work.**

## Honest limits

- One render per arm. BASE reproduced the recorded +8.2 / 19.4 to the tenth, but no arm was rendered twice.
- The source PDF's own rule pitch is not recoverable by the extractor (one horizontal item on page 0), so
  "the source is 14.00 pt" is inferred from the engine's declaration plus LibreOffice reproducing it.
- The content floor is measured at about 15.00 pt on this document's cells. Whether it is the same on
  every document is unmeasured, and it decides whether the fix is one constant or one formula.


---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
