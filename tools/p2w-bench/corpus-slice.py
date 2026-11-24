#!/usr/bin/env python3
"""corpus-slice.py - build the corpus cache in slices that each fit one 290 s call.

WHY THIS EXISTS
  corpus-convert.py --ensure builds all 213 documents in ONE call. Measured on this engine at
  11 s/document with 4 workers that is ~10 minutes, and the platform kills a call at 290 s. So the
  build dies half way, no stamp is written, and the NEXT call re-converts every document from
  scratch - including the ones already on disk. Every fixer run on a fresh pod therefore starts
  from a cold cache, cannot pass the pre-commit gate, and ends with an unlandable patch. That is
  the mechanical reason a slot lands nothing, and it is not the engine's fault.

  This driver converts ONLY the documents that have no .docx on disk yet, up to --budget seconds,
  and exits 0 with "N to go". Run it repeatedly until it says DONE; the last slice writes the
  stamp corpus-convert.py would have written, using the tool's own write_stamp(), so --ensure then
  reads WARM and regress.py --check gates immediately.

  Nothing is deleted. A document already converted is never re-converted.

USAGE
  python3 tools/p2w-bench/corpus-slice.py            # convert as many as fit in 240 s
  python3 tools/p2w-bench/corpus-slice.py --budget 200 -j 6
  python3 tools/p2w-bench/corpus-slice.py --status   # what is left, cost nothing

EXIT 0  more work may remain ("N to go") or the corpus is DONE and stamped
EXIT 1  a document failed to convert - it is named, and the stamp is NOT written
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import importlib.util

# The module name must be REGISTERED in sys.modules, not just executed: convert_one is shipped to
# the worker processes by reference, and a function whose __module__ is not importable raises
# "Can't pickle <function convert_one>: import of module 'cc' failed". Registering it under a real
# name makes the fork's inherited sys.modules resolve it.
_spec = importlib.util.spec_from_file_location("corpus_convert", os.path.join(HERE, "corpus-convert.py"))
cc = importlib.util.module_from_spec(_spec)
sys.modules["corpus_convert"] = cc
_spec.loader.exec_module(cc)


def missing():
    """Every document this build still has to convert, or None if there is no corpus.

    MEASURED 24 Nov, cold pod: this function used to require a STAMP for this engine before it would
    count a .docx on disk as done, and a stamp is written only when this function returns empty. On a
    cold pod that is a deadlock - every slice converted the same first 51 documents, printed
    "213 to go", and never wrote the stamp, so regress.py --check could never pass and NO commit could
    ever land. Six slices, 51 documents each, zero progress: the run reported it as "corpus could not
    be built".

    The stamp is the wrong instrument for resume, because the stamp is the END of the build and resume
    needs the MIDDLE. corpus-convert.build() already keeps that middle: the PROGRESS file names the
    engine a rebuild is for. Same engine in the progress file = a good .docx on disk is this build's
    progress and is not work. A different engine, or no progress file, = nothing on disk may be
    trusted, which is the original rule and stays.
    """
    d = cc.pdf_dir()
    if not d:
        return None
    _st = cc.read_stamp()
    _fresh = bool(_st) and _st.get('engine') == cc.engine_now()
    eng = cc.engine_now()
    # A .docx ON DISK IS NOT A .docx FROM THIS ENGINE. Skipping on existence alone is right on an
    # empty cache and wrong the moment the engine moves: the old bytes stay, the corpus becomes a mix
    # of two engines, and every measurement after it is against the wrong file.
    resuming = _fresh or cc._read_progress().get('engine') == eng
    if not _fresh:
        # Claim the build for this engine before the first conversion, so the NEXT slice can see the
        # progress this one makes. Same call build() makes, for the same reason.
        cc._write_progress(eng)
    out = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(".pdf"):
            continue
        stem = f[:-4]
        # _docx_ok, not os.path.exists: a call killed at 290 s leaves a truncated zip under the right
        # name, and "the name is on disk" is not evidence that the document was converted.
        if resuming and cc._docx_ok(os.path.join(cc.CACHE, stem + '.docx')):
            continue
        out.append(os.path.join(d, f))
    return out


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--budget", type=int, default=240, help="seconds of conversion this slice may use")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args(argv)

    d = cc.pdf_dir()
    if not d:
        print("  no corpus PDFs found - run corpus-fetch.sh first")
        return 1
    todo = missing()
    total = len([f for f in os.listdir(d) if f.endswith(".pdf")])
    have = total - len(todo)

    if a.status:
        print("  corpus PDFs : %d" % total)
        print("  converted   : %d" % have)
        print("  to go       : %d" % len(todo))
        st = cc.read_stamp()
        print("  stamp       : %s" % (st if st else "none"))
        return 0

    if not todo:
        cc.write_stamp(cc.engine_now(), total)
        print("  DONE - %d documents converted, stamp written for engine %s"
              % (total, cc.engine_now()))
        return 0

    java = cc.java_bin()
    if not java:
        print("  no java on PATH and no JAVA_HOME - run jdk-fetch.sh")
        return 1
    os.makedirs(cc.CACHE, exist_ok=True)

    # MEASURED 24 Nov: 68 documents in 300 s with 6 workers = 4.4 s/document of WALL time on this
    # pod. The first version divided the 11 s/document SINGLE-DOCUMENT cost by the worker count and
    # asked for 109 documents in a 200 s budget; the call was killed at 300 s having done 68. The
    # cost that matters is wall time per document at this worker count, and it is not linear.
    per_doc = 4.5
    n = max(1, int(a.budget / per_doc))
    batch = todo[:n]
    print("  %d to go, converting %d this slice (%d workers, %d s budget)"
          % (len(todo), len(batch), a.jobs, a.budget))

    t0 = time.time()
    work = [(p, cc.CACHE, cc.DEFAULT_CP, java) for p in batch]
    import concurrent.futures as cf
    ok = bad = 0
    failures = []
    with cf.ProcessPoolExecutor(max_workers=a.jobs) as ex:
        for name, good, secs, msg in ex.map(cc.convert_one, work,
                                            chunksize=max(1, len(batch) // a.jobs)):
            if good:
                ok += 1
            else:
                bad += 1
                failures.append((name, msg))
    took = time.time() - t0
    print("  %d converted, %d failed in %.0f s" % (ok, bad, took))
    for name, msg in failures[:5]:
        last = (msg or "").strip().splitlines()
        print("    %s : %s" % (name, last[-1][:160] if last else "no message"))
    if bad:
        print("  no stamp written - a partial corpus must not look like a whole one")
        return 1

    left = missing()
    if left:
        print("  %d to go - run this again" % len(left))
        return 0
    cc.write_stamp(cc.engine_now(), total)
    print("  DONE - %d documents converted, stamp written for engine %s"
          % (total, cc.engine_now()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
