#!/usr/bin/env python3
"""health.py - is the pipeline moving, or has it stopped and nobody noticed.

WHY THIS EXISTS. The system is meant to run for months without a person looking at it. Five crons each
report what they did, and a run that says "measured 20 documents" sounds like progress whether or not
the number has moved for a fortnight. Nothing in the pipeline could answer the only question that
matters over that timescale: **is the thing that was supposed to happen this hour actually happening.**

So this reads the evidence - committed results, file timestamps, the attempt ledger - and says, for each
stage, whether it is done, moving, or stopped. It never trusts a report.

    python3 tools/p2w-bench/health.py             # the whole picture
    python3 tools/p2w-bench/health.py --json      # for a cron to parse
    python3 tools/p2w-bench/health.py --stalled   # exit 1 if anything is stopped, for a watchdog

WHAT "STOPPED" MEANS. Not "slow". A stage is stopped when its own output has not changed in longer than
that stage needs to produce one unit of it. The thresholds below are per-stage and derived from how long
that stage actually takes, not from a round number:

    measure-google   one run measures up to 20 documents, hourly     -> 4 hours without a new result
    matrix           the LibreOffice half, same cadence              -> 4 hours
    classify         regenerated after new results                   -> 6 hours
    fix              the fixer runs hourly and must record an attempt -> 3 hours with none
    txt              measured by the baseline; the txt table is the evidence -> 12 hours

A threshold that is too tight turns the watchdog into noise, and a watchdog that cries wolf is ignored
exactly when it matters. These are deliberately loose.
"""
import argparse, calendar, csv, glob, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GVERIFY = os.path.join(ROOT, "benchmarks", "gverify")
LORES = os.path.join(ROOT, "benchmarks", "gverify-lo")
TXT = os.path.join(HERE, "txt", "RANKING-TXT.csv")
RANK = os.path.join(ROOT, "benchmarks", "RANKING.csv")
CLASSES = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")
# THE TABLE THE FIXER ACTUALLY RANKS IS THE GOOGLE ONE, AND THIS WATCHED THE OTHER.
#
# classpick.py ranks benchmarks/DEFECT-CLASSES-GOOGLE.md, which classify_google.py regenerates on the
# classifier cron. health.py measured only benchmarks/DEFECT-CLASSES.md - the LibreOffice-derived table
# that attempt.py writes but no run picks a class from. Measured 21 Nov 21:35 UTC: the classifier
# regenerated the GOOGLE table at 19:51 (1.7 h old, current against the 18:19 results), while this
# row read `stopped` at 13.3 h because the .md had not been touched since 08:14. A watchdog that
# reports a stall on a file nobody ranks is the false alarm that makes a watchdog ignorable, so the
# row is current when EITHER table is current, and the age shown is the younger of the two.
CLASSES_GOOGLE = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES-GOOGLE.md")
# THE .TXT ROW HAD THE SAME FALSE ALARM THE `classify` ROW WAS REPAIRED FOR, AND IT RAN RED FOR 16 HOURS.
#
# RANKING-TXT.csv is a function of three things and nothing else: the engine sources, verify_txt.py and
# restamp_txt.py. When none of those has moved since the table was committed, re-scoring the corpus
# reproduces the table byte for byte - there is no work for any run to do, and an age past twelve hours
# is the age of an unchanged engine, not of a stalled stage. Measured 22 Nov 15:09 IST: the table was
# committed 21 Nov 17:08 UTC; verify_txt.py in that same commit; restamp_txt.py 20 Nov 06:33; the engine
# 21 Nov 11:30. The table was newer than every input, ENGINE-STAMP.json's txt fingerprint
# (ae5b3129bfa31f15) matched regress.py's fingerprint of the live engine, and STATE-TXT.json recorded
# 462353f - the engine as it stands. The row still read `stopped` at 16.5 h, and would have read it
# every three hours until an engine patch landed. A watchdog that reports a stall on a table nothing
# can change is the false alarm that makes a watchdog ignorable.
#
# This adds a STATE, not a threshold: the age is still printed and still compared with the same twelve
# hours. The moment the engine or either script is committed, the table is older than its inputs again
# and the row goes back to moving/stopped by itself. See BLOCKERS.md 2026-11-22 15:09.
VERIFY_TXT = os.path.join(HERE, "verify_txt.py")
RESTAMP_TXT = os.path.join(HERE, "restamp_txt.py")
ENGINE_DIR = os.path.join(ROOT, "app", "src", "main", "java", "com", "kavopdf", "app", "engine")
ATTEMPTS = os.path.join(HERE, "ATTEMPTS.json")
BLOCKERS = os.path.join(HERE, "BLOCKERS.md")

