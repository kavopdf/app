# Fixer report - 2026-11-22 08:16

```
# P2W Fixer - Run Report

**22 Nov 2026 · slot 08:16 → running IST · 12 min**

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
| Committed | **11** files in 1 commit(s) from `2ba798b` — 18_displacement-SPACER-REFUTED-0900-f1x.md, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, ROUND.json, RUN-LOG.md, RUN.json, SETTLED.md, TIMELINE.jsonl, TRACE.md, screen.py |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 08:26 | **reverted** | 1/16 | table-top spacer w:line -> w:before + hairline: 1 of 16 moved (68_journal 12.09->11.24), none worse. REFUTED as the cause: RANKING.csv gives 68_journal max_pt 8.64, not the -114.8 the lead assumed; af |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 08:16 → running · 12 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 14 |
| Longest silence | **3.5 min** — from 08:16:26, after `gaps.py: reading the timeline` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **3 min** | `######` |
| screen - the class's own documents | **0 min** | `#` |
| record - attempt, handoff, class rows | **1 min** | `##` |
| report - the report and the chain | **1 min** | `##` |
| other - not attributed to a tool | **5 min** | `##########` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Do not rebuild the table-top spacer and do not believe the -114.8 pt figure - both are refuted in SETTLED.md with the numbers: RANKING.csv gives 68_journal_wide_table_spanning max_pt 8.64, and the w:before build moved 1 of 16 by 0.85. The lead worth having is the uniform page offset: fourteen of the sixteen read median_pt 0.96 or 1.44, which at 150 DPI is two or three pixels out on EVERY line - one constant applied to the page, not sixteen constructs. Test it against the two em-offsets already measured and never tried here: the first baseline of a page sits 0.0565 em below the paper's top edge, and the first baseline of a cell 0.92 em below the row's top edge (REMAINING-DEFECTS.md). 71_invoice_space_aligned_no_rules is the exception - share@5 26.88, median_pt 3.84, no table spacer at all - and needs its own look. Also settled: screen.py was measuring NOTHING on a fresh pod (ENGINE_SRC frozen at import); it is fixed, so a screen that reports 0 of N measured should be treated as a tool failure, not as evidence.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
