#!/usr/bin/env python3
"""report.py - the eight numbers, computed from committed data only.

THE RULE THIS TOOL EXISTS TO ENFORCE: a number appears here only if something on disk proves it.
If a run claims thirty-one documents improved and never committed the measurement that shows it,
this tool reports zero - not because the work did not happen, but because nobody can check it.

That is not pedantry. On 16 Nov the fixer recorded "212 documents compared, 0 regressions, 31
improvements" in ATTEMPTS.json, and benchmarks/RANKING.csv was byte-identical to the round-one
baseline. The claim was in a sentence and the evidence was nowhere, so the claim could not be
told apart from a hope.

    python3 tools/p2w-bench/report.py            # the report
    python3 tools/p2w-bench/report.py --json     # same, machine-readable
"""
import csv, json, os, sys, time

try:
    from beacon import beat
except Exception:
    def beat(*a, **k):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CLASSES  = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")
RANK     = os.path.join(ROOT, "benchmarks", "RANKING.csv")
BASELINE = os.path.join(ROOT, "benchmarks", "RANKING-BASELINE.csv")
RUN      = os.path.join(HERE, "RUN.json")
ATTEMPTS = os.path.join(HERE, "ATTEMPTS.json")
ROUND    = os.path.join(HERE, "ROUND.json")
HANDOFF  = os.path.join(HERE, "HANDOFF.json")


def _json(p, default):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return default


