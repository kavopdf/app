# P2W Watchdog - Run Report

**27 Nov 2026 · 15:41 IST**

> **1 stage(s) stopped: classify**

classify is the only stage stopped, and it went red today rather than being stuck: it read waiting while the Google corpus was short and turned stopped when the corpus reached every document, with the class table older than the verdicts it ranks. This watchdog has no cron tool, so it could not look at the classifier cron or move it - the exact calls it would have made are in BLOCKERS.md, and that is a missing tool rather than a decision for a person. The fixer slot was free and the fixer is working, so nothing was released. The trend row was amended from the live tables, not appended. The Google clean fall is the corpus and not the row: five documents that passed on 26 Nov fail today, and the five are named in BLOCKERS.md with the two checks that moved.

## Stages


| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 1.4 h |
| matrix | done | 213 of 213 | 1.4 h |
| classify | **stopped** |  | 13.3 h |
| fix | moving | 2 attempt(s) in 3 h | 0.3 h |
| txt | moving | 205 clean, 8 failing | 5.5 h |

## Trend

| | 2026-11-26 | 2026-11-27 | |
|:--|--:|--:|:--|
| .docx open | 60 | **59** | -1 |
| .txt failing | 8 | **8** | no change |
| Google measured | 205 | **212** | +7 |
| Google clean | 47 | **42** | -5 |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* **A stage is stopped** - see BLOCKERS.md.

