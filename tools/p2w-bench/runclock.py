#!/usr/bin/env python3
"""How long has this run been going - and is it time to write the report yet?

WHY THIS EXISTS. The brief told a run "it ends when the work does" and never said how long the work was.
So a run did one attempt, wrote an accurate report, and stopped - which is what it had been told to do.
Measured over 31 timed fixer runs: median 36 minutes, mean 42, and only 3 of 31 reached 90. Ten finished
inside twenty. The user's target is "har ek run 1.5 hours se zyada ka hona chahiye", and a target nobody
can measure is not a target.

This prints the clock. Nothing else. A run reads it before writing its report and knows whether it is
finishing or quitting early.

    python3 tools/p2w-bench/runclock.py          # the verdict
    python3 tools/p2w-bench/runclock.py --json   # the numbers

Exit 0 = keep working. Exit 1 = the report is due now.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ROUND = os.path.join(HERE, "ROUND.json")

# The slot is 90 minutes of work. The report is the last 15 of them, because a report that is written and
# not committed is worth nothing - and committing, pushing and releasing takes real time.
# NO STOPPING POINT. There used to be a 90-minute budget with the report due at 75, and the effect was
# measurable: median 37 minutes, median 1.0 attempt, 32 of 32 runs releasing themselves. The user's rule is
# that a run works until the platform stops it or a real limit is hit, and that a run with work left never
# ends on its own. A minute count is a number to stop at, so there is no longer one.
#
# What replaces it: the report is refreshed and committed after EVERY attempt, so whichever moment the
# platform ends the run, the last committed report is current and the next run loses nothing. Writing it once
# at the end meant the report had to be scheduled, and scheduling it is what created the stopping point.
BUDGET_MIN = None
REPORT_AT_MIN = None

# A CHECKPOINT IS NOT A STOPPING POINT. There is no time at which the run ends, but there IS a time by which
# the report must already be complete and committed - because the platform can end the run at any moment and a
# run that dies with nothing written teaches the next one nothing.
#
# 60 minutes: inside the measured longest real run (105 min, 70 beacons, 3 attempts), inside the platform's own
# limits (no run-length cap; 300 s per command, 10 min idle, 30 min with no tool call), and late enough that
# four to six attempts have happened. Past it the run keeps working - the checkpoint only guarantees that
# whatever it has done so far is already on disk and pushed.
CHECKPOINT_MIN = 60


def _claimed_at():
    """When the current claim was made, as an epoch second. None if there is no claim.

    THE FIELD IS fixer_started. ROUND.json keeps a flat record - fixer_started, fixer_last_beat,
    fixer_engine_at_claim - and not a nested "fixer" object, so the first version of this tool read
    nothing and told every run it held no slot. Read what is there.
    """
    try:
        d = json.load(open(ROUND, encoding="utf-8"))
    except Exception:
        return None
    for key in ("fixer_started", "fixer_claimed_ts", "fixer_at_ts"):
        v = d.get(key)
        if isinstance(v, (int, float)) and v > 0:
            return float(v)
    # older records carry only an HH:MM string; fall back to today
    v = d.get("fixer_started")
    if isinstance(v, str) and ":" in v:
        try:
            hh, mm = (v.split(":") + ["0"])[:2]
            lt = time.localtime()
            return time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday,
                                int(hh), int(mm), 0, 0, 0, -1))
        except Exception:
            return None
    return None


def main(argv):
    started = _claimed_at()
    if not started:
        print("no claim in ROUND.json - this run does not hold the slot, so there is no clock to read")
        print("claim first: python3 tools/p2w-bench/round.py --claim-fixer")
        return 2

    elapsed = (time.time() - started) / 60.0
    left = None
    due = False
    checkpoint = elapsed >= CHECKPOINT_MIN

    if "--json" in argv:
        print(json.dumps({"elapsed_min": round(elapsed, 1), "stopping_point": None,
                          "checkpoint_min": CHECKPOINT_MIN, "checkpoint_passed": checkpoint,
                          "report_due": False}))
        return 0

    print("  claimed        : %s" % time.strftime("%H:%M", time.localtime(started)))
    print("  elapsed        : %.0f min" % elapsed)
    print("  stopping point : none. The run ends when the platform ends it, or when the engine")
    print("                   genuinely blocks you - never because a clock said so.")
    print()
    if checkpoint:
        print("  CHECKPOINT PASSED. Not a reason to stop - a reason to make sure the report is")
        print("  already complete and committed, because the platform can end this run at any moment.")
        print("  Write the FULL report now, commit it, push it. Then carry on with the next attempt.")
    else:
        print("  CHECKPOINT IN %.0f MIN." % (CHECKPOINT_MIN - elapsed))
        print("  Until then: refresh and commit the report after EVERY attempt, so a kill loses nothing.")
    print()
    print("  KEEP WORKING. There is no stopping point in this file.")
    print("  Next attempt: python3 tools/p2w-bench/classpick.py --leverage")
    print("                python3 tools/p2w-bench/allreports.py --unread")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