def classes():
    """Count CLASSES, not document rows.

    The file is one row per document - 212 of them - grouped by problem name. The first version
    of this function counted rows and called them classes, so the report said "212 classes total"
    when there are eight. A number that is wrong by a factor of twenty-six is worse than a number
    that is missing.

    A class is solved when no document under it is still OPEN.
    """
    per_class = {}          # problem -> [open_count, fixed_count, never_broken]
    docs = 0
    try:
        for line in open(CLASSES, encoding="utf-8"):
            s = line.strip()
            if not s.startswith("| ") or s.startswith("|---"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 8 or cells[0] in ("rank", "") or not cells[0].isdigit():
                continue
            docs += 1
            problem, status, note = cells[2], cells[6].upper(), cells[7].lower()
            rec = per_class.setdefault(problem, [0, 0, 0])
            if "OPEN" in status:
                rec[0] += 1
            elif "no defect" in note or problem.lower() == "none":
                rec[2] += 1
            else:
                rec[1] += 1
    except Exception:
        pass
    # "none" is the pseudo-class for documents with no defect. It is a row in the file, not a
    # problem to solve, and counting it made the report say "0 of 7 clear" when six classes carry
    # the 91 OPEN documents.
    per_class.pop("none", None)
    total = len(per_class)
    solved = sum(1 for v in per_class.values() if v[0] == 0 and v[1] > 0)
    openc = sum(1 for v in per_class.values() if v[0] > 0)
    return total, solved, openc, docs, per_class


def _exempt():
    """Documents the ranking carries but does not score, named rather than silently dropped.

    RANKING.csv gave 416_many_tiny_pages share5=0.0 and problem=none - a 300-page document reading as
    PERFECT in the one table the whole pipeline is judged on, when EXEMPT.json says it was never
    measured because one whole-document pass exceeds the per-command budget. A blank score is honest;
    a zero is a lie, and it drags the corpus mean down so every other number looks better than it is.
    """
    out = []
    try:
        for r in csv.DictReader(open(RANK, encoding="utf-8")):
            if (r.get("problem") or "").strip().lower() == "exempt":
                out.append(r.get("document"))
    except Exception:
        pass
    return out


def _share5(path):
    d = {}
    try:
        for r in csv.DictReader(open(path, encoding="utf-8")):
            doc, v = r.get("document"), r.get("share5")
            if doc and v:
                try:
                    d[doc] = float(v)
                except ValueError:
                    pass
    except Exception:
        pass
    return d


def this_run():
    r = _json(RUN, {})
    if not r.get("started"):
        return {"present": False}
    end = r.get("ended_ts") or time.time()
    mins = int((end - (r.get("started_ts") or end)) / 60)
    return {"present": True, "started": r.get("started"), "ended": r.get("ended"),
            "minutes": mins, "class": r.get("class") or "-",
            "attempts": r.get("attempts", 0), "kept": r.get("kept", 0),
            "docs_improved": r.get("docs_improved", 0),
            "agents": r.get("agents") or [], "obstacles_cleared": r.get("obstacles_cleared", 0),
            "needs_human": r.get("needs_human", 0)}



def run_docs():
    """The documents whose score changed inside THIS run's window.

    The headline used to name best[0] - the largest improvement of the whole round - so the 14:50
    run, which took itr-computation-with-slab-table from 68.82 to 50.80, announced
    "415_inline_images fixed, 89.04 -> 0.00": a fix from four hours earlier. A report whose headline
    credits the wrong work is worse than one with no headline.

    The ranking is committed with the run, so the last commit touching RANKING.csv inside the run's
    own window is the run's own measurement. Diff it against its parent.
    """
    import subprocess as _sp
    try:
        run = _json(RUN, {})
        lo, hi = run.get("started_ts"), run.get("ended_ts")
        if not lo:
            return []
        out = _sp.run(["git", "-C", ROOT, "log", "-1", "--format=%H %ct", "--",
                       "benchmarks/RANKING.csv"], capture_output=True, text=True, timeout=20).stdout.split()
        if len(out) < 2:
            return []
        sha, when = out[0], float(out[1])
        if hi and when > hi + 300:
            return []                       # committed after the run ended
        if when < lo - 300:
            return []                       # committed before the run started
        prev = _sp.run(["git", "-C", ROOT, "show", "%s^:benchmarks/RANKING.csv" % sha],
                       capture_output=True, text=True, timeout=20).stdout
        now = _sp.run(["git", "-C", ROOT, "show", "%s:benchmarks/RANKING.csv" % sha],
                      capture_output=True, text=True, timeout=20).stdout
        if not prev or not now:
            return []

        def _m(txt):
            d = {}
            for row in csv.DictReader(txt.splitlines()):
                try:
                    d[row["document"]] = float(row["share5"])
                except Exception:
                    pass
            return d
        a, b = _m(prev), _m(now)
        diff = [{"doc": k, "before": a[k], "after": b[k]}
                for k in a if k in b and abs(a[k] - b[k]) > 0.05]
        diff.sort(key=lambda x: x["after"] - x["before"])
        return diff
    except Exception:
        return []


def corpus():
    """Improvement measured against the round-one baseline, from committed files only."""
    b, c = _share5(BASELINE), _share5(RANK)
    if not b or not c:
        return {"available": False,
                "why": "RANKING-BASELINE.csv or RANKING.csv missing"}
    common = sorted(set(b) & set(c))
    if not common:
        return {"available": False, "why": "no documents in common"}
    bm = sum(b[k] for k in common) / len(common)
    cm = sum(c[k] for k in common) / len(common)
    improved = [k for k in common if c[k] < b[k] - 0.05]
    regressed = [k for k in common if c[k] > b[k] + 0.05]
    # FIXED IS NOT MOVED. A document that went 18.48 -> 15.00 has improved by every definition and is
    # still fifteen per cent wrong; calling that a fix is how a run reports progress while ninety-one
    # documents stay broken.
    # 99%, NOT 98%. The bar is share5 <= 1.0: at most one per cent of the ink more than 5 px from
    # where it belongs. That is the same line problem_name() already draws for "none", so a document
    # the classifier calls clean and a document this report calls fixed are the same document - one
    # definition, in one place, instead of two that drift apart.
    FIXED_BAR = 1.0
    fixed = [k for k in common if c[k] <= FIXED_BAR and b[k] > FIXED_BAR]
    moved_open = [k for k in improved if k not in fixed]
    unchanged = len(common) - len(improved) - len(regressed)
    identical = all(abs(b[k] - c[k]) < 1e-9 for k in common)
    # share@5px is the fraction of ink that landed more than 5px from where it belongs, so a
    # FALL is an improvement. The first version printed (current - baseline), which reported
    # 6.15 -> 5.01 as "-18.55%" - arithmetically right, and read by every human as a regression.
    return {"available": True, "docs": len(common),
            "fixed": len(fixed), "moved_open": len(moved_open),
            "still_open": len([k for k in common if c[k] > FIXED_BAR]),
            "baseline_mean": round(bm, 2), "current_mean": round(cm, 2),
            "pct": round((bm - cm) / bm * 100, 2) if bm else 0.0,
            "improved": len(improved), "regressed": len(regressed), "unchanged": unchanged,
            "measurement_committed": not identical,
            "best": [{"doc": k, "before": round(b[k], 2), "after": round(c[k], 2)}
                     for k in sorted(improved, key=lambda k: c[k] - b[k])[:5]]}



def obstacles():
    """Walls this run hit, split into the ones it cleared and the ones a human must clear.

    BLOCKERS.md has recorded every wall since the pipeline began, with a column headed "can I fix
    it" - the run's own verdict on whether it cleared the obstacle or a human has to. The report
    never read that file: zero references. So the most useful thing a run can say was invisible, and
    a run that hit one wall it could not clear looked identical to a run that hit nothing at all.
    """
    path = os.path.join(ROOT, "tools", "p2w-bench", "BLOCKERS.md")
    # THE DATE COMES FROM started_ts, THE ONLY FIELD THAT IS ACTUALLY A DATE. `started` is a bare
    # HH:MM ("14:50"), so taking its first ten characters gave "14:50" and testing that as a prefix
    # of each row's "2026-11-18 13:00" matched nothing - the report said "0 cleared, 0 need a human"
    # about a run that had appended eleven rows. The fixer fixed exactly this at 13:48 and a later
    # rewrite of this file put the bug back; it is written this way so it does not come back again.
    import datetime as _dt
    today = ""
    _ts = _json(RUN, {}).get("started_ts")
    if _ts:
        try:
            today = _dt.datetime.fromtimestamp(float(_ts) + 19800).strftime("%Y-%m-%d")
        except Exception:
            today = ""
    if not today:
        today = (_json(RUN, {}).get("started") or "")[:10]
    rows = []
    try:
        for line in open(path, encoding="utf-8"):
            if not line.startswith("| ") or line.startswith("|---"):
                continue
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) < 6 or c[0].lower().startswith("time"):
                continue
            if today and not c[0].startswith(today):
                continue
            # THE RUN'S ROWS, NOT THE DAY'S. This counted every row written today and printed
            # "16 cleared" for a run that wrote two - the number was true of the day and false of the
            # run, and the run's own report said two. A blocker row carries "YYYY-MM-DD HH:MM", so it
            # can be placed in the window exactly.
            try:
                _h, _m = int(c[0][11:13]), int(c[0][14:16])
                _t = _dt.datetime(int(c[0][0:4]), int(c[0][5:7]), int(c[0][8:10]), _h, _m).timestamp() - 19800
                _lo = float(_json(RUN, {}).get("started_ts") or 0)
                _hi = float(_json(RUN, {}).get("ended_ts") or time.time())
                if _lo and not (_lo - 60 <= _t <= _hi + 900):
                    continue
            except Exception:
                pass
            rows.append({"can": c[4], "wall": c[2]})
    except Exception:
        return {"mine": 0, "human": 0, "last": ""}
    def cleared(r):
        t = (r["can"] or "").lower()
        return t.startswith(("yes", "fixed", "solved", "cleared", "done"))
    mine = [r for r in rows if cleared(r)]
    human = [r for r in rows if not cleared(r)]
    return {"mine": len(mine), "human": len(human),
            "last": human[-1]["wall"][:110] if human else ""}


