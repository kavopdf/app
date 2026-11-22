# Watchdog - run report

The pipeline is moving. One stage is stopped: the .txt half, on a table 28.5 h older than the engine,
not on a dead cron.

## The five stages

| stage | state | progress | age |
|---|---|---|---|
| measure-google | done | 213 of 213 | 0.6 h |
| matrix | done | 213 of 213 | 27.2 h |
| classify | moving | | 4.3 h |
| fix | moving | | 0.6 h |
| txt | stopped | 197 clean, 16 failing | 28.5 h |

## The trend

Today's row already existed, so progress.py appended nothing and I left it alone. Against the row
before it: docx open 59 to 59, no change; txt failing 23 to 16; google measured 192 to 192, clean 6 to
23. Two days of .docx work moved both numbers, and today's kept attempt moved Google again after that
row was written.

## The round

phase fix, round 1. Nothing to reopen - the phase is not done, so round.py --reopen refuses. Nothing
to release either: the fixer holds the slot on a live claim from 21:27 UTC, and status.py reads
SILENT, which is a beacon overdue, not a zombie.

## What is stopped, and what I decided

The .txt table was committed 21 Nov 17:08 UTC and has not moved in 28.5 h. It reads stopped rather
than superseded only because a kept attempt moved the engine at 20:59 UTC, so the 197 and the 16
describe the engine of a day earlier.

Two measured facts settle it. The .txt diagnosis committed 21 Nov (FINDINGS/txt-16-failures-NINE-ARE-THE-CHECK)
reproduced all 16 verdicts by three independent paths: 7 of them carry a real engine fault, one
document each, and the rest are the check's own false positives. And classpick already suggests
t08\_line\_order, 2 documents, .txt - the ranking is pointed at the .txt half for the next slot.

So I did not park the class: 7 engine documents would be parked with the fault still in the engine.
And I did not edit verify_txt.py, which this run may not touch to move a number; the mechanism of each
check-side verdict is written down for the run that is allowed to change it. What would overturn it: a
re-stamp on the current engine still reporting 16 failing, or those check-side verdicts failing to
reproduce.

## No cron tool

This watchdog has no cron tool, so a paused or zombie cron cannot be moved by automation. A file
cannot tell me next\_fire\_at or a paused status. The calls I would have made: cron(action="list"),
then cron(action="runs", cron_id=...) on any stopped stage, then pause plus resume for a stale fire, or
delete plus create for a zombie. No cron was recreated, and none could be. Both rows are in
BLOCKERS.md.
