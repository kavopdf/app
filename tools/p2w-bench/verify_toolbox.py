#!/usr/bin/env python3
"""
verify_toolbox.py - test what TOOLBOX.md claims, not just which flags it names.

toolbox_check.py proves the flags exist. It cannot prove the sentences around them
are true: that exit 1 means failed and not something else, that a file is actually
written, that a duplicate is actually refused. A reference can be flag-perfect and
still lie about behaviour, and a cron that trusts it acts on the lie.

So every behavioural claim in TOOLBOX.md gets a test here. If a tool changes what
it returns or what it writes, this fails and the document has to be corrected with
it. That is the only way a reference stays honest.

Run from tools/p2w-bench:  python3 verify_toolbox.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
ok = 0
bad = []


def check(name, condition, detail=""):
    global ok
    if condition:
        ok += 1
        print("  PASS  %s" % name)
    else:
        bad.append("%s %s" % (name, detail))
        print("  FAIL  %s  %s" % (name, detail))


def run(work, script, *args):
    r = subprocess.run([PY, os.path.join(work, script)] + list(args),
                       cwd=work, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def run_stdout(work, script, *args):
    """stdout only.

    round.py writes an interface hint to stderr, and PyMuPDF writes warnings
    there. Merging the two made --phase look like two words and put warning text
    into the check universe, which then looked like a different verifier and
    quietly disabled the ratchet. Both were test bugs, not tool bugs - but a test
    that reads the wrong stream will always find the wrong thing.
    """
    r = subprocess.run([PY, os.path.join(work, script)] + list(args),
                       cwd=work, capture_output=True, text=True)
    return r.returncode, r.stdout


def fresh(files=("verify_google.py", "record.py", "ratchet.py", "round.py",
                 "classify.py", "hypothesis.py", "reset_round.py")):
    d = tempfile.mkdtemp(prefix="tbx-")
    for f in files:
        src = os.path.join(HERE, f)
        if os.path.exists(src):
            shutil.copy(src, d)
    return d


def make_pdf(path, extra=False):
    import fitz
    d = fitz.open()
    p = d.new_page(width=595, height=842)
    p.insert_text((72, 100), "Invoice 123", fontsize=11)
    if extra:
        p.insert_text((72, 400), "extra line", fontsize=11)
    d.save(path)
    d.close()


def baseline_row(work, rows):
    with open(os.path.join(work, "BASELINE.md"), "w", encoding="utf-8") as f:
        f.write("| document | score | verdict | failed checks | engine | measured |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(r + "\n")


def main():
    # ---------------- verify_google.py ----------------
    print("verify_google.py")
    w = fresh()
    make_pdf(os.path.join(w, "a.pdf"))
    make_pdf(os.path.join(w, "b.pdf"))
    make_pdf(os.path.join(w, "c.pdf"), extra=True)

    rc, _ = run(w, "verify_google.py", "a.pdf", "b.pdf")
    check("exit 0 when every check passes", rc == 0, "got %d" % rc)
    rc, _ = run(w, "verify_google.py", "a.pdf", "c.pdf")
    check("exit 1 when a check fails", rc == 1, "got %d" % rc)
    rc, _ = run(w, "verify_google.py", "a.pdf", "missing.pdf")
    check("exit 2 when it cannot run", rc == 2, "got %d" % rc)

    rc, out = run_stdout(w, "verify_google.py", "--list-checks")
    check("--list-checks prints the denominator", len(out.split()) >= 40,
          "%d ids" % len(out.split()))

    run(w, "verify_google.py", "a.pdf", "c.pdf", "--json", "o1.json")
    run(w, "verify_google.py", "a.pdf", "c.pdf", "--json", "o2.json")
    d = json.load(open(os.path.join(w, "o1.json")))
    need = ["document", "source_file", "render_file", "passed", "total", "ok",
            "failed", "checks"]
    check("--json carries every documented field", all(k in d for k in need),
          "missing %s" % [k for k in need if k not in d])
    check("--json check value has source, render, ok",
          all(k in list(d["checks"].values())[0] for k in ("source", "render", "ok")))
    same = (open(os.path.join(w, "o1.json")).read() ==
            open(os.path.join(w, "o2.json")).read())
    check("deterministic: the same pair twice is identical", same)
    shutil.rmtree(w, ignore_errors=True)

    # ---------------- record.py ----------------
    print("record.py")
    w = fresh()
    make_pdf(os.path.join(w, "a.pdf"))
    make_pdf(os.path.join(w, "c.pdf"), extra=True)
    run(w, "verify_google.py", "a.pdf", "c.pdf", "--json", "o.json")
    run(w, "record.py", "o.json", "--round", "1", "--engine", "e1")
    n1 = len(open(os.path.join(w, "RESULTS.jsonl")).readlines())
    run(w, "record.py", "o.json", "--round", "1", "--engine", "e1")
    n2 = len(open(os.path.join(w, "RESULTS.jsonl")).readlines())
    run(w, "record.py", "o.json", "--round", "1", "--engine", "e2")
    n3 = len(open(os.path.join(w, "RESULTS.jsonl")).readlines())
    check("writes RESULTS.jsonl", n1 == 1, "%d lines" % n1)
    check("same document, round and engine replaces, not appends", n2 == 1, "%d lines" % n2)
    check("a different engine adds a line", n3 == 2, "%d lines" % n3)
    rc, out = run(w, "record.py", "--show", "a")
    check("--show finds a recorded document", rc == 0, "got %d" % rc)
    check("--show prints source and render", "source=" in out and "render=" in out)
    rc, _ = run(w, "record.py", "--show", "nope")
    check("--show exits 1 when there is no record", rc == 1, "got %d" % rc)
    shutil.rmtree(w, ignore_errors=True)

    # ---------------- ratchet.py ----------------
    print("ratchet.py")
    w = fresh()
    rc, out = run_stdout(w, "verify_google.py", "--list-checks")
    uni = [l.strip() for l in out.split() if l.strip()]
    # a mark from the same universe, nothing changed
    json.dump({"a": {"best": 56, "out_of": 58, "failed": ["09_font_names"],
                     "universe": uni}}, open(os.path.join(w, "RATCHET.json"), "w"))
    baseline_row(w, ["| a | 56/58 | FAIL | 09_font_names | e | d |"])
    rc, _ = run(w, "ratchet.py")
    check("exit 0 when the bar held", rc == 0, "got %d" % rc)
    baseline_row(w, ["| a | 50/58 | FAIL | 09_font_names | e | d |"])
    rc, _ = run(w, "ratchet.py")
    check("exit 1 when the score fell", rc == 1, "got %d" % rc)
    # the same score, but a check that used to pass now fails
    json.dump({"a": {"best": 56, "out_of": 58,
                     "failed": ["09_font_names", "20_within_10pt"],
                     "universe": uni}}, open(os.path.join(w, "RATCHET.json"), "w"))
    baseline_row(w, ["| a | 56/58 | FAIL | 09_font_names, 32_stroke_lines | e | d |"])
    rc, out = run(w, "ratchet.py")
    check("exit 1 when a check that passed now fails", rc == 1, "got %d" % rc)
    check("says which check newly failed", "32_stroke_lines" in out)
    # a mark taken by a smaller verifier must not bind
    json.dump({"a": {"best": 31, "out_of": 50, "failed": ["09_font_names"],
                     "universe": uni[:31]}}, open(os.path.join(w, "RATCHET.json"), "w"))
    baseline_row(w, ["| a | 31/58 | FAIL | 09_font_names, 49_page_size | e | d |"])
    rc, _ = run(w, "ratchet.py")
    check("a weaker verifier's mark does not bind", rc == 0, "got %d" % rc)
    # documented: only 0 and 1 exist
    src = open(os.path.join(w, "ratchet.py")).read()
    check("ratchet has no third exit code", "return 2" not in src)
    shutil.rmtree(w, ignore_errors=True)

    # ---------------- round.py ----------------
    print("round.py")
    w = fresh()
    rc, out = run_stdout(w, "round.py", "--phase")
    check("--phase prints one bare word", out.strip() == "measure", repr(out.strip()))
    run(w, "round.py", "--advance")
    rc, out = run_stdout(w, "round.py", "--phase")
    check("--advance moves measure to classify", out.strip() == "classify", repr(out.strip()))
    run(w, "round.py", "--advance")
    rc, _ = run(w, "round.py", "--claim-fixer")
    check("--claim-fixer allows the first run", rc == 0, "got %d" % rc)
    rc, _ = run(w, "round.py", "--claim-fixer")
    check("--claim-fixer refuses a second", rc == 1, "got %d" % rc)
    s = json.load(open(os.path.join(w, "ROUND.json")))
    s["fixer_started"] = 0
    json.dump(s, open(os.path.join(w, "ROUND.json"), "w"))
    rc, _ = run(w, "round.py", "--apk-status")
    check("--apk-status refuses while the rounds run", rc == 1, "got %d" % rc)

    baseline_row(w, ["| a | 40/58 | FAIL | x | e | d |"])
    json.dump({"c": {"attempts": 2}}, open(os.path.join(w, "ATTEMPTS.json"), "w"))
    run(w, "round.py", "--claim-fixer")
    s = json.load(open(os.path.join(w, "ROUND.json")))
    s["apk_shipped"] = "9.9.9"
    json.dump(s, open(os.path.join(w, "ROUND.json"), "w"))
    run(w, "round.py", "--close-round")
    check("--close-round writes ROUND-1.md", os.path.exists(os.path.join(w, "ROUND-1.md")))
    check("--close-round writes ATTEMPTS-round-1.json",
          os.path.exists(os.path.join(w, "ATTEMPTS-round-1.json")))
    body = open(os.path.join(w, "BASELINE.md")).read().split("\n")[2]
    check("--close-round empties the score", body.split("|")[2].strip() == "", body)
    s = json.load(open(os.path.join(w, "ROUND.json")))
    check("--close-round clears the fixer claim", not s.get("fixer_started"))
    check("--close-round clears the shipped mark", not s.get("apk_shipped"))
    check("--close-round moves to the next round", s["round"] == 2 and s["phase"] == "measure",
          "%s %s" % (s["round"], s["phase"]))
    os.remove(os.path.join(w, "BASELINE.md"))
    rc, _ = run(w, "round.py", "--close-round")
    check("--close-round survives a missing BASELINE.md", rc == 0, "got %d" % rc)
    shutil.rmtree(w, ignore_errors=True)

    # ---------------- classify.py ----------------
    print("classify.py")
    w = fresh()
    rows = []
    for i in range(20):
        fails = ["47_margins"]
        if i % 2 == 0:
            fails.append("22_reading_order")
        rows.append("| d%02d | 40/58 | FAIL | %s | e | d |" % (i, ", ".join(fails)))
    baseline_row(w, rows)
    rc, out = run(w, "classify.py")
    check("classify.py runs", rc == 0, "got %d" % rc)
    check("writes DEFECT-CLASSES.md", os.path.exists(os.path.join(w, "DEFECT-CLASSES.md")))
    check("ATTEMPTS.json waits for the first attempt",
          not os.path.exists(os.path.join(w, "ATTEMPTS.json")))
    body = open(os.path.join(w, "DEFECT-CLASSES.md")).read()
    check("a universal check is its own class",
          "| 47_margins " in body or "| 47_margins |" in body, "not found alone")
    rc, out = run(w, "classify.py", "--subclusters", "47_margins")
    check("--subclusters finds a class by its printed name", rc == 0, "got %d" % rc)
    rc, out = run(w, "classify.py", "--attempt", "47_margins", "--outcome", "kept")
    check("--attempt kept marks the class FIXED", "FIXED" in out, out.strip()[:60])
    rc, out = run(w, "classify.py", "--attempt", "22_reading_order", "--outcome", "improved")
    check("--attempt improved restarts the day", "requeue" in out, out.strip()[:60])
    rc, out = run(w, "classify.py", "--attempt", "22_reading_order", "--outcome", "reverted")
    check("--attempt reverted counts against the limit", "attempts=" in out, out.strip()[:60])
    shutil.rmtree(w, ignore_errors=True)

    # ---------------- hypothesis.py ----------------
    print("hypothesis.py")
    w = fresh()
    rc, out = run(w, "hypothesis.py", "--show", "c1")
    check("--show on an empty class says so", "no hypotheses" in out)
    run(w, "hypothesis.py", "--add", "c1", "theory one", "--result", "ruled-out",
        "--evidence", "n=3")
    check("writes HYPOTHESES.md", os.path.exists(os.path.join(w, "HYPOTHESES.md")))
    rc, out = run(w, "hypothesis.py", "--add", "c1", "theory one", "--result", "ruled-out")
    check("refuses a duplicate hypothesis", "already recorded" in out)
    run(w, "hypothesis.py", "--add", "c1", "theory two", "--result", "untested")
    rc, out = run(w, "hypothesis.py", "--next", "c1")
    check("--next shows only what is untested", "theory two" in out and "theory one" not in out)
    rc, out = run(w, "hypothesis.py", "--add", "c1", "theory two", "--result", "ruled-out")
    check("a theory already recorded can be given its result",
          "updated" in out, out.strip()[:70])
    rc, out = run(w, "hypothesis.py", "--next", "c1")
    check("--next says so when nothing is left", "nothing left untested" in out)
    shutil.rmtree(w, ignore_errors=True)

    # ---------------- reset_round.py ----------------
    print("reset_round.py")
    w = fresh()
    baseline_row(w, ["| a | 31/58 | FAIL | x | e | d |"])
    json.dump({"a": {"best": 31}}, open(os.path.join(w, "RATCHET.json"), "w"))
    json.dump({"c": {"attempts": 1}}, open(os.path.join(w, "ATTEMPTS.json"), "w"))
    json.dump({"round": 2, "rounds_total": 3, "phase": "fix", "history": []},
              open(os.path.join(w, "ROUND.json"), "w"))
    before = open(os.path.join(w, "BASELINE.md")).read()
    rc, out = run(w, "reset_round.py")
    check("dry run changes nothing",
          open(os.path.join(w, "BASELINE.md")).read() == before)
    check("dry run says nothing changed", "nothing changed" in out)
    rc, _ = run(w, "reset_round.py", "--yes")
    check("--yes exits 0 and verifies itself clean", rc == 0, "got %d" % rc)
    check("scores are emptied",
          open(os.path.join(w, "BASELINE.md")).read().split("\n")[2].split("|")[2].strip() == "")
    check("RATCHET.json is emptied",
          json.load(open(os.path.join(w, "RATCHET.json"))) == {})
    check("ATTEMPTS.json is removed", not os.path.exists(os.path.join(w, "ATTEMPTS.json")))
    s = json.load(open(os.path.join(w, "ROUND.json")))
    check("ROUND.json is back to round 1 measure",
          s["round"] == 1 and s["phase"] == "measure", "%s %s" % (s["round"], s["phase"]))
    check("everything was archived first",
          any(d.startswith("reset-") for d in os.listdir(os.path.join(w, "archive"))))
    shutil.rmtree(w, ignore_errors=True)

    # ---------------- summary ----------------
    print("")
    total = ok + len(bad)
    print("%d checks, %d passed, %d failed" % (total, ok, len(bad)))
    if bad:
        print("")
        for b in bad:
            print("  FAILED: %s" % b)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
