#!/usr/bin/env python3
"""regress.py - THE COMMIT GATE. Nothing lands without a full-corpus regression check.

THE RULE, AND IT IS UNIVERSAL: no commit may land, for the .docx or the .txt, unless the whole
corpus has been measured with the engine as it stands and **no document got worse**. Not one. Not
by one point. Not "only a little". A fix that improves 20 documents and damages 1 is not a fix, it
is a trade, and nobody authorised the trade.

This is enforced in three ways, because a rule in a document is not a rule:

    1. tools/p2w-bench/regress.py --check          exit 1 on any regression
    2. .git/hooks/pre-commit                       runs it; a non-zero exit aborts the commit
    3. tools/p2w-bench/step.py                     refuses to release a fixer slot while it fails

WHAT "WORSE" MEANS, PER FORMAT

    .docx   share@5px went UP for any document. share5 is the share of the page's ink that sits
            more than 5 px from where the page drew it, so a larger number is a worse document.
            The bar for FIXED is share5 <= 1.0 (99 %), but the bar for NOT WORSE is zero movement
            upward - a document at 40 may not drift to 40.1.

    .txt    any document that fails a check it did not fail in the baseline. Checks are pass/fail,
            so the comparison is the failing set, and a new member of that set is a regression
            however small the check looks.

THE SECOND HALF, WHICH IS EASIER TO FORGET: AN UNMEASURED CHANGE IS NOT A PASS.

    If the engine has changed since the corpus was last measured, the tables describe an engine
    that no longer exists, and "no regressions" is a statement about nothing. This tool compares
    the current engine fingerprint against the one stamped into the tables and REFUSES when they
    differ. That is why the 411 fix could be committed and the t13 patch could not: 411 was
    measured across 213 documents and proved to move exactly one; t13 was measured and moved 101
    the wrong way.

    python3 tools/p2w-bench/regress.py --check
    python3 tools/p2w-bench/regress.py --check --allow-engine-change   (never for a commit)
"""
import argparse, csv, hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RANK = os.path.join(ROOT, "benchmarks", "RANKING.csv")
RANK_BASE = os.path.join(ROOT, "benchmarks", "RANKING-BASELINE.csv")
TXT = os.path.join(HERE, "txt", "RANKING-TXT.csv")
TXT_BASE = os.path.join(HERE, "txt", "RANKING-TXT-BASELINE.csv")
STAMP = os.path.join(HERE, "txt", "ENGINE-STAMP.json")
ENGINE_DIR = os.path.join(ROOT, "app", "src", "main", "java", "com", "kavopdf", "app", "engine")


def sh(cmd, timeout=120):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=timeout, cwd=ROOT)
    except Exception:
        return None


def engine_fingerprint():
    """A hash of the engine sources, so a table can say which engine produced it."""
    h = hashlib.sha256()
    if not os.path.isdir(ENGINE_DIR):
        return "NO-ENGINE-DIR"
    for name in sorted(os.listdir(ENGINE_DIR)):
        if not name.endswith(".java"):
            continue
        h.update(name.encode())
        with open(os.path.join(ENGINE_DIR, name), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:16]


def read_rank(path):
    """{document: share5} for rows that carry a score."""
    out = {}
    if not os.path.exists(path):
        return out
    for r in csv.DictReader(open(path, encoding="utf-8")):
        d = r.get("document")
        s = (r.get("share5") or "").strip()
        if not d or not s:
            continue
        try:
            out[d] = float(s)
        except ValueError:
            continue
    return out


def read_txt(path):
    """{document: set(failing check ids)}. '-' is the published placeholder for 'fails nothing'."""
    out = {}
    if not os.path.exists(path):
        return out
    for r in csv.DictReader(open(path, encoding="utf-8")):
        d = r.get("document")
        if not d:
            continue
        out[d] = {x for x in (r.get("failed_ids") or "").split() if x and x != "-"}
    return out


def previous_table(path):
    """The committed version of a table, read out of git - the real floor for the ratchet.

    A BASELINE IS NOT ENOUGH ON ITS OWN. RANKING-BASELINE.csv is the 15 Nov starting point, so a
    document that improved from 10.78 to 0.50 could drift back to 5.00 and this gate would still
    say "no regression", because 5.00 is better than 10.78. That is a ratchet with a slack rope.
    Whatever a document last measured at, it may not be worse than that now.
    """
    r = sh("git show HEAD:%s" % os.path.relpath(path, ROOT), timeout=60)
    if r is None or r.returncode != 0 or not r.stdout.strip():
        return {}
    import io
    out = {}
    for row in csv.DictReader(io.StringIO(r.stdout)):
        d, v = row.get("document"), (row.get("share5") or "").strip()
        if not d or not v:
            continue
        try:
            out[d] = float(v)
        except ValueError:
            continue
    return out


