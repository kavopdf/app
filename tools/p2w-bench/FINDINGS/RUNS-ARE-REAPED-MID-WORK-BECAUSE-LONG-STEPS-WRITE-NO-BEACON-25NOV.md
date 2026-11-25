# Zero of the last sixty fixer runs ended on their own terms

## Measured from the timeline

    events: beat 5860 | attempt 152 | claim 87 | release 71 | killed 66

66 killed against 87 claims. 152 attempts between them - 1.75 per claim, so runs are not idle, they are cut
off. `RUN-HISTORY.json` shows the shape directly:

    08:14 -> (never) | killed - slot cleared by a force release | attempts=4
    09:25 -> (never) | killed - slot cleared by a force release | attempts=0
    09:59 -> (never) | killed - never released the slot        | attempts=0
    09:59 -> (never) | killed - slot cleared by a force release | attempts=1

`ended: (never)`. A run that is killed never closes its record.

## The code already knows, and says so

`round.py:197`:

    "The ledger says the window was too tight, and says it without ambiguity: of the last 60 fixer runs,
     ZERO ended on their own terms. 42 were 'killed - slot cleared by a force release' and 18 'killed -
     never released the slot'. Every single run was reaped, and 48 of the 60 kept nothing - not because
     the class was wrong but because the run died inside its work."

## And the reason, in the same comment

    "a gverify batch pushes 60 documents through Google upload, PDF export and 42 checks, a corpus rebuild
     is hours, and two background subagents run for as long as they like. None of that is a 290 s call,
     and a run inside any of it writes no beacon."

That is the fault. The heartbeat exists - `attempt.py` writes `fixer_last_beat`, `round.py` reads the newest
of claim/beat/doing-since - but it is written when a TOOL CALLS, and a long operation is one tool call that
runs for an hour. Inside it the run writes nothing, so at 45 minutes it is indistinguishable from a corpse.

## The value was never raised after the heartbeat landed

`round.py:204`:

    CLAIM_STALE_MIN = {"fixer": 45, "baseline": 45, "classifier": 20}

and its own comment above it:

    "45 is what baseline uses, and it is the window the fixer had before the heartbeat existed."

The comment records that 45 predates the heartbeat, and the constant was left at 45 anyway. So the reader was
improved and the window it guards was not.

## What this costs

48 of 60 runs kept nothing, and the cause was not the class, the patch or the measurement - it was the run
dying inside its own work. Every attempt that never got recorded, every finding half-written, every engine
change reverted by the next run: this is upstream of all of them. It also explains the reverted attempts
better than anything I proposed earlier, without proving it.

## What to change

The window has to cover the longest single step a run takes, not the longest tool call it makes. A gverify
batch of 60 documents is tens of minutes; a corpus rebuild is hours; a subagent runs as long as it likes.

Two ways, and they compose:

1. WRITE A BEACON FROM INSIDE THE LONG STEPS. `p2w.py --force` and the gverify batch should beat as they
   progress. That makes the heartbeat mean what it says - "this run is alive" - for the whole run.

2. RAISE THE WINDOW to cover the longest step, 45 -> 150, accepting that a genuinely dead run then costs 150
   minutes. The relay cron at :10 is the safety net for that, and it only has to find the slot free once.

Option 1 is the honest fix and option 2 is the cheap one. Doing only 2 without 1 means the window is still a
guess about how long a step takes; doing only 1 without 2 means a step that forgets to beat is still fatal.

Not changed here: this is the slot, and a wrong change to it lets two runs corrupt the engine. Recorded with
the measurement so the change is made against evidence rather than against my earlier guess, which was that
the heartbeat did not exist at all. It does. It is just not written during the work.
