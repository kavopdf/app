# Fixer report - 2026-11-21 15:17

```
# P2W Fixer - Run Report

**21 Nov 2026 · slot 15:17 → running IST · 31 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `47_margins` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 15:48 | **partial** | 1/213 | 180deg patch measured on .docx for the first time: 140 of 213 byte-identical (136 full-conversion + the 4 rotation docs), .txt changes only one-page-rotated-180-degrees, t02_position FAIL->PASS. Not l |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **189** (88.7%) |
| Failing at least one check | **24** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `47_mA-02` | .docx blast radius of the uprightIfPageIsUpsideDown  | 15:19 | - | - |
| `47_mB-02` | true size of 47_margins on the CURRENT engine: re-re | 15:19 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 15:17 → running · 31 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 15 |
| Longest silence | **26.6 min** — from 15:19:03, after `deployed 2 agents, working my own angle: 47_margins .docx anchor` |
| Silences over 2 min | 2 |
| Obstacles | 1 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **0 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **29 min** | `####################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Land the pBdr rule replacement: FINDINGS/RULES-PBDR-IMPLEMENTATION.md, first statement of DocxWriter.shape() at line 2772 (return before line 2779), carrying the ctx.flowY = s.topPt update. Screen 32_stroke_lines first, then the full corpus pass. The finding predicts 124 documents cleared among the 144 LibreOffice-only ones, and all 145 if the residual is only the footer rule.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
