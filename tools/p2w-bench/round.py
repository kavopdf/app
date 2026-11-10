#!/usr/bin/env python3
"""
round.py - the state machine that runs the whole thing three times.

THE SHAPE THE USER ASKED FOR
  Round 1: measure all 208, separate the defects, fix them all.
  When every document is done - however long that takes - start again:
  Round 2: a fresh baseline on the fixed engine, separate, fix.
  Round 3: the same once more. Then stop.

WHY A STATE FILE AND NOT THREE CRONS GUESSING
  Three crons on timers will not do this by themselves. The baseline fires every
  four hours whether or not the fixer has finished; the fixer fires whether or not
  anything has been measured; and nothing knows what a round is. Each one would
  keep doing its own job forever, which is exactly the behaviour that produced
  208 measurements and no progress in one direction.

  ROUND.json is the only thing that decides whose turn it is. Every cron reads its
  phase first and does nothing if the phase is not its own. One file, one writer
  per phase, no race.

THE PHASES
  measure    baseline runs, 20 documents a run, until all 208 have a score
  classify   classifier runs once and writes the ranked classes
  fix        fixer runs, one class a run, until no class is OPEN
  done       three rounds finished; every cron reports and stops

WHAT ENDS A PHASE
  measure -> classify   when every row in BASELINE.md has a score
  classify -> fix       when DEFECT-CLASSES.md is newer than BASELINE.md
  fix -> measure        when classify.py reports no OPEN class
  fix -> done           when that happens in round 3

USAGE
  python3 tools/p2w-bench/round.py                 # status
  python3 tools/p2w-bench/round.py --phase         # just the phase, for a cron to compare
  python3 tools/p2w-bench/round.py --advance       # move to the next phase
  python3 tools/p2w-bench/round.py --close-round   # archive, reset, next round
  python3 tools/p2w-bench/round.py --force-round N # set the round by hand
"""
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "ROUND.json")
BASE = os.path.join(HERE, "BASELINE.md")
CLASSES = os.path.join(HERE, "DEFECT-CLASSES.md")
ATTEMPTS = os.path.join(HERE, "ATTEMPTS.json")

ROUNDS_TOTAL = 3
PHASES = ["measure", "classify", "fix", "done"]

# A fixer attempt takes about two hours and the fixer is scheduled every two
# hours, so two runs can land on top of each other - both editing the engine,
# both committing, one overwriting the other. This claim makes the second run
# step aside instead. It expires, because a run that dies must not block the
# next one forever.
FIXER_STALE_MIN = 100


def load():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE, encoding="utf-8"))
        except Exception:
            pass
    return {"round": 1, "rounds_total": ROUNDS_TOTAL, "phase": "measure",
            "started": time.time(), "history": []}


def save(s):
    json.dump(s, open(STATE, "w", encoding="utf-8"), indent=2, sort_keys=True)


def rows():
    """(total, scored) from BASELINE.md. Header found by its first cell."""
    total = scored = 0
    if not os.path.exists(BASE):
        return 0, 0
    for line in open(BASE, encoding="utf-8"):
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not cells[0] or cells[0].lower() == "document":
            continue
        total += 1
        if re.match(r"\d+\s*/\s*\d+", cells[1] if len(cells) > 1 else ""):
            scored += 1
    return total, scored


def open_classes():
    """Count classes still marked OPEN in DEFECT-CLASSES.md."""
    if not os.path.exists(CLASSES):
        return None
    n = 0
    for line in open(CLASSES, encoding="utf-8"):
        if line.startswith("| ") and not line.startswith("|---"):
            if line.rstrip().endswith("| OPEN |"):
                n += 1
    return n


def status(s=None):
    s = s or load()
    total, scored = rows()
    oc = open_classes()
    print("round %d of %d   phase: %s" % (s["round"], s["rounds_total"], s["phase"]))
    print("  documents scored : %d of %d" % (scored, total))
    print("  open classes     : %s" % ("-" if oc is None else oc))
    if s["phase"] == "measure":
        print("  next             : baseline runs until %d of %d are scored" % (total or 208, total or 208))
    elif s["phase"] == "classify":
        print("  next             : classifier runs once")
    elif s["phase"] == "fix":
        print("  next             : fixer runs until no class is OPEN")
    else:
        shipped = s.get("apk_shipped") or ""
        print("  apk shipped      : %s" % (shipped or "not yet"))
        print("  next             : %s" % ("nothing - already shipped" if shipped
                                            else "the APK cron ships once, on its next run"))
    for h in s.get("history", [])[-4:]:
        print("  was: round %s %s -> %s" % (h.get("round"), h.get("phase"), h.get("at", "")))
    return s


