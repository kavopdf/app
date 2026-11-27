# Fixer report - 2026-11-28 00:58

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 00:58 → running IST · 1h 15m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8477** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **534** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; .txt age: measured 6.2 h ago vs nothing re-measures it on a schedule |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **46** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (66 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 02:13 | **lead** | None/None | gate unblocked instead: full 213/213 re-measure on engine a05b20eb committed and stamped; the table it replaced described d28ca751 and was 82 documents optimistic - table-with-no-header-row 0.61 vs 47 |


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

## The txt

| | |
|:--|:--|
| Measured | **6.2 h ago** - nothing re-measures this on a schedule; run `txt_gate.py --score 60` |
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
| Slot window | 00:58 → running · 1h 15m |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 124 |
| Longest silence | **38.8 min** — from 00:58:41, after `pending.py: reading the pending gate` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **1 min** | `#` |
| fix - diagnose and change the engine | **4 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **1h 04m** | `###################` |
| other - not attributed to a tool | **4 min** | `#` |

The unattributed row is 4 distinct beat(s) that matched no phase. They said:

- `measuring corpus on HEAD engine to test whether the gate can be satisfied in a slot`
- `measuring corpus on HEAD engine: 72/213 done, ~5.9s/doc`
- `measuring corpus on HEAD engine: 169/213, 44 left`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

**FIRST ATTEMPT NEXT RUN: the rung A/B on the committed table.** `ROW_RUNG_UNDER_TW`
(`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:54`, from `8fb4f503`) set to 0,
`P2W_ENGINE_SRC` pointed at a clone carrying only that line, converted into its own output
directory, scored, and diffed document by document against the table this run committed. If it
restores the five documents in the table above without costing the 82 that are already open, it
is the largest single win available. Prove it in Google on `table-with-no-header-row` and on one
control that currently passes `18_displacement`, before committing.

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 39 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.

## Why nothing moved, and what did

**The gate was the work, and it is now honest.** For the last several runs `regress.py --check`
refused every commit with one line:

```
ENGINE CHANGED (docx): table measured on d28ca7516c3f9165, the tree is a05b20eb05fe0fc8
An unmeasured change is not a pass. Re-measure, then --stamp.
```

That was true and nobody had acted on it: `benchmarks/RANKING.csv` described an engine two
commits behind the tree, so no fixer could land anything, and no fixer could see it either.
`measure_gate.py` said NOT READY for the same reason.

This run re-measured the corpus on the tree the repository actually has: `p2w.py --budget 250`
called repeatedly, resumable, 213/213 scored (1 exempt, `416_many_tiny_pages`). The table is
committed and the engine is stamped. `regress.py --check` now reads the tree instead of refusing
to look at it.

**What that cost, stated plainly.** The table it replaced was 82 documents optimistic. On the tree:

| document | table said (d28ca751) | measured on the tree (a05b20eb) |
|:--|--:|--:|
| `table-with-no-header-row` | 0.61 | **47.48** |
| `boq-tender-bill-of-quantities` | 0.62 | **41.95** |
| `electricity-bill` | 1.33 | **36.78** |
| `very-long-single-column-table` | 2.38 | **41.14** |
| `balance-sheet-and-profit-loss` | 0.21 | **36.69** |

Mean 3.71 → 7.68, documents at zero 76 → 49, 73 of 212 worse than the 15 Nov baseline. The
regression is real, it is in the tree, and it was invisible because the only table anyone read
was measured on code that no longer exists.

**The lead this points at, and why it is a lead and not a fix.** The previous run reported
`ROW_RUNG_UNDER_TW = 0` taking `table-with-no-header-row` 47.48 → 0.61 in LibreOffice. Those two
numbers are the tree's measurement (47.48, measured here) and the *old table's* value (0.61,
measured on d28ca751). So either the rung is exactly the difference between the two engines, or
that run read a stale table as its own after-column. Both readings make the rung
(`DocxWriter.java:54`, introduced in `8fb4f503`) the prime suspect for the largest regression in
the corpus, and neither is proved. The A/B on the current engine is the next run's first
attempt: convert with `ROW_RUNG_UNDER_TW = 0`, score, and compare against this committed table,
not against a remembered one.

I did not run that A/B because the re-measure consumed the slot: 213 documents at 5.9 s/document
is 21 minutes of measurement after a cold-pod install, and it is the prerequisite for *any*
change being landable. Recorded as `18_displacement` attempt 119, outcome `lead`.

## What the next run should not have to rediscover

* `p2w.py --budget N` is resumable and its progress survives the call being killed at the ceiling.
  213 documents cost six calls. It is not a four-hour job; the 73 s/document figure in older
  findings is wrong by an order of magnitude once the corpus cache is warm.
* The corpus cache must be warm before measuring (`corpus-slice.py`, or `install-gate.sh`), or the
  first call spends its budget converting.
* `regress.py --stamp` must run *after* `RANKING.csv` is committed, not before: `_newer_than_engine`
  compares commit times, so a stamp attempted on an uncommitted table is refused by design.
