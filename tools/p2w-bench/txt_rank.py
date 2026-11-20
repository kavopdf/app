#!/usr/bin/env python3
"""txt_rank.py - score the .txt the way the .docx is scored, so the fixer can see it.

THE TXT WAS NEVER MEASURED. verify_txt.py has twelve named checks and its own docstring says why they
matter: "the pipeline measures the .docx path and nothing else... the .txt is never opened. So the
fixer cannot improve it: a defect it cannot see is a defect it cannot fix, and the .txt could break
outright without a single number moving." That was true when it was written and it stayed true -
RESULTS-TXT.jsonl does not exist, RANKING.csv has no txt column, and the fixer's prompt never mentions
the format.

This runs the twelve checks over every document and writes RANKING-TXT.csv, one row per document:

    document, applicable, passed, failed, abstained, failed_ids

A document meets the same 99% bar the .docx has when EVERY applicable check passes - a txt that fails
one of twelve is not 99% of a document, it is a document with a known defect. `abstained` is reported
separately and never counted as a pass.

    python3 tools/p2w-bench/txt_rank.py --limit 20
    python3 tools/p2w-bench/txt_rank.py --all
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
# THE TXT LIVES IN ITS OWN DIRECTORY. Nothing under tools/p2w-bench/txt/ is read by the .docx path,
# and nothing in the .docx path writes there, so a txt change cannot move a docx number by accident
# and a docx change cannot hide behind a txt score. The two formats share the ENGINE and nothing else.
TXT_DIR = os.path.join(HERE, "txt")
os.makedirs(TXT_DIR, exist_ok=True)
OUT = os.path.join(TXT_DIR, "RANKING-TXT.csv")
# THE TXT GRADES ITSELF AGAINST ITS OWN RECORDS, NOT AGAINST ITS OWN SCORE FILE.
#
# The ratchet used to compare each document with the previous row in OUT - the same file it was about
# to overwrite. That is the store grading itself, and it fails in the one case that matters: delete or
# reset OUT and every document is a first score, nothing is compared, and the ratchet prints "no
# document got worse" over an empty table. Measured: with OUT absent, two documents at 3 and 1
# failing checks both reported as clean.
#
# Two files fix it, and neither is read or written by anything on the .docx side:
#   RATCHET-TXT.json          the best failed-count each document has ever reached, plus the check
#                             universe it was reached under. Written only when a document improves.
#   RANKING-TXT-BASELINE.csv  the reference table, written once by --baseline and never by scoring.
MARKS = os.path.join(TXT_DIR, "RATCHET-TXT.json")
BASELINE = os.path.join(TXT_DIR, "RANKING-TXT-BASELINE.csv")
CORPUS = "/scratch/work/p2w/corpus"
TXT = "/scratch/work/p2w/out"

# LEGACY PATH. restamp_txt.py --apply is the supported way to write RANKING-TXT.csv now, and it is the
# one the brief gives. This tool still works when the work directories are present, and it must not
# pretend otherwise when they are not: in a fresh cron sandbox it exited 2 with no explanation.
if not (os.path.isdir(CORPUS) and os.path.isdir(TXT)):
    print("refused: this is the legacy ranking builder and it needs the work directories.")
    print("  %s and %s are not both present." % (CORPUS, TXT))
    print("  Use the supported path instead:")
    print("      python3 tools/p2w-bench/restamp_txt.py --run   # measure (after p2w.py built the corpus)")
    print("      python3 tools/p2w-bench/restamp_txt.py --apply # write RANKING-TXT.csv")
    raise SystemExit(3)


def _universe():
    """(ids, sha12, error) for the .txt verifier, asked of the instrument right now.

    A mark is only comparable with a score taken under the same set of checks. Adding or dropping a
    check moves this sha, and every mark stamped with the old one is stale - not compared, not
    carried forward, and not silently replaced. Same rule the .docx ratchet learned the hard way.
    """
    try:
        sys.path.insert(0, HERE)
        from instrument import live_universe
        return live_universe(True)
    except Exception as e:
        return [], "", "instrument.live_universe failed: %s" % e


def docs():
    out = []
    if not os.path.isdir(CORPUS):
        return out
    for f in sorted(os.listdir(CORPUS)):
        if f.endswith(".pdf"):
            d = f[:-4]
            if os.path.exists(os.path.join(TXT, d + ".txt")):
                out.append(d)
    return out


def score(doc):
    pdf = os.path.join(CORPUS, doc + ".pdf")
    txt = os.path.join(TXT, doc + ".txt")
    j = os.path.join("/tmp", "txtcheck-%s.json" % doc[:40])
    try:
        r = subprocess.run(["python3", os.path.join(HERE, "verify_txt.py"), pdf, txt, "--json", j],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        return {"document": doc, "applicable": 0, "passed": 0, "failed": -1,
                "abstained": 0, "failed_ids": "error:%s" % type(e).__name__}
    # rc=1 MEANS CHECKS FAILED, NOT THAT THE RUNNER BROKE. verify_txt exits 1 whenever any check
    # fails, which is the normal way to report a defective txt - treating it as an error threw away
    # the result for exactly the documents that needed it. Only a missing JSON is an error.
    if not os.path.exists(j):
        return {"document": doc, "applicable": 0, "passed": 0, "failed": -1,
                "abstained": 0, "failed_ids": "error:rc%d" % r.returncode}
    try:
        data = json.load(open(j, encoding="utf-8"))
    except Exception:
        return {"document": doc, "applicable": 0, "passed": 0, "failed": -1,
                "abstained": 0, "failed_ids": "error:json"}
    # the checks dict is keyed by the check id; the entry itself carries no id field
    ch = data.get("checks") or {}
    judged = [(k, v) for k, v in ch.items() if v.get("applicable")]
    failed = [(k, v) for k, v in judged if not v.get("ok")]
    return {"document": doc,
            "applicable": len(judged),
            "passed": len(judged) - len(failed),
            "failed": len(failed),
            "abstained": len(ch) - len(judged),
            "failed_ids": " ".join(sorted(k for k, _ in failed)) or "-"}


def main(argv):
    if len(argv) < 2:
        print("usage: txt_rank.py --limit N | --all | --rescore | --ratchet")
        print("  scores the next N UNSCORED documents into tools/p2w-bench/txt/RANKING-TXT.csv")
        return 2
    ds = docs()
    if not ds:
        print("no documents found - is the corpus built?")
        return 2
    # SCORE WHAT IS NOT SCORED YET. Taking the first n every time re-scored the same documents and
    # left the rest of the corpus invisible, which is the shape of the bug that produced a day of
    # "0 of 213". --rescore forces everything; --all means the whole corpus either way.
    if os.path.exists(OUT) and "--rescore" not in argv:
        import csv as _c
        done = {r["document"] for r in _c.DictReader(open(OUT, encoding="utf-8"))}
        fresh = [d for d in ds if d not in done]
        if fresh:
            ds = fresh
    # --baseline writes the reference table ONCE, from whatever the store holds now, and refuses to
    # overwrite it. Scoring never touches it: a file that scoring could rewrite is a file that
    # records the last measurement rather than the reference the measurements are judged against.
    if "--baseline" in argv:
        if os.path.exists(BASELINE) and "--force" not in argv:
            print("  %s already exists - refusing to overwrite it." % os.path.basename(BASELINE))
            print("  It is the reference, not a log. Pass --force only if you mean to move the")
            print("  reference, and say why in the commit message.")
            return 2
        if not os.path.exists(OUT):
            print("  no %s to take a baseline from - score the corpus first" % os.path.basename(OUT))
            return 2
        import csv as _c, shutil as _sh
        _sh.copyfile(OUT, BASELINE)
        n = sum(1 for _ in _c.DictReader(open(BASELINE, encoding="utf-8")))
        print("  baseline written: %s (%d rows, taken from %s)"
              % (os.path.basename(BASELINE), n, os.path.basename(OUT)))
        return 0

    if "--all" not in argv:
        n = 20
        if "--limit" in argv:
            n = int(argv[argv.index("--limit") + 1])
        ds = ds[:n]
    rows = []
    for i, d in enumerate(ds):
        r = score(d)
        rows.append(r)
        if r["failed"] > 0:
            print("  %-40s %d/%d  FAIL %s" % (d[:40], r["passed"], r["applicable"], r["failed_ids"][:50]))
    # THE TXT RATCHET: NO DOCUMENT MAY GET WORSE.
    #
    # The docx has had one since the beginning - a change is kept only if no document regresses - and
    # the txt had none, because it had no scores. Now that it has scores it gets the same rule: a
    # document whose failing-check count goes UP between passes is a regression, and it is printed and
    # counted rather than quietly written over.
    old = {}
    if os.path.exists(OUT):
        import csv as _c
        for row in _c.DictReader(open(OUT, encoding="utf-8")):
            old[row["document"]] = row
    for r in rows:
        old[r["document"]] = {k: str(v) for k, v in r.items()}

    # THE RATCHET, AGAINST RATCHET-TXT.json AND NOTHING ELSE.
    marks = {}
    if os.path.exists(MARKS):
        try:
            _m = json.load(open(MARKS, encoding="utf-8"))
            marks = _m.get("marks") or {}
            marks_universe = (_m.get("instrument") or {}).get("sha")
        except (ValueError, OSError):
            marks, marks_universe = {}, None
    else:
        marks_universe = None

    ids, live_sha, live_err = _universe()
    unmeasured = not marks
    stale = bool(marks) and marks_universe != live_sha
    regressed = []
    if not unmeasured and not stale:
        for r in rows:
            m = marks.get(r["document"])
            if not m:
                continue                      # first score for this document - nothing to compare
            try:
                was, now = int(m.get("best_failed", 0)), r["failed"]
            except (TypeError, ValueError):
                continue
            if now > was:
                regressed.append((r["document"], was, now))

    # A mark is raised only when a document actually improves, so the file records the best each
    # document has ever reached rather than the last thing that happened to be measured.
    raised = 0
    if not stale:
        for r in rows:
            m = marks.setdefault(r["document"], {})
            try:
                best = int(m.get("best_failed", 10 ** 6))
            except (TypeError, ValueError):
                best = 10 ** 6
            if r["failed"] < best:
                m["best_failed"] = r["failed"]
                m["best_ids"] = r["failed_ids"]
                raised += 1
        json.dump({"instrument": {"checks": len(ids), "sha": live_sha, "tool": "verify_txt.py",
                                  "error": live_err or ""},
                   "marks": marks},
                  open(MARKS, "w", encoding="utf-8"), indent=1, sort_keys=True)
    import csv as _c
    fields = ["document", "applicable", "passed", "failed", "abstained", "failed_ids"]
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = _c.DictWriter(fh, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for d in sorted(old):
            w.writerow({k: old[d].get(k, "") for k in fields})
    clean = [r for r in rows if r["failed"] == 0 and r["applicable"] > 0]
    print()
    print("  scored %d this pass | %d clean | %d with a failed check | %d errors"
          % (len(rows), len(clean),
             len([r for r in rows if r["failed"] > 0]),
             len([r for r in rows if r["failed"] < 0])))
    print("  wrote %s" % OUT)
    if raised:
        print("  marks raised for %d document(s) -> %s" % (raised, os.path.basename(MARKS)))
    if unmeasured:
        print()
        print("  UNMEASURED - %s holds no marks, so nothing was compared." % os.path.basename(MARKS))
        print("  An empty marks file proves nothing about any document. This is not a pass.")
        print("  Every document scored above is a FIRST score; the next pass has something to")
        print("  compare against.")
        return 3
    if stale:
        print()
        print("  STALE MARKS - %s was stamped under a different set of checks." % os.path.basename(MARKS))
        print("      marks : %s" % (marks_universe or "none"))
        print("      live  : %s (%d checks)" % (live_sha or "unknown", len(ids)))
        print("  Not compared, not carried forward, and not replaced: the marks were left as they")
        print("  were. Re-measure the corpus, or reset with a reason if the universe really moved.")
        return 3
    if regressed:
        print()
        print("  RATCHET: %d document(s) got WORSE in the txt:" % len(regressed))
        for d, was, now in regressed:
            print("    %-40s %d failing -> %d" % (d[:40], was, now))
        return 1
    print("  ratchet: no document got worse")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
