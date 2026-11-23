# Fixer report - 2026-11-23 15:02

```
# P2W Fixer - Run Report

**23 Nov 2026 · slot 15:02 → 16:38 IST · 1h 36m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **0** of the **0** re-measured on this engine - **190** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 190 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `00_page_count` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 16:34 | **partial** | 2/23 | LANDED the column-page shape merge (21 documents change in document.xml, 361 124->40 paragraphs, 401 52->27, 301 untouched at 85). Corpus on this tree: 212/212 scored, 0 documents worse, regress PASS, |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `00_pA-02` | which construct costs 350_question_paper its second  | 16:37 | - | not recorded |
| `gverB-01` | why gverify --collect cannot read the download resul | 16:37 | - | not recorded |

## Timing

| | |
|:--|:--|
| Slot window | 15:02 → 16:38 · 1h 36m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 55 |
| Longest silence | **6.1 min** — from 15:28:54, after `attempt 1: forced rebuild of 213 on the patched tree, call 1` |
| Silences over 2 min | 18 |
| Obstacles | 2 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | `health.py --stalled` exits 0 and the fix row reads moving, 1 attempt(s) in the last 3 h, stage age 1.2 h. `st |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **3 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **16 min** | `####` |
| record - attempt, handoff, class rows | **3 min** | `#` |
| report - the report and the chain | **13 min** | `###` |
| other - not attributed to a tool | **58 min** | `#############` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

00_page_count: measure 041122-Account_Opening_Form in Google (2464 drawing-only paragraphs, nine pages, worst score in the corpus at 98.65) - the scale test for the carrier paragraph. Then 350_question_paper: FINDINGS/00_page_count-350-INLINE-PICTURE-CARRIES-THE-LINE-1120-agent.md charges picture() lines 2542-2564 (an unplaced picture emitted <wp:inline> in a paragraph with no w:pPr, inheriting sz=22 and w:after=120 from docDefaults, which spacingTw cannot see); the patch beside it is UNCOMPILED. Then w:tcBorders for 32_stroke_lines/05_chars_extra.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
