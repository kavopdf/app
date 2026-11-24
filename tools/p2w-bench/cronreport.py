#!/usr/bin/env python3
"""The report for the five crons that do not have one. Generated, never written.

    python3 tools/p2w-bench/cronreport.py --for gverify   > /tmp/report.md
    python3 tools/p2w-bench/lastmessage.py --file /tmp/report.md --for gverify

WHY THIS EXISTS. The fixer has had a generator since the beginning: report.py reads the state files
and prints a report whose every number came from a file. The other five wrote prose. Their numbers are
checked now - lastmessage.py refuses one that no tool printed - but the SHAPE was still whatever the run
felt like, which is how a report arrives as four pages of loose text with a table that is not a table.

A generated report has no shape a run can get wrong and no number a run can mistype. These five are
built from the same files the verifiers read, so the two agree by construction rather than by care.

WHAT EACH ONE LOOKS LIKE, and why:

  baseline    a corpus scoreboard. The only thing anyone asks it is "how many documents are still
              wrong", so the four counts are the top of the page and the change since the last row
              sits directly under them.
  classifier  a class list. It answers "what is left and how big is each piece", so the classes are
              ranked by the number of documents they cost, biggest first.
  gverify     the gap between the two renderers. Google's number first, LibreOffice's beside it, so a
              reader can see at a glance which checks only Google fails.
  watchdog    five rows, one per stage, and the trend under them. It exists to answer "is anything
              stopped", so a stopped stage is the first thing on the page.
  apk         a headline and a small table. Almost every run ships nothing, and that must read as a
              decision rather than a failure.
"""
import json, os, subprocess, sys, glob
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IST = timezone(timedelta(hours=5, minutes=30))

RANK = os.path.join(ROOT, "benchmarks", "RANKING.csv")
RANK_BASE = os.path.join(ROOT, "benchmarks", "RANKING-BASELINE.csv")
TXT = os.path.join(HERE, "txt", "RANKING-TXT.csv")
GV = os.path.join(ROOT, "benchmarks", "gverify")
GLO = os.path.join(ROOT, "benchmarks", "gverify-lo")
GOOGLE_CLASSES = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES-GOOGLE.md")
ROUND = os.path.join(HERE, "ROUND.json")


def now_ist():
    return datetime.now(IST)


def stamp():
    d = now_ist()
    return d.strftime("%d %b %Y"), d.strftime("%H:%M")


def sh(cmd):
    try:
        r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=120)
        return (r.stdout or "") + (r.stderr or "")
    except Exception:
        return ""


def csv_rows(path):
    import csv
    if not os.path.exists(path):
        return []
    try:
        return list(csv.DictReader(open(path, encoding="utf-8")))
    except Exception:
        return []


def rank_scores(path):
    out = {}
    for r in csv_rows(path):
        v = (r.get("share5") or "").strip()
        if not v or not r.get("document"):
            continue
        try:
            out[r["document"]] = float(v)
        except ValueError:
            pass
    return out


def txt_state():
    rows = csv_rows(TXT)
    clean = sum(1 for r in rows if (r.get("failed_ids") or "").strip() in ("-", ""))
    return len(rows), clean, len(rows) - clean


def google_state():
    scored, refused, clean = 0, 0, 0
    failed_by = {}
    for f in sorted(glob.glob(GV + "/*.json")):
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if j.get("status") == "page_count_refused":
            refused += 1
            continue
        scored += 1
        bad = j.get("failed") or []
        if not bad:
            clean += 1
        for c in bad:
            failed_by[c] = failed_by.get(c, 0) + 1
    return scored, refused, clean, failed_by


def _gv_results():
    """Every Google verdict on disk, as {name: dict}."""
    out = {}
    for f in sorted(glob.glob(GV + "/*.json")):
        try:
            out[os.path.basename(f)[:-5]] = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
    return out


def _checks_applied():
    """How many checks the documents were actually measured against, as a readable string.

    DERIVED, NEVER ASSUMED. This said "42" for as long as the check set was 42; when it reached 47 the
    report kept saying "passes all 42" over documents that had never been asked the other five questions.
    A mixed set is stated as mixed, because one number cannot describe two standards.
    """
    totals = sorted({v.get("total") for v in _gv_results().values() if v.get("total")})
    if not totals:
        return "unknown"
    if len(totals) == 1:
        return "%d" % totals[0]
    return ", ".join(str(x) for x in totals) + " (mixed - a document is clean only against its own set)"


