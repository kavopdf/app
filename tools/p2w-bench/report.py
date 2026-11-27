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
import csv, json, os, re, sys, time

# THE REPORT IS NOT WORK, AND IT MUST NOT BE COUNTED AS ANY. This is set BEFORE the helpers below
# are called, so the beats pending.py, chain.py and gaps.py write while building this report are
# not written at all - the count then cannot move between the report and lastmessage.py's re-read.
os.environ.setdefault("P2W_BEAT_QUIET", "1")

try:
    from beacon import beat
except Exception:
    def beat(*a, **k):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CLASSES  = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES-GOOGLE.md")
# THE REPORT READ THE OLD LIBREOFFICE TABLE AND CALLED IT THE CLASS LIST. benchmarks/
# DEFECT-CLASSES.md is one row per document from the round-one LibreOffice classification - six
# classes. benchmarks/DEFECT-CLASSES-GOOGLE.md is the capability table built from the Google
# renderer, one row per class - thirty-five of them. The user asked on 22 Nov why the report said
# "0 of 6" when the table has 35, and the answer was that the report was reading a different file
# from the one everything else works from.
RANK     = os.path.join(ROOT, "benchmarks", "RANKING.csv")
BASELINE = os.path.join(ROOT, "benchmarks", "RANKING-BASELINE.csv")
RUN      = os.path.join(HERE, "RUN.json")
ATTEMPTS = os.path.join(HERE, "ATTEMPTS.json")
ROUND    = os.path.join(HERE, "ROUND.json")
HANDOFF  = os.path.join(HERE, "HANDOFF.json")


# How many documents the :20 gverify cron pushes through a Google round trip in one run. It is a
# throughput, not a target: it belongs to that cron's prompt, so if the prompt changes this must
# change with it. Kept here so there is one place to correct, and used only to say how many runs
# the outstanding re-measurement is - never to claim anything was measured.
GVERIFY_PER_RUN = 60


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
    # THE GOOGLE CAPABILITY TABLE HAS ONE ROW PER CLASS, NOT ONE PER DOCUMENT:
    #
    #   | signature | problem | open | status | fixed-in-LO-only | libreoffice | google |
    #   | `32_stroke_lines` | 32_stroke_lines | 113 | OPEN | 112 | 1 | 113 |
    #
    # so `open` (cells[2]) is how many documents still fail that class, and a class is solved when it
    # reaches zero. There is no per-document status to decode here, which is why the old eight-cell
    # parser found six classes in a table of thirty-five.
    per_class = {}          # problem -> [open_count, fixed_count, never_broken]
    docs = 0
    try:
        for line in open(CLASSES, encoding="utf-8"):
            t = line.strip()
            if not t.startswith("| `"):
                continue
            cells = [c.strip() for c in t.strip("|").split("|")]
            if len(cells) < 4:
                continue
            problem = cells[1].strip("`")
            if not problem or problem.lower() == "none":
                continue
            try:
                open_n = int(cells[2])
            except Exception:
                continue
            docs += open_n
            per_class[problem] = [open_n, 0, 0]
    except Exception:
        pass
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


def _attempts_in_window(r):
    """How many attempt records ATTEMPTS.json holds inside this run's own window.

    The `at` field is IST wall-clock ("2026-11-24 08:18"); started_ts/ended_ts are epochs. Both are
    converted to IST before comparing, because a bare strftime here would compare UTC against IST and
    lose or gain 5h30m - the mistake that put an end before its own start at line 155.
    """
    try:
        st = float(r.get("started_ts") or 0)
        en = float(r.get("ended_ts") or 0)
    except Exception:
        return 0
    if not st:
        return 0
    if not en:
        en = time.time()
    lo, hi = st - 60, en + 60          # a minute either side: a run writes its own first record
    n = 0
    try:
        d = json.load(open(os.path.join(HERE, "ATTEMPTS.json"), encoding="utf-8"))
        for row in d.values():
            if not isinstance(row, dict):
                continue
            for x in (row.get("history") or []):
                at = str(x.get("at") or "")
                try:
                    ts = time.mktime(time.strptime(at, "%Y-%m-%d %H:%M")) - 19800
                except Exception:
                    continue
                if lo <= ts <= hi:
                    n += 1
    except Exception:
        return 0
    return n


