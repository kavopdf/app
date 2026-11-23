# P2W Watchdog - Run Report

**24 Nov 2026 · 03:07 IST**

> **1 stage(s) stopped: txt**

Nothing else in the pipeline was stopped, and nothing here could be moved from this pass. The fixer holds its slot and is working, the Google measurement and the class table are current, and today's trend row was already in place, so no past row was touched. The .txt row is the one thing standing still: the verifier was corrected after that table was written, so the score it prints was taken with an instrument that no longer exists, and the only cron that re-stamps it may not run while the phase is fix. This run has no cron tool, so the baseline cron could not be inspected or restarted; the exact calls that were not made are in BLOCKERS.md, together with the decision that the refresh route, not the class, is what is wrong.

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 212 | 1.3 h |
| matrix | done | 213 of 213 | 7.1 h |
| classify | moving |  | 2.6 h |
| fix | moving |  | 0.5 h |
| txt | **stopped** | 199 clean, 14 failing | 15.7 h |

## Trend

| | 2026-11-22 | 2026-11-23 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 16 | **14** | -2 |
| Google measured | 192 | **190** | -2 |
| Google clean | 23 | **30** | +7 |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* **A stage is stopped** - see BLOCKERS.md.

