# P2W Watchdog - Run Report

**27 Nov 2026 · 00:07 IST**

> Nothing is stopped.

## Stages


| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | moving | 68 of 213 | 0.4 h |
| matrix | done | 213 of 213 | 1.5 h |
| classify | waiting |  | 17.6 h |
| fix | moving | 1 attempt(s) in 3 h | 1.9 h |
| txt | moving | 205 clean, 8 failing | 9.2 h |

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


This pass has no cron tool in its tool list, so the platform half of the watchdog could not run: a paused
or zombie cron cannot be moved by automation from here. The calls it would have made are written out in
BLOCKERS.md with the ids from HEALTH-BRIEF's table. Nothing was stopped, so nothing needed moving; the
one thing that did need doing was today's trend row, which the live tables had moved past, and
progress.py --amend rewrote it from those tables and named what it used to say.
