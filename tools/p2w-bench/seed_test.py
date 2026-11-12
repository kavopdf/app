#!/usr/bin/env python3
"""
seed_test.py - does seed.py add exactly the missing rows and nothing else?

The failure it guards against is silent: a corpus document with no row in BASELINE.md is
never chosen by "the first 10 rows whose score is empty", so it is never measured, and no
gate notices because the table and the store agree with each other.

    python3 tools/p2w-bench/seed_test.py
"""

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, "seed.py")
FAILS = []


def check(name, got, want):
    ok = got == want
    print("  %s  %-56s %s" % ("PASS" if ok else "FAIL", name, got))
    if not ok:
        FAILS.append("%s: got %r want %r" % (name, got, want))


def fixture(rows, pdfs):
    d = tempfile.mkdtemp()
    b = os.path.join(d, "tools", "p2w-bench")
    os.makedirs(b)
    os.makedirs(os.path.join(d, "all"))
    shutil.copy(SEED, os.path.join(b, "seed.py"))
    lines = ["| document | score | verdict | failed |", "|---|---|---|---|"]
    for r in rows:
        lines.append("| %s | %s |  |  |" % (r, "59/59" if r.startswith("m") else ""))
    open(os.path.join(b, "BASELINE.md"), "w").write("\n".join(lines) + "\n")
    for p in pdfs:
        open(os.path.join(d, "all", p + ".pdf"), "w").write("x")
    return d, os.path.join(b, "BASELINE.md")


def run(d, *args):
    r = subprocess.run([sys.executable, os.path.join(d, "tools", "p2w-bench", "seed.py")]
                       + list(args), capture_output=True, text=True, cwd=d)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def rows_of(path):
    out = []
    for line in open(path, encoding="utf-8"):
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0].lower() != "document":
            out.append(cells)
    return out


def main():
    print("=" * 78)
    print("seed.py - a corpus document with no row is never measured")
    print("=" * 78)

    print("\n1. A MISSING DOCUMENT GETS A ROW")
    d, base = fixture(["m1", "m2"], ["m1", "m2", "600_new"])
    rc, out = run(d, "--corpus", "all")
    check("exits 0", rc, 0)
    check("it names the missing document", "600_new" in out, True)
    check("the row was added", len(rows_of(base)), 3)
    check("the new row has no score", rows_of(base)[-1][1], "")

    print("\n2. IT ADDS NOTHING WHEN NOTHING IS MISSING")
    rc, out = run(d, "--corpus", "all")
    check("exits 0", rc, 0)
    check("says so", "nothing to add" in out, True)
    check("still three rows", len(rows_of(base)), 3)

    print("\n3. IT NEVER TOUCHES A MEASURED ROW")
    d, base = fixture(["m1", "m2"], ["m1", "m2", "601_new", "602_new"])
    before = [r for r in rows_of(base) if r[0] == "m1"][0]
    run(d, "--corpus", "all")
    after = [r for r in rows_of(base) if r[0] == "m1"][0]
    check("a scored row is unchanged", after, before)
    check("both new rows arrived", len(rows_of(base)), 4)

    print("\n4. --dry-run CHANGES NOTHING")
    d, base = fixture(["m1"], ["m1", "603_new"])
    rc, out = run(d, "--corpus", "all", "--dry-run")
    check("exits 0", rc, 0)
    check("says it is a dry run", "dry run" in out, True)
    check("the file is untouched", len(rows_of(base)), 1)

    print("\n5. AN EMPTY CORPUS IS A FAILURE, NOT A SUCCESS")
    d, base = fixture(["m1"], [])
    rc, out = run(d, "--corpus", "all")
    check("exits 1", rc, 1)
    check("and says the download did not land", "no PDFs" in out, True)

    print("\n6. A MISSING CORPUS DIRECTORY IS A FAILURE")
    d, base = fixture(["m1"], ["m1"])
    rc, out = run(d, "--corpus", "nope")
    check("exits 1", rc, 1)

    print("\n7. THE TABLE STAYS CONTIGUOUS")
    d, base = fixture(["m1", "m2"], ["m1", "m2", "604_new"])
    run(d, "--corpus", "all")
    lines = open(base, encoding="utf-8").read().splitlines()
    table = [i for i, l in enumerate(lines) if l.startswith("|")]
    check("the table rows are adjacent", table, list(range(table[0], table[0] + len(table))))

    print()
    print("=" * 78)
    if FAILS:
        print("%d failed" % len(FAILS))
        for f in FAILS:
            print("   " + f)
        return 1
    print("all cases behave as claimed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