def docx_regressions():
    cur, base = read_rank(RANK), read_rank(RANK_BASE)
    prev = previous_table(RANK)
    if not base:
        return [], "no baseline table"
    worse = []
    for d in set(base) | set(prev):
        c = cur.get(d)
        b, pv = base.get(d), prev.get(d)
        if c is None:
            worse.append((d, b, None, "MISSING from the current table"))
            continue
        if b is not None and c > b + 1e-9:
            worse.append((d, b, c, "share@5 up %.2f -> %.2f vs the 15 Nov baseline" % (b, c)))
        elif pv is not None and c > pv + 1e-9:
            worse.append((d, pv, c, "share@5 up %.2f -> %.2f vs the last commit" % (pv, c)))
    return worse, ""


def txt_regressions():
    cur, base = read_txt(TXT), read_txt(TXT_BASE)
    if not base:
        return [], "no baseline table"
    worse = []
    for d, b in base.items():
        c = cur.get(d)
        if c is None:
            worse.append((d, sorted(b), None, "MISSING from the current table"))
        elif c - b:
            worse.append((d, sorted(b), sorted(c), "new failing: %s" % ", ".join(sorted(c - b))))
    return worse, ""


def load_stamp():
    try:
        return json.load(open(STAMP, encoding="utf-8"))
    except Exception:
        return {}


def stamp(scope):
    """Stamp the formats this change can move. A txt-only change does not invalidate the .docx
    table, because the .docx was not re-measured and its engine did not change either."""
    fp = engine_fingerprint()
    rec = load_stamp()
    if not isinstance(rec, dict):
        rec = {}
    rec.pop("engine", None)
    for f in scope:
        rec[f] = fp
    os.makedirs(os.path.dirname(STAMP), exist_ok=True)
    json.dump(rec, open(STAMP, "w", encoding="utf-8"), indent=1)
    print("  stamped %s to engine %s" % (", ".join(sorted(scope)), fp))


def scope_of_change():
    """Which formats this change can move, derived by scope.py. Defaults to BOTH when unsure."""
    r = sh("python3 tools/p2w-bench/scope.py", timeout=120)
    if r is None or r.returncode != 0:
        return {"docx", "txt"}, "scope.py failed - assuming both"
    out = r.stdout
    if "BOTH formats" in out:
        return {"docx", "txt"}, "scope.py: both"
    if "nothing to check" in out:
        return set(), "scope.py: no engine change"
    return ({"txt"} if "txt" in out and "docx" not in out else
            {"docx"} if "docx" in out and "txt" not in out else {"docx", "txt"}), "scope.py: " + out.splitlines()[0].strip()


