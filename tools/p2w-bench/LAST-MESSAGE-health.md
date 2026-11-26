# P2W Watchdog - Run Report

**26 Nov 2026 · 12:10 IST**

Nothing is stopped. Every stage is done, moving, or waiting on a stage that is still measuring.

## Stages

| stage | state | progress | age |
|:--|:--|:--|--:|
| measure-google | moving | 187 of 213 | 0.5 h |
| matrix | done | 213 of 213 | under 3 h |
| classify | waiting |  | 5.6 h |
| fix | moving | 8 attempt(s) in 3 h | 0.3 h |
| txt | moving | 205 clean, 8 failing | 0.6 h |

## Trend

| | 2026-11-25 | 2026-11-26 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 9 | **8** | -1 |
| Google measured | 213 | **208** | -5 |
| Google clean | 42 | **42** | no change |

The committed row for today reads 208 for Google measured and the data now reads 207, so that row is one behind a measurement that is still being rewritten. The generator flags it; I did not touch a past row.

## What this pass did

- Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.
- Nothing was stopped, so nothing was moved.
- Today's trend row was already committed by an earlier pass. progress.py appended nothing, so there was nothing to commit for it.
- The reopen path was not run: the round phase is fix, not a finished phase with documents still failing.
- The force-release path was not run: the fixer claim is live. ROUND.json reads fixer_started at 06:33, the slot has 8 attempt(s) in 3 h and the last beat is recent, so this is a working run and not a dead one.

## What this pass could not do

This pass has no cron tool in its tool list, so the platform half of the watchdog cannot run here. A paused cron, a stale next_fire_at or a zombie run stays invisible and cannot be moved by automation. The exact calls it would have made, against the ids in HEALTH-BRIEF's table and not from memory: cron(action="list"), then cron(action="runs", cron_id=...) for each fixer cron. That is a missing tool, not a decision anyone has to make. It is recorded in BLOCKERS.md.

## The flat .docx axis

.docx open reads 59 in every committed row including today's, while .txt failing moved 9 to 8 and Google clean stayed at 42. The fixer is working - 8 attempt(s) in 3 h - and keeping nothing on that axis. The decision recorded earlier today stands: the gate charges a full corpus re-score to every change, so changes are measured, reverted and never land. What replaces it is a scope keyed on the documents a change can actually move. Overturned by one engine change that lands and moves .docx open. No class was parked and no past row was edited.
