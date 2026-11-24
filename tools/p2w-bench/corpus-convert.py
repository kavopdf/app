#!/usr/bin/env python3
"""corpus-convert.py - build the converted corpus once per engine, in parallel, and keep it.

WHY THIS EXISTS.

Every engine change invalidates the converted corpus: the 213 `.docx` files are output of the engine, so a
one-line change to `DocxWriter` makes all of them stale. Rebuilding them took 38 minutes sequentially, and
that cost was paid inside a run whose whole budget is shorter than that. The result, measured on 24 Nov:
`regress.py --check` finishes in 12.6 seconds and prints

    google-safe : no .docx output directory - cannot check

so the commit gate that is supposed to stop a construct Google ignores from spreading could not run at all,
and 0 of the day's patches landed. The gate was never the bottleneck. Building its input was.

Two things fix that, and neither is a person doing it again:

  1. PARALLEL. 213 conversions at ~10.8 s each is 38 min in one process and about 10 min across four. The
     work is independent per document and needs no network - only a JVM and the local PDFs - so it is
     exactly the shape that parallelises cleanly.

  2. CACHED, KEYED ON THE ENGINE. The output is reusable until the engine changes, and the engine is
     identifiable from the commit that built it. So the cost is paid once per engine, not once per run, and
     a run that changes nothing starts with a warm corpus instead of rebuilding it.

USAGE

    python3 tools/p2w-bench/corpus-convert.py --ensure        # build only if the engine moved (what a run calls)
    python3 tools/p2w-bench/corpus-convert.py --force         # rebuild regardless
    python3 tools/p2w-bench/corpus-convert.py --ensure -j 6   # six workers
    python3 tools/p2w-bench/corpus-convert.py --status        # what is cached, and for which engine

Exit codes: 0 ready, 1 could not build, 3 no corpus PDFs found.

The stamp is a file, `CACHE/.stamp`, holding the engine commit and the document count. `--ensure` compares
it to the engine in the tree and to the PDFs on disk. A mismatch rebuilds; a match costs a stat call. The
stamp is written only after every conversion in the batch succeeded, so a half-built corpus can never be
mistaken for a whole one - which is the same rule the verdict tables follow.
"""
import argparse
import hashlib
import concurrent.futures as cf
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# google_safe.py looks here first, so the cache and the gate agree without either being told twice.
CACHE = "/scratch/work/p2w/out"
STAMP = os.path.join(os.path.dirname(CACHE), ".stamp")
# WHAT ENGINE THE DOCUMENTS ALREADY IN CACHE WERE CONVERTED BY. Without this a resumed build cannot tell
# a document converted on THIS engine from one left behind by the engine before it, and would skip the
# second kind as if it were the first - the cache equivalent of trusting a fossil.
PROGRESS = os.path.join(os.path.dirname(CACHE), ".progress.json")

# The build runs from tools/engine-verify and writes its classes to out/ there, so both the working
# directory and this classpath are relative to THAT, not to the repo root. Measured by finding
# ConvertAll.class: it is tools/engine-verify/out/ConvertAll.class, and the first version of this tool
# pointed at the repo root and failed with ClassNotFoundException on all 75 documents.
WORK = os.path.join(ROOT, "tools", "engine-verify")
DEFAULT_CP = "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"

PDF_DIRS = (
    # corpus-fetch.sh unpacks here, and every other tool in this directory reads it here
    # (gverify.py, stage.py, benchmarks/census.py). This tool alone still looked in CORP/, so a pod
    # that had fetched the corpus with the repo's own script reported "corpus PDFs : 0 (none found)"
    # and refused to build - the cache was full and the tool said COLD. Measured 24 Nov 09:40.
    "/scratch/work/p2w/corpus",
    "/scratch/work/CORP/pdf-to-word-test-corpus-v3/pdf-to-word-test-corpus-v3/pdfs",
    "/scratch/work/CORP/pdfs",
)


def pdf_dir():
    for d in PDF_DIRS:
        if os.path.isdir(d) and any(f.endswith(".pdf") for f in os.listdir(d)):
            return d
    return None


