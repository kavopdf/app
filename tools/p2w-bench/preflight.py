#!/usr/bin/env python3
"""Can this pod do a fixer attempt at all? Answer in under a minute, before the slot is spent.

WHY THIS EXISTS. Measured 24 Nov, four slots in a row died on a wall that was already known:
  - --claim-fixer refused on a dirty tree            (19:59)
  - regress.py --check crashed in google_safe.py     (every run)
  - the corpus could not be built inside one call    (cold pods)
  - p2w.py --budget 170 was killed at 290 s          (the measurement)
Each was discovered AFTER the run had read the brief, chosen a class and started work. The wall was
the same every time; only the discovery was expensive.

This checks the four things a run cannot start without, in the order they fail, and prints one line
each. Exit 0 = go. Exit 1 = one or more are broken, named, and the run should fix that instead of
spending the slot on a class it cannot land.

Nothing here writes. It is safe to run first, every run.
"""
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CACHE = os.environ.get("P2W_OUT") or "/scratch/work/p2w/out"
STAMP = os.path.join(os.path.dirname(CACHE), ".stamp")


def sh(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout after %ds" % timeout
    except Exception as e:
        return 125, "", type(e).__name__


def java():
    j = shutil.which("java")
    if j:
        return True, j
    home = os.environ.get("JAVA_HOME")
    if home and os.path.exists(os.path.join(home, "bin", "java")):
        return True, os.path.join(home, "bin", "java")
    return False, "no java on PATH and no JAVA_HOME - run jdk-fetch.sh"


def corpus():
    n = 0
    try:
        n = len([f for f in os.listdir(CACHE) if f.endswith(".docx")])
    except OSError:
        return False, "no cache directory at %s - run corpus-slice.py" % CACHE
    st = {}
    try:
        st = json.load(open(STAMP, encoding="utf-8"))
    except Exception:
        pass
    if not st:
        return False, "%d .docx but no stamp - run corpus-slice.py (a cold pod needs two calls)" % n
    if st.get("documents") != n:
        return False, "stamp says %s documents, %d on disk" % (st.get("documents"), n)
    return True, "%d documents, engine %s" % (n, st.get("engine"))


def changed_list():
    p = os.path.join(ROOT, "benchmarks", "DOCX-CHANGED.json")
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return False, "no changed list - run corpus-changed.py --record after the build"
    try:
        if os.path.exists(STAMP) and os.path.getmtime(STAMP) > os.path.getmtime(p):
            return False, "the corpus is newer than the list - re-record or the filter skips real work"
    except OSError:
        pass
    return True, "%d of %d to measure (%d changed)" % (
        len(d.get("todo") or []), d.get("of") or 0, len(d.get("changed") or []))


def gate():
    # Cheap probe only: does google_safe import and run? A full regress is minutes, not seconds.
    rc, out, err = sh("python3 tools/p2w-bench/google_safe.py --corpus --check", timeout=180)
    if rc == 0:
        return True, "google-safe clean"
    if rc == 3:
        return False, "google-safe cannot see the corpus"
    tail = (err or out).strip().splitlines()[-1][:80] if (err or out).strip() else "no output"
    return False, "google-safe exited %d: %s" % (rc, tail)


CHECKS = [("java", java), ("corpus", corpus), ("changed list", changed_list), ("gate", gate)]


def main(argv):
    quiet = "-q" in argv
    t0 = time.time()
    bad = []
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, "check raised %s" % type(e).__name__
        if not ok:
            bad.append((name, detail))
        if not quiet or not ok:
            print("  %-13s %s  %s" % (name, "ok  " if ok else "FAIL", detail))
    if bad:
        print("")
        print("  NOT READY (%d) - fix these before choosing a class, or the slot is spent on a wall:"
              % len(bad))
        for name, detail in bad:
            print("    - %s: %s" % (name, detail))
        return 1
    if not quiet:
        print("")
        print("  READY in %.1f s" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
