# Fixer report - 2026-11-26 15:50

```
# P2W Fixer - Run Report

**26 Nov 2026 · slot 15:50 → running IST · 27 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **91** of 94 (96.8%) on 2 documents |
| Check-instances still failing | **3** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **48** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - run window: RUN.json says this run began at 15:50 vs TIMELINE.jsonl records the claim at 15:10, so the window was reset and the duration is short; subagents: 2 deployed vs no FINDINGS file for 18_dB-01 |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+40.32%** — mean 6.15 → 3.67 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **0** of the **2** re-measured on this engine - **205** of the 207 scored are still on an older engine, and **42** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 205 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **6** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (47 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 15:50 | **kept** | 2/None | page-top gap moved from w:before into w:pgMar w:top; Google 42/47->46/47 (bs5) and 42/47->45/47 (gst-invoice), 7 check-instances cleared, no document worse |

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

>
>
> Nothing moved because this run spent its first 40 minutes making the pod able to measure at all, and
> then spent the rest proving that the class it was about to work cannot be worked the way every earlier
> run has worked it.
>
> The pod cost is real and worth stating: `install-gate.sh` was killed at 300 s because `pod-prep.sh`
> fetches 213 corpus PDFs, a JDK and four jars and then compiles the engine, and none of that is cached
> on a cold pod. Re-running it four times finished the corpus; the gate then passed first time
> (`regress.py --check` silent, `measure_gate.py` READY, engine a4de7df896875a39). So the gate was never
> the obstacle this run - the cold pod was, and that is a known, priced 25-30 minutes.
>
> The class was `18_displacement`: 113 of 207 documents fail it, and `classpick.py --leverage` values it
> at 51.9 CLEAN documents, five times the next check. The obvious theory was sitting in the repo as a
> column: `benchmarks/DISP-TABLE.csv` labels 75 documents `attribution=table-row`, i.e. rows growing
> slightly and the drift accumulating down the page. It has never been tested against a Google render -
> its `google_per_row_growth_pt` column is empty for all 213 rows.
>
> It is false. On the 207 committed Google results, median displacement has a *negative* slope against
> table row count (-0.108, r² = 0.00) and worst displacement has a slope of 0.518 pt/row at r² = 0.01.
> Nine rows or nineteen, the page is displaced by the same amount. The row counts themselves were
> re-derived from the `.docx` files to make sure the join was not the fault: 76 of 76 agree.
>
> Two more standing assumptions fell with it. There is no corpus-wide page constant - the 23 documents
> that fail this check and nothing else span 18.4 pt in both directions (sd 4.37), so the page-origin
> pairing the 10:54 slot recommended would have been 23 different answers, not one. And the class is not
> one defect: 82 of the 113 are systematically displaced (|med_dy| >= 1.5 pt), 31 are not displaced at
> all (worst_dy median 5.0 pt, med_dy under 1.5) and fail only the check's third clause, a single run
> twice its tolerance out.
>
> What is left is a real lead, and it is a different shape from everything tried so far. The tail grows
> with document length (worst_dy = 13.55 + 0.287 x runs_matched, r² = 0.31) while the median line does
> not move at all (r² = 0.05). Sorted by the size of the worst run, 17 documents are a fifth to four
> fifths of a *page* out, and not one of them fails `00_page_count` - the page count is right and the
> content on a later page is in the wrong place. No line-box construct reaches those. The 58 line-scale
> documents are the only ones a line construct is testable on, and they are exactly the ones whose
> median is already correct.
>
> That is why no engine change was committed: the next patch has to be chosen against that split, and
> choosing it blind is what the last five attempts did.

## The txt

| | |
|:--|:--|
| Measured | **5.0 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-01` | page-scale half: is the page-top gap the dropped w:b | 16:18 | - | not recorded |
| `18_dB-01` | single-page half: is the exact-line spacer charged p | 16:18 | - | not recorded |

## Timing

| | |
|:--|:--|
| Slot window | 15:50 → running · 27 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 50 |
| Longest silence | **5.6 min** — from 16:11:28, after `p2w.py --force: re-measuring the docx table on the new engine` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **6 min** | `#####` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **20 min** | `################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
