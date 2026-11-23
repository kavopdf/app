# P2W Fixer - Run Report

**23 Nov 2026 · slot 18:58 → running IST · 39 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 3 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **0** of the **7** re-measured on this engine - **183** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 183 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `60_text_column_right_edge` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 19:31 | **reverted** | 0/0 | table-gap spacer spent PARTIALLY up to the page's remaining slack, instead of the binary whole-or-nothing spend: 49 docs' document.xml changed, and in Google it moved nothing on the two documents pred |
| 19:34 | **lead** | 0/0 | stale-engine hypothesis for the 24 one-check documents refuted on the 4 that share 60_text_column_right_edge: re-measured 302/313/316/321 on the current engine, all four still 41,46,41,41 with 60_text |
| 19:36 | **lead** | 0/0 | the check fires UNDER not over: all four report source=0 render=1 and the render's column is 58-66 pt NARROWER. Cause measured: docx declares DejaVuSerif/DejaVuSans, Google substitutes Arial, median l |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

**Two, both landed in-slot, both source-grounded, both with a ranked census.**

- *18_displacement construct ranking* — censused the class against the `.docx` the engine emits for all
  213 documents. Corrected the population from ~30 to **100**, and found the stored results carry **no
  displacement numbers at all** (`verify_google.py:5653-5655` computes `med_dy`, `worst_dy`, `med_dx`
  and writes none). Ranked ten constructs; named the table-gap spacer first (53 documents) with a
  computed prediction of three documents going clean. **That prediction was then refuted by
  measurement** — see attempt 1.
- *00_page_count census* — found **21 of the 23 page-count refusals render the source's exact page count
  in LibreOffice and only gain a sheet in Google**, and **14 of them pass every LibreOffice check they
  have**. Named one construct with a measured Google delta that nobody has built: the page frame emitted
  as 62 anchored shapes instead of `w:pgBorders` (`60_page_border` 2 → 1 page, same 689 characters).
  Filed as `FINDINGS/00_page_count-ANCHOR-RASTERISATION-CENSUS-agent-2312.md`.

## Timing

| | |
|:--|:--|
| Slot window | 18:58 → running · 39 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 21 |
| Longest silence | **19.8 min** — from 18:58:36, after `report.py: building the report` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **7 min** | `####` |
| measure or build - a conversion, screen or compile writes no beacon | **23 min** | `#############` |
| record - attempt, handoff, class rows | **2 min** | `##` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **5 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

**1. `60_text_column_right_edge` is a font substitution, and it is one round trip to settle.** The check
fires **under**, not over: the render's column is 58-66 pt narrower, the margins are zero, and the docx
declares **DejaVuSerif / DejaVuSans** while Google renders **Arial** — median line width drops 10-15 %.
Either embed the face, or pick the installed Google family whose advance widths match DejaVu at 10 pt
(measurable locally against the source PDF before uploading anything). 17.0 clean documents ride on it.

**2. `18_displacement` cannot be worked blind.** The check prints a count and never a distance. Publishing
`med_dy` / `worst_dy` / `med_dx` is an instrument change, not an engine change, so the corpus measure does
not block it — and until it lands, every attempt at this class is guessing at a magnitude it cannot see.
`tools/p2w-bench/dy.py` already exists and calls itself "the measurement `18_displacement` never prints".

**3. `00_page_count` — build the `w:pgBorders` page frame.** The only construct in this class with a
*measured* Google delta (`60_page_border` 2 → 1 page, same characters). It converts unscorable documents
into scorable ones, and 14 of the 23 already pass every LibreOffice check they have.

**4. Do not re-propose the spacer partial spend.** Refuted on 2 of 2 predicted documents and harmful on a
third; the finding is in `FINDINGS/18_displacement-PARTIAL-SPEND-IS-INERT-AND-COSTS-68-JOURNAL-2315-fixer.md`.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
