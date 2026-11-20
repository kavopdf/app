# Fixer report - 2026-11-20 05:51

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 05:51 → running IST · 30 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.44%** — mean 6.15 → 3.72 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **32** of 213 — the rest are still off |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` |
| Committed | **14** files in 1 commit(s) from `17bc575` — ...-displaced-rules-are-flow-neutral-065000-f1x.md, ATTEMPTS.json, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, LAST-MESSAGE.md, REPORT.md, ROUND.json, RUN-HISTORY.json, RUN-LOG.md, RUN.json, TIMELINE.jsonl, TRACE.md,  |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 05:53 | **reverted** | 0/23 | attempt 12: rules flush-by-top re-applied + ctx.flowY residual test (flowY left at s.topPt vs carrier-bottom) on 18_centred |
| 06:20 | **reverted** | 0/23 | attempt 13: rule as the FOLLOWING paragraph's w:top border, found by a pre-pass, no reordering, no extra paragraph - flow-neutral, measures exactly baseline on 8/8 documents (18_centred 0.00, bank-sta |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **167** (78.4%) |
| Failing at least one check | **46** |
| Most common failure | `t13_amount_columns` - 18 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 05:51 → running · 30 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **27.2 min** — from 05:53:11, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 1 need a human |
| Still a wall | The fixer run that claimed the slot at 05:17:58 IST (23:47:58 UTC) beat until 05:18:43 IST, committed `6dfe946 |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **27 min** | `####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FINDINGS/content-present-partly-displaced-rules-are-flow-neutral-065000-f1x.md BEFORE TOUCHING THE RULE CLASS. Two handoff claims are now measured FALSE: (1) the flush-by-top precondition is a regression, not a precondition - with the border path OFF it takes bank-statement 0.10 -> 17.07 and gst-invoice 0.38 -> 15.13, because every shape moved into the flow charges ~9.6 pt; (2) the residual on 18_displacement was never the gap or the flowY bookkeeping - a carrier paragraph costs 9.6 pt in LibreOffice whatever it contains (measured four ways), which is the whole of 0.00 -> 77.01. A flow-neutral construct exists and is in FINDINGS/rules-top-border-FLOW-NEUTRAL-065000-f1x.patch: a pre-pass hands each rule to the paragraph that follows it as a w:top border, the gap becomes w:before and the rule-to-text distance becomes w:space, nothing is reordered and no paragraph is added. It measures EXACTLY baseline on all 8 documents tried (18_centred 0.00, 411 0.00, 62 0.00, bank-statement 0.10, gst-invoice 0.38, mobile-bill 1.55, 315 1.91, 64 3.46) - and places pBdr=0, because its own safety guards decline every rule it could reach. Where a border IS placed, 18_centred goes 0.00 -> 0.53. THAT is the wall and it is not an engine bug: regress.py scores share@5 on a LibreOffice render, LibreOffice draws the floating drawing exactly, and a border can never be pixel-identical - so a fix Google needs is always a small LibreOffice regression, and the brief forbids landing one. DO NOT start another rule-class attempt until a human answers: gate this class in Google (32_stroke_lines / 05_chars_extra on the Google result), declare the class out of scope, or authorise a stated tolerance. Spend the next slot on a class the gate can see.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
