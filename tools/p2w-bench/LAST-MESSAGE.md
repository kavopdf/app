
  written to tools/p2w-bench/REPORT.md - commit it, so the report survives the run
# P2W Fixer - Run Report

**22 Nov 2026 · slot 05:56 → 06:18 IST · 22 min**

> **19 document(s)** improved this run, but the run did not commit benchmarks/RANKING.csv, so the report cannot name them.

## Progress

| | |
|:--|:--|
| Document-moves this run | **19** — 3 attempt(s), 2 kept (a sum: a document moved twice counts twice) |
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
| 06:10 | **kept** | 3/213 | check 32 read only vector segments; Google exports an anchored rule as a raster image at the same geometry. Made the check read image bands (band=RULE_BAND_REN, the same width the vector path uses). M |
| 06:13 | **kept** | 16/213 | the check change measured on 20 Google exports from a live round trip: 16 documents 41/42 -> 42/42, 0 worse. 13 of 14 documents failing {05,32} came back 42/42 - 05_chars_extra passes on HEAD too, so |
| 06:17 | **lead** | None/None | 15 documents that failed {05,18,32} were re-measured through Google on HEAD: every one is now 41/42 failing 18_displacement ALONE (4 are 46/47 failing it alone). 05_chars_extra and 32_stroke_lines bot |

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
| Slot window | 05:56 → 06:18 · 22 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 28 |
| Longest silence | **8.8 min** — from 05:56:39, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **this watchdog has no `cron` tool, so a paused or zombie cron cannot be moved by automation.** STEP 3 and STE |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2 min** | `###` |
| measure or build - a conversion, screen or compile writes no beacon | **13 min** | `#############` |
| record - attempt, handoff, class rows | **3 min** | `###` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **2 min** | `##` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Apply tools/p2w-bench/patches/rule-carrier-horizontal-only-2008.patch, build, run the corpus pass and take the exact LO regressions. The 16 documents already measured in Google under this patch are in benchmarks/gverify-carrier-2008/: 13 reach 42/42, 3 reach 41/42, none regress, all 16 clear 05_chars_extra. regress.py already exempts a LibreOffice regression when Google improved on the same document - it needs benchmarks/gverify/<doc>.json in the working tree. So run gverify --plan 60 over the regressed documents that have no carrier result, and land the patch with those results in the same push. Do NOT build the cell guard the last report asked for: no Shape is ever routed into a w:tc (max tc-depth 0 across 156 carriers in 22 docs) and the guard built byte-identical output on five PDFs.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
