#!/usr/bin/env python3
"""Falsification test for the debt-freeze in regress.py docx_regressions().

Four cases, each a table built by hand. The gate must say REFUSE where a document
got worse, and pass where the only movement is a debt document improving.

  A  clean at HEAD (at its baseline)      B  already in debt at HEAD      C  clean, baseline 0.00
"""
import csv, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import regress  # noqa: E402

BASE = {"A": 1.00, "B": 5.00, "C": 0.00}      # 15 Nov baseline
HEAD = {"A": 1.00, "B": 6.00, "C": 0.00}      # what the last commit measured: B is in debt


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "document", "share5"])
        for i, (d, v) in enumerate(sorted(rows.items()), 1):
            w.writerow([i, d, "%.2f" % v])


def run(cur):
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "cur.csv")
    write(p, cur)
    regress.RANK = p
    regress.RANK_BASE = os.path.join(tmp, "base.csv")
    write(regress.RANK_BASE, BASE)
    regress.previous_table = lambda path: dict(HEAD)      # git is not involved in a unit test
    regress.google_failed_committed = lambda: {}
    regress.google_failed_now = lambda: {}
    regress.exempt_docx = lambda: set()
    os.environ.pop("P2W_ACCEPT_WORSE", None)
    bad, err = regress.docx_regressions()
    return [b[0] for b in bad], err, regress._DEBT_N


CASES = [
    ("clean document moves up",      {"A": 2.00, "B": 6.00, "C": 0.00}, ["A"]),
    ("debt document moves up",       {"A": 1.00, "B": 7.00, "C": 0.00}, ["B"]),
    ("debt document improves",       {"A": 1.00, "B": 5.50, "C": 0.00}, []),
    ("table unchanged from HEAD",    {"A": 1.00, "B": 6.00, "C": 0.00}, []),
    ("clean doc at baseline, 0.00 -> 0.01", {"A": 1.00, "B": 6.00, "C": 0.01}, ["C"]),
    ("debt paid off completely",     {"A": 1.00, "B": 5.00, "C": 0.00}, []),
]

fail = 0
for name, cur, want in CASES:
    got, err, debt = run(cur)
    ok = sorted(got) == sorted(want)
    fail += 0 if ok else 1
    print("%-40s %s  got %s want %s  (debt at HEAD %d) %s"
          % (name, "PASS" if ok else "FAIL", got or "-", want or "-", debt, err or ""))

print()
print("debt-freeze falsification: %d of %d" % (len(CASES) - fail, len(CASES)))
sys.exit(1 if fail else 0)
