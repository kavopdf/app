# Fixer report - 2026-11-18 18:00

```
# P2W Fixer — Run Report

**18 Nov 2026 · slot 18:00 → 19:08 IST · 1h 08m**

> **22 document(s)** improved this run, but the run did not commit benchmarks/RANKING.csv, so the report cannot name them.

## Progress

| | |
|:--|:--|
| Documents improved this run | **22** — 1 attempt(s), 1 kept |
| Documents improved, round total | 36 of 212 |
| Corpus improvement vs 15 Nov | **+27.52%** — mean 6.15 → 4.46 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| **Fixed to 99%** | **20** of 212 — the rest are still off |
| Moved but still open | **16** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-missing-nothing-in-its-place` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 19:07 | **kept** | 22/29 | per-row separator stroke: table interior rules whose weight/colour differs from the table's insideH are emitted as per-cell tcBorders bottom instead of collapsing into one border. salary-slip-factory- |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **149** (70.0%) |
| Failing at least one check | **64** |
| Most common failure | `t13_amount_columns` - 30 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Session | 18:00 → 19:08 · **1h 08m** |
| Slot window | 18:00 → 19:08 · 1h 08m |
| Before the claim | 0 min - pod setup, cloning and retries |
| Tool beats | 20 |
| Longest silence | **66.9 min** — from 18:00:10, after `gaps.py: reading the timeline` |
| Silences over 2 min | 1 |
| Obstacles | 1 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **1h 06m** | `######################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `salary-slip-factory-wages` | 18.09 | 0.73 | -17.36 |
| `mobile-bill` | 18.48 | 1.55 | -16.93 |
| `two-tables-stacked-with-no-gap` | 17.20 | 0.77 | -16.43 |

## Next run

Take the next class, content-partly-lost (11 open). The class-wide screen now covers the whole corpus in about 30 minutes across 6 calls via screen.py --docs with the full RANKING.csv document list - p2w.py --budget does NOT resume and cannot finish a corpus pass inside the 300 s cap, so use screen.py --docs. Do not retry run-size-from-sizePt-not-Tf, the anchor rule, the cell-baseline fallback, or the row separator stroke - the last is now implemented.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
