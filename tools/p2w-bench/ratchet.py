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

  THE DENOMINATOR IS NOT OURS TO ASSERT (13 Nov)
  A score is a count of passes, and a count means nothing without the set it was
  counted out of. ratchet.py used to take that set from the row itself:
  `same_denominator = (out_of == prev['out_of'])`. Both sides of that comparison
  came out of the same stores, so two checks could be dropped, every stored
  denominator stay at 59, and the gate would compare 59 against 59 and pass. It
  did exactly that on 13 Nov: 02_text_run_count and 56_rtl_runs were dropped and
  20_within_10pt was replaced by 20_line_placement, the verifier went to 57, and
  the stores still said 59. The drift was arithmetically invisible.

  So the denominator is now read from the instrument, never from the store:
  `len(verify_google.py --list-checks)` is the only authority. Every row must
  declare the universe it was measured under, that declaration must equal its own
  out_of, and both must equal the live list. Anything else is reported and fails.

  A mark taken by a different set of checks is STALE: it is not compared, not
  carried forward, and above all not silently replaced - replacing it without a
  comparison is how dropping one check once disarmed the gate for the whole
  corpus. A stale mark stays exactly as measured until someone re-measures and
  passes --recut, which archives the old mark inside the new one.

USAGE
  python3 tools/p2w-bench/ratchet.py            # check and raise
  python3 tools/p2w-bench/ratchet.py --check    # check only, do not raise
  python3 tools/p2w-bench/ratchet.py --strict   # also fail on any unmeasured document
  python3 tools/p2w-bench/ratchet.py --allow-stale   # report drift, do not fail on it
  python3 tools/p2w-bench/ratchet.py --recut --reason "<why>"   # re-mark a stale doc

exits   0 held or rose
        1 a document fell, or the stores disagree with the live instrument
        2 the check list could not be read - refused to gate at all
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
try:
    from trace import note
except Exception:
    def note(*a, **k):
        pass

RATCHET = os.path.join(HERE, "RATCHET.json")

# The .txt marks live apart from the .docx marks for the same reason the results do: a
# regression in one must never be able to hide behind a good score in the other.
RATCHET_TXT = os.path.join(HERE, "RATCHET-TXT.json")
RESULTS_TXT = os.path.join(HERE, "RESULTS-TXT.jsonl")


