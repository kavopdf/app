# Fixer report - 2026-11-27 22:00

```
# P2W Fixer - Run Report

**27 Nov 2026 · slot 22:00 → running IST · 0 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8477** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **534** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **46** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (63 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

> Nothing was KEPT because the change is real but unlandable, and that is a gate verdict, not a diagnosis
> problem.
>
> The change: `PATCHES/18-small-dy-cellbefore.patch`, a one-line `LINE_BASE` rescale of the `w:before` a
> single-line table cell already carries. Measured live in Google by this run, before and after, on two
> documents:
>
> 74_balance_sheet_indented_subitems      41/42 -> 42/42  CLEAN
> 72_bank_statement_no_rules_right_amounts 41/42 -> 41/42  not worse
>
> Predicted net-zero, measured +1 clean and 0 worse. I reverted it because:
>
> measure_gate.py  -> engine docx d28ca7516c3f9165, tree f4ce54f257d15f1c  NOT READY
> regress.py --check -> ENGINE CHANGED (docx): table measured on d28ca7, the tree is f4ce54f2  REFUSED
>
> Both tables pass the comparison ("docx: no document worse than baseline", "txt: no document worse than
> baseline"). What refuses is that RANKING.csv has not been re-measured on this engine. That is one full
> corpus pass - 213 documents through LibreOffice and 42 checks each - and it is the measurement cron's
> work, not something a fixer can do in a slot and still write an honest report.
>
> What I did spend the slot on instead, because it changes what the NEXT run should do:
>
> 1. The patch is worth +1, not 54. I measured the three other documents whose cells carry the same
> 0.500 shape that made 74 clean - 71_invoice_space_aligned_no_rules, 22_invoice_four_columns_txtpos,
> price-list-2col-dense-right-aligned - and all three stay at 41/42. The shape is necessary and not
> sufficient. That kills the "worth 53.9 clean documents" reading of the leverage table for this
> construct with a measurement instead of an inference.
>
> 2. The relay's proposed gate (cellBoxTw*2 >= rowHeightTw) is unnecessary AND ineffective: counting the
> emitted XML, 72 carries 66 cells at exactly the shape the gate is meant to exclude, so it does not
> spare 72 - and 72 does not need sparing, because it does not get worse at the check level. The
> earlier "72 regresses" was read off med_dy, and med_dy moving inside a still-failing check is not a
> regression.
>
> 3. The residual on 71 and 22 is NOT a row displacement. An independent probe (not verify_google.py)
> shows every run on the page off by the same 5.84 pt (71) and 4.01 pt (22), footer included. It is
> the page's flow origin, and the two documents need OPPOSITE corrections. That is the lead.

## The txt

| | |
|:--|:--|
| Measured | **2.0 h ago** |
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
| Slot window | 22:00 → running · 0 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 3 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