def self_check():
    """Every number this report prints that TWO files also describe, compared. Disagreements are listed.

    THE REPORT HAS BEEN WRONG SIX TIMES IN ONE DAY AND ALWAYS THE SAME WAY: a field that two files describe,
    and the report silently reading one of them. corpus 212 vs 213 (RANKING.csv vs the gverify files); the slot
    clock (an IST string vs an epoch); "29 were clean there" (all engines vs the current one); the .txt table
    (16.8 h old, printed as current); attempts 0 vs 2 (RUN.json's counter vs ATTEMPTS.json's history).

    Each of those is invisible until the two sources happen to diverge, which is why the report looked right
    most runs and wrong on some. A person reading it cannot tell which. So the check is here, and its result
    is printed as a row: if two files disagree about something this report states, the report says so instead
    of picking one and sounding certain.

    Returns a list of (field, what one source says, what the other says).
    """
    out = []
    # google_fixed() RETURNS A 5-TUPLE, NOT A DICT. Written as g.get(...) every check below raised
    # AttributeError into its own try/except and reported nothing - five checks that were dead code and
    # looked like passing ones. Caught by planting a known-wrong value and watching for a report.
    try:
        _gf, _gs, _gfc, _gsc, _grf = google_fixed()
    except Exception:
        _gf = _gs = _gfc = _gsc = _grf = 0
    g = {"google_fixed": _gf, "google_scored": _gs, "google_fixed_current": _gfc,
         "google_scored_current": _gsc, "google_refused": _grf}
    # A DEPENDENCY THAT RAISES MUST NOT TAKE THE SELF-CHECK WITH IT. These two calls sat outside every
    # try, so a broken corpus() crashed self_check() and the report was never written at all - worse
    # than a check that stays silent, because the whole row disappears and nothing says why.
    try:
        t = txt() or {}
    except Exception as _e:
        t = {}
        out.append(("self-check", "txt() raised " + _e.__class__.__name__ + ": " + str(_e)[:60],
                    "the .txt checks did not run"))
    try:
        c = corpus() or {}
    except Exception as _e:
        c = {}
        out.append(("self-check", "corpus() raised " + _e.__class__.__name__ + ": " + str(_e)[:60],
                    "the corpus checks did not run"))

    # 1. corpus size: the gverify files against the ranking's own row count.
    try:
        import glob as _g
        _nv = len([x for x in _g.glob(os.path.join(HERE, "..", "..", "benchmarks",
                                                   "gverify", "*.json"))])
        _nr = c.get("docs")
        if _nr and _nv and int(_nr) != int(_nv):
            out.append(("corpus size", "ranking says %s" % _nr, "gverify has %s files" % _nv))
    except Exception as _e:
        out.append(("self-check", "the corpus size check raised " + _e.__class__.__name__ + ": " + str(_e)[:60], "it did not run, so it cannot vouch for anything"))

    # 2. attempts: RUN.json's counter against the history inside this run's window.
    try:
        _r = this_run()
        _counter = json.load(open(os.path.join(HERE, "RUN.json"), encoding="utf-8")).get("attempts", 0) or 0
        _hist = _attempts_in_window(json.load(open(os.path.join(HERE, "RUN.json"), encoding="utf-8")))
        if int(_counter) != int(_hist):
            out.append(("attempts", "RUN.json counter %s" % _counter,
                        "ATTEMPTS.json history %s" % _hist))
    except Exception as _e:
        out.append(("self-check", "the attempts check raised " + _e.__class__.__name__ + ": " + str(_e)[:60], "it did not run, so it cannot vouch for anything"))

    # 2b. A KEPT CHANGE IN GIT WITH NO KEPT RECORD IN THE LEDGER IS AN IMPROVEMENT NOBODY WILL FIND AGAIN.
    #
    # Measured 26 Nov on the 15:10 run: it landed aa496eb, moved the page-top gap from w:before into
    # w:pgMar w:top, and the Google renders went 42/47 -> 46/47 and 42/47 -> 45/47 - the first real
    # document movement in days. ATTEMPTS.json held no kept record for it at all: 18_displacement's
    # history for the whole day is lead/moved=0, and the class stands PARKED. The next run reads the
    # ledger, sees a parked class that never moved anything, and has no way to know the fix exists.
    #
    # The fix is not to write the ledger by hand - a number nobody can check is what this whole day was
    # about. The fix is to say the two sources disagree, every run, until someone records it properly.
    try:
        import subprocess as _sp2
        _rr0 = _json(RUN, {})
        _lo = float(_rr0.get("started_ts") or 0)
        if _lo:
            _lg = _sp2.run(["git", "log", "--since=@%d" % int(_lo), "--pretty=%s", "--no-merges"],
                           cwd=ROOT, capture_output=True, text=True, timeout=30)
            _book = ("state:", "report:", "claim", "release:", "gverify:", "attempt:", "baseline:",
                     "round:", "handoff:", "pending:", "classrow:", "measure:", "relay:", "corpus:")
            _code = [m for m in (_lg.stdout or "").splitlines()
                     if m.strip() and not m.strip().lower().startswith(_book)]
            _kept = 0
            try:
                _ap = json.load(open(os.path.join(HERE, "ATTEMPTS.json"), encoding="utf-8"))
                for _row in _ap.values():
                    if not isinstance(_row, dict):
                        continue
                    for _x in (_row.get("history") or []):
                        if _x.get("outcome") != "kept":
                            continue
                        try:
                            _ts = time.mktime(time.strptime(str(_x.get("at") or ""),
                                                            "%Y-%m-%d %H:%M")) - 19800
                        except Exception:
                            continue
                        if _ts >= _lo - 60:
                            _kept += 1
            except Exception:
                _kept = -1
            if _code and _kept == 0:
                out.append(("kept change", "%d code commit(s) in this window, first: %s"
                            % (len(_code), _code[0][:48]),
                            "ATTEMPTS.json has no kept record in the window - the next run will read the "
                            "class as parked and never find this change"))
    except Exception as _e:
        out.append(("self-check", "the kept-change check raised " + _e.__class__.__name__ + ": " + str(_e)[:60],
                    "it is not known whether a landed change was recorded"))

    # 3. the .txt table's own size against the corpus it claims to cover.
    try:
        _tr = t.get("scored")
        _cr = c.get("docs")
        if _tr and _cr and int(_tr) != int(_cr):
            out.append((".txt scored", "RANKING-TXT says %s" % _tr, "corpus says %s" % _cr))
    except Exception as _e:
        out.append(("self-check", "the txt scored check raised " + _e.__class__.__name__ + ": " + str(_e)[:60], "it did not run, so it cannot vouch for anything"))

    # 4. the .txt table's age. Not a disagreement, but a number that reads as current and is not.
    try:
        _a = t.get("age_h")
        if _a is not None and _a >= 6.0:
            out.append((".txt age", "measured %.1f h ago" % _a, "nothing re-measures it on a schedule"))
    except Exception as _e:
        out.append(("self-check", "the txt age check raised " + _e.__class__.__name__ + ": " + str(_e)[:60], "it did not run, so it cannot vouch for anything"))

    # 4b. THE RUN WINDOW AGAINST ITS OWN CLAIM. RUN.json is a whole file that a rebase can conflict on and
    # a merge can take from the remote side, which wipes the claim; round.py --claim-fixer then writes a
    # fresh started_ts and the header reads "1 min" for a run that worked for an hour and a half. Measured
    # 26 Nov: the 08:27 header said "1 min" over an 89-minute run with 21 beats, and only the prose below
    # the table said so. TIMELINE.jsonl is append-only and survives the merge, and it records the claim
    # itself, so the claim event - not a beat - is the second source. A beat is not used here because beats
    # from the run before this one also sit before the claim, and flagging those would be a false alarm.
    try:
        _rs = float(json.load(open(os.path.join(HERE, "RUN.json"), encoding="utf-8")).get("started_ts") or 0)
        _lc = _lr = None
        for _line in open(os.path.join(HERE, "TIMELINE.jsonl"), encoding="utf-8"):
            _line = _line.strip()
            if not _line:
                continue
            try:
                _row = json.loads(_line)
                _ev = _row.get("ev")
                _tv = float(_row.get("t") or 0)
            except Exception:
                continue
            if _ev == "claim":
                _lc = _tv
            elif _ev in ("release", "killed"):
                _lr = _tv
        if _rs and _lc and (_lr is None or _lc > _lr) and (_rs - _lc) > 600:
            out.append(("run window",
                        "RUN.json says this run began at %s" % time.strftime("%H:%M", time.gmtime(_rs + 19800)),
                        "TIMELINE.jsonl records the claim at %s, so the window was reset and the duration is short"
                        % time.strftime("%H:%M", time.gmtime(_lc + 19800))))
    except Exception as _e:
        out.append(("self-check", "the run window check raised " + _e.__class__.__name__ + ": " + str(_e)[:60], "it did not run, so it cannot vouch for anything"))

    # 5. clean counts: gverify's own count against the number the ranking table carries.
    try:
        _gc = g.get("google_fixed_current")
        _tc = c.get("clean")
        if _gc is not None and _tc is not None and int(_gc) != int(_tc):
            out.append(("clean count", "gverify says %s" % _gc, "ranking says %s" % _tc))
    except Exception as _e:
        out.append(("self-check", "the clean count check raised " + _e.__class__.__name__ + ": " + str(_e)[:60], "it did not run, so it cannot vouch for anything"))
    # 6. THE ARITHMETIC IDENTITIES. A report can lie without any second file disagreeing, by printing
    # three numbers that cannot all be true at once. Each of these is a sum that must close.
    try:
        _gf = g.get("google_fixed", 0) or 0
        _gfc = g.get("google_fixed_current", 0) or 0
        _gs = g.get("google_scored", 0) or 0
        _gsc = g.get("google_scored_current", 0) or 0
        if int(_gs) and int(_gsc):
            _older_clean = int(_gf) - int(_gfc)
            if _older_clean < 0:
                out.append(("clean split", "all-engine clean %s is less than current-engine clean %s"
                            % (_gf, _gfc), "the difference cannot be negative"))
            if int(_gsc) > int(_gs):
                out.append(("scored split", "current %s exceeds all %s" % (_gsc, _gs),
                            "a subset cannot be larger than its set"))
        if _gs and _gsc and int(_gsc) + (int(_gs) - int(_gsc)) != int(_gs):
            out.append(("scored total", "does not add up", "current + older must equal scored"))
        if int(_gfc) > int(_gsc):
            out.append(("clean vs scored", "clean %s exceeds scored %s" % (_gfc, _gsc),
                        "more documents cannot be clean than were scored"))
    except Exception as _e:
        out.append(("self-check", "the clean split check raised " + _e.__class__.__name__ + ": " + str(_e)[:60], "it did not run, so it cannot vouch for anything"))

    # 7. scored + refused must equal the corpus. 190 + 23 = 213 is the identity the report relies on.
    try:
        _docs = c.get("docs")
        _scored = g.get("google_scored")
        _refused = g.get("google_refused")
        if _docs and _scored is not None and _refused is not None:
            if int(_scored) + int(_refused) != int(_docs):
                out.append(("corpus identity", "scored %s + refused %s" % (_scored, _refused),
                            "does not equal the corpus %s" % _docs))
    except Exception as _e:
        out.append(("self-check", "the scored total check raised " + _e.__class__.__name__ + ": " + str(_e)[:60], "it did not run, so it cannot vouch for anything"))

    # 8. the .txt table's own arithmetic: clean + failing must equal scored.
    try:
        _ts, _tc, _tf = t.get("scored"), t.get("clean"), t.get("failing")
        if _ts and _tc is not None and _tf is not None:
            if int(_tc) + int(_tf) != int(_ts):
                out.append((".txt identity", "clean %s + failing %s" % (_tc, _tf),
                            "does not equal scored %s" % _ts))
    except Exception as _e:
        out.append(("self-check", "the clean vs scored check raised " + _e.__class__.__name__ + ": " + str(_e)[:60], "it did not run, so it cannot vouch for anything"))

    # 9. classes solved cannot exceed the class count, and the count must match the file the classes
    # come from. "0 of 34 clear" is a claim about 34 rows somewhere.
    try:
        _cl = classes() or {}
        _total = len(_cl) if isinstance(_cl, (list, dict)) else 0
        if _total:
            _open = sum(1 for _k, _v in (_cl.items() if isinstance(_cl, dict) else enumerate(_cl))
                        if (_v.get("open") if isinstance(_v, dict) else 0))
            if _open > _total:
                out.append(("classes", "%s open of %s" % (_open, _total),
                            "more open classes than classes"))
    except Exception as _e:
        out.append(("self-check", "the corpus identity check raised " + _e.__class__.__name__ + ": " + str(_e)[:60], "it did not run, so it cannot vouch for anything"))

    # 10. a subagent the run says it deployed should have left a FINDINGS file. An agent claimed and not
    # found is the same false-zero shape as attempts.
    try:
        _r = this_run()
        _claimed = _r.get("agents") or []
        if _claimed:
            _fd = os.path.join(HERE, "FINDINGS")
            _have = set(os.listdir(_fd)) if os.path.isdir(_fd) else set()
            _missing = []
            for _a in _claimed:
                # `agents` HOLDS STRINGS, NOT DICTS. RUN.json writes ["60_tB-02", "04_cA-01"], so
                # `_a.get("id")` raised AttributeError on every run with a subagent and the whole check
                # reported nothing but that error - the second time this block has hidden itself, the
                # first being an undefined name. A string is the id; a dict may carry one under id or
                # class; anything else is skipped rather than guessed.
                _id = (_a.strip() if isinstance(_a, str)
                       else str((_a or {}).get("id") or (_a or {}).get("class") or ""))
                if _id and not any(_id[:12] in _n for _n in _have):
                    _missing.append(_id[:16])
            if _missing:
                # SAY WHAT IS CHECKABLE, AND NOTHING ELSE. "no FINDINGS file for R-01" is true and
                # useless on its own: it cannot tell a reader whether the agent's work was lost or was
                # written up under a topic name, and those need different answers. Measured 26 Nov: two
                # agents deployed as R-01 and R-02, both landed, and the findings were written as
                # 18-displacement-PAGE-BREAK-IS-UNEARNED-26NOV-relay.md - real work, invisible to a
                # check that looks for the id in the filename.
                #
                # An earlier version of this message also counted how many files were written inside
                # the run window, using os.path.getmtime. That was removed: a git checkout resets
                # mtime, so the count would have said "nothing written this run" about a run that
                # wrote four findings - the same false-current shape as the .txt age row. The only
                # fact here that survives a checkout is the filenames themselves.
                out.append(("subagents", "%d deployed" % len(_claimed),
                            "no FINDINGS filename carries %s - the work may be on disk under a topic "
                            "name, and the next run cannot find it by id; rename it with the id first"
                            % ", ".join(_missing[:2])))
    except Exception as _e:
        # A CHECK THAT CANNOT RUN IS NOT A CHECK THAT PASSED. Every block above swallowed its own
        # exception, and that is exactly how five of these checks were dead code while looking live:
        # google_fixed() returns a tuple, g.get() raised, `except: pass` hid it. A self-check that
        # hides its own failures is worse than none, because it reports "every field agrees".
        out.append(("self-check", "the subagent check raised %s" % type(_e).__name__,
                    "it did not run, so it cannot vouch for anything"))
    return out


