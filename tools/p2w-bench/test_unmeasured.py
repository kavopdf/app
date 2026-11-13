#!/usr/bin/env python3
"""
test_unmeasured.py - does the gate actually behave the way it now claims to?

WHY THIS EXISTS
  On 13 Nov the ratchet had two answers for three states of the world. Every one of
  the 211 marks had been taken by an instrument that no longer existed, so it said
  "FAIL - the bar fell" about a corpus where nothing had moved, and it said
  "PASS (--allow-stale)" when asked to stop saying that. Both were wrong, and the
  fix - a third verdict plus a written waiver plus a policy that bounds it - is
  exactly the kind of fix that rots unless something checks it.

  The two harnesses that might have caught the original defect are both red at HEAD
  for reasons of their own (verify_toolbox.py dies in its record.py fixture,
  audit_sim.py dies building its first RATCHET.json), so this file is standalone on
  purpose: no corpus, no Drive, no engine, a three-document store built here.

WHAT IT ASSERTS
  The verdicts       0 pass, 1 a document fell, 2 refused, 3 unmeasured - and 3 is
                     never 0, because "not asked" must not read as "held".
  The ledger         names every document it could not compare, and why.
  The waiver         cannot exist without a reason, and does not turn 3 into 0.
  The policy         refuses a gap with nothing compared; allows one that a
                     measurement round has paid down; refuses a changed row that
                     was measured by a retired instrument; refuses a gap that grows;
                     refuses a gap carried for more than three waivers.
  Closure            a full re-measure makes the ratchet pass and needs no waiver.

USAGE
  python3 tools/p2w-bench/test_unmeasured.py
  python3 tools/p2w-bench/test_unmeasured.py -v
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
COPIES = ("ratchet.py", "instrument.py", "verify_google.py", "unmeasured.py",
          "record.py", "trace.py")

results = []


def check(name, ok, why=""):
    results.append((name, ok, why))
    print("%s %-62s %s" % ("ok  " if ok else "FAIL", name, why))


def live():
    out = subprocess.check_output(
        [sys.executable, os.path.join(HERE, "verify_google.py"), "--list-checks"],
        text=True, stderr=subprocess.DEVNULL)
    return sorted({l.strip() for l in out.splitlines() if l.strip()})


def sha(ids):
    return hashlib.sha1("\n".join(sorted(ids)).encode()).hexdigest()[:12]


def sandbox(n=3):
    """A three-document store, committed, with marks from a retired instrument.

    The marks are stamped with N-1 checks and a universe one short of the live one,
    which is the shape the 211 real marks are in: measured, complete, and by an
    instrument that no longer exists.
    """
    d = tempfile.mkdtemp(prefix="um-")
    os.makedirs(os.path.join(d, "tools/p2w-bench"))
    for f in COPIES:
        src = os.path.join(HERE, f)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(d, "tools/p2w-bench", f))
    ids = live()
    old = ids[:-1]
    oldsha = sha(old)
    docs = ["doc%02d" % i for i in range(n)]
    rows, marks, table = [], {}, []
    for i, doc in enumerate(docs):
        failed = [ids[0]] if i == 0 else []
        score = len(old) - len([c for c in failed if c in old])
        rows.append({"doc": doc, "engine": "old", "round": 1, "score": score,
                     "total": len(old), "failed": failed, "universe": old,
                     "universe_n": len(old), "universe_sha": oldsha,
                     "universe_source": "values", "values": {}})
        marks[doc] = {"best": score, "out_of": len(old), "failed": failed,
                      "universe": old, "universe_n": len(old),
                      "universe_sha": oldsha}
        table.append("| %s | %d/%d | FAIL | %s | old | 13 Nov | u%d |"
                     % (doc, score, len(old), ", ".join(failed), len(old)))
    p = os.path.join(d, "tools/p2w-bench")
    open(os.path.join(p, "RESULTS.jsonl"), "w").write(
        "".join(json.dumps(r) + "\n" for r in rows))
    json.dump(marks, open(os.path.join(p, "RATCHET.json"), "w"), indent=2)
    open(os.path.join(p, "BASELINE.md"), "w").write(
        "# baseline\n\n| document | score | verdict | failed checks | engine | measured | universe |\n"
        "|---|---|---|---|---|---|---|\n" + "\n".join(table) + "\n")
    for cmd in (["init", "-q"], ["config", "user.email", "t@t"],
                ["config", "user.name", "t"], ["add", "-A"],
                ["commit", "-qm", "stores as committed"]):
        subprocess.run(["git"] + cmd, cwd=d, capture_output=True)
    return d, docs, ids


def run(d, script, *args):
    r = subprocess.run([sys.executable, os.path.join(d, "tools/p2w-bench", script)]
                       + list(args), cwd=d, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def remeasure(d, docs, ids):
    """What a real measurement round writes: row, mark and table row, all live."""
    s = sha(ids)
    p = os.path.join(d, "tools/p2w-bench")
    rows = [json.loads(l) for l in open(os.path.join(p, "RESULTS.jsonl")) if l.strip()]
    marks = json.load(open(os.path.join(p, "RATCHET.json")))
    table = open(os.path.join(p, "BASELINE.md")).read().splitlines()
    for doc in docs:
        failed = [c for c in (marks.get(doc, {}).get("failed") or []) if c in ids]
        score = len(ids) - len(failed)
        rows.append({"doc": doc, "engine": "new", "round": 1, "score": score,
                     "total": len(ids), "failed": failed, "universe": ids,
                     "universe_n": len(ids), "universe_sha": s,
                     "universe_source": "values", "values": {}})
        marks[doc] = {"best": score, "out_of": len(ids), "failed": failed,
                      "universe": ids, "universe_n": len(ids), "universe_sha": s}
        for i, line in enumerate(table):
            if line.startswith("| %s |" % doc):
                c = line.split("|")
                c[2] = " %d/%d " % (score, len(ids))
                c[4] = " " + ", ".join(failed) + " "
                c[7] = " u%d " % len(ids)
                table[i] = "|".join(c)
    open(os.path.join(p, "RESULTS.jsonl"), "w").write(
        "".join(json.dumps(r) + "\n" for r in rows))
    json.dump(marks, open(os.path.join(p, "RATCHET.json"), "w"), indent=2)
    open(os.path.join(p, "BASELINE.md"), "w").write("\n".join(table) + "\n")


def main():
    ids = live()

    # ---- the verdicts ------------------------------------------------------
    d, docs, ids = sandbox()
    rc, out = run(d, "ratchet.py", "--check")
    check("every mark stale -> exit 3 (UNMEASURED)", rc == 3, "exit %d" % rc)
    check("and it does not say the bar fell", "the bar fell" not in out)
    led = json.load(open(os.path.join(d, "tools/p2w-bench/UNMEASURED.json")))
    check("ledger names every document it could not compare",
          set(led["not_compared"]) == set(docs), "%d" % len(led["not_compared"]))
    check("ledger says why", {v["why"] for v in led["not_compared"].values()}
          == {"stale-mark"})

    # ---- the waiver --------------------------------------------------------
    rc, _ = run(d, "ratchet.py", "--allow-stale")
    check("--allow-stale without --reason is refused (exit 2)", rc == 2, "exit %d" % rc)
    rc, _ = run(d, "ratchet.py", "--allow-stale", "--reason", "carrying the gap")
    check("--allow-stale does not launder a pass (still exit 3)", rc == 3, "exit %d" % rc)
    w = json.load(open(os.path.join(d, "tools/p2w-bench/WAIVER.json")))
    check("the waiver carries its reason", w["reason"] == "carrying the gap")

    # ---- the policy: nothing was compared ----------------------------------
    rc, out = run(d, "unmeasured.py")
    check("policy refuses a gap with nothing compared", rc == 1, "exit %d" % rc)
    check("and asks for a measurement", "measure at least one" in out)

    # ---- the policy: a round lands -----------------------------------------
    remeasure(d, [docs[0]], ids)
    rc, out = run(d, "ratchet.py", "--check")
    check("a partly measured corpus is still exit 3", rc == 3, "exit %d" % rc)
    check("and reports what it did compare", "compared against a mark   : 1" in out)
    run(d, "ratchet.py", "--allow-stale", "--reason", "measured what the attempt touched")
    rc, out = run(d, "unmeasured.py")
    check("policy allows a gap that a round has paid down", rc == 0, "exit %d" % rc)

    # ---- the policy: evidence must come from this instrument ---------------
    p = os.path.join(d, "tools/p2w-bench")
    rows = [json.loads(l) for l in open(os.path.join(p, "RESULTS.jsonl")) if l.strip()]
    rows.append({"doc": docs[1], "engine": "old", "round": 2, "score": 3,
                 "total": len(ids) - 1, "failed": [], "universe": ids[:-1],
                 "universe_n": len(ids) - 1, "universe_sha": sha(ids[:-1]),
                 "universe_source": "values", "values": {}})
    open(os.path.join(p, "RESULTS.jsonl"), "w").write(
        "".join(json.dumps(r) + "\n" for r in rows))
    rc, out = run(d, "unmeasured.py")
    check("policy refuses a changed row from a retired instrument", rc == 1,
          "exit %d" % rc)
    check("and names the document", docs[1] in out)

    # ---- the policy: the gap may not grow ----------------------------------
    d2, docs2, ids2 = sandbox()
    remeasure(d2, [docs2[0]], ids2)
    run(d2, "ratchet.py", "--allow-stale", "--reason", "one measured, two carried")
    rc, _ = run(d2, "unmeasured.py")
    check("waiver one is allowed", rc == 0, "exit %d" % rc)
    p2 = os.path.join(d2, "tools/p2w-bench")
    rows = [json.loads(l) for l in open(os.path.join(p2, "RESULTS.jsonl")) if l.strip()]
    rows = [r for r in rows if not (r["doc"] == docs2[0] and r["universe_n"] == len(ids2))]
    open(os.path.join(p2, "RESULTS.jsonl"), "w").write(
        "".join(json.dumps(r) + "\n" for r in rows))
    marks = json.load(open(os.path.join(p2, "RATCHET.json")))
    marks[docs2[0]] = {"best": 3, "out_of": len(ids2) - 1, "failed": [],
                       "universe": ids2[:-1], "universe_n": len(ids2) - 1,
                       "universe_sha": sha(ids2[:-1])}
    json.dump(marks, open(os.path.join(p2, "RATCHET.json"), "w"), indent=2)
    run(d2, "ratchet.py", "--allow-stale", "--reason", "one went back to unmeasured")
    rc, out = run(d2, "unmeasured.py")
    check("policy refuses a gap that grew", rc == 1, "exit %d" % rc)
    check("and names the document that went back", docs2[0] in out)

    # ---- the policy: the gap cannot be carried for ever --------------------
    d3, docs3, ids3 = sandbox()
    remeasure(d3, [docs3[0]], ids3)
    for i in (1, 2, 3):
        run(d3, "ratchet.py", "--allow-stale", "--reason", "carry %d" % i)
        rc, _ = run(d3, "unmeasured.py")
        check("waiver %d of 3 is allowed" % i, rc == 0, "exit %d" % rc)
    run(d3, "ratchet.py", "--allow-stale", "--reason", "carry 4")
    rc, out = run(d3, "unmeasured.py")
    check("the fourth waiver is refused", rc == 1, "exit %d" % rc)
    check("and a measurement round is demanded", "measurement round" in out)

    # ---- closure: the gap can be paid off ----------------------------------
    d4, docs4, ids4 = sandbox()
    remeasure(d4, docs4, ids4)
    rc, out = run(d4, "ratchet.py", "--check")
    check("a full re-measure passes (exit 0)", rc == 0, "exit %d" % rc)
    check("and says the bar held", "PASS - the bar held or rose" in out)
    check("nothing is left in the gap",
          json.load(open(os.path.join(d4, "tools/p2w-bench/UNMEASURED.json")))
          ["counts"]["not_compared"] == 0
          if os.path.exists(os.path.join(d4, "tools/p2w-bench/UNMEASURED.json")) else True)

    bad = [n for n, ok, _ in results if not ok]
    print("\n%d checks, %d passed, %d failed"
          % (len(results), len(results) - len(bad), len(bad)))
    if bad:
        print("\nA verdict that cannot tell 'not asked' from 'passed' is the defect")
        print("this file exists to keep out.")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
