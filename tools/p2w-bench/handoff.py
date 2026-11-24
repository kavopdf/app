#!/usr/bin/env python3
"""handoff.py - one file that answers "what is happening, and what do I do next".

WHY THIS EXISTS

A fixer run can end three ways: it releases cleanly, it is forced out, or the platform
kills it mid-attempt. In the third case nothing is written at all, and the next run has to
reconstruct what happened from six files - ROUND.json, ATTEMPTS.json, HYPOTHESES.md,
RUN-LOG.md, TRACE.md, BLOCKERS.md - and still cannot answer the one question that matters:
what was this run in the middle of, and what should I do first?

So there is one file. HANDOFF.md is written by every step that changes the state of the
work: the claim, every attempt, every agent deployed, every finding that lands, and the
release. It is never more than one attempt old, which is about seven minutes.

The next run reads it before it reads anything else and before it picks a class.

    python3 tools/p2w-bench/handoff.py --show
    python3 tools/p2w-bench/handoff.py --plan "take 20_within_10pt, diagnose the 3pt band"
    python3 tools/p2w-bench/handoff.py --note "attempt 2 kept, 22/30 moved"
    python3 tools/p2w-bench/handoff.py --next "run the full 213-document ratchet on 232f622"
    python3 tools/p2w-bench/handoff.py --context "what the next run needs to know, in prose"
    python3 tools/p2w-bench/handoff.py --agent-add "class|A|which code path places inline images|11:35"
    python3 tools/p2w-bench/handoff.py --agent-land "class|A" --finding "FINDINGS/x.md"
    python3 tools/p2w-bench/handoff.py --run-end released
"""
import json, os, subprocess, sys, time

try:
    from beacon import beat
except Exception:
    def beat(*a, **k):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
MD   = os.path.join(HERE, "HANDOFF.md")
JS   = os.path.join(HERE, "HANDOFF.json")


def ist(ts=None):
    return time.strftime("%H:%M", time.gmtime((ts or time.time()) + 19800))


def load():
    try:
        return json.load(open(JS, encoding="utf-8"))
    except Exception:
        return {"plan": "", "notes": [], "next": "", "agents": [], "run": {}, "history": []}


# THE HANDOFF GREW WITHOUT A CEILING AND THE COST WAS THE RUN'S OWN TIME.
#
# Measured 23 Nov on the 19:57 run: 48 minutes total, of which 23.8 was a single silence that began
# right after handoff.py ran. The 17:58 run showed the same shape - 20.3 minutes after report.py.
# HANDOFF.json was 88,754 bytes and 78,270 of that was two lists that only ever grew: `notes` at 314
# items and `agents` at 78. Every run appends; nothing ever trimmed. A run that reads 78 KB of history
# spends a fifth of its budget doing it and then has time for one attempt - which is exactly what the
# user kept seeing.
#
# So the lists are capped on the way out, and the overflow is APPENDED TO AN ARCHIVE, never dropped.
# Nothing is lost: HANDOFF-ARCHIVE.jsonl holds every entry that leaves the live file, oldest first, one
# JSON object per line. A run that needs older history greps the archive instead of reading all of it.
KEEP_NOTES = 60      # several runs' worth of the running log
KEEP_AGENTS = 24     # the last few runs' agents; older ones are in the archive
ARCHIVE = os.path.join(HERE, "HANDOFF-ARCHIVE.jsonl")


def _trim(d):
    """Cap the two unbounded lists, moving the overflow into the archive rather than losing it."""
    moved = []
    for key, keep in (("notes", KEEP_NOTES), ("agents", KEEP_AGENTS)):
        v = d.get(key)
        if isinstance(v, list) and len(v) > keep:
            over = v[:-keep]
            d[key] = v[-keep:]
            moved.extend({"_list": key, "_entry": e} for e in over)
    if moved:
        with open(ARCHIVE, "a", encoding="utf-8") as fh:
            for e in moved:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    return d


def _pending_count():
    """How many items pending.py lists that a run can close, or 0. Subprocess, like round.py does.

    A subprocess and not an import: pending.py is the single authority on what is outstanding, and a
    second copy of its rules here is how two answers to one question start.
    """
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "pending.py"), "--json"],
                           capture_output=True, text=True, timeout=90)
        items = (json.loads(r.stdout) or {}).get("pending") or []
        return len([i for i in items
                    if not (i.get("kind") == "blocker"
                            and (i.get("why") or "").lower().startswith("can i fix it: no"))])
    except Exception:
        return 0


