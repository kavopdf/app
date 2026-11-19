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
import argparse, csv, glob, json, os, subprocess, sys, time

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
THRESHOLD = {
    "measure-google": 4 * HOUR,
    "matrix": 4 * HOUR,
    "classify": 6 * HOUR,
    "fix": 3 * HOUR,
    "txt": 12 * HOUR,
}


def _age(path):
    """Hours since a path last changed. A missing path is infinitely old, not zero."""
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
                t = time.mktime(time.strptime(at, "%Y-%m-%d %H:%M"))
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

    out["stages"]["classify"] = {
        "age_h": round(_age(CLASSES), 1),
        "state": ("moving" if _age(CLASSES) < THRESHOLD["classify"] else "stopped")
                 if g >= total and total else "waiting"}

    recent = _attempts_recent(3.0)
    out["stages"]["fix"] = {
        "attempts_3h": recent, "age_h": round(_age(ATTEMPTS), 1),
        "state": "moving" if recent else "stopped"}

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
