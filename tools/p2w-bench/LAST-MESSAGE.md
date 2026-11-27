# Fixer report - 2026-11-27 21:17

```
# P2W Fixer - Run Report

**27 Nov 2026 · slot 21:17 → running IST · 1h 01m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8437** of 8969 (94.1%) on 212 documents |
| Check-instances still failing | **532** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1 |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **46** of the **205** re-measured on this engine - **1** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 1 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (57 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 22:16 | **lead** | None/213 | measured the tree instead of a construct: p2w --force reached 206/213 in 44 min, 7 documents give no render, so RANKING.csv could not be republished and measure_gate is still NOT READY. Next run must |

## Why nothing moved, in this run's own words

> Nothing moved because I spent the slot proving where the block actually is, and it is not in the engine.
>
> The last four runs each ended the same way: a fix measured live in Google, and `regress.py` refusing it
> because `RANKING.csv` was not measured on the tree. The 20:09 run named that as "the measurement cron's
> work, not something a fixer can do in a slot". This run tested that sentence instead of repeating it, and
> it is wrong in one direction and right in the other.
>
> Wrong: a fixer CAN do the pass. `p2w.py --force` on this pod rendered and scored 206 of 213 documents in
> 44 minutes across nine `--budget` calls. That is inside a 90-minute slot.
>
> Right: only if it starts at minute zero. `p2w.py` publishes nothing until the table is complete -
> "PARTIAL: 170 of 213 measured - writing RANKING.partial.csv, the published RANKING.csv is untouched" -
> and everything it renders lives in `/scratch/work/p2w/`, outside the repository. So a pass that starts at
> minute 20 is 44 minutes of work that leaves the sandbox with nothing to show: no table, no stamp, no
> landed patch. That is the arithmetic behind six runs with a measured fix and no document fixed, and
> `18_displacement-FULL-PASS-DOES-NOT-FIT-A-SLOT-0650-fixer.md` reached the same conclusion at 06:50 today
> with a different measurement. Two runs, same answer, so it is not a bad night.
>
> The seven documents that stop it at 206 are the part I could not finish. They produce no soffice render;
> `Account_Opening_Form_Fillable_filled` rendered alone in 64 s and the measured count still did not move,
> so at least one fails after its render rather than before it. Naming them is the next run's first job,
> because a pass that can reach 213 publishes, and a pass that cannot never will however long the slot.
>
> What I did not do, and why: I did not land `PATCHES/18-small-dy-cellbefore.patch`, which two agents this
> run confirmed is the best-evidenced unlanded change (+1 clean, 0 worse, live Google, one line at
> `DocxWriter.java:7013`). Landing it needs a `RANKING.csv` measured on the patched tree - a second 44-minute
> pass - and the slot did not have two. Recording it as kept would have been a claim no tool backs.
>
> The honest ledger for this run: 0 documents clean, 0 documents worse, 206 documents measured on an engine
> that had 0 this morning, and the next run's first instruction written down with the minutes attached.

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

Accounts share 14% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **2.3 h ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-01` | Which of the 41 docs failing 18_displacement share O | 21:26 | - | - |
| `18_dB-01` | Is the 11:57 landing 33863086 real in Google, and ho | 21:26 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 21:17 → running · 1h 01m |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 128 |
| Longest silence | **9.1 min** — from 21:17:10, after `pending.py: reading the pending gate` |
| Silences over 2 min | 9 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **5 min** | `##` |
| fix - diagnose and change the engine | **4 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **39 min** | `##############` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **10 min** | `####` |

The unattributed row is 9 distinct beat(s) that matched no phase. They said:

- `relay: agents A/B deploying, measuring corpus state`
- `relay: corpus pass 1 on current engine a05b20eb (unblocks landing); agents landed`
- `relay: corpus pass 1 chunk 2`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 33 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
