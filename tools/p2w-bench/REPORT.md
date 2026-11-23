# Fixer report - 2026-11-24 00:56

```
# P2W Fixer - Run Report

**24 Nov 2026 · slot 02:08 → 02:09 IST · 1h 13m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **27** of the **123** re-measured on this engine - **67** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **2** run(s) for the 67 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 01:42 | **lead** | 0/213 | t12's 21 invented words on 600 split into 3 faults; source reader now sees printing annotations (21->20, blast radius 1 doc, no verdict moved); remaining 20 are the converter duplicating FreeText text |
| 01:43 | **lead** | 0/213 | 23 page_count_refused docs: 21 render the RIGHT page count in LibreOffice and one too many in Google (proxy is blind); the 350 inline-picture construct is REFUTED - 0 wp:inline across all 23, the engi |
| 02:08 | **lead** | 0/13 | Four live Google round trips on the 13 sole-failure documents give the distances this class has never had: med_dy -2.8 / -3.0 / -6.7 / -13.0 pt, worst_dy 5.4 / 4.9 / 10.0 / 28.2, med_dx -0.2..+0.2, ba |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-02` | which single failing Google check, if fixed, makes t | 02:07 | - | not recorded |
| `04_cB-02` | is the missing-char multiset fully explained by anch | 02:07 | - | not recorded |

## Timing

| | |
|:--|:--|
| Slot window | 02:08 → 02:09 · 1h 13m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 64 |
| Longest silence | **24.4 min** — from 00:56:37, after `pending.py: reading the pending gate` |
| Silences over 2 min | 8 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **3 min** | `#` |
| fix - diagnose and change the engine | **3 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **34 min** | `##########` |
| record - attempt, handoff, class rows | **4 min** | `#` |
| report - the report and the chain | **14 min** | `####` |
| other - not attributed to a tool | **13 min** | `####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

NEXT RUN: (1) 18_displacement is measured and staged - the pair is (first-row cell w:before carries the table gap) + (w:trHeight declared less by the same per-row amount), and 362_price_list_dense is the falsifier because it has a ramp and no step. (2) The 5 ratchet items are very likely stale: benchmarks/STATE.json, RANKING.csv and the engine last changed in the SAME commit b7699196, and both regress.py --check and measure_gate.py pass on this tree (212/212 scored, engine docx == tree). Do not stamp them without checking - a corpus pass that covered them is what closes them, and the honest close is one corpus pass, not five stamps. (3) The 80 remaining pending items are mostly [blocker] rows that say 'this needs a decision, not a patch'.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