def save(d):
    # THE HANDOFF IS THE FIRST THING A RUN READS, SO THE GATE MUST BE IN IT.
    #
    # classpick.decide() refuses a class while pending work is open, and that refusal was being
    # bypassed every time without anyone ignoring it: the handoff is written by the previous run and
    # says "18_displacement: apply the patch, build, start the slot". A run follows the handoff and
    # never asks classpick. Measured 24 Nov: the 08:57 run took 18_displacement with 23 items open,
    # because that is what the handoff told it to do.
    #
    # So the gate is prepended here. A run that reads only one file reads the right instruction first.
    try:
        _n = _pending_count()
        if _n > 0:
            _lead = ("PENDING FIRST: %d item(s) you can close - run pending.py and take them in its "
                     "order before the class below. " % _n)
            _cur = str(d.get("next") or "")
            if not _cur.startswith("PENDING FIRST"):
                _cur = _lead + _cur
            if not _cur.startswith("CORPUS:"):
                _cur = CORPUS + _cur
            if not _cur.startswith("READ FIRST:"):
                _cur = READ_FIRST + _cur
            d["next"] = _cur
    except Exception:
        pass
    json.dump(_trim(d), open(JS, "w", encoding="utf-8"), indent=1)
    render(d)


# A FILE NOBODY IS SENT TO IS A FILE NOBODY READS.
#
# On 24 Nov thirty sub-agents root-caused every open docx class and eighteen did the same for txt. The
# results are two files. The brief names them, but the brief is prose and `next` is the data a run actually
# opens first - so the pointer goes in both. Six of the ten docx classes turn out to be ONE construct, the
# 120 pt gap cap in DocxWriter, which no class-specific patch can touch.
CORPUS = ("CORPUS: regress.py --check now builds the converted corpus itself "
          "(corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "
          "\"no .docx output directory\" was ever the reason it could not run. ")
READ_FIRST = ("READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and "
              "FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the "
              "measurement that proves it. ")


def render(d):
    L = ["# HANDOFF - read this before you pick a class", ""]
    nh = d.get("needs_human") or []
    if nh:
        # "NEEDS A HUMAN - no future run can clear these" was the header here, and it was the most
        # expensive sentence in the repository: it told every run that followed not to bother. Nobody
        # is coming. What a run actually leaves behind is a wall plus the evidence about it, and the
        # next run has every right to try a different approach through it.
        L.append("## PARKED - what was tried, and what would re-open it")
        L.append("")
        L.append("A run tried these and could not get through. That is a record of one approach, not a")
        L.append("verdict on the problem: the next run may take any of them again with a genuinely")
        L.append("different idea. What is not worth repeating is the attempt listed below.")
        L.append("")
        L.append("| # | what it is | what was tried | what would re-open it | when |")
        L.append("|---|---|---|---|---|")
        for n, x in enumerate(nh):
            L.append("| %d | %s | %s | %s | %s |" % (
                n, (x.get("what") or "").replace("|", "/")[:90],
                (x.get("tried") or "").replace("|", "/")[:70],
                (x.get("change") or "").replace("|", "/")[:70], x.get("at", "")))
        L.append("")
    L.append("Written by handoff.py on every claim, every attempt, every agent and every release.")
    L.append("It is never more than one attempt old. If the claim in ROUND.json is older than the")
    L.append("stale limit, the run that wrote this died without releasing - treat its plan as")
    L.append("unfinished work, not as a result.")
    L.append("")
    r = d.get("run") or {}
    L.append("## The run that wrote this")
    L.append("")
    L.append("| | |")
    L.append("|---|---|")
    L.append("| started | %s |" % (r.get("started") or "-"))
    L.append("| ended | %s |" % (r.get("ended") or "still running"))
    L.append("| how it ended | %s |" % (r.get("ended_how") or "-"))
    L.append("| plan | %s |" % ((d.get("plan") or "-").replace("|", "/")))
    L.append("")
    if d.get("context"):
        L.append("## The picture, in the words of the run that left it")
        L.append("")
        for para in (d["context"] or "").split("\n"):
            L.append("> " + para if para.strip() else ">")
        L.append("")
    if d.get("next"):
        L.append("## What the next run should do first")
        L.append("")
        L.append("> " + d["next"])
        L.append("")
    ag = d.get("agents") or []
    if ag:
        L.append("## Agents deployed and not yet accounted for")
        L.append("")
        L.append("| id | class | angle | question | deployed | expected | status | finding |")
        L.append("|---|---|---|---|---|---|---|---|")
        for a in ag:
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                a.get("id", ""), a.get("class", ""), a.get("angle", ""), (a.get("question") or "").replace("|", "/")[:70],
                a.get("deployed", ""), a.get("expected", ""), a.get("status", ""), a.get("finding", "")))
        L.append("")
        L.append("A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent")
        L.append("that wrote it is long gone - that is why it writes a file instead of replying.")
        L.append("")
    if d.get("notes"):
        L.append("## What happened, most recent last")
        L.append("")
        for n in d["notes"][-25:]:
            L.append("- `%s` %s" % (n.get("at", ""), n.get("text", "")))
        L.append("")
    L.append("## Where the rest of the state lives")
    L.append("")
    L.append("| file | what it answers |")
    L.append("|---|---|")
    L.append("| ROUND.json | phase, round, who holds which slot |")
    L.append("| ATTEMPTS.json | every attempt on every class, with its outcome |")
    L.append("| HYPOTHESES.md | which theories are confirmed, ruled out, untested |")
    L.append("| FINDINGS/ | what subagents proved, including ones that outlived their run |")
    L.append("| BLOCKERS.md | walls a run could not clear, and what is needed |")
    L.append("| RUN-LOG.md | the timeline, one line per event |")
    open(MD, "w", encoding="utf-8").write("\n".join(L) + "\n")


