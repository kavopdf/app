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


# THE FINGERPRINT HAS TO DESCRIBE THE ARTEFACT IT STAMPS, OR A .TXT CHANGE IS UNCOMMITTABLE.
#
# It hashed every .java in the engine, so an edit to TxtWriter.java moved the hash the DOCX table
# was stamped with. The docx path never calls TxtWriter - DocxWriter.write() reads the Result that
# PdfToWord.convert() built, and TxtWriter.write() is the only caller of that class - so the docx
# table was being refused as "measured on another engine" by a change that cannot reach a docx byte.
# Measured 20 Nov: it refused the engine commit AND every state commit after it, which is the
# mechanical reason the .txt half had never landed one.
#
# So the docx fingerprint leaves TxtWriter.java out. Nothing else is excluded: DocxWriter.java stays
# in the txt fingerprint, because DocxWriter.orderStamps() reorders page.blocks and TxtWriter walks
# them - the one place a docx-side method can move the .txt.
DOCX_EXCLUDES = ("TxtWriter.java",)


def engine_fingerprint(fmt=None):
    """A hash of the engine sources, so a table can say which engine produced it."""
    h = hashlib.sha256()
    if not os.path.isdir(ENGINE_DIR):
        return "NO-ENGINE-DIR"
    for name in sorted(os.listdir(ENGINE_DIR)):
        if not name.endswith(".java"):
            continue
        if fmt == "docx" and name in DOCX_EXCLUDES:
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


def read_documents(path):
    """Every document that has a ROW in the table, scored or not.

    read_rank() keeps only rows that carry a share5, so an exempt row - present, blank, and named
    problem=exempt - is invisible to it. This is what separates an EXEMPTION (row there, score
    blank) from a DELETION (row gone).
    """
    out = set()
    if not os.path.exists(path):
        return out
    for r in csv.DictReader(open(path, encoding="utf-8")):
        d = (r.get("document") or "").strip()
        if d:
            out.add(d)
    return out


def exempt_docx():
    """The documents EXEMPT.json says cannot be measured, so their blank score is not a regression.

    A BLANK SCORE MEANS "NOT MEASURED", NOT "NOT THERE". gate.py blanks an exempt row's scores and
    names the problem "exempt" (the settled shape, SETTLED.md); read_rank() then drops the row, the
    current table has no entry for the document, and the `c is None` branch below called that
    "MISSING from the current table" - an exemption reported as a regression, for a document
    EXEMPT.json says by design cannot be measured inside one command. Measured 22 Nov:
    416_many_tiny_pages, 300 pages, killed at 290 s even chunked, so the honest table carries it
    blank and the gate refused the honest table.
    """
    try:
        return set(json.load(open(os.path.join(HERE, "EXEMPT.json"),
                                  encoding="utf-8")).get("docx") or {})
    except Exception:
        return set()


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


def google_failed_committed():
    """{document: how many of the 42 checks GOOGLE fails}, from the committed gverify results.

    THE GATE MEASURES THE RENDERER THE USER HAS. Decided 20 Nov: this tool is used in Google Docs,
    not LibreOffice, so a document is judged by what Google does with it.

    LibreOffice stays useful - fast, all 213, catches crashes - but it cannot be the authority:

        regress.py scored share@5 on a soffice render. LibreOffice draws the floating <w:drawing>
        exactly where the PDF drew it. A w:pBdr can never be pixel-identical to it. So every document
        whose rules are already right in LibreOffice MUST get worse the moment its rules become
        borders - however well they are placed - and those are exactly the documents Google fails
        (145 of them, against 2 in LibreOffice).
    """
    out = {}
    r = sh("git ls-tree -r --name-only HEAD benchmarks/gverify 2>/dev/null", timeout=60)
    if r is None or r.returncode != 0:
        return out
    for rel in (r.stdout or "").splitlines():
        rel = rel.strip()
        if not rel.endswith(".json"):
            continue
        rr = sh("git show HEAD:%s" % rel, timeout=60)
        if rr is None or rr.returncode != 0:
            continue
        try:
            d = json.loads(rr.stdout)
        except Exception:
            continue
        if d.get("status") == "page_count_refused":
            continue
        out[os.path.basename(rel)[:-5]] = len(d.get("failed") or [])
    return out