def _on_current():
    """How many scored documents carry the current (largest) check count."""
    res = _gv_results()
    totals = [v.get("total") for v in res.values() if v.get("total")]
    if not totals:
        return 0
    cur = max(totals)
    return sum(1 for v in res.values()
               if v.get("status") != "page_count_refused" and v.get("total") == cur)


def scored_names():
    """The documents the Google count is over: a result that is not a page-count refusal.

    THE LIBREOFFICE COLUMN MUST BE COUNTED OVER THE SAME DOCUMENTS AS THE GOOGLE COLUMN, or the
    report compares two different corpora in one sentence. It counted every file in gverify-lo -
    including the ones Google refused - and printed "Google passes all 42 on 7; LibreOffice on 122"
    over a stated 192 measured. The 14 documents Google refused and LibreOffice passed were inside
    that 122, so the gap looked wider than the paired evidence supports. gverify.py --matrix has
    always used this denominator; the report now does too.
    """
    names = set()
    for f in sorted(glob.glob(GV + "/*.json")):
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if j.get("status") == "page_count_refused":
            continue
        names.add(os.path.basename(f)[:-5])
    return names


def lo_failed_by(names=None):
    out = {}
    for f in sorted(glob.glob(GLO + "/*.json")):
        if names is not None and os.path.basename(f)[:-5] not in names:
            continue
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for k, v in (j.get("checks") or {}).items():
            if v.get("ok") is False:
                out[k] = out.get(k, 0) + 1
    return out


def round_state():
    try:
        return json.load(open(ROUND, encoding="utf-8"))
    except Exception:
        return {}


def progress_rows():
    p = os.path.join(ROOT, "benchmarks", "PROGRESS.md")
    rows = []
    if not os.path.exists(p):
        return rows
    for line in open(p, encoding="utf-8"):
        if not line.startswith("| 20"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) >= 5:
            rows.append(c)
    return rows


