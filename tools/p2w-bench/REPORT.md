# Fixer report - 2026-11-23 23:58

```
# P2W Fixer - Run Report

**24 Nov 2026 · slot 23:58 → running IST · 32 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 3 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
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
| Working on | `content-present-partly-displaced` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 00:09 | **lead** | 0/13 | instrument now prints med_dy/worst_dy/med_dx (KEPT); unruled row-excess quantum 15->5 twips spends the table-gap spacer on 72_bank_statement and takes Google med_dy -13.0->+1.1, worst 28.2->4.8, still |
| 00:24 | **lead** | 0/13 | instrument prints med_dy/worst_dy/med_dx (KEPT+committed, cross-checked to 0.1pt against independent PyMuPDF); unruled row-excess quantum 15->5 spends the table-gap spacer, Google med_dy -13.0->+1.1 w |
| 00:30 | **lead** | 0/13 | three solo documents measured in Google with the new dy instrument: 72_bank med_dy -13.0/worst 28.2 (spacer step), 71_invoice +1.1/6.7 (no spacer at all), table-no-header -0.5/9.0 (spacer correctly re |

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
| Slot window | 23:58 → running · 32 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 29 |
| Longest silence | **6.5 min** — from 00:18:24, after `lastmessage.py: running a tool for its numbers` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **8 min** | `######` |
| measure or build - a conversion, screen or compile writes no beacon | **3 min** | `###` |
| record - attempt, handoff, class rows | **6 min** | `####` |
| report - the report and the chain | **2 min** | `##` |
| other - not attributed to a tool | **10 min** | `#######` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

PENDING FIRST, FIXING SECOND - AND FIXING RESUMES BY ITSELF WHEN THE LIST IS EMPTY. `python3 tools/p2w-bench/pending.py` lists the 22 items you can close, in the order to take them. classpick.py refuses to name a class until those 22 are gone, so a run that tries to pick one is told to work the list instead. Nothing else changes: when the 22 reach zero, decide() returns a class again and the rotation carries on exactly as before - there is no separate mode to switch back on. The 22 are 4 [agent] (deployed 550-700 min ago, no finding committed - they died with their runs: check FINDINGS/ for the id and close them as dead, never re-deploy blind), 5 [ratchet] (fixes that landed on their own class and were never proved across the corpus - these are the cheapest wins, 38 documents already moved) and 13 [blocker] rows whose 'can I fix it' names a real action. THE OTHER 59 ARE NOT YOURS AND THEY DO NOT BLOCK YOU. `python3 tools/p2w-bench/pending.py --decisions` prints them: each says 'no - this needs a decision, not a patch'. They stay in BLOCKERS.md and in that view so a person can decide; they are never a reason to sit still. A gate that waited for them would never open, which is why it does not. After the 22: classpick picks by expected fixes - 05_chars_extra, then 32_stroke_lines, then 04_chars_missing (65 documents, never tried) and 25_invisible_text (48, never tried). 18_displacement is 8th because 20 attempts there moved 4 documents.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
