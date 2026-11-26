# P2W Watchdog - Run Report

**26 Nov 2026 · 18:12 IST**

> Nothing is stopped.

This pass read the evidence rather than the reports: a Google measurement is in flight right now (the newest result files were written this minute), so measure-google is moving and classify is correctly waiting behind it. The fixer slot is free - the newest commit is the release - and the round phase is fix, so the reopen guard does not apply. The .docx column is still flat while the .txt column moved, the same shape as earlier today; that is recorded in BLOCKERS.md, not treated as a fault to guess past. One thing is missing, not decided: this pass has no cron tool in its tool list, so a paused or zombie cron cannot be moved by automation, and the exact calls it would have made are written into BLOCKERS.md.

## Stages

> **Today's row is stale** - google: committed row says 208, the data says 207. The trend below is the committed row; the data has moved.


| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | moving | 88 of 213 | 1.4 h |
| matrix | done | 213 of 213 | 4.0 h |
| classify | waiting |  | 11.7 h |
| fix | moving | 3 attempt(s) in 3 h | 0.6 h |
| txt | moving | 205 clean, 8 failing | 3.3 h |

## Trend

| | 2026-11-25 | 2026-11-26 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 9 | **8** | -1 |
| Google measured | 213 | **208** | -5 |
| Google clean | 42 | **42** | no change |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* Nothing needed moving.

