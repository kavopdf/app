# Fixer report - 2026-11-18 16:18

```
# P2W Fixer — Run Report

**18 Nov 2026 · 15:58 → running IST · 19 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
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
| Run time | 19 min |
| Tool beats | 15 |
| Longest silence | **12.8 min** — from 15:58:51, after `gaps.py: reading the timeline` |
| Silences over 2 min | 2 |
| Obstacles | 3 cleared · 0 need a human |

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `itr-computation-with-slab-table` | 68.82 | 50.80 | -18.02 |
| `newsletter-3col-header-footer` | 3.45 | 3.13 | -0.32 |

## Next run

Do NOT re-open the squeeze or the anchor rule on itr-computation-with-slab-table - both are measured and refuted (FINDINGS/itr-slab-the-squeeze-is-not-the-defect-1645.md). The largest single term there is the cell baseline: cellBeforeTw's fallback is LINE_BASE*(rowLineTw - cellBoxTw) and rowLineTw is the cell's LINE capped at 200 twips, not the row's pitch, so in a tall row (18.4 pt) every cell lands 5.2 pt high. Screen that on the table documents that already score well (320_balance_sheet_statutory, 404_sudoku_grid, 42_table_coloured_header_alternating_rows) BEFORE touching it - it changes every table on the corpus. Second, and cheaper: the class still needs the human decision in BLOCKERS 14:50 (6 of 7 documents are already under 5.0; attempt.py's bar cannot close it). Third: measure_doc_chunked reports pages_done=160 pages_total=300 beside a complete result and pages_compared=1200 - check its accumulator before the next 300-page document.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
