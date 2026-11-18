#!/usr/bin/env python3
"""repro.py - prove a measurement is reproducible, or say exactly what was not.

WHY THIS EXISTS. Every number this pipeline reports is a claim about a document, and a claim nobody
can reproduce is a claim nobody can check. Three things make a measurement unreproducible, and all
three have bitten this pipeline already:

  * the TOOLS. soffice 7.4 and soffice 24 lay a .docx out differently, and a score taken under one
    says nothing about the other. The same is true of the Java the engine runs on and the scipy that
    computes the distance transform - without scipy the fallback is forty times slower and the
    per-command budget kills the document mid-measurement, which is how 416_many_tiny_pages spent a
    day as "0.0".
  * the INPUTS. A corpus that changed is not the corpus the baseline was taken on.
  * the ORDER. A dict, a set or a directory listing iterated in arrival order produces a different
    file every run from identical data.

This records the first two as a fingerprint and tests the third by measuring the same document twice
and comparing the numbers exactly.

    python3 tools/p2w-bench/repro.py --fingerprint          # what produced these numbers
    python3 tools/p2w-bench/repro.py --prove <doc>          # measure it twice, compare
    python3 tools/p2w-bench/repro.py --prove-all --limit 5  # five documents, worst first
"""
import hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "PROVENANCE.json")
CORPUS = "/scratch/work/p2w/corpus"


def sh(cmd):
    try:
        r = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True, timeout=60)
        return ((r.stdout or "") + (r.stderr or "")).strip().split("\n")[0][:90]
    except Exception:
        return "unknown"


def versions():
    v = {
        "python": sh("python3 --version"),
        "soffice": sh("soffice --version 2>/dev/null | head -1"),
        "java": sh("java -version 2>&1 | head -1"),
        "os": sh("uname -sm"),
    }
    for mod in ("scipy", "numpy", "fitz", "PIL", "pymupdf"):
        try:
            m = __import__(mod)
            v[mod] = getattr(m, "__version__", "present")
        except Exception:
            v[mod] = "MISSING"
    return v


def engine():
    return subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%h"],
                          capture_output=True, text=True).stdout.strip()


def corpus_manifest():
    """One hash over every source PDF, so a changed corpus cannot look like a changed engine."""
    h = hashlib.sha256()
    n = 0
    try:
        for f in sorted(os.listdir(CORPUS)):
            if not f.endswith(".pdf"):
                continue
            p = os.path.join(CORPUS, f)
            h.update(f.encode())
            h.update(str(os.path.getsize(p)).encode())
            n += 1
    except Exception:
        return {"count": 0, "sha": "missing"}
    return {"count": n, "sha": h.hexdigest()[:16]}


def fingerprint():
    fp = {"engine": engine(), "tools": versions(), "corpus": corpus_manifest()}
    warn = []
    if fp["tools"].get("scipy") == "MISSING":
        warn.append("scipy is MISSING: the EDT falls back to a forty-times-slower path and "
                    "long documents are killed mid-measurement. Any score taken now is suspect.")
    if fp["tools"].get("java") in ("unknown", "") or "not found" in fp["tools"].get("java", ""):
        warn.append("java is MISSING: the engine cannot be built, so no .docx measurement is possible.")
    fp["warnings"] = warn
    json.dump(fp, open(OUT, "w", encoding="utf-8"), indent=1, sort_keys=True)
    print("  engine  : %s" % fp["engine"])
    for k, v in fp["tools"].items():
        print("  %-8s: %s" % (k, v))
    print("  corpus  : %d pdf, sha %s" % (fp["corpus"]["count"], fp["corpus"]["sha"]))
    for w in warn:
        print("  WARNING : %s" % w)
    print("  wrote %s" % OUT)
    return fp


def prove_txt(doc):
    """Measure one document's .txt twice and compare every number the check produced."""
    pdf = os.path.join(CORPUS, doc + ".pdf")
    txt = "/scratch/work/p2w/out/%s.txt" % doc
    if not (os.path.exists(pdf) and os.path.exists(txt)):
        return {"doc": doc, "verdict": "not-built"}
    runs = []
    for i in range(2):
        j = "/tmp/repro-%d.json" % i
        subprocess.run(["python3", os.path.join(HERE, "verify_txt.py"), pdf, txt, "--json", j],
                       capture_output=True, text=True, timeout=120)
        try:
            d = json.load(open(j, encoding="utf-8"))
        except Exception:
            return {"doc": doc, "verdict": "error"}
        # only the numbers: the timestamp and the temp paths differ by design
        runs.append({k: d.get(k) for k in ("passed", "applicable", "total", "abstained",
                                           "ok", "failed", "checks")})
    same = runs[0] == runs[1]
    return {"doc": doc, "verdict": "identical" if same else "DIFFERENT",
            "run1": runs[0].get("passed"), "run2": runs[1].get("passed"),
            "applicable": runs[0].get("applicable")}


def prove_report():
    """Run the report twice and compare the bytes. Identical input must give an identical file."""
    hashes, texts = [], []
    for i in range(2):
        r = subprocess.run(["python3", os.path.join(HERE, "report.py")],
                           capture_output=True, text=True, timeout=180)
        texts.append(r.stdout)
        hashes.append(hashlib.sha256(r.stdout.encode()).hexdigest()[:16])
    if hashes[0] == hashes[1]:
        print("  report: identical across two runs (%s)" % hashes[0])
        return 0
    print("  report: DIFFERENT across two runs (%s vs %s)" % (hashes[0], hashes[1]))
    a, b = texts[0].split("\n"), texts[1].split("\n")
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            print("  first difference, line %d:" % (i + 1))
            print("    run1: %s" % x[:100])
            print("    run2: %s" % y[:100])
            break
    return 1


def main(argv):
    if "--fingerprint" in argv or len(argv) < 2:
        fingerprint()
        return 0
    if "--prove-report" in argv:
        return prove_report()
    docs = []
    if "--prove" in argv:
        i = argv.index("--prove") + 1
        docs = [argv[i]] if i < len(argv) else []
    elif "--prove-all" in argv:
        import csv
        p = os.path.join(HERE, "txt", "RANKING-TXT.csv")
        rows = []
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding="utf-8")):
                try:
                    rows.append((r["document"], int(r.get("failed") or 0)))
                except ValueError:
                    pass
        rows.sort(key=lambda t: -t[1])
        n = 5
        if "--limit" in argv:
            n = int(argv[argv.index("--limit") + 1])
        docs = [d for d, _ in rows[:n]]
    if not docs:
        print("usage: repro.py --fingerprint | --prove <doc> | --prove-all [--limit N]")
        return 2

    print("  proving %d document(s): measure twice, compare every number" % len(docs))
    bad = 0
    for d in docs:
        r = prove_txt(d)
        mark = "OK " if r["verdict"] == "identical" else "!! "
        print("  %s%-40s %s" % (mark, d[:40], r["verdict"]))
        if r["verdict"] != "identical":
            bad += 1
    print()
    if bad:
        print("  NOT REPRODUCIBLE: %d of %d documents gave two different answers." % (bad, len(docs)))
        print("  A number that changes between two runs of the same input is not a measurement.")
        return 1
    print("  REPRODUCIBLE: all %d documents gave identical numbers on both runs." % len(docs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
