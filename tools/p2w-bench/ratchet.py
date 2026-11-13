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

THREE ANSWERS, NOT TWO (13 Nov)
  On 13 Nov the instrument retired five checks and added two - 59 became 56 - and
  every one of the 211 marks became stale at once. The guard was right about that
  and useless about it, because it had only two answers:

    exit 1   printed "FAIL - the bar fell" on a run where no document had moved.
             That is a false accusation, and the fixer's only way to answer a
             false accusation is to ignore it.
    --allow-stale
             printed "PASS (--allow-stale)" and exited 0. That is worse: it
             laundered 211 unasked documents into a green light, and the reason
             it was told to give (--reason) was parsed and then thrown away -
             it was only ever used by --recut.

  Neither is the truth, and the truth is the third answer. A document whose mark
  was taken by a retired instrument has not held its bar and has not dropped below
  it: it has not been ASKED. So there are three verdicts, and they exit
  differently so a caller cannot mistake one for another:

    0  PASS        every scored document was compared against its mark under the
                   instrument in force, and none fell
    1  FAIL        a document fell, or a row contradicts itself
    2  REFUSED     no instrument, or a waiver with no reason - cannot gate
    3  UNMEASURED  nothing fell, but at least one document could not be compared

  UNMEASURED is not a pass and it is not a failure, and it is deliberately not
  exit 0: every existing caller treats non-zero as "do not commit", so the
  default stays safe without anyone having to be told about the new code. What
  turns it into permission is a separate, written act - see UNMEASURED.json below
  and tools/p2w-bench/unmeasured.py, which decides whether the gap is small
  enough, old enough and paid-down enough to commit through.

  --allow-stale no longer means "pretend this is a pass". It means "record the
  gap, with a reason, as a waiver" - it still exits 3. The gate reads the record;
  the flag does not decide.

WHAT IT RECORDS (the ledger)
  UNMEASURED.json       the gap as it stands after this run: which documents were
                        compared, which were not, and for each one why. Written
                        on every UNMEASURED run, waived or not, so the gap is on
                        disk even on a run nobody was watching.
  WAIVER.json           written only by --allow-stale --reason. It is the act of
                        accepting the gap, and it is the only file that can
                        carry a reason into the gate.
  UNMEASURED-HISTORY.jsonl
                        one line per waiver, deduplicated, so the gate can tell a
                        gap that is being paid down from one that is growing.
  The .txt half keeps its own three, suffixed -TXT, for the same reason the marks
  are separate: one conversion writes both outputs and neither may hide behind
  the other.

USAGE
  python3 tools/p2w-bench/ratchet.py            # check and raise
  python3 tools/p2w-bench/ratchet.py --check    # check only, do not raise a mark
  python3 tools/p2w-bench/ratchet.py --strict   # also fail on any unscored document
  python3 tools/p2w-bench/ratchet.py --allow-stale --reason "<why>"  # record a waiver
  python3 tools/p2w-bench/ratchet.py --recut --reason "<why>"   # re-mark a stale doc

exits   0 held or rose
        1 a document fell, or a row contradicts itself
        2 the check list could not be read, or --allow-stale came without --reason
        3 UNMEASURED - nothing fell, but something could not be compared
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
RESULTS = os.path.join(HERE, "RESULTS.jsonl")


# The ledger. Three files because they answer three different questions, and folding
# them into one is how the 13 Nov run lost the distinction between "not asked" and
# "passed": the record of the gap, the act of accepting it, and its trend over time.
#
#   UNMEASURED.json  written by EVERY unmeasured run, waived or not. A run nobody was
#                    watching still leaves the gap on disk.
#   WAIVER.json      written only by --allow-stale --reason. The deliberate act, and
#                    the only place a reason can come from.
#   UNMEASURED-HISTORY.jsonl
#                    appended on a waiver, deduplicated, so "is this gap being paid
#                    down or is it growing" is a question with an answer in a file
#                    rather than in someone's memory of last week.
def _ledger_paths(txt):
    suffix = "-TXT" if txt else ""
    return (os.path.join(HERE, "UNMEASURED%s.json" % suffix),
            os.path.join(HERE, "WAIVER%s.json" % suffix),
            os.path.join(HERE, "UNMEASURED-HISTORY%s.jsonl" % suffix))


