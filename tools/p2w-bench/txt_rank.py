#!/usr/bin/env python3
"""txt_rank.py - score the .txt the way the .docx is scored, so the fixer can see it.

THE TXT WAS NEVER MEASURED. verify_txt.py has twelve named checks and its own docstring says why they
matter: "the pipeline measures the .docx path and nothing else... the .txt is never opened. So the
fixer cannot improve it: a defect it cannot see is a defect it cannot fix, and the .txt could break
outright without a single number moving." That was true when it was written and it stayed true -
RESULTS-TXT.jsonl does not exist, RANKING.csv has no txt column, and the fixer's prompt never mentions
the format.

This runs the twelve checks over every document and writes RANKING-TXT.csv, one row per document:

    document, applicable, passed, failed, abstained, failed_ids

A document meets the same 99% bar the .docx has when EVERY applicable check passes - a txt that fails
one of twelve is not 99% of a document, it is a document with a known defect. `abstained` is reported
separately and never counted as a pass.

    python3 tools/p2w-bench/txt_rank.py --limit 20
    python3 tools/p2w-bench/txt_rank.py --all
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
# THE TXT LIVES IN ITS OWN DIRECTORY. Nothing under tools/p2w-bench/txt/ is read by the .docx path,
# and nothing in the .docx path writes there, so a txt change cannot move a docx number by accident
# and a docx change cannot hide behind a txt score. The two formats share the ENGINE and nothing else.
TXT_DIR = os.path.join(HERE, "txt")
os.makedirs(TXT_DIR, exist_ok=True)
OUT = os.path.join(TXT_DIR, "RANKING-TXT.csv")
CORPUS = "/scratch/work/p2w/corpus"
TXT = "/scratch/work/p2w/out"


def docs():
    out = []
    if not os.path.isdir(CORPUS):
        return out
    for f in sorted(os.listdir(CORPUS)):
        if f.endswith(".pdf"):
            d = f[:-4]
            if os.path.exists(os.path.join(TXT, d + ".txt")):
                out.append(d)
    return out


def score(doc):
    pdf = os.path.join(CORPUS, doc + ".pdf")
    txt = os.path.join(TXT, doc + ".txt")
    j = os.path.join("/tmp", "txtcheck-%s.json" % doc[:40])
    try:
        r = subprocess.run(["python3", os.path.join(HERE, "verify_txt.py"), pdf, txt, "--json", j],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        return {"document": doc, "applicable": 0, "passed": 0, "failed": -1,
                "abstained": 0, "failed_ids": "error:%s" % type(e).__name__}
    # rc=1 MEANS CHECKS FAILED, NOT THAT THE RUNNER BROKE. verify_txt exits 1 whenever any check
    # fails, which is the normal way to report a defective txt - treating it as an error threw away
    # the result for exactly the documents that needed it. Only a missing JSON is an error.
    if not os.path.exists(j):
        return {"document": doc, "applicable": 0, "passed": 0, "failed": -1,
                "abstained": 0, "failed_ids": "error:rc%d" % r.returncode}
    try:
        data = json.load(open(j, encoding="utf-8"))
    except Exception:
        return {"document": doc, "applicable": 0, "passed": 0, "failed": -1,
                "abstained": 0, "failed_ids": "error:json"}
    # the checks dict is keyed by the check id; the entry itself carries no id field
    ch = data.get("checks") or {}
    judged = [(k, v) for k, v in ch.items() if v.get("applicable")]
    failed = [(k, v) for k, v in judged if not v.get("ok")]
    return {"document": doc,
            "applicable": len(judged),
            "passed": len(judged) - len(failed),
            "failed": len(failed),
            "abstained": len(ch) - len(judged),
            "failed_ids": " ".join(sorted(k for k, _ in failed)) or "-"}


def main(argv):
    ds = docs()
    if not ds:
        print("no documents found - is the corpus built?")
        return 2
    # SCORE WHAT IS NOT SCORED YET. Taking the first n every time re-scored the same documents and
    # left the rest of the corpus invisible, which is the shape of the bug that produced a day of
    # "0 of 213". --rescore forces everything; --all means the whole corpus either way.
    if os.path.exists(OUT) and "--rescore" not in argv:
        import csv as _c
        done = {r["document"] for r in _c.DictReader(open(OUT, encoding="utf-8"))}
        fresh = [d for d in ds if d not in done]
        if fresh:
            ds = fresh
    if "--all" not in argv:
        n = 20
        if "--limit" in argv:
            n = int(argv[argv.index("--limit") + 1])
        ds = ds[:n]
    rows = []
    for i, d in enumerate(ds):
        r = score(d)
        rows.append(r)
        if r["failed"] > 0:
            print("  %-40s %d/%d  FAIL %s" % (d[:40], r["passed"], r["applicable"], r["failed_ids"][:50]))
    # THE TXT RATCHET: NO DOCUMENT MAY GET WORSE.
    #
    # The docx has had one since the beginning - a change is kept only if no document regresses - and
    # the txt had none, because it had no scores. Now that it has scores it gets the same rule: a
    # document whose failing-check count goes UP between passes is a regression, and it is printed and
    # counted rather than quietly written over.
    old = {}
    if os.path.exists(OUT):
        import csv as _c
        for row in _c.DictReader(open(OUT, encoding="utf-8")):
            old[row["document"]] = row
    regressed = []
    for r in rows:
        prev = old.get(r["document"])
        if prev:
            try:
                was, now = int(prev.get("failed") or 0), r["failed"]
            except ValueError:
                was = now = 0
            if was >= 0 and now > was:
                regressed.append((r["document"], was, now))
        old[r["document"]] = {k: str(v) for k, v in r.items()}
    import csv as _c
    fields = ["document", "applicable", "passed", "failed", "abstained", "failed_ids"]
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = _c.DictWriter(fh, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for d in sorted(old):
            w.writerow({k: old[d].get(k, "") for k in fields})
    clean = [r for r in rows if r["failed"] == 0 and r["applicable"] > 0]
    print()
    print("  scored %d this pass | %d clean | %d with a failed check | %d errors"
          % (len(rows), len(clean),
             len([r for r in rows if r["failed"] > 0]),
             len([r for r in rows if r["failed"] < 0])))
    print("  wrote %s" % OUT)
    if regressed:
        print()
        print("  RATCHET: %d document(s) got WORSE in the txt:" % len(regressed))
        for d, was, now in regressed:
            print("    %-40s %d failing -> %d" % (d[:40], was, now))
        return 1
    print("  ratchet: no document got worse")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
