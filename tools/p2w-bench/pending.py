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
RATCHET_GOOGLE = os.path.join(HERE, "RATCHET-GOOGLE.json")
FINDINGS = os.path.join(HERE, "FINDINGS")
RUN      = os.path.join(HERE, "RUN.json")

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
    _next = (h.get("next") or "").strip()
    if _next:
        # A CARRY-OVER THIS RUN WROTE IS NOT PENDING WORK FOR THIS RUN.
        #
        # The documented order is: write the handoff, commit, release. But this gate treats any
        # non-empty `next` as outstanding work, so writing the handoff first made the release
        # refuse with "1 item(s) still pending" - the run blocking itself with its own note to the
        # future. The 14:15 run had to save HANDOFF.json, blank the field, release, and restore it.
        #
        # The handoff file's own mtime settles it: if it was written after this run started, this
        # run wrote it, and its note belongs to the next run, not to this one.
        _run = _load(RUN, {})
        _started = _run.get("started_ts")
        _wrote_it = False
        try:
            if _started and os.path.getmtime(HANDOFF) >= float(_started):
                _wrote_it = True
        except Exception:
            pass
        if not _wrote_it:
            items.append({"kind": "carry-over", "who": "the last run",
                          "what": _next,
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
    # EVIDENCE CLOSES A RATCHET, NOT ONLY A HAND-WRITTEN STAMP. The stamp was the only exit and three runs
    # in a row did the corpus work without writing it - the 04:20 relay ran a full pass and all 6 ratchets
    # stayed pending, which keeps the gate shut. Three rows could never clear at all:
    #   00_page_count, t08_line_order, t09_page_furniture -> 0 documents fail them, nothing to ratchet
    #   25_invisible_text                                -> the store already covers 43 of 43
    # So a row is also cleared when the store proves it: no document fails the class, or RATCHET-GOOGLE.json
    # holds a fresh entry on the current engine for every document that does. The stamp still wins.
    _gv, _rt, _engine = {}, _load(RATCHET_GOOGLE, {}), ""
    try:
        import glob as _glob
        for _f in _glob.glob(os.path.join(HERE, "..", "..", "benchmarks", "gverify", "*.json")):
            _j = json.load(open(_f, encoding="utf-8"))
            if _j.get("status") == "page_count_refused":
                continue
            _gv[os.path.basename(_f)[:-5]] = _j
    except Exception:
        _gv = {}
    # THE CURRENT ENGINE IS THE ONE MOST VERDICTS CARRY, not a file. There is no ENGINE file at the repo
    # root - checked - so reading one left _engine empty and the fresh-store test never ran, which is why
    # 25_invisible_text stayed pending with its store already covering 43 of 43. gverify re-measures on
    # HEAD, so the modal engine among its verdicts is HEAD by construction.
    _engine = ""
    if _gv:
        _c = {}
        for _j in _gv.values():
            _e = str(_j.get("engine") or "")[:8]
            if _e:
                _c[_e] = _c.get(_e, 0) + 1
        if _c:
            _engine = max(_c, key=_c.get)
    for cls, row in att.items():
        if "kept" not in (row.get("outcomes") or []):
            continue
        if row.get("ratchet_at"):
            continue
        _docs = [d for d, j2 in _gv.items() if cls in (j2.get("failed") or [])]
        if _gv and not _docs:
            continue                    # nothing fails this class - nothing to ratchet
        if _gv and _engine:
            _fresh = [d for d in _docs
                      if d in _rt and str(_rt[d].get("engine") or "")[:8] == _engine]
            if len(_fresh) == len(_docs):
                continue                # the store already covers every document this class fails
        items.append({"kind": "ratchet", "who": cls,
                      "what": "kept, %s/%s moved, never ratcheted at corpus scale"
                              % (row.get("last_moved", "?"), row.get("last_total", "?")),
                      "why": ("A fix measured on its own class is unproven everywhere else. Run the "
                              "full corpus ratchet, then close it with "
                              "`python3 tools/p2w-bench/attempt.py --class %s --ratchet <docs-checked>`. "
                              "That stamp is the ONLY thing that clears this row - ratchet_google.py "
                              "--doc <name> does one document at a time, so the store builds across "
                              "slots, but only the stamp ends it." % cls)})

    # 4. Walls that were written down and not cleared.
    #
    # ONLY rows under the "## Rows" heading, and never inside a code fence. The first version of
    # this scan read the whole file and matched the format example in "How to add a row" as a real
    # blocker - a false positive of exactly the kind this pipeline is supposed to be free of. A
    # detector that reports the documentation is worse than no detector.
    # EVERY SIX-COLUMN ROW IN THE FILE, NOT ONLY THE ONES UNDER "## Rows".
    #
    # The scanner used to require a "## Rows" heading and a six-cell row. On 18 Nov all eleven of
    # the day's rows had been appended under "## Cleared this round" - including three marked "no -
    # needs a decision" - while "## Rows" held three truncated four-column rows from 16 Nov. The gate
    # reported zero blockers while four were open, and it could not have reported otherwise.
    #
    # The section name is not the truth; the "can I fix it" cell is. A row that says it was cleared
    # is cleared wherever it sits, and a row that does not is pending wherever it sits.
    try:
        in_fence = False
        for line in open(BLOCKERS, encoding="utf-8"):
            t = line.strip()
            if t.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence or not t.startswith("| ") or t.startswith("|---"):
                continue
            cells = [c.strip() for c in t.strip("|").split("|")]
            if len(cells) < 6 or "what I was doing" in cells[1]:
                continue
            can = (cells[4] or "").lower()
            if can.startswith(("yes", "fixed", "solved", "cleared", "done")):
                continue                      # the run cleared it; it is not a wall any more
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

    if "--decisions" in argv:
        # THE ITEMS A FIXER CANNOT CLOSE ARE NOT THE FIXER'S WORK, AND THEY MUST NOT BE LOST EITHER.
        # 59 of the 81 items on 23 Nov are blockers whose own "can I fix it" column begins with "no" -
        # they need a decision from a person. classpick.py does not let them block a run (a gate that
        # waited for them would never open), so without this view they would sit in BLOCKERS.md and be
        # read by nobody. This prints only those, so the decisions that are owed stay visible.
        dec = [i for i in items
               if i.get("kind") == "blocker"
               and (i.get("why") or "").lower().startswith("can i fix it: no")]
        if not dec:
            print("NO DECISIONS OWED - every open item is one a fixer can close.")
            return 0
        print("NEEDS A DECISION (%d) - these are not a fixer's to close, and they do not block it." % len(dec))
        print("")
        for n, it in enumerate(dec, 1):
            print("%d. %s" % (n, it["who"]))
            print("   %s" % it["what"])
            print("   %s" % it["why"])
            print("")
        print("A fixer keeps working while these are open. They are reported so a person can decide,")
        print("not so a slot can wait.")
        return 1

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
