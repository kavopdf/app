watchdog - run report, 24 Nov 2026

One stage is stopped: the .txt table. Everything else is done or moving, and the stopped stage's owner has just taken the slot to refresh it.

| stage | state | progress | age |
|:--|:--|:--|--:|
| measure-google | done | 213 of 212 | 0.8 h |
| matrix | done | 213 of 213 | 5.4 h |
| classify | moving | | 1.9 h |
| fix | moving | attempts logged | 0.8 h |
| txt | stopped | 199 clean, 14 failing | 21.7 h |

## Trend

Today's row was already in the progress table from an earlier pass, so nothing was appended and nothing was edited. Against yesterday's row: docx open 59 to 59, txt failing 14 to 14, google 190 to 190, google clean 30 to 29. Three columns did not move and the one that did fell by one. That is the signal to watch, not a failure by itself.

## Round

Phase fix, round 1, 212 of 212 documents scored. round.py still lists open classes, so the phase is right to stay in fix.

## The stopped stage, on the evidence

The .txt table is 21.7 h old while its newest input is 7.4 h old, so it is genuinely stale, not a false alarm from an old clock. The earlier pass today corrected the baseline brief so the .txt refresh runs outside the measure phase, and that correction is now being exercised: a baseline run claimed the baseline slot minutes before this pass and owns the refresh. If that run finishes and the table is still 21.7 h old, then the phase gate was not the blocker and the next pass treats it as the instrument.

## The fixer

The claim is 9 minutes old and the current run has 0 attempts and has not beaconed since it claimed. status.py calls that SILENT. I did not force-release the slot: the claim is inside its stale window, and a release would have put a second run into the engine. The relay cron that runs ten minutes after the fixer is the designed answer to a wedged fixer, so both fixer crons were left alone.

## What this run could not do

This run's tool list has no cron operation, so nothing on the platform could be read or moved. The calls that would have been made and were not: cron(action="list") for every id in the brief, cron(action="runs") for the baseline id and for both fixer ids, and cron(action="pause") then cron(action="resume") in the same pass for any stale fire. A paused or zombie cron therefore cannot be moved by automation from here, and health.py reads files and cannot see the platform. This is recorded in BLOCKERS.md.

round.py --reopen refused, correctly: the phase is fix, not done, so there was nothing to reopen.
