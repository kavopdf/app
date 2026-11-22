# Fixer report - 2026-11-22 08:56

```
# P2W Fixer - Run Report

**22 Nov 2026 · slot 08:56 → running IST · 24 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 09:19 | **lead** | 6/16 | Table spacer as w:before + hairline (DocxWriter 5872-5875) and the 2880->4320 twip cap (5852,5866). Measured in Google on all 16 solo-18 documents: 6 became 42/42 (16_right_aligned, 22_invoice, 29_dot |

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
| `18_dA-04` | which clause of the check can fire on a 1.44-2.40 pt | 09:20 | - | - |
| `18_dB-03` | do 05/32/59/18 share ONE engine construct in the emi | 09:20 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 08:56 → running · 24 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 12 |
| Longest silence | **14.1 min** — from 09:05:17, after `read findings; C2 spacer probe is the lead` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **14 min** | `#############` |
| measure or build - a conversion, screen or compile writes no beacon | **8 min** | `########` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Land BOTH constructs in one build: (1) the table spacer as w:before + hairline w:line=1 exact at DocxWriter.java:5872-5875, and (2) the row height scaled by 0.9634 at the trHeight emitter (line 6228 max(rowTwHere,rowLineTw)) so Google's atLeast growth cannot exceed the source pitch - 0.9634 is measured this slot (19.10/18.40 renders), NOT the 0.9785 in the 08:20 finding. Raise the spacer cap 2880->4320 (5852,5866); only 68_journal reaches it and its real gap is 2961 twips. Do not use hRule=exact - Google's cell content is 19.10 and exact would clip. Then COUNT the blast radius before committing: the spacer change touches every corpus document with a table spacer and only the 16 that fail 18 were measured; render the currently-clean ones that have one. Do NOT screen this class with screen.py - it renders in soffice, which honours w:line as a length and cannot see either state.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