def engine_now():
    """The ENGINE SOURCES the corpus was built from, or 'unknown'.

    Was the git commit; see engine_sources() for why that was wrong.
    """
    src = engine_sources()
    if src:
        return src
    for f in ("ENGINE", ".engine"):
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            try:
                return open(p, encoding="utf-8").read().strip()[:40]
            except Exception:
                pass
    try:
        r = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=30)
        return (r.stdout or "").strip() or "unknown"
    except Exception:
        return "unknown"


def engine_sources():
    """A hash of the ENGINE SOURCES - the same quantity regress.py:engine_fingerprint() uses.

    WHY NOT THE COMMIT. This used to key the cache on `git rev-parse HEAD`, so EVERY commit moved the
    key: a commit that only adds a FINDINGS file, or a claim, or a report, made all 213 .docx stale and
    the next `--ensure` paid a 200 s rebuild for it. regress.py calls --ensure from inside the gate, so
    the gate then ran past the 300 s call limit and a run could not commit at all - the same
    "0 patches landed" failure the tool was written to fix, moved one step later. Measured 24 Nov
    15:03 slot: two findings-only commits, each forcing a full rebuild.

    The engine is the .java in app/src/main/java/com/kavopdf/app/engine. Nothing else can change a
    converted byte, so nothing else may invalidate the cache.
    """
    d = os.path.join(ROOT, "app", "src", "main", "java", "com", "kavopdf", "app", "engine")
    if not os.path.isdir(d):
        return None
    h = hashlib.sha256()
    for name in sorted(os.listdir(d)):
        if not name.endswith(".java"):
            continue
        h.update(name.encode())
        with open(os.path.join(d, name), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:16]


def java_bin():
    for c in (os.path.join(os.environ.get("JAVA_HOME", ""), "bin", "java"),
              "/scratch/work/jdk-17.0.21.1+2/bin/java",
              "/scratch/work/.p2w-jdk/jdk/bin/java"):
        if os.environ.get("JAVA_HOME") and c.startswith(os.environ["JAVA_HOME"]) and os.path.exists(c):
            return c
        if not os.environ.get("JAVA_HOME") and os.path.exists(c):
            return c
    return shutil.which("java")


def read_stamp():
    try:
        return json.load(open(STAMP, encoding="utf-8"))
    except Exception:
        return {}


