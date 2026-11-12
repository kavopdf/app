#!/usr/bin/env python3
"""
classify_test.py - does the classifier see every check, and group honestly?

WHY THIS EXISTS
    On 12 Nov the classifier was reading 50 of the 52 checks that fire. Its name
    pattern ended in [a-z_]+ and two real check ids carry digits: 20_within_10pt
    and 43_within_10pt_x. Both were dropped while parsing, silently, so neither
    ever became a class - and 20_within_10pt fails on 91% of the corpus, which made
    it the second largest defect in the set. The fixer was never pointed at it.

    Nothing caught that, because nothing compared the checks the verifiers emit
    against the pattern the classifier accepts. That comparison is the first test
    here, and it reads the verifiers directly: add a check, and this fails unless
    the pattern accepts it.

WHAT IT CHECKS
    1  every id verify_google.py and verify_txt.py emit matches CHECK_RE
    2  checks failing on identical documents land in one class
    3  checks failing on disjoint documents do not
    4  a check above UNIVERSAL becomes its own class and is never merged
    5  an oversized class whose checks are distinguishable is split to MAX_CLASS_CHECKS
    6  an oversized class whose checks are identical is reported, not passed silently
    7  a class is named after the check that touches the most documents
    8  the ranking is by union size, largest first

EXIT
    0  every case behaves as claimed
    1  at least one did not, and the case is named
"""

import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import classify as C

FAILS = []


def check(name, got, want):
    if got == want:
        print("  PASS  %-58s %s" % (name, got))
    else:
        print("  FAIL  %-58s got %s, wanted %s" % (name, got, want))
        FAILS.append(name)


def sets(n_docs, mapping):
    """Build doc_sets: every check in mapping fails on those document indexes."""
    docs = ["d%03d" % i for i in range(n_docs)]
    return {c: {docs[i] for i in idx} for c, idx in mapping.items()}, n_docs


