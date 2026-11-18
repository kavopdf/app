#!/usr/bin/env python3
"""pending.py - nothing new starts while anything is unfinished.

WHY THIS EXISTS

A fixer run can end with work half-done in four different ways, and each one leaves a different
kind of debt:

  * it wrote down what the next run should do, and the next run took a fresh class instead
  * it deployed a subagent, and the finding never arrived - or arrived and nobody read it
  * it kept a fix that was measured on thirty documents, and the other 180 were never checked
  * it hit a wall, wrote it in BLOCKERS.md, and the wall is still there

None of those is visible from the class list. A run that picks the biggest OPEN class looks
productive and leaves the debt to grow. So this tool answers one question - is anything
unfinished? - and the brief makes it a gate: while it lists something, that is the work.

    python3 tools/p2w-bench/pending.py            # human
    python3 tools/p2w-bench/pending.py --json     # machine

Exit 0  nothing pending - a new class may be taken
Exit 1  pending - the items printed are the work, in the order they should be done
"""
import json, os, sys, time

try:
    from beacon import beat
except Exception:
    def beat(*a, **k):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
HANDOFF  = os.path.join(HERE, "HANDOFF.json")
ATTEMPTS = os.path.join(HERE, "ATTEMPTS.json")
BLOCKERS = os.path.join(HERE, "BLOCKERS.md")
FINDINGS = os.path.join(HERE, "FINDINGS")

# An agent still 'running' after this long has almost certainly died with its run. The finding may
# still arrive - that is what the file is for - but the next run should not wait on it silently.
AGENT_SILENT_MIN = 40


def _load(p, default):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return default


def _findings():
    try:
        return [f for f in os.listdir(FINDINGS) if f.endswith(".md") and f != "README.md"]
    except Exception:
        return []


def _finding_landed(a):
    """Did this agent actually land a finding?

    AN AGENT IS NOT SILENT JUST BECAUSE TIME PASSED. This list called every agent older than the
    threshold "no finding committed - it may have died" without ever looking. Measured 18 Nov: two
    agents were reported dead at 59 minutes while both of their findings sat in FINDINGS/ - A at
    10,100 bytes and B at 12,406 bytes, committed an hour earlier. The run that read this list would
    have re-deployed work it already had.
    """
    d = os.path.join(HERE, "FINDINGS")
    if not os.path.isdir(d):
        return ""
    cls = (a.get("class") or "").split(" / ")[0].strip()
    angle = (a.get("angle") or "").strip()
    if not cls:
        return ""
    for f in sorted(os.listdir(d)):
        if cls not in f:
            continue
        if angle and ("-%s-" % angle) not in f:
            continue
        return f
    return ""


def collect():
    items = []
    now = time.time()

    # 1. What the last run said to do first.
    h = _load(HANDOFF, {})
    if (h.get("next") or "").strip():
        items.append({"kind": "carry-over", "who": "the last run",
                      "what": h["next"].strip(),
                      "why": "HANDOFF.md says this is the first work. It is ahead of any new class."})

    # 2. Agents that were deployed and have not landed a finding.
    for a in h.get("agents") or []:
        if a.get("status") != "running":
            continue
        age = None
        try:
            hh, mm = (a.get("deployed") or "").split(":")
            now_ist = time.gmtime(now + 19800)
            age = (now_ist.tm_hour * 60 + now_ist.tm_min) - (int(hh) * 60 + int(mm))
            if age < 0:
                age += 1440
        except Exception:
            pass
        landed = _finding_landed(a)
        silent = age is not None and age >= AGENT_SILENT_MIN and not landed
        items.append({"kind": "agent", "who": a.get("id") or (a.get("class", "") + "/" + a.get("angle", "")),
                      "what": "%s / %s - %s" % (a.get("class", ""), a.get("angle", ""),
                                                (a.get("question") or "")[:100]),
                      "why": ("its finding LANDED - FINDINGS/%s. Read it and act on it; do not "
                              "re-deploy this agent." % landed) if landed else
                             (("deployed %s min ago and no finding committed - it may have died with "
                               "its run. Check FINDINGS/ for %s, then either read it or re-deploy."
                               % (age, a.get("class", ""))) if silent else
                              ("deployed %s min ago, expected %s - check FINDINGS/ before you re-deploy"
                               % (age if age is not None else "?", a.get("expected") or "?")))})

    # 3. A fix that was kept but never ratcheted at corpus scale.
    att = _load(ATTEMPTS, {})
    for cls, row in att.items():
        if "kept" not in (row.get("outcomes") or []):
            continue
        if row.get("ratchet_at"):
            continue
        items.append({"kind": "ratchet", "who": cls,
                      "what": "kept, %s/%s moved, never ratcheted at corpus scale"
                              % (row.get("last_moved", "?"), row.get("last_total", "?")),
                      "why": "A fix measured on its own class is unproven everywhere else. Run the "
                             "full corpus ratchet before this class is called done."})

    # 4. Walls that were written down and not cleared.
    #
    # ONLY rows under the "## Rows" heading, and never inside a code fence. The first version of
    # this scan read the whole file and matched the format example in "How to add a row" as a real
    # blocker - a false positive of exactly the kind this pipeline is supposed to be free of. A
    # detector that reports the documentation is worse than no detector.
    try:
        in_rows = False
        in_fence = False
        for line in open(BLOCKERS, encoding="utf-8"):
            s = line.strip()
            if s.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if s.startswith("## Rows"):
                in_rows = True
                continue
            if s.startswith("## ") and in_rows:
                in_rows = False
                continue
            if not in_rows:
                continue
            if not s.startswith("| ") or s.startswith("|---") or "what I was doing" in s:
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) >= 6 and any(cells):
                items.append({"kind": "blocker", "who": cells[0],
                              "what": "%s - %s" % (cells[1][:80], cells[2][:80]),
                              "why": "can I fix it: %s | needed: %s" % (cells[4], cells[5])})
    except Exception:
        pass

    return items


def main(argv):
    beat("pending.py", "reading the pending gate")
    items = collect()
    if "--json" in argv:
        print(json.dumps({"pending": items, "count": len(items)}, indent=1))
        return 0 if not items else 1

    if not items:
        print("NOTHING PENDING - a new class may be taken.")
        print("Every carried-over item is closed, no agent is outstanding, no kept fix is")
        print("unratcheted and no blocker is open. Go to STEP 2 and pick the biggest OPEN class.")
        return 0

    print("PENDING (%d) - this is the work. Do not take a new class until it is empty." % len(items))
    print("")
    for n, it in enumerate(items, 1):
        print("%d. [%s] %s" % (n, it["kind"], it["who"]))
        print("   %s" % it["what"])
        print("   %s" % it["why"])
        print("")
    print("Order: carry-over first, then agents (read FINDINGS/, never re-deploy blind), then")
    print("ratchets, then blockers. Close them in HANDOFF/BLOCKERS/ATTEMPTS as you go - this")
    print("tool reads those files, so it goes quiet when you are actually done.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
