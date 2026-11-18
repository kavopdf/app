#!/usr/bin/env python3
"""step.py - everything mechanical, in one call, so the run spends its turns on the work.

WHY THIS EXISTS. A fixer run was measured making three or four tool calls and then stopping -
claim, heartbeat, evidence commit - while every one of those tools ran in under a second. Eight
separate calls to get from "the slot is free" to "the engine is built and I know what to do" is
seven more chances to stop, and the run never got as far as an attempt.

So the mechanical part is one script. It claims the slot, reads the handoff and the pending list,
rotates housekeeping, builds the engine, and prints a SHORT brief - the class, the carry-over, the
engine hash, and the exact commands to run next. One call instead of eight.

    python3 tools/p2w-bench/step.py            claim, read, build, print the brief
    python3 tools/p2w-bench/step.py --no-build skip the 60-second build
    python3 tools/p2w-bench/step.py --status   what it would do, without claiming

It prints at most about 3 KB. The run does not need to read FIXER-BRIEF.md to start: the brief is
for the step it is on, and this tells it which step that is.

Exit 0 means the slot is yours and the engine is built. Exit 1 means not your turn or the slot is
taken - the reason is printed.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def sh(cmd, timeout=290):
    try:
        r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return 1, str(e)


def py(script, *args):
    return sh("python3 tools/p2w-bench/%s %s" % (script, " ".join(args)))


def by_all_open():
    path = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")
    by = {}
    try:
        for line in open(path, encoding="utf-8"):
            if not line.startswith("| "):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 8 or cells[6] != "OPEN":
                continue
            by.setdefault(cells[2], []).append(cells[1].strip("`"))
    except Exception:
        return {}
    return by


def biggest_open_class():
    """The OPEN class to take next, smallest first, and its documents.

    SMALLEST FIRST IS DELIBERATE. A screen costs a few minutes whatever the class size, because
    soffice needs about eighty seconds to start either way. So the small classes are where a class
    can actually be closed inside one run: single-element-far-out (1 document),
    partly-lost-and-displaced (7), partly-lost (11) and partly-displaced (12) are 31 of the 92 OPEN
    documents between them. Taking the thirty-document class first spends a run on one class that
    cannot close; taking the four small ones closes four classes and shrinks the round.
    """
    import re as _re
    path = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")
    by = {}
    try:
        for line in open(path, encoding="utf-8"):
            if not line.startswith("| "):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 8 or cells[6] != "OPEN":
                continue
            by.setdefault(cells[2], []).append(cells[1].strip("`"))
    except Exception:
        return "", []
    if not by:
        return "", []
    cls = min(by, key=lambda k: (len(by[k]), k))
    return cls, by[cls]


def engine_hash():
    rc, out = sh("git log -1 --format=%h -- app/src/main/java/com/kavopdf/app/engine/")
    return out.strip().split("\n")[0] if rc == 0 and out.strip() else "unknown"


def refresh_clone():
    """Start the slot on origin's tip, not on the commit the pod happened to clone.

    THE SLOT CLONES ONCE AND ORIGIN KEEPS MOVING. Five crons fire an hour; a slot that clones
    at 14:21 and commits at 14:55 writes whole files, and every file it read at 14:21 is a
    version of the tree that no longer exists. Measured 17 Nov 14:5x: a run read DocxWriter at
    9f7a094, another slot committed a 218-line engine fix at cf2f9c6, and the first run's
    commit - built from the stale file - silently reverted it. Nothing failed; the commit
    succeeded; the fix was gone.

    So fetch before the work, not after. The tree is clean at slot start by construction (the
    pod cloned it), so a fast-forward is safe here and only here.
    """
    rc, _ = sh("git fetch -q --depth 1 origin main", timeout=90)
    if rc != 0:
        return "fetch failed - working on %s, re-read every file before you commit" % _head()
    rc, cur = sh("git rev-parse HEAD")
    rc2, tip = sh("git rev-parse origin/main")
    cur, tip = cur.strip(), tip.strip()
    if not cur or not tip or cur == tip:
        return "up to date (%s)" % (cur[:7] or "?")
    rc, out = sh("git merge --ff-only -q origin/main", timeout=90)
    if rc != 0:
        return "BEHIND origin and could not fast-forward: %s -> %s. Re-read every file before you commit." % (cur[:7], tip[:7])
    return "refreshed %s -> %s" % (cur[:7], tip[:7])


def _head():
    rc, out = sh("git rev-parse --short HEAD")
    return out.strip() or "unknown"


def main(argv):
    if "--status" in argv:
        rc, out = py("round.py", "--phase")
        print(out.strip().split("\n")[-1])
        rc, out = py("pending.py")
        print(out.strip()[:1200])
        return 0

    # 0. origin's tip, before anything is read
    print("clone       : %s" % refresh_clone())

    # 1. whose turn
    rc, out = py("round.py", "--phase")
    if "fix" not in out:
        print("not my turn - phase is %s" % out.strip().split("\n")[-1])
        return 1

    # 2. claim
    rc, out = py("round.py", "--claim-fixer")
    if rc != 0:
        print("previous fixer run still active")
        print(out.strip()[:300])
        return 1

    # 2b. remember which engine this run started on
    #
    # The release guard compares this against the engine at the end. A run that commits an engine
    # change outside a kept attempt is never checked by the ratchet - the ratchet measures what an
    # attempt says it kept - so the change ships unmeasured and the corpus drifts away from the
    # baseline without anything reporting it. That is exactly what happened on 17 Nov: a run
    # recorded '1 attempt, 0 kept' and committed a folio rule that regressed seventy documents.
    try:
        import json as _j
        _rp = os.path.join(ROOT, "tools", "p2w-bench", "ROUND.json")
        _d = _j.load(open(_rp, encoding="utf-8"))
        _d["fixer_engine_at_claim"] = engine_hash()
        _j.dump(_d, open(_rp, "w", encoding="utf-8"), indent=1)
    except Exception:
        pass

    # 3. say we are alive, in the same breath
    py("round.py", "--heartbeat", "--doing", '"claimed, gathering work"')

    # 4. housekeeping, then the two reads that decide the work
    py("archive.py")
    rc_h, handoff = py("handoff.py", "--show")
    rc_p, pending = py("pending.py")
    rc_g, gaps = py("gaps.py", "--last")

    # 5. build
    built = "skipped"
    if "--no-build" not in argv:
        rc_b, bout = sh("bash tools/p2w-bench/build-engine.sh", timeout=200)
        built = "ok" if rc_b == 0 else "FAILED"

    # 6. a short brief, not the whole world
    L = []
    L.append("=== YOUR TURN - the slot is yours ===")
    L.append("")
    L.append("engine      : %s" % engine_hash())
    L.append("build       : %s" % built)
    L.append("")
    L.append("--- WHAT IS PENDING (this is the work) ---")
    p = pending.strip()
    L.append(p[:1400] if p else "(nothing pending - take the class with the most documents)")
    L.append("")
    g = gaps.strip()
    if "BETWEEN RUNS" in g:
        L.append("--- THE PIPELINE WAS DOWN ---")
        L.append(g[g.index("BETWEEN RUNS"):][:400])
        L.append("")
    L.append("--- WHAT THE LAST RUN SAID ---")
    h = handoff.strip()
    L.append(h[:900] if h else "(no handoff)")
    L.append("")
    # 6b. NAME THE CLASS. A run that has to go and find the biggest OPEN class spends a turn on a
    # table lookup it could have been handed, and a run that reads the whole FIXER-BRIEF to find out
    # what to do spends many - the brief itself records that "a run that read it whole produced
    # sixteen silent minutes and no attempt". So the class, its documents and the exact command are
    # printed here and the run starts working instead of looking things up.
    cls, docs = biggest_open_class()
    L.append("--- WORK ON THIS ---")
    if cls:
        L.append("class       : %s" % cls)
        L.append("documents   : %d  %s" % (len(docs), ", ".join(docs[:6]) + (" ..." if len(docs) > 6 else "")))
        L.append("")
        L.append("  SCREEN IT FIRST - minutes, not forty:")
        L.append("     python3 tools/p2w-bench/screen.py --class \"%s\"" % cls)
        _ladder = sorted(by_all_open().items(), key=lambda kv: (len(kv[1]), kv[0]))
        L.append("  open classes, smallest first: " +
                 ", ".join("%s (%d)" % (k, len(v)) for k, v in _ladder[:5]))
        L.append("  SCREEN FAIL -> revert, next idea. PARTIAL -> run it again. SCREEN PASS -> then:")
        L.append("     python3 tools/p2w-bench/attempt.py --class \"%s\" --moved N --total M --reason \"...\"" % cls)
    else:
        L.append("(no OPEN class - check DEFECT-CLASSES.md, or close the round)")
    L.append("")
    L.append("--- NEXT, IN ORDER ---")
    L.append("  1. do NOT read FIXER-BRIEF.md end to end. This message is your brief.")
    L.append("     Open only the one section you need, if you need one.")
    L.append("  2. make the change; build again if you touched the engine")
    L.append("  3. screen.py --class \"<cls>\"   then   attempt.py --class \"<cls>\" --moved N --total M --reason \"...\"")
    L.append("  4. handoff.py --context \"...\" --next \"...\"; round.py --release-fixer")
    L.append("  5. commit; chain.py --after-release")
    L.append("")
    L.append("Every tool writes a beacon. Keep calling tools.")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