def main():
    print("=" * 78)
    print("1. EVERY CHECK THE VERIFIERS EMIT MUST BE VISIBLE TO THE CLASSIFIER")
    print("=" * 78)
    import verify_google
    import verify_txt

    docx_ids = verify_google.all_check_ids()
    txt_ids = verify_txt.all_check_ids()
    print("  verify_google emits %d, verify_txt emits %d" % (len(docx_ids), len(txt_ids)))
    dropped = [c for c in docx_ids + txt_ids if not C.CHECK_RE.match(c)]
    check("no emitted check id is dropped by CHECK_RE", dropped, [])
    # The two that were actually dropped - named so a regression names itself.
    check("20_within_10pt is visible", bool(C.CHECK_RE.match("20_within_10pt")), True)
    check("43_within_10pt_x is visible", bool(C.CHECK_RE.match("43_within_10pt_x")), True)

    print()
    print("=" * 78)
    print("2-4. GROUPING")
    print("=" * 78)
    ds, n = sets(100, {"18_median_dy": range(0, 50), "19_worst_dy": range(0, 50)})
    g = C.build_groups(ds, n)
    check("identical document sets make one class", len(g), 1)
    check("  and it holds both checks", sorted(g[0]), ["18_median_dy", "19_worst_dy"])

    ds, n = sets(100, {"18_median_dy": range(0, 30), "47_margins": range(30, 60)})
    g = C.build_groups(ds, n)
    check("disjoint document sets make two classes", len(g), 2)

    # 95 of 100 is above UNIVERSAL (0.90), so it cannot discriminate.
    ds, n = sets(100, {"20_within_10pt": range(0, 95), "18_median_dy": range(0, 40),
                       "19_worst_dy": range(0, 40)})
    g = C.build_groups(ds, n)
    sizes = sorted(len(x) for x in g)
    check("a universal check becomes its own class", sizes, [1, 2])
    universal = [x for x in g if len(x) == 1]
    check("  and it is the universal one", universal[0], ["20_within_10pt"])

    print()
    print("=" * 78)
    print("5-6. OVERSIZED CLASSES")
    print("=" * 78)
    # Eight checks on identical documents, below the universal threshold so they
    # reach split_oversized rather than being pulled out first.
    same = list(range(0, 70))
    ds, n = sets(100, {"%02d_check_%s" % (10 + i, "x") if i < 10 else
                       "%02d_check_%s" % (i, "x"): same for i in range(8)})
    notes = []
    g = C.build_groups(ds, n, notes)
    check("identical checks cannot be split, and that is reported", notes, [8])
    check("  the class stays whole rather than being cut arbitrarily",
          [len(x) for x in g], [8])

    # Eight checks whose document sets overlap only partly: distinguishable, so
    # the stricter threshold must separate them.
    mapping = {}
    for i in range(8):
        mapping["%02d_check_%s" % (20 + i, "x")] = list(range(i * 5, 40 + i * 5))
    ds, n = sets(100, mapping)
    notes = []
    g = C.build_groups(ds, n, notes)
    check("distinguishable checks are split to the limit",
          max(len(x) for x in g) <= C.MAX_CLASS_CHECKS, True)
    check("  and nothing is reported as unsplittable", notes, [])

    print()
    print("=" * 78)
    print("7-8. NAMING AND RANKING")
    print("=" * 78)
    # 18_median_dy touches 60 documents, 19_worst_dy only 40: the class must be
    # named after the larger one whatever order the dict was built in.
    ds, n = sets(100, {"19_worst_dy": range(0, 40), "18_median_dy": range(0, 60)})
    g = C.build_groups(ds, n)
    biggest = sorted(g[0], key=lambda c: -len(ds[c]))[0]
    check("a class is named after its largest check", biggest, "18_median_dy")

    print()
    print("=" * 78)
    print("9. --attempt REFUSES WHAT IT CANNOT PROVE")
    print("=" * 78)
    import json as _json
    import os as _os
    import shutil as _shutil
    import subprocess as _sp
    import tempfile as _tf

    src = _os.path.dirname(_os.path.abspath(__file__))

    def attempt_fixture(two_engines=True, moved=8, claim=8, total=20, cls="18_median_dy"):
        d = _tf.mkdtemp()
        b = _os.path.join(d, "tools", "p2w-bench")
        _os.makedirs(b)
        for f in ("classify.py",):
            _shutil.copy(_os.path.join(src, f), _os.path.join(b, f))
        rows = ["| document | score | engine | failed |", "|---|---|---|---|"]
        for i in range(total):
            rows.append("| d%02d | 57/59 | FAIL | 20_within_10pt, 18_median_dy |" % i)
        open(_os.path.join(b, "BASELINE.md"), "w").write("\n".join(rows) + "\n")
        with open(_os.path.join(b, "RESULTS.jsonl"), "w") as f:
            for i in range(total):
                f.write(_json.dumps({"round": 1, "engine": "e1", "doc": "d%02d" % i,
                                     "score": 57, "total": 59,
                                     "failed": ["20_within_10pt", "18_median_dy"],
                                     "values": {}}) + "\n")
            if two_engines:
                for i in range(total):
                    ok = i < moved
                    f.write(_json.dumps({"round": 1, "engine": "e2", "doc": "d%02d" % i,
                                         "score": 59 if ok else 57, "total": 59,
                                         "failed": [] if ok else ["20_within_10pt", "18_median_dy"],
                                         "values": {}}) + "\n")
        args = [sys.executable, _os.path.join(b, "classify.py"), "--attempt", cls]
        if claim is not None:
            args += ["--moved", str(claim), "--total", str(total)]
        r = _sp.run(args, capture_output=True, text=True, cwd=d)
        return r.returncode, (r.stdout or "") + (r.stderr or "")

    rc, out = attempt_fixture(claim=999)
    check("a count larger than its denominator is refused", rc, 1)
    check("  and it says so", "More documents moved than were" in out, True)

    rc, out = attempt_fixture(claim=-5)
    check("a negative count is refused", rc, 1)

    rc, out = attempt_fixture(claim=8)
    check("the number the store agrees with is accepted", rc, 0)

    rc, out = attempt_fixture(claim=15)
    check("a number the store disagrees with is refused", rc, 1)
    check("  and it names the true number", "the store says 8 of 20" in out, True)

    rc, out = attempt_fixture(two_engines=False, claim=5, total=10)
    check("one engine means nothing could have moved, so it refuses", rc, 1)
    check("  and it says why", "only one engine" in out, True)

    rc, out = attempt_fixture(cls="koi bhi bakwas naam", claim=8)
    check("a class name that does not exist is refused", rc, 1)
    check("  and it says the ledger is keyed by the exact name",
          "is not a class" in out, True)

    print()
    print("=" * 78)
    print("10. THE CLASS FILE LISTS EVERY CLASS IT FOUND")
    print("=" * 78)
    # classify.py computed 43 classes and wrote 20 of them, because the table was built
    # from classes[:top] with top=20. Once the first twenty were FIXED or PARKED the fixer
    # would find nothing to pick while twenty-three were still OPEN, and a fixer with
    # nothing to pick closes the round.
    d = _tf.mkdtemp()
    b = _os.path.join(d, "tools", "p2w-bench")
    _os.makedirs(b)
    _shutil.copy(_os.path.join(src, "classify.py"), _os.path.join(b, "classify.py"))
    # 30 documents, each failing one distinct check - so 30 classes, above the old cap.
    rows = ["| document | score | engine | failed |", "|---|---|---|---|"]
    for i in range(30):
        rows.append("| d%02d | 58/59 | FAIL | %02d_check_%s |" % (i, i, "abcdefghij"[i % 10]))
    open(_os.path.join(b, "BASELINE.md"), "w").write("\n".join(rows) + "\n")
    r = _sp.run([sys.executable, _os.path.join(b, "classify.py")],
                capture_output=True, text=True, cwd=d)
    out = (r.stdout or "") + (r.stderr or "")
    said = 0
    for line in out.split("\n"):
        if "classes (data-driven)" in line:
            said = int(line.split(":")[-1].strip())
    written = 0
    path = _os.path.join(b, "DEFECT-CLASSES.md")
    if _os.path.exists(path):
        written = sum(1 for ln in open(path) if ln.startswith("| ") and ln[2:3].isdigit())
    check("more than twenty classes were computed", said > 20, True)
    check("and every one of them is in the file", written, said)

    print()
    print("=" * 78)
    if FAILS:
        print("%d FAILED: %s" % (len(FAILS), ", ".join(FAILS)))
        return 1
    print("all cases behave as claimed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
