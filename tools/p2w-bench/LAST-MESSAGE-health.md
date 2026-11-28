# P2W Watchdog - Run Report

**28 Nov 2026 · 06:11 IST**

> **1 stage(s) stopped: matrix**

## Stages


| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 214 of 214 | 0.5 h |
| matrix | **stopped** | 213 of 214 (37 on the engine in the tree) | 8.5 h |
| classify | moving |  | 4.0 h |
| fix | moving | 6 attempt(s) in 3 h | 0.5 h |
| txt | moving | 208 clean, 6 failing | 0.5 h |

## Trend

| | 2026-11-27 | 2026-11-28 | |
|:--|--:|--:|:--|
| .docx open | 116 | **116** | no change |
| .txt failing | 6 | **6** | no change |
| Google measured | 206 | **206** | no change |
| Google clean | 46 | **48** | +2 |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* **A stage is stopped** - see BLOCKERS.md.


**What this run did.** Nothing needed moving and nothing was moved: the progress row was appended and committed, matrix is the one stopped stage and its cause is the corpus a fresh pod does not carry, and the escalation the last pass set has not come due. This watchdog has no `cron` tool, so no cron was inspected, recreated, paused or resumed - the exact calls it would have made are in BLOCKERS.md. The commit gate this repository installs per clone is the open question behind a flat .docx column, and it is written up there too.
