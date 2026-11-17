#!/usr/bin/env python3
"""gaps.py - every silent stretch in a run, measured to the second.

THE CLAIM THIS TOOL EXISTS TO SETTLE. "Did the cron stop?" is not answerable from a start time
and an end time. A run can spend its whole life in one long measurement - which is not a stop -
or wedge for six minutes in the middle of a loop, which is. The difference is whether anything
was written down between two moments.

So every event appends a line to TIMELINE.jsonl with an epoch float: the claim, every beacon
(--heartbeat --doing), every attempt, every release. gaps.py reads those lines and reports each
interval longer than the threshold, with what was happening on either side of it.

    python3 tools/p2w-bench/gaps.py                  # threshold 5 minutes
    python3 tools/p2w-bench/gaps.py --threshold 2
    python3 tools/p2w-bench/gaps.py --last           # only the most recent run

Exit 0 when nothing exceeds the threshold, 1 when something does - so a caller can gate on it.

THE HONEST LIMIT, stated here so nobody reads more into this than it says: a gap is a stretch
with no event. If a run announces "measuring 213 documents" and then goes quiet for twenty
minutes, this tool reports a twenty-minute gap AND the announcement - and the reader decides
whether that was a long measurement or a wedge. It cannot know. What it can do is make sure the
reader is never guessing about whether the gap was there.
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
TL = os.path.join(HERE, "TIMELINE.jsonl")
DEFAULT_THRESHOLD_MIN = 5.0


def load():
    out = []
    try:
        for line in open(TL, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    except Exception:
        pass
    return out


def runs(events):
    """Split the timeline into runs at each claim."""
    out, cur = [], None
    for e in events:
        if e.get("ev") == "claim" and "fixer" in (e.get("d") or ""):
            cur = {"start": e, "events": [e], "end": None}
            out.append(cur)
        elif cur is not None:
            cur["events"].append(e)
            if e.get("ev") == "release":
                cur["end"] = e
    return out


def between_runs(rs, threshold_min):
    """The gap nobody was measuring: one run released, the next did not start.

    This is the 15 hours of 16-17 Nov. Every run inside the timeline looked healthy - the last
    one released normally at 18:10 - and then nothing at all until 09:21 the next morning, because
    the workspace usage budget ran out and the platform paused all three crons after five
    failures. gaps.py measured gaps INSIDE a run, so the largest outage the pipeline has had was
    invisible to it: there was no run to contain the gap.

    A pipeline that is supposed to run 24/7 is defined as much by the space between its runs as by
    the runs themselves.
    """
    out = []
    for a, b in zip(rs, rs[1:]):
        end = a["end"].get("t") if a["end"] else None
        if not end:
            continue
        start = b["start"].get("t") or 0
        d = (start - end) / 60.0
        if d > threshold_min:
            out.append({"from_ist": a["end"].get("ist"), "to_ist": b["start"].get("ist"),
                        "minutes": round(d, 1)})
    return out


def analyse(run, threshold_min):
    evs = run["events"]
    gaps = []
    for a, b in zip(evs, evs[1:]):
        d = (b.get("t") or 0) - (a.get("t") or 0)
        if d > threshold_min * 60:
            gaps.append({"from_ist": a.get("ist"), "to_ist": b.get("ist"),
                         "from_ev": a.get("ev"), "to_ev": b.get("ev"),
                         "from_d": (a.get("d") or "")[:70], "to_d": (b.get("d") or "")[:70],
                         "minutes": round(d / 60.0, 1)})
    # the tail: last event to now (or to the release)
    last = evs[-1]
    end_t = run["end"].get("t") if run["end"] else time.time()
    tail = (end_t - (last.get("t") or 0)) / 60.0
    if tail > threshold_min:
        gaps.append({"from_ist": last.get("ist"), "to_ist": "(now)" if not run["end"] else run["end"].get("ist"),
                     "from_ev": last.get("ev"), "to_ev": "end" if run["end"] else "STILL OPEN",
                     "from_d": (last.get("d") or "")[:70], "to_d": "",
                     "minutes": round(tail, 1), "tail": True})
    return gaps


def main(argv):
    thr = DEFAULT_THRESHOLD_MIN
    if "--threshold" in argv:
        thr = float(argv[argv.index("--threshold") + 1])
    events = load()
    if not events:
        print("no TIMELINE.jsonl yet - nothing to measure")
        return 0
    rs = runs(events)
    if "--last" in argv:
        rs = rs[-1:]
    if not rs:
        print("no fixer run in the timeline")
        return 0

    bad = 0
    print("=== TIMELINE GAPS (anything over %.0f min) ===" % thr)
    print("")
    for r in rs:
        st = r["start"].get("ist")
        en = r["end"].get("ist") if r["end"] else "(open)"
        span = ((r["end"].get("t") if r["end"] else time.time()) - (r["start"].get("t") or 0)) / 60.0
        beats = sum(1 for e in r["events"] if e.get("ev") == "beat")
        atts = sum(1 for e in r["events"] if e.get("ev") == "attempt")
        g = analyse(r, thr)
        print("run %s -> %s   %.0f min   %d beacon(s), %d attempt(s)"
              % (st, en, span, beats, atts))
        if not g:
            print("   no gap over %.0f min" % thr)
        else:
            bad += len(g)
            for x in g:
                print("   GAP %5.1f min  %s (%s) -> %s (%s)"
                      % (x["minutes"], x["from_ist"], x["from_ev"], x["to_ist"], x["to_ev"]))
                if x.get("from_d"):
                    print("        was doing: %s" % x["from_d"])
                if x.get("tail"):
                    print("        this is the tail: the run stopped writing and never came back")
        print("")
    # and the space between runs, which is where a 24/7 pipeline actually dies
    br = between_runs(rs, thr)
    if br:
        print("=== BETWEEN RUNS ===")
        print("")
        for x in br:
            print("   GAP %6.1f min  %s (released) -> %s (next claim)" % (x["minutes"], x["from_ist"], x["to_ist"]))
        print("")
        print("   A pipeline meant to run 24/7 is defined by the space between its runs as much as")
        print("   by the runs. Nothing was working here - check whether the crons were paused.")
        print("")
        bad += len(br)

    if bad:
        print("%d gap(s) over %.0f min. A gap is silence, not proof of a stop - check the"
              % (bad, thr))
        print("'was doing' line: an announced long measurement explains it, nothing does not.")
        return 1
    print("No gap over %.0f min in any run." % thr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
