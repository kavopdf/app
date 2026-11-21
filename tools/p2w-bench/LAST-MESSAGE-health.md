# P2W Watchdog - Run Report

**21 Nov 2026 · 18:06 IST**

> Nothing is stopped. Every stage is done or moving, and the fixer's slot is free.

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 0.4 h |
| matrix | done | 213 of 213 | 4.8 h |
| classify | moving |  | 4.4 h |
| fix | moving |  | 0.4 h |
| txt | moving | 190 clean, 23 failing | 1.1 h |

## Trend

| | 2026-11-20 | 2026-11-21 | |
|:--|--:|--:|:--|
| .docx open | 60 | **59** | -1 |
| .txt failing | 46 | **27** | -19 |
| Google measured | 192 | **192** | no change |
| Google clean | 7 | **6** | -1 |

Both halves of the round moved: docx open fell and txt failing fell by far more. The one number
that went the wrong way is Google clean, 7 to 6 - one document that used to pass through Google no
longer does on the re-measured set. That is a measurement of the same engine, not a code change, and
it is the kind of move the classifier is supposed to turn into a class.

Today already had a progress row when this pass ran, so progress.py appended nothing. The row
records 27 txt failures and the live measurement is 23, so the row is behind the day it describes.
Editing a past row is not allowed, so it was left alone and written into BLOCKERS.md instead.

## Phase

round.py --phase prints fix. stage.py reports classify is behind - the class table is older than the
newest Google results - so classify is the next thing due and it belongs to the classifier's own
hourly slot, not to this pass. The two tools disagreeing on the stage is the documented behaviour
while a measurement is fresher than the class table, not a fault.

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py, round.py --phase, ROUND.json and
  status.py.
* Nothing needed moving. No cron was recreated, none was paused, no slot was released.
* The reopen check did not apply: the phase is fix, not a finished phase with documents still
  failing, so there was nothing to reopen.
* The slot check did not apply: no fixer claim is held and the slot is free, so no dead run is
  holding it.

## The tool this agent does not have

This watchdog has no cron tool, so a paused or zombie cron cannot be moved by automation. The
cron-inspection step, the pause/resume step and the zombie-recreate step of the watchdog prompt
cannot run in this agent, and they did not run - nothing here pretends a cron was inspected or
restarted. The first call it would have made is
cron(action="list"), then cron(action="runs", cron_id=<the id from HEALTH-BRIEF's table>) for any
stopped stage. That is a missing tool, not a decision waiting for a person. It is written into
BLOCKERS.md with both rows: the missing tool, and the progress row that is behind its own day.
