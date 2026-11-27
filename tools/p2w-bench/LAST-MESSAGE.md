The gate is not blocked by the rung. It is blocked by 82 documents worse than the 15 Nov baseline, and the rung is 28 of them — the lead the last two runs discarded was judged against the wrong table.

Both prior runs measured `ROW_RUNG_UNDER_TW = 0` against `benchmarks/RANKING.csv`, which is the rung=10 tree's own output. Against `RANKING-BASELINE.csv` — the 15 Nov state the gate actually compares to — it is a net improvement: **57 documents worse than baseline instead of 82**, and more better, at the price of exactly one document newly worse (`marksheet-subject-left-marks-right` 4.55 -> 5.21, where rung=10 gives 2.15). I re-derived the rung=0 stamp `b648594972a7682b` by hashing the tree with only that constant changed. It still does not unblock the gate — 57 is a refusal — but the remaining 57 are five constructs, not one constant, and the largest coherent one is **stamps: ten documents**, worst `03_stamp_vertical_90deg` 16.98 -> 34.38.

The txt half can still be committed today and is **three documents from the charter's 99%**. Two of those three are one construct: the two `Account_Opening_Form` documents carry 127 U+FFFD where their source carries none — ligature glyphs the engine cannot name, not a decode fault.

# P2W Fixer - Run Report

**28 Nov 2026 · slot 02:24 → running IST · 19 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8477** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **534** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; kept change: 1 code commit(s) in this window, first: relay 28nov 02:24: the gate is 84 regressions, n vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change |
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
| Working on | `63_table_rows` - taken from the pending list (64 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `63_table_rows` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 02:43 | **lead** | None/None | Gate state measured: regress.py --check refuses on 84 docx regressions vs the 15 Nov baseline (fingerprint refusal already cleared at 00:58 - different message, same tool). Judged the rung on the gate |

## Why nothing moved, in this run's own words

> Nothing was kept because the commit gate refuses every engine change, and this run measured what it
> refuses on rather than working around it.
>
> `regress.py --check` returns:
>
>     docx: 84 REGRESSION(S)
>     REFUSED. This commit would land a regression or an unmeasured engine.
>
> The 00:58 report calls the gate "unblocked". That is true of one of the tool's two refusals. It cleared
> the fingerprint refusal — the table now names the engine it was measured on — and the regression refusal,
> which is a different message from the same tool, was never cleared and is live now. No engine change can
> land until it is.
>
> The run's real work was to test the lead the last two reports discarded. Both judged `ROW_RUNG_UNDER_TW = 0`
> by comparing it against `benchmarks/RANKING.csv`, which is the rung=10 tree's own output; that comparison
> can only ever report that rung=0 is worse than rung=10, which is not the gate's question. Against
> `RANKING-BASELINE.csv`, the 15 Nov state the gate actually compares to, rung=0 is a net improvement:
> 57 documents worse than baseline instead of 84, 64 better instead of 47, and exactly one document newly
> worse (`marksheet-subject-left-marks-right`, 4.55 → 5.21, where rung=10 gives 2.15). The rung=0 table's
> stamp was re-derived by hashing the tree with only that constant changed, so the table is a measurement of
> the tree and not of some other state.
>
> That still does not unblock the gate — 57 is a refusal — but it changes what the next run should build:
> the remaining 57 are five constructs, not one constant, and the largest coherent one is stamps, ten
> documents whose names all carry `stamp`. A per-row rung would keep the one document the constant earns
> and release the 28 it costs.
>
> The run did not get to a build. The pod was warm but 18 documents short of a converted corpus, and
> diagnosing the stamp cluster properly is more than the slot allowed after the gate measurement. It stopped
> at the measurement and recorded it, rather than starting a patch it could not prove.

### The run before this one said

>
>
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

Accounts share 17% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **2 min ago** |
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
| Slot window | 02:24 → running · 19 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 32 |
| Longest silence | **7.0 min** — from 02:27:39, after `relay: checking the gate itself` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **2 min** | `###` |
| build - compiling the engine | **4 min** | `#####` |
| measure or build - a conversion, screen or compile writes no beacon | **7 min** | `########` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **3 min** | `####` |

The unattributed row is 4 distinct beat(s) that matched no phase. They said:

- `relay: checking the gate itself`
- `relay: warming pod (corpus+jdk+engine)`
- `relay: writing report`
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