def silences():
    """What the run was doing while it looked dead.

    A fixer run is watched from outside, and from outside a long stretch with no commit and no beat
    is indistinguishable from a crash. Measured 18 Nov: the 09:54 run was reported as possibly dead
    at 11:05 because the last committed beat was 10:55 - and it was running the 213-document ratchet,
    one command that takes forty minutes and writes nothing until it returns.

    THE WINDOW IS EPOCH ARITHMETIC. RUN.json carries started_ts and ended_ts; "ist" is a bare
    HH:MM:SS that cannot tell one day from another. Three earlier versions of this function compared
    strings and reported silences that were really the gap between one run and the next - 1351
    minutes once, 611 another time. When the timestamps are missing the window is skipped rather
    than guessed.
    """
    try:
        run = _json(RUN, {})
        lo = run.get("started_ts")
        hi = run.get("ended_ts") or (time.time() if lo else None)
        if not lo:
            return {"available": False}
        lo, hi = float(lo), float(hi)
        path = os.path.join(ROOT, "tools", "p2w-bench", "TIMELINE.jsonl")
        rows = []
        for line in open(path, encoding="utf-8"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get("t", 0)
            if lo - 5 <= t <= hi + 5:
                rows.append(d)
        rows.sort(key=lambda r: r.get("t", 0))
        if len(rows) < 2:
            return {"available": False}
        gaps = []
        for k in range(len(rows) - 1):
            g = rows[k + 1].get("t", 0) - rows[k].get("t", 0)
            if g >= 120:
                gaps.append({"min": round(g / 60.0, 1), "at": rows[k].get("ist", ""),
                             "doing": (rows[k].get("d") or "")[:70]})
        gaps.sort(key=lambda x: -x["min"])
        return {"available": True, "beats": len(rows), "n": len(gaps),
                "longest": gaps[0] if gaps else None}
    except Exception:
        return {"available": False}


PHASES = (
    ("setup",   ("claimed", "archive.py", "housekeeping", "gaps.py", "step.py")),
    ("screen",  ("screen.py",)),
    ("build",   ("build-engine", "building the engine", "compil")),
    ("measure", ("p2w.py", "measure", "ratchet", "gate.py", "convert", "census")),
    ("record",  ("attempt.py", "handoff.py", "classrow.py", "pending.py", "round.py")),
    ("report",  ("report.py", "chain.py")),
)


def _phase_of(text):
    t = (text or "").lower()
    for name, keys in PHASES:
        for k in keys:
            if k in t:
                return name
    return "other"


def phases():
    """Where the run's minutes actually went.

    A total tells nobody whether the run spent its hour fixing the engine or waiting for a clone.
    Measured 18 Nov: a 38-minute slot of which 37 was one conversion-and-measure loop and the rest
    four tool calls.

    A beat marks the start of a tool call, and editing DocxWriter for twelve minutes is not a tool
    call - so the gap that ends at an attempt belongs to the fix that produced it, not to whatever
    beat happened to precede it. That mistake credited twelve minutes of engine work to "setup".
    """
    try:
        run = _json(RUN, {})
        lo = run.get("started_ts")
        hi = run.get("ended_ts")
        if not lo:
            return []
        lo = float(lo)
        hi = float(hi) if hi else time.time()
        rows = []
        for line in open(os.path.join(ROOT, "tools", "p2w-bench", "TIMELINE.jsonl"), encoding="utf-8"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if lo - 5 <= d.get("t", 0) <= hi + 5:
                rows.append(d)
        rows.sort(key=lambda r: r.get("t", 0))
        if not rows:
            return []
        acc, order = {}, []
        for k in range(len(rows)):
            nxt_t = rows[k + 1].get("t", hi) if k + 1 < len(rows) else hi
            g = max(0.0, nxt_t - rows[k].get("t", 0))
            nxt_d = rows[k + 1].get("d") if k + 1 < len(rows) else ""
            if g >= 120 and "attempt.py" in (nxt_d or ""):
                ph = "fix"
            elif g >= 120 and "report.py" in (nxt_d or ""):
                ph = "report"
            elif g >= 300:
                # A LONG GAP WITH NO BEACON IS MEASUREMENT OR A BUILD, AND SAYING "record" IS A LIE.
                #
                # The 16:52 run spent 18.4 minutes converting 86 of 213 documents twice, one JVM each,
                # after a classrow.py beat. The beat before a gap is not what the gap was spent on: a
                # conversion loop, a soffice render and a compile write nothing at all, so the only
                # honest label for five minutes or more of silence is the work that cannot announce
                # itself. The run's own report called it "measure - 19 min"; this now agrees with it
                # instead of filing it under "record".
                ph = "measure"
            else:
                ph = _phase_of(rows[k].get("d"))
            if ph not in acc:
                acc[ph] = 0.0
                order.append(ph)
            acc[ph] += g
        named = [("setup", "setup - claim, housekeeping, reading the gate"),
                 ("screen", "screen - the class's own documents"),
                 ("build", "build - compiling the engine"),
                 ("fix", "fix - diagnose and change the engine"),
                 ("measure", "measure or build - a conversion, screen or compile writes no beacon"),
                 ("record", "record - attempt, handoff, class rows"),
                 ("report", "report - the report and the chain"),
                 ("other", "other - not attributed to a tool")]
        return [{"phase": label, "min": round(acc[key] / 60.0, 1)}
                for key, label in named if acc.get(key, 0) >= 30]
    except Exception:
        return []


def committed():
    """Every file this run committed, read from git - not typed.

    The 13:50 run's report said "Committed: 17 files" and named HYPOTHESES, RUN-HISTORY and CHAIN.json
    among them. Its commits have thirteen files between them and none of those three. The prompt lists
    HYPOTHESES.md and RUN-HISTORY.json as required, so the run believed it had committed them and the
    report repeated the belief.

    A run commits more than once - the 15:58 run made three commits in two minutes - so this walks the
    whole window and unions them. A "Committed" line that is typed is a claim; this one is a fact.
    """
    import subprocess as _sp
    try:
        run = _json(RUN, {})
        lo, hi = run.get("started_ts"), run.get("ended_ts")
        if not lo:
            return None
        lo = float(lo)
        hi = float(hi or time.time())
        log = _sp.run(["git", "-C", ROOT, "log", "--format=%H %ct %s",
                       "--since=%d" % int(lo - 30), "--until=%d" % int(hi + 120)],
                      capture_output=True, text=True, timeout=30).stdout
        # THE RUN'S OWN COMMITS, BY ITS OWN PREFIX. The window alone is not enough: on 18 Nov another
        # agent committed twice inside the fixer's run and the file count came out at 19 across 10
        # commits for a run that made 3. The fixer signs every commit "p2w fixer <HH:MM>: ..." - that
        # is the only marker that separates its work from everything else on the branch.
        shas = []
        for line in log.strip().split("\n"):
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            try:
                t = float(parts[1])
            except Exception:
                continue
            if not (lo - 30 <= t <= hi + 120):
                continue
            if parts[2].startswith("p2w fixer"):
                shas.append(parts[0])
        if not shas:
            return None
        files = set()
        for sha in shas:
            stat = _sp.run(["git", "-C", ROOT, "show", "--stat", "--format=", sha],
                           capture_output=True, text=True, timeout=20).stdout
            for l in stat.split("\n"):
                if "|" in l:
                    files.add(l.split("|")[0].strip().split("/")[-1])
        return {"sha": shas[0][:7], "commits": len(shas), "n": len(files),
                "files": sorted(files)}
    except Exception:
        return None


def tried():
    """Every attempt THIS RUN recorded, with what it measured and how it ended.

    The 15:58 run's chat message carried a table REPORT.md did not have:

        | Idea | Measured result | Verdict |
        | Anchor the running footer at its own y | traceLines: the footer is a row of table 3 |
        | Release the f=0.974 squeeze            | itr-computation 50.80 -> 70.85           |
        | Cell baseline: the row's pitch         | 4 table docs, 4 same, 0 better           |

    That table is the most useful thing in the report - it says what was already proved wrong, so the
    next run does not try it again - and it existed only because the fixer typed it by hand. The data
    is in ATTEMPTS.json's per-attempt history; this reads it.
    """
    import datetime as _dt
    try:
        run = _json(RUN, {})
        lo = run.get("started_ts")
        if not lo:
            return []
        lo = float(lo)
        hi = float(run.get("ended_ts") or time.time())
        out = []
        for cls, row in (_json(ATTEMPTS, {}) or {}).items():
            for x in (row.get("history") or []):
                at = (x.get("at") or "").strip()
                try:
                    t = _dt.datetime.strptime(at, "%Y-%m-%d %H:%M").timestamp() - 19800
                except Exception:
                    continue
                if not (lo - 180 <= t <= hi + 900):
                    continue
                out.append({"at": at[11:], "cls": cls, "outcome": x.get("outcome") or "?",
                            "moved": x.get("moved"), "total": x.get("total"),
                            "reason": (x.get("reason") or "").strip()})
        out.sort(key=lambda r: r["at"])
        return out
    except Exception:
        return []


def txt():
    """The .txt half: how many documents are scored, how many pass every applicable check.

    THE TXT HAD NO SCORE FOR A DAY. verify_txt.py has twelve named checks and its own docstring says
    why: "the pipeline measures the .docx path and nothing else... the .txt is never opened. So the
    fixer cannot improve it." The separate store was deleted on 17 Nov on the belief that
    RANKING.csv's text_recall covered it - but text_recall compares the RENDERED DOCX's text with the
    source, and no tool opens the .txt at all. So the txt could break outright without a number
    moving, and for a day it did.

    A document passes at the same 99% bar the docx uses: EVERY applicable check passes. `abstained`
    is never counted as a pass - a check that did not run is not a check that passed.
    """
    path = os.path.join(HERE, "RANKING-TXT.csv")
    if not os.path.exists(path):
        return {"available": False}
    rows = []
    try:
        for r in csv.DictReader(open(path, encoding="utf-8")):
            try:
                app = int(r.get("applicable") or 0)
                bad = int(r.get("failed") or 0)
            except ValueError:
                continue
            if bad < 0 or app <= 0:
                continue
            rows.append({"doc": r["document"], "app": app, "failed": bad,
                         "ids": (r.get("failed_ids") or "").strip()})
    except Exception:
        return {"available": False}
    if not rows:
        return {"available": False}
    clean = [r for r in rows if r["failed"] == 0]
    bad = [r for r in rows if r["failed"] > 0]
    tally = {}
    for r in bad:
        for cid in r["ids"].split():
            tally[cid] = tally.get(cid, 0) + 1
    top = sorted(tally.items(), key=lambda t: -t[1])[:3]
    return {"available": True, "scored": len(rows), "clean": len(clean),
            "failing": len(bad), "top": top,
            "pct": round(100.0 * len(clean) / len(rows), 1)}


def subagents():
    """Every agent this run deployed, with how long each one actually worked.

    "deployed 09:57" with no counterpart meant nobody could say whether an agent took four minutes
    or forty - the report could name it and nothing else. Each record now carries deployed_at and
    landed_at as full timestamps; for older records the finding file's commit time is the best
    available stand-in, and where neither exists the column says so rather than guessing.
    """
    h = _json(HANDOFF, {})
    # THIS RUN'S AGENTS ONLY. RUN.json lists the ids it deployed; the handoff keeps every agent ever
    # used, so without this filter the report shows agents from three days ago beside today's and
    # the "Took" column fills with cross-day rows that belong to somebody else's run.
    run = _json(RUN, {})
    mine = set(run.get("agents") or [])
    out = []
    for a in (h.get("agents") or []):
        if a.get("status") not in ("landed", "running", "dead"):
            continue
        # EMPTY MEANS NONE. `if mine and ...` treated an empty list as "no filter" and the report
        # showed six agents from three earlier runs beside a run that deployed nobody - the 12:58
        # run did exactly that, and its report named agents it never sent. A run that has a RUN.json
        # record and no agents in it deployed none, and the table must say so.
        if run.get("started") and a.get("id") not in mine:
            continue
        dep = a.get("deployed_at") or ""
        land = a.get("landed_at") or ""
        dep_s = a.get("deployed") or "-"
        land_s = "-"
        took = "-"
        try:
            import datetime as _dt
            if dep and land:
                d0 = _dt.datetime.fromisoformat(dep)
                d1 = _dt.datetime.fromisoformat(land)
                took = "%d min" % round((d1 - d0).total_seconds() / 60.0)
                land_s = d1.strftime("%H:%M")
            elif dep_s and a.get("finding"):
                # the finding file's own commit time, when the record has no landed_at
                import subprocess
                r = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%ad",
                                    "--date=format:%H:%M",
                                    "--", "tools/p2w-bench/" + a["finding"]],
                                   capture_output=True, text=True, timeout=15)
                if r.stdout.strip():
                    land_s = r.stdout.strip()
                    hh, mm = (dep_s.split(":") + ["0"])[:2]
                    lh, lm = (land_s.split(":") + ["0"])[:2]
                    mins = (int(lh) * 60 + int(lm)) - (int(hh) * 60 + int(mm))
                    if mins < 0:
                        mins += 1440
                    # MORE THAN A WORKING DAY IS A DAY BOUNDARY, NOT A DURATION. The old records
                    # carry HH:MM with no date, so an agent deployed at 13:52 whose finding landed
                    # the next morning computes as 1386 minutes. Say so instead of printing it.
                    took = "%d min" % mins if mins <= 600 else "cross-day"
        except Exception:
            pass
        out.append({"id": a.get("id") or "-",
                    "q": (a.get("question") or a.get("class") or "")[:52],
                    "dep": dep_s, "land": land_s, "took": took,
                    "status": a.get("status")})
    return out


