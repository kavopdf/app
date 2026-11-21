# P2W Fixer - Run Report

**21 Nov 2026 · slot 11:18 → running IST · 16 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 0 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `-` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 11:16 | **partial** | 0/5 | 601's last lost word was the reference counting General twice; guard added to glyph_truth (211 docs A/B: 0 newly failing, 1 newly clean on the patched engine). The engine /AP walk that supplies the ot |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `32_sB-01` | why Google drops the rules LibreOffice draws, and wh | 11:34 | 06:04 | 0 min |
| `t02_A-01` | is the two-line 47_margins/t02 claim a real two-form | 11:34 | 06:04 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 11:18 → running · 16 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 18 |
| Longest silence | **13.8 min** — from 11:19:36, after `pending.py: reading the pending gate` |
| Silences over 2 min | 1 |
| Obstacles | 1 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **0 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **13 min** | `####################` |
| record - attempt, handoff, class rows | **1 min** | `##` |
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