# The instrument lives in instrument.py so that ratchet.py and record.py cannot
# disagree about how many checks there are - which is the whole class of bug this
# file was repaired for. It owns CHECK_RE too, because the .txt checks are t01..t05
# rather than 01..59: one pattern has to cover both or every .txt check is dropped
# and the ratchet guards nothing. Everything below derives its denominator from it.
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from instrument import CHECK_RE, live_universe, parse_stamp, stamp_of  # noqa: E402


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
        # The declared universe comes off the row itself, never from the live list.
        # If a row does not say what it was measured with, that is a fact about the
        # row, and read_scores' callers must be able to see it.
        declared = e.get("universe_n") or (len(e["universe"]) if e.get("universe") else None)
        out[doc] = (e.get("score") or 0, e.get("total") or 0,
                    frozenset(e.get("failed") or []), declared)
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
        # Column 7 is the universe stamp (u59). A row without one predates the
        # stamp; it is treated as claiming its own denominator, which the guard
        # then reports if that disagrees with the instrument.
        declared = parse_stamp(cells[6]) if len(cells) > 6 else None
        out[cells[0]] = (int(m.group(1)), int(m.group(2)), failed, declared)
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
    allow_stale = "--allow-stale" in argv
    recut_ok = "--recut" in argv
    reason = ""
    if "--reason" in argv:
        i = argv.index("--reason")
        if i + 1 < len(argv):
            reason = argv[i + 1].strip()

    # The universe is EVERY check the verifier knows, not just the ones that
    # failed, and it is asked of the verifier rather than read from the store.
    # A check that passed at the mark is in neither failed set, so a failed-set
    # universe cannot see it fail later. And a universe read from the store is
    # the store grading itself - which is the bug this file was fixed for.
    ids, live_sha, live_err = live_universe(TXT_MODE)
    if not ids:
        # Not a warning. A gate that cannot name its instrument compares against
        # nothing, and 'compared against nothing' is what printed PASS on the run
        # that dropped two checks. Refuse to gate at all.
        print("ratchet: CANNOT GATE - %s" % live_err)
        print("  No check list means no denominator, and a denominator taken from the")
        print("  stores is exactly the drift this gate exists to catch. Refusing.")
        return 2
    universe = set(ids)
    N = len(ids)

    if not scores:
        print("ratchet: no scored documents in %s - nothing to check"
          % ("RESULTS-TXT.jsonl" if TXT_MODE else "BASELINE.md"))
        return 0

    # ---- the denominator guard --------------------------------------------
    # Three separate failures, because they need three different fixes:
    #   DRIFT        a row is scored out of a count the instrument does not have
    #   INCONSISTENT a row's own stamp disagrees with its own denominator
    #   MARK-DRIFT   a stored high-water mark is out of a count that never existed
    drift, inconsistent, mark_drift = [], [], []
    for doc, (score, out_of, failed, declared) in sorted(scores.items()):
        if declared is not None and declared != out_of:
            inconsistent.append((doc, score, out_of, declared))
        if out_of != N:
            drift.append((doc, score, out_of, declared))
    for doc, mark in sorted(ratchet.items()):
        if not isinstance(mark, dict):
            continue
        mo = mark.get("out_of")
        if mo is not None and mo != N:
            mark_drift.append((doc, mark.get("best"), mo))

    if inconsistent:
        print("  ROW LIES ABOUT ITS OWN UNIVERSE: %d row(s)" % len(inconsistent))
        for doc, score, out_of, declared in inconsistent[:10]:
            print("      %-40s %2d/%d stamped %s"
                  % (doc[:40], score, out_of, stamp_of(declared)))

    if drift:
        print("  DENOMINATOR DRIFT: %d of %d row(s) are scored out of something other"
              % (len(drift), len(scores)))
        print("  than the live check universe.")
        print("      live instrument : %s --list-checks = %d checks (sha %s)"
              % ("verify_txt.py" if TXT_MODE else "verify_google.py", N, live_sha))
        claimed = sorted({o for _d, _s, o, _u in drift})
        print("      rows claim      : %s" % ", ".join("x/%d" % c for c in claimed))
        print("      delta           : %s"
              % ", ".join("%+d" % (N - c) for c in claimed))
        for doc, score, out_of, declared in drift[:10]:
            print("      %-40s %2d/%d%s"
                  % (doc[:40], score, out_of,
                     "  stamped %s" % stamp_of(declared) if declared else "  unstamped"))
        if len(drift) > 10:
            print("      ... and %d more" % (len(drift) - 10))
        print("      A count out of %s is not a count out of %d. The store must be"
              % ("/".join(str(c) for c in claimed), N))
        print("      reconciled or the documents re-measured before this gate can mean")
        print("      anything.")

    if mark_drift:
        print("  MARK DENOMINATOR DRIFT: %d high-water mark(s) recorded out_of a count"
              % len(mark_drift))
        print("  the instrument does not have (live %d): %s"
              % (N, ", ".join("%d" % c for c in sorted({m[2] for m in mark_drift}))))

    regressions = []
    new_marks = []
    stale = []
    for doc, (score, out_of, failed, _declared) in scores.items():
        prev = ratchet.get(doc)
        if prev is None:
            new_marks.append((doc, score, out_of))
            if not check_only:
                ratchet[doc] = {"best": score, "out_of": out_of,
                                "failed": sorted(failed),
                                "universe": sorted(universe),
                                "universe_n": N, "universe_sha": live_sha}
            continue

        best = prev.get("best", 0)
        prev_failed = frozenset(prev.get("failed", []))
        prev_universe = frozenset(prev.get("universe", []))

        # A mark is only a standard if it was taken by the SAME set of checks.
        # The verifier gains and loses checks. A document measured at 45 of 50 that
        # now scores 44 of 58 has not regressed - eight new checks arrived and it
        # failed one of them - and a document measured at 45 of 50 that now scores
        # 43 of 48 has not improved either. Comparing raw counts across two
        # denominators calls the first a regression on every document in the corpus
        # and the second a rise on every one.
        #
        # The earlier repair compared the INTERSECTION of the two universes. That
        # is not enough: a mark taken by a smaller verifier lets its old passes gate
        # a stronger one, so every check added since reads as newly failing and the
        # document is condemned for having been measured with a weaker instrument.
        # The repair after that replaced the mark outright and skipped the
        # comparison - so dropping ONE check disabled the gate for the whole corpus,
        # silently, on exactly the run where a regression mattered most. Measured
        # 13 Nov: dropping 02_text_run_count took the universe from 59 to 58, every
        # one of the 211 marks was replaced without a comparison, and the gate
        # printed PASS while 187 documents were newly failing checks against their
        # own recorded marks.
        #
        # A mark taken by a different instrument is STALE, and stale is a third
        # answer next to pass and fail: it is not a comparison at all. It is not
        # carried (max() of a 58/59 and a 55/57 is arithmetic on two rulers), it
        # is not compared (the intersection lets an old pass gate a new check),
        # and it is not replaced (that is how one dropped check disarmed the gate
        # for 211 documents on 13 Nov, printing PASS). It is reported, and it
        # stays exactly as measured until --recut says otherwise.
        if prev_universe and prev_universe != universe:
            stale.append((doc, best, prev.get("out_of"), len(prev_universe), score, out_of))
            if recut_ok and not check_only:
                old = {k: prev.get(k) for k in ("best", "out_of", "universe_n")}
                old["universe_sha"] = prev.get("universe_sha") or ""
                old["superseded_on"] = time.strftime("%Y-%m-%d",
                                                     time.gmtime(time.time() + 19800))
                old["reason"] = reason or "re-measured under the live instrument"
                hist = list(prev.get("superseded") or [])
                hist.append(old)
                ratchet[doc] = {"best": score, "out_of": out_of,
                                "failed": sorted(failed),
                                "universe": sorted(universe),
                                "universe_n": N, "universe_sha": live_sha,
                                "superseded": hist[-4:]}
            continue

        common = prev_universe & universe
        if not common:
            # No recorded universe (a mark from before universes were recorded):
            # fall back to the check ids in either failed set, all we can know.
            common = prev_failed | failed
        # The denominator is now the instrument's, on BOTH sides: this row was
        # checked against N above, and the mark is only comparable if it too was
        # counted out of N. Comparing out_of to the row's own out_of is what made
        # a two-check drift invisible.
        same_denominator = (out_of == N and prev.get("out_of") == N)

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
                            "universe": sorted(universe),
                            "universe_n": N, "universe_sha": live_sha}

    # A store whose numbers are counted out of two different universes must not be
    # written at all: every write would fold one instrument's number into the
    # other's, which is the aggregation record.py now stamps against.
    blocked = bool(drift or inconsistent)
    if not check_only and not blocked:
        json.dump(ratchet, open(RATCHET_TXT if TXT_MODE else RATCHET, "w",
                                encoding="utf-8"), indent=2, sort_keys=True)

    total = len(scores)
    measured_all = len([1 for l in open(BASE, encoding="utf-8")
                        if l.startswith("| ") and not l.startswith("|---")]) - 1

    print("ratchet")
    print("  instrument                : %d checks (sha %s)"
          % (N, live_sha))
    print("  documents scored this run : %d of %d rows" % (total, measured_all))
    print("  high-water marks held     : %d" % len(ratchet))
    print("  new documents, first mark : %d" % len(new_marks))
    if stale:
        # Loud, because a stale mark is the one moment the gate is weakest: it can
        # neither pass nor fail the document, so a regression on this run is
        # invisible for it. Silence here is how 211 documents stopped being gated.
        print("  STALE marks (measured by a retired instrument): %d" % len(stale))
        print("      %d of them counted out of %s, the live instrument has %d."
              % (len(stale),
                 ", ".join(sorted({str(o) for _d, _b, o, _n, _s, _no in stale})), N))
        for doc, best, po, pun, score, out_of in stale[:8]:
            print("      %-40s marked %2s/%s, now %2d/%d"
                  % (doc[:40], best, po, score, out_of))
        if len(stale) > 8:
            print("      ... and %d more" % (len(stale) - 8))
        print("      These are NOT compared, NOT carried and NOT replaced. They need")
        print("      re-measurement; --recut re-marks one and archives the old mark.")
    if blocked:
        print("  NOTHING WRITTEN: the store disagrees with the instrument (%d drifted,"
              % len(drift))
        print("  %d inconsistent, %d marks)." % (len(inconsistent), len(mark_drift)))

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

    if inconsistent:
        fail = True
        print("  FAIL: %d row(s) stamp a universe that is not their denominator"
              % len(inconsistent))
    if (drift or mark_drift) and not allow_stale:
        fail = True
        print("  FAIL: DENOMINATOR DRIFT - %d row(s) and %d mark(s) are counted out of a"
              % (len(drift), len(mark_drift)))
        print("  universe the instrument does not have (%d). Every score above is a count"
              % N)
        print("  out of a set that no longer exists; a comparison across the two is not a")
        print("  ratchet. Pass --allow-stale to report this and carry on, and say why.")
    elif (drift or mark_drift):
        print("  ALLOWED: %d drifted row(s) / %d drifted mark(s) reported, not compared."
              % (len(drift), len(mark_drift)))
    if stale and not allow_stale:
        fail = True
        print("  FAIL: %d mark(s) STALE - measured by an instrument this run does not use."
              % len(stale))
        print("  A document that cannot be compared has not held its bar; it has not been")
        print("  asked. Pass --allow-stale to accept that gap explicitly.")

    # The trace line has to say what this run actually concluded. It used to say
    # "held or rose" whenever no document regressed - so on 13 Nov, when every mark
    # was re-cut without a comparison and the gate printed PASS, and again on any run
    # that fails on drift alone, TRACE.md recorded a hold. A log that reports a hold
    # on a failing run is the drift hiding in a second place.
    why = []
    if regressions:
        why.append("REGRESSED %d" % len(regressions))
    if drift or mark_drift:
        why.append("DRIFT %d rows/%d marks" % (len(drift), len(mark_drift)))
    if stale:
        why.append("STALE %d" % len(stale))
    if inconsistent:
        why.append("INCONSISTENT %d" % len(inconsistent))
    if fail:
        note("ratchet%s" % (" --txt" if TXT_MODE else ""), "FAIL " + "; ".join(why))
    elif why:
        note("ratchet%s" % (" --txt" if TXT_MODE else ""),
             "NOT COMPARED (--allow-stale) " + "; ".join(why))
    else:
        note("ratchet%s" % (" --txt" if TXT_MODE else ""), "held or rose")

    if fail:
        print("  FAIL - the bar fell")
    elif drift or mark_drift or stale:
        # A PASS that compared nothing is not a pass. Saying 'the bar held' here would
        # be the same lie in the last line that the old code told in the first.
        print("  PASS (--allow-stale) - but %d row(s) and %d mark(s) were NOT compared."
              % (max(len(drift), len(stale)), len(mark_drift)))
        print("  This run proves nothing about them; the gap is explicit, not closed.")
    else:
        print("  PASS - the bar held or rose")
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
