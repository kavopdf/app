# Fixer report - 2026-11-28 01:27

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 01:27 → running IST · 0 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8477** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **534** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - run window: RUN.json says this run began at 01:27 vs TIMELINE.jsonl records the claim at 00:18, so the window was reset and the duration is short |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **46** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (65 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 01:27 | **reverted** | 0/0 | ROW_RUNG_UNDER_TW=0 reproduces four published table values digit for digit (table-with-no-header-row 47.48->0.61, boq 0.62, mobile-bill 1.55, electricity-bill 1.33) but the full 213-document measure i |

## Why nothing moved, in this run's own words

> The 27 Nov run's claim was that `ROW_RUNG_UNDER_TW` is one constant whose deletion restores 84-96 documents. The four documents it named do come back, digit for digit, and I reproduced that on my own build. But the full corpus says the constant is a per-document trade, not a defect: 4 documents better, **63 worse**, 146 unchanged, measured on one engine, one conversion pass, 213 documents scored.
>
> The worst case is a dense two-column price list: `price-list-2col-dense-right-aligned` goes 2.69 -> 27.89. I converted that one document again on its own and scored it again, and got 27.89 - the regression is in the render, not in the table.
>
> The reason is mechanical. The rung subtracts a fixed 10 twips from every row that has 5 pt of foot room. On a long ruled table whose source pitch equals the page pitch, that subtraction is pure accumulated error and removing it is right. On a dense price list the rows are shorter than the pitch and the shortfall is what keeps each row's ink inside its own band; removing it lays every row low and the ink crosses the rules. One constant cannot be right for both. The correct fix computes the per-row difference between the source pitch and the room that row's own text needs - a real change, not a one-line edit, and the next run's build.
>
> So the change was reverted and nothing went into the engine. The measured table for the whole corpus at rung=0 is committed beside the finding so the next run does not pay the hour again, and the falsifier the previous run wrote for itself has fired and is recorded.

### The run before this one said

> The 84-96 table regressions are one constant, and it is proved on four documents but not landed.
>
> `ROW_RUNG_UNDER_TW` (`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:54`) is declared 10 and
> applied once per row at `:6601`, gated on `footRoom` (`:6591-6599`), which passes on any row with 5 pt
> below its lowest baseline - most rows of a roomy ruled table. Every such row's `w:trHeight` is declared
> 10 twips (0.5 pt) short of the page pitch, and the shortfall is not absorbed at that row: the next row
> starts from the short declaration, so the displacement accumulates as a ramp in row index, about 0.5*n
> pt. On `table-with-no-header-row` (26 rows) that is up to 13 pt at the foot. That is why the longest
> tables lost the most and documents with no ruled table lost nothing.
>
> Measured on my own clone, my own JDK, my own conversion and scoring, one document per JVM, one class
> recompiled between the two columns: with the rung at 0, `table-with-no-header-row` 47.48 -> 0.61,
> `boq-tender-bill-of-quantities` 0.62, `electricity-bill` 1.33, `mobile-bill` 1.55 - every one of them
> its published RANKING.csv value digit for digit, `share1` and `max_pt` included.
>
> Not landed because the full-corpus measurement the commit gate requires did not fit the slot: there is
> no JDK on the pod, so the first 40 minutes went on fetching one and getting the engine to compile at
> all, and `corpus-convert.py` then needed about 5 minutes for 214 documents. The one-line change and the
> full instructions are in `FINDINGS/table-row-placement-IS-THE-RUNG-PROVEN-27NOV-relay.md`.
>
>
>
> Accounts share 2% of their significant words - a different account (the cut is 50%).

Accounts share 13% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **5.5 h ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 01:27 → running · 0 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 7 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| report - the report and the chain | **0 min** | `######################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
