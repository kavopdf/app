#!/usr/bin/env python3
"""Which .docx did the last engine change actually touch?

WHY THIS EXISTS. An attempt costs a 54-minute Google restamp of all 213 documents, so a fixer slot
affords one attempt. Measured in FINDINGS/, an engine change touches a fraction of the corpus, not
all of it: 2 of 213 documents on one patch, 8 of 72 on another, 18 of 19 on a third. Re-measuring the
ones the bytes did not change cannot produce a different verdict - the source PDF is the same, the
.docx is the same, the instrument is the same, only the clock moved.

So the expensive half is spent on documents whose answer is already known, and that is the mechanical
reason 218 attempts produced 0 kept changes: each one could afford a single try.

  --record   after a corpus build: hash every .docx, diff against the previous manifest, write the
             changed list, and rotate the manifest forward. Cheap - a stat and a sha256 per file.
  --list     print the documents whose bytes changed since the last --record, one per line. A
             never-measured document is always included: no verdict is not "unchanged".
  --status   what the manifest holds and how stale it is.

The manifest is a fact about bytes, not a policy. A patch that changes 213 documents reports 213 and
nothing is skipped; a patch that changes 2 reports 2.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CACHE = os.environ.get("P2W_OUT") or "/scratch/work/p2w/out"
MANIFEST = os.path.join(ROOT, "benchmarks", "DOCX-HASHES.json")
CHANGED = os.path.join(ROOT, "benchmarks", "DOCX-CHANGED.json")
GVERIFY = os.path.join(ROOT, "benchmarks", "gverify")


def _sha(path, blocks=1 << 20):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(blocks), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def _now():
    out = {}
    try:
        names = sorted(os.listdir(CACHE))
    except OSError:
        return out
    for n in names:
        if n.endswith(".docx"):
            out[n[:-5]] = _sha(os.path.join(CACHE, n))
    return out


def _load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return {}


def _measured(name):
    return os.path.exists(os.path.join(GVERIFY, name + ".json"))


def record(quiet=False):
    now = _now()
    if not now:
        print("  no .docx in %s - nothing to record" % CACHE)
        return 3
    before = _load(MANIFEST)
    prev = before.get("docx") or {}
    changed = [n for n, h in now.items() if prev.get(n) != h]
    # A document with no verdict is work even when its bytes did not move: it has never been asked.
    unmeasured = [n for n in now if not _measured(n)]
    todo = sorted(set(changed) | set(unmeasured))
    json.dump({"docx": now, "at": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(MANIFEST, "w", encoding="utf-8"), indent=0)
    json.dump({"changed": sorted(changed), "unmeasured": sorted(unmeasured),
               "todo": todo, "of": len(now), "at": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(CHANGED, "w", encoding="utf-8"), indent=0)
    if not quiet:
        print("  %d .docx recorded: %d changed since the last record, %d never measured, %d to measure"
              % (len(now), len(changed), len(unmeasured), len(todo)))
        if prev and not changed:
            print("  the engine did not move a single document - nothing needs re-measuring")
    return 0


def listing():
    d = _load(CHANGED)
    if not d:
        print("  no changed list - run --record after a corpus build", file=sys.stderr)
        return 3
    for n in d.get("todo") or []:
        print(n)
    return 0


def status():
    m, c = _load(MANIFEST), _load(CHANGED)
    print("  manifest     : %d documents, recorded %s" % (len(m.get("docx") or {}), m.get("at") or "never"))
    print("  changed list : %d of %d, at %s" % (len(c.get("todo") or []), c.get("of") or 0, c.get("at") or "never"))
    print("  changed      : %d" % len(c.get("changed") or []))
    print("  never measured: %d" % len(c.get("unmeasured") or []))
    return 0


def main(argv):
    if "--record" in argv:
        return record("-q" in argv)
    if "--list" in argv:
        return listing()
    if "--status" in argv:
        return status()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