def this_run():
    r = _json(RUN, {})
    if not r.get("started"):
        return {"present": False}
    end = r.get("ended_ts") or time.time()
    mins = int((end - (r.get("started_ts") or end)) / 60)
    # THE CLOCK AND THE DURATION MUST AGREE. `ended` was passed through as a raw string written by
    # whoever closed the record, while `minutes` is computed from `ended_ts`. The 17:58 run printed
    # "17:58 -> 18:37 IST - 35 min": 17:58 to 18:37 is 39 minutes, so the two fields were reading
    # different clocks and the reader had no way to tell which was true. Derive the label from the
    # timestamp that the duration already uses, so a wrong `ended` cannot survive into a report.
    _end_label = r.get("ended")
    if r.get("ended_ts") and r.get("started_ts"):
        # IST, LIKE EVERY OTHER STAMP IN THIS FILE. time.localtime() is the sandbox's clock, which is
        # UTC, while `started` is written as IST - so deriving the label with localtime printed
        # "started 20:54, ended 17:13": an end before its own start, which is worse than the mismatch it
        # was meant to fix. 19800 s is the same +5:30 this file already uses at 370 and 662.
        _end_label = time.strftime("%H:%M", time.gmtime(r["ended_ts"] + 19800))
    return {"present": True, "started": r.get("started"), "ended": _end_label,
            "minutes": mins, "class": r.get("class") or "-",
            # ATTEMPTS FROM TWO PLACES, AND THE BIGGER ONE WINS. RUN.json carries an `attempts` counter
            # that the run is expected to bump; ATTEMPTS.json carries the per-class history that
            # attempt.py writes. On 24 Nov the 08:18 run recorded `60_text_column_right_edge -> lead` in
            # ATTEMPTS.json and left RUN.json at 0, so the report printed "0 attempt(s), 0 kept" over a
            # run that had made one. A zero that is not true is the worst kind: it reads as idle.
            # Counted from the history inside the run window, which is evidence rather than a counter
            # someone had to remember to increment.
            "attempts": max(r.get("attempts", 0) or 0, _attempts_in_window(r)),
            "kept": r.get("kept", 0),
            "docs_improved": r.get("docs_improved", 0),
            "agents": r.get("agents") or [], "obstacles_cleared": r.get("obstacles_cleared", 0),
            "needs_human": r.get("needs_human", 0)}



def engine_now():
    """The engine the corpus is built from right now - THE SAME QUANTITY THE STORE IS STAMPED WITH.

    THE STAMP IS NOT A COMMIT. Since 25 Nov the verdict store, RANKING.csv and the corpus stamp are
    keyed on `sha256(name+bytes of every app/.../engine/*.java)[:16]` - the same quantity as
    regress.py:engine_fingerprint() and corpus-convert.py:engine_sources(), and the id gvbatch.py
    writes into every verdict. This function still answered `git log -1 --format=%h -- engine/`, a
    git ABBREVIATION (8 chars, e.g. 85b8735f), and google_fixed() compared it with `==` against the
    16-char source hash in the store (981ff1fa35e2cf67). Two different quantities, two different
    lengths, so the comparison matched NOTHING and the report printed
    "could not be read - 0 of 212 scored were read as current" over 212 rows that were all current.
    Measured 25 Nov: the store held 212 scored rows, every one stamped 981ff1fa35e2cf67, which IS
    this tree's engine hash, and 42 of them clean.

    A COMMIT CANNOT BE THE KEY ANYWAY. It moves for a FINDINGS file or a claim, which cannot change a
    converted byte, and it cannot see an uncommitted engine edit. The source hash moves only when the
    engine changes.

    Falls back to the corpus stamp file, then to the commit abbreviation, so a pod without the engine
    sources still answers something instead of "".
    """
    import hashlib as _h
    d = os.path.join(ROOT, "app", "src", "main", "java", "com", "kavopdf", "app", "engine")
    # THE HASH HAS TO BE THE ONE THE STORE IS STAMPED WITH, AND THAT ONE LEAVES TxtWriter.java OUT.
    # regress.py:DOCX_EXCLUDES and corpus-convert.py:DOCX_EXCLUDES both skip it for the docx form -
    # the .txt writer cannot change a converted .docx byte - and `.stamp`, which gvbatch.py stamps
    # every Google verdict from, is written with that docx form. This function hashed EVERY .java, so
    # on 27 Nov the store held 212 rows stamped d28ca7516c3f9165 while this returned 74a152e7d3fb3d26:
    # `_same_engine` matched nothing and the report printed "could not be read - 0 of 212 scored were
    # read as current" over a store that was entirely current, and check_instances() printed
    # "0 of 0 (0.0%) on 0 documents" from the same read. gverify.py:_engine_now() was corrected for
    # this exact one-file disagreement on 27 Nov; this is its twin, and two readers of one store must
    # answer the same quantity or one of them will always read zero.
    _DOCX_EXCLUDES = ("TxtWriter.java",)
    try:
        if os.path.isdir(d):
            _s = _h.sha256()
            for _n in sorted(os.listdir(d)):
                if not _n.endswith(".java"):
                    continue
                if _n in _DOCX_EXCLUDES:
                    continue
                _s.update(_n.encode())
                with open(os.path.join(d, _n), "rb") as _f:
                    _s.update(_f.read())
            return _s.hexdigest()[:16]
    except Exception:
        pass
    try:
        return (json.load(open("/scratch/work/p2w/.stamp", encoding="utf-8")).get("engine") or "")[:16]
    except Exception:
        pass
    import subprocess as _sp
    try:
        r = _sp.run(["git", "-C", ROOT, "log", "-1", "--format=%h", "--",
                     "app/src/main/java/com/kavopdf/app/engine/"],
                    capture_output=True, text=True, timeout=20)
        return (r.stdout or "").strip()
    except Exception:
        return ""


def _same_engine(stamp, now):
    """Is this row's engine stamp the engine in the tree?

    PREFIX-TOLERANT, because a git abbreviation's length is not stable - `--format=%h` prints 7 chars
    in a repository that has never needed 8, and gverify.py already compares this way for exactly
    that reason (its 22 Nov note: "an instrument that reports zero is not a quiet instrument, it is a
    wrong one, and it was one character away from being believed"). report.py compared with `==`,
    which is the same bug the store had already been fixed for.
    """
    _e, _n = (stamp or "").strip(), (now or "").strip()
    if not _e or not _n:
        return False
    return _e == _n or _n.startswith(_e) or _e.startswith(_n)


def check_instances():
    """(passed, total, documents) over the current engine - the unit of progress that moves first.

    THE REPORT ONLY COUNTED DOCUMENTS CLEAN, AND THAT CANNOT MOVE UNTIL A DOCUMENT LAST CHECK FALLS.
    A patch taking eighteen documents from -114 pt to -3 pt moves nothing by that count, reads as
    worthless, and gets reverted - which is what happened on 25 Nov: 70 findings on 18_displacement,
    0 documents moved, docx open 59 for four days.

    A check-instance is one document against one applicable check. It moves the moment the render
    improves, whatever else on that document still fails. Current engine only, so stale rows cannot
    inflate it.
    """
    import glob as _g
    try:
        now = engine_now()
    except Exception:
        now = ""
    p = f = n = 0
    for path in _g.glob(os.path.join(ROOT, "benchmarks", "gverify", "*.json")):
        try:
            j = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        if (j.get("engine") or "") != now:
            continue
        n += 1
        p += int(j.get("passed") or 0)
        f += len(j.get("failed") or [])
    return p, p + f, n


