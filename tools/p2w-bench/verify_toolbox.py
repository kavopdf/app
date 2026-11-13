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
    # The fixtures must use the count the verifier actually has. Written as 58,
    # they went stale the moment check 59 was added - the same hardcoded
    # denominator this whole pipeline is built to avoid.
    N = len(uni)
    # a mark from the same universe, nothing changed
    json.dump({"a": {"best": N - 2, "out_of": N, "failed": ["09_font_names"],
                     "universe": uni}}, open(os.path.join(w, "RATCHET.json"), "w"))
    baseline_row(w, ["| a | %d/%d | FAIL | 09_font_names | e | d |" % (N - 2, N)])
    rc, _ = run(w, "ratchet.py")
    check("exit 0 when the bar held", rc == 0, "got %d" % rc)
    baseline_row(w, ["| a | %d/%d | FAIL | 09_font_names | e | d |" % (N - 8, N)])
    rc, _ = run(w, "ratchet.py")
    check("exit 1 when the score fell", rc == 1, "got %d" % rc)
    # the same score, but a check that used to pass now fails
    json.dump({"a": {"best": N - 2, "out_of": N,
                     "failed": ["09_font_names", "20_within_10pt"],
                     "universe": uni}}, open(os.path.join(w, "RATCHET.json"), "w"))
    baseline_row(w, ["| a | %d/%d | FAIL | 09_font_names, 32_stroke_lines | e | d |" % (N - 2, N)])
    rc, out = run(w, "ratchet.py")
    check("exit 1 when a check that passed now fails", rc == 1, "got %d" % rc)
    check("says which check newly failed", "32_stroke_lines" in out)
    # A mark taken by a smaller verifier must not bind - and it must not be called a
    # pass either. This asserted rc == 0, which was the defect: a document whose mark
    # was taken by another instrument was reported as having held its bar. It is
    # UNMEASURED now, and 3 is the answer that says so without accusing the document.
    json.dump({"a": {"best": 31, "out_of": 50, "failed": ["09_font_names"],
                     "universe": uni[:31]}}, open(os.path.join(w, "RATCHET.json"), "w"))
    baseline_row(w, ["| a | 31/%d | FAIL | 09_font_names, 49_page_size | e | d |" % N])
    rc, out = run(w, "ratchet.py")
    check("a weaker verifier's mark does not bind", rc == 3, "got %d" % rc)
    check("and is called UNMEASURED, not a pass", "UNMEASURED" in out and "PASS" not in out)
    check("and is recorded in the ledger",
          os.path.exists(os.path.join(w, "UNMEASURED.json")))
    # documented: 0 pass, 1 fell, 2 refused, 3 not asked
    src = open(os.path.join(w, "ratchet.py")).read()
    check("ratchet has all four exit codes", "return 3" in src and "return 2" in src)
    check("and never exits 0 for an unmeasured run",
          "UNMEASURED - the bar was not asked" in src)
    # A waiver is a written act: no reason, no waiver.
    rc, _ = run(w, "ratchet.py", "--allow-stale")
    check("--allow-stale without --reason is refused", rc == 2, "got %d" % rc)
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
    for name in ("fixer", "baseline", "classifier"):
        rc, _ = run(w, "round.py", "--claim-%s" % name)
        first = rc
        rc, _ = run(w, "round.py", "--claim-%s" % name)
        second = rc
        run(w, "round.py", "--release-%s" % name)
        check("--claim-%s allows then refuses" % name, first == 0 and second == 1,
              "first %d, second %d" % (first, second))
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
    # The outcome is computed from the numbers. A fixer cannot call something kept
    # when the numbers say improved, and cannot claim either without numbers.
    rc, out = run(w, "classify.py", "--attempt", "47_margins", "--moved", "12", "--total", "20")
    check("12 of 20 moved is computed as kept", "kept" in out and "FIXED" in out,
          out.strip()[:70])
    rc, out = run(w, "classify.py", "--attempt", "22_reading_order", "--moved", "8", "--total", "20")
    check("8 of 20 moved is computed as improved", "improved" in out and "requeue" in out,
          out.strip()[:70])
    rc, out = run(w, "classify.py", "--attempt", "09_font_names", "--moved", "3", "--total", "20")
    check("3 of 20 moved is computed as reverted", "reverted" in out, out.strip()[:70])

    rc, out = run(w, "classify.py", "--attempt", "11_bold_runs", "--moved", "8",
                  "--total", "20", "--outcome", "kept")
    check("a claim the numbers contradict is refused", rc == 1, "got %d" % rc)
    check("and it says what the numbers actually were", "improved" in out, out.strip()[:70])
    rc, out = run(w, "classify.py", "--attempt", "36_underline_rules", "--outcome", "kept")
    check("kept without numbers is refused", rc == 1, "got %d" % rc)
    rc, out = run(w, "classify.py", "--attempt", "42_alignment_mix", "--outcome", "error")
    check("error needs no numbers", rc == 0, "got %d" % rc)
    led = json.load(open(os.path.join(w, "ATTEMPTS.json")))
    check("a refused attempt is not recorded",
          "11_bold_runs" not in led and "36_underline_rules" not in led,
          "ledger holds %s" % sorted(led))
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

    # ---------------- docnames.py ----------------
    print("docnames.py")
    d = tempfile.mkdtemp(prefix="dn-")
    subprocess.run(["git", "init", "-q"], cwd=d, capture_output=True)
    bench = os.path.join(d, "tools", "p2w-bench")
    os.makedirs(bench, exist_ok=True)
    shutil.copy(os.path.join(HERE, "docnames.py"), bench)
    base = os.path.join(bench, "BASELINE.md")
    head = ("| document | score | verdict | failed checks | engine | measured |\n"
            "|---|---|---|---|---|---|\n"
            "| 375_attendance_register | 47/59 | FAIL | x | e | d |\n"
            "| 37_font_not_embedded_substitution | 55/59 | FAIL | y | e | d |\n"
            "| 380_runbook_terminal_output | 50/59 | FAIL | z | e | d |\n")
    open(base, "w", encoding="utf-8").write(head)
    subprocess.run(["git", "add", "-A"], cwd=d, capture_output=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=a",
                    "commit", "-qm", "base"], cwd=d, capture_output=True)

    def dn(*args):
        r = subprocess.run([PY, os.path.join(bench, "docnames.py")] + list(args),
                           cwd=d, capture_output=True, text=True)
        return r.returncode, r.stdout.strip()

    rc, out = dn()
    check("docnames says so when nothing changed", out == "no document changed", out)

    # one row moves: exactly that name comes back
    open(base, "w", encoding="utf-8").write(head.replace("| 47/59 |", "| 48/59 |"))
    rc, out = dn()
    check("docnames names the document that changed", out == "375_attendance_register", out)
    rc, out = dn("--count")
    check("--count agrees", out == "1", out)

    # the case that fooled the range: 375 and 37 are both inside "375-382"
    open(base, "w", encoding="utf-8").write(
        head.replace("| 47/59 |", "| 48/59 |").replace("| 55/59 |", "| 56/59 |"))
    rc, out = dn()
    check("docnames lists both, and never a range",
          "375_attendance_register" in out and "37_font_not_embedded_substitution" in out
          and "-" not in out.replace("_", ""), out)
    rc, out = dn("--long")
    check("--long puts one per line", len(out.split("\n")) == 2, repr(out))

    rc, out = dn("--count")
    check("docnames always exits 0", rc == 0, "rc %d" % rc)
    shutil.rmtree(d, ignore_errors=True)

    # the brief must carry the rule
    body = open(os.path.join(HERE, "BASELINE-BRIEF.md"), encoding="utf-8").read()
    check("the baseline brief forbids a range in the commit message",
          "docnames.py" in body and "Never a range" in body)

    # ---------------- retry.sh ----------------
    print("retry.sh")
    RETRY = os.path.join(HERE, "..", "retry.sh")

    def retry(*args):
        r = subprocess.run(["bash", RETRY] + list(args), capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr).strip()

    for text, want in [
        ("API rate limit exceeded for 1.2.3.4", "transient"),
        ("You have exceeded a secondary rate limit", "transient"),
        ("HttpError 429: Too Many Requests", "transient"),
        ("502 Bad Gateway", "transient"),
        ("fatal: unable to access: Connection reset by peer", "transient"),
        ("Bad credentials", "permanent"),
        ("403 Resource not accessible by integration", "permanent"),
        ("404 Not Found", "permanent"),
        ("no space left on device", "permanent"),
        ("403 Forbidden", "permanent"),
        ("fatal: destination path already exists", "already-done"),
        ("something entirely unexpected", "unknown"),
    ]:
        rc, out = retry("--classify", text)
        check("classify %-42s" % ('"' + text[:40] + '"'), out == want,
              "expected %s, got %s" % (want, out))

    # a permanent failure must not be retried: one attempt, then stop
    d = tempfile.mkdtemp(prefix="rt-")
    counter = os.path.join(d, "n")
    script = os.path.join(d, "perm.sh")
    open(script, "w").write(
        "#!/bin/bash\nN=$(cat %s 2>/dev/null || echo 0); N=$((N+1)); echo $N > %s\n"
        "echo 'Bad credentials'; exit 1\n" % (counter, counter))
    os.chmod(script, 0o755)
    rc, out = retry("--", script)
    check("a permanent failure is attempted once, not three times",
          open(counter).read().strip() == "1", "attempts: %s" % open(counter).read().strip())
    check("and it says so plainly", "PERMANENT" in out, out[-90:])

    # a transient failure retries and gives up at the limit
    open(counter, "w").write("0")
    script2 = os.path.join(d, "trans.sh")
    open(script2, "w").write(
        "#!/bin/bash\nN=$(cat %s 2>/dev/null || echo 0); N=$((N+1)); echo $N > %s\n"
        "echo '429 Too Many Requests'; exit 1\n" % (counter, counter))
    os.chmod(script2, 0o755)
    rc, out = retry("--tries", "2", "--", script2)
    check("a transient failure retries up to the limit",
          open(counter).read().strip() == "2", "attempts: %s" % open(counter).read().strip())
    check("and it names the next run as the retry", "next scheduled run" in out, out[-90:])

    # a command that works first time is not retried
    open(counter, "w").write("0")
    script3 = os.path.join(d, "ok.sh")
    open(script3, "w").write(
        "#!/bin/bash\nN=$(cat %s 2>/dev/null || echo 0); N=$((N+1)); echo $N > %s\nexit 0\n"
        % (counter, counter))
    os.chmod(script3, 0o755)
    rc, out = retry("--", script3)
    check("a command that succeeds is run once", rc == 0 and open(counter).read().strip() == "1",
          "rc %d, attempts %s" % (rc, open(counter).read().strip()))

    # already-done counts as success
    open(counter, "w").write("0")
    script4 = os.path.join(d, "exists.sh")
    open(script4, "w").write(
        "#!/bin/bash\necho 'fatal: destination path already exists'; exit 128\n")
    os.chmod(script4, 0o755)
    rc, out = retry("--", script4)
    check("already-done exits 0 rather than failing the cron", rc == 0, "rc %d" % rc)

    # the documents the crons are told to read must exist
    for f in ("RETRY.md", "INCIDENTS.md", "LESSONS.md"):
        check("%s exists for the crons to read" % f, os.path.exists(os.path.join(HERE, f)))
    for name in ("BASELINE", "CLASSIFIER", "FIXER"):
        b = os.path.join(HERE, "%s-BRIEF.md" % name)
        body = open(b, encoding="utf-8").read() if os.path.exists(b) else ""
        check("%s brief tells the cron what to do when something fails" % name,
              "RETRY.md" in body and "INCIDENTS.md" in body)

    shutil.rmtree(d, ignore_errors=True)

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
