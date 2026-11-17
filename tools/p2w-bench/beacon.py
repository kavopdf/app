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
    """Append one line to TIMELINE.jsonl. Never raises, never blocks the caller."""
    try:
        ist = time.strftime("%H:%M:%S", time.gmtime(time.time() + 19800))
        rec = {"t": time.time(), "ist": ist, "ev": "beat",
               "d": ("%s: %s" % (tool, what)).strip(": ")}
        with open(TL, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass
    # and refresh the claim, so the stale check sees a live run rather than a dead one
    try:
        s = json.load(open(ROUND, encoding="utf-8"))
        if s.get("fixer_started"):
            s["fixer_started"] = time.time()
            s["fixer_last_beat"] = time.time()
            if what:
                s["fixer_doing"] = what
                s["fixer_doing_since"] = time.time()
            json.dump(s, open(ROUND, "w", encoding="utf-8"), indent=1)
    except Exception:
        pass
