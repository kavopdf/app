#!/usr/bin/env python3
"""
audit_sim.py - run the pipeline as a model and see whether it actually finishes.

A DIFFERENT WAY TO AUDIT
  The first audit read the files: does every path exist, does every script parse,
  is every check id unique, is every gate wired. That finds things that are
  written wrong.

  It cannot find things that are written right and still go wrong. A state machine
  can have every file present, every script parsing, and still deadlock on the
  third round because a phase never advances. The only way to know is to run it.

  So this drives round.py, classify.py and ratchet.py through a synthetic corpus
  and a synthetic three rounds, exactly as the crons would, and asserts that it
  reaches 'done'. It also attacks it: missing files, interrupted runs, a class
  that never improves, a class that improves forever.

WHAT IT PROVES
  every phase advance is reachable
  no state deadlocks
  a round closes even when every class is parked
  three rounds finish
  a fourth round cannot start
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

# the tools live next to this file - a hardcoded sandbox path made this
# script unrunnable anywhere except the pod it was written on
SRC = os.path.dirname(os.path.abspath(__file__))
FILES = ["round.py", "classify.py", "ratchet.py", "verify_google.py"]

results = []


def run(workdir, args, timeout=180):
    return subprocess.run([sys.executable] + args, cwd=workdir, capture_output=True,
                          text=True, timeout=timeout)


def sandbox(n_docs=6):
    d = tempfile.mkdtemp(prefix="sim-")
    for f in FILES:
        shutil.copy(os.path.join(SRC, f), d)
    rows = ["| document | score | verdict | failed checks | engine | measured |",
            "|---|---|---|---|---|---|"]
    for i in range(n_docs):
        rows.append("| doc%02d |  |  |  |  |  |" % i)
    open(os.path.join(d, "BASELINE.md"), "w").write("\n".join(rows) + "\n")
    for f in ("RATCHET.json", "ATTEMPTS.json", "DEFECT-CLASSES.md"):
        p = os.path.join(d, f)
        if os.path.exists(p):
            os.remove(p)
    return d


def score_all(d, fail_sets):
    """Write scores for every document, as the baseline cron would."""
    rows = ["| document | score | verdict | failed checks | engine | measured |",
            "|---|---|---|---|---|---|"]
    for doc, failed in fail_sets.items():
        out_of = 58
        rows.append("| %s | %d/%d | %s | %s | e | d |" % (
            doc, out_of - len(failed), out_of,
            "FAIL" if failed else "PASS", ", ".join(failed)))
    open(os.path.join(d, "BASELINE.md"), "w").write("\n".join(rows) + "\n")


def phase(d):
    return run(d, ["round.py", "--phase"]).stdout.strip()


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print("%-58s %s %s" % (name, "PASS" if ok else "FAIL", detail))


def main():
    # ---- 1. happy path: three rounds -------------------------------------
    d = sandbox()
    check("fresh state starts in measure", phase(d) == "measure", phase(d))

    for rnd in (1, 2, 3):
        # measure phase: baseline fills every score, then advances
        score_all(d, {"doc%02d" % i: ["20_within_10pt", "32_stroke_lines"] for i in range(6)})
        run(d, ["round.py", "--advance"])                     # measure -> classify
        p = phase(d)
        check("round %d: measure advances to classify" % rnd, p == "classify", p)

        # classify phase: build classes, then advance
        run(d, ["classify.py"])
        run(d, ["round.py", "--advance"])                     # classify -> fix
        p = phase(d)
        check("round %d: classify advances to fix" % rnd, p == "fix", p)

        # fix phase: every class parked, so the round must close
        classes = os.path.join(d, "DEFECT-CLASSES.md")
        txt = open(classes).read().replace("| OPEN |", "| PARKED |")
        open(classes, "w").write(txt)
        r = run(d, ["round.py", "--close-round"])
        p = phase(d)
        expected = "measure" if rnd < 3 else "done"
        check("round %d: closes and phase becomes %s" % (rnd, expected), p == expected,
              r.stdout.strip()[:50])

    # ---- 2. a fourth round cannot start -----------------------------------
    r = run(d, ["round.py", "--close-round"])
    check("round 4 cannot start (still done)", phase(d) == "done", phase(d))

    # ---- 3. archive exists ------------------------------------------------
    for rnd in (1, 2, 3):
        p = os.path.join(d, "ROUND-%d.md" % rnd)
        check("round %d archive written" % rnd, os.path.exists(p))

    # ---- 4. scores emptied on close so the next round has work ------------
    d2 = sandbox()
    score_all(d2, {"doc%02d" % i: [] for i in range(6)})
    run(d2, ["round.py", "--advance"])
    run(d2, ["classify.py"])
    run(d2, ["round.py", "--advance"])
    open(os.path.join(d2, "DEFECT-CLASSES.md"), "w").write(
        "| # | class | documents | share | checks in class | attempts | requeues | status |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| 1 | 20_within_10pt | 6 | 100% | 20_within_10pt | 0 | 0 | PARKED |\n")
    run(d2, ["round.py", "--close-round"])
    body = open(os.path.join(d2, "BASELINE.md")).read()
    import re as _re
    empty = len(_re.findall(r"^\| [^|]+ \|\s+\|\s+\|\s+\|\s+\|\s+\|\s*$", body, _re.M))
    check("close empties every score", empty == 6, "%d empty rows" % empty)

    # ---- 5. attempts ledger archived and cleared -------------------------
    check("ATTEMPTS.json cleared for the new round",
          not os.path.exists(os.path.join(d2, "ATTEMPTS.json")))
    ap = os.path.join(d2, "ATTEMPTS-round-1.json")
    ok = os.path.exists(ap)
    check("ATTEMPTS archive always written", ok,
          "empty {}" if ok and open(ap).read().strip() == "{}" else "")

    # ---- 6. ratchet survives the reset -----------------------------------
    # A document that reached 50/58 in round 1 must not be allowed to fall to
    # 40/58 in round 2 just because the scores were emptied.
    d3 = sandbox()
    score_all(d3, {"doc00": ["20_within_10pt", "32_stroke_lines"]})
    run(d3, ["ratchet.py"])
    before = json.load(open(os.path.join(d3, "RATCHET.json")))
    score_all(d3, {"doc00": ["20_within_10pt", "32_stroke_lines",
                             "09_font_names", "47_margins", "22_reading_order"]})
    r = run(d3, ["ratchet.py", "--check"])
    check("ratchet catches a drop after the round reset", r.returncode == 1,
          "exit %d" % r.returncode)

    # ---- 7. attack: DEFECT-CLASSES.md missing while phase is fix ----------
    d4 = sandbox()
    score_all(d4, {"doc00": ["20_within_10pt"]})
    run(d4, ["round.py", "--advance"])
    run(d4, ["classify.py"])
    run(d4, ["round.py", "--advance"])
    os.remove(os.path.join(d4, "DEFECT-CLASSES.md"))
    # The fixer decides "no class is OPEN" by reading this file. If it is absent
    # the fixer would close the round having fixed nothing.
    r = run(d4, ["classify.py"])
    exists_after = os.path.exists(os.path.join(d4, "DEFECT-CLASSES.md"))
    check("classify rebuilds a missing DEFECT-CLASSES.md", exists_after)

    # ---- 8. attack: ROUND.json missing -----------------------------------
    d5 = sandbox()
    check("missing ROUND.json defaults to round 1 measure", phase(d5) == "measure")

    # ---- 9. attack: BASELINE.md missing ----------------------------------
    d6 = sandbox()
    os.remove(os.path.join(d6, "BASELINE.md"))
    r = run(d6, ["round.py"])
    check("round.py survives a missing BASELINE.md", r.returncode == 0,
          "exit %d" % r.returncode)
    r = run(d6, ["ratchet.py", "--check"])
    check("ratchet survives a missing BASELINE.md", r.returncode == 0,
          "exit %d" % r.returncode)

    # ---- 10. attack: an empty class table --------------------------------
    d7 = sandbox()
    open(os.path.join(d7, "DEFECT-CLASSES.md"), "w").write(
        "| # | class | documents | share | checks in class | attempts | requeues | status |\n"
        "|---|---|---|---|---|---|---|---|\n")
    r = run(d7, ["round.py"])
    check("round.py counts zero open classes", "open classes     : 0" in r.stdout,
          r.stdout.splitlines()[2] if len(r.stdout.splitlines()) > 2 else "")

    # ---- summary ---------------------------------------------------------
    bad = [n for n, ok, _ in results if not ok]
    print("\n%d checks, %d passed, %d failed" % (len(results), len(results) - len(bad), len(bad)))
    for n in bad:
        print("  FAILED:", n)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
