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
    return {"measured": len(rows), "clean": clean, "failing": len(rows) - clean,
            "age_h": round(_age(TXT), 1)}


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
    g = _count(GVERIFY)
    lo = _count(LORES)
    txt = _txt_state()
    out = {"corpus": total, "stages": {}}

    out["stages"]["measure-google"] = {
        "done": g, "of": total, "age_h": round(_newest(GVERIFY), 1),
        "state": "done" if total and g >= total else
                 ("moving" if _newest(GVERIFY) < THRESHOLD["measure-google"] else "stopped")}

    out["stages"]["matrix"] = {
        "done": lo, "of": g, "age_h": round(_newest(LORES), 1),
        "state": "done" if g and lo >= g else
                 ("moving" if _newest(LORES) < THRESHOLD["matrix"] else "stopped")}

    # A TABLE NEWER THAN ITS RESULTS IS CURRENT, NOT LATE. The class table is regenerated AFTER new
    # results land; when it is newer than the newest result, no run is behind and an age past six
    # hours is the age of the inputs, not of the work. Reading `stopped` there is the false alarm
    # that makes a watchdog ignorable - BLOCKERS.md 20 Nov 18:10 asked for exactly this state.
    out["stages"]["classify"] = {
        "age_h": round(_age(CLASSES), 1),
        "state": ("superseded" if _is_current(CLASSES, GVERIFY) else
                  ("moving" if _age(CLASSES) < THRESHOLD["classify"] else "stopped"))
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
        out["stages"]["fix"]["why"] = ("a run is still marked running but has not beaconed for %d min "
                                       "- the slot is free, so the next scheduled run takes over; if "
                                       "the platform keeps the old one running it never will" % hung)

    out["stages"]["txt"] = {
        "measured": txt["measured"], "clean": txt["clean"], "failing": txt["failing"],
        "age_h": txt["age_h"],
        "state": ("moving" if txt["age_h"] < THRESHOLD["txt"] else "stopped")
                 if txt["measured"] else "never measured"}

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
