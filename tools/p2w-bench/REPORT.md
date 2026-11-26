# Fixer report - 2026-11-26 15:46

```
# P2W Fixer - Run Report

**26 Nov 2026 · slot 15:46 → running IST · 1 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8521** of 9058 (94.1%) on 208 documents |
| Check-instances still failing | **537** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **48** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - run window: RUN.json says this run began at 15:46 vs TIMELINE.jsonl records the claim at 15:24, so the window was reset and the duration is short |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+40.32%** — mean 6.15 → 3.67 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **207** re-measured on this engine - **0** of the 207 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **6** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (47 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 15:46 | **lead** | 0/None | row-count lead restored: worst_dy~docx_table_rows slope 2.188 r2=0.423 n=207 from gverify (DISP-TABLE google cols are stale, 32/130 disagree up to 96.70pt); p2w.fitreserve 96->300 byte-identical on th |

## Why nothing moved, in this run's own words

> > The class was `18_displacement` (113 of 207 documents fail it) and the run kept no engine change,
> > because the premise every earlier patch was built on turned out to be wrong in a way that could be
> > measured in four minutes and had been carried for a day.
> >
> > The 15:12 run closed by telling the next run not to touch rows: "worst displacement has a slope of
> > 0.518 pt/row at r² = 0.01". That number does not reproduce. On `benchmarks/gverify/*.json`, which is
> > the only committed source that reproduces the 113-of-207 failure count, worst displacement against
> > `docx_table_rows` is **2.188 pt/row at r² = 0.423 over 207 documents** - the second strongest single
> > predictor in the corpus after source page count. The 0.518/0.01 figure appears in no subset I could
> > build. The reason is an instrument defect, measured here: `benchmarks/DISP-TABLE.csv`'s Google columns
> > are a stale measurement - 32 of 130 `worst_dy` values disagree with `gverify/` by more than 0.5 pt, up
> > to 96.70 pt, and 20 of 213 `google_fail_18` flags disagree. A run that fits on the CSV, or on a join
> > that mixes the two, measures an engine that no longer exists.
> >
> > With the lead restored, the obvious mechanism was tested and did not hold: the 15:12 story was that a
> > sheet is left with ~25 pt of slack, row growth eats it, and the renderer breaks before the writer's
> > explicit break. If that were true the engine's own fit reserve (`p2w.fitreserve`, 96 twips by default,
> > with 300 twips named in the code as measured for `bank-statement-5-pages`) would be the lever. It is
> > not. Converted the eight largest-displacement documents that have both many rows and several pages
> > twice, at 96 and at 300 twips: `word/document.xml` is **byte-identical in all eight**, page breaks and
> > `w:line` totals unchanged. The reserve only fires on a page whose flow comes within 96 twips of the
> > budget, and the model believes these pages have room to spare - while Google displaces their content
> > by 70 to 657 pt. The failure is not "the page is slightly over"; it is that the model and the renderer
> > disagree about how tall the page is, by an amount that scales with row count.
> >
> > That is the sharper question this run leaves: the engine charges a ruled row 15 twips (0.75 pt) of
> > excess in its spacer guard (`DocxWriter.java:6151`, "the quantum the 22 Nov sweep measured"), and the
> > displacement slope says the rendered excess is about 2.2 pt/row - three times that constant. One probe
> > document decides it: measure, in Google, the rendered height of one ruled row against its `w:trHeight`
> > declaration on `324_loan_amortisation_schedule` (246 rows).
> >
> > The slot went where the pod goes: a cold pod cost ~28 minutes - `install-gate.sh` killed at 300 s, then
> > three `pod-prep.sh` corpus slices (53 + 53 + 17 documents, 224 s + 186 s + 88 s) before `regress.py
> > --check` passed. That left one experiment and the write-up, not four attempts.

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

Accounts share 20% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **4.5 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 15:46 → running · 1 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 6 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| report - the report and the chain | **1 min** | `######################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