HOUR = 3600.0
# Every timestamp this pipeline writes is IST; this pod runs UTC. See _attempts_recent().
IST_OFFSET = 5 * 3600 + 30 * 60
# IN HOURS, because that is what every age in this file is. `_age()` returns hours and the state
# lines compare `_age(...) < THRESHOLD[...]`; these were written in SECONDS (4 * HOUR = 14400), so
# the comparison was `0.5 < 14400` and `stopped` could never be printed for measure-google, matrix,
# classify or txt. A check that cannot fail is decoration - the exact bug this watchdog exists to
# catch in other people's instruments.
#
# Measured 21 Nov 12:47 on the live tree: `txt` read **moving** at an age of 13.2 h against a 12 h
# intent. After this line it reads `stopped`. The thresholds themselves are unchanged in meaning -
# 4, 4, 6, 3 and 12 hours - only their unit was wrong. A watchdog must not move its own thresholds;
# it may repair a unit, and this is the repair. (BLOCKERS.md row 5, 20 Nov, asked for exactly this.)
THRESHOLD = {
    "measure-google": 4.0,
    "matrix": 4.0,
    "classify": 6.0,
    "fix": 3.0,
    "txt": 12.0,
}


def _commit_time(path):
    """When the last commit touched a path, in epoch seconds - or None if git cannot say.

    THIS IS THE PIPELINE'S OWN CLOCK AND mtime IS NOT. Every cron starts from a FRESH CLONE
    (COORDINATION.md), so `os.path.getmtime` on any file in the tree is the time the clone was
    made, not the time the file changed. Measured on 20 Nov: `health.py` reported `0.0 h` for
    all five stages while the newest gverify result was hours old - every age was the age of the
    clone. A watchdog reading those numbers can never turn red, which is the one thing it exists
    to do. `git log -1 --format=%ct` survives a clone because the commit carries its own date.
    """
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "log", "-1", "--format=%ct", "--", path],
            capture_output=True, text=True, timeout=20)
        v = (out.stdout or "").strip()
        return float(v) if v else None
    except Exception:
        return None


def _age(path):
    """Hours since a path last changed. A missing path is infinitely old, not zero.

    The commit date is used when git knows one; mtime is the fallback for a file that has never
    been committed. Taking the NEWER of the two would put the clone's own timestamp back in
    front and restore the bug, so the commit wins whenever it exists.
    """
    if not os.path.exists(path):
        return 1e9
    c = _commit_time(os.path.relpath(path, ROOT))
    if c is not None:
        return max(0.0, (time.time() - c) / HOUR)
    try:
        return (time.time() - os.path.getmtime(path)) / HOUR
    except OSError:
        return 1e9


def _newest(d):
    if not os.path.isdir(d):
        return 1e9
    files = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".json")]
    if not files:
        return 1e9
    return min(_age(p) for p in files)


def _newest_epoch(d):
    """The commit time of the most recent file in a directory, in epoch seconds - or None.

    `_newest` answers "how old is the freshest thing here"; this answers "when was the freshest
    thing here written", which is the only way to ask whether a TABLE is newer than the RESULTS it
    summarises. A table that is newer than its inputs is not late - it is current, and a stage
    reading `stopped` for it is a false alarm. See compute()'s `superseded` state.
    """
    if not os.path.isdir(d):
        return None
    best = None
    for f in os.listdir(d):
        if not f.endswith(".json"):
            continue
        c = _commit_time(os.path.relpath(os.path.join(d, f), ROOT))
        if c is not None and (best is None or c > best):
            best = c
    return best


def _is_current(table, results_dir):
    """True when the table was committed at or after the newest result it summarises."""
    t = _commit_time(os.path.relpath(table, ROOT))
    r = _newest_epoch(results_dir)
    if t is None or r is None:
        return False
    return t >= r


def _count(d):
    if not os.path.isdir(d):
        return 0
    return len([f for f in os.listdir(d) if f.endswith(".json")])