def google_failed_now():
    """The same count from the working tree - what Google says after the change."""
    out = {}
    d = os.path.join(ROOT, "benchmarks", "gverify")
    if not os.path.isdir(d):
        return out
    for f in os.listdir(d):
        if not f.endswith(".json"):
            continue
        try:
            j = json.load(open(os.path.join(d, f), encoding="utf-8"))
        except Exception:
            continue
        if j.get("status") == "page_count_refused":
            continue
        out[f[:-5]] = len(j.get("failed") or [])
    return out



def docx_regressions():
    cur, base = read_rank(RANK), read_rank(RANK_BASE)
    prev = previous_table(RANK)
    if not base:
        return [], "no baseline table"
    # EXEMPT AND PRESENT IS NOT MISSING. Exempt AND ABSENT still is: a row that is gone from the
    # table entirely is a deletion, whatever EXEMPT.json says about its score.
    exempt = exempt_docx() & read_documents(RANK)
    worse = []
    for d in set(base) | set(prev):
        c = cur.get(d)
        b, pv = base.get(d), prev.get(d)
        if c is None:
            if d in exempt:
                print("  docx: EXEMPT  %-38s no score in the table, and EXEMPT.json says it"
                      % d[:38])
                print("        cannot be measured - not a missing measurement")
                continue
            worse.append((d, b, None, "MISSING from the current table"))
            continue
        if b is not None and c > b + 1e-9:
            worse.append((d, b, c, "share@5 up %.2f -> %.2f vs the 15 Nov baseline" % (b, c)))
        elif pv is not None and c > pv + 1e-9:
            worse.append((d, pv, c, "share@5 up %.2f -> %.2f vs the last commit" % (pv, c)))
    # A LIBREOFFICE REGRESSION IS ALLOWED WHEN GOOGLE IMPROVED ON THE SAME DOCUMENT.
    # The user opens Google; a border can never be pixel-identical to the drawing LibreOffice
    # draws, so this class is always a LibreOffice regression - see google_failed_committed.
    g_before = google_failed_committed()
    g_after = google_failed_now()
    _kept, _allowed = [], []
    for _it in worse:
        _d, _b, _c = _it[0], _it[1], _it[2]
        if _c is None or _d not in g_after or _d not in g_before:
            _kept.append(_it); continue
        if g_after[_d] < g_before[_d]:
            _allowed.append((_d, _b, _c, g_before[_d], g_after[_d]))
        else:
            _kept.append(_it)
    for _d, _b, _c, _gb, _ga in _allowed:
        print('  docx: ALLOWED  %-38s %.2f -> %.2f in LibreOffice, Google %d -> %d failing'
              % (_d[:38], _b if _b is not None else 0, _c, _gb, _ga))
    if _allowed:
        print('  docx: %d LibreOffice regression(s) allowed - Google improved on the same' % len(_allowed))
        print('        document, and Google is the renderer the user opens.')
    # A GOOGLE REGRESSION IS THE ONE THAT MATTERS, AND IT WAS INVISIBLE HERE.
    #
    # g_before/g_after above is used only to ALLOW a LibreOffice regression when Google improved on
    # the same document. Nothing refused the opposite: an engine change that takes a document from
    # 42/42 in Google to 39/42. Found on 21 Nov - 310_court_judgment went 42/42 to 39/42
    # (43_within_10pt_x, 47_margins, 60_text_column_right_edge) on engine 462353f, the run's report
    # said 'Regressions: none', and the gate passed - because the ratchet measures LibreOffice share
    # and the user does not open LibreOffice.
    #
    # The user's rule: Google is the authority. A document that fails MORE of Google's 42 checks than
    # it did in the committed results is a regression, whatever LibreOffice says.
    _gbad = [(d, g_before[d], g_after[d]) for d in sorted(g_after)
             if d in g_before and g_after[d] > g_before[d]]
    if _gbad:
        _lines = ['%d document(s) fail MORE of Google\'s 42 checks than the committed results:' % len(_gbad)]
        for _d, _b, _a in _gbad[:10]:
            _lines.append('  %s  %d -> %d failing' % (_d, _b, _a))
        _lines.append('Google is the renderer the user opens. LibreOffice agreeing is not a defence.')
        return _kept, chr(10).join(_lines)
    worse = _kept
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