def write_stamp(engine, count):
    os.makedirs(os.path.dirname(STAMP), exist_ok=True)
    json.dump({"engine": engine, "documents": count, "at": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(STAMP, "w", encoding="utf-8"), indent=1)


def have_docx():
    try:
        return len([f for f in os.listdir(CACHE) if f.endswith(".docx")])
    except Exception:
        return 0


def convert_one(args):
    """One document. Returns (name, ok, seconds, message). Independent, so it runs in any worker."""
    src, out, cp, java = args
    name = os.path.basename(src)
    t0 = time.time()
    try:
        # ConvertOne, not ConvertAll: ConvertAll takes a DIRECTORY of PDFs and refuses a single file
        # ("no pdfs in .../301_lab_report_panel.pdf"). Per-document conversion is what makes the work
        # splittable across workers, so this is the whole point of the tool.
        # ConvertAll takes a DIRECTORY and reuses one JVM for every file in it. ConvertOne spawns a JVM
        # per document, and 75 documents across 4 workers blew the whole 290 s call limit on start-up
        # alone. So the unit of work is a shard: a directory of symlinks handed to one ConvertAll.
        shard = "/scratch/work/.cc-shard-%s" % str(abs(hash(src)) % 100000)
        if os.path.isdir(shard):
            shutil.rmtree(shard, ignore_errors=True)
        os.makedirs(shard, exist_ok=True)
        os.symlink(src, os.path.join(shard, name))
        r = subprocess.run([java, "-cp", cp, "ConvertAll", shard, out],
                           cwd=WORK, capture_output=True, text=True, timeout=280)
        if r.returncode != 0:
            return (name, False, time.time() - t0,
                    (r.stdout or "")[-300:] + (r.stderr or "")[-300:])
        return (name, True, time.time() - t0, "")
    except subprocess.TimeoutExpired:
        return (name, False, time.time() - t0, "timed out after 300 s")
    except Exception as e:
        return (name, False, time.time() - t0, "%s: %s" % (type(e).__name__, e))


def _docx_ok(path):
    """Is this a document we may skip, or a corpse a killed worker left behind?

    A call that hits the 290 s limit kills the JVM mid-write, so the output name can exist while the
    file is truncated. "The name is on disk" is not evidence that the document was converted; a zip
    that opens and holds word/document.xml is.
    """
    try:
        if os.path.getsize(path) < 2048:
            return False
        import zipfile
        with zipfile.ZipFile(path) as z:
            return "word/document.xml" in z.namelist()
    except Exception:
        return False


def _read_progress():
    try:
        return json.load(open(PROGRESS, encoding="utf-8"))
    except Exception:
        return {}


def _write_progress(engine):
    try:
        os.makedirs(os.path.dirname(PROGRESS), exist_ok=True)
        json.dump({"engine": engine, "at": time.strftime("%Y-%m-%dT%H:%M:%S")},
                  open(PROGRESS, "w", encoding="utf-8"), indent=1)
    except Exception:
        pass


def convert_shard(args):
    """One JVM, many documents. Returns [(name, ok, seconds, message)].

    convert_one() gives every document its own JVM, which is right when the unit of work is a document
    and wrong when it is the corpus: 213 start-ups is minutes of the budget spent before a page is read.
    ConvertAll takes a directory and converts every PDF in it in one JVM, so the unit of work here is a
    shard of BATCH documents.
    """
    srcs, out, cp, java = args
    t0 = time.time()
    shard = "/scratch/work/.cc-shard-%s" % str(abs(hash(tuple(sorted(srcs)))) % 100000)
    try:
        if os.path.isdir(shard):
            shutil.rmtree(shard, ignore_errors=True)
        os.makedirs(shard, exist_ok=True)
        for src in srcs:
            os.symlink(src, os.path.join(shard, os.path.basename(src)))
        r = subprocess.run([java, "-cp", cp, "ConvertAll", shard, out],
                           cwd=WORK, capture_output=True, text=True, timeout=280)
        msg = ""
        if r.returncode != 0:
            msg = ((r.stdout or "")[-300:] + (r.stderr or "")[-300:]).strip()
        res = []
        for src in srcs:
            name = os.path.basename(src)
            docx = os.path.join(out, name[:-4] + ".docx")
            good = _docx_ok(docx)
            res.append((name, good, time.time() - t0,
                        "" if good else (msg or "no .docx written")))
        return res
    except subprocess.TimeoutExpired:
        return [(os.path.basename(s), False, time.time() - t0, "timed out after 280 s") for s in srcs]
    except Exception as e:
        return [(os.path.basename(s), False, time.time() - t0,
                 "%s: %s" % (type(e).__name__, e)) for s in srcs]
    finally:
        shutil.rmtree(shard, ignore_errors=True)


def build(jobs, quiet=False, batch=10):
    d = pdf_dir()
    if not d:
        print("  no corpus PDFs found in %s" % ", ".join(PDF_DIRS))
        return 3
    java = java_bin()
    if not java:
        print("  no java on PATH and no JAVA_HOME - the engine cannot be run")
        return 1
    pdfs = sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".pdf"))
    os.makedirs(CACHE, exist_ok=True)
    # A stale stamp must never outlive the rebuild that replaces it: if the build dies half way, the next
    # --ensure has to see "no stamp" and rebuild rather than trust a corpus with missing documents.
    try:
        os.remove(STAMP)
    except Exception:
        pass

    # RESUME, BECAUSE A BUILD IS LONGER THAN ONE CALL. 213 documents at ~10.8 s is 19 minutes on this
    # two-core pod and a bash call is 290 s, so a build that starts from zero can never finish inside a
    # run: it was rebuilt from zero every time and every run ended with the "corpus could not be built"
    # the gate refuses. A document already converted by THIS engine is not work, it is the progress the
    # last call made. Anything left by a different engine is stale and is converted again.
    eng = engine_now()
    prog = _read_progress()
    if prog.get("engine") != eng:
        todo = list(pdfs)
    else:
        todo = [p for p in pdfs
                if not _docx_ok(os.path.join(CACHE, os.path.basename(p)[:-4] + ".docx"))]
    _write_progress(eng)
    done = len(pdfs) - len(todo)
    if done and not quiet:
        print("    %d/%d already converted on engine %s - resuming" % (done, len(pdfs), eng))
    if not todo:
        write_stamp(eng, len(pdfs))
        if not quiet:
            print("  %d converted, nothing left to do - cached for engine %s" % (len(pdfs), eng))
        return 0

    t0 = time.time()
    # ONE JVM PER SHARD, AND ONE SHARD AT A TIME PER WORKER. ConvertAll converts every PDF it is handed
    # in a single JVM, so the unit of work is a shard of `batch` documents: 213 JVM start-ups cost more
    # than the conversions they precede.
    n = max(1, min(jobs, len(todo)))
    shards = [[] for _ in range(n)]
    for i, p in enumerate(todo):
        shards[i % n].append(p)
    work = []
    for sh in shards:
        for i in range(0, len(sh), max(1, batch)):
            work.append((sh[i:i + max(1, batch)], CACHE, DEFAULT_CP, java))
    ok, bad = done, 0
    failures = []
    with cf.ProcessPoolExecutor(max_workers=n) as ex:
        for res in ex.map(convert_shard, work, chunksize=1):
            for name, good, secs, msg in res:
                if good:
                    ok += 1
                else:
                    bad += 1
                    failures.append((name, msg))
            if not quiet:
                print("    %d/%d  %.0f s elapsed" % (ok + bad, len(pdfs), time.time() - t0))

    took = time.time() - t0
    if bad:
        print("  %d converted, %d FAILED in %.1f min (%d workers)" % (ok, bad, took / 60, jobs))
        for n, m in failures[:5]:
            print("    %s : %s" % (n, m.strip().splitlines()[-1][:150] if m.strip() else "no message"))
        print("  no stamp written - a partial corpus must not look like a whole one")
        return 1

    write_stamp(eng, ok)
    print("  %d converted in %.1f min (%d workers) - cached for engine %s"
          % (ok, took / 60, jobs, eng))
    return 0


