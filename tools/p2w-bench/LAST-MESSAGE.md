# Fixer report - 2026-11-23 05:58

```
# P2W Fixer - Run Report

**23 Nov 2026 · slot 05:58 → 06:18 IST · 19 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 3 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **28**, out of the 190 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 06:11 | **lead** | 0/None | LO census: 7 docs are one check from clean in the measurable renderer and they are 7 distinct mechanisms. Controlled 3-variant experiment on balance-sheet-two-columns-of-figures: w:trHeight is inert o |
| 06:15 | **lead** | 0/None | Instrumented the row model at DocxWriter.java:6146 (P2W_DBG env, reverted, app/ clean). exactRows is TRUE on all four candidates and the per-row edges ARE used, so the uniform-average path is not the |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dresidual-census-01` | which current-engine documents fail 18_displacement, | 06:17 | 00:47 | 0 min |
| `18_dblast-radius-01` | the exact writer rule for w:trHeight/w:hRule, what t | 06:17 | 00:47 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 05:58 → 06:18 · 19 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 29 |
| Longest silence | **5.3 min** — from 06:01:27, after `attempt.py: recording an attempt` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 4 parked, with the evidence to re-open them |
| Still a wall | **`stage.py` calls the corpus measured, but most of it is not measured on the engine that is on HEAD.** `measu |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **10 min** | `############` |
| measure or build - a conversion, screen or compile writes no beacon | **5 min** | `#######` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **2 min** | `##` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

`18_displacement` - the row-0 construct is MEASURED AND DERIVED, and the fix is refused, not unproven. See
`FINDINGS/18_displacement-ROW0-TABLE-TOP-DERIVED-CLEARS-ONE-REGRESSES-ANOTHER-0740-relay.md`.

What is established: row 0 of a table is placed from `rowEdge[0] - 0.8 * firstPitch` (`DocxWriter:6403-6409`)
while the table's own top is `t.rowTopPt`; the gap is `0.8 * (firstPitch - lastPitch)` and is computable per
table. On `balance-sheet-two-columns-of-figures` it is **+3.52 pt** and the measured first-row error is
**+3.69 pt** - the same correction the 06:30 run found by tuning, now derived. Applying it takes that document
from **6 runs out of 94 to 0** (span 4.18 -> 0.89), i.e. 41/42 -> **42/42 in the measurable renderer**.

What kills it: `360_restaurant_menu` goes **share@5 34.43 -> 35.66** (reproduced on a fresh measure of the same
.docx, and 34.43 again from the reverted engine). `regress.py --check` refused the commit. Guarding the change
on `spacerTw > 0` does not separate them - `360` spends a spacer too.

Why, and the missing term: for `360` the pitch-derived edge (102.4) is RIGHT and the table's top (104.0) is
1.6 pt low; for `balance-sheet` the table's top (106.07) is RIGHT and the pitch-derived edge (102.55) is 3.5 pt
high. **The sign of the correct answer differs between two documents**, so no constant row-0 rule is right for
both. The deciding number is where the spacer's box **actually landed**, and nothing in the writer knows it:
the spacer computes a distance and never checks the result. That is D-26, and row 0 is only where it shows.

Cheapest next measurement: for both documents, print the rendered top edge of the table against `t.rowTopPt`
and against `flowTopPt + spacerTw/20`. If those agree on `360` and disagree on `balance-sheet`, the fix belongs
in the spacer's split (`spendable`, the `w:line` under-read, `squeeze`), not in the row model.

Also this run, for the next one: the +/-9.52 / -9.06 whole-block pair that the 06:30 run left open is **NOT**
the `lastPitch` construct - both tables are inert under it (`shift = 0.0` on `71`, and
`table-inside-two-column-page` has no whitespace table at all, its table is ruled). On `71` the gap before the
table is `extraAbs = -1.50`, so no spacer is written and the table simply continues the flow 9.52 pt below
where the page drew it. That is a flow-position defect, not a table-arithmetic one.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
