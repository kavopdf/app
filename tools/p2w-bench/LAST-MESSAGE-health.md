# P2W Watchdog - Run Report

**22 Nov 2026 · 12:16 IST**

> **1 stage(s) stopped: txt**

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 6.0 h |
| matrix | done | 213 of 213 | 12.3 h |
| classify | superseded |  | 5.4 h |
| fix | moving |  | 0.2 h |
| txt | **stopped** | 197 clean, 16 failing | 13.6 h |

## Trend

| | 2026-11-21 | 2026-11-22 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 23 | **16** | -7 |
| Google measured | 192 | **192** | no change |
| Google clean | 6 | **23** | +17 |

## What this pass did

Read health.py, health.py --stalled, stage.py, progress.py, round.py --phase and status.py. The round phase is fix, round 1. No cron was recreated, and none could be: this watchdog has no cron tool, so it cannot list a cron, read a run, pause or resume one, or delete and recreate a zombie. The exact calls it would have made are in BLOCKERS.md with their arguments. That is a missing tool, not a decision for a person.

## The stopped row is not a stall

The txt row ages the .txt ranking table. That table is stamped against the engine: the state file beside it records the engine commit it was measured on, and that is still the newest engine commit on the branch. Nothing has changed the converter since the table was written, so no re-measurement is due, and a re-measurement would print the same 197 clean and 16 failing. The threshold is twelve hours and the table is 13.6 h old, so the row goes red on age alone while the work underneath it has not stopped.

What would overturn that, and make this a real stall: an engine commit newer than the table, or a fixer run that lands an engine change without re-scoring the .txt half. Either one, with the row still red, needs the .txt half to get its own scheduled re-measurement. I did not move the threshold to make the row green.

## The other rows

Nothing is wedged. status.py reports the fixer WORKING with a fresh beacon, so the slot is held by a live run and was not released; the reopen path does not apply because the phase is fix, not done. The trend row moved: .txt failing 23 to 16 and Google clean 6 to 23. .docx open is unchanged at 59 for the second row running, which is the number to watch, with the fixer's attempt count beside it in BLOCKERS.md.
