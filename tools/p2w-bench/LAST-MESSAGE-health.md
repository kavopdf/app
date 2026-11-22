# P2W Watchdog - Run Report

**22 Nov 2026 · 15:15 IST**

> Nothing is stopped.

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 9.0 h |
| matrix | done | 213 of 213 | 15.3 h |
| classify | superseded |  | 8.4 h |
| fix | moving |  | 0.5 h |
| txt | superseded | 197 clean, 16 failing | 16.6 h |

## Trend

| | 2026-11-21 | 2026-11-22 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 23 | **16** | -7 |
| Google measured | 192 | **192** | no change |
| Google clean | 6 | **23** | +17 |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* Nothing needed moving.
* The .txt table is newer than the engine, verify_txt.py and restamp_txt.py, so it is current and not late - see BLOCKERS.md.

## The step that could not run

This watchdog has no cron tool, so STEP THREE and STEP FOUR A/B - the steps that read and move the cron platform - could not run. That is a missing tool, not a judgement call: a paused or zombie cron cannot be moved by this run, and nothing in the repository can see one. The exact calls this pass would have made, with the fixer ids read from HEALTH-BRIEF's table rather than from memory, are written into BLOCKERS.md.

## What was repaired

The txt row had been red on age alone. The table is a function of the engine, verify_txt.py and restamp_txt.py; every one of those is older than the table, and the txt fingerprint in ENGINE-STAMP.json matches the live engine exactly. health.py now tests that and prints superseded - the same state the classify row already uses for the same false alarm. The age and the threshold are untouched, and any commit to an input turns the row red again on its own.

## What is still stuck

The .docx half. benchmarks/RANKING.csv was last measured before the engine changed, so the docx table describes an engine that no longer exists, and the gate refuses the held-back row-grid patch for that reason. round.py --remeasure is the unblock, and it is not safe to pull while a live fixer run holds the slot.
