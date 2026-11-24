"""beacon.py - a liveness mark that every run-facing tool leaves behind.

THE QUESTION THIS ANSWERS, AND THE ONE IT REPLACES.

A cron run can show 'running' at the platform for sixteen minutes and produce nothing - no
attempt, no commit, no beacon - and nothing can tell whether it is measuring, reading a 1510-line
brief, or wedged. status.py could only report silence, not explain it.

So every tool the run touches marks the timeline on entry. That changes what silence MEANS:

    before   silence = the run might be doing a long thing, or might be dead. Unknown.
    after    silence = the run called NO tool at all in that window. That is a different and much
             narrower failure: the model spent the time inside one response - reading, or
             thinking - and it is diagnosable, because a run that is working calls tools.

The mark is deliberately cheap: one appended line, no file read, no lock. A beacon that costs
anything is a beacon people stop calling.

    from beacon import beat
    beat("pending.py", "reading the gate")

It never raises. A tool must not fail because a log line could not be written.
"""
import json, os, time

HERE = os.path.dirname(os.path.abspath(__file__))
TL = os.path.join(HERE, "TIMELINE.jsonl")
ROUND = os.path.join(HERE, "ROUND.json")


def beat(tool, what=""):
    """Append one line to TIMELINE.jsonl. Never raises, never blocks the caller.

    A READER'S FOOTSTEPS ARE NOT THE RUN'S WORK, AND P2W_BEAT_QUIET IS HOW A READER SAYS SO.
    report.py builds the report by calling pending.py, chain.py and gaps.py, and each of those
    beats under its OWN name - so a blacklist of "report.py" in report.py's beat counter never
    matched them. Measured 24 Nov 19:51, three report.py runs in a row on an idle repository:
    "Tool beats 25", then 26, then 27. The count moved between the report being written and
    lastmessage.py re-reading it, so no report could be validated or committed while the run was
    live - the gate refused a report against its own next reading.
    """
    if os.environ.get("P2W_BEAT_QUIET"):
        return
    try:
        ist = time.strftime("%H:%M:%S", time.gmtime(time.time() + 19800))
        rec = {"t": time.time(), "ist": ist, "ev": "beat",
               "d": ("%s: %s" % (tool, what)).strip(": ")}
        with open(TL, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass
    # A BEACON MUST NOT REFRESH THE CLAIM. Found by doing it to myself: during a verification pass
    # on 17 Nov I ran pending, report, classrow, gaps, handoff and chain in a row, and each one
    # refreshed the claim of a run that had been blocked for thirty-three minutes. status.py then
    # reported WORKING with the claim zero minutes old - a dead run made to look alive by an
    # observer. Anyone running these tools would do the same, and so would the watchdog.
    #
    # Only the run itself may hold the slot, so only the run may refresh it: round.py --heartbeat
    # and attempt.py do that, because they are called by the run about its own work. A tool that
    # merely reads state must not write the one field the stale check depends on.
