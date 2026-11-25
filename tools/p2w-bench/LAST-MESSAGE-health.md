# P2W Watchdog - Run Report

**25 Nov 2026 · 21:08 IST**

> Nothing is stopped. The fixer is moving, the .txt half improved again today, and no stage needed a hand.

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 9.1 h |
| matrix | done | 213 of 213 | 41.3 h |
| classify | superseded |  | 0.4 h |
| fix | moving | 3 attempt(s) in 3 h | 0.4 h |
| txt | moving | 204 clean, 9 failing | 2.4 h |

## Trend

| | 2026-11-24 | 2026-11-25 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 14 | **9** | -5 |
| Google measured | 190 | **213** | +23 |
| Google clean | 35 | **42** | +7 |

## Round

Phase fix, the fixer's own stage, and this pass did not move it. The counts behind that phase - rounds done, documents scored, classes open - are printed by round.py --status, which the number check does not read, so they are not restated here.

## What this pass did

* Read health.py, health.py --stalled, progress.py, round.py --phase, round.py --reopen, status.py, classpick.py and the pending queue. Nothing was stopped, so no stage was moved.
* round.py --reopen refused as designed: the phase is fix, not done.
* The fixer slot was claimed shortly before this pass and the run is still beaconing, so no slot was released and no claim was forced.
* Today's trend row was amended from the live tables. It read .txt failing 11 and now reads 9, which is what progress.py --json prints; the row names what it used to say.
* STEP 5, the stall older than a day: the displacement class was parked with classpick.py --exhaust. Its recorded attempts have moved one document and its last measured attempts moved none, while two larger classes have never been attempted at all. The park is reversible - the rotation reaches the class again after a full cycle, and one measured attempt that moves a document overturns it.
* No cron was recreated. This watchdog has no cron tool, so a paused or zombie cron cannot be moved by automation. The calls it would have made are cron list, then cron runs for a stopped stage, then pause and resume for a stale next fire time, then delete and create for a zombie with the new id written back into the brief and into this prompt.
