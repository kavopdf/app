#!/usr/bin/env python3
"""status.py - is the fixer actually working, or has it wedged?

THE QUESTION THIS ANSWERS. A claim timestamp tells you when a run started, and a stale window
tells you when to give up on it. Neither tells you whether work is happening. On 16 Nov a run sat
for 32 minutes with zero attempts and nothing anywhere could say whether it was measuring 213
documents or stuck in a loop - the two look identical from outside.

So there are two new signals and this command reads them:

  * round.py --heartbeat --doing "<what I am doing>"   a beacon that carries the activity, not
    just the fact of being alive. A run that starts a long measurement says so BEFORE it starts,
    so silence afterwards means something.

  * the elapsed-versus-progress ratio. A run ninety minutes in with two attempts is not slow, it
    is not doing attempts. Two numbers that should move together, and don't.

    python3 tools/p2w-bench/status.py
    python3 tools/p2w-bench/status.py --json
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROUND = os.path.join(HERE, "ROUND.json")
RUN = os.path.join(HERE, "RUN.json")

WORKING_MIN = 8      # a beacon younger than this means work is being reported
SLOW_MIN = 20        # the stale window - past this the slot is up for takeover


def _j(p, d):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return d


def mins(ts):
    return None if not ts else (time.time() - ts) / 60.0


def collect():
    r = _j(ROUND, {})
    run = _j(RUN, {})
    started = r.get("fixer_started") or 0
    beat = r.get("fixer_last_beat") or started
    doing = r.get("fixer_doing") or ""
    doing_since = r.get("fixer_doing_since")

    claim_age = mins(started)
    # CLAIMING IS SPEAKING. This read fixer_last_beat only, so a run that claimed two minutes ago
    # inherited the PREVIOUS run's last beacon and read as silent for that whole age. Measured
    # 22 Nov 07:56: the :50 run claimed at 07:50, the previous run's last beat was 62 min old, and
    # status.py reported "SILENT - no beacon for 62 min ... or it has wedged" about a run that was
    # six minutes old and still cloning. A watchdog reading that would force-release a healthy run.
    #
    # The silence clock starts when the run claims, not before it existed.
    _beat_or_claim = max(beat or 0, started or 0)
    silent = mins(_beat_or_claim)
    elapsed = mins(run.get("started_ts"))
    attempts = run.get("attempts", 0) or 0

    # THE VERDICT IS THE BEACON, NOT THE CLAIM. round.py --heartbeat refreshes the claim as well
    # as the beacon, so on a live run the two agree - but the claim is what the stale check reads,
    # and the beacon is what says work is happening. Judging liveness by the claim age meant a run
    # that had been going twenty-five minutes while reporting every two was called dead.
    if not started:
        verdict, why = "IDLE", "no fixer claim - the slot is free"
    elif claim_age is not None and claim_age >= SLOW_MIN:
        # THE CLAIM IS THE AUTHORITY. It is refreshed only by the run itself - round.py --heartbeat
        # and attempt.py - so its age is "how long since the run last spoke for itself". Beacons
        # from a reading tool are not the run speaking, and judging liveness by them let an
        # observer's own calls make a blocked run look alive.
        verdict, why = "LIKELY DEAD", ("the run has not refreshed its claim for %.0f min, past the "
                                       "%d-min stale window - the next run will take it over"
                                       % (claim_age, SLOW_MIN))
    elif silent is not None and silent >= WORKING_MIN:
        verdict, why = "SILENT", ("no beacon for %.0f min. Either it is inside one long step it "
                                  "did not announce, or it has wedged" % silent)
    else:
        verdict, why = "WORKING", "beacon %.0f min ago" % (silent or 0)

    rate = (attempts / (elapsed / 60.0)) if elapsed and elapsed > 1 else None
    return {"claim_age_min": round(claim_age, 1) if claim_age is not None else None,
            "silent_min": round(silent, 1) if silent is not None else None,
            "doing": doing, "doing_for_min": round(mins(doing_since), 1) if doing_since else None,
            "run_started": run.get("started"), "elapsed_min": round(elapsed, 0) if elapsed else None,
            "attempts": attempts, "kept": run.get("kept", 0), "partial": run.get("partial", 0),
            "attempts_per_hour": round(rate, 1) if rate is not None else None,
            "verdict": verdict, "why": why}


def main(argv):
    d = collect()
    if "--json" in argv:
        print(json.dumps(d, indent=1))
        return 0

    L = ["=== FIXER STATUS ===", ""]
    L.append("verdict      : %s" % d["verdict"])
    L.append("why          : %s" % d["why"])
    L.append("")
    if d["claim_age_min"] is not None:
        L.append("claim        : %.0f min old" % d["claim_age_min"])
        L.append("last beacon  : %.0f min ago" % (d["silent_min"] or 0))
    if d["doing"]:
        L.append("doing        : \"%s\"%s" % (d["doing"],
                 (" for %.0f min" % d["doing_for_min"]) if d["doing_for_min"] is not None else ""))
    else:
        L.append("doing        : (not reported - the run has not said)")
    L.append("")
    if d["run_started"]:
        L.append("this run     : started %s, %.0f min elapsed"
                 % (d["run_started"], d["elapsed_min"] or 0))
        L.append("progress     : %d attempt(s) - %d kept, %d partial"
                 % (d["attempts"], d["kept"], d["partial"]))
        if d["attempts_per_hour"] is not None:
            L.append("rate         : %.1f attempts/hour" % d["attempts_per_hour"])
            if d["elapsed_min"] and d["elapsed_min"] > 40 and d["attempts_per_hour"] < 1.5:
                L.append("")
                L.append("               An attempt costs about seven minutes. Under 1.5 an hour over")
                L.append("               forty minutes is not a slow run, it is a run not making")
                L.append("               attempts - which is the thing to look at, not the clock.")
    else:
        L.append("this run     : no record")
    print("\n".join(L))
    return 0 if d["verdict"] in ("WORKING", "IDLE") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