def claim_fixer():
    """Return 0 if this run may proceed, 1 if a previous one is still working."""
    s = load()
    last = s.get("fixer_started") or 0
    age_min = (time.time() - last) / 60.0 if last else 1e9
    if age_min < FIXER_STALE_MIN:
        print("fixer busy - previous run started %d min ago (stale after %d min)"
              % (age_min, FIXER_STALE_MIN))
        return 1
    s["fixer_started"] = time.time()
    save(s)
    print("fixer claimed at %s" % time.strftime("%H:%M"))
    return 0


def release_fixer():
    s = load()
    s["fixer_started"] = 0
    save(s)
    print("fixer released")
    return 0


def main(argv):
    s = load()

    if "--apk-status" in argv:
        # "may ship" only when every round is finished and nothing was shipped yet.
        if s.get("phase") != "done":
            print("phase is %s - not done" % s.get("phase"))
            return 1
        done = s.get("apk_shipped") or ""
        if done:
            print("already shipped %s - nothing to do" % done)
            return 1
        print("may ship - all %s rounds done, nothing shipped yet" % s.get("rounds_total"))
        return 0

    if "--mark-apk-shipped" in argv:
        v = argv[argv.index("--mark-apk-shipped") + 1] if "--mark-apk-shipped" in argv else "yes"
        s["apk_shipped"] = v
        save(s)
        print("apk marked shipped: %s" % v)
        return 0

    if "--claim-fixer" in argv:
        return claim_fixer()

    if "--release-fixer" in argv:
        return release_fixer()

    if "--phase" in argv:
        print(s["phase"])
        return 0

    if "--force-round" in argv:
        n = int(argv[argv.index("--force-round") + 1])
        s["round"] = n
        s["phase"] = "measure"
        save(s)
        print("round forced to %d, phase measure" % n)
        return 0

    if "--advance" in argv:
        i = PHASES.index(s["phase"])
        if i < len(PHASES) - 1:
            s.setdefault("history", []).append(
                {"round": s["round"], "phase": s["phase"], "at": time.strftime("%Y-%m-%d %H:%M")})
            s["phase"] = PHASES[i + 1]
            save(s)
        print(s["phase"])
        return 0

    if "--close-round" in argv:
        total, scored = rows()
        # Archive the finished round so its numbers are never lost.
        if os.path.exists(BASE):
            shutil.copy(BASE, os.path.join(HERE, "ROUND-%d.md" % s["round"]))
        # Always write the archive, even when nothing was attempted. A round that
        # closed with zero attempts is a fact worth keeping - it means the fixer
        # never ran, or every class was already parked - and silence would hide it.
        if os.path.exists(ATTEMPTS):
            shutil.copy(ATTEMPTS, os.path.join(HERE, "ATTEMPTS-round-%d.json" % s["round"]))
        else:
            json.dump({}, open(os.path.join(HERE, "ATTEMPTS-round-%d.json" % s["round"]),
                               "w", encoding="utf-8"), indent=2)

        s.setdefault("history", []).append(
            {"round": s["round"], "phase": "closed", "scored": scored,
             "at": time.strftime("%Y-%m-%d %H:%M")})

        if s["round"] >= s["rounds_total"]:
            s["phase"] = "done"
            save(s)
            print("round %d closed - all %d rounds done" % (s["round"], s["rounds_total"]))
            return 0

        # Reset for the next round: every score empty, so the baseline has work
        # to do again and the ratchet is the only thing that remembers the past.
        out = []
        # A missing BASELINE.md must not crash a round close - the archive and
        # the phase move still have to happen, or the pipeline is stuck forever
        # in a round it cannot leave.
        base_lines = open(BASE, encoding="utf-8").readlines() if os.path.exists(BASE) else []
        for line in base_lines:
            if line.startswith("| ") and not line.startswith("|---"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if cells and cells[0] and cells[0].lower() != "document":
                    out.append("| %s |  |  |  |  |  |" % cells[0])
                    continue
            out.append(line.rstrip("\n"))
        open(BASE, "w", encoding="utf-8").write("\n".join(out) + "\n")

        # A new round means new defects to find; classes start fresh, but the
        # attempt ledger is archived first so the history survives.
        if os.path.exists(ATTEMPTS):
            os.remove(ATTEMPTS)

        s["round"] += 1
        s["phase"] = "measure"
        s["started"] = time.time()
        s["fixer_started"] = 0
        s["apk_shipped"] = ""
        save(s)
        print("round %d closed, round %d begins in phase measure" % (s["round"] - 1, s["round"]))
        return 0

    status(s)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
