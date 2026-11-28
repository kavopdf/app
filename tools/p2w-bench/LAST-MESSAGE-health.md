## The pipeline is moving

Nothing is stopped. `health.py --stalled` exits 0 with all five stages clear, so this pass had no
stage to restart and no cron to touch.

| stage | state | progress | age |
|:--|:--|:--|--:|
| measure-google | done | 214 of 214 | 6.5 h |
| matrix | done | 214 of 214, all on the engine in the tree | 4.6 h |
| classify | superseded | - | 4.0 h |
| fix | moving | 8 attempt(s) in 3 h | 0.6 h |
| txt | moving | 209 clean, 5 failing | 0.6 h |

Matrix is the change since the last pass: it read stopped, with only a fraction of its results on the
engine in the tree, and now reads done at 214 on the engine. The escalation that pass set against 27 Nov
did not have to fire.

## Trend

Today's row was already appended by an earlier pass, so nothing new was written to
benchmarks/PROGRESS.md and there was nothing to commit for it.

| | 27 Nov | 28 Nov |
|:--|--:|--:|
| docx open | 116 | 116 |
| txt failing | 6 | 6 |
| google measured | 206 | 206 |
| google clean | 46 | 48 |

Two of the four columns did not move, and the fixer's count beside that flat line is 8 attempt(s) in
3 h. That is the signal STEP 2 asks for and it is written into BLOCKERS.md. The movement that
contradicts a stall is google clean, up 2 on the day, with txt now reading 209 clean and 5 failing.

## Round

The phase is fix, with open classes still to close. STEP 4 C did not fire, because `round.py --reopen`
refuses unless the phase is done and the phase is fix.

## What this pass could not do

This watchdog's tool list carries no `cron` operation. STEP 3 and STEP 4 A and B did not run: no cron
was inspected, paused, resumed, deleted or recreated, and the id of no cron is reported here because
none was read. A paused or zombie cron cannot be moved by automation from this agent until a `cron`
operation is in its tool list. The exact calls are recorded in BLOCKERS.md.

STEP 4 D did not fire either: `status.py` reads SILENT on a claim that is minutes old inside a run that
is still in its slot, so the slot is held by a live run, not a dead one, and `--release-fixer --force`
was not run.