def _corpus_total():
    """Every document that exists - NOT every row of RANKING.csv.

    The ranking has 212 rows because 416_many_tiny_pages is exempt from the round-one baseline and so
    is absent from it, while still being a document. Counting rows printed "corpus: 212 documents" and
    then "measure-google done 213 of 212" - a stage that measured more documents than the corpus was
    said to contain. The watchdog reported that impossible line, and lastmessage.py passed it because
    213 and 212 both appear in the tool output.

    The corpus is what gverify saw: scored + page-count-refused. The ranking row count is the fallback
    for when gverify has not run. Same rule as report.py's corpus().
    """
    try:
        import glob as _g
        scored = refused = 0
        for f in _g.glob(os.path.join(HERE, "..", "..", "benchmarks", "gverify", "*.json")):
            try:
                j = json.load(open(f, encoding="utf-8"))
            except Exception:
                continue
            if j.get("status") == "page_count_refused":
                refused += 1
            else:
                scored += 1
        if scored + refused:
            return scored + refused
    except Exception:
        pass
    try:
        with open(RANK, encoding="utf-8") as f:
            return len([r for r in csv.DictReader(f) if r.get("document")])
    except Exception:
        return 0


def _txt_state():
    """The .txt half. The user asked for both formats to be perfect, so it gets its own row."""
    try:
        rows = list(csv.DictReader(open(TXT, encoding="utf-8")))
    except Exception:
        return {"measured": 0, "clean": 0, "failing": 0, "age_h": 1e9}
    clean = len([r for r in rows if int(r.get("failed") or 0) == 0])
    # The age of the newest thing that can change a .txt score. The table is current when it is
    # younger than all of them; `_age` is hours since the path last changed, so the newest input is
    # the SMALLEST of the three.
    # COMPARED AS COMMIT EPOCHS, NOT AS HOURS. The table and verify_txt.py were written by the SAME
    # commit (bd1c2e52), so their ages are identical to the second and a strict `age <` comparison
    # reads the tie as "stale" - which is the bug this repair exists to remove. A table committed at
    # or after its newest input is current.
    inputs = max(_commit_time(p) or 0.0 for p in (ENGINE_DIR, VERIFY_TXT, RESTAMP_TXT))
    table = _commit_time(TXT) or 0.0
    return {"measured": len(rows), "clean": clean, "failing": len(rows) - clean,
            "age_h": round(_age(TXT), 1),
            "inputs_age_h": round(max(0.0, (time.time() - inputs) / HOUR), 1),
            "current": bool(table) and table >= inputs}


def _attempts_recent(hours=3.0):
    """Attempts the fixer recorded inside the window. The ledger is the only honest source."""
    try:
        d = json.load(open(ATTEMPTS, encoding="utf-8"))
    except Exception:
        return 0
    n = 0
    cutoff = time.time() - hours * HOUR
    for cls, rec in (d or {}).items():
        if not isinstance(rec, dict):
            continue
        for h in rec.get("history") or []:
            at = h.get("at") or ""
            try:
                # THE LEDGER WRITES IST AND THIS POD RUNS UTC. attempt.py stamps `at` with
                # `time.gmtime(time.time() + 19800)` - IST wall time, deliberately, so every
                # timestamp in the pipeline agrees. `time.mktime` then read that wall time as
                # LOCAL, and local here is UTC, so every attempt was placed 5.5 hours in the
                # FUTURE and counted as "in the last 3 hours" for ever. Measured on 20 Nov: the
                # watchdog read `6 attempt(s) in 3 h` when the ledger held fewer. calendar.timegm
                # reads the struct as UTC (so the pod's own TZ cannot move it) and the offset
                # takes it back to the real epoch.
                t = calendar.timegm(time.strptime(at, "%Y-%m-%d %H:%M")) - IST_OFFSET
            except Exception:
                continue
            if t >= cutoff:
                n += 1
    return n


