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
    python3 tools/p2w-bench/handoff.py --agent-add "class|A|which code path places inline images|11:35"
    python3 tools/p2w-bench/handoff.py --agent-land "class|A" --finding "FINDINGS/x.md"
    python3 tools/p2w-bench/handoff.py --run-end released
"""
import json, os, sys, time

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


def save(d):
    json.dump(d, open(JS, "w", encoding="utf-8"), indent=1)
    render(d)


def render(d):
    L = ["# HANDOFF - read this before you pick a class", ""]
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
    if d.get("next"):
        L.append("## What the next run should do first")
        L.append("")
        L.append("> " + d["next"])
        L.append("")
    ag = d.get("agents") or []
    if ag:
        L.append("## Agents deployed and not yet accounted for")
        L.append("")
        L.append("| class | angle | question | deployed | expected | status | finding |")
        L.append("|---|---|---|---|---|---|---|")
        for a in ag:
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                a.get("class", ""), a.get("angle", ""), (a.get("question") or "").replace("|", "/")[:70],
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


def main(argv):
    d = load()
    if "--show" in argv or len(argv) == 1:
        render(d)
        print(open(MD, encoding="utf-8").read())
        return 0
    if "--run-start" in argv:
        d["run"] = {"started": ist(), "ended": None, "ended_how": None}
        d["plan"] = ""
    if "--plan" in argv:
        d["plan"] = argv[argv.index("--plan") + 1]
        d["run"] = {"started": ist(), "ended": None, "ended_how": None}
    if "--note" in argv:
        d["notes"].append({"at": ist(), "text": argv[argv.index("--note") + 1]})
    if "--next" in argv:
        d["next"] = argv[argv.index("--next") + 1]
    if "--agent-add" in argv:
        raw = argv[argv.index("--agent-add") + 1]
        parts = (raw.split("|") + ["", "", "", ""])[:4]
        d["agents"].append({"class": parts[0].strip(), "angle": parts[1].strip(),
                            "question": parts[2].strip(), "expected": parts[3].strip(),
                            "deployed": ist(), "status": "running", "finding": ""})
        d["notes"].append({"at": ist(), "text": "agent deployed: %s / %s - %s"
                           % (parts[0].strip(), parts[1].strip(), parts[2].strip()[:80])})
    if "--agent-land" in argv:
        raw = argv[argv.index("--agent-land") + 1]
        parts = (raw.split("|") + ["", ""])[:2]
        fnd = argv[argv.index("--finding") + 1] if "--finding" in argv else ""
        for a in d["agents"]:
            if a.get("class") == parts[0].strip() and a.get("angle") == parts[1].strip() \
               and a.get("status") == "running":
                a["status"] = "landed"
                a["finding"] = fnd
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
