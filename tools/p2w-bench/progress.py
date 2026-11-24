#!/usr/bin/env python3
"""progress.py - one dated row per day, so two months of work is visible as a trend.

WHY THIS EXISTS. Five crons report what they did this hour. Nothing anywhere says whether the corpus
is better than it was last week, and over a two-month run that is the only question that matters. A
fixer that lands one document a day and a fixer that lands none read identically in every per-run
report, and a pipeline that has stopped improving looks exactly like one that is working.

So this appends today's numbers to benchmarks/PROGRESS.md - once per day, never twice - and prints the
change since the previous row.

    python3 tools/p2w-bench/progress.py             # append today if it is not there, print the trend
    python3 tools/p2w-bench/progress.py --show      # print the table, append nothing
    python3 tools/p2w-bench/progress.py --json      # today's row

WHAT IT READS. Only committed evidence: RANKING.csv for the .docx, RANKING-TXT.csv for the .txt, and
benchmarks/gverify/ for the Google measurement. It computes nothing it cannot point at.

WHAT IT DOES NOT DO. It does not decide whether the numbers are good, and it does not stop anything.
A row that is worse than the one before it is a fact to look at, not a failure to revert - a corpus that
got worse on the day a class was taken on may have got better on three documents that mattered more.
"""
import argparse, csv, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RANK = os.path.join(ROOT, "benchmarks", "RANKING.csv")
TXT = os.path.join(HERE, "txt", "RANKING-TXT.csv")
GVERIFY = os.path.join(ROOT, "benchmarks", "gverify")
OUT = os.path.join(ROOT, "benchmarks", "PROGRESS.md")

HEAD = """# Progress - one row per day

Written by `tools/p2w-bench/progress.py`, which the watchdog runs. Each row is the committed state of
the corpus on that date; nothing here is typed by hand.

`docx open` is the number of documents whose share@5px is above 1.0 in RANKING.csv. `txt failing` is
the number whose .txt fails a check. `google` is how many documents have been measured through Google's
own renderer, and `google clean` how many of those pass all 42 checks.

A row that does not move is the signal: it means a day of the pipeline produced no change, and the
watchdog's job is to find out why.

| date | docx open | txt failing | google | google clean | note |
|---|---:|---:|---:|---:|---|
"""


def _docx_open():
    try:
        rows = [r for r in csv.DictReader(open(RANK, encoding="utf-8")) if r.get("share5")]
    except Exception:
        return None, None
    bad = 0
    for r in rows:
        try:
            if float(r["share5"]) > 1.0:
                bad += 1
        except ValueError:
            pass
    return bad, len(rows)


def _txt_failing():
    try:
        rows = list(csv.DictReader(open(TXT, encoding="utf-8")))
    except Exception:
        return None, None
    bad = 0
    for r in rows:
        try:
            if int(r.get("failed") or 0) > 0:
                bad += 1
        except ValueError:
            pass
    return bad, len(rows)


def _google():
    if not os.path.isdir(GVERIFY):
        return 0, 0
    n = clean = 0
    for f in os.listdir(GVERIFY):
        if not f.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(GVERIFY, f), encoding="utf-8"))
        except Exception:
            continue
        if d.get("status") == "page_count_refused":
            continue
        n += 1
        if not d.get("failed"):
            clean += 1
    return n, clean


def today():
    dopen, dtotal = _docx_open()
    tfail, ttotal = _txt_failing()
    g, gclean = _google()
    return {"date": time.strftime("%Y-%m-%d"),
            "docx_open": dopen, "docx_total": dtotal,
            "txt_failing": tfail, "txt_total": ttotal,
            "google": g, "google_clean": gclean}


def today_is_stale():
    """The committed row for today against what the data says now. Returns a list of disagreements.

    rows() is history and must not be recomputed - that rule is right. But TODAY'S row is not history yet,
    and on 24 Nov it said google_clean 29 while the same function's today() computed 35. The watchdog read the
    committed row, as it is told to, and reported 29 over live data that said 35 - six documents adrift, with
    nothing in the pipeline able to notice because the two numbers are never compared.

    That is the same shape as every reporting fault fixed this week: two sources describe one quantity, one is
    read, and the other is never asked. Here both live in the same module, so the comparison is free.
    """
    out = []
    try:
        t = today()
        rs = [r for r in rows() if r.get("date") == t["date"]]
        if not rs:
            return out                       # no row for today yet: appending one is the watchdog's job
        r = rs[-1]
        for k in ("docx_open", "txt_failing", "google", "google_clean"):
            if k in r and k in t and int(r[k]) != int(t[k]):
                out.append("%s: committed row says %s, the data says %s" % (k, r[k], t[k]))
    except Exception as e:
        out.append("could not compare today's row: %s" % type(e).__name__)
    return out


