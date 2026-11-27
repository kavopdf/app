# Fixer report - 2026-11-27 22:16

```
# P2W Fixer - Run Report

**27 Nov 2026 · slot 22:16 → 22:24 IST · 7 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8477** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **534** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - kept change: 1 code commit(s) in this window, first: finding: the last seven are a scoring loop, not  vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **46** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (62 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

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
> The seven documents that stop it at 206 are the part I could not finish, and the reason is not rendering:
> `pre/` holds 213 PDFs and `out/` 214 docx, so every document but the exempt one has a render. They fail at
> **scoring** - `p2w.py:1604` builds its work list from documents with no `dist/<name>.json`, and these seven
> never get one, so each call re-renders them (55 s and 15 s, measured at 16:52) and throws the result away.
> That loop is the next run's first job: a pass that reaches 213 publishes, and one that cannot never will,
> however long the slot.
>
> What I did not do, and why: I did not land `PATCHES/18-small-dy-cellbefore.patch`, which two agents this
> run confirmed is the best-evidenced unlanded change (+1 clean, 0 worse, live Google, one line at
> `DocxWriter.java:7013`). Landing it needs a `RANKING.csv` measured on the patched tree - a second 44-minute
> pass - and the slot did not have two. Recording it as kept would have been a claim no tool backs.
>
> The honest ledger for this run: 0 documents clean, 0 documents worse, 206 documents measured on an engine
> that had 0 this morning, and the next run's first instruction written down with the minutes attached.

## The txt

| | |
|:--|:--|
| Measured | **2.4 h ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-01` | Which of the 41 docs failing 18_displacement share O | 21:26 | 22:24 | 58 min |
| `18_dB-01` | Is the 11:57 landing 33863086 real in Google, and ho | 21:26 | 22:24 | 58 min |

## Timing

| | |
|:--|:--|
| Slot window | 22:16 → 22:24 · 7 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 12 |
| Longest silence | **4.8 min** — from 22:19:06, after `relay: all 213 renders exist, final scoring call to publish RANKING` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **4 min** | `################` |
| report - the report and the chain | **1 min** | `######` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
