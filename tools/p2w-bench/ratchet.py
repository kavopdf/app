#!/usr/bin/env python3
"""
ratchet.py - a document may improve freely; it may never go backwards.

WHY THIS EXISTS
  "No document got worse" was checked by comparing a run against the previous
  run's numbers, and that is not a ratchet. If a fix takes a document from 30 to
  28 and the next run records 28 as the new baseline, the loss becomes the
  standard and the next comparison is against a worse number. Ten small
  regressions later the corpus has quietly slid and every comparison along the
  way said 'nothing got worse'. That is exactly how three broken fixes shipped.

  A ratchet keeps the BEST score each document has ever reached, permanently.
  Every run compares against that high-water mark, not against the last run. A
  document at 30 that drops to 28 fails immediately and keeps failing until it is
  back at 30 or above. The bar only ever goes up.

WHAT IT DOES
  reads   tools/p2w-bench/BASELINE.md   current scores
          tools/p2w-bench/RATCHET.json  best score ever seen, per document
  writes  RATCHET.json, raised to any new high
  exits   0 if nothing regressed, 1 if any document is below its high-water mark

  A document measured for the first time sets its own mark - it cannot regress
  against nothing.

USAGE
  python3 tools/p2w-bench/ratchet.py            # check and raise
  python3 tools/p2w-bench/ratchet.py --check    # check only, do not raise
  python3 tools/p2w-bench/ratchet.py --strict   # also fail on any unmeasured document
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "BASELINE.md")
RATCHET = os.path.join(HERE, "RATCHET.json")


def read_scores():
    """{document: (score, out_of)} for every row that has a score."""
    out = {}
    if not os.path.exists(BASE):
        return out
    for line in open(BASE, encoding="utf-8"):
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not cells[0] or cells[0].lower() == "document":
            continue
        m = re.match(r"(\d+)\s*/\s*(\d+)", cells[1] if len(cells) > 1 else "")
        if m:
            out[cells[0]] = (int(m.group(1)), int(m.group(2)))
    return out


def load_ratchet():
    if os.path.exists(RATCHET):
        try:
            return json.load(open(RATCHET, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def main(argv):
    check_only = "--check" in argv
    strict = "--strict" in argv

    scores = read_scores()
    ratchet = load_ratchet()

    if not scores:
        print("ratchet: no scored documents in BASELINE.md - nothing to check")
        return 0

    regressions = []
    new_marks = []
    for doc, (score, out_of) in scores.items():
        prev = ratchet.get(doc)
        if prev is None:
            new_marks.append((doc, score, out_of))
            if not check_only:
                ratchet[doc] = {"best": score, "out_of": out_of}
            continue
        best = prev.get("best", 0)
        if score < best:
            regressions.append((doc, score, best, out_of))
        elif score > best and not check_only:
            ratchet[doc] = {"best": score, "out_of": out_of}

    if not check_only:
        json.dump(ratchet, open(RATCHET, "w", encoding="utf-8"), indent=2, sort_keys=True)

    total = len(scores)
    measured_all = len([1 for l in open(BASE, encoding="utf-8")
                        if l.startswith("| ") and not l.startswith("|---")]) - 1

    print("ratchet")
    print("  documents scored this run : %d of %d rows" % (total, measured_all))
    print("  high-water marks held     : %d" % len(ratchet))
    print("  new documents, first mark : %d" % len(new_marks))

    fail = False
    if regressions:
        fail = True
        print("  REGRESSED: %d document(s) below their best ever score" % len(regressions))
        for doc, score, best, out_of in sorted(regressions)[:15]:
            print("      %-44s %2d/%d  was %2d/%d  (-%d)"
                  % (doc[:44], score, out_of, best, out_of, best - score))
        if len(regressions) > 15:
            print("      ... and %d more" % (len(regressions) - 15))
    if strict and total < measured_all:
        fail = True
        print("  FAIL (--strict): %d document(s) never measured" % (measured_all - total))

    print("  %s" % ("PASS - the bar held or rose" if not fail else "FAIL - the bar fell"))
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
