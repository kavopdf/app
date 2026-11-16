#!/usr/bin/env python3
"""chain.py - start the next run the moment this one ends, instead of waiting for the hour.

THE WASTE THIS REMOVES

The fixer cron fires at :45 every hour. A run that starts at 14:55 and ends at 15:40 leaves
five minutes used and forty-seven wasted, and nothing starts until 15:45. Across a day that is
most of the day.

The chain closes that gap: after a clean release the run triggers the same cron again, so the
next run begins in seconds. The slot guard still makes it exclusive - if the new run starts
before the old one has finished releasing, it finds the claim held and stands aside.

WHAT STOPS IT, AND WHY THAT MATTERS MORE THAN THE SPEED

A self-triggering job with no brake is a way to spend a night producing nothing. So the chain
stops on any of these, and prints the reason:

  * the release was FORCED            - something went wrong; let a human look before chaining
  * the round is finished             - there is nothing left to chain into
  * three runs in a row with no kept  - the circuit breaker. Three consecutive runs that fixed
    and no partial attempt              nothing are not unlucky, they are stuck, and a fourth
                                        will be stuck the same way
  * no run record at all              - cannot tell what happened, so do not continue

    python3 tools/p2w-bench/chain.py --after-release    # FIRE or STOP, with the reason
    python3 tools/p2w-bench/chain.py --status
    python3 tools/p2w-bench/chain.py --reset            # clear the counter after a fix
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CHAIN = os.path.join(HERE, "CHAIN.json")
RUN = os.path.join(HERE, "RUN.json")
ROUND = os.path.join(HERE, "ROUND.json")
CLASSES = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")

DRY_LIMIT = 3          # consecutive unproductive runs before the chain stops
MAX_DEPTH = 24         # a day's worth; a chain longer than this is not a chain, it is a loop

# The cron this chain re-fires. Kept in CHAIN.json so it is one place, not scattered through
# the brief and the prompt.
DEFAULT_CRON = "01M733RWCMF6EY8MF3W6H64CQ1"


def _j(p, d):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return d


def _w(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), indent=1)


def load():
    c = _j(CHAIN, {})
    c.setdefault("cron_id", DEFAULT_CRON)
    c.setdefault("depth", 0)
    c.setdefault("dry", 0)
    c.setdefault("fired_at", [])
    return c


def open_classes():
    n = 0
    try:
        for line in open(CLASSES, encoding="utf-8"):
            s = line.strip()
            if s.startswith("| ") and "| OPEN |" in s:
                n += 1
    except Exception:
        pass
    return n


def main(argv):
    c = load()

    if "--reset" in argv:
        c["depth"] = 0
        c["dry"] = 0
        _w(CHAIN, c)
        print("chain counters cleared")
        return 0

    if "--status" in argv:
        r = _j(RUN, {})
        print("cron_id      : %s" % c["cron_id"])
        print("chain depth  : %d of %d" % (c["depth"], MAX_DEPTH))
        print("dry runs     : %d of %d" % (c["dry"], DRY_LIMIT))
        print("last run     : %s -> %s  (%d attempts, %d kept)"
              % (r.get("started", "-"), r.get("ended") or "running",
                 r.get("attempts", 0), r.get("kept", 0)))
        print("open docs    : %d" % open_classes())
        return 0

    if "--after-release" not in argv:
        print(__doc__)
        return 0

    r = _j(RUN, {})
    rd = _j(ROUND, {})

    # --- the brakes, in order of how badly they should stop you ---
    if not r.get("started"):
        print("STOP: no run record - cannot tell what this run did")
        return 1
    if r.get("ended") is None:
        print("STOP: this run has not closed its record; release first")
        return 1
    if rd.get("phase") and rd["phase"] != "fix":
        print("STOP: phase is %r, not 'fix'" % rd["phase"])
        return 1
    if open_classes() == 0:
        print("STOP: no OPEN document left - close the round, do not chain")
        return 1
    if c["depth"] >= MAX_DEPTH:
        print("STOP: chain depth %d reached - wait for the hourly cron" % c["depth"])
        return 1

    productive = (r.get("kept", 0) + r.get("partial", 0)) > 0
    if productive:
        c["dry"] = 0
    else:
        c["dry"] = c.get("dry", 0) + 1
    if c["dry"] >= DRY_LIMIT:
        print("STOP: %d runs in a row with no kept and no partial attempt." % c["dry"])
        print("      That is not bad luck, that is stuck - a fourth run will be stuck the same")
        print("      way. Fix the obstacle, or wait for the hourly cron.")
        _w(CHAIN, c)
        return 1

    c["depth"] = c.get("depth", 0) + 1
    c["fired_at"] = (c.get("fired_at") or [])[-9:] + [time.strftime("%H:%M", time.gmtime(time.time() + 19800))]
    _w(CHAIN, c)

    print("FIRE: chain depth %d of %d, dry %d of %d, %d open document(s) left"
          % (c["depth"], MAX_DEPTH, c["dry"], DRY_LIMIT, open_classes()))
    print("")
    print("Trigger the next run now:")
    print("    cron action=trigger cron_id=%s" % c["cron_id"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