def check(allow_engine_change, only=None):
    fail = 0
    fp = engine_fingerprint()
    scope, why = scope_of_change()
    if only:
        scope = set(only)
        why = "forced by --only"
    print("  engine fingerprint : %s" % fp)
    print("  scope of the change: %s   (%s)" % (", ".join(sorted(scope)) or "nothing", why))

    need_docx = "docx" in scope
    need_txt = "txt" in scope

    st = load_stamp()
    if not allow_engine_change:
        # THE STAMP IS CHECKED FOR EVERY FORMAT, INCLUDING THE SKIPPED ONES.
        #
        # It used to run only inside `if not needed: continue`, so when scope.py said "no engine
        # change" BOTH formats were skipped and the stamp was never read - the commit passed having
        # verified neither the corpus nor the table's provenance. That is the one path by which a
        # commit could land without a full-corpus regression check, and it was reachable from a
        # tooling-only change, which is most commits.
        #
        # Skipping the measurement is only sound when the table IS the full-corpus measurement of
        # the engine in the tree. The stamp is what says so. If it does not match, the skip is not a
        # pass - it is an unmeasured table, and the run must measure before it commits.
        # EVERY FORMAT, WHETHER OR NOT IT IS BEING RE-MEASURED. A format that is not re-measured is
        # being passed on the strength of the table alone, so the table's stamp is the ONLY thing
        # standing between this commit and an unmeasured corpus. Checking it only for the formats
        # that are being measured checks it exactly where it is least needed.
        for f in ("docx", "txt"):
            was = st.get(f)
            if was is None:
                print("  UNSTAMPED (%s): the table does not say which engine made it, so" % f)
                print("             'no regressions' is a claim about nothing.")
                fail = 1
            elif was != fp:
                print("  ENGINE CHANGED (%s): table measured on %s, the tree is %s" % (f, was, fp))
                print("             An unmeasured change is not a pass. Re-measure, then --stamp.")
                fail = 1

    # THE TABLE IS CHECKED EVEN WHEN THE ENGINE DID NOT CHANGE.
    #
    # This read `docx_regressions() if need_docx else ([], "")`, so a run that did not touch the engine
    # skipped the check. Falsified 19 Nov: a document's share5 was changed from 0.00 to 99.00 and
    # committed, and the gate answered PASS with "docx: not re-measured - the tree is the engine the
    # table was measured on".
    #
    # The stamp says the table was MADE by this engine. It does not say the numbers in it are right,
    # and a baseline run re-measures every document and can write a worse table without touching a line
    # of engine code - a soffice failure, a truncated render, a bad read. Over two months that is the
    # difference between a ratchet and a table nobody is checking.
    #
    # Reading two CSVs costs milliseconds. It runs every time.
    d_bad, d_err = docx_regressions()
    if not need_docx:
        if d_bad:
            print("  docx: %d REGRESSION(S) in the table even though the engine did not change"
                  % len(d_bad))
            for d, b, c, why in d_bad[:10]:
                print("    %-44s %.2f -> %s   %s"
                      % (d[:44], b, "-" if c is None else "%.2f" % c, why))
            print("             The engine is unchanged, so the numbers should be too. Something")
            print("             re-measured and got worse - that is not a pass.")
            fail = 1
        print("  docx: not re-measured - the tree is the engine the table was measured on (%s)"
              % (st.get("docx") or "?"))
    elif d_err:
        print("  docx: %s - cannot check" % d_err)
        fail = 1
    elif d_bad:
        print("  docx: %d REGRESSION(S)" % len(d_bad))
        for d, b, c, why in d_bad[:10]:
            # b is None when the document is in the previous table but not in the 15 Nov
            # baseline - a document added since. The printer used to crash on it
            # ("must be real number, not NoneType") instead of naming the row, so a gate that
            # had found a regression reported a traceback and no reason.
            print("    %-44s %s -> %s   %s" % (d[:44],
                  "-" if b is None else "%.2f" % b,
                  "-" if c is None else "%.2f" % c, why))
        fail = 1
    else:
        print("  docx: no document worse than baseline")

    # SAME HOLE AS THE .docx SIDE, found by the same falsification. A .txt whose failed_ids went from
    # '-' to 't13' was committed with no engine change and the gate answered PASS, because this read
    # `txt_regressions() if need_txt else ([], "")` and need_txt was False.
    #
    # read_txt reads `failed_ids`, not the `failed` count - a falsification that changed only the count
    # proved nothing, and that is worth writing down: a test that cannot fail is not a test.
    t_bad, t_err = txt_regressions()
    if not need_txt:
        if t_bad:
            print("  txt : %d REGRESSION(S) in the table even though the engine did not change"
                  % len(t_bad))
            for d, b, c, why in t_bad[:10]:
                print("    %-44s %s" % (d[:44], why))
            print("             The engine is unchanged, so the numbers should be too.")
            fail = 1
        print("  txt : not re-measured - the tree is the engine the table was measured on (%s)"
              % (st.get("txt") or "?"))
    elif t_err:
        print("  txt : %s - cannot check" % t_err)
        fail = 1
    elif t_bad:
        print("  txt : %d REGRESSION(S)" % len(t_bad))
        for d, b, c, why in t_bad[:10]:
            print("    %-44s %s" % (d[:44], why))
        fail = 1
    else:
        print("  txt : no document worse than baseline")

    print()
    if fail:
        print("  REFUSED. This commit would land a regression or an unmeasured engine.")
        print("  There is no override. Fix the change or revert it.")
    else:
        print("  PASS - nothing got worse in %s, and the table matches this engine."
              % ("both formats" if (need_docx and need_txt) else
                 ("the .docx only" if need_docx else "the .txt only")))
    return fail


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--stamp", action="store_true")
    ap.add_argument("--allow-engine-change", action="store_true")
    ap.add_argument("--only", default="", help="force the scope: docx, txt, or both")
    a = ap.parse_args(argv)
    if a.stamp:
        scope, _ = scope_of_change()
        if a.only:
            scope = {"both": {"docx", "txt"}}.get(a.only, {x.strip() for x in a.only.split(",") if x.strip()})
        stamp(scope or {"docx", "txt"})
        return 0
    if a.check:
        only = None
        if a.only:
            only = ({"docx", "txt"} if a.only == "both"
                    else {x.strip() for x in a.only.split(",") if x.strip()})
        return check(a.allow_engine_change, only)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
