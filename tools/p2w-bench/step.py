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


def engine_hash():
    rc, out = sh("git log -1 --format=%h -- app/src/main/java/com/kavopdf/app/engine/")
    return out.strip().split("\n")[0] if rc == 0 and out.strip() else "unknown"


def main(argv):
    if "--status" in argv:
        rc, out = py("round.py", "--phase")
        print(out.strip().split("\n")[-1])
        rc, out = py("pending.py")
        print(out.strip()[:1200])
        return 0

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
    L.append("--- NEXT, IN ORDER ---")
    L.append("  1. read the section of tools/p2w-bench/FIXER-BRIEF.md that matches the pending item")
    L.append("  2. make the change; build again if you touched the engine")
    L.append("  3. python3 tools/p2w-bench/attempt.py --class \"<cls>\" --moved N --total M --reason \"...\"")
    L.append("  4. handoff.py --context \"...\" --next \"...\"; round.py --release-fixer")
    L.append("  5. commit; chain.py --after-release")
    L.append("")
    L.append("Every tool writes a beacon. Keep calling tools.")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
