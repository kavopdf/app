# P2W Watchdog - Run Report

**27 Nov 2026 · 03:08 IST**

> Nothing is stopped.

This pass found every stage that can run either moving or done, so nothing was paused, released or reopened, and the fixer slot is held by a live claim. The committed trend row and the live tables disagree in one column, and the tool that writes the row allows a single correction a day which an earlier pass already used, so the row stands as written and the difference is recorded in BLOCKERS.md instead of being rewritten. This run holds no cron tool, so the platform half of the check - a paused cron, a stale fire time, a zombie run - could not be run at all; the exact calls are named in BLOCKERS.md.

## Stages

> **Today's row is stale** - docx_open: committed row says 60, the data says 59. The trend below is the committed row; the data has moved.


| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | moving | 124 of 213 | 0.2 h |
| matrix | done | 213 of 213 | 4.5 h |
| classify | waiting |  | 0.7 h |
| fix | moving | 6 attempt(s) in 3 h | 0.7 h |
| txt | moving | 205 clean, 8 failing | 0.1 h |

## Trend

| | 2026-11-25 | 2026-11-26 | |
|:--|--:|--:|:--|
| .docx open | 59 | **60** | +1 |
| .txt failing | 9 | **8** | -1 |
| Google measured | 213 | **205** | -8 |
| Google clean | 42 | **47** | +5 |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* Nothing needed moving.

