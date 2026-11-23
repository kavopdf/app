# P2W Fixer - Run Report

**23 Nov 2026 · slot 20:54 → running IST · 1h 47m**

> No change was kept this run. The numbers below say what was tried.

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

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 21:29 | **lead** | 0/0 | nine live Google renders of table-with-no-header-row: Google honours w:trHeight (600tw->30/31pt) and quantises the rendered row pitch to whole points (352tw->18.0, 354/356tw->19.0, 368tw->19.5); the 1 |

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
| Slot window | 20:54 → running · 1h 47m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **72.2 min** — from 21:30:38, after `report.py: building the report` |
| Silences over 2 min | 4 |
| Obstacles | 3 cleared · 2 parked, with the evidence to re-open them |
| Still a wall | **This watchdog has no `cron` tool**, so a paused or zombie cron cannot be moved by automation and STEP 3 cann |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **25 min** | `#####` |
| record - attempt, handoff, class rows | **4 min** | `#` |
| report - the report and the chain | **1h 12m** | `###############` |
| other - not attributed to a tool | **5 min** | `#` |
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

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