def _write_json(path, payload):
    """Atomic: a half-written ledger would read as a smaller gap than there is."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def _now():
    """IST, because every timestamp a human reads in this repo is IST."""
    return time.strftime("%Y-%m-%dT%H:%M:%S+05:30", time.gmtime(time.time() + 19800))


def _append_history(path, payload):
    """Append unless it repeats the last line.

    ratchet.py is called more than once per commit - the fixer runs it, then the gate
    runs it again. Counting those as two waivers would spend the carry allowance on
    one decision, so an identical line is not written twice.
    """
    line = json.dumps(payload, sort_keys=True)
    last = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    last = l.strip()
    if line != last:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")


# The instrument lives in instrument.py so that ratchet.py and record.py cannot
# disagree about how many checks there are - which is the whole class of bug this
# file was repaired for. It owns CHECK_RE too, because the .txt checks are t01..t05
# rather than 01..59: one pattern has to cover both or every .txt check is dropped
# and the ratchet guards nothing. Everything below derives its denominator from it.
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from instrument import (CHECK_RE, body_map, digest, live_universe,  # noqa: E402
                        parse_stamp, stamp_of)


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
    for _seq, line in enumerate(open(RESULTS_TXT, encoding="utf-8")):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        # ORDER BY WRITE, NOT BY ENGINE NAME (13 Nov). This was (round, engine) compared with
        # `>=`, and "22728b1" >= "2a68de6" is FALSE - so a whole round of 211 rows was
        # silently discarded and the ratchet re-compared the PRE-round rows, never seeing
        # the 139 documents that had improved. The line index is the only ordering a JSONL
        # store has.
        key = (e.get("round", 0), _seq)
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


def redefined_checks(mark, live_bodies):
    """Which of this mark's checks now ask something different, by name.

    Needs the per-check digests the mark carries (check_bodies). A mark written
    before 13 Nov has none, and this returns [] rather than guessing - the sha
    mismatch still makes it stale, it just cannot say which check moved. That is
    the difference between "re-measure, something changed" and "22_reading_order
    was redefined, its old verdicts are not comparable", and the second is what a
    fixer needs.
    """
    was = mark.get("check_bodies") or {}
    return sorted(k for k in was if k in live_bodies and was[k] != live_bodies[k])


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
        # Outside the branch: the history archive below needs it even when there was
        # no mark file to archive, which is exactly the run where a NameError would
        # turn a reset into a crash.
        stamp = time.strftime("%Y%m%d-%H%M%S")
        if os.path.exists(path):
            archive = path.replace(".json", "-%s.json" % stamp)
            shutil.copy(path, archive)
            old = json.load(open(path, encoding="utf-8"))
            print("archived %s -> %s (%d marks)" % (os.path.basename(path),
                                                    os.path.basename(archive), len(old)))
        else:
            print("nothing to archive - %s does not exist yet" % os.path.basename(path))
        json.dump({}, open(path, "w", encoding="utf-8"), indent=2)
        # The ledger describes a gap against marks that no longer exist. A waiver left
        # behind after a reset would authorise a commit through a comparison nobody
        # made, so it goes with the marks it was about - and the history is archived
        # rather than deleted, because it is the record that the gap was ever carried.
        led, wvr, hist = _ledger_paths(TXT_MODE)
        for f in (led, wvr):
            if os.path.exists(f):
                os.remove(f)
                print("removed %s" % os.path.basename(f))
        if os.path.exists(hist):
            arch = hist.replace(".jsonl", "-%s.jsonl" % stamp)
            shutil.move(hist, arch)
            print("archived %s -> %s" % (os.path.basename(hist),
                                         os.path.basename(arch)))
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
        if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            reason = argv[i + 1].strip()

    # A waiver without a reason is not a waiver, it is a shrug.
    #
    # --allow-stale used to accept --reason and then discard it: the variable was
    # parsed at the top of main() and read only by the --recut branch. So on 13 Nov a
    # run could pass --allow-stale, print PASS, exit 0, and leave no statement on disk
    # of what it had chosen not to compare. The reason is now the thing the gate reads,
    # so refusing to proceed without one is the whole point rather than a formality -
    # the same rule --reset already had, for the same reason.
    if allow_stale and not reason:
        print("refused: --allow-stale needs --reason \"<what you are accepting, and why>\"")
        print("  A waiver is a statement about which documents were not compared. Without")
        print("  the statement there is nothing to read at commit time, and the gap becomes")
        print("  a green light with no author.")
        return 2

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
    live_bodies, bodies_err = body_map(TXT_MODE)

    # An empty store is the extreme case of "not asked", not a pass.
    #
    # This returned 0 and printed "nothing to check", which TOOLBOX.md then had to
    # warn about: "with no BASELINE.md there is nothing to compare and it exits 0,
    # which is why a cron must never treat 0 as proof that measurement happened".
    # A guard that needs a paragraph telling you not to believe its exit code is not
    # a guard. Zero scored documents is UNMEASURED: nothing was compared.
    if not scores:
        store = "RESULTS-TXT.jsonl" if TXT_MODE else "BASELINE.md"
        print("ratchet: no scored documents in %s - nothing was compared" % store)
        led, wvr, hist = _ledger_paths(TXT_MODE)
        _write_json(led, {
            "verdict": "UNMEASURED", "waived": False, "reason": "",
            "written_at": _now(), "store": store,
            "instrument": {"tool": "verify_txt.py" if TXT_MODE else "verify_google.py",
                           "checks": N, "sha": live_sha},
            "counts": {"scored": 0, "compared": 0, "not_compared": 0,
                       "unscored": 0, "regressed": 0},
            "compared_docs": [], "not_compared": {},
        })
        print("  UNMEASURED - an empty store proves nothing about any document")
        return 3

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
    redefined_seen = set()
    # Which documents this run actually ASKED, and for the rest, what stopped it.
    #
    # These two sets are the difference between a pass and a green light. A document
    # is compared when its row and its mark were counted out of the live instrument;
    # everything else is a named gap with a reason attached, which is what makes the
    # ledger something a reader can act on instead of a number that says 211.
    compared = []
    not_compared = {}
    for doc, (score, out_of, failed, _declared) in scores.items():
        prev = ratchet.get(doc)
        if prev is None:
            new_marks.append((doc, score, out_of))
            if out_of == N:
                compared.append(doc)
            else:
                not_compared[doc] = {"why": "row-drifted", "marked": None,
                                     "now": "%d/%d" % (score, out_of),
                                     "mark_universe_sha": None, "mark_out_of": None}
            if not check_only:
                ratchet[doc] = {"best": score, "out_of": out_of,
                                "failed": sorted(failed),
                                "universe": sorted(universe),
                                "universe_n": N, "universe_sha": live_sha,
                                "id_sha": digest(universe),
                                "check_bodies": {k: live_bodies[k] for k in universe
                                                 if k in live_bodies}}
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
        # THE SET IS NOT THE QUESTION (13 Nov). A mark also goes stale when the ids
        # are the same and the bodies are not: 32_stroke_lines, 22_reading_order,
        # 08_image_count, 18_displacement and 53_embedded_faces each changed what
        # they ASK while keeping their id, and this test - which only compared id
        # sets - compared the marks taken under the old question against the new
        # one. On 22 that is 88 documents failing under the old rule against 4
        # under the new: read as 84 documents getting better, which is not a thing
        # that happened. A mark whose stamp does not match is stale for the same
        # reason a mark with a different set is: it was not taken by this instrument.
        set_moved = bool(prev_universe) and prev_universe != universe
        prev_sha = prev.get("universe_sha") or ""
        sha_moved = bool(prev_sha) and prev_sha != live_sha
        if set_moved or sha_moved:
            redef = redefined_checks(prev, live_bodies)
            stale.append((doc, best, prev.get("out_of"), len(prev_universe), score,
                          out_of, "set" if set_moved else "bodies"))
            not_compared[doc] = {"why": "stale-mark",
                                 "marked": "%s/%s" % (best, prev.get("out_of")),
                                 "now": "%d/%d" % (score, out_of),
                                 "mark_universe_sha": prev_sha,
                                 "mark_out_of": prev.get("out_of"),
                                 "stale_because": ("the set of checks changed"
                                                   if set_moved else
                                                   "same ids, redefined: "
                                                   + (", ".join(redef) or
                                                      "(bodies not recorded on the mark)"))}
            if redef:
                redefined_seen.update(redef)
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
                                "id_sha": digest(universe),
                                "check_bodies": {k: live_bodies[k] for k in universe
                                                 if k in live_bodies},
                                "superseded": hist[-4:]}
            continue

        # Reached only when the mark and the row were taken by the same instrument.
        # Even here the denominators are checked rather than assumed: a mark can
        # carry the right universe list and the wrong out_of, which is a row that
        # contradicts itself and must not be counted as an answer.
        if out_of != N or prev.get("out_of") != N:
            not_compared[doc] = {"why": "mark-drifted",
                                 "marked": "%s/%s" % (best, prev.get("out_of")),
                                 "now": "%d/%d" % (score, out_of),
                                 "mark_universe_sha": prev.get("universe_sha") or "",
                                 "mark_out_of": prev.get("out_of")}
        else:
            compared.append(doc)

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
                            "universe_n": N, "universe_sha": live_sha,
                            "id_sha": digest(universe),
                            "check_bodies": {k: live_bodies[k] for k in universe
                                             if k in live_bodies}}

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
    unscored = sorted(set(ratchet) - set(scores))

    # ---- the verdict, decided before it is printed --------------------------
    # Three answers, and the order of these tests is the policy.
    #
    # A REGRESSION OUTRANKS EVERYTHING. If any document fell, the run is a failure
    # and no gap anywhere can soften it: "the instrument changed" is not an excuse
    # for a number that moved under the same instrument. A row that contradicts
    # itself is the same kind of answer - it is not a gap, it is a store that cannot
    # be trusted, and a waiver over a store that lies is worse than no waiver.
    #
    # Only then does UNMEASURED apply. It is the answer for a run that accused no
    # document of anything and still cannot say the bar held, because some marks
    # were taken by an instrument this run does not use.
    if regressions or inconsistent or (strict and total < measured_all):
        verdict = "FAIL"
    elif drift or mark_drift or stale:
        verdict = "UNMEASURED"
    else:
        verdict = "PASS"

    # ---- the ledger ---------------------------------------------------------
    # Written on every UNMEASURED run, whether or not anyone waived it. The gap is a
    # fact about the stores, not about who was watching, and a record that only
    # appears when somebody asks for forgiveness is a record of the asking.
    if verdict == "UNMEASURED":
        led, wvr, hist = _ledger_paths(TXT_MODE)
        payload = {
            "verdict": "UNMEASURED",
            "waived": bool(allow_stale),
            "reason": reason if allow_stale else "",
            "written_at": _now(),
            "store": "RESULTS-TXT.jsonl" if TXT_MODE else "BASELINE.md",
            "instrument": {
                "tool": "verify_txt.py" if TXT_MODE else "verify_google.py",
                "checks": N, "sha": live_sha,
            },
            "counts": {
                "scored": total, "compared": len(compared),
                "not_compared": len(not_compared), "unscored": len(unscored),
                "regressed": len(regressions),
            },
            "compared_docs": sorted(compared),
            "not_compared": not_compared,
        }
        _write_json(led, payload)
        if allow_stale:
            # The waiver is a separate file on purpose. The gate runs ratchet.py
            # again with no flags, and that run must be able to refresh
            # UNMEASURED.json without erasing the statement somebody signed.
            _write_json(wvr, dict(payload, waived=True, reason=reason))
            _append_history(hist, {
                "at": payload["written_at"], "reason": reason,
                "instrument": live_sha, "checks": N,
                "compared": len(compared), "not_compared": len(not_compared),
                "not_compared_docs": sorted(not_compared),
            })

    print("ratchet")
    print("  instrument                : %d checks (sha %s)"
          % (N, live_sha))
    print("  documents scored this run : %d of %d rows" % (total, measured_all))
    print("  high-water marks held     : %d" % len(ratchet))
    print("  new documents, first mark : %d" % len(new_marks))
    print("  compared against a mark   : %d" % len(compared))
    if stale:
        # Loud, because a stale mark is the one moment the gate is weakest: it can
        # neither pass nor fail the document, so a regression on this run is
        # invisible for it. Silence here is how 211 documents stopped being gated.
        print("  STALE marks (measured by a retired instrument): %d" % len(stale))
        print("      %d of them counted out of %s, the live instrument has %d."
              % (len(stale),
                 ", ".join(sorted({str(o) for _d, _b, o, _n, _s, _no, _w in stale})), N))
        why_sets = {}
        for row in stale:
            why_sets.setdefault(row[6], 0)
            why_sets[row[6]] += 1
        if why_sets.get("bodies"):
            print("      %d of them by a REDEFINED CHECK - same ids, different question."
                  % why_sets["bodies"])
            if redefined_seen:
                print("      redefined since those marks: %s"
                      % ", ".join(sorted(redefined_seen)[:12]))
        for row in stale[:8]:
            doc, best, po, pun, score, out_of, why = row
            print("      %-40s marked %2s/%s, now %2d/%d%s"
                  % (doc[:40], best, po, score, out_of,
                     "" if why == "set" else "  [redefined check]"))
        if len(stale) > 8:
            print("      ... and %d more" % (len(stale) - 8))
        print("      These are NOT compared, NOT carried and NOT replaced. They need")
        print("      re-measurement; --recut re-marks one and archives the old mark.")
    if blocked:
        print("  NOTHING WRITTEN: the store disagrees with the instrument (%d drifted,"
              % len(drift))
        print("  %d inconsistent, %d marks)." % (len(inconsistent), len(mark_drift)))

    if regressions:
        print("  REGRESSED: %d document(s) below their best ever score" % len(regressions))
        for doc, score, best, out_of, checks, why in sorted(regressions)[:15]:
            print("      %-40s %2d/%d was %2d/%d  %s%s"
                  % (doc[:40], score, out_of, best, out_of, why,
                     (": " + ", ".join(checks[:4])) if checks else ""))
        if len(regressions) > 15:
            print("      ... and %d more" % (len(regressions) - 15))
    if strict and total < measured_all:
        print("  FAIL (--strict): %d document(s) never measured" % (measured_all - total))

    if inconsistent:
        print("  FAIL: %d row(s) stamp a universe that is not their denominator"
              % len(inconsistent))
    if drift or mark_drift:
        print("  NOT COMPARED: %d row(s) and %d mark(s) are counted out of a universe"
              % (len(drift), len(mark_drift)))
        print("  the instrument does not have (%d). A count out of %s is not a count"
              % (N, "/".join(sorted({str(o) for _d, _s, o, _u in drift})) or "?"))
        print("  out of %d, so these are reported and skipped - never compared, never" % N)
        print("  carried, never replaced. That is the drift this file exists to catch.")

    # The trace line has to say what this run actually concluded. It used to say
    # "held or rose" whenever no document regressed - so on 13 Nov, when every mark
    # was re-cut without a comparison and the gate printed PASS, and again on any run
    # that fails on drift alone, TRACE.md recorded a hold. A log that reports a hold
    # on a failing run is the drift hiding in a second place. It now says UNMEASURED
    # when the run compared less than it scored, which is the one thing a reader of
    # the trace most needs to know.
    why = []
    if regressions:
        why.append("REGRESSED %d" % len(regressions))
    if drift or mark_drift:
        why.append("DRIFT %d rows/%d marks" % (len(drift), len(mark_drift)))
    if stale:
        why.append("STALE %d" % len(stale))
    if inconsistent:
        why.append("INCONSISTENT %d" % len(inconsistent))
    tool = "ratchet%s" % (" --txt" if TXT_MODE else "")

    if verdict == "PASS":
        note(tool, "held or rose - %d of %d compared" % (len(compared), total))
        print("  PASS - the bar held or rose")
        return 0

    if verdict == "FAIL":
        note(tool, "FAIL " + "; ".join(why))
        if regressions or inconsistent:
            print("  FAIL - the bar fell")
        else:
            print("  FAIL (--strict) - %d document(s) were never measured"
                  % (measured_all - total))
        return 1

    # ---- UNMEASURED --------------------------------------------------------
    gap = max(len(not_compared), len(stale), len(drift))
    note(tool, "UNMEASURED %d of %d not compared%s%s"
         % (len(not_compared), total,
            "; waived: " + reason if allow_stale else "",
            "; " + "; ".join(why) if why else ""))
    print("  UNMEASURED - the bar was not asked: %d of %d document(s) could not be"
          % (gap, total))
    print("  compared, and %d were. Nothing fell. This is not a pass: a document that"
          % len(compared))
    print("  could not be compared has not held its bar, it has not been asked.")
    print("  ledger: %s" % os.path.basename(_ledger_paths(TXT_MODE)[0]))
    if allow_stale:
        print("  WAIVED: \"%s\"" % reason)
        print("  The gap is recorded, not closed. tools/commit-gate.sh reads WAIVER.json")
        print("  and decides whether this is small enough and paid-down enough to commit")
        print("  through. It is not this file's decision to make.")
    else:
        print("  To record a waiver: --allow-stale --reason \"<what you are accepting>\".")
        print("  To close it: re-measure the documents named above under this instrument.")
    return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
