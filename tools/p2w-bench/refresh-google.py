#!/usr/bin/env python3
"""refresh-google.py - the whole Google loop in one command, with no human step.

WHY THIS EXISTS
    The verdicts must describe the engine on disk or nothing can be measured. Before this, refreshing
    them needed someone to put .docx into Drive, which is why the store went stale and 218 attempts
    produced no visible improvement.

WHAT IT DOES
    1. finds the .docx for every corpus document in the Drive folder
    2. copies each one with mimeType=google-apps.document, which is how Drive converts a .docx into a
       Google Doc - measured, and the reason the whole loop is possible without an upload
    3. exports each converted doc as PDF, which is Google's render
    4. scores source PDF against that render and stamps the verdict with the engine hash

    Steps 2-4 need no human. Step 1 needs the .docx to already be in the folder, and the ONLY routes a
    sandbox has for putting them there are:
        - the user drops a zip in Drive and extracts it (manual, once)
        - GOOGLEDRIVE_UPLOAD_FROM_URL with the .docx at a public URL (automatic, needs a public host)
    Everything else (CREATE_FILE, UPLOAD_FILE, RESUMABLE_UPLOAD) demands an `s3key` that only a
    platform-staged download produces, and a local path is rejected outright:
        "The file key does not belong to this project or session"

USAGE
    python3 refresh-google.py --folder <drive folder id> [--slice N] [--jobs N]
"""
import argparse
import asyncio
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
RENDERS = "/scratch/work/renders-live"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
DOC_MIME = "application/vnd.google-apps.document"


def engine_now():
    try:
        return json.load(open("/scratch/work/p2w/.stamp", encoding="utf-8")).get("engine") or ""
    except Exception:
        return ""


async def refresh(folder, slice_n, jobs):
    from sarvam_tools import (GOOGLEDRIVE_FIND_FILE, GOOGLEDRIVE_COPY_FILE_ADVANCED,
                              GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE)
    os.makedirs(RENDERS, exist_ok=True)
    eng = engine_now()
    names = sorted(f[:-5] for f in os.listdir(DOCX) if f.endswith(".docx"))

    # which documents still need a verdict on this engine
    todo = []
    for n in names:
        out = os.path.join(RES, n + ".json")
        if os.path.exists(out):
            try:
                if (json.load(open(out, encoding="utf-8")).get("engine") or "") == eng:
                    continue
            except Exception:
                pass
        todo.append(n)
    if not todo:
        print("nothing to do - every verdict is on engine %s" % eng[:16])
        return 0
    todo = todo[:slice_n] if slice_n else todo
    print("%d documents need a verdict on %s" % (len(todo), eng[:16]))

    sem = asyncio.Semaphore(jobs)

    async def one(n):
        async with sem:
            try:
                r = await GOOGLEDRIVE_FIND_FILE(
                    query="name = '%s.docx' and '%s' in parents" % (n, folder),
                    fields="files(id,name)")
            except Exception as e:
                return n, "find:" + type(e).__name__
        fs = (r or {}).get("files") or []
        if not fs:
            return n, "not-in-drive"
        async with sem:
            try:
                c = await GOOGLEDRIVE_COPY_FILE_ADVANCED(fileId=fs[0]["id"], name=n, mimeType=DOC_MIME)
            except Exception as e:
                return n, "convert:" + type(e).__name__
        did = (c or {}).get("id")
        if not did:
            return n, "no-id"
        async with sem:
            try:
                e = await GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=did, mimeType="application/pdf")
            except Exception as ex:
                return n, "export:" + type(ex).__name__
        arts = (e or {}).get("artifacts") or []
        if not arts:
            return n, "no-artifact"
        try:
            with open(arts[0]["workspace_path"], "rb") as f:
                data = f.read()
            with open(os.path.join(RENDERS, n + ".pdf"), "wb") as f:
                f.write(data)
        except Exception as ex:
            return n, "write:" + type(ex).__name__
        return n, "ok"

    res = await asyncio.gather(*[one(n) for n in todo])
    ok = [n for n, s in res if s == "ok"]
    bad = {}
    for n, s in res:
        if s != "ok":
            bad[s] = bad.get(s, 0) + 1
    print("rendered %d of %d | %s" % (len(ok), len(todo), bad or "no failures"))
    return len(ok)


def score(jobs):
    r = subprocess.run([sys.executable, os.path.join(HERE, "gvbatch.py"),
                        "--slice", "100000", "--jobs", str(jobs), "--renders", RENDERS],
                       text=True)
    return r.returncode


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--slice", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args(argv)
    n = asyncio.run(refresh(a.folder, a.slice, a.jobs))
    if n:
        score(a.jobs)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