def _stamp_ist():
    """A full timestamp on the same clock as ist(), so a duration means what it says.

    `deployed` and `landed` were HH:MM from ist() (Asia/Kolkata); deployed_at and landed_at were
    time.strftime, which is UTC. A row could therefore read "deployed 06:17" beside a timestamp of
    00:47 - a 5h30 gap that is not a delay, it is two clocks - and report.py, given two UTC stamps
    written in the same minute, printed "0 min" for an agent that had worked. Measured 23 Nov: 30 of
    62 agent records carried identical deployed_at and landed_at, so every one of them reported zero.
    """
    try:
        from zoneinfo import ZoneInfo
        import datetime as _d
        return _d.datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%dT%H:%M")
    except Exception:
            # NOT time.strftime - that is UTC, and falling back to it is how this bug would come
            # back: a sandbox without tzdata would silently stamp UTC into a field report.py
            # subtracts from an IST one, and every duration would be off by 5h30 again with nothing
            # to show for it. IST is UTC+05:30 with no daylight saving, so no tzdata is needed.
            import datetime as _d
            return (_d.datetime.utcnow()
                    + _d.timedelta(hours=5, minutes=30)).strftime("%Y-%m-%dT%H:%M")


def main(argv):
    beat("handoff.py", "reading or writing the handoff")
    d = load()
    if "--show" in argv or len(argv) == 1:
        render(d)
        print(open(MD, encoding="utf-8").read())
        return 0
    if "--run-start" in argv:
        d["run"] = {"started": ist(), "ended": None, "ended_how": None}
        d["plan"] = ""
    if "--next" in argv:
        nxt = argv[argv.index("--next") + 1]
        d["next"] = nxt
        # WHICH CLASS THIS CARRY-OVER BELONGS TO, derived rather than asked for.
        #
        # pending.py reports this text as work that blocks every new class. When the class it
        # describes is PARKED it can never be attempted again, so the gate would hold it for ever -
        # STEP 10 says park and move on, the gate says move on only when nothing is pending, and a
        # parked class is always pending. Nothing cleared it, so the two rules contradicted.
        #
        # The fix needs to know which class the prose is about, and a run will not remember to say.
        # So it is read off the text: every class name in DEFECT-CLASSES.md is looked for, and a
        # single unambiguous match is recorded as next_class. classify.py clears the carry-over when
        # that class is parked.
        d["next_class"] = ""
        try:
            known = []
            cf = os.path.join(HERE, "..", "..", "benchmarks", "DEFECT-CLASSES.md")
            for line in open(cf, encoding="utf-8"):
                cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
                for c in cells:
                    if c.count("-") >= 1 and " " not in c and len(c) > 12 and c.islower():
                        known.append(c)
            known = sorted(set(known))
            hits = [k for k in known if k in nxt]
            if len(hits) == 1:
                d["next_class"] = hits[0]
        except Exception:
            pass
    if "--plan" in argv:
        d["plan"] = argv[argv.index("--plan") + 1]
        d["run"] = {"started": ist(), "ended": None, "ended_how": None}
    if "--note" in argv:
        d["notes"].append({"at": ist(), "text": argv[argv.index("--note") + 1]})
    if "--next" in argv:
        d["next"] = argv[argv.index("--next") + 1]
    if "--needs-human" in argv:
        # Something the run could not clear and a human must change. It goes to the top of
        # HANDOFF.md, above everything else, because it is the only item here that no future run
        # can fix by itself - every run after this one will hit the same wall until a person
        # removes it.
        raw = argv[argv.index("--needs-human") + 1]
        parts = [x.strip() for x in (raw.split("|") + ["", "", ""])[:3]]
        try:
            _rp = os.path.join(HERE, "RUN.json")
            _r = json.load(open(_rp, encoding="utf-8"))
            _r["needs_human"] = _r.get("needs_human", 0) + 1
            json.dump(_r, open(_rp, "w", encoding="utf-8"), indent=1)
        except Exception:
            pass
        d.setdefault("needs_human", []).append(
            {"at": ist(), "what": parts[0], "tried": parts[1], "change": parts[2]})
    if "--needs-human-clear" in argv:
        n = int(argv[argv.index("--needs-human-clear") + 1])
        if 0 <= n < len(d.get("needs_human") or []):
            d["needs_human"].pop(n)
    if "--context" in argv:
        # The narrative. `notes` is a log of what happened; this is the picture - what is true now,
        # what was ruled out and why, and what the next run would waste time rediscovering.
        d["context"] = argv[argv.index("--context") + 1]
    if "--agent-add" in argv:
        raw = argv[argv.index("--agent-add") + 1]
        parts = (raw.split("|") + ["", "", "", ""])[:4]
        # The id has to be unique on its own. A prefix of class+angle is not: two agents on the
        # same class and angle - which is exactly the case that needed disambiguating - produced
        # the same id and the bug survived its own fix until it was tested.
        _base = "%s%s" % (parts[0].strip()[:4], parts[1].strip())
        _used = {a.get("id") for a in d["agents"]}
        _n = 1
        while "%s-%02d" % (_base, _n) in _used:
            _n += 1
        try:
            _rp = os.path.join(HERE, "RUN.json")
            _r = json.load(open(_rp, encoding="utf-8"))
            _r.setdefault("agents", []).append("%s-%02d" % (_base, _n))
            json.dump(_r, open(_rp, "w", encoding="utf-8"), indent=1)
        except Exception:
            pass
        d["agents"].append({"id": "%s-%02d" % (_base, _n),
                            "class": parts[0].strip(), "angle": parts[1].strip(),
                            "question": parts[2].strip(), "expected": parts[3].strip(),
                            "deployed": ist(), "status": "running", "finding": "",
                            # Full timestamp as well as the HH:MM, so a duration survives midnight
                            # and so report.py can say how long the agent actually worked.
                            # THE SAME CLOCK AS `deployed`. This used time.strftime, which is UTC, while
                            # `deployed` uses ist() - so a row could read "deployed 06:17" beside a
                            # timestamp of 00:47, and report.py then subtracted two UTC stamps written in
                            # the same minute and printed "0 min" for an agent that had worked. One clock.
                            "deployed_at": _stamp_ist()})
        d["notes"].append({"at": ist(), "text": "agent deployed: %s / %s - %s"
                           % (parts[0].strip(), parts[1].strip(), parts[2].strip()[:80])})
    if "--agent-land" in argv:
        raw = argv[argv.index("--agent-land") + 1]
        parts = (raw.split("|") + ["", ""])[:2]
        fnd = argv[argv.index("--finding") + 1] if "--finding" in argv else ""
        # Match by id first, then class+angle. Two agents on the same class and angle used to be
        # ambiguous: the first running one was marked landed whichever had actually returned.
        target = raw.strip()
        for a in d["agents"]:
            if a.get("status") != "running":
                continue
            if a.get("id") == target or (a.get("class") == parts[0].strip()
                                         and a.get("angle") == parts[1].strip()):
                a["status"] = "landed"
                a["finding"] = fnd
                # WHEN IT LANDED, not just that it did. "deployed 09:57" with no counterpart
                # meant nobody could say whether an agent took four minutes or forty - the report
                # could name it and nothing else. A full timestamp also survives midnight, which
                # the bare HH:MM in "deployed" does not.
                a["landed_at"] = _stamp_ist()
                d["notes"].append({"at": ist(), "text": "agent landed: %s / %s -> %s"
                                   % (parts[0].strip(), parts[1].strip(), fnd or "(no file)")})
                break
    if "--run-end" in argv:
        d.setdefault("run", {})["ended"] = ist()
        d["run"]["ended_how"] = argv[argv.index("--run-end") + 1]
        d["history"].append({"at": ist(), "how": d["run"]["ended_how"],
                             "plan": d.get("plan", "")})
        d["history"] = d["history"][-20:]
    save(d)
    print("handoff written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