def ensure(jobs, quiet=False):
    """Build only if the engine moved or the cache is short. The fast path is two stats and a listdir."""
    d = pdf_dir()
    if not d:
        print("  no corpus PDFs found")
        return 3
    want = len([f for f in os.listdir(d) if f.endswith(".pdf")])
    eng = engine_now()
    st = read_stamp()
    have = have_docx()
    if st.get("engine") == eng and st.get("documents") == want and have == want:
        if not quiet:
            print("  corpus is warm: %d documents, engine %s - nothing to rebuild" % (have, eng))
        return 0
    why = []
    if st.get("engine") != eng:
        why.append("engine is %s, the cache is %s" % (eng, st.get("engine") or "unstamped"))
    if st.get("documents") != want:
        why.append("the corpus has %d PDFs, the cache says %s" % (want, st.get("documents")))
    if have != want:
        why.append("%d .docx on disk for %d PDFs" % (have, want))
    print("  rebuilding: %s" % "; ".join(why))
    return build(jobs, quiet)


def status():
    d = pdf_dir()
    want = len([f for f in os.listdir(d) if f.endswith(".pdf")]) if d else 0
    st = read_stamp()
    have = have_docx()
    print("  corpus PDFs : %d%s" % (want, "" if d else "  (none found)"))
    print("  .docx cached: %d  in %s" % (have, CACHE))
    print("  engine      : %s" % engine_now())
    print("  stamp       : %s" % (json.dumps(st) if st else "none"))
    warm = st.get("engine") == engine_now() and st.get("documents") == want and have == want
    print("  state       : %s" % ("WARM - a run can gate immediately" if warm
                                  else "COLD - the next --ensure continues from what is on disk, it does not start over"))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--ensure", action="store_true", help="build only if the engine moved")
    ap.add_argument("--force", action="store_true", help="rebuild regardless")
    ap.add_argument("--status", action="store_true", help="what is cached, and for which engine")
    ap.add_argument("-j", "--jobs", type=int, default=4, help="parallel workers (default 4)")
    ap.add_argument("-q", "--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.status:
        return status()
    if a.force:
        return build(a.jobs, a.quiet)
    if a.ensure:
        return ensure(a.jobs, a.quiet)
    print(__doc__.strip().split("\n\n")[0])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