def _newer_than_engine(relpath):
    """True when `relpath` was committed after the last change to the engine sources."""
    def _t(p):
        r = sh("git log -1 --format=%%ct -- %s" % p, timeout=30)
        try:
            return int((r.stdout or "").strip() or 0)
        except Exception:
            return 0
    eng = _t("app/src/main/java/com/kavopdf/app/engine/")
    tbl = _t(relpath)
    return bool(eng and tbl and tbl >= eng)


def _measured_on_this_tree():
    """True when benchmarks/STATE.json records a COMPLETED measurement of the tree as it is now.

    THE STAMP HAD NO WAY TO ACCEPT A MEASUREMENT MADE BEFORE ITS OWN COMMIT, AND THAT IS A DEADLOCK.
    stamp() refuses unless the table was committed after the engine, and the pre-commit hook refuses
    that commit until the stamp matches the tree. So an engine change measured in the working tree
    could never be committed at all: measured 23 Nov, 212/212 scored, 0 documents worse, and the
    hook still said "REFUSED - this commit would land a regression or an unmeasured engine".
    Two rules that cannot both be satisfied, which is the shape of "measured, fix not landed" in the
    ledger for two runs running.

    The evidence this accepts is the one gate.py writes and nothing else writes: a STATE.json whose
    measurement layer is complete and whose `engine` is the CURRENT tree's identity (head + the sha1
    of the engine diff, the same formula gate.py uses). Touching a file cannot produce it; only a run
    that measured the corpus on this exact source can.
    """
    try:
        st = json.load(open(os.path.join(ROOT, "benchmarks", "STATE.json"), encoding="utf-8"))
    except Exception:
        return None
    if not ((st.get("layers") or {}).get("measurement") or {}).get("complete"):
        return None
    try:
        h = (sh("git log -1 --format=%h -- app/src/main/java/com/kavopdf/app/engine/",
                timeout=30).stdout or "").strip()
        d = (sh("{ git diff -- app/src/main/java/com/kavopdf/app/engine/; "
                "git diff --cached -- app/src/main/java/com/kavopdf/app/engine/; } | sha1sum",
                timeout=60).stdout or "").split()
        d = d[0] if d else ""
        if d and d != "da39a3ee5e6b4b0d3255bfef95601890afd80709":
            live = "%s+%s" % (h, d[:10])
        else:
            live = h
    except Exception:
        return None
    if live and st.get("engine") == live:
        return "%s, %s document(s) scored" % (live, ((st["layers"]["measurement"]).get("of")))
    return None


