#!/usr/bin/env python3
"""archive.py - keep the repository to what the pipeline actually uses.

THE RULE THIS ENFORCES. A file that nothing reads is not evidence, it is weight. It costs a clone,
it costs a diff, it makes every search slower and every reviewer read further - and the one time it
matters, it is the file someone reads by mistake. This repository had 13 MB and roughly a third of it
was files no current tool opens: five RATCHET backups at 400 KB each, a 312 KB file with ARCHIVE
already in its name, a 146 KB position dump, a 127 KB DEFECTS.md, a 103 KB VISUAL-SCORE.md.

Nothing is deleted. Everything unused moves to archive/<date>/ and stays there, in git, readable.
The date directory is the record of when it stopped being live.

TWO KINDS OF ACCUMULATION, TWO TREATMENTS:

  dead     nothing reads it at all - move it to archive/<date>/ once
  growing  the pipeline DOES read it, but it is append-only and would grow for ever -
           keep the tail in place, move the rest to archive/<date>/<name>.head

A growing file is rotated, never truncated: the newest N lines stay where the tools expect them, and
everything older is preserved in the archive. RUN-LOG.md and TRACE.md are read by round.py and
handoff.py, so they cannot simply go - but neither can they grow without limit.

    python3 tools/p2w-bench/archive.py --report    what is unused, and how much
    python3 tools/p2w-bench/archive.py             do it (once per day; idempotent)

Exit 0 always: this is housekeeping, and housekeeping must never fail a run.
"""
import json, os, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))       # the repo root
ARCH = os.path.join(ROOT, "archive")
STATE = os.path.join(HERE, "ARCHIVE.json")

# Nothing in the current pipeline opens these. Verified by grepping every tool the crons run for an
# exact reference - not a substring, because "RANKING-BASELINE.csv" matches "BASELINE" and that
# false positive is exactly how a live file gets archived by mistake.
DEAD = [
    "tools/p2w-bench/RATCHET.json",
    "tools/p2w-bench/DEFECTS.md",
    "tools/p2w-bench/REMAINING-DEFECTS-ARCHIVE.md",
    "tools/p2w-bench/base208-position.json",
    "tools/p2w-bench/VISUAL-SCORE.md",
    "tools/p2w-bench/BATCH-LOG.md",
]
DEAD_GLOBS = [
    "tools/p2w-bench/RATCHET-2*.json",       # timestamped backups of a file nothing reads
    "tools/p2w-bench/RATCHET-TXT-2*.json",
]

# Read by the pipeline, but append-only. Keep this many lines; archive the rest.
GROWING = {
    "tools/p2w-bench/RUN-LOG.md":       400,
    "tools/p2w-bench/TRACE.md":         400,
    "tools/p2w-bench/TIMELINE.jsonl":  2000,
    "tools/p2w-bench/INCIDENTS.md":     300,
    "tools/p2w-bench/HYPOTHESES.md":    400,
}


def today():
    return time.strftime("%Y-%m-%d", time.gmtime(time.time() + 19800))


def load():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {"last": "", "moved": []}


def save(s):
    try:
        json.dump(s, open(STATE, "w", encoding="utf-8"), indent=1)
    except Exception:
        pass


def plan():
    import glob as g
    dead = [p for p in DEAD if os.path.exists(os.path.join(ROOT, p))]
    for pat in DEAD_GLOBS:
        dead += [os.path.relpath(x, ROOT) for x in g.glob(os.path.join(ROOT, pat))]
    grow = []
    for rel, keep in GROWING.items():
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        try:
            n = sum(1 for _ in open(p, encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if n > keep:
            grow.append((rel, keep, n))
    return dead, grow


def report():
    dead, grow = plan()
    dt = sum(os.path.getsize(os.path.join(ROOT, p)) for p in dead if os.path.exists(os.path.join(ROOT, p)))
    print("=== UNUSED IN THE REPOSITORY ===")
    print("")
    if not dead:
        print("  nothing unused")
    for p in dead:
        fp = os.path.join(ROOT, p)
        if os.path.exists(fp):
            print("  %7.0fK  %s" % (os.path.getsize(fp) / 1024, p))
    print("")
    print("  %d dead file(s), %.1f MB" % (len(dead), dt / 1024 / 1024))
    print("")
    print("=== GROWING (read by the pipeline, rotated not truncated) ===")
    print("")
    if not grow:
        print("  nothing over its keep-line")
    for rel, keep, n in grow:
        print("  %-40s %5d lines, keeps %d" % (rel, n, keep))
    return dead, grow


def run(force=False):
    s = load()
    if not force and s.get("last") == today():
        print("archive: already done today (%s)" % today())
        return
    dead, grow = plan()
    if not dead and not grow:
        s["last"] = today()
        save(s)
        print("archive: nothing to do")
        return

    d = os.path.join(ARCH, today())
    os.makedirs(d, exist_ok=True)
    moved = []
    for rel in dead:
        src = os.path.join(ROOT, rel)
        if not os.path.exists(src):
            continue
        dst = os.path.join(d, os.path.basename(rel))
        shutil.move(src, dst)
        moved.append(rel)
        print("  archived %-52s %7.0fK" % (rel, os.path.getsize(dst) / 1024))

    for rel, keep, n in grow:
        src = os.path.join(ROOT, rel)
        lines = open(src, encoding="utf-8", errors="replace").readlines()
        head, tail = lines[:-keep], lines[-keep:]
        dst = os.path.join(d, os.path.basename(rel) + ".head")
        open(dst, "w", encoding="utf-8").writelines(head)
        open(src, "w", encoding="utf-8").writelines(tail)
        moved.append(rel + " (rotated)")
        print("  rotated  %-52s %5d -> %d lines (kept), %d archived"
              % (rel, n, len(tail), len(head)))

    s["last"] = today()
    s["moved"] = (s.get("moved") or [])[-40:] + moved
    save(s)
    print("")
    print("archive: %d item(s) -> archive/%s/ - nothing deleted" % (len(moved), today()))


if __name__ == "__main__":
    if "--report" in sys.argv:
        report()
    else:
        run(force="--force" in sys.argv)
    sys.exit(0)
