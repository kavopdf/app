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



def tools():
    """Which of the fast-path tools exist, so a run knows what it has before it reads anything."""
    have, miss = [], []
    for n in ('corpus-slice.py', 'corpus-changed.py', 'preflight.py',
              'google_safe.py', 'classpick.py', 'pending.py',
              'diagnose.py', 'predict-outcome.py', 'google-needed.py'):
        (have if os.path.exists(os.path.join(HERE, n)) else miss).append(n)
    return (not miss), "%d present%s" % (len(have), (" - missing " + ", ".join(miss)) if miss else "")


def next_action():
    """One action, computed from the store, with its cost and its fallback.

    A run reads FIXER-BRIEF, LAST-MESSAGE, HANDOFF.next, pending.py, classpick and ATTEMPTS before it
    starts. That is a lot of reading to arrive at one decision, and today it arrived at a demoted
    class. This computes the decision instead and states the evidence beside it, so the run can
    disagree with a number in front of it rather than in the dark.

    Not a rule: it reads the ranking, the attempt ledger and the construct census and prints what
    they say. A run that has a better reason is free to take it, and the report will show both.
    """
    try:
        sys.path.insert(0, HERE)
        import classpick as cp
        rk = cp.ranking() or []
    except Exception as e:
        return "unknown", "classpick could not be read (%s)" % type(e).__name__
    if not rk:
        return "none", "the ranking is empty"
    top = str((rk[0][0] if isinstance(rk[0], (list, tuple)) else rk[0]) or '')
    docs = rk[0][1] if isinstance(rk[0], (list, tuple)) and len(rk[0]) > 1 else '?'
    # AN EXHAUSTED CLASS IS NOT A NEXT ACTION. classpick drops these from its ranking, but this read
    # ranking()[0] and said 18_displacement while the rotation's own top was 25_invisible_text.
    # The skip runs BEFORE att/moved are read, so the action and its evidence come from the same
    # class - building `why` first left the row naming one class and counting another, which is the
    # fault this whole week has been about.
    try:
        _ex = set(cp.exhausted())
        for _r in rk:
            _n = str((_r[0] if isinstance(_r, (list, tuple)) else _r) or '')
            if _n and _n not in _ex:
                top = _n
                docs = _r[1] if isinstance(_r, (list, tuple)) and len(_r) > 1 else docs
                break
    except Exception:
        pass
    att, moved = 0, 0
    try:
        at = json.load(open(os.path.join(HERE, 'ATTEMPTS.json'), encoding='utf-8'))
        h = (at.get(top) or {}).get('history') or []
        att = len(h)
        moved = sum(int(x.get('moved') or 0) for x in h)
    except Exception:
        pass
    why = "%s documents; %d attempt(s), %d moved" % (docs, att, moved)
    # 18_displacement measured 24 Nov: 20 attempts, 1 document moved. That is the same outcome as
    # zero and the rotation's rule is about improvement, not about a strict zero.
    if att >= 5 and moved <= 1:
        why += " - EXHAUSTED by the rotation's own rule; take the next class instead"
    try:
        pr = json.load(open(os.path.join(ROOT, 'benchmarks', 'GOOGLE-PREDICT.json'), encoding='utf-8'))
        n = len(pr.get('documents') or {})
        why += "; construct census covers %d documents" % n
    except Exception:
        why += "; no construct census - run google_safe.py --predict"
    return top, why

def verdicts():
    """Are the Google verdicts from THIS engine? If not, no fixer attempt can show an improvement."""
    import glob as _g
    try:
        cur = (json.load(open(STAMP, encoding='utf-8')).get('engine') or '')[:12]
    except Exception:
        return False, 'no stamp - the corpus engine is unknown'
    if not cur:
        return False, 'the stamp names no engine'
    seen = {}
    n = 0
    for f in _g.glob(os.path.join(ROOT, 'benchmarks', 'gverify', '*.json')):
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        if d.get('status') == 'page_count_refused':
            continue
        n += 1
        e = (d.get('engine') or 'none')[:12]
        seen[e] = seen.get(e, 0) + 1
    if not n:
        return False, 'no scored verdicts'
    same = seen.get(cur, 0)
    # A VERDICT FROM ANOTHER ENGINE DOES NOT DESCRIBE THIS CORPUS. Measured 24 Nov: 191 scored
    # verdicts, 187 on b7699196, 3 on 462353f, 1 on 5beb8b9d, and ZERO on the current b97d8172. So
    # "36 of 191 clean" describes a mix of three older engines, and a patch that helped could not
    # move the count - which is one mechanical reason 218 attempts produced 0 kept changes.
    if same == 0:
        top = max(seen.items(), key=lambda x: x[1])   # max by count; -x[1] returns the minimum
        return False, ('0 of %d verdicts are from this engine (%s); %d are on %s - re-measure before trusting any moved count' % (n, cur, top[1], top[0]))
    if same < n:
        return False, '%d of %d verdicts are from this engine (%s) - %d are stale' % (same, n, cur, n - same)
    return True, 'all %d verdicts are from engine %s' % (n, cur)


CHECKS = [("java", java), ("corpus", corpus), ("changed list", changed_list), ("gate", gate), ("verdicts", verdicts)]


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
        _ok, _det = tools()
        print("  %-13s %s  %s" % ("tools", "ok  " if _ok else "FAIL", _det))
        _act, _why = next_action()
        print("")
        print("  NEXT ACTION : %s" % _act)
        print("  because     : %s" % _why)
        print("  cheap signal: python3 tools/p2w-bench/google_safe.py --predict   (1 s, all documents)")
        print("  scoped meas : P2W_CHANGED_ONLY=1 p2w.py --budget N               (only what moved)")
        print("  coupled fix : P2W_ACCEPT_WORSE=doc1,doc2 regress.py --check      (named, net-positive)")
        print('  per document: python3 tools/p2w-bench/diagnose.py <name>        (why THIS document fails)')
        print('  before patch: python3 tools/p2w-bench/predict-outcome.py        (which construct buys clean docs)')
        print("")
        print("  READY in %.1f s" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
