# P2W Watchdog - Run Report

**25 Nov 2026 · 06:06 IST**

> **1 stage(s) stopped: txt**

## Stages


| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 0.4 h |
| matrix | done | 213 of 213 | 26.3 h |
| classify | moving |  | 4.6 h |
| fix | moving | 5 attempt(s) in 3 h | 0.3 h |
| txt | **stopped** | 199 clean, 14 failing | 20.3 h |

## Trend

| | 2026-11-24 | 2026-11-25 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 14 | **14** | no change |
| Google measured | 190 | **191** | +1 |
| Google clean | 35 | **36** | +1 |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
* **A stage is stopped** - see BLOCKERS.md.

## What this pass did

* Read health.py, health.py --stalled, progress.py, round.py --phase, status.py and pending.py before deciding anything, then the last BLOCKERS rows and the baseline cron's own commits.
* **One stage is stopped: txt** - 199 clean and 14 failing. The baseline run committed a restamp of all 213 .txt rows before this pass and no row changed, so the table is current and the 14 failures are real, not a stale table.
* The trend did not move on docx open (59) or txt failing (14). It moved on Google measured (190 to 191) and Google clean (35 to 36). The fixer's attempt count beside the flat pair is 5 attempts in 3 h.
* The fixer slot is free and the phase is fix, so round.py had nothing to release and nothing to reopen.

## What I decided about the txt stall

The txt column has read 14 for 3 consecutive rows and no attempt has closed one of them. Those 14 sit in the word-invention, position, word-accuracy and line-order checks, and every one of them has had a turn. I did not park a class: classpick.py --exhaust asks for what was proved, and this pass proved nothing new. What is already proved is narrower - the two bank forms in the word-accuracy check cannot be recovered without a reference face or an English word list. The approach is not wrong either: the fixer is moving, and its rotation has reached the txt side. What would overturn this: an attempt on the word-invention check, which carries the largest share of the 14, that measures and keeps nothing.

## What did not run

**This watchdog has no cron tool.** STEP 3 and both cron fixes - the zombie and the stale schedule - cannot run, so the cron half of the brief did not happen this pass. The calls I would have made are written out in full in BLOCKERS.md: list the crons and read next_fire_at and status for the baseline and both fixers, runs for any stage reading stopped, then delete and recreate only a run still marked running past an hour on a free slot, and pause then resume only for a stale schedule, in the same run.

## Recorded, not acted on

CLASS-HISTORY.jsonl carries committed merge-conflict markers, so a tool that parses it crashes on them. Both writers only append, so nothing is broken at this hour; choosing which side to keep would edit a past record, so it is recorded in BLOCKERS.md for the run that owns that file.