def rows():
    """Every committed row, in order. The table is the only history - read it, do not recompute it."""
    out = []
    try:
        for line in open(OUT, encoding="utf-8"):
            if not line.startswith("| 2"):
                continue
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) < 5:
                continue
            try:
                out.append({"date": c[0], "docx_open": int(c[1]), "txt_failing": int(c[2]),
                            "google": int(c[3]), "google_clean": int(c[4]),
                            "note": c[5] if len(c) > 5 else ""})
            except ValueError:
                continue
    except OSError:
        pass
    return out


def amend(t):
    """Rewrite TODAY's row with the live numbers, keeping what it used to say in the note.

    ONCE PER DAY IS RIGHT; NEVER CORRECTED IS NOT. A row is written from the tables as they stood at
    the moment it was appended, and the tables move for the rest of the day - so the committed row
    disagrees with the corpus it summarises, and a reader comparing the two cannot tell which one is
    the day's truth. Measured on 21 Nov: the row recorded `.docx open` 60 while `RANKING.csv` read 61,
    and `.txt failing` 46 against 27. Three blocker rows (20 Nov 18:10, 21 Nov 00:07 and 12:10) asked
    for this and none of them could do it, because this file had no way to say "today, again".

    It only ever touches a row whose date is TODAY, so the history is still append-only: yesterday's
    row is not a draft. The note names what the row used to say, so the correction is visible rather
    than silent - a row that changes without saying so is the `number that looks better` trap.
    """
    if not os.path.exists(OUT):
        return False
    lines = open(OUT, encoding="utf-8").read().split("\n")
    def v(x):
        return "?" if x is None else str(x)
    hit = None
    for i, line in enumerate(lines):
        if not line.startswith("| %s |" % t["date"]):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 5:
            continue
        if (c[1] == v(t["docx_open"]) and c[2] == v(t["txt_failing"])
                and c[3] == str(t["google"]) and c[4] == str(t["google_clean"])):
            return "unchanged"
        hit = (i, c)
    if not hit:
        return "no row for today"
    i, c = hit
    note = "amended: was docx %s, txt %s, google %s/%s" % (c[1], c[2], c[3], c[4])
    lines[i] = ("| %s | %s | %s | %d | %d | %s |"
                % (t["date"], v(t["docx_open"]), v(t["txt_failing"]),
                   t["google"], t["google_clean"], note))
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    os.replace(tmp, OUT)
    return note


def append(t, note=""):
    have = {r["date"] for r in rows()}
    if not os.path.exists(OUT):
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(HEAD)
    if t["date"] in have:
        return False
    def v(x):
        return "?" if x is None else str(x)
    with open(OUT, "a", encoding="utf-8") as f:
        f.write("| %s | %s | %s | %d | %d | %s |\n"
                % (t["date"], v(t["docx_open"]), v(t["txt_failing"]),
                   t["google"], t["google_clean"], note))
    return True


def trend():
    rs = rows()
    if len(rs) < 2:
        print("  %d row(s) - a trend needs two. Nothing to compare yet." % len(rs))
        return
    a, b = rs[-2], rs[-1]
    def d(k):
        x = (b[k] - a[k])
        return "%+d" % x if x else "no change"
    print("  %s -> %s" % (a["date"], b["date"]))
    print("    docx open    %4s -> %-4s  %s" % (a["docx_open"], b["docx_open"], d("docx_open")))
    print("    txt failing  %4s -> %-4s  %s" % (a["txt_failing"], b["txt_failing"], d("txt_failing")))
    print("    google       %4s -> %-4s  %s" % (a["google"], b["google"], d("google")))
    print("    google clean %4s -> %-4s  %s" % (a["google_clean"], b["google_clean"], d("google_clean")))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--note", default="")
    ap.add_argument("--amend", action="store_true",
                    help="rewrite TODAY's row from the live tables, naming what it used to say")
    a = ap.parse_args(argv)
    t = today()
    if a.amend:
        r = amend(t)
        print("  %s  docx open %s/%s | txt failing %s/%s | google %d (clean %d)"
              % (t["date"], t["docx_open"], t["docx_total"], t["txt_failing"], t["txt_total"],
                 t["google"], t["google_clean"]))
        print("  %s" % (r if r not in (True, False) else
                        ("today has no row to amend" if r is False else "amended")))
        print()
        trend()
        return 0
    if a.json:
        print(json.dumps(t, indent=1))
        return 0
    if a.show:
        try:
            sys.stdout.write(open(OUT, encoding="utf-8").read())
        except OSError:
            print("no progress file yet")
        return 0
    added = append(t, a.note)
    print("  %s  docx open %s/%s | txt failing %s/%s | google %d (clean %d)"
          % (t["date"], t["docx_open"], t["docx_total"], t["txt_failing"], t["txt_total"],
             t["google"], t["google_clean"]))
    print("  %s" % ("row appended" if added else "today already has a row - nothing appended"))
    print()
    trend()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
