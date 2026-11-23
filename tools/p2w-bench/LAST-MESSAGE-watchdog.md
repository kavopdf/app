# P2W Watchdog - Run Report

**23 Nov 2026 · 06:09 IST**

> **2 stage(s) stopped: classify, txt**

Nothing was moved by this pass, and each reason is written into BLOCKERS.md rather than acted on. The fix stage is live, so no slot was released and none was forced. The round is in `fix`, so there was nothing to reopen. The two red rows belong to the classifier and the baseline, and this run holds no cron tool to reach either of them - the exact calls are named in BLOCKERS.md. The `.txt` half has now stood still for longer than a day; the standing decision on it is unchanged, and the engine documents it names still need a fixer slot that picks a `.txt` class.

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 1.4 h |
| matrix | done | 213 of 213 | 1.4 h |
| classify | **stopped** |  | 7.3 h |
| fix | moving |  | 0.7 h |
| txt | **stopped** | 197 clean, 16 failing | 31.5 h |

## Trend

| | 2026-11-22 | 2026-11-23 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 16 | **16** | no change |
| Google measured | 192 | **190** | -2 |
| Google clean | 23 | **28** | +5 |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* **A stage is stopped** - see BLOCKERS.md.

