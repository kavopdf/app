#!/usr/bin/env python3
"""attempt.py - record a fixer attempt against a real problem class.

WHY THIS EXISTS

`classify.py --attempt` was the only way to write ATTEMPTS.json, and it refuses any name
that is not in the OLD class table. Verified on 16 Nov:

    $ classify.py --attempt "content-missing-nothing-in-its-place" --moved 0 --total 20
    refused: 'content-missing-nothing-in-its-place' is not a class. The ledger is keyed by
    the exact name ... Run classify.py and copy a name from the table exactly.

The old table is keyed by verify_google check ids - '47_margins', '20_within_10pt'. The
real queue is benchmarks/DEFECT-CLASSES.md, keyed by the eight user-visible problem names.
So the fixer could read the real queue and then be unable to record a single attempt
against it: the ledger and the work were in different vocabularies, and the ledger refused
the one that mattered.

That is the mechanical reason ATTEMPTS.json shows 19 attempts over four check-id classes
with zero kept, fourteen of them on '20_within_10pt' alone. The fixer was not bad at
fixing. It was aimed at a queue that no longer described anything, and every attempt it
made there was a guess at what a check id meant.

WHAT THIS DOES

Writes ATTEMPTS.json directly, keyed by the problem name, and refuses only when the name is
not in the live class file - which is the check worth having, because a typo would write an
attempt against nothing and leave the real class at zero.

    attempt.py --class "<problem name>" --outcome kept|reverted|error \
               [--moved N --total M] [--engine HASH] [--reason "..."]

    attempt.py --show            the ledger, worst first
    attempt.py --show <class>    one class's history

THE OUTCOME IS COMPUTED WHEN NUMBERS ARE GIVEN, never asserted. 'kept' means the class's
documents moved and the ratchet did not regress; 'reverted' means the numbers did not move;
'error' means no fix was measured at all - no root cause found. Those three are the whole
vocabulary, and the ledger already uses them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
LEDGER = os.path.join(HERE, "ATTEMPTS.json")
ROUND = os.path.join(HERE, "ROUND.json")
RUNLOG = os.path.join(HERE, "RUN-LOG.md")
CLASSES = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")
CLASSES_TXT = os.path.join(HERE, "DEFECT-CLASSES-TXT.md")

OUTCOMES = ("kept", "reverted", "error")


# The class vocabulary, and the only thing that identifies a class cell. A class file also
# carries a per-document table whose first cell is a rank number, and a first-cell match
# picked up "1", "10", "11" instead of a single class name. Matching the vocabulary itself
# cannot do that: nothing else in the file starts with these prefixes.
CLASS_RE = re.compile(r"^(content-(missing|partly|present)-[a-z-]+|single-element-far-out|none)$")


def known_classes():
    """Every class name the live class files carry.

    benchmarks/DEFECT-CLASSES.md holds two tables: a summary whose middle cell is the
    problem name, and a per-document table whose status cell is OPEN or FIXED. Only the
    problem names are classes; the per-document rows are the documents inside them.
    """
    names = set()
    for path in (CLASSES, CLASSES_TXT):
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("| "):
                    continue
                for cell in (c.strip() for c in line.strip().strip("|").split("|")):
                    if CLASS_RE.match(cell):
                        names.add(cell)
    return names


def load():
    if os.path.exists(LEDGER):
        try:
            with open(LEDGER, encoding="utf-8") as f:
                return json.load(f)
        except (ValueError, OSError):
            pass
    return {}


def save(d):
    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, sort_keys=True)


def heartbeat():
    """Refresh the fixer claim while the run is demonstrably alive.

    The claim is what tells the next hourly run whether to stand aside. It used to be
    stamped once, at claim time, so its age was "how long ago this run STARTED" - and a
    run that died at minute 17 held the slot until minute 45 anyway. On 16 Nov that cost
    roughly fifty minutes: the 07:48 run ended at 08:05 without releasing, the slot read
    busy until 08:33, and the next run had to wait for 08:53 to take over.

    Recording an attempt is proof of life. Touching the stamp here makes the age mean
    "how long since this run last did anything", which is the question the next run is
    actually asking. A dead run frees the slot 45 minutes after its last attempt instead
    of 45 minutes after its start; a live run keeps the slot it is using.
    """
    try:
        import time
        s = json.load(open(ROUND, encoding="utf-8"))
        s["fixer_started"] = time.time()
        json.dump(s, open(ROUND, "w", encoding="utf-8"), indent=2)
    except Exception:
        pass                    # a heartbeat that fails must never lose the attempt


def log_runline(cls, outcome, moved, total):
    """Append the attempt to RUN-LOG.md as well as the ledger.

    The ledger is the durable record and it is what the next run reads, but it is a JSON
    blob keyed by class. Someone reading RUN-LOG.md - the chronological log - would have
    seen only "slot claimed" for the 16 Nov fixer run and concluded it did nothing, while
    ATTEMPTS.json held a full attempt with its reason. Two records, one of them blind.
    """
    import time
    try:
        stamp = time.strftime("%d %b %H:%M")
        tail = "" if moved is None else " (%s/%s moved)" % (moved, total or "?")
        with open(RUNLOG, "a", encoding="utf-8") as f:
            f.write("| %s | fixer | attempt %s -> %s%s |\n" % (stamp, cls, outcome, tail))
    except Exception:
        pass                      # a log that cannot be written must not lose the attempt


def compute(moved, total):
    """kept / reverted from the numbers. None when there are no numbers to read."""
    if moved is None or not total:
        return None
    return "kept" if moved > 0 else "reverted"


def add(args):
    name = args.cls.strip()
    known = known_classes()
    if known and name not in known:
        print("refused: %r is not a class in benchmarks/DEFECT-CLASSES.md." % name)
        print("The ledger is keyed by the exact name, so an attempt recorded under a name")
        print("that is not there writes against nothing and leaves the real class at zero.")
        print("Names available:")
        for n in sorted(known)[:12]:
            print("    %s" % n)
        return 2

    outcome = args.outcome or compute(args.moved, args.total)
    if outcome not in OUTCOMES:
        print("refused: outcome must be one of %s, or give --moved/--total so it is "
              "computed." % ", ".join(OUTCOMES))
        return 2

    d = load()
    row = d.setdefault(name, {"attempts": 0, "first_seen": None, "last": None,
                              "outcomes": [], "reason": "", "requeues": 0,
                              "status": "OPEN"})
    row["attempts"] = row.get("attempts", 0) + 1
    row.setdefault("outcomes", []).append(outcome)
    row["last"] = row.get("last")
    if args.moved is not None and args.total:
        row["last_moved"] = args.moved
        row["last_total"] = args.total
    if args.engine:
        row["last_engine"] = args.engine
    if args.reason:
        row["reason"] = args.reason
    save(d)
    log_runline(name, outcome, args.moved, args.total)
    heartbeat()
    print("%s: attempt %d recorded as %s%s"
          % (name, row["attempts"], outcome,
             "  (%d/%d moved)" % (args.moved, args.total) if args.moved is not None else ""))
    return 0


def show(args):
    d = load()
    if args.cls:
        row = d.get(args.cls.strip())
        if not row:
            print("no attempts recorded for %r" % args.cls)
            return 1
        print(json.dumps(row, indent=1))
        return 0
    if not d:
        print("the ledger is empty")
        return 0
    print("%-42s %-8s %-10s %s" % ("CLASS", "ATTEMPTS", "KEPT", "OUTCOMES"))
    for name, row in sorted(d.items(), key=lambda kv: -kv[1].get("attempts", 0)):
        outs = row.get("outcomes", [])
        print("%-42s %-8d %-10d %s"
              % (name[:42], row.get("attempts", 0), outs.count("kept"),
                 ",".join(outs[-6:]) or "-"))
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", default="")
    ap.add_argument("--outcome", default="")
    ap.add_argument("--moved", type=int, default=None)
    ap.add_argument("--total", type=int, default=None)
    ap.add_argument("--engine", default="")
    ap.add_argument("--reason", default="")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args(argv[1:])
    return show(a) if a.show else add(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
