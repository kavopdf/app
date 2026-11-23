# P2W Fixer - Run Report

**24 Nov 2026 · slot 00:56 → running IST · 0 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
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
| Working on | `-` |

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
| Slot window | 00:56 → running · 0 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 2 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

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
