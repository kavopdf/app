# Fixer report - 2026-11-19 21:59

```
# P2W Fixer - Run Report

**19 Nov 2026 · slot 21:59 → running IST · 32 min**

> **report-2col-table-spanning-both-columns** improved — 16.10 → 0.76. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **13** — 1 attempt(s), 1 kept |
| Documents improved, round total | 58 of 213 |
| Corpus improvement vs 15 Nov | **+37.17%** — mean 6.15 → 3.86 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **31** of 213 — the rest are still off |
| Moved but still open | **27** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 22:30 | **kept** | 13/18 | recordBaseline(): a row the page drew as one baseline but emitted as two paragraphs put each continuation one hairline box low and the pitch solver never took it back, so the drift accumulated down th |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **166** (77.9%) |
| Failing at least one check | **47** |
| Most common failure | `t13_amount_columns` - 19 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 21:59 → running · 32 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 14 |
| Longest silence | **30.4 min** — from 22:00:25, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **0 min** | `#` |
| fix - diagnose and change the engine | **30 min** | `#####################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `salary-slip-factory-wages` | 18.09 | 0.73 | -17.36 |

## Next run

Re-run screen.py on content-present-partly-displaced: 13 documents moved but the class bar is a quarter of 18 = 5, so it is kept, not solved - the remaining open rows are 75_merged_header_cell_three_columns (w:vMerge, 1 of 18), 374_org_chart, payslip-label-left-amount-right and the ones the screen shows unchanged. Take the next-biggest class if this one is closer to done. Do not retry dropping fill-only rules from the Edge list.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