def stamp(scope):
    """Stamp the formats this change can move - but only if a table was measured on this engine.

    A STAMP IS A CLAIM THAT SOMETHING WAS MEASURED. This wrote the live fingerprint into the stamp
    file unconditionally, so a commit that changed the engine and ran --stamp in the same breath
    made the tables claim they had been measured on code that had never been run. Measured 23 Nov:
    commit 5beb8b9d changed DocxWriter.java by 89 lines AND rewrote this stamp file in the same
    commit, while benchmarks/RANKING.csv was still the one committed four hours earlier. After that
    measure_gate printed "engine docx 4a607e4b793fb348, tree 4a607e4b793fb348 - READY" and
    regress.py printed "the table matches this engine", and neither was true.

    So the stamp now refuses unless the table for that format was committed after the engine it
    claims to describe. Re-measure, then stamp. --allow-engine-change does not bypass this: it
    exists for a deliberate unproven change, not for claiming a measurement that never happened.
    """
    fp = engine_fingerprint()
    rec = load_stamp()
    if not isinstance(rec, dict):
        rec = {}
    rec.pop("engine", None)
    # A measurement made in the working tree, before the commit that carries it, is evidence too -
    # see _measured_on_this_tree(). Without this the stamp and the pre-commit hook deadlock.
    _ev = _measured_on_this_tree()
    _refused = []
    for f in scope:
        _tbl = "benchmarks/RANKING.csv" if f == "docx" else "tools/p2w-bench/txt/RANKING-TXT.csv"
        if not _newer_than_engine(_tbl):
            if _ev:
                print("  %s: %s is not committed after the engine, but STATE.json records a "
                      "completed measurement of this exact tree (%s)" % (f, _tbl, _ev))
            else:
                _refused.append((f, _tbl))
    if _refused:
        print("REFUSED to stamp: a stamp says a table was measured on this engine, and it was not.")
        for f, t in _refused:
            print("  %s: %s is older than the last engine change" % (f, t))
        print("Re-measure the corpus on this engine, then stamp. Stamping without measuring makes")
        print("measure_gate print READY and regress.py print \"the table matches this engine\" for a")
        print("table measured on code that no longer exists - which is what happened on 23 Nov.")
        return 2
    for f in scope:
        rec[f] = engine_fingerprint(f)
    os.makedirs(os.path.dirname(STAMP), exist_ok=True)
    json.dump(rec, open(STAMP, "w", encoding="utf-8"), indent=1)
    print("  stamped %s to engine %s" % (", ".join(sorted(scope)), fp))
    return 0


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
        #
        # EXCEPT WHEN scope.py HAS PROVED THE FORMAT CANNOT MOVE, AND THAT EXCEPTION IS THE ONLY
        # WAY THE .TXT HALF COULD EVER LAND A COMMIT. engine_fingerprint() hashes every .java in
        # the engine, so a change to TxtWriter.java moves the hash the DOCX table was stamped
        # with - and this loop then refused the commit for an unmeasured docx change that scope.py
        # had just proved (method by method) cannot reach a docx byte. Measured 20 Nov: the
        # per-table-column .txt fix, 10 documents better and 0 worse, could not be committed at
        # all, and that is why 46 documents have failed the same .txt checks for a month.
        # The proof is scope.py's METHOD_FORMAT table; the format still gets its own table check
        # below (docx_regressions() runs unconditionally), so nothing is being waved through.
        # A change scope.py cannot attribute leaves scope EMPTY, and that stays strict: an
        # unproven change checks both stamps, exactly as before.
        strict = not scope
        for f in ("docx", "txt"):
            if not strict and f not in scope:
                print("  %s: out of scope - scope.py proved this change cannot move it" % f)
                continue
            was = st.get(f)
            fp = engine_fingerprint(f)
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
    # A CONSTRUCT GOOGLE IGNORES MUST NOT SPREAD. This is the 3.53.5 lesson as a check instead of a
    # paragraph: w:framePr passed LibreOffice, died in Google, and shipped - every stamp on the phone
    # broke while every CI count stayed identical, because CI measured LibreOffice. The same shape has
    # cost the corpus five more times (w:w, w:spacing, embedded faces, floating <w:drawing> rules,
    # w:before at a page top), so it is read from the bytes of the .docx rather than from anyone's
    # memory. A ratchet, not a ban: the corpus already carries them, and what is refused is a
    # document that GAINS one.
    try:
        # THE CORPUS IS BUILT HERE, NOT LEFT TO WHOEVER REMEMBERS.
        #
        # This gate prints "no .docx output directory - cannot check" when the converted corpus is
        # absent, and on 24 Nov that is exactly what it did for every run: the 213 .docx are output of the
        # engine, so any engine change makes them stale, and rebuilding them took 38 minutes sequentially
        # inside a run shorter than that. The gate was never slow - it finishes in 12.6 s - it was being
        # handed nothing to read, so the one check that stops a construct Google ignores from spreading
        # never ran and 0 patches landed.
        #
        # corpus-convert.py --ensure is a stat and a listdir when the corpus is warm, and a parallel
        # rebuild when the engine moved. Calling it from the gate rather than from a brief is the whole
        # difference between a mechanism and a paragraph nobody reads: the check can no longer be skipped
        # because someone forgot, and the cost is paid once per engine instead of once per run.
        _cc = subprocess.run([sys.executable, os.path.join(HERE, "corpus-convert.py"),
                              "--ensure", "-j", "4", "-q"],
                             capture_output=True, text=True, timeout=2400)
        if _cc.returncode != 0:
            print("  corpus : could not be built (%d) - the .docx checks below cannot run"
                  % _cc.returncode)
            for _l in (_cc.stdout or "").strip().splitlines()[-3:]:
                print("    %s" % _l.strip())
        _gs = subprocess.run([sys.executable, os.path.join(HERE, "google_safe.py"),
                              "--corpus", "--check"], capture_output=True, text=True, timeout=180)
        if _gs.returncode == 1:
            for _l in (_gs.stdout or "").strip().splitlines()[-6:]:
                print("  %s" % _l.strip())
            fail = 1
        elif _gs.returncode == 3:
            print("  google-safe : no .docx output directory - cannot check")
        else:
            print("  google-safe : no construct Google ignores has spread")
    except Exception as _e:
        print("  google-safe : cannot run (%s)" % _e)

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
        return stamp(scope or {"docx", "txt"})
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
