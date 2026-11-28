# P2W Watchdog - Run Report

**28 Nov 2026 · 15:03 IST**

> Nothing is stopped.

## Stages


| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 214 of 214 | 9.4 h |
| matrix | done | 214 of 214 | 7.5 h |
| classify | superseded |  | 7.0 h |
| fix | moving | 7 attempt(s) in 3 h | 0.1 h |
| txt | moving | 209 clean, 5 failing | 0.9 h |

## Trend

| | 2026-11-27 | 2026-11-28 | |
|:--|--:|--:|:--|
| .docx open | 116 | **116** | no change |
| .txt failing | 6 | **5** | -1 |
| Google measured | 206 | **206** | no change |
| Google clean | 46 | **48** | +2 |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* Nothing needed moving.

* Amended today's PROGRESS.md row from the live tables: txt failing was 6 there, the tables read 5. That is the single correction the tool allows in a day, and no past row was touched.
* The reopen check did not fire. round.py --reopen refused because the phase is fix, not done.
* The release check did not fire. status.py reads IDLE with the slot free and the last fixer run minutes old, so no dead run was holding it.
* No cron was listed, inspected, paused, resumed, deleted or recreated. This run has no cron tool; the exact calls are named in BLOCKERS.md.

The fixer is inside its budget and the txt stage is inside its threshold, so the pipeline is moving on its own. The flat .docx column is the standing signal, not a new stall: docx open has read 116 on both of the last two rows while google clean rose 46 to 48, which says the renderer the settled decision names is producing passes the LibreOffice column does not show. Nothing was parked with classpick.py --exhaust, because the class table is fresh and the fixer has not exhausted its approach.
