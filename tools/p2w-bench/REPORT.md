# Fixer report - 2026-11-28 02:24

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 02:24 → running IST · 2 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8477** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **534** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - .txt age: measured 6.5 h ago vs nothing re-measures it on a schedule |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **46** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (65 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

> **The gate was the work, and it is now honest.** For the last several runs `regress.py --check`
> refused every commit with one line:
>
> ```
> ENGINE CHANGED (docx): table measured on d28ca7516c3f9165, the tree is a05b20eb05fe0fc8
> An unmeasured change is not a pass. Re-measure, then --stamp.
> ```
>
> That was true and nobody had acted on it: `benchmarks/RANKING.csv` described an engine two
> commits behind the tree, so no fixer could land anything, and no fixer could see it either.
> `measure_gate.py` said NOT READY for the same reason.
>
> This run re-measured the corpus on the tree the repository actually has: `p2w.py --budget 250`
> called repeatedly, resumable, 213/213 scored (1 exempt, `416_many_tiny_pages`). The table is
> committed and the engine is stamped. `regress.py --check` now reads the tree instead of refusing
> to look at it.
>
> **What that cost, stated plainly.** The table it replaced was 82 documents optimistic. On the tree:
>
> | document | table said (d28ca751) | measured on the tree (a05b20eb) |
> |:--|--:|--:|
> | `table-with-no-header-row` | 0.61 | **47.48** |
> | `boq-tender-bill-of-quantities` | 0.62 | **41.95** |
> | `electricity-bill` | 1.33 | **36.78** |
> | `very-long-single-column-table` | 2.38 | **41.14** |
> | `balance-sheet-and-profit-loss` | 0.21 | **36.69** |
>
> Mean 3.71 → 7.68, documents at zero 76 → 49, 73 of 212 worse than the 15 Nov baseline. The
> regression is real, it is in the tree, and it was invisible because the only table anyone read
> was measured on code that no longer exists.
>
> **The lead this points at, and why it is a lead and not a fix.** The previous run reported
> `ROW_RUNG_UNDER_TW = 0` taking `table-with-no-header-row` 47.48 → 0.61 in LibreOffice. Those two
> numbers are the tree's measurement (47.48, measured here) and the *old table's* value (0.61,
> measured on d28ca751). So either the rung is exactly the difference between the two engines, or
> that run read a stale table as its own after-column. Both readings make the rung
> (`DocxWriter.java:54`, introduced in `8fb4f503`) the prime suspect for the largest regression in
> the corpus, and neither is proved. The A/B on the current engine is the next run's first
> attempt: convert with `ROW_RUNG_UNDER_TW = 0`, score, and compare against this committed table,
> not against a remembered one.
>
> I did not run that A/B because the re-measure consumed the slot: 213 documents at 5.9 s/document
> is 21 minutes of measurement after a cold-pod install, and it is the prerequisite for *any*
> change being landable. Recorded as `18_displacement` attempt 119, outcome `lead`.

## The txt

| | |
|:--|:--|
| Measured | **6.5 h ago** - nothing re-measures this on a schedule; run `txt_gate.py --score 60` |
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
| Slot window | 02:24 → running · 2 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 10 |
| Longest silence | **2.1 min** — from 02:25:03, after `relay: reading last report and gaps` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **2 min** | `######################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
