# Fixer report - 2026-11-21 15:58

```
# P2W Fixer - Run Report

**21 Nov 2026 · slot 15:58 → running IST · 1h 43m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 17:00 | **partial** | 1/5 | uprightIfPageIsUpsideDown patch landed: one-page-rotated-180-degrees t02_position FAIL->PASS, 213 of 213 .txt converted+scored, 190 clean (was 189), 0 newly failing. .docx proved byte-identical on all |
| 17:25 | **reverted** | 0/5 | The 180deg guard, built and measured on all 213 documents (213/213 .docx word/document.xml byte-identical, 212/213 .txt identical, one-page-rotated-180-degrees t02_position FAIL->PASS, t02_position 5- |
| 17:39 | **reverted** | 0/145 | pBdr rule carrier REFUTED by measurement, not by argument: patched engine, 12 class documents, 172 source rules counted with check 32's own detector. 68 rules became w:pBdr, but 48 of the 68 land more |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **190** (89.2%) |
| Failing at least one check | **23** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `32_sA-01` | Does the pBdr replacement in FINDINGS/RULES-PBDR-IMP | 15:59 | 12:10 | 101 min |
| `t02_B-01` | The 180deg uprightIfPageIsUpsideDown patch (FINDINGS | 15:59 | 12:09 | 100 min |
| `t08_B-01` | which code path decides the .txt line order, and wha | 17:39 | 12:09 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 15:58 → running · 1h 43m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 40 |
| Longest silence | **22.7 min** — from 16:37:48, after `HEAD rebuilt; converting all 213 to out-head for a byte-for-byte docx ` |
| Silences over 2 min | 11 |
| Obstacles | 2 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **Two fixers ran the same slot and duplicated 65 minutes of work.** This run claimed at 16:16 (`round.py --cla |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **22 min** | `#####` |
| measure or build - a conversion, screen or compile writes no beacon | **1h 09m** | `###############` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **6 min** | `#` |
| other - not attributed to a tool | **3 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Judge the t08 verifier question before touching the engine: is t08_line_order measuring line order or drawing order? FINDINGS/t08_line_order-DRAWING-ORDER-1740.md has the numbers (10 of 10 rows clear when only our own line sequence is put into drawing order). The agent's proposed one-line sort of _src_pages is NOT obviously right - it would compare sorted-vs-sorted. Decide with a falsification: construct a .txt whose lines are deliberately swapped in y and confirm t08 still fires after the change. Then take t01_word_accuracy's .docx half or 32_stroke_lines' cell-border construct.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
