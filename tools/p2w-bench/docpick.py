#!/usr/bin/env python3
"""Which check, if closed, turns the most documents CLEAN.

WHY THIS EXISTS. The fixer has been picking a CLASS and taking one attempt at it. Measured 23 Nov: 60 runs,
80% improved nothing, 60% made 0 or 1 attempt - and 20 documents a day "improved" while the clean count sat at
30 for days. An improvement that moves a check on one document is not progress; it is a number that looks like
progress. What moves the score is a document reaching all 42 checks.

So the unit is not the class and not the check. It is THE DOCUMENT THAT IS CLOSEST TO CLEAN, and the check that
is standing in its way.

    python3 tools/p2w-bench/docpick.py             # the lever table: check -> documents it would clean
    python3 tools/p2w-bench/docpick.py --next      # the one thing to do now
    python3 tools/p2w-bench/docpick.py --doc NAME  # what still blocks one document, and by how much

The top line on 23 Nov was 18_displacement: 101 documents fail it and 13 are failing NOTHING ELSE, so closing
that one check takes the clean count from 30 to 43 in a single move. No class table showed that, because a
class table counts documents affected, not documents finished.

Reads only benchmarks/gverify/*.json - the Google verdict, which is the authority. A document refused on page
count is not scored and is not counted here.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GVERIFY = os.path.join(ROOT, "benchmarks", "gverify")


def _engine_now():
    """The engine commit the corpus is built from right now."""
    import subprocess
    try:
        r = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%h", "--",
                            "app/src/main/java/com/kavopdf/app/engine/"],
                           capture_output=True, text=True, timeout=20)
        return (r.stdout or "").strip()
    except Exception:
        return ""


def scored(current_only=True):
    """[(name, [failed check ids])] for every document Google scored ON THE CURRENT ENGINE.

    MIXING ENGINES SENDS THE FIXER AFTER PROBLEMS THAT ARE ALREADY GONE. Measured 23 Nov: over all engines
    `18_displacement` failed 101 documents and looked like the whole job; on the engine the corpus is built
    from now it fails 20. The other 81 were measured before the fix landed, so ranking on them ranks history.

    gverify.py's own --report already counts only current-engine results for this reason. This now agrees
    with it. A document with no engine stamp, or an older one, is not counted - the tool that owns the number
    is gverify, and this reads what it says rather than what happens to be on disk.
    """
    now = _engine_now()
    out = []
    for f in glob.glob(os.path.join(GVERIFY, "*.json")):
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if j.get("status") == "page_count_refused":
            continue
        if current_only and now and j.get("engine") != now:
            continue
        out.append((os.path.basename(f)[:-5], list(j.get("failed") or [])))
    return out


def lever(rows):
    """[(check, docs_failing_it, docs_it_would_clean)] sorted by documents finished."""
    fail = {}
    only = {}
    for _name, failed in rows:
        for c in failed:
            fail[c] = fail.get(c, 0) + 1
        if len(failed) == 1:
            only[failed[0]] = only.get(failed[0], 0) + 1
    out = [(c, n, only.get(c, 0)) for c, n in fail.items()]
    # Documents finished first: that is the score. Documents touched is a tiebreak, not the goal.
    out.sort(key=lambda t: (-t[2], -t[1], t[0]))
    return out


def main(argv):
    rows = scored()
    if not rows:
        print("no scored documents in %s - run gverify first" % GVERIFY)
        return 2

    clean = [n for n, f in rows if not f]
    if "--doc" in argv:
        want = argv[argv.index("--doc") + 1]
        hit = [(n, f) for n, f in rows if want in n]
        if not hit:
            print("no scored document matches %r" % want)
            return 1
        for n, f in hit:
            if not f:
                print("%s: CLEAN - all 42 checks pass" % n)
            else:
                print("%s: %d check(s) left" % (n, len(f)))
                for c in f:
                    print("    %s" % c)
        return 0

    table = lever(rows)

    if "--next" in argv:
        # The single best move: the check that finishes the most documents, and one document to prove it on.
        if not table:
            print("every scored document is clean")
            return 0
        check, fails, cleans = table[0]
        proof = [n for n, f in rows if f == [check]]
        print("NEXT: close %s" % check)
        print("  %d document(s) fail it, and %d fail NOTHING ELSE - so this one check takes the clean "
              "count from %d to %d." % (fails, cleans, len(clean), len(clean) + cleans))
        if proof:
            print("  prove it on: %s" % proof[0])
            print("  then the other %d: %s" % (len(proof) - 1, ", ".join(proof[1:6]) or "-"))
        print()
        print("  A document counts as improved when it is CLEAN, not when a check moved. Record the attempt")
        print("  with the document name; attempt.py keeps it.")
        return 0

    print("clean: %d of %d scored" % (len(clean), len(rows)))
    print()
    print("  %-34s %8s %10s" % ("check", "fails", "would clean"))
    for c, n, cl in table[:15]:
        mark = "  <<<" if cl >= 3 else ""
        print("  %-34s %8d %10d%s" % (c[:34], n, cl, mark))
    print()
    left = len(rows) - len(clean)
    near = sum(1 for _n, f in rows if 0 < len(f) <= 3)
    print("  %d document(s) still not clean; %d of them are 1-3 checks away." % (left, near))
    print("  The score is documents finished. Pick the check that finishes the most.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