def compute():
    total = _corpus_total()
    # A FILE ON DISK IS NOT A MEASUREMENT. This counted every .json in benchmarks/gverify/, so the
    # stage read `done 213 of 213` while only 82 results carried the engine on HEAD - the watchdog was
    # told the measurement stage was finished, so a stale table could never be reported as late.
    # `gverify._done()` is the engine-aware count `--plan` has used since 21 Nov; two answers to one
    # question is how the 22 Nov "0 verified" report happened. Falls back to the file count if the
    # import fails, so health.py still runs if gverify.py moves.
    try:
        import gverify as _g
        g = len(_g._done())
    except Exception:
        g = _count(GVERIFY)
    lo = _count(LORES)
    txt = _txt_state()
    out = {"corpus": total, "stages": {}}

    out["stages"]["measure-google"] = {
        "done": g, "of": total, "age_h": round(_newest(GVERIFY), 1),
        "state": "done" if total and g >= total else
                 ("moving" if _newest(GVERIFY) < THRESHOLD["measure-google"] else "stopped")}

    # `of` WAS `g`, THE GOOGLE COUNT. Once the Google count became engine-aware (82 of 213) the matrix
    # line printed "done 213 of 82" - a fraction greater than one, which is the same class of nonsense
    # as the "213 of 212" this file already warns about at the top. The matrix is a LibreOffice render
    # of every document in the corpus; the corpus is what it can have, so the corpus is what it is
    # measured against.
    # A FILE ON DISK IS NOT A MEASUREMENT - THE SAME RULE, FOR THE OTHER HALF. The count above is
    # files, and on 27 Nov it read `213 of 214` while only 37 of those results carried the engine in
    # the tree: the LibreOffice half is refreshed by `gverify.py --lo-stale`, and nothing in this file
    # could see that 176 results were an engine old. `done` stays coverage (it is what the corpus can
    # have); the engine-stamped count is reported beside it, because that is the pair the fixer's
    # capability table depends on and the only number that says whether the pair is one engine.
    _lo_on = None
    try:
        import gverify as _gl
        _now = _gl._engine_now()
        _on = 0
        for _f in os.listdir(LORES):
            if not _f.endswith(".json"):
                continue
            try:
                _d = json.load(open(os.path.join(LORES, _f), encoding="utf-8"))
            except Exception:
                continue
            if _gl._same_engine(_d.get("engine"), _now):
                _on += 1
        _lo_on = _on
    except Exception:
        _lo_on = None
    out["stages"]["matrix"] = {
        "done": lo, "of": total, "age_h": round(_newest(LORES), 1),
        "state": "done" if total and lo >= total else
                 ("moving" if _newest(LORES) < THRESHOLD["matrix"] else "stopped")}
    if _lo_on is not None:
        out["stages"]["matrix"]["on_engine"] = _lo_on
        if _lo_on < lo:
            out["stages"]["matrix"]["why"] = (
                "only %d of %d results carry the engine in the tree - the rest are re-measured by "
                "gverify.py --lo-stale" % (_lo_on, lo))

    # A TABLE NEWER THAN ITS RESULTS IS CURRENT, NOT LATE. The class table is regenerated AFTER new
    # results land; when it is newer than the newest result, no run is behind and an age past six
    # hours is the age of the inputs, not of the work. Reading `stopped` there is the false alarm
    # that makes a watchdog ignorable - BLOCKERS.md 20 Nov 18:10 asked for exactly this state.
    # Both tables are read: the GOOGLE one is the queue the fixer ranks (classpick.py), the .md is the
    # ledger attempt.py records into. Either being newer than the results means no classify run is
    # behind. See the CLASSES_GOOGLE note above for the 21 Nov false alarm this repairs.
    _class_age = min(_age(CLASSES), _age(CLASSES_GOOGLE))
    _class_current = _is_current(CLASSES, GVERIFY) or _is_current(CLASSES_GOOGLE, GVERIFY)
    out["stages"]["classify"] = {
        "age_h": round(_class_age, 1),
        "state": ("superseded" if _class_current else
                  ("moving" if _class_age < THRESHOLD["classify"] else "stopped"))
                 if g >= total and total else "waiting"}

    recent = _attempts_recent(3.0)
    # A RUN THAT IS STILL "RUNNING" AND HAS STOPPED BEACONING IS THE FAILURE THIS WATCHDOG EXISTS FOR.
    #
    # Attempts in the last three hours said "moving" for a run that had been hung for 39 minutes with
    # zero attempts - it had recorded two earlier, so the window was satisfied and the stall was
    # invisible. Measured 19 Nov: a fixer run started 18:52, released its slot, and sat with no beacon
    # while the cron platform still called it running and so did not schedule the next one.
    #
    # The beacon is the honest signal. status.py already computes it; this reads the same file.
    hung = None
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "status.py"), "--json"],
                           capture_output=True, text=True, timeout=90)
        st = json.loads(r.stdout) if r.stdout.strip().startswith("{") else {}
        mins = st.get("beacon_age_min") or st.get("claim_age_min")
        if isinstance(mins, (int, float)) and mins > 20:
            hung = round(mins)
    except Exception:
        pass
    out["stages"]["fix"] = {
        "attempts_3h": recent, "age_h": round(_age(ATTEMPTS), 1),
        "state": "stopped" if hung else ("moving" if recent else "stopped")}
    if hung:
        # THE SLOT IS NOT "FREE" BECAUSE A RUN STOPPED SPEAKING - THAT IS A SECOND FACT, NOT THIS ONE.
        #
        # This line read "the slot is free, so the next scheduled run takes over". Measured 25 Nov
        # 00:43 IST: the fixer had claimed at 23:45 and its claim was 24 min old, inside round.py's
        # CLAIM_STALE_MIN["fixer"] of 45, so --claim-fixer refused every run for another 21 min. The
        # slot was held. That sentence has been quoted as evidence in BLOCKERS.md more than once
        # (22 Nov 18:11 read it as "the slot is free" while ROUND.json still carried fixer_started).
        # A watchdog line that asserts a state it never read is the instrument lying in the one place
        # a reader looks first, so it now prints the two facts it has: the beacon age, and the age at
        # which round.py releases the claim. No threshold moves - CLAIM_STALE_MIN is read, not copied.
        _limit = 45
        try:
            # Loaded by path, not by `import round`: a module called `round` on sys.path is one
            # bad day from shadowing the builtin this file calls on almost every line.
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location("_roundmod", os.path.join(HERE, "round.py"))
            _mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _limit = int(_mod.CLAIM_STALE_MIN.get("fixer", 45))
        except Exception:
            pass
        out["stages"]["fix"]["why"] = (
            "a run is still marked running but has not beaconed for %d min - round.py frees a fixer "
            "claim %d min after it is taken, so a run before then stands down and one after it takes "
            "over; if the platform keeps the old one running it never will" % (hung, _limit))

    # A TABLE NEWER THAN EVERYTHING THAT CAN CHANGE IT IS CURRENT, NOT LATE - the same rule the
    # `classify` row uses, applied to the inputs a .txt score actually has.
    _txt_current = bool(txt["measured"]) and txt.get("current", False)
    # ...BUT A FRESH SCORE IS NOT A FINISHED JOB. The .txt row read "superseded - 199 clean, 14
    # failing" for days while nothing touched the 14, because every reader of this state treats it as
    # "no work here". A current measurement of 14 failures is a current measurement OF 14 FAILURES.
    _txt_current = _txt_current and not txt["failing"]
    out["stages"]["txt"] = {
        "measured": txt["measured"], "clean": txt["clean"], "failing": txt["failing"],
        "age_h": txt["age_h"], "inputs_age_h": txt["inputs_age_h"],
        "state": ("superseded" if _txt_current else
                  ("moving" if txt["age_h"] < THRESHOLD["txt"] else "stopped"))
                 if txt["measured"] else "never measured"}
    if _txt_current:
        out["stages"]["txt"]["why"] = ("the table was committed after the engine, verify_txt.py and "
                                        "restamp_txt.py last changed - re-scoring reproduces it")

    out["blockers"] = []
    try:
        for line in open(BLOCKERS, encoding="utf-8"):
            if line.startswith("| 19 Nov") or line.startswith("| 20 Nov"):
                out["blockers"].append(line.strip()[:160])
    except Exception:
        pass
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--stalled", action="store_true")
    a = ap.parse_args(argv)

    # THE UNIT GUARD. The thresholds were in seconds and every age in this file is in hours, so
    # four of five stages could not read `stopped` and this tool printed green over a 13-hour-old
    # table. Repairing the numbers is not enough - a future edit can put the seconds back and the
    # failure is silent, which is exactly how this one survived a day of watchdog passes.
    # No stage in this pipeline is meant to be given more than two days of silence.
    _worst = max(THRESHOLD.items(), key=lambda kv: kv[1])
    if _worst[1] > 48:
        print("  REFUSED - THRESHOLD[%r] = %s, but every age in this file is in HOURS. "
              "A threshold over 48 cannot be hours; it is seconds, and it can never fire."
              % (_worst[0], _worst[1]), file=sys.stderr)
        return 3
    d = compute()

    if a.json:
        print(json.dumps(d, indent=1))
    else:
        print("  corpus: %d documents\n" % d["corpus"])
        print("  %-16s %-10s %-22s %s" % ("stage", "state", "progress", "age"))
        for name, s in d["stages"].items():
            prog = ""
            if "of" in s:
                prog = "%d of %d" % (s["done"], s["of"])
            elif name == "txt":
                prog = "%d clean, %d failing" % (s["clean"], s["failing"])
            elif name == "fix":
                prog = "%d attempt(s) in 3 h" % s["attempts_3h"]
            print("  %-16s %-10s %-22s %.1f h" % (name, s["state"], prog, s["age_h"]))
            if s.get("why"):
                print("      %s" % s["why"])
        if d["blockers"]:
            print("\n  blockers recorded:")
            for b in d["blockers"][-5:]:
                print("   ", b)

    stalled = [n for n, s in d["stages"].items() if s["state"] == "stopped"]
    if a.stalled:
        if stalled:
            print("\nSTOPPED: %s" % ", ".join(stalled))
            return 1
        print("\nnothing is stopped")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
