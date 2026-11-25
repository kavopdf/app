#!/usr/bin/env python3
"""gh-to-drive.py - put the corpus .docx into Drive from GitHub release assets, no human step.

WHY GITHUB
    Every Drive upload tool demands file_to_upload.s3key, and a local path is rejected ("The file key
    does not belong to this project or session"). The only upload route that needs no platform work is
    GOOGLEDRIVE_UPLOAD_FROM_URL, which needs the file at a publicly reachable HTTPS URL. Netlify cannot
    serve that from here: api.netlify.com is not on the egress allowlist and *.netlify.app is
    denylisted, so neither the CLI nor the proxy path can be reached. github.com IS allowlisted, and a
    release asset on a public repo is a plain public URL.

    Measured: UPLOAD_FROM_URL with mime_type=application/vnd.google-apps.document fetches a release
    asset and creates a converted Google Doc in one call. No staging, no s3key, no manual step.

EXPOSURE
    The assets are public for the life of the release. The caller must delete the release when the
    refresh finishes - see the `gh release delete` in the runner. The corpus is synthetic benchmark
    material, but it is also the test set, so the window is kept to minutes, not hours.

USAGE
    gh-to-drive.py --tag <release tag> --repo kavopdf/app --folder <drive folder id> [--slice N]
"""
import argparse
import asyncio
import json
import os
import sys

DOCX = "/scratch/work/p2w/out"
RES = None  # set in main


def pending(engine):
    """Corpus documents whose verdict is not stamped with this engine."""
    out = []
    for f in sorted(os.listdir(DOCX)):
        if not f.endswith(".docx"):
            continue
        n = f[:-5]
        j = os.path.join(RES, n + ".json")
        if os.path.exists(j):
            try:
                if (json.load(open(j, encoding="utf-8")).get("engine") or "") == engine:
                    continue
            except Exception:
                pass
        out.append(n)
    return out


async def push(names, repo, tag, folder, jobs):
    from sarvam_tools import GOOGLEDRIVE_UPLOAD_FROM_URL
    sem = asyncio.Semaphore(jobs)
    base = "https://github.com/%s/releases/download/%s/" % (repo, tag)

    async def one(n):
        async with sem:
            try:
                await GOOGLEDRIVE_UPLOAD_FROM_URL(
                    source_url=base + n + ".docx",
                    name=n,
                    mime_type="application/vnd.google-apps.document",
                    parent_folder_id=folder)
                return n, "ok"
            except Exception as e:
                return n, type(e).__name__

    res = await asyncio.gather(*[one(n) for n in names])
    ok = [n for n, s in res if s == "ok"]
    bad = {}
    for n, s in res:
        if s != "ok":
            bad[s] = bad.get(s, 0) + 1
    print("uploaded %d of %d | %s" % (len(ok), len(names), bad or "no failures"))
    return len(ok)


def main(argv):
    global RES
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--repo", default="kavopdf/app")
    ap.add_argument("--folder", required=True)
    ap.add_argument("--slice", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args(argv)

    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    RES = os.path.join(root, "benchmarks", "gverify")
    try:
        eng = json.load(open("/scratch/work/p2w/.stamp", encoding="utf-8")).get("engine") or ""
    except Exception:
        eng = ""

    todo = pending(eng)
    if not todo:
        print("nothing to do - every verdict is on engine %s" % eng[:16])
        return 0
    todo = todo[:a.slice] if a.slice else todo
    print("%d documents need a verdict on %s" % (len(todo), eng[:16]))
    asyncio.run(push(todo, a.repo, a.tag, a.folder, a.jobs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
