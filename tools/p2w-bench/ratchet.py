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
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "BASELINE.md")
RATCHET = os.path.join(HERE, "RATCHET.json")

# The .txt marks live apart from the .docx marks for the same reason the results do: a
# regression in one must never be able to hide behind a good score in the other.
RATCHET_TXT = os.path.join(HERE, "RATCHET-TXT.json")
RESULTS_TXT = os.path.join(HERE, "RESULTS-TXT.jsonl")


# The .txt checks are t01..t05 rather than 01..59, so one pattern would silently drop
# every one of them and the ratchet would guard nothing at all.
CHECK_RE = re.compile(r"^(?:\d{2}[a-c]?|t\d{2})_[a-z_]+$")


# Set by main(). A module flag rather than a parameter threaded through four functions,
# because read_scores, load_ratchet and the universe lookup all need it and none of them
# is called from anywhere but main.
TXT_MODE = False


def read_scores_txt():
    """{document: (score, out_of, failed)} from the .txt store, latest row per document.

    There is no BASELINE-TXT.md. The .docx path keeps a hand-written table because a
    human reads it; the .txt path has no reader but this one, so the store is the truth
    and a second table would be a second thing to fall out of step.
    """
    out = {}
    if not os.path.exists(RESULTS_TXT):
        return out
    latest = {}
    for line in open(RESULTS_TXT, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        key = (e.get("round", 0), e.get("engine", ""))
        doc = e.get("doc")
        if not doc:
            continue
        if doc not in latest or key >= latest[doc][0]:
            latest[doc] = (key, e)
    for doc, (_k, e) in latest.items():
        out[doc] = (e.get("score") or 0, e.get("total") or 0,
                    frozenset(e.get("failed") or []))
    return out


def read_scores():
    """{document: (score, out_of, frozenset(failed checks))} for every scored row."""
    if TXT_MODE:
        return read_scores_txt()
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
        if not m:
            continue
        failed = frozenset(
            c.strip() for c in (cells[3] if len(cells) > 3 else "").split(",")
            if CHECK_RE.match(c.strip()))
        out[cells[0]] = (int(m.group(1)), int(m.group(2)), failed)
    return out


def load_ratchet():
    path = RATCHET_TXT if TXT_MODE else RATCHET
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def main(argv):
    global TXT_MODE
    TXT_MODE = "--txt" in argv
    check_only = "--check" in argv
    strict = "--strict" in argv

    # ---- --reset -----------------------------------------------------------
    # When the YARDSTICK changes, every old mark is measuring a different thing and
    # comparing against it is not a ratchet, it is a false alarm. Tightening a check
    # from 0.7 to 0.9 on 12 Nov would have failed 26 documents that had not moved.
    #
    # So the marks are archived with the reason, and the store starts empty: every
    # document sets a fresh mark on its next measurement. The archive is the record
    # that the numbers changed meaning, and a reason is mandatory - a silent reset
    # would erase the only evidence that the corpus ever scored higher.
    if "--reset" in argv:
        reason = ""
        if "--reason" in argv:
            i = argv.index("--reason")
            if i + 1 < len(argv):
                reason = argv[i + 1].strip()
        if not reason:
            print("refused: --reset needs --reason \"<why the yardstick changed>\"")
            print("A reset without a reason erases the record of what the old marks meant.")
            return 1
        path = RATCHET_TXT if TXT_MODE else RATCHET
        if os.path.exists(path):
            stamp = time.strftime("%Y%m%d-%H%M%S")
            archive = path.replace(".json", "-%s.json" % stamp)
            shutil.copy(path, archive)
            old = json.load(open(path, encoding="utf-8"))
            print("archived %s -> %s (%d marks)" % (os.path.basename(path),
                                                    os.path.basename(archive), len(old)))
        else:
            print("nothing to archive - %s does not exist yet" % os.path.basename(path))
        json.dump({}, open(path, "w", encoding="utf-8"), indent=2)
        print("cleared %s - every document sets a fresh mark on its next measurement"
              % os.path.basename(path))
        print("reason: %s" % reason)
        return 0

    scores = read_scores()
    ratchet = load_ratchet()
    # The universe is EVERY check the verifier knows, not just the ones that
    # failed. Using the failed set was wrong: a check that passed at the mark is
    # in neither set, so if it fails later the comparison never sees it and the
    # regression is invisible. verify_google.py --list-checks reports the real
    # list, and it is discovered rather than hard-coded, so adding a check cannot
    # leave a stale universe behind.
    universe = set()
    try:
        out = subprocess.check_output(
            [sys.executable,
             os.path.join(HERE, "verify_txt.py" if TXT_MODE else "verify_google.py"),
             "--list-checks"],
            stderr=subprocess.DEVNULL, timeout=120, text=True)
        universe = {l.strip() for l in out.splitlines() if l.strip()}
    except Exception:
        # Fall back to what the rows themselves mention. Weaker, and reported.
        for _doc, (_s, _o, _f) in scores.items():
            universe |= _f
        if universe:
            print("  NOTE: could not read the check list from verify_google.py; "
                  "comparing only the %d checks these rows mention" % len(universe))

    if not scores:
        print("ratchet: no scored documents in %s - nothing to check"
          % ("RESULTS-TXT.jsonl" if TXT_MODE else "BASELINE.md"))
        return 0

    regressions = []
    new_marks = []
    for doc, (score, out_of, failed) in scores.items():
        prev = ratchet.get(doc)
        if prev is None:
            new_marks.append((doc, score, out_of))
            if not check_only:
                ratchet[doc] = {"best": score, "out_of": out_of,
                                "failed": sorted(failed),
                                "universe": sorted(universe)}
            continue

        best = prev.get("best", 0)
        prev_failed = frozenset(prev.get("failed", []))
        prev_universe = frozenset(prev.get("universe", []))

        # The verifier gains checks. A document measured at 45 of 50 that now
        # scores 44 of 58 has not regressed - eight new checks arrived and it
        # failed one of them. Comparing raw counts across two different
        # denominators would call that a regression on every document in the
        # corpus and make the ratchet useless the day a check is added.
        # So only checks that existed at BOTH marks are compared.
        # A mark is only a standard if it was taken by the SAME set of checks.
        # Comparing the intersection is not enough: a mark taken by a smaller
        # verifier lets its old passes gate a stronger one, so every check added
        # since reads as newly failing and the document is condemned for having
        # been measured with a weaker instrument. A different universe means the
        # mark is stale, not that the document got worse - so it is replaced.
        if prev_universe and prev_universe != universe:
            if not check_only:
                ratchet[doc] = {"best": score, "out_of": out_of,
                                "failed": sorted(failed),
                                "universe": sorted(universe)}
            continue

        common = prev_universe & universe
        if not common:
            # No recorded universe (a mark from before universes were recorded):
            # fall back to the check ids in either failed set, all we can know.
            common = prev_failed | failed
        same_denominator = (out_of == prev.get("out_of", out_of))

        # Two ways to regress, and the second one is the one a score cannot see.
        # A fix can make one check pass and another fail: the score stays at 30 of
        # 50, a score-only ratchet says nothing got worse, and a defect has quietly
        # replaced another. So a check that used to pass and now fails is a
        # regression even when the total is unchanged or higher.
        new_failures = sorted((failed & common) - prev_failed)

        if same_denominator and score < best:
            regressions.append((doc, score, best, out_of,
                                new_failures, "score fell"))
        elif new_failures:
            regressions.append((doc, score, best, out_of,
                                new_failures, "check(s) newly failing"))
        elif not check_only and (score > best or
                                 len(failed & common) < len(prev_failed & common)):
            ratchet[doc] = {"best": max(score, best), "out_of": out_of,
                            "failed": sorted(failed),
                            "universe": sorted(universe)}

    if not check_only:
        json.dump(ratchet, open(RATCHET_TXT if TXT_MODE else RATCHET, "w",
                                encoding="utf-8"), indent=2, sort_keys=True)

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
        for doc, score, best, out_of, checks, why in sorted(regressions)[:15]:
            print("      %-40s %2d/%d was %2d/%d  %s%s"
                  % (doc[:40], score, out_of, best, out_of, why,
                     (": " + ", ".join(checks[:4])) if checks else ""))
        if len(regressions) > 15:
            print("      ... and %d more" % (len(regressions) - 15))
    if strict and total < measured_all:
        fail = True
        print("  FAIL (--strict): %d document(s) never measured" % (measured_all - total))

    print("  %s" % ("PASS - the bar held or rose" if not fail else "FAIL - the bar fell"))
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
