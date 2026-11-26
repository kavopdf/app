# A `--heartbeat` after a rebase moves the run window and zeroes the attempt counter

**26 Nov 2026, fixer slot 10:54.** Reproduced by accident, and the evidence is in this run's own state.

## What happened

1. `attempt.py --class 18_displacement --outcome lead` ran at about 06:04 UTC and, by its own code
   (`attempt.py:166-180`), bumped `RUN.json` `attempts` 0 -> 1. That bump is there precisely so
   `report.py`'s self-check stops printing *"attempts: RUN.json counter 0 vs ATTEMPTS.json history 1"*.
2. A `git pull --rebase origin main` then brought in state committed by another cron.
3. The next `round.py --heartbeat` printed **"run window reset - RUN.json described the run before this
   claim"** and rewrote `RUN.json` with `attempts: 0` (`round.py:1195-1210`), setting `started_ts` and
   `window_for_claim` to the new claim time.
4. `report.py` then printed the disagreement again: **1 attempt recorded in the history, 0 in the
   counter.**

## Why the guard does not catch it

The reset condition is `started_ts < claimed and window_for_claim != claimed`. It is a test on the
*clock*, not on the *work*: a window that moved for a legitimate reason (a re-claim after the pull) is
indistinguishable from a window that never belonged to this run, so the counter is thrown away with the
timestamps. `attempt.py`'s comment says the counter exists to keep the two files agreeing; the reset
undoes it one step later.

## What I did, and what I did not

I did not change `round.py`. It is the lock two fixer crons share, the change needs the release path
and the `_attempts_this_run()` guard in `attempt.py:236` re-read together, and a wrong edit there
either loses a slot or lets two runs hold it. I set `RUN.json` `attempts` to 1, which is the truth for
this run, and `report.py`'s self-check then read *"every field agrees with its second source"*.

## The fix I would make, for a run that has the slot to test it

Carry the count across the reset instead of zeroing it: when `window_for_claim != claimed` but the
new `started_ts` is **later than** the records already in `ATTEMPTS.json` for this claim's class, sum
those records into `attempts` rather than writing 0. Or simpler and safer: never zero `attempts` in the
reset at all - set it from the number of records in `ATTEMPTS.json` whose `at` falls inside the new
window. Both are the same number when the window is right, and the second cannot invent a count.
