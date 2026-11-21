# Fixer report - 2026-11-21 12:12

```
# P2W Fixer - Run Report

**21 Nov 2026 · slot 12:12 → running IST · 32 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 0 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `-` |
| Committed | **14** files in 2 commit(s) from `6347cd3` — ...-PBDR-IMPLEMENTATION-SUPERSEDED-124500-relay.md, ...troke_lines-A-pbdr-verification-124000-relay.md, ...troke_lines-B-rule-flow-neutral-124500-relay.md, BLOCKERS.md, HANDOFF.json, HANDOFF.md, ROTATION.json, ROUND.json |

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
| `32_sA-01` | Verify the pBdr implementation in FINDINGS/RULES-PBD | 12:14 | 07:10 | 26 min |
| `32_sB-02` | From the source PDFs, count horizontal hairline rule | 12:14 | 07:10 | 26 min |

## Timing

| | |
|:--|:--|
| Slot window | 12:12 → running · 32 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 14 |
| Longest silence | **24.6 min** — from 12:14:42, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 2 |
| Obstacles | 1 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | `_done()` in gverify.py counts a document as measured only when its result carries the CURRENT engine stamp (` |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **0 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **24 min** | `#################` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **5 min** | `####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
