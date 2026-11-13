#!/usr/bin/env python3
"""Prove audit.py both ways: does it catch a planted bug, and does it stay quiet otherwise?

THE GROUND TRUTH IS THIS FILE. Every mutation below is a bug I wrote on purpose, in a scratch
copy, and I know exactly which check should see it. Nothing here asks audit.py whether it is
right - it asks whether the thing I planted came back, and whether anything else did.

Three kinds of case:
  FIRE   a planted bug must produce a finding naming the right kind
  QUIET  code that is correct must produce no finding
  MISS   a bug I believe the check CANNOT see - recorded so the limitation is stated, not hidden

Usage: python3 prove_audit.py [--verbose]
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "R")
BENCH = os.path.join(REPO, "tools", "p2w-bench")
VERBOSE = "--verbose" in sys.argv


def scratch():
    d = tempfile.mkdtemp(prefix="prove-")
    shutil.copytree(REPO, os.path.join(d, "R"),
                    ignore=shutil.ignore_patterns(".git", "t", "all", "out", "gd", "res"))
    return os.path.join(d, "R")


def run_audit(root, check):
    r = subprocess.run([sys.executable, os.path.join(root, "tools", "p2w-bench", "audit.py"),
                        "--" + check],
                       capture_output=True, text=True, cwd=root)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def read(root, rel):
    return open(os.path.join(root, rel), encoding="utf-8").read()


def write(root, rel, s):
    open(os.path.join(root, rel), "w", encoding="utf-8").write(s)


def patch(root, rel, old, new, count=1):
    s = read(root, rel)
    if s.count(old) < 1:
        raise RuntimeError("mutation anchor not found in %s: %r" % (rel, old[:60]))
    write(root, rel, s.replace(old, new, count))


# ------------------------------------------------------------------ mutations
def m_tools(r):
    patch(r, "tools/p2w-bench/FIXER-BRIEF.md", "STEP 0c - READ WHAT ALREADY COST US TIME",
          "Run tools/p2w-bench/does_not_exist.py first.\n\nSTEP 0c - READ WHAT ALREADY COST US TIME")


def m_numbers(r):
    patch(r, "tools/p2w-bench/classify.py", "MAX_ATTEMPTS = 24", "MAX_ATTEMPTS = 30")


def m_ranges(r):
    tb = read(r, "tools/p2w-bench/TOOLBOX.md")
    # insert a section the fixer brief never mentions, between two of its anchors
    tb = tb.replace("## seed.py", "## brand_new_tool.py\n\n    nothing uses this\n\n## seed.py", 1)
    write(r, "tools/p2w-bench/TOOLBOX.md", tb)


def m_gates(r):
    # a measure gate that accepts a document scored twice
    p = os.path.join(r, "tools", "p2w-bench", "measure_gate.py")
    s = open(p, encoding="utf-8").read()
    s = s.replace("    return 0 if ok else 1", "    return 0")
    open(p, "w", encoding="utf-8").write(s)


def m_clock(r):
    patch(r, "tools/p2w-bench/ratchet.py", "def main(", "def _stamp():\n    return time.strftime('%H:%M:%S')\n\n\ndef main(")


def m_dead(r):
    patch(r, "tools/p2w-bench/ratchet.py", "def main(", "def orphan_function():\n    return 1\n\n\ndef main(")


def m_ids(r):
    s = read(r, "tools/p2w-bench/FIXER-BRIEF.md")
    s = re.sub(r'ENGINE="\$ENGINE-[^"]*"', 'ENGINE="$ENGINE-dirty"', s, count=1)
    write(r, "tools/p2w-bench/FIXER-BRIEF.md", s)


def m_growth(r):
    with open(os.path.join(r, "tools", "p2w-bench", "TRACE.md"), "a", encoding="utf-8") as f:
        f.write(("| 13 Nov 00:00 | fixer | padding | " + "x" * 180 + " |\n") * 1200)


def m_evidence(r):
    s = read(r, "tools/p2w-bench/round.py")
    s = s.replace("note(", "_nope(").replace("trace import note", "trace import _nope")
    write(r, "tools/p2w-bench/round.py", s)


def m_states(r):
    s = read(r, "tools/p2w-bench/round.py")
    s = s.replace('if "--close-round" in argv', 'if "--archive-round" in argv')
    write(r, "tools/p2w-bench/round.py", s)


def m_mutation(r):
    # a suite that no longer tests what it claims
    write(r, "tools/p2w-bench/code_test.py",
          "import sys\n\ndef main():\n    print('all cases behave as claimed')\n    return 0\n\nsys.exit(main())\n")


# ------------------------------------------------------------------ blind spots
def m_dead_in_prose(r):
    """A dead function whose name is also mentioned in a brief. K counts occurrences in all
    text, so the mention hides the definition. Believed MISSED."""
    patch(r, "tools/p2w-bench/ratchet.py", "def main(", "def visible_helper():\n    return 1\n\n\ndef main(")
    patch(r, "tools/p2w-bench/FIXER-BRIEF.md", "STEP 0c - READ WHAT ALREADY COST US TIME",
          "visible_helper is a thing that exists.\n\nSTEP 0c - READ WHAT ALREADY COST US TIME")


def m_ids_gone(r):
    """The engine-id formula removed entirely. E says 'no formula' and passes. Believed MISSED."""
    s = read(r, "tools/p2w-bench/FIXER-BRIEF.md")
    s = re.sub(r'ENGINE="\$ENGINE-[^"]*"', 'ENGINE="whatever"', s, count=1)
    write(r, "tools/p2w-bench/FIXER-BRIEF.md", s)


# ------------------------------------------------------------------ cases
CASES = [
    # (name, check, mutation, expect, kind)
    ("a brief names a tool that does not exist", "tools", m_tools, "FIRE", "B"),
    ("MAX_ATTEMPTS changed to 30, prose still says 24", "numbers", m_numbers, "FIRE", "B"),
    ("a new TOOLBOX section lands inside a fixer range", "ranges", m_ranges, "FIRE", "I"),
    ("measure_gate accepts a document scored twice", "gates", m_gates, "FIRE", "C"),
    ("a timestamp written without the IST offset", "clock", m_clock, "FIRE", "J"),
    ("a function defined and never called", "dead", m_dead, "FIRE", "K"),
    ("the engine id becomes a constant suffix", "ids", m_ids, "FIRE", "E"),
    ("TRACE.md grows past its trim", "growth", m_growth, "FIRE", "N"),
    ("round.py stops writing trace lines", "evidence", m_evidence, "FIRE", "A"),
    ("--close-round removed, so fix has no exit", "states", m_states, "FIRE", "F"),
    ("a test suite stops testing", "mutation", m_mutation, "FIRE", "L"),

    # near-misses: correct code that looks like a bug
    ("a docstring that merely mentions a tool path", "tools", None, "QUIET", ""),
    ("the real repo, unmutated", "numbers", None, "QUIET", ""),
    ("the real repo, unmutated (clock)", "clock", None, "QUIET", ""),
    ("the real repo, unmutated (dead)", "dead", None, "QUIET", ""),
    ("the real repo, unmutated (evidence)", "evidence", None, "QUIET", ""),

    # blind spots, recorded rather than hidden
    # These two were the blind spots the first proof run found. They are cases now, not
    # footnotes: a check that knows it cannot see something should be fixed or say so, and
    # after 13 Nov these two were fixed.
    ("a dead function whose name appears in a brief", "dead", m_dead_in_prose, "FIRE", "K"),
    ("the engine-id formula removed altogether", "ids", m_ids_gone, "FIRE", "E"),
]


def main():
    print("=" * 78)
    print("proving audit.py - planted bugs, and code that is not a bug")
    print("=" * 78)
    if not os.path.isdir(REPO):
        print("  the repo is not at %s" % REPO)
        return 1

    results = []
    for name, check, mut, expect, kind in CASES:
        root = scratch()
        try:
            if mut:
                try:
                    mut(root)
                except Exception as e:
                    results.append((name, check, expect, "BROKEN", str(e)))
                    print("  %-52s %-8s BROKEN  %s" % (name[:52], check, e))
                    continue
            code, out = run_audit(root, check)
            fired = code != 0
            got_kind = ""
            if fired:
                m = re.search(r"\[([A-Z])\]", out)
                got_kind = m.group(1) if m else "?"

            if expect == "FIRE":
                if fired and (not kind or got_kind == kind):
                    verdict = "PASS"
                elif fired:
                    verdict = "WRONG-KIND(%s)" % got_kind
                else:
                    verdict = "MISSED"
            elif expect == "QUIET":
                verdict = "PASS" if not fired else "FALSE-POSITIVE"
            else:  # MISS
                verdict = "PASS(as predicted)" if not fired else "CAUGHT(better than expected)"

            results.append((name, check, expect, verdict, got_kind))
            print("  %-52s %-8s %-22s %s" % (name[:52], check, expect, verdict))
            if VERBOSE and fired:
                for line in out.splitlines():
                    if "[%s]" % got_kind in line:
                        print("       -> %s" % line.strip()[:100])
        finally:
            shutil.rmtree(os.path.dirname(root), ignore_errors=True)

    print("\n" + "=" * 78)
    fire = [r for r in results if r[2] == "FIRE"]
    quiet = [r for r in results if r[2] == "QUIET"]
    miss = [r for r in results if r[2] == "MISS"]
    caught = [r for r in fire if r[3] == "PASS"]
    wrong = [r for r in fire if r[3] not in ("PASS",)]
    fp = [r for r in quiet if r[3] != "PASS"]
    blind = [r for r in miss if r[3].startswith("PASS")]

    print("SENSITIVITY  %d of %d planted bugs caught with the right kind" % (len(caught), len(fire)))
    for r in wrong:
        print("   MISSED  %s (%s) -> %s" % (r[0], r[1], r[3]))
    print("SPECIFICITY  %d of %d clean cases stayed quiet" % (len(quiet) - len(fp), len(quiet)))
    for r in fp:
        print("   FALSE POSITIVE  %s (%s)" % (r[0], r[1]))
    print("BLIND SPOTS  %d of %d predicted misses confirmed" % (len(blind), len(miss)))
    for r in blind:
        print("   cannot see  %s" % r[0])
    return 0 if not wrong and not fp else 1


if __name__ == "__main__":
    sys.exit(main())
