# Pipeline watchdog — 25 Nov 2026

Two stages stopped: classify at 7.7 h and txt at 23.4 h. The fix stage is moving with 4 attempt(s) in 3 h. Nothing was measured, classified, fixed or shipped by this pass.

| stage | state | progress | age |
|---|---|---|---|
| measure-google | done | 213 of 213 | 0.5 h |
| matrix | done | 213 of 213 | 29.4 h |
| classify | stopped | — | 7.7 h |
| fix | moving | 4 attempt(s) in 3 h | 0.3 h |
| txt | stopped | 199 clean, 14 failing | 23.4 h |

## What the two stopped rows actually are

**classify** is a real gap this pass found for the first time. stage.py names classify independently — "the table is older than the results" — and fresh Google measurements landed after the class table was last regenerated, so the queue the fixer ranks is built on older results.

**txt** is not a stale table. The .txt state file names the current engine, and restamp_txt.py --report prints 213 scored, 213 unchanged. The 14 failures are a measurement of today's engine, so the row is red for the reason health.py intends: a current measurement of 14 failures.

## The trend

Today's row was already written by the earlier pass, so nothing was appended. Against 24 Nov: docx open 59 -> 59 and txt failing 14 -> 14, both flat — the fifth consecutive flat row for docx open and the third for txt — while Google moved 190 -> 191 measured and 35 -> 37 clean. The fixer's count beside the flat pair is 4 attempt(s) in 3 h, none kept.

## What I did, and what I could not do

The round phase is fix, so round.py --reopen refuses: the phase is fix, not done. status.py reads the fixer slot IDLE with no claim, so there was nothing to release and --release-fixer --force was not run.

This watchdog has no cron tool, so STEP 3 and STEP 4 A and B cannot run: a paused, stale or zombie cron cannot be moved by automation here. That is a missing tool, not a decision a person has to make. The calls I would have made are written into BLOCKERS.md with the ids from the health brief's table.

## Decision on the txt stall (STEP 5)

No class is parked. The earlier pass set its own overturn condition — park t12_word_invention if an attempt on it measures and keeps nothing — and that attempt exists, but its own record contradicts the conclusion: it names the mechanism, says a patch was written, and measured the invented-word count dropping on one document, then recorded no files changed. A class whose last attempt found a working patch and did not land it is not unwinnable, and parking it would discard a measured fix. The defect is the landing, not the class. What would overturn this: an attempt that lands a patch and still moves no document, or further attempts that end with no files and no explanation.

The evidence and the overturn conditions are in tools/p2w-bench/BLOCKERS.md, and the blockers row for this pass is committed with this report.
