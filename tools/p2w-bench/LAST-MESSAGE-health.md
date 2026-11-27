# P2W Watchdog - Run Report

**27 Nov 2026 · 06:13 IST**

> Nothing is stopped.

The pipeline is moving on every stage that can move, so nothing was restarted. I appended and committed today's trend row, and recorded a fixer claim that has gone silent: it is left to expire on its own rather than force-releasing a run that may be mid-render. This watchdog has no cron tool, so the scheduler half was not read, and that is written into BLOCKERS.md with the calls it would have made.

## Stages


| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | moving | 197 of 213 | 2.0 h |
| matrix | done | 213 of 213 | 1.0 h |
| classify | waiting |  | 3.8 h |
| fix | moving | 6 attempt(s) in 3 h | 0.2 h |
| txt | moving | 205 clean, 8 failing | 0.4 h |

## Trend

| | 2026-11-26 | 2026-11-27 | |
|:--|--:|--:|:--|
| .docx open | 60 | **59** | -1 |
| .txt failing | 8 | **8** | no change |
| Google measured | 205 | **205** | no change |
| Google clean | 47 | **47** | no change |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* Nothing needed moving.

