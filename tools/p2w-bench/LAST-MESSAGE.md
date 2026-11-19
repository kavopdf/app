# P2W Fixer - Run Report

**19 Nov 2026 · slot 21:59 → 22:35 IST · 36 min**

> **report-2col-table-spanning-both-columns** improved — 16.10 → 0.76. Corpus ratchet clean across 213 documents.

## What the tables cannot show

**The gate was the defect, and it had been failing every fixer run since 11:55.** Measuring the
whole corpus with origin/main's engine and no change at all put 203 of 213 documents back exactly
where the committed table had them and ten higher. Those ten are the rows the 11:55 justified-line
commit touched; the table kept their older numbers, and `regress.py` compares every later commit
against that table, so every run since then has been shown ten phantom regressions and no engine
change could land. This run published the table the engine actually produces (commit `c6d8cdf`,
no engine change in it) and the fix then landed.

**Three versions of the fix were needed, and each one is a number.** The mechanism is that a row
the page drew as one baseline is emitted as two paragraphs, and the second lands one hairline box
low with nothing to take it back - 0.4554 pt per split row, +5.85 pt by y=421 on
`bank-statement-horizontal-rules-only`. The first version broke a drop cap page (1.49 -> 4.28), the
second counted one continuation of two on a three-box row, the third broke a question paper
(0.11 -> 19.59) and a two-column page (0.80 -> 7.82) by treating a sidebar label 0.85 pt off a
body line as that line's continuation. What finally held is exactness - 0.2 pt - not a fraction
of the em.

**w:vMerge is real but it is not this class.** `spanR` is computed at `PdfToWord:7950` and read by
nothing, so a vertically merged source cell is written as three `w:gridSpan` and no `w:vMerge`.
Subagent B measured all eighteen documents in the class and only `75_merged_header_cell_three_columns`
has such a cell: the feature cannot close this class and is not what moves these numbers. It is
still the right next piece of engine work, and the finding says exactly where it goes.

**416_many_tiny_pages is EXEMPT and its row was not re-measured this run** - it carries the value
the committed table had, which is the same value the previous run's hand measurement produced.

## Progress

| | |
|:--|:--|
| Documents improved this run | **13** — 2 attempt(s), 2 kept |
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
| 22:32 | **kept** | 13/18 | recordBaseline(): a split row's second paragraph landed one hairline box low and the pitch solver measured every later row from there, so the drift accumulated (0.4554 pt per row). Whole corpus 213 me |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **166** (77.9%) |
| Failing at least one check | **47** |
| Most common failure | `t13_amount_columns` - 19 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `contA-04` | bank-statement-horizontal-rules-only: which code pat | 22:31 | 17:05 | 4 min |
| `contB-04` | blast radius of w:vMerge across the 18 documents in  | 22:31 | 17:05 | 4 min |

## Timing

| | |
|:--|:--|
| Slot window | 21:59 → 22:35 · 36 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 31 |
| Longest silence | **30.4 min** — from 22:00:25, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **0 min** | `#` |
| fix - diagnose and change the engine | **30 min** | `##################` |
| record - attempt, handoff, class rows | **4 min** | `###` |
| report - the report and the chain | **0 min** | `#` |
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
