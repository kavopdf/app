# `runclock.py`'s elapsed time is reset by `attempt.py`, so the 75-minute checkpoint cannot fire after the first attempt

**Measured 26 Nov 2026** on this pod, in one run, by running the two tools back to back.

    python3 tools/p2w-bench/runclock.py      ->  claimed 14:29   elapsed 22 min
    ... attempt.py --class ... --outcome lead ...
    python3 tools/p2w-bench/runclock.py      ->  claimed 15:05   elapsed  0 min

`attempt.py` refreshes the claim record's timestamp, and `runclock.py` computes `elapsed` from that
same field, so recording an attempt at minute 36 reports a run that has just started. Two things
follow, and the second is the one that matters:

1. `round.py --heartbeat` does **not** do this — measured: heartbeat, then clock, still `elapsed 8
   min`. So it is `attempt.py` specifically, not the beacon.
2. **The 75-90 minute checkpoint can never be reached by a run that records an attempt**, which is
   every run. `runclock.py` exits 0 ("keep working") from then on no matter how long the run has
   been going, so the tool the prompt tells a run to consult before writing its report is the one
   instrument that cannot say the report is due.

The user's complaint — 31 timed runs, median 36 minutes, only 3 of 31 reached 90 — is consistent with
this: a run's only clock restarts every time it does the thing it is supposed to do. Whether that is
the whole cause is not measured here and is not claimed; what is measured is that the clock cannot
tell a run how long it has been working after its first attempt.

**The fix is one line** — `attempt.py` should write its own record and leave the claim's `at`
untouched, or `runclock.py` should read the claim's *original* claim time from the claim commit's
author date rather than the record's refreshed field. It is not landed here: `attempt.py` is the
ledger, a wrong edit to it silently mis-credits every future attempt, and this run had no slot left to
re-measure the ledger after the change. It belongs to a run that starts with it.
