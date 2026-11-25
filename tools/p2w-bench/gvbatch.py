#!/usr/bin/env python3
"""Score a slice of Google renders against their source PDFs and write verdicts.

verify_google.py takes <src.pdf> <google-render.pdf> --docx <docx> --json <out>. This walks a slice in
parallel, skips documents that already have a verdict stamped with THIS engine, and rewrites the json
with the engine hash so the store says which engine it describes.

    gvbatch.py --slice 24 --jobs 6 --renders /scratch/work/renders25
"""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CORPUS = "/scratch/work/p2w/corpus"
DOCX = "/scratch/work/p2w/out"
RES = os.path.join(ROOT, "benchmarks", "gverify")


def engine_now():
    try:
        return json.load(open("/scratch/work/p2w/.stamp", encoding="utf-8")).get("engine") or ""
    except Exception:
        return ""


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", type=int, default=12)
    ap.add_argument("--renders", required=True)
    ap.add_argument("--engine", default="")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args(argv)

    eng = a.engine or engine_now()
    names = sorted(f[:-4] for f in os.listdir(a.renders) if f.endswith(".pdf"))
    todo = []
    for n in names:
        if not (os.path.exists(os.path.join(CORPUS, n + ".pdf"))
                and os.path.exists(os.path.join(DOCX, n + ".docx"))):
            continue
        out = os.path.join(RES, n + ".json")
        if os.path.exists(out):
            try:
                if (json.load(open(out, encoding="utf-8")).get("engine") or "") == eng:
                    continue
            except Exception:
                pass
        todo.append(n)

    if not todo:
        print("ALL DONE - %d renders, every verdict is on engine %s" % (len(names), eng[:16]))
        return 0

    def score(n):
        src = os.path.join(CORPUS, n + ".pdf")
        dx = os.path.join(DOCX, n + ".docx")
        rp = os.path.join(a.renders, n + ".pdf")
        out = os.path.join(RES, n + ".json")
        try:
            subprocess.run([sys.executable, os.path.join(HERE, "verify_google.py"),
                            src, rp, "--docx", dx, "--json", out],
                           capture_output=True, text=True, timeout=240)
        except subprocess.TimeoutExpired:
            return 0
        if not os.path.exists(out):
            return 0
        try:
            d = json.load(open(out, encoding="utf-8"))
        except Exception:
            return 0
        d["engine"] = eng
        d["render"] = "google"
        json.dump(d, open(out, "w", encoding="utf-8"), indent=1)
        return 1

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        done = sum(ex.map(score, todo[:a.slice]))
    print("scored %d of %d attempted | %d todo remain"
          % (done, min(a.slice, len(todo)), max(0, len(todo) - a.slice)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