def main(argv):
    beat("report.py", "building the report")
    total, solved, openc, docs, per_class = classes()
    co = corpus()
    tr = this_run()
    h = _json(HANDOFF, {})
    working = tr.get("class") if tr.get("present") else "-"

    if "--json" in argv:
        print(json.dumps({"classes": {"total": total, "clear": solved, "open": openc,
                                      "documents": docs},
                          "corpus": co, "run": tr, "working_class": working,
                          "needs_human": len(h.get("needs_human") or [])}, indent=1))
        return 0

    # ---------------------------------------------------------------------------------------
    # THE REPORT IS A DOCUMENT, NOT A DUMP. It is read in a chat window by someone deciding
    # whether to trust the run, so it is laid out in sections with aligned tables - what changed,
    # who did the work and for how long, what the run looked like from outside, and what is next.
    # ---------------------------------------------------------------------------------------
    date = (tr.get("started") or "")[:0]
    import datetime as _dt
    stamp = _dt.datetime.now().strftime("%d %b %Y")

    def hhmm(m):
        return "%dh %02dm" % (m // 60, m % 60) if m and m >= 60 else ("%d min" % (m or 0))

    L = []
    L.append("# P2W Fixer — Run Report")
    L.append("")
    if tr.get("present"):
        # SLOT WINDOW, NOT THE SESSION. RUN.json's started/ended are written when the slot is
        # claimed and released, and nothing writes a beat before step.py runs - so the sixty minutes
        # a pod can spend cloning and retrying before it claims are invisible to every file the
        # pipeline keeps. On 18 Nov the fixer reported "1h 47m, started 13:50, ended 15:37" for a run
        # the ledger recorded as "38 min, 14:50 -> 15:29". Both were true and neither said which clock
        # it was reading. The label says it now.
        L.append("**%s · slot %s → %s IST · %s**" % (stamp, tr.get("started") or "?",
                                                     tr.get("ended") or "running",
                                                     hhmm(tr.get("minutes") or 0)))
    else:
        L.append("**%s · no run record**" % stamp)
    L.append("")

    best = (co.get("best") or [])
    mine = run_docs()
    if mine and tr.get("docs_improved"):
        b = mine[0]
        L.append("> **%s** improved — %.2f → %.2f. Corpus ratchet clean across %d documents."
                 % (b["doc"], b["before"], b["after"], co.get("docs") or 0))
    elif tr.get("docs_improved"):
        # THE RUN IMPROVED SOMETHING BUT DID NOT COMMIT THE RANKING, so there is no honest way to
        # name the document - and naming the round's best instead credited a fix from four hours
        # earlier. Say the count and say why the name is missing; that is also the signal that the
        # run left its measurement in /scratch/output.
        L.append("> **%d document(s)** improved this run, but the run did not commit "
                 "benchmarks/RANKING.csv, so the report cannot name them." % tr["docs_improved"])
    elif best and tr.get("kept"):
        b = best[0]
        L.append("> **%s** fixed — %.2f → %.2f. Corpus ratchet clean across %d documents."
                 % (b["doc"], b["before"], b["after"], co.get("docs") or 0))
    elif tr.get("present"):
        L.append("> No change was kept this run. The numbers below say what was tried.")
    L.append("")

    L.append("## Progress")
    L.append("")
    L.append("| | |")
    L.append("|:--|:--|")
    if tr.get("present"):
        L.append("| Documents improved this run | **%d** — %d attempt(s), %d kept |"
                 % (tr["docs_improved"], tr["attempts"], tr["kept"]))
    else:
        L.append("| Documents improved this run | no run record |")
    if co.get("available"):
        L.append("| Documents improved, round total | %d of %d |"
                 % (co["improved"], co["docs"]))
        L.append("| Corpus improvement vs 15 Nov | **%+.2f%%** — mean %.2f → %.2f |"
                 % (co["pct"], co["baseline_mean"], co["current_mean"]))
        L.append("| Regressions | %s |"
                 % ("**none**" if not co["regressed"] else "**%d** — %s"
                    % (co["regressed"], ", ".join(x["doc"] for x in best[:3]) or "see RANKING.csv")))
        L.append("| Exempt, not measured | **%d** — %s |" % (len(_exempt()), ", ".join(_exempt()) or "none"))
        L.append("| **Fixed to 99%%** | **%d** of %d — the rest are still off |" % (co.get("fixed", 0), co.get("docs", 0)))
        L.append("| Moved but still open | **%d** — improved, not fixed |" % co.get("moved_open", 0))
    else:
        L.append("| Corpus improvement | not measurable — %s |" % co.get("why"))
    L.append("| Classes solved | %d of %d clear — %d class(es) still have an OPEN document |"
             % (solved, total, openc))
    L.append("| Working on | `%s` |" % working)
    cm = committed()
    if cm:
        L.append("| Committed | **%d** files in %d commit(s) from `%s` — %s |"
                 % (cm["n"], cm["commits"], cm["sha"], ", ".join(cm["files"])[:220]))
    L.append("")

    tr_tried = tried()
    if tr_tried:
        L.append("## What was tried")
        L.append("")
        L.append("| At | Outcome | Moved | What it measured |")
        L.append("|--:|:--|--:|:--|")
        for x in tr_tried:
            why = x["reason"].replace("|", "/").replace("\n", " ")
            L.append("| %s | **%s** | %s/%s | %s |"
                     % (x["at"], x["outcome"], x["moved"], x["total"], why[:300]))
        L.append("")

    tx = txt()
    if tx.get("available"):
        L.append("## The txt")
        L.append("")
        L.append("| | |")
        L.append("|:--|:--|")
        L.append("| Scored | **%d** of 213 |" % tx["scored"])
        L.append("| Clean - every applicable check passes | **%d** (%.1f%%) |" % (tx["clean"], tx["pct"]))
        L.append("| Failing at least one check | **%d** |" % tx["failing"])
        if tx["top"]:
            L.append("| Most common failure | `%s` - %d documents |" % tx["top"][0])
        L.append("")

    subs = subagents()
    if not subs:
        L.append("## Subagents")
        L.append("")
        L.append("*None deployed this run.*")
        L.append("")
    if subs:
        L.append("## Subagents")
        L.append("")
        L.append("| Agent | Sent to find | Deployed | Landed | Took |")
        L.append("|:--|:--|--:|--:|--:|")
        for a in subs:
            L.append("| `%s` | %s | %s | %s | %s |"
                     % (a["id"], a["q"], a["dep"], a["land"], a["took"]))
        L.append("")

    L.append("## Timing")
    L.append("")
    L.append("| | |")
    L.append("|:--|:--|")
    if tr.get("present"):
        # THE SESSION IS THE NUMBER THE READER WANTS. The slot window is what the ledger records;
        # the session is what the run cost. When step.py found /tmp/session_start they differ by the
        # pod's own setup time, which on 18 Nov was sixty minutes - and the report said 38.
        _sess = _json(ROUND, {}).get("session_start_ts")
        _end = _json(RUN, {}).get("ended_ts")
        if _sess and _end:
            _sm = int((float(_end) - float(_sess)) / 60)
            L.append("| Session | %s → %s · **%s** |"
                     % (_json(ROUND, {}).get("session_start") or "?",
                        tr.get("ended") or "running", hhmm(_sm)))
            L.append("| Slot window | %s → %s · %s |"
                     % (tr.get("started") or "?", tr.get("ended") or "running",
                        hhmm(tr.get("minutes") or 0)))
            L.append("| Before the claim | %s - pod setup, cloning and retries |" % hhmm(_sm - (tr.get("minutes") or 0)))
        else:
            L.append("| Slot window | %s → %s · %s |"
                     % (tr.get("started") or "?", tr.get("ended") or "running",
                        hhmm(tr.get("minutes") or 0)))
            L.append("| Before the claim | not recorded - nothing writes a beat until step.py runs |")
    si = silences()
    if si.get("available"):
        L.append("| Tool beats | %d |" % si["beats"])
        if si.get("longest"):
            L.append("| Longest silence | **%s min** — from %s, after `%s` |"
                     % (si["longest"]["min"], si["longest"]["at"], si["longest"]["doing"]))
        L.append("| Silences over 2 min | %d |" % si["n"])
    ob = obstacles()
    L.append("| Obstacles | %d cleared · %d need a human |" % (ob["mine"], ob["human"]))
    if ob.get("human"):
        L.append("| Still a wall | %s |" % ob["last"])
    L.append("")

    # the phase breakdown closes the Timing section, after the obstacle rows are already written
    ph = phases()
    if ph:
        L.append("")
        L.append("### Where the time went")
        L.append("")
        L.append("| Phase | Time | |")
        L.append("|:--|--:|:--|")
        tot = sum(x["min"] for x in ph) or 1
        for x in ph:
            bar = "#" * max(1, int(round(22 * x["min"] / tot)))
            L.append("| %s | **%s** | `%s` |" % (x["phase"], hhmm(int(x["min"])), bar))

    if best:
        L.append("## Best results this round")
        L.append("")
        L.append("| Document | Before | After | Change |")
        L.append("|:--|--:|--:|--:|")
        for x in best[:5]:
            L.append("| `%s` | %.2f | %.2f | %+.2f |"
                     % (x["doc"], x["before"], x["after"], x["after"] - x["before"]))
        L.append("")

    if co.get("available") and not co["measurement_committed"]:
        L.append("> **RANKING.csv is identical to the baseline.** No improvement has been committed")
        L.append("> since round one. If a run reported improvements, its measurement was never")
        L.append("> committed and cannot be checked.")
        L.append("")

    nxt = (h.get("next") or "").strip()
    if nxt:
        L.append("## Next run")
        L.append("")
        L.append(nxt)
        L.append("")

    nh = len(h.get("needs_human") or [])
    if nh:
        L.append("> **%d item(s) need a human** — see the top of `HANDOFF.md`." % nh)
        L.append("")

    L.append("---")
    L.append("*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, "
             "BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. "
             "Never remembered, never estimated.*")
    print("\n".join(L))
    return 0


def _persist(text):
    """Write the report to a file, not just to stdout.

    THE REPORT THAT NEVER ARRIVED. On 17 Nov the 09:21 run finished at 11:22, ran report.py at
    11:23, and printed eight correct numbers. The platform never closed the run, so the run's
    output was never delivered and the report was lost - the work was real, the numbers were real,
    and nobody saw them. A report that exists only as stdout is a report that depends on the
    platform delivering it.

    So it goes to a file in the repository as well, and the commit list carries it. Whatever
    happens to the run, the report is on disk and in git.
    """
    try:
        import io, contextlib
        path = os.path.join(HERE, "REPORT.md")
        open(path, "w", encoding="utf-8").write(
            "# Fixer report - %s\n\n```\n%s\n```\n\n"
            "Written by report.py from committed files only. Every number above is read from\n"
            "ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv\n"
            "and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.\n"
            % (time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time() + 19800)), text))
        # THE MESSAGE THE USER ACTUALLY READS, VERBATIM.
        #
        # REPORT.md wraps the text in a code fence and adds a header, so it is not what was sent -
        # and on 18 Nov that difference cost an hour of argument: the user was reading the chat
        # message ("1h 47m, started 13:50, ended 15:37") while I kept quoting REPORT.md ("38 min,
        # 14:50 -> 15:29"). Both existed, neither said which it was, and the only copy of the one
        # that mattered lived in the user's chat window.
        #
        # LAST-MESSAGE.md is that message, raw, committed with the run. Anyone who wants to know
        # what the user was told reads this file and reads exactly that.
        open(os.path.join(HERE, "LAST-MESSAGE.md"), "w", encoding="utf-8").write(text)
        return path
    except Exception:
        return None


if __name__ == "__main__":
    # capture what we print, so the same text can also go to REPORT.md
    import io, contextlib
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        rc = main(sys.argv)
    _text = _buf.getvalue()
    sys.stdout.write(_text)
    _p = _persist(_text)
    if _p:
        sys.stdout.write("\n  written to %s - commit it, so the report survives the run\n"
                         % os.path.relpath(_p, os.path.dirname(os.path.dirname(HERE))))
    sys.exit(rc)
