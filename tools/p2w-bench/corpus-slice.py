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


def beat(doing):
    """Say the run is alive from inside a loop that can go minutes without printing anything.

    Two consecutive relay reports named this exact silence as the reason a watchdog released the claim:
    "pod-prep.sh's conversion step beats once and then goes quiet for four minutes at a time, four times
    over" and "Longest silence 38.7 min - from 08:35:19, after heartbeat before any claim: gverify:
    converting corpus slices". A conversion costs about 4.5 s a document here, so a beat every few
    documents is under half a minute of silence, well inside any window.

    round.py --heartbeat exists for precisely this: a run doing a long ratchet looked identical to a run
    that had died. Every failure is swallowed - a beat that cannot be written must never cost a
    conversion, and a conversion is the thing this process is for.
    """
    try:
        import subprocess
        subprocess.run([sys.executable, os.path.join(HERE, "round.py"), "--heartbeat", "--doing", doing],
                       timeout=10, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

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
    eng = cc.engine_now()
    # A .docx ON DISK IS NOT A .docx FROM THIS ENGINE, and until 27 Nov this function could only
    # approximate that with a build start time compared against mtime (see the comment below). It now
    # asks the file in front of it: cc.doc_fresh() requires a per-document key naming this engine
    # fingerprint and this pdf's content hash, so an engine move, a re-fetched PDF, a restored cache
    # or a clock change all answer correctly instead of relying on timestamps that agree by luck.
    #
    # THE PROGRESS FILE IS STILL READ, FOR ONE PURPOSE ONLY: adopting a cache that predates the keys.
    # cc.adopt_legacy() takes an unkeyed .docx in only when the OLD rule would have trusted it (the
    # progress file names this engine and the .docx is newer than that build's start), so a pod that
    # is already warm stays warm instead of paying a 16-minute rebuild for a bookkeeping change. Once
    # adopted, the trust is per document and permanent; a key that is present and stale is never
    # adopted, it is re-converted.
    _prog = cc._read_progress()
    _since = 0.0
    if _prog.get('engine') == eng and _prog.get('at'):
        try:
            _since = time.mktime(time.strptime(_prog['at'], "%Y-%m-%dT%H:%M:%S"))
        except Exception:
            _since = 0.0
    if _prog.get('engine') != eng:
        # Claim the build for this engine before the first conversion, so the log names the build these
        # slices belong to. Nothing decides anything from it any more; the keys do.
        cc._write_progress(eng)
    out = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(".pdf"):
            continue
        stem = f[:-4]
        src = os.path.join(d, f)
        if cc.doc_fresh(stem, src, eng):
            continue
        if cc.adopt_legacy(stem, src, eng, _prog, _since):
            continue
        out.append(src)
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
            _done = ok + bad + 1
            if _done % 6 == 0:
                beat("corpus-slice: %d of %d converted" % (_done, len(batch)))
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
