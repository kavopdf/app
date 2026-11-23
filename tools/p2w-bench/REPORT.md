# Fixer report - 2026-11-24 02:34

```
# P2W Fixer - Run Report

**24 Nov 2026 · slot 02:34 → running IST · 1 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
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
| 02:34 | **lead** | 0/13 | Four documents converted on this tree; unspendable spacers counted in word/document.xml and matched one-for-one to the four live Google steps the previous slot recorded (14.35 vs -13.0, 9.72/5.02/4.86 |

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
| `18_dA-03` | audit the pending gate: which of the 21 closable ite | 02:35 | - | - |
| `18_dB-01` | table block-top gap and per-row height in DocxWriter | 02:35 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 02:34 → running · 1 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 8 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| report - the report and the chain | **0 min** | `#############` |
| other - not attributed to a tool | **0 min** | `#########` |
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
