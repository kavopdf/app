# P2W Watchdog - Run Report

**22 Nov 2026 · 03:07 IST**

> **1 stage(s) stopped: fix**

This pass found one instrument lying and repaired it: the classify row was reading a class table no fixer ranks, while the Google table the fixer actually picks from was current, which two earlier watchdog passes had already mistaken for a stalled classifier. The only remaining stop is the fixer run that died mid-scoring with a free slot behind it, and the next scheduled fixer will take that slot on its own. This watchdog has no cron tool in its declared tool list, so it cannot see or clear a platform-side zombie run, and the exact calls it would have made are written into BLOCKERS.md rather than dressed up as a decision. No cron was paused, deleted or recreated by this pass.

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 3.3 h |
| matrix | done | 213 of 213 | 3.1 h |
| classify | superseded |  | 1.8 h |
| fix | **stopped** |  | 1.0 h |
| txt | moving | 197 clean, 16 failing | 4.5 h |

## Trend

| | 2026-11-20 | 2026-11-21 | |
|:--|--:|--:|:--|
| .docx open | 60 | **59** | -1 |
| .txt failing | 46 | **23** | -23 |
| Google measured | 192 | **192** | no change |
| Google clean | 7 | **6** | -1 |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* **A stage is stopped** - see BLOCKERS.md.