def classes():
    """(signature, open_count, lo_count) from the Google class table, biggest first."""
    out = []
    if not os.path.exists(GOOGLE_CLASSES):
        return out
    for line in open(GOOGLE_CLASSES, encoding="utf-8"):
        if not line.startswith("| `"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 6:
            continue
        name = c[0].strip("` ")
        try:
            out.append((name, int(c[2]), int(c[4]), int(c[5])))
        except ValueError:
            continue
    return sorted(out, key=lambda x: -x[3])


def esc(s):
    """A check name must survive markdown. Underscores are italic markers."""
    return (s or "").replace("_", "\\_")


def bar(n, of, width=18):
    if not of:
        return ""
    filled = int(round(width * (n / float(of))))
    return "#" * max(0, filled) + "." * max(0, width - filled)


# ---------------------------------------------------------------- the five

class NoData(Exception):
    """The report cannot be made, because the thing it describes is not there."""


def need(value, what):
    """A report is a claim. A claim about nothing is not a report.

    Found on 20 Nov by running the generators against an empty tree: every one of them printed a
    confident report about zero documents - "0 of 0 documents are fixed to 99%", "Google passes all 42
    on 0" - and the baseline one even mixed a missing RANKING.csv with a present .txt table, so the same
    page said Documents 0 and .txt clean 167. A run that posts that has told the user something false in
    a format that looks verified. It must refuse instead.
    """
    if not value:
        raise NoData(what)
    return value


def baseline():
    d, t = stamp()
    scores, base = rank_scores(RANK), rank_scores(RANK_BASE)
    total = need(len(scores), "benchmarks/RANKING.csv has no scored rows - nothing to report on")
    open_ = sum(1 for v in scores.values() if v > 1.0)
    fixed = total - open_
    trows, tclean, tfail = txt_state()
    scored, refused, gclean, _ = google_state()
    need(trows, "tools/p2w-bench/txt/RANKING-TXT.csv has no rows")
    improved = sum(1 for k, v in scores.items() if k in base and v < base[k] - 0.005)
    worse = [k for k, v in scores.items() if k in base and v > base[k] + 0.005]
    mean_now = sum(scores.values()) / total if total else 0
    mean_base = sum(base.values()) / len(base) if base else 0
    gain = (100.0 * (mean_base - mean_now) / mean_base) if mean_base else 0

    L = ["# P2W Baseline - Run Report", "",
         "**%s · %s IST**" % (d, t), "",
         "> %d of %d documents are at or under 1%% share@5px in LibreOffice. The corpus is %.1f%% closer to the 15 Nov baseline"
         " than it started." % (fixed, total, gain), "",
         "## Corpus", "",
         "| | |", "|:--|--:|",
         "| Documents | **%d** |" % total,
         "| .docx at or under 1%% share@5px (LibreOffice) | **%d** |" % fixed,
         "| .docx still open | **%d** |" % open_,
         "| .txt clean | **%d** |" % tclean,
         "| .txt failing | **%d** |" % tfail,
         "| Google measured | **%d** of %d |" % (scored, total),
         "| Google clean | **%d** |" % gclean,
         "", "## Against the 15 Nov baseline", "",
         "| | baseline | now | |", "|:--|--:|--:|:--|",
         "| mean share@5 | %.2f | **%.2f** | %+.2f%% |" % (mean_base, mean_now, -gain),
         "| documents improved at all (any fall) | | **%d** | |" % improved,
         "| regressions | | **%d** | %s |" % (len(worse), "none" if not worse else "LOOK"),
         ""]
    if worse:
        L += ["Regressions are a defect, not a result:", ""]
        for w in worse[:10]:
            L.append("* `%s` %.2f -> %.2f" % (w, base.get(w, 0), scores[w]))
        L.append("")
    return "\n".join(L)


def classifier():
    d, t = stamp()
    cl = need(classes(), "benchmarks/DEFECT-CLASSES-GOOGLE.md names no classes")
    scored, refused, gclean, _ = google_state()
    r = round_state()
    # A DOCUMENT THAT FAILS THREE CLASSES IS ONE DOCUMENT. This summed the per-class counts, so a
    # document failing three checks was counted three times - and it summed the wrong column besides:
    # c[3] is "newly clean in LibreOffice only", not "failing". Measured 22 Nov, the report said
    # "35 classes cover 126 failing documents" when 169 documents fail at least one check.
    #
    # The honest total is the number of distinct documents with any failed check, read from the
    # measurement rather than derived from a table that counts per class.
    total = 0
    for _f in glob.glob(os.path.join(ROOT, "benchmarks", "gverify", "*.json")):
        try:
            _r = json.load(open(_f, encoding="utf-8"))
        except Exception:
            continue
        if _r.get("status") == "page_count_refused":
            continue
        if _r.get("failed"):
            total += 1
    L = ["# P2W Classifier - Run Report", "",
         "**%s · %s IST**" % (d, t), "",
         "> %d classes cover %d failing documents across %d measured in Google."
         % (len(cl), total, scored), "",
         "## Classes, biggest first", "",
         "| class | open | documents |", "|:--|--:|--:|"]
    for name, openc, loc, gcount in cl[:15]:
        L.append("| `%s` | %d | **%d** |" % (esc(name), openc, gcount))
    L += ["", "## Where the measurement stands", "",
          "| | |", "|:--|--:|",
          "| measured in Google | **%d** |" % scored,
          "| refused on page count | **%d** |" % refused,
          "| clean in Google | **%d** |" % gclean,
          "| round | %s of %s |" % (r.get("round", "?"), r.get("rounds_total", "?")),
          "| phase | `%s` |" % r.get("phase", "?"),
          ""]
    if cl:
        L += ["The top class is `%s` at %d documents. Take one class at a time and let the gate decide."
              % (esc(cl[0][0]), cl[0][3]), ""]
    return "\n".join(L)


def gverify():
    d, t = stamp()
    scored, refused, gclean, gf = google_state()
    need(scored, "benchmarks/gverify has no scored results")
    names = scored_names()
    lf = lo_failed_by(names)
    lclean = 0
    for f in sorted(glob.glob(GLO + "/*.json")):
        if os.path.basename(f)[:-5] not in names:
            continue
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if not any(v.get("ok") is False for v in (j.get("checks") or {}).values()):
            lclean += 1
    gaps = sorted(((c, n, lf.get(c, 0)) for c, n in gf.items()), key=lambda x: -(x[1] - x[2]))
    stage = ""
    try:
        r = subprocess.run(["python3", os.path.join(HERE, "stage.py"), "--json"], cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        stage = (json.loads(r.stdout or "{}").get("stage") or "")
    except Exception:
        pass
    L = ["# P2W Google Verify - Run Report", "",
         "**%s · %s IST%s**" % (d, t, (" · stage " + stage) if stage else ""), "",
         "> %d of %d measured in Google, %d refused on page count. Google passes every check on %d;"
         " LibreOffice on %d of the same %d." % (scored, scored + refused, refused, gclean, lclean, scored), "",
         # THE CHECK SET HAS GROWN AND NOT EVERY DOCUMENT HAS CAUGHT UP. "passes all 42" was a
         # hard-coded 42 that stopped being the standard when the set reached 47. Measured 24 Nov:
         # all 35 clean documents were scored against 42 checks, and all 62 documents scored against
         # the current 47 fail. So "35 pass" is the best case of an older standard, and a reader who
         # takes it as today's number is being told something better than the truth. The count is now
         # derived from the results, and a mixed set is stated rather than resolved silently.
         "| checks applied | **%s** |" % _checks_applied(),
         "| measured against the current set | **%d of %d** |" % (_on_current(), scored),
         "## Measured", "",
         "| | |", "|:--|--:|",
         "| scored | **%d** |" % scored,
         "| refused on page count | **%d** |" % refused,
         "| clean in Google | **%d** |" % gclean,
         "| clean in LibreOffice | **%d** |" % lclean,
         ""]
    if gaps:
        L += ["## Checks Google fails and LibreOffice does not", "",
              "| check | Google | LibreOffice |", "|:--|--:|--:|"]
        for c, g, l in gaps[:8]:
            if g - l <= 0:
                continue
            L.append("| `%s` | **%d** | %d |" % (esc(c), g, l))
        L.append("")
        top = gaps[0]
        L += ["The first row is the class to take: `%s`, %d documents in Google against %d in"
              " LibreOffice." % (esc(top[0]), top[1], top[2]), ""]
    return "\n".join(L)


def watchdog():
    d, t = stamp()
    out = ""
    try:
        r = subprocess.run(["python3", os.path.join(HERE, "health.py"), "--json"], cwd=ROOT,
                           capture_output=True, text=True, timeout=180)
        out = r.stdout or ""
    except Exception:
        pass
    h = {}
    try:
        h = json.loads(out)
    except Exception:
        pass
    stages = need(h.get("stages") or {}, "health.py printed no stages")
    need(h.get("corpus"), "health.py reports a corpus of 0 - there is nothing to watch")
    stopped = [k for k, v in stages.items() if v.get("state") == "stopped"]
    rows = progress_rows()
    L = ["# P2W Watchdog - Run Report", "",
         "**%s · %s IST**" % (d, t), "",
         "> %s" % ("**%d stage(s) stopped: %s**" % (len(stopped), ", ".join(stopped)) if stopped
                   else "Nothing is stopped."), "",
         "## Stages", "",
         "| stage | state | progress | age |", "|:--|:--|--:|--:|"]
    for name in ("measure-google", "matrix", "classify", "fix", "txt"):
        v = stages.get(name) or {}
        prog = ""
        if v.get("done") is not None and v.get("of"):
            prog = "%d of %d" % (v["done"], v["of"])
        elif v.get("clean") is not None:
            prog = "%d clean, %d failing" % (v["clean"], v.get("failing") or 0)
        state = v.get("state") or "-"
        mark = "**%s**" % state if state == "stopped" else state
        # health.py uses a large sentinel for "no evidence at all" and it was printed as a real age:
        # "measure-google stopped, 1000000000.0 h" is 114,000 years and reads as a measurement. A
        # sentinel is not a number; show it as one dash.
        age = v.get("age_h")
        age_s = "\u2014" if (age is None or age >= 1e6) else "%.1f h" % age
        L.append("| %s | %s | %s | %s |" % (name, mark, prog, age_s))
    L.append("")
    if len(rows) >= 2:
        cur, prev = rows[-1], rows[-2]
        L += ["## Trend", "",
              "| | %s | %s | |" % (prev[0], cur[0]), "|:--|--:|--:|:--|"]
        for i, label in ((1, ".docx open"), (2, ".txt failing"), (3, "Google measured"),
                         (4, "Google clean")):
            try:
                a, b = int(prev[i]), int(cur[i])
                delta = b - a
                L.append("| %s | %d | **%d** | %s |" % (label, a, b,
                         ("%+d" % delta) if delta else "no change"))
            except (ValueError, IndexError):
                pass
        L.append("")
    L += ["## What this pass did", "",
          "* Read health.py, health.py --stalled, stage.py, progress.py and round.py --phase.",
          "* %s" % ("**A stage is stopped** - see BLOCKERS.md." if stopped else "Nothing needed moving.")]
    # A PASS THAT REPAIRED AN INSTRUMENT DID SOMETHING, AND "Nothing needed moving" WOULD SAY IT DID NOT.
    # The txt row reads `superseded` when the table is newer than the engine and the two scripts that
    # can change a .txt score; that state only exists because a watchdog pass put it there, so the
    # report says so rather than reporting silence over a change it made.
    if (stages.get("txt") or {}).get("state") == "superseded":
        L.append("* The .txt table is newer than the engine, verify_txt.py and restamp_txt.py, so it is "
                 "current and not late - see BLOCKERS.md.")
    L.append("")
    return "\n".join(L)


def apk():
    d, t = stamp()
    tag = sh("git describe --tags --abbrev=0 2>/dev/null").strip() or "-"
    ver = ""
    try:
        txt = open(os.path.join(ROOT, "app", "build.gradle"), encoding="utf-8").read()
        import re
        m = re.search(r'versionName\s+"([^"]+)"', txt)
        ver = m.group(1) if m else "-"
    except Exception:
        ver = "-"
    r = round_state()
    phase = r.get("phase", "?")
    rnd = "%s of %s" % (r.get("round", "?"), r.get("rounds_total", "?"))
    ready = (phase == "done")
    L = ["# KavoPDF APK - Run Report", "",
         "**%s · %s IST**" % (d, t), "",
         "> %s" % ("All rounds are finished - a release is due." if ready
                   else "Nothing shipped. Round %s is in phase `%s`, and the APK ships only when every"
                        " round is done." % (rnd, phase)), "",
         "## Release", "",
         "| | |", "|:--|:--|",
         "| Latest tag | `%s` |" % tag,
         "| versionName | `%s` |" % ver,
         "| Rounds | %s |" % rnd,
         "| Phase | `%s` |" % phase,
         "| Shipped this run | **%s** |" % ("yes" if ready else "no"),
         "", "## Gates", "",
         "| gate | result |", "|:--|:--|",
         "| signed build | required, never skipped |",
         "| no asset label | required |",
         "| engine change measured | required |",
         ""]
    return "\n".join(L)


BUILDERS = {"baseline": baseline, "classifier": classifier, "gverify": gverify,
            "watchdog": watchdog, "apk": apk}


def numbers(cron):
    """Every number the report for this cron can contain, one per line.

    THE GENERATOR AND THE VERIFIER MUST SHARE ONE SOURCE, OR THEY DISAGREE.
    They did, immediately: the gverify report said LibreOffice is clean on 122 documents - true, counted
    from benchmarks/gverify-lo - and the verifier refused it, because it was comparing against what
    gverify.py --report prints and that tool does not print that figure. A generator whose numbers the
    checker cannot see is a generator that fails its own check.

    So the generator publishes what it used. A fabricated number is still caught: it is not in here.
    """
    import re
    out = []
    try:
        text = BUILDERS[cron]()
    except Exception:
        return ""
    for m in re.finditer(r"\d+(?:\.\d+)?", text):
        out.append(m.group(0))
    return "\n".join(sorted(set(out)))


def main(argv):
    cron = "baseline"
    if "--for" in argv:
        i = argv.index("--for") + 1
        if i < len(argv):
            cron = argv[i].strip().lower()
    if "--numbers" in argv:
        print(numbers(cron))
        return 0
    fn = BUILDERS.get(cron)
    if not fn:
        print("unknown cron %r - one of: %s" % (cron, ", ".join(sorted(BUILDERS))), file=sys.stderr)
        return 2
    try:
        print(fn())
    except NoData as e:
        print("refused: %s" % e, file=sys.stderr)
        print("A report about nothing is not a report. Check the source, then run this again.",
              file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