def google_fixed():
    """What GOOGLE calls fixed, and the denominator that is honest about which engine measured it.

    THE REPORT'S "Fixed to 99%" WAS A LIBREOFFICE CLAIM - it read share5 <= 1.0 from RANKING.csv, a
    soffice render, and LibreOffice draws constructs Google drops. Measured 20 Nov: the report said
    153 of 213 fixed while Google passed all 42 on 7 of the 192 it could measure. So Google is the
    headline and LibreOffice is shown beside it as the proxy.

    THE DENOMINATOR WAS MIXING ENGINES. gverify/ holds results from several engine versions - on
    23 Nov, 137 stamped 98be7c3c (the tree), 45 on 462353f, 8 on 462353f9 and 23 unstamped - and
    this counted all of them as one population. "28 of 190" then reads as 162 documents failing when
    53 of those 190 were measured on code that no longer exists and may pass or fail today.

    Returns (fixed_all, scored_all, fixed_current, scored_current). The current-engine pair is the
    one the report prints, because it is the only pair that describes the code in the tree.
    """
    import glob as _g
    now = engine_now()
    fixed = scored = fixed_cur = scored_cur = refused = 0
    for f in _g.glob(os.path.join(ROOT, "benchmarks", "gverify", "*.json")):
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if j.get("status") == "page_count_refused":
            # COUNTED, NOT SKIPPED. This used to `continue` without a word, and the effect was that
            # 23 of 213 documents - 11% of the corpus - were absent from every headline number the
            # report printed, with nothing anywhere saying so. They are absent because the page count
            # did not match, which is a DEFECT (the user's own words: "original pdf me kai me sirf 1
            # page hai jabki docs me 2 page hai"), so the skip hid exactly the failure it should have
            # been loudest about: 041122-Account_Opening_Form drew 14 pages for 9,
            # 05_round_company_seal_curved_text 2 for 1, 305_vaccination_certificate 2 for 1.
            #
            # Such a document cannot be compared line by line, so it still does not enter `scored` -
            # but the count comes back to the caller, which prints it as its own row.
            refused += 1
            continue
        scored += 1
        ok = not (j.get("failed") or [])
        if ok:
            fixed += 1
        if _same_engine(j.get("engine"), now):
            scored_cur += 1
            if ok:
                fixed_cur += 1
    return fixed, scored, fixed_cur, scored_cur, refused



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
        # BOTH RANKINGS. This looked only at benchmarks/RANKING.csv, so a run that worked the .txt
        # half - which commits RANKING-TXT.csv instead - always came back empty, and the report told
        # the user "the run did not commit benchmarks/RANKING.csv" while it had committed exactly the
        # right file. Found 20 Nov by asking what the report says about a .txt run.
        out = []
        # TAKE THE NEWER OF THE TWO, NOT THE FIRST. Looping and breaking on the first hit always chose
        # RANKING.csv, because it always has a commit - so a .txt run still reported the docx ranking and
        # said the wrong file was missing.
        out = []
        _best_when = -1.0
        for _path in ("benchmarks/RANKING.csv", "tools/p2w-bench/txt/RANKING-TXT.csv"):
            _r = _sp.run(["git", "-C", ROOT, "log", "-1", "--format=%H %ct", "--", _path],
                         capture_output=True, text=True, timeout=20).stdout.split()
            if len(_r) >= 2:
                try:
                    _w = float(_r[1])
                except ValueError:
                    continue
                if _w > _best_when:
                    _best_when = _w
                    out = _r + [_path]
        if len(out) < 2:
            return []
        sha, when = out[0], float(out[1])
        rank_path = out[2] if len(out) > 2 else "benchmarks/RANKING.csv"
        is_txt = "RANKING-TXT" in rank_path
        if hi and when > hi + 300:
            return []                       # committed after the run ended
        if when < lo - 300:
            return []                       # committed before the run started
        prev = _sp.run(["git", "-C", ROOT, "show", "%s^:%s" % (sha, rank_path)],
                       capture_output=True, text=True, timeout=20).stdout
        now = _sp.run(["git", "-C", ROOT, "show", "%s:%s" % (sha, rank_path)],
                      capture_output=True, text=True, timeout=20).stdout
        if not prev or not now:
            return []

        def _m(txt):
            d = {}
            for row in csv.DictReader(txt.splitlines()):
                try:
                    # the .txt table has no share5 - its measure is how many checks a document fails
                    d[row["document"]] = (float(row["failed"]) if is_txt
                                          else float(row["share5"]))
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
    # THE CORPUS AND THE COMPARED SET ARE NOT THE SAME NUMBER, AND SAYING "212" FOR BOTH IS A LIE
    # ABOUT THE CORPUS. `common` is the documents in the baseline AND in the current table: 416 was
    # exempt when the baseline was taken, so it is in one and not the other and the intersection is
    # 212. The corpus is 213. Every report for weeks printed "of 212" as the corpus total because
    # this field was the only one available, and the fixer then copied it into a sentence about the
    # corpus. Both numbers are reported now, each under the name that says what it counts.
    _gf, _gs, _gfc, _gsc, _grf = google_fixed()
    # THE CORPUS IS EVERY DOCUMENT THAT EXISTS, NOT EVERY ROW IN RANKING.csv. `len(c)` is the ranking
    # table, and 416_many_tiny_pages is exempt from the round-one baseline, so it is absent from the table
    # while still being a document. `len(c)` therefore printed 212 as "the corpus" while the corpus is
    # 213 - the exact lie the comment above warns about. The corpus is what gverify saw: scored plus
    # refused. Fall back to the table only when gverify has not run.
    corpus_total = (_gs + _grf) if (_gs + _grf) > 0 else len(c)
    return {"available": True, "docs": corpus_total, "compared": len(common),
                "google_fixed": _gf, "google_scored": _gs,
                  "google_fixed_current": _gfc, "google_scored_current": _gsc,
                "google_refused": _grf,
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
    # THE "can" COLUMN IS FOUND BY ITS HEADER, NOT BY ITS POSITION. This file carries more than
    # one table - a 6-column one with "can I fix it", and a 4-column one headed
    # "when | what | what was tried | what must change" - and the parser required 6 cells, so it
    # dropped every row of the second table without saying so. Measured on the committed
    # BLOCKERS.md: 28 rows, of which 6 have fewer than 6 cells and were silently skipped.
    #
    # The 06:51 run's report blamed this on "a row whose can column starts with no -", which is
    # not the mechanism: a row saying "no - ..." is counted as needing a human, not dropped. The
    # count came out 0 cleared / 0 human because the rows never reached the counter at all.
    rows = []
    try:
        can_at = 4                     # the 6-column table's position, kept as the default
        for line in open(path, encoding="utf-8"):
            if not line.startswith("| ") or line.startswith("|---"):
                continue
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if not c:
                continue
            head = c[0].lower()
            if head.startswith("time") or head == "when":
                can_at = -1                      # this table has no "can I fix it" column
                for i, h in enumerate(c):        # learn this table's own column order
                    if h.lower().startswith("can"):
                        can_at = i
                        break
                continue
            # A table with no "can" column still records a wall. A row that does not say it was
            # cleared was not cleared, so it counts as needing a human rather than vanishing.
            if can_at >= 0 and len(c) <= can_at:
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
            rows.append({"can": (c[can_at] if 0 <= can_at < len(c) else "no"),
                         "wall": c[2] if len(c) > 2 else ""})
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
        # A REPORT IS NOT WORK, AND COUNTING IT MAKES THE COUNT UNSETTLED.
        #
        # report.py marks the timeline on entry like every other tool, so the beat it writes
        # lands AFTER the count it just took. Every regeneration therefore sees one more beat
        # than the last, and lastmessage.py - which re-runs report.py to check the message
        # against it - compares a number that moved between the two calls. Measured 19 Nov: a
        # report that report.py itself had just written was REFUSED for "Tool beats 35" against
        # its own 36, and no report could be committed while the run was live. The beats that
        # count are the run's work; the reader's own footsteps are not.
        # AND THE FILTER ABOVE WAS NOT ENOUGH - THE CUTOFF IT NEEDED IS GONE, BECAUSE THE BEATS
        # ARE NO LONGER WRITTEN. Excluding report.py's own beat still left the count moving, because
        # report.py calls pending.py, chain.py and gaps.py while it builds and each of those beats
        # under its OWN name. Measured 24 Nov 19:51, three report.py runs on an idle repository:
        # "Tool beats 25", then 26, then 27 - so a report report.py had just written was refused
        # against its own next reading, and no report could be committed while the run was live.
        #
        # report.py now sets P2W_BEAT_QUIET before it calls anything, and beacon.beat() writes
        # nothing while it is set (see beacon.py). Nothing moves the count, so no cutoff is needed
        # and the number is the run's work rather than the reader's footsteps.

        def _work(r):
            d = str(r.get("d") or "")
            return not (d.startswith("report.py") or d.startswith("lastmessage.py"))
        beats = len([r for r in rows if _work(r)])
        gaps = []
        for k in range(len(rows) - 1):
            g = rows[k + 1].get("t", 0) - rows[k].get("t", 0)
            if g >= 120:
                gaps.append({"min": round(g / 60.0, 1), "at": rows[k].get("ist", ""),
                             "doing": (rows[k].get("d") or "")[:70]})
        gaps.sort(key=lambda x: -x["min"])
        return {"available": True, "beats": beats, "n": len(gaps),
                "longest": gaps[0] if gaps else None}
    except Exception:
        return {"available": False}


# THE KEYS ARE TOOL NAMES AND THE BEATS ARE PROSE, SO MOST OF THEM FELL THROUGH.
#
# Measured 26 Nov on the 12:16 run: 70 of its 186 beats landed in "other", and the phase table then
# showed 35 minutes as "not attributed to a tool" - a fifth of a three-hour run with no account. Every
# one of the 70 was a real beat, and every one was legible: "relay: re-scoring docx table (slice 1)",
# "relay: corpus build slice 2", "relay: pod-prep in slices", "relay: soffice gives no render". The
# classifier matched tool FILENAMES, and a run describing its work in its own words never used one.
#
# So the keys now carry the verbs the beats are written with. This is not whack-a-mole if the set is
# the run's real vocabulary rather than one run's: converting, building, scoring, rendering and
# preparing a pod are the five things a slot does, and each of them has one entry here.
PHASES = (
    ("setup",   ("claimed", "archive.py", "housekeeping", "gaps.py", "step.py",
                 "pod-prep", "install-gate", "reading", "inspecting", "sizing", "timing a")),
    ("screen",  ("screen.py",)),
    ("build",   ("build-engine", "building the engine", "compil", "corpus build",
                 "building corpus", "corpus-slice", "corpus 78")),
    ("measure", ("p2w.py", "measure", "ratchet", "gate.py", "convert", "census",
                 "re-scor", "scoring", "soffice", "render", "export", "upload")),
    ("record",  ("attempt.py", "handoff.py", "classrow.py", "pending.py", "round.py")),
    ("report",  ("report.py", "chain.py", "lastmessage.py")),
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
        # WHATEVER STILL FALLS THROUGH IS NAMED, NOT JUST COUNTED. A row that says "other - 35 min" and
        # stops there is the same shape as a number printed against a thing it does not describe: the
        # reader cannot tell whether the run was idle, working in a way the table has no word for, or
        # lying. Three real beat descriptions cost nothing and answer all three.
        _unclassified = []
        for k in range(len(rows)):
            if _phase_of(rows[k].get("d")) == "other":
                _d = (rows[k].get("d") or "").strip()
                if _d and _d not in _unclassified:
                    _unclassified.append(_d)
        out = []
        for key, label in named:
            if acc.get(key, 0) < 30:
                continue
            row = {"phase": label, "min": round(acc[key] / 60.0, 1)}
            if key == "other":
                row["examples"] = _unclassified[:3]
                row["unclassified_beats"] = len(_unclassified)
            out.append(row)
        return out
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
    path = os.path.join(HERE, "txt", "RANKING-TXT.csv")
    if not os.path.exists(path):
        path = os.path.join(HERE, "RANKING-TXT.csv")
    if not os.path.exists(path):
        return {"available": False}
    # THE .TXT NUMBERS ARE ONLY AS CURRENT AS THIS FILE, AND NOTHING RE-MEASURES IT ON A SCHEDULE.
    # txt_gate.py regenerates RANKING-TXT.csv and no cron calls it - step_txt.py and ratchet.py only PRINT
    # the command. So the table can be a day old and still be reported as "213 of 213 scored", which is
    # how a stalled half reads as a healthy one. Measured 24 Nov: written 23 Nov 09:56, reported as current.
    # THE AGE MUST COME FROM THE DATA, NOT FROM THE FILE. os.path.getmtime answers "when did this file
    # last get written to disk", and a git checkout, a rebase or a copy resets that to now while the
    # numbers inside stay hours old. Measured 26 Nov: STATE-TXT.json carried at="2026-11-26 11:20" (2.7 h
    # old) and the report printed "Measured 0 min ago", because a checkout had touched the file. That is
    # the same false-current failure this row exists to prevent, so `at` is read first and the mtime is
    # only the fallback. Both sides go through mktime against the same wall clock, so the sandbox's own
    # timezone cancels out and the IST stamp needs no offset constant.
    _txt_age_h = None
    try:
        _st = json.load(open(os.path.join(HERE, "txt", "STATE-TXT.json"), encoding="utf-8"))
        _at = str(_st.get("at") or "")[:16]
        if _at:
            _now_ist = time.gmtime(time.time() + 19800)
            _txt_age_h = max(0.0, (time.mktime(_now_ist)
                                   - time.mktime(time.strptime(_at, "%Y-%m-%d %H:%M"))) / 3600.0)
    except Exception:
        _txt_age_h = None
    if _txt_age_h is None:
        try:
            _txt_age_h = (time.time() - os.path.getmtime(path)) / 3600.0
        except Exception:
            _txt_age_h = None
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
    # HOW MANY .TXT IMPROVED, NOT JUST HOW MANY ARE CLEAN.
    # The user asked on 20 Nov why the report never says whether the .txt is moving. It did not: the
    # section gave the standing total and stopped, so 46 failing read the same on a run that fixed
    # three of them and a run that touched none. A number that cannot move cannot show progress.
    #
    # The comparison is against the committed table - the same reference the gate uses - so moved is
    # what this run actually changed, not a guess from a baseline three days old.
    moved = regressed = 0
    try:
        import subprocess as _sp
        _r = _sp.run(["git", "-C", ROOT, "show",
                     "HEAD:tools/p2w-bench/txt/RANKING-TXT.csv"],
                    capture_output=True, text=True, timeout=60)
        if _r.returncode == 0 and _r.stdout.strip():
            _before = {}
            for _b in csv.DictReader(_r.stdout.splitlines()):
                try:
                    _before[_b["document"]] = int(_b.get("failed") or 0)
                except (ValueError, KeyError):
                    continue
            for _row in rows:
                _was = _before.get(_row["doc"])
                if _was is None:
                    continue
                if _row["failed"] < _was:
                    moved += 1
                elif _row["failed"] > _was:
                    regressed += 1
    except Exception:
        pass
    return {"available": True, "scored": len(rows), "clean": len(clean),
            "failing": len(bad), "top": top,
            "moved": moved, "regressed": regressed,
            "pct": round(100.0 * len(clean) / len(rows), 1),
            "age_h": _txt_age_h}


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
    # RUN.json's "agents" is a list of RECORDS now (id, class, angle, question, status), not a list
    # of ids, and `set()` over dicts raises TypeError - report.py died with
    # "unhashable type: 'dict'" on 21 Nov, which took the number-checker out of lastmessage.py with
    # it, so every report that day was refused for a reason that had nothing to do with its numbers.
    # Read the id out of a record, and keep accepting a bare id.
    mine = set(a.get("id") if isinstance(a, dict) else a
               for a in (run.get("agents") or [])
               if (a.get("id") if isinstance(a, dict) else a))
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
                _secs = (d1 - d0).total_seconds()
                # TWO STAMPS IN THE SAME MINUTE IS NOT "THE AGENT DID NOTHING". deployed_at and
                # landed_at were both written by time.strftime (UTC) at the moment the record was
                # written, so 30 of 62 agent records carried identical values and every one of them
                # reported "0 min" - for agents whose findings were real. A zero now says the
                # recording cannot measure it, which is the truth, instead of claiming the agent was idle.
                if _secs <= 0:
                    # A LANDING BEFORE THE DEPLOY IS NOT A DURATION, IT IS TWO CLOCKS. Older records
                    # carry deployed_at from ist() and landed_at from time.strftime (UTC), so the
                    # landing reads 5h30 earlier than the deploy. Printing it invites the reader to
                    # believe an agent finished before it started, so the column says what is true:
                    # the recording cannot measure it.
                    took = "not recorded"
                    if d1 < d0:
                        land_s = "-"
                else:
                    took = "%d min" % round(_secs / 60.0)
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
    # A WINDOW RESET MUST NOT BLANK THE CLASS. Measured 26 Nov: three claims landed in one slot - baseline
    # at 15:07, a fixer at 15:10, another at 15:50 - and the last one reset RUN.json, so this_run() said
    # present=False and the row printed "Working on -" while RUN.json.class held 18_displacement the whole
    # time. The class is data on the run record; the window is a guess about which run the record belongs
    # to. Print the data and say the window is in doubt, rather than a dash over a field that has an answer.
    working = tr.get("class") if tr.get("present") else "-"
    if working in ("", "-", None):
        try:
            _rr = _json(RUN, {})
            if _rr.get("class"):
                working = "%s *(RUN.json began %s - the window was reset, so this may be another run's " \
                          "class)*" % (_rr["class"], _rr.get("started") or "?")
        except Exception:
            pass

    # WHICH CRON IS THIS REPORT FOR, AND THEREFORE WHICH SECTIONS BELONG IN IT.
    #
    # Only the fixer had a generator; the baseline, the classifier and the APK each wrote their own
    # message by hand, so every number in them was typed and nothing checked it. They all read the
    # same files report.py already reads, so they can all be generated - and a generated report has
    # no number in it that a run can get wrong.
    cron = "fixer"
    if "--for" in argv:
        i = argv.index("--for") + 1
        if i < len(argv):
            cron = argv[i].strip().lower()
    KEEP = {
        "baseline":   ("Progress", "The txt", "Timing", "Where the time went"),
        "classifier": ("Progress", "Timing", "Where the time went"),
        "fixer":      None,          # every section
        "apk":        ("Progress", "Timing"),
    }
    keep = KEEP.get(cron, None)

    if "--json" in argv:
        # EVERY SECTION THE MARKDOWN CARRIES IS IN THE JSON, so a checker can compare the two.
        # txt and subagents were computed and printed in the document and absent here, which meant
        # lastmessage.py had nothing to compare a .txt sentence or an agent's timings against - and
        # a number nobody can check is a number that drifts. The fixer's own report quoted the .txt
        # not at all and gave an agent's window as "16:22 -> 16:32" with nothing behind it.
        print(json.dumps({"classes": {"total": total, "clear": solved, "open": openc,
                                      "documents": docs},
                          "corpus": co, "run": tr, "working_class": working,
                          "txt": txt(), "subagents": subagents(),
                          "needs_human": len(h.get("needs_human") or [])}, indent=1))
        return 0

    # ---------------------------------------------------------------------------------------
    # THE REPORT IS A DOCUMENT, NOT A DUMP. It is read in a chat window by someone deciding
    # whether to trust the run, so it is laid out in sections with aligned tables - what changed,
    # who did the work and for how long, what the run looked like from outside, and what is next.
    # ---------------------------------------------------------------------------------------
    date = (tr.get("started") or "")[:0]
    import datetime as _dt
    # THE POD RUNS UTC AND EVERY OTHER STAMP IN THIS PIPELINE IS IST. `datetime.now()` therefore
    # dated a run that claimed at 03:53 IST on 20 Nov as "19 Nov", one line above a table whose
    # own date field is computed from started_ts + 19800 - two clocks in one report, which is the
    # defect SETTLED.md records twice. Same conversion as the date below it.
    stamp = _dt.datetime.fromtimestamp(time.time() + 19800).strftime("%d %b %Y")

    def hhmm(m):
        return "%dh %02dm" % (m // 60, m % 60) if m and m >= 60 else ("%d min" % (m or 0))

    L = []
    # THE TITLE NAMES THE CRON THAT WROTE IT. Four crons read these files; a baseline report headed
    # "P2W Fixer" is wrong in its first line, and the first line is the one a reader trusts.
    L.append("# P2W %s - Run Report" % {"baseline": "Baseline", "classifier": "Classifier",
                                        "fixer": "Fixer", "apk": "APK"}.get(cron, cron.title()))
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
    try:
        _cp, _ct, _cn = check_instances()
        _pct = (100.0 * _cp / _ct) if _ct else 0.0
        L.append("| Check-instances passing | **%d** of %d (%.1f%%) on %d documents |" % (_cp, _ct, _pct, _cn))
        L.append("| Check-instances still failing | **%d** |" % (_ct - _cp))
    except Exception:
        L.append("| Check-instances passing | could not be read |")
    # A KEPT ATTEMPT IS NOT A CLEAN DOCUMENT. 15 classes carry a kept attempt and 42 documents
    # are clean, while 171 still fail a check - the kept bar is max(2, 25% of the class), which is
    # progress WITHIN a class, and a document is clean only when all its checks pass. Printed
    # alone, either number misleads about how far the corpus has actually moved.
    try:
        _att = json.load(open(os.path.join(ROOT, "tools", "p2w-bench", "ATTEMPTS.json"), encoding="utf-8"))
        _ka = sum(1 for _v in (_att or {}).values() if "kept" in ((_v or {}).get("outcomes") or []))
        _gd = os.path.join(ROOT, "benchmarks", "gverify")
        _cl = 0
        for _n in os.listdir(_gd):
            if _n.endswith(".json") and not (json.load(open(os.path.join(_gd, _n), encoding="utf-8")).get("failed") or []):
                _cl += 1
        L.append("| Kept attempts vs documents clean | **%d** classes with a kept attempt, **%d** documents clean - a kept attempt is progress inside a class, not a finished document |" % (_ka, _cl))
        # THE PIXEL SCORE ANSWERS "DOES IT LOOK LIKE THE ORIGINAL", which no boolean check does.
        try:
            import csv as _csvmod
            _prow = [r for r in _csvmod.DictReader(open(os.path.join(ROOT, "benchmarks", "PIXEL-SCORES-112-DOCS.csv"), encoding="utf-8")) if (r.get("ssim_pct") or "").strip()]
            _p99 = sum(1 for r in _prow if float(r["ssim_pct"]) >= 99)
            _p95 = sum(1 for r in _prow if float(r["ssim_pct"]) >= 95)
            _pmed = sorted(float(r["ssim_pct"]) for r in _prow)[len(_prow) // 2] if _prow else 0
            L.append("| Visual match, Google render | **%d** at 99%%+ SSIM, **%d** at 95%%+, median %.1f%% over %d scored |" % (_p99, _p95, _pmed, len(_prow)))
        except Exception as _e:
            L.append("| Visual match, Google render | could not be read (%s) |" % type(_e).__name__)
    except Exception as _e:
        L.append("| Kept attempts vs documents clean | could not be read (%s) |" % type(_e).__name__)

        # Every other row counts boolean checks; a document can fail one check and still be a 99 %
        # visual match, which is the standard the product is judged on. 213 documents carry both
        # metrics from the Google render.
        try:
            _px = os.path.join(ROOT, "benchmarks", "PIXEL-SCORES-112-DOCS.csv")
            _prow = [r for r in _csv.DictReader(open(_px, encoding="utf-8")) if (r.get("ssim_pct") or "").strip()]
            _p99 = sum(1 for r in _prow if float(r["ssim_pct"]) >= 99)
            _p95 = sum(1 for r in _prow if float(r["ssim_pct"]) >= 95)
            _pmed = sorted(float(r["ssim_pct"]) for r in _prow)[len(_prow) // 2] if _prow else 0
            L.append("| Visual match, Google render | **%d** at 99%%+ SSIM, **%d** at 95%%+, median %.1f%% over %d scored |" % (_p99, _p95, _pmed, len(_prow)))
        except Exception as _e:
            L.append("| Visual match, Google render | could not be read (%s) |" % type(_e).__name__)
    L.append("| | |")
    L.append("|:--|:--|")
    if tr.get("present"):
        # A SUM IS NOT A COUNT OF DOCUMENTS. RUN.json accumulates `docs_improved` as the sum of every
        # attempt's --moved, so three documents improved twice read as six. On 22 Nov that printed
        # "19" when the distinct documents that changed were 16 - the first attempt's three are inside
        # the second attempt's sixteen. The label now says what the number is, and the note below the
        # table still gives the distinct figure where the run recorded it.
        # THE REPORT OWN CROSS-CHECK, BEFORE ANY NUMBER IT PRINTS. Six fields have been wrong in one day and
        # every one was a number two files describe. Printed here so a disagreement is visible instead of being
        # silently resolved in favour of whichever file the code happened to read.
        _sc = self_check()
        if _sc:
            L.append("| **Self-check** | **%d disagreement(s)** - %s |" % (
                len(_sc), "; ".join("%s: %s vs %s" % (f, a, b) for f, a, b in _sc[:3])))
        else:
            L.append("| Self-check | **every field agrees with its second source** |")
        L.append("| Document-moves this run | **%d** — %d attempt(s), %d kept (a sum: a document moved "
                 "twice counts twice) |"
                 % (tr["docs_improved"], tr["attempts"], tr["kept"]))
    else:
        L.append("| Documents improved this run | no run record |")
    if co.get("available"):
        # "61 OF 213" MIXED TWO DENOMINATORS. improved is counted over `common` - the documents in BOTH
        # the baseline table and the current one, which is 212, because one document was exempt when the
        # baseline was taken. Printing it over the corpus total (213) put a 212-based numerator on a
        # 213-based denominator, and the user caught it on 22 Nov. Both numbers are true and they are not
        # the same number, so each is printed under the name that says what it counts.
        L.append("| Documents improved, round total | **%d** of the %d compared (corpus %d) |"
                 % (co["improved"], co.get("compared") or co["docs"], co["docs"]))
        L.append("| Corpus improvement vs 15 Nov | **%+.2f%%** — mean %.2f → %.2f |"
                 % (co["pct"], co["baseline_mean"], co["current_mean"]))
        L.append("| Regressions | %s |"
                 % ("**none**" if not co["regressed"] else "**%d** — %s"
                    % (co["regressed"], ", ".join(x["doc"] for x in best[:3]) or "see RANKING.csv")))
        # "Not measured" was true of one population and false of the other: this document is exempt
        # from the LibreOffice comparison (212 of the 213) and IS in the Google population (190 of
        # 213). Said without the qualifier, the row contradicted the Google row two lines below it -
        # one line calling the document unmeasured, the next counting it. The user's rule is that the
        # corpus total must be the same number everywhere; when it cannot be, each number must say
        # which population it counts.
        L.append("| Exempt from the LibreOffice comparison | **%d** — %s |" % (len(_exempt()), ", ".join(_exempt()) or "none"))
        # GOOGLE FIRST. The user's rule: a document is fixed when it matches the original in
        # Google's render at 99% or better. The LibreOffice count is a proxy and is labelled as one,
        # because LibreOffice draws what Google drops and 32-vs-7 on the same corpus is not a rounding
        # difference - it is two different products.
        # "of the N documents both renderers measured", not "of N": the Google table is the
        # intersection of the two render sets and is smaller than the corpus, and lastmessage.py
        # reads any bare "of NNN" in the hundreds as a claim about the corpus size and refuses the
        # report. The two numbers are both right and the sentence has to say which is which.
        # THE DENOMINATOR NOW SAYS WHICH ENGINE MEASURED IT. gverify/ holds results from several
        # engine versions - on 23 Nov, 137 stamped 98be7c3c (the tree), 45 on 462353f, 8 on 462353f9 and
        # 23 unstamped - and "28 of 190" counted all of them as one population. 53 of those 190 were
        # measured on code that no longer exists, so the sentence read as 162 documents failing when the
        # honest population is the 135 measured on the engine in the tree. The full pair is still shown
        # beside it so nothing is hidden.
        # A ZERO WITH NO OWNER IS NOT A NUMBER, IT IS A SHRUG.
        #
        # This row read "0, out of the 2 measured on THIS engine (all engines: 30 of 190)". Every
        # word true, and the sentence still misled: 0 of 2 reads as total failure when what it says
        # is that 188 documents have not been re-measured since the engine changed, and nothing in
        # the report said whether anything ever would. The user: "agar napa nhi gya toh usko kaun
        # napega har zero dikhana aur yeh bolna napa nhi gya yeh sahi nhi hai".
        #
        # The row now states the verified count, the gap, and the gap's owner in one line.
        _gfc = co.get("google_fixed_current", 0)
        _gsc = co.get("google_scored_current", 0)
        _gs = co.get("google_scored", 0)
        _to_go = max(0, _gs - _gsc)
        # A TRANSIENT FAILURE IS NOT A ZERO. google_fixed() raised once on 24 Nov and the except
        # above turned it into "0 of the 0 re-measured ... 190 of the 190 scored are still on an
        # older engine" - a confident sentence with a denominator of zero, when the store held 186
        # of 190 current. Zero current out of N scored is a failed read, not a measurement.
        if _gsc == 0 and _gs > 0:
            L.append("| **Fixed - Google, every applicable check** | **could not be read** - 0 of %d "
                     "scored were read as current, which is a failed read and not a measurement. "
                     "No count is stated rather than a zero |" % _gs)
            L.append("| Who re-measures them | the **:20 gverify** cron, once the read works |")
            _to_go = 0   # A FAILED READ CANNOT PRODUCE A QUEUE. The 09:59 report stated "about 4 runs
            # for the 212 outstanding" from the same read that could not say how many were fixed. If the
            # instrument could not count what was done, it cannot count what is left; a reader takes the
            # queue as a measurement because it is formatted like one.
        else:
            L.append("| **Fixed - Google, every applicable check** | **%d** of the **%d** re-measured on this "
                     "engine - **%d** of the %d scored are still on an older engine, and **%d** of those "
                     "were clean on the engine they were measured with |"
                     % (_gfc, _gsc, _to_go, _gs, max(0, co.get("google_fixed", 0) - _gfc)))
        if _to_go:
            L.append("| Who re-measures them | the **:20 gverify** cron, up to %d documents a run "
                     "- about **%d** run(s) for the %d outstanding. Until then \"fixed\" means "
                     "fixed on an engine that is not this one |"
                     % (GVERIFY_PER_RUN, -(-_to_go // GVERIFY_PER_RUN), _to_go))
        # SAME MIXED DENOMINATOR. `fixed` is also counted over `common` (212), not the corpus (213).
        L.append("| Fixed - LibreOffice proxy | %d of the %d compared - a renderer the user does not open |"
                 % (co.get("fixed", 0), co.get("compared") or co.get("docs", 0)))
        # THE DOCUMENTS THE HEADLINE CANNOT SCORE, SAID OUT LOUD. These are excluded from
        # every number above because the page count did not match, and a page count that does
        # not match is a defect, not a pass. Skipping them silently made 11% of the corpus
        # invisible and made the headline read better than the corpus is.
        if co.get("google_refused"):
            # The denominator is the population gverify actually saw - scored plus refused - and not
            # `docs`, which is the LibreOffice-compared corpus (212, one document exempt). Using 212
            # would pair a Google count with a LibreOffice total, which is the mixed denominator this
            # function was rewritten to stop.
            _seen = (co.get("google_scored") or 0) + (co.get("google_refused") or 0)
            L.append("| Not scored - page count did not match | **%d** of the %d gverify saw - a "
                     "document that drew the wrong number of pages cannot be compared line by line, "
                     "and it is a defect, not a pass |"
                     % (co.get("google_refused", 0), _seen))
        L.append("| Moved but still open | **%d** — improved, not fixed |" % co.get("moved_open", 0))
    else:
        L.append("| Corpus improvement | not measurable — %s |" % co.get("why"))
    L.append("| Classes solved | %d of %d clear — %d class(es) still have an OPEN document |"
             % (solved, total, openc))
    # A CLASS NAME IN THIS ROW DOES NOT MEAN A CLASS WAS TAKEN. On 24 Nov the report said "Working on
    # 18_displacement" while 22 pending items were open, which reads as the gate being bypassed. It was
    # not: pending.py's item 1 IS an 18_displacement question, so the run took the pending item and the
    # row lost the distinction. Say which it was, because the difference is the whole gate.
    # AND IF IT CANNOT BE READ, SAY SO. The first version fell back to _pend = 0 on any exception,
    # which silently printed the old wording - and that is what happened: the 11:54 report HAS this
    # code and still showed no note, so pending.py failed in that environment and the fallback hid it.
    # A fallback that looks exactly like success is the fault this whole day was about.
    _pend, _why = None, ''
    try:
        import subprocess as _sp
        _r = _sp.run([sys.executable, os.path.join(HERE, 'pending.py')],
                     capture_output=True, text=True, timeout=120)
        _m = re.search(r'PENDING \((\d+)\)', _r.stdout or '')
        if _m:
            _pend = int(_m.group(1))
        else:
            _why = 'pending.py printed no PENDING line (exit %d)' % _r.returncode
    except Exception as _e:
        _why = 'pending.py could not be run (%s)' % type(_e).__name__
    if _pend:
        _note = ' - taken from the pending list (%d still open), not a new class' % _pend
    elif _pend == 0:
        _note = ' - the pending list is empty, so this is a new class'
    else:
        _note = ' - **the pending list could not be read**: %s' % _why
    L.append('| Working on | `%s`%s |' % (working, _note))
    # INVESTIGATING IS CHEAPER THAN LANDING, SO IT HAPPENS INSTEAD. 32_stroke_lines has 26
    # findings files and 2 documents still failing it. That is not laziness - writing a finding is
    # one commit and cannot regress anything, while a change must survive the gate and a 54-minute
    # restamp. Nothing in the report said so, so the imbalance was invisible.
    #
    # Counted from the findings filenames, which carry the class name, so this needs no mapping
    # between the attempt ledger and the capability table. Report only: it names the imbalance and
    # leaves the decision to the run.
    _fn, _mv = 0, 0
    try:
        import glob as _g, os as _o, json as _j
        _fd = _o.path.join(HERE, 'FINDINGS')
        _key = str(working).split()[0] if working else ''
        if _key and len(_key) >= 5 and _key not in ('-', 'none', 'None'):
            _fn = len([x for x in _g.glob(_o.path.join(_fd, '*.md')) if _key in _o.path.basename(x)])
            _at = _j.load(open(_o.path.join(HERE, 'ATTEMPTS.json'), encoding='utf-8'))
            _mv = sum(int(h.get('moved') or 0) for h in ((_at.get(_key) or {}).get('history') or []))
    except Exception:
        _fn, _mv = 0, 0
    if _fn >= 10 and _mv <= 1:
    # 18_displacement measured 24 Nov: 64 findings files and 1 document moved. 32_stroke_lines has
    # 24 findings and 33 moved - it landed its changes. The ratio is what separates the two.
        L.append('| Findings vs landing | **%d** finding(s) on this class and **0** documents moved - '
                 'writing is cheaper than landing, and nothing else says so |' % _fn)
    # A RUN THAT PICKS A DEMOTED CLASS BY HAND IS INVISIBLE IN ITS OWN REPORT.
    # Measured 24 Nov: the rotation's first five classes were attempted zero times while the run
    # hand-picked 04_chars_missing (4 attempts, nothing moved) and 60_text_column_right_edge (5,
    # nothing moved). The report said 'Working on 04_chars_missing' and nothing said the rotation
    # disagreed. This does not block the run - a gate that waits for agreement never opens - it makes
    # the disagreement readable in the one place a person looks.
    _rot = ''
    try:
        import classpick as _cp
        _rk = _cp.ranking()
        _rot = str((_rk[0][0] if isinstance(_rk[0], (list, tuple)) else _rk[0]) or '') if _rk else ''
    except Exception:
        _rot = ''
    if _rot and working and _rot.split()[0][:20] not in str(working):
        L.append('| The rotation says | `%s` - the run chose `%s` by hand instead |' % (_rot, working))
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

    # WHY NOTHING MOVED, IN THE FIXER'S OWN WORDS.
    #
    # Every other row in this report is a number checked against a second file. This one is not, and it
    # cannot be: it asks what the run believes, which no ledger holds. So it carries NO NUMBERS - the
    # numbers are in the tables above and they are checked - and it is written by the run itself into
    # /tmp/why-nothing-moved.md before the report is produced.
    #
    # It exists because the honest reading of most runs is "nothing moved", and a table cannot say why.
    # A reader who sees no document move needs to know whether that is the class being hard, the gate
    # refusing, the measurement not fitting, or the run not understanding its own blocker - four
    # different problems with four different answers, and they look identical in every other section.
    #
    # An absent file is printed as a gap rather than skipped. A section that silently disappears is how
    # a report starts looking complete while missing the one thing that explains it.
    _why = "/tmp/why-nothing-moved.md"
    _wt = ""          # defined for every branch: the comparison below reads it even when the file is absent
    L.append("## Why nothing moved, in this run's own words")
    L.append("")
    if os.path.exists(_why):
        try:
            _wt = open(_why, encoding="utf-8").read().strip()
        except Exception as _e:
            _wt = ""
            L.append("*(the file exists but could not be read: %s)*" % type(_e).__name__)
            L.append("")
        if _wt:
            # Indented as a quote so a reader can tell the run's own reasoning from the checked tables
            # above it. Nothing here is validated: it is the run's account, and it is labelled as one.
            for _ln in _wt.splitlines():
                L.append(("> " + _ln) if _ln.strip() else ">")
            L.append("")
    else:
        L.append("*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so "
                 "the only answer to \"why did nothing move\" is the table above - and a table of "
                 "attempts is not a diagnosis. That absence is itself the finding.)*")
        L.append("")

    # THE RUN BEFORE THIS ONE, BESIDE IT. One account of "why nothing moved" cannot be told apart from a
    # well-written story: an account that reads like thinking and one that is thinking are the same
    # twenty lines of prose. Two accounts can be. If this run and the last name the same blocker and
    # neither moved a document, the run is repeating itself, and that is a fact about the pair rather
    # than an opinion about either.
    #
    # Read from git, not from a new file: the previous run's section is exactly what it published, in the
    # LAST-MESSAGE.md it committed. Nothing is written here, so a report can be re-run as often as a run
    # likes without changing the tree and tripping the claim gate.
    try:
        import subprocess as _sp
        _prev = ""
        try:
            _raw = _sp.run(["git", "show", "HEAD:tools/p2w-bench/LAST-MESSAGE.md"], cwd=HERE,
                           capture_output=True, text=True, timeout=20)
            if _raw.returncode == 0 and _raw.stdout:
                # THE HEADING MOVES WITH THE RUN, THE SECTION DOES NOT. "Why nothing moved" is right for a
                # run that moved nothing; the 15:10 run landed a real fix and wrote "What happened, in this
                # run's own words" instead, which is a better heading and would have made this comparison
                # silently find nothing. Match the invariant part - "in this run's own words" - and fall
                # back to the older wording, so a run that renames its section is still compared.
                _sec = _raw.stdout.split("in this run's own words", 1)
                if len(_sec) == 1:
                    _sec = _raw.stdout.split("## Why nothing moved", 1)
                if len(_sec) == 2:
                    _body = _sec[1]
                    _cut = _body.find("\n## ")
                    _body = _body[:_cut] if _cut != -1 else _body
                    # drop whatever is left of the heading line itself
                    _body = _body.split("\n", 1)[1] if "\n" in _body else ""
                    _prev = _body.strip()
        except Exception:
            _prev = ""
        # A SELF-COMPARISON, HOWEVER MANY TIMES IT HAS BEEN EMBEDDED. Exact equality is not enough:
        # once the section has embedded itself, the previous body CONTAINS this run's account rather
        # than equalling it. So the test is containment of a window of the current text.
        if _prev and _wt and _wt.strip()[:60] and _wt.strip()[:60] in _prev:
            _prev = ""
        if _prev and _prev.strip() == (_wt or "").strip():
            # THE PREVIOUS MESSAGE IS THIS RUN'S OWN. A run that commits its report and then re-runs
            # report.py (to pick up an agent's landing time, or to fix a number) makes HEAD its own
            # message, so the "run before this one" is this one. Left unguarded the section compares
            # the run to itself, then embeds it, then the next regeneration embeds the embedding - on
            # 26 Nov a report reached 22 KB with the same account pasted three times. An identical
            # body is not a previous run, so there is nothing to put beside this one.
            _prev = ""
        if _prev:
            L.append("### The run before this one said")
            L.append("")
            for _ln in _prev.splitlines():
                _ln = _ln.strip()
                if _ln.startswith(">"):
                    _ln = _ln.lstrip(">").strip()
                if _ln.startswith("*(") or _ln.startswith("###"):
                    continue
                L.append(("> " + _ln) if _ln else ">")
            L.append("")
            # A WORD-OVERLAP SCORE, NOT A VERDICT. Content words of five letters or more, lowercased, and
            # the share the two accounts have in common. It is a number, so it is computed rather than
            # written, and the threshold is printed with it so a reader can disagree with the cut.
            def _words(t):
                return set(w for w in re.findall(r"[a-z]{5,}", t.lower()))
            _a, _b = _words(_wt or ""), _words(_prev)
            if _a and _b:
                _j = len(_a & _b) / float(len(_a | _b))
                L.append("Accounts share %.0f%% of their significant words - %s (the cut is 50%%)."
                         % (_j * 100, "**the same blocker, named twice**" if _j >= 0.50
                            else "a different account"))
                L.append("")
    except Exception as _e:
        L.append("*(the previous run's account could not be read: %s)*" % type(_e).__name__)
        L.append("")

    tx = txt()
    if tx.get("available"):
        L.append("## The txt")
        L.append("")
        L.append("| | |")
        L.append("|:--|:--|")
        # HOW OLD THESE NUMBERS ARE, BEFORE THE NUMBERS. Nothing re-measures RANKING-TXT.csv on a
        # schedule: txt_gate.py regenerates it and only step_txt.py prints the command. On 24 Nov the
        # file was 16.7 h old and the table still read "213 of 213 scored", which is a stalled half
        # reading as a healthy one. The age goes first so a stale table cannot look current.
        if tx.get("age_h") is not None:
            _a = tx["age_h"]
            L.append("| Measured | **%s ago**%s |" % (
                ("%.1f h" % _a) if _a >= 1 else ("%d min" % int(_a * 60)),
                "" if _a < 6 else " - nothing re-measures this on a schedule; run "
                "`txt_gate.py --score 60`" if _a >= 6 else ""))
        L.append("| Scored | **%d** of 213 |" % tx["scored"])
        L.append("| Clean - every applicable check passes | **%d** (%.1f%%) |" % (tx["clean"], tx["pct"]))
        L.append("| Failing at least one check | **%d** |" % tx["failing"])
        # THE LINE THE USER ASKED FOR: is the .txt moving, not just how many are clean.
        if tx.get("moved") or tx.get("regressed"):
            L.append("| Moved since the last commit | **%d** improved, %d worse |"
                     % (tx["moved"], tx["regressed"]))
        else:
            L.append("| Moved since the last commit | **none** - nothing changed |")
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
        # A SESSION CANNOT START AFTER IT ENDED, AND WHEN IT SAYS IT DID THE FIELD IS STALE.
        # ROUND.json survives the run that wrote it; session_start_ts is written once at the top of
        # a run and not cleared, so by the time this reads it it can belong to a LATER run than the
        # RUN.json beside it. Measured 19 Nov: the report printed "Session 18:00 -> 17:00 · 23h 00m"
        # and "Before the claim 22h 12m" for a run that lasted 48 minutes. Both numbers were
        # arithmetically right and both were nonsense. Skipping the line is the honest answer: a
        # session figure nobody can trust is worse than no session figure.
        # A SESSION IS THE SLOT PLUS THE POD'S SETUP, AND NOTHING ELSE. The pod can spend an hour
        # cloning and retrying before step.py writes the first beat; it cannot spend twenty-three.
        # Measured 19 Nov: the report printed "Session 18:00 -> 17:00 · 23h 00m" - the field held
        # the PREVIOUS day's 18:00, so it was earlier in epoch than the end, passed a naive
        # before-the-end test, and produced a duration of 23 hours for a run that lasted 48 minutes.
        # The bound is the slot plus three hours: generous for setup, and far short of a day.
        _slot = (float(_end) - float(_json(RUN, {}).get("started_ts") or _end)) if _end else 0
        _ok = (_sess and _end and float(_sess) < float(_end)
               and (float(_end) - float(_sess)) <= max(_slot, 3600) + 3 * 3600)
        if _ok:
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
            L.append("| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |")
    si = silences()
    if si.get("available"):
        L.append("| Tool beats | %d |" % si["beats"])
        if si.get("longest"):
            L.append("| Longest silence | **%s min** — from %s, after `%s` |"
                     % (si["longest"]["min"], si["longest"]["at"], si["longest"]["doing"]))
        L.append("| Silences over 2 min | %d |" % si["n"])
    ob = obstacles()
    L.append("| Obstacles | %d cleared · %d parked, with the evidence to re-open them |" % (ob["mine"], ob["human"]))
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
        for x in ph:
            if x.get("examples"):
                L.append("")
                L.append("The unattributed row is %d distinct beat(s) that matched no phase. They said:"
                         % x.get("unclassified_beats", 0))
                L.append("")
                for _e in x["examples"]:
                    L.append("- `%s`" % _e[:110])

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
        L.append("> **%d item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`." % nh)
        L.append("")

    L.append("---")
    L.append("*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, "
             "BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. "
             "Never remembered, never estimated.*")
    if keep is not None:
        out, on = [], False
        for line in L:
            if line.startswith("## "):
                on = line[3:].strip() in keep
            if on or not line.startswith("## "):
                if on or line.startswith("# ") or line.strip() == "" or line.startswith("**"):
                    out.append(line)
        # keep the title and the header, drop everything the cron does not need
        L = [x for x in out if x.startswith("# ") or x.startswith("**") or x.startswith("## ")
             or not x.strip() or True]
    print("\n".join(L))
    return 0


def _report_stamp():
    """The run's own start, not the wall clock, so the same run produces the same file for ever.

    The header used time.time(), so REPORT.md written at 17:19:59 and 17:20:01 carried different
    timestamps for identical content - which makes two files impossible to compare byte for byte and
    turns every reproducibility check into a diff of clock digits. A report describes a run; the run
    has a start, and that is the only time it should carry.
    """
    try:
        run = _json(RUN, {})
        ts = run.get("started_ts")
        if ts:
            return time.strftime("%Y-%m-%d %H:%M", time.gmtime(float(ts) + 19800))
    except Exception:
        pass
    return "unknown run"


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
            % (_report_stamp(), text))
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
    # --json IS FOR A MACHINE AND MUST BE PURE JSON. `_persist` writes REPORT.md and then announces
    # it on stdout, so `report.py --json | python3 -c "json.load(sys.stdin)"` failed with "Extra
    # data" - every consumer of the JSON had to know to strip a trailing sentence. A checker that
    # parses this output is the thing that keeps the report honest, so it must not need a workaround.
    _p = None if "--json" in sys.argv else _persist(_text)
    if _p:
        # STDERR, NOT STDOUT. This line is a notice to the run, not part of the report - and on
        # stdout it became a line of the report: lastmessage.py read it back as a Timing row and
        # refused a message for not containing "written to tools/p2w-bench/REPORT.md". stdout is
        # the document; anything else goes where logs go.
        sys.stderr.write("\n  written to %s - commit it, so the report survives the run\n"
                         % os.path.relpath(_p, os.path.dirname(os.path.dirname(HERE))))
    sys.exit(rc)
