# Fixer report - 2026-11-19 16:11

```
# P2W Fixer — Run Report

**19 Nov 2026 · slot 16:11 → running IST · 47 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 37 of 212 |
| Corpus improvement vs 15 Nov | **+29.90%** — mean 6.15 → 4.31 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **21** of 212 — the rest are still off |
| Moved but still open | **16** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-partly-lost` |
| Committed | **24** files in 2 commit(s) from `0a9de90` — ARCHIVE.json, ATTEMPTS.json, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, HYPOTHESES.md, HYPOTHESES.md.head, PATCH-justified-lines-spacing.patch, REPORT.md, ROUND.json, RUN-LOG.md, RUN.json, TIMELINE.jsonl, TRACE.md, T |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 16:58 | **partial** | 5/10 | justified lines emitted left-aligned: model carries the measured shortfall (Box.stretchPt/Line.stretchPt), writer emits w:spacing in flowFromBox and lineParagraph. SCREEN PASS 5 of 10 better, 0 worse |

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
| Slot window | 16:11 → running · 47 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 20 |
| Longest silence | **17.3 min** — from 16:11:34, after `pending.py: reading the pending gate` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **14 min** | `#######` |
| measure or build - a conversion, screen or compile writes no beacon | **31 min** | `###############` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `salary-slip-factory-wages` | 18.09 | 0.73 | -17.36 |
| `mobile-bill` | 18.48 | 1.55 | -16.93 |

## Next run

Apply patches/PATCH-justified-lines-spacing.patch, build, re-screen content-partly-lost (expect 5 better 0 worse), then spend the rest of the run on the corpus pass - screen.py --docs with every document in RANKING.csv, 22-24 per call in about nine calls, then write RANKING.csv and STATE.json from screen-out/dist/*.json. scope.py says BOTH: re-score the .txt too. Do not retry the two mistakes recorded in FINDINGS/content-partly-lost-JUSTIFY-170800-fixer.md - the 0.06 em spacing cap and the word-gap test that cannot see a space glyph.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
