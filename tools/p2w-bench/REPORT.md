# Fixer report - 2026-11-18 16:25

```
# P2W Fixer — Run Report

**18 Nov 2026 · 15:58 → 16:24 IST · 25 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 3 of 212 |
| Corpus improvement vs 15 Nov | **+8.24%** — mean 6.15 → 5.64 |
| Regressions | **none** |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-partly-lost-and-displaced` |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Run time | 25 min |
| Tool beats | 24 |
| Longest silence | **12.8 min** — from 15:58:51, after `gaps.py: reading the timeline` |
| Silences over 2 min | 3 |
| Obstacles | 3 cleared · 0 need a human |

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `itr-computation-with-slab-table` | 68.82 | 50.80 | -18.02 |
| `newsletter-3col-header-footer` | 3.45 | 3.13 | -0.32 |

## Next run

The pending gate is EMPTY, so a new class may be taken - but do not take one on itr-computation-with-slab-table's account: its three remaining defects are named in FINDINGS/itr-slab-the-squeeze-is-not-the-defect-1645.md and HYPOTHESES.md, and the cheapest untested one is H3, the footer ROW's position in the row order (the page draws it last at 811.4, the engine emits it between the 816.4 and 834.8 rows). The class content-partly-lost-and-displaced still cannot be closed by attempt.py's bar - 6 of 7 documents are already under 5.0 - and that is the human decision in BLOCKERS 14:50. If a new class is taken, take the smallest OPEN one and screen before building.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
