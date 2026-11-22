# P2W Watchdog - Run Report

**22 Nov 2026 · 23:58 IST**

> Nothing is stopped.

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 0.1 h |
| matrix | done | 213 of 213 | 0.1 h |
| classify | superseded |  | 0.1 h |
| fix | moving |  | 0.1 h |
| txt | superseded | 197 clean, 16 failing | 0.1 h |

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

