# Fixer report - 2026-11-26 12:16

```
# P2W Fixer - Run Report

**26 Nov 2026 · slot 12:16 → 15:13 IST · 2h 56m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8521** of 9058 (94.1%) on 208 documents |
| Check-instances still failing | **537** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **48** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 8 vs ATTEMPTS.json history 5; subagents: 2 deployed vs no FINDINGS file for R-01 |
| Document-moves this run | **0** — 8 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+40.32%** — mean 6.15 → 3.67 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **207** re-measured on this engine - **0** of the 207 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **6** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (47 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 13:11 | **lead** | 0/None | guarded pgMar page-top patch: 213/213 converted on the patched engine, regress says no document worse than baseline, refused only on the table stamp; the corpus re-score is 73 s/doc = 4.3 h, which no |
| 13:35 | **reverted** | 0/212 | txt-meta-annotation patch applied, corpus built (213/213, 1.4 min) and fully re-measured (212/212 in 6 calls); gate refused on 1 docx regression 600_reviewed_invoice_with_annotations 54.30 -> 62.46. T |
| 14:59 | **lead** | 0/None | No engine change. Refuted three standing assumptions on 207 committed Google results: (1) attribution=table-row predicts nothing in Google - med_dy slope vs docx_table_rows -0.108, r2=0.00; worst_dy 0 |
| 15:12 | **lead** | 0/None | Page-scale family diagnosed from the emitted XML (no Drive call): every source page is a hand-built block placed at 97% of the 16838-twip usable height with ~25 pt slack, ended by an explicit <w:br w: |
| 15:12 | **lead** | 0/None | Line-scale family (27 docs with a docx on the pod): med_dy = -5.17 + 0.765*median_font_size_pt, n=27, r2=0.20; family spans -3.1..+4.2 pt, median 1.2 pt, worst_dy median 4.5 pt - i.e. it fails on tail |

## Why nothing moved, in this run's own words

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

### The run before this one said

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
>
> Accounts share 100% of their significant words - **the same blocker, named twice** (the cut is 50%).

Accounts share 94% of their significant words - **the same blocker, named twice** (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **3.9 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `R-01` | two runs of ConvertOne on one PDF - identical bytes? | 14:22 | 14:47 | 25 min |
| `R-02` | explicit break or renderer flow? | 15:10 | 15:19 | 9 min |

## Timing

| | |
|:--|:--|
| Slot window | 12:16 → 15:13 · 2h 56m |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 70 |
| Longest silence | **27.9 min** — from 14:14:50, after `lastmessage.py: running a tool for its numbers` |
| Silences over 2 min | 19 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **2 min** | `#` |
| fix - diagnose and change the engine | **24 min** | `###` |
| measure or build - a conversion, screen or compile writes no beacon | **1h 20m** | `##########` |
| record - attempt, handoff, class rows | **5 min** | `#` |
| report - the report and the chain | **21 min** | `###` |
| other - not attributed to a tool | **35 min** | `#####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below.

## Next run

**Read `FINDINGS/18-displacement-TABLE-ROW-ATTRIBUTION-REFUTED-26NOV-relay.md` before touching
`18_displacement`.** Three things this run measured forbid the obvious moves:

- `attribution=table-row` is not a cause in Google. Median displacement does not scale with
  `docx_table_rows`; the slope is negative and r² is 0.00. Do not write a row-height, `trHeight` or
  cell-margin patch on the strength of that label.
- There is no corpus-wide page constant. The solo documents span 18.4 pt in both directions. Do not
  pair page origins looking for one number.
- The class is three families by the *size* of the worst run: 17 documents a fifth to four fifths of a
  page out (none of them fails `00_page_count`, so the page count is right and a later page's content
  is not), 38 between 9 and 100 pt, and 58 at or under 9 pt. A line-box change can only reach the 58,
  and those are the ones whose median line is already correct.

**The first attempt of the next run should be on `bank-statement-5-pages`.** The second angle of this
run read the emitted XML of the eight largest-`worst_dy` documents and found the mechanism: the writer
places every source page as a hand-built block — furniture, one table fragment, spacers — at **97 % of
the usable height with about 25 pt of slack**, terminated by an explicit `<w:br w:type="page"/>`
(`DocxWriter.java:690`), with `w:pgMar` zero on all four sides. Every row is `w:hRule="atLeast"` with
`<w:cantSplit/>`, so the renderer may grow a row but may not cut one. Once row growth eats the 25 pt,
the renderer breaks *before* the writer's break and the whole following block — a 522–659 pt `w:before`
spacer, the next table fragment — lands one block late. That is hundreds of points, and it is why the
page count stays right while the content does not. The cheapest falsifier is to emit `hRule="exact"` on
the cell rows of that one document: if `worst_dy` does not fall below 100 pt, the break is not being
pushed by row growth and the candidate is refuted for the family at the cost of one document. See
`FINDINGS/18-displacement-PAGE-BREAK-IS-UNEARNED-26NOV-relay.md`.

**Pod cost, priced:** a cold pod needs `pod-prep.sh` four to five times before the commit gate can run
at all (213 PDFs, a JDK, four jars, then the engine compile, then the corpus conversion in 240 s
slices). `install-gate.sh` will be killed at 300 s on a cold pod every time. Run `pod-prep.sh` first,
repeatedly, and only then the gate.

**Instrument note, not a defect:** the writer is deterministic in content but not in bytes - every
difference between two conversions of one PDF is the ZIP entry mtime (`ZipEntry` defaults to
`System.currentTimeMillis()`; nothing calls `setTime`). Comparing two `.docx` by hash will always say
"changed". Compare the XML parts, or normalise the ZIP time fields first.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
