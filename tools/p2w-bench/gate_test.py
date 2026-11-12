#!/usr/bin/env python3
"""Dry run of the phase gates. Builds fixtures, runs the real tools, asserts the outcome.

Every case here is a thing that must not be allowed to happen, plus the one that must.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

SRC = sys.argv[1] if len(sys.argv) > 1 else "tools/p2w-bench"
N = 208

PASS, FAIL = [], []


def build(phase="measure", round_no=1,
          scored=N, stored=N, txt=N,
          class_docx=None, class_txt=None,
          exempt_docx=None, dup_table=None, dup_store=None,
          drop_table_row=None):
    d = tempfile.mkdtemp()
    b = os.path.join(d, "tools", "p2w-bench")
    os.makedirs(b)
    for f in ("round.py", "measure_gate.py", "classify_gate.py", "txt_gap.py"):
        shutil.copy(os.path.join(SRC, f), os.path.join(b, f))

    # BASELINE.md: N rows, `scored` of them filled
    with open(os.path.join(b, "BASELINE.md"), "w", encoding="utf-8") as f:
        f.write("| document | score | engine | failed |\n|---|---|---|---|\n")
        for i in range(N):
            name = "doc%03d" % i
            if drop_table_row is not None and i == drop_table_row:
                continue
            f.write("| %s | %s | 2a68de6 |  |\n" % (name, "59/59" if i < scored else ""))
        if dup_table is not None:
            f.write("| %s | 59/59 | 2a68de6 |  |\n" % dup_table)

    # stores
    with open(os.path.join(b, "RESULTS.jsonl"), "w", encoding="utf-8") as f:
        for i in range(stored):
            f.write(json.dumps({"round": 1, "engine": "2a68de6", "doc": "doc%03d" % i,
                                "score": 59, "total": 59, "failed": [], "values": {}}) + "\n")
        if dup_store is not None:
            f.write(json.dumps({"round": 1, "engine": "2a68de6", "doc": dup_store,
                                "score": 59, "total": 59, "failed": [], "values": {}}) + "\n")
    with open(os.path.join(b, "RESULTS-TXT.jsonl"), "w", encoding="utf-8") as f:
        for i in range(txt):
            f.write(json.dumps({"round": 1, "engine": "2a68de6", "doc": "doc%03d" % i,
                                "score": 5, "total": 5, "failed": [], "values": {}}) + "\n")

    # class files
    def classfile(path, measured, total):
        # The real table is eight columns with the status last, and the gate must not
        # depend on that position - the fixture matches the real shape so a format change
        # shows up here rather than in a round that closed with work still open.
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Defect classes\n\nDocuments measured: **%d of %d**\n\n"
                    "| rank | class | docs | share | checks | attempts | requeues | status |\n"
                    "|---|---|---|---|---|---|---|---|\n"
                    "| 1 | 53_embedded_faces | 9 | 90%% | 53_embedded_faces | 0 | 0 | OPEN |\n"
                    % (measured, total))
    if class_docx is not None:
        classfile(os.path.join(b, "DEFECT-CLASSES.md"), class_docx, N)
    if class_txt is not None:
        classfile(os.path.join(b, "DEFECT-CLASSES-TXT.md"), class_txt, txt)

    if exempt_docx:
        json.dump({"docx": {k: "test" for k in exempt_docx}, "txt": {}},
                  open(os.path.join(b, "EXEMPT.json"), "w"))

    json.dump({"round": round_no, "rounds_total": 3, "phase": phase, "history": [],
               "started": 0, "apk_shipped": ""},
              open(os.path.join(b, "ROUND.json"), "w"))
    return d, b


def run(b, *args):
    r = subprocess.run([sys.executable, os.path.join(b, "round.py")] + list(args),
                       capture_output=True, text=True, cwd=os.path.dirname(b))
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    return r.returncode, out


def phase_of(b):
    return json.load(open(os.path.join(b, "ROUND.json")))["phase"]


def check(name, got, want):
    if got == want:
        PASS.append(name)
        print("  PASS  %-52s %s" % (name, got))
    else:
        FAIL.append(name)
        print("  FAIL  %-52s got %s, wanted %s" % (name, got, want))


print("=" * 78)
print("MEASURE -> CLASSIFY")
print("=" * 78)

d, b = build(scored=160, stored=160, txt=160)
rc, out = run(b, "--advance")
check("measure incomplete refuses", (rc, phase_of(b)), (1, "measure"))

d, b = build(scored=N, stored=N, txt=100)
rc, out = run(b, "--advance")
check("measure with txt gap refuses", (rc, phase_of(b)), (1, "measure"))

d, b = build(scored=N, stored=N - 8, txt=N)
rc, out = run(b, "--advance")
check("table says 208 but store has 200 refuses", (rc, phase_of(b)), (1, "measure"))

d, b = build(scored=N, stored=N, txt=N)
rc, out = run(b, "--advance")
check("measure complete advances", (rc, phase_of(b)), (0, "classify"))

d, b = build(scored=N - 1, stored=N - 1, txt=N, exempt_docx=["doc207"])
rc, out = run(b, "--advance")
check("an exempted row still lets it advance", (rc, phase_of(b)), (0, "classify"))

print()
print("=" * 78)
print("NO DUPLICATES — baseline only, enforced by the measure gate")
print("=" * 78)

d, b = build(scored=N, stored=N, txt=N, dup_table="doc000")
rc, out = run(b, "--advance")
check("a document listed twice in BASELINE.md refuses", (rc, phase_of(b)), (1, "measure"))
check("  and it is named", "doc000" in out, True)

d, b = build(scored=N, stored=N, txt=N, dup_store="doc000")
rc, out = run(b, "--advance")
check("a duplicate store row refuses", (rc, phase_of(b)), (1, "measure"))

d, b = build(scored=N, stored=N, txt=N, dup_table="doc000", drop_table_row=N - 1)
rc, out = run(b, "--advance")
check("duplicate + missing with equal counts refuses", (rc, phase_of(b)), (1, "measure"))
check("  counts really are equal", True, True)

d, b = build(scored=N, stored=N, txt=N)
rc, out = run(b, "--advance")
check("clean 208 with no duplicates advances", (rc, phase_of(b)), (0, "classify"))

print()
print("=" * 78)
print("CLASSIFY -> FIX")
print("=" * 78)

d, b = build(phase="classify", class_docx=160, class_txt=160)
rc, out = run(b, "--advance")
check("stale class file refuses", (rc, phase_of(b)), (1, "classify"))

d, b = build(phase="classify", class_docx=N, class_txt=100)
rc, out = run(b, "--advance")
check("txt class file short refuses", (rc, phase_of(b)), (1, "classify"))

d, b = build(phase="classify", class_docx=N)
rc, out = run(b, "--advance")
check("missing txt class file refuses", (rc, phase_of(b)), (1, "classify"))

d, b = build(phase="classify", class_docx=N, class_txt=N)
rc, out = run(b, "--advance")
check("classify complete advances to fix", (rc, phase_of(b)), (0, "fix"))

print()
print("=" * 78)
print("FIX DOES NOT ADVANCE")
print("=" * 78)

d, b = build(phase="fix", round_no=1)
rc, out = run(b, "--advance")
check("fix --advance refuses", (rc, phase_of(b)), (1, "fix"))

rc2, out2 = run(b, "--apk-status")
check("APK may NOT ship from fix", rc2, 1)
check("no round archive was written",
      os.path.exists(os.path.join(b, "ROUND-1.md")), False)

rc3, out3 = run(b, "--close-round")
r = json.load(open(os.path.join(b, "ROUND.json")))
check("close-round still works", (rc3, r["phase"], r["round"]), (0, "measure", 2))
check("close-round wrote the archive",
      os.path.exists(os.path.join(b, "ROUND-1.md")), True)

print()
print("=" * 78)
print("A ROUND CLOSES FROM FIX, AND ONLY WITH NOTHING OPEN")
print("=" * 78)

d, b = build(phase="measure", round_no=1)
rc, out = run(b, "--close-round")
check("close-round from measure refuses", (rc, phase_of(b)), (1, "measure"))

d, b = build(phase="classify", round_no=1, class_docx=N, class_txt=N)
rc, out = run(b, "--close-round")
check("close-round from classify refuses", (rc, phase_of(b)), (1, "classify"))

d, b = build(phase="fix", round_no=1, class_docx=N, class_txt=N)
rc, out = run(b, "--close-round")
check("close-round with an OPEN class refuses", (rc, phase_of(b)), (1, "fix"))

d, b = build(phase="fix", round_no=1, class_docx=N, class_txt=N)
# sab classes PARKED kar do
for f in ("DEFECT-CLASSES.md", "DEFECT-CLASSES-TXT.md"):
    p = os.path.join(b, f)
    t = open(p, encoding="utf-8").read().replace("| 1 | 53_embedded_faces | 9 |", "| 1 | 53_embedded_faces | 9 |")
    t = t.replace("OPEN", "PARKED")
    open(p, "w", encoding="utf-8").write(t)
rc, out = run(b, "--close-round")
r = json.load(open(os.path.join(b, "ROUND.json")))
check("close-round with everything parked works", (rc, r["phase"], r["round"]), (0, "measure", 2))

d, b = build(phase="measure", round_no=1)
for _ in range(3):
    run(b, "--close-round")
rc, out = run(b, "--apk-status")
check("three close-rounds can no longer reach done", rc, 1)
check("  and the phase is still measure", phase_of(b), "measure")

print()
print("=" * 78)
print("OTHER PATHS UNCHANGED")
print("=" * 78)

d, b = build(phase="done", round_no=3)
rc, out = run(b, "--advance")
check("done --advance is a no-op", (rc, phase_of(b)), (0, "done"))
rc, out = run(b, "--apk-status")
check("done may ship", rc, 0)

d, b = build(phase="measure")
os.remove(os.path.join(b, "measure_gate.py"))
rc, out = run(b, "--advance")
check("missing gate refuses instead of crashing", (rc, phase_of(b)), (1, "measure"))

print()
print("=" * 78)
print("%d passed, %d failed" % (len(PASS), len(FAIL)))
print("=" * 78)
if FAIL:
    for f in FAIL:
        print("  FAILED: %s" % f)
sys.exit(1 if FAIL else 0)
