#!/usr/bin/env python3
"""ratchet_google.py - the ratchet, asked of the renderer the user opens.

WHY THIS EXISTS (24 Nov)

`ratchet.py` is the tool that enforces non-negotiable 3, "no document gets worse".
It reads `BASELINE.md` and `RESULTS.jsonl`, and `RETIRED.md` says of `BASELINE.md`:

    "the old check-id baseline: one row per document, a 40/58 score and a list of
     failed check ids ... what replaced it: benchmarks/RANKING.csv"

So the ratchet was gating a pipeline that no longer runs. Measured on 24 Nov, on a
clean tree at c618445f:

    $ python3 tools/p2w-bench/ratchet.py --check
    instrument                : 47 checks (sha 97b6067807c2)
    documents scored this run : 211 of 211 rows
    compared against a mark   : 0
    NOT COMPARED: 211 row(s) and 0 mark(s) are counted out of a universe the
      instrument does not have (47). A count out of 59 is not a count out of 47 ...
    UNMEASURED - the bar was not asked: 211 of 211 document(s) could not be
      compared, and 0 were.

211 of 211 UNMEASURED is not a gate that is passing and it is not a gate that is
failing. It is a gate that cannot be asked, and it cannot become askable by
measuring harder: the store's denominator (59) is a different instrument's, so no
amount of new measurement reconciles it. That is why the five "kept, never
ratcheted at corpus scale" items in `pending.py` have never closed - the tool that
would close them refuses to compare anything - and `pending.py` is itself a gate
("a run may not take a new class while it lists something"), so the whole pipeline
sat behind it.

WHY A SEPARATE FILE AND NOT A PATCH TO ratchet.py

`ratchet.py` is 824 lines of accumulated reasoning about count-vs-universe, and its
guard is correct for the store it was written for. The live store is a different
shape and needs a different comparison, so this file reuses the VERDICT VOCABULARY
and none of the arithmetic:

    exit 0  PASS        every scored document was compared and none fell
    exit 1  FAIL        a document fell
    exit 2  REFUSED     no records to compare - cannot gate
    exit 3  UNMEASURED  nothing fell, but at least one document was not compared

Nothing in `ratchet.py` is changed, so the retired path keeps working exactly as it
did and nothing is deleted.

THE STORE: benchmarks/gverify/*.json - Google Docs, one record per document

That is the truth renderer (`FIXER-BRIEF.md`: "Google is the truth. LibreOffice is
a proxy that hides what the phone shows"). A record is

    {"name", "status", "rc", "passed", "total", "failed": [...], "engine"}

213 records at c618445f: 190 `status: ok`, 23 `page_count_refused`.

THE COMPARISON IS BY CHECK IDENTITY, NOT BY COUNT

A count is only meaningful against the universe it was counted out of, and in this
store the universe is per-document and variable: 126 records are out of 42, 62 out
of 47, 2 out of 44, because a check that does not apply to a document is not asked
of it. So `passed` alone cannot be compared across a mark and a re-measurement, and
`total` is not the instrument's size either.

The `failed` list is a set of check NAMES, and names survive a denominator change.
So a document FELL when it now fails a check that its mark did not fail:

    fell = failed_now - failed_at_mark        (non-empty -> FAIL, and name the checks)

That is the definition of "worse" a user would give, it is immune to the 42/47/44
drift, and it names the check that moved instead of printing two counts that differ.
A document ROSE when the new failed set is a proper subset of the mark's, and the
mark is then raised - the bar only ever goes up.

TWO THINGS THIS DELIBERATELY WILL NOT DO

1. It will not compare a mark to a measurement whose `total` differs from the mark's.
   A check that was never asked of a document at the mark cannot be said to have
   passed at the mark, so a mark out of 42 and a reading out of 47 are not
   like-for-like and this reports the document as UNMEASURED rather than guessing
   in either direction. Exit 3, never exit 0.
2. It will not treat a missing mark as a pass. A document seen for the first time
   sets its mark and is reported NEW, and a run that only sets marks exits 3 -
   because it compared nothing, and "compared nothing" is what printed PASS on the
   run that dropped two checks.

    python3 tools/p2w-bench/ratchet_google.py            # check and raise marks
    python3 tools/p2w-bench/ratchet_google.py --check    # do not raise a mark
    python3 tools/p2w-bench/ratchet_google.py --show     # the store, without comparing
    python3 tools/p2w-bench/ratchet_google.py --doc <name>   # one document, verbose
"""
import argparse
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
STORE = os.path.join(ROOT, "benchmarks", "gverify")
MARKS = os.path.join(HERE, "RATCHET-GOOGLE.json")
LEDGER = os.path.join(HERE, "UNMEASURED-GOOGLE.json")


def now():
    """IST, because every timestamp a human reads in this repo is IST."""
    return time.strftime("%Y-%m-%dT%H:%M:%S+05:30", time.gmtime(time.time() + 19800))


def write_json(path, payload):
    """Atomic: a half-written ledger reads as a smaller gap than there is."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def read_store():
    """{document: record} from benchmarks/gverify, keyed by the document name."""
    out = {}
    for path in sorted(glob.glob(os.path.join(STORE, "*.json"))):
        try:
            rec = json.load(open(path, encoding="utf-8"))
        except Exception as exc:
            out[os.path.basename(path)[:-5]] = {"status": "unreadable", "why": str(exc)}
            continue
        name = rec.get("name") or os.path.basename(path)[:-5]
        out[name] = rec
    return out


def load_marks():
    if os.path.exists(MARKS):
        try:
            return json.load(open(MARKS, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--check", action="store_true", help="do not raise a mark")
    ap.add_argument("--show", action="store_true", help="print the store, do not compare")
    ap.add_argument("--doc", default="", help="one document, verbose")
    ap.add_argument("--quiet", action="store_true")
    # A gate that can only ever print exit 3 is a gate nobody reads, and that is how the
    # retired one died. The 23 `page_count_refused` documents cannot be compared at all
    # (they drew the wrong number of pages, so there is no line-by-line comparison to
    # make), so the gap is structural and has to be ACCEPTED in writing or the tool is
    # decorative. Same rule as ratchet.py: the reason is mandatory, it goes on disk, and
    # --allow-stale still cannot turn a FALL into a pass.
    ap.add_argument("--allow-stale", action="store_true",
                    help="accept the documents that cannot be compared, with --reason")
    ap.add_argument("--reason", default="")
    # A universe change is not a fall and not a pass. When the instrument legitimately
    # asks a different number of checks of a document, its old mark is out of a set the
    # new reading is not out of, and the only honest ways forward are to re-mark it or to
    # leave it uncompared for ever. --recut is the first, with a reason, on the record.
    ap.add_argument("--recut", action="store_true",
                    help="re-mark the documents whose check universe changed, with --reason")
    a = ap.parse_args(argv)
    if a.recut and not a.reason.strip():
        print("refused: --recut needs --reason \"<why the mark is out of a different universe>\"")
        return 2
    if a.allow_stale and not a.reason.strip():
        print("refused: --allow-stale needs --reason \"<which documents you are not comparing,"
              " and why that is acceptable>\"")
        print("  A waiver is a statement about which documents were not compared. Without the")
        print("  statement the gap becomes a green light with no author.")
        return 2

    store = read_store()
    if not store:
        print("ratchet_google: no records in benchmarks/gverify - nothing to compare")
        print("  An empty store proves nothing about any document. Refusing to gate.")
        return 2

    marks = load_marks()

    if a.show:
        print("ratchet_google: %d record(s) in %s, %d mark(s) in %s"
              % (len(store), os.path.relpath(STORE, ROOT), len(marks),
                 os.path.basename(MARKS)))
        clean = sum(1 for r in store.values()
                    if r.get("status") == "ok" and not r.get("failed"))
        print("  status ok : %d   page_count_refused/other : %d   clean (no failed checks) : %d"
              % (sum(1 for r in store.values() if r.get("status") == "ok"),
                 sum(1 for r in store.values() if r.get("status") != "ok"), clean))
        return 0

    fell, rose, held, new, unmeasured, recut = [], [], [], [], [], []

    for doc in sorted(store):
        rec = store[doc]
        if a.doc and a.doc != doc:
            continue
        if rec.get("status") != "ok" or rec.get("total") is None:
            unmeasured.append((doc, "status %s" % rec.get("status")))
            continue
        failed_now = frozenset(rec.get("failed") or [])
        total_now = int(rec["total"])
        mark = marks.get(doc)
        if not mark:
            new.append((doc, len(failed_now), total_now))
            if not a.check:
                marks[doc] = {"failed": sorted(failed_now), "total": total_now,
                              "passed": int(rec.get("passed") or 0),
                              "engine": rec.get("engine"), "at": now()}
            continue
        mark_failed = frozenset(mark.get("failed") or [])
        mark_total = mark.get("total")
        if mark_total is not None and int(mark_total) != total_now:
            if a.recut and not a.check:
                marks[doc] = {"failed": sorted(failed_now), "total": total_now,
                              "passed": int(rec.get("passed") or 0),
                              "engine": rec.get("engine"), "at": now()}
                recut.append((doc, mark_total, total_now))
                continue
            unmeasured.append((doc, "universe changed: mark x/%s, now x/%d"
                               % (mark_total, total_now)))
            continue
        newly = failed_now - mark_failed
        if newly:
            fell.append((doc, sorted(newly), rec.get("engine")))
            continue
        if failed_now < mark_failed:
            rose.append((doc, sorted(mark_failed - failed_now)))
            if not a.check:
                marks[doc] = {"failed": sorted(failed_now), "total": total_now,
                              "passed": int(rec.get("passed") or 0),
                              "engine": rec.get("engine"), "at": now()}
            continue
        held.append(doc)

    compared = len(fell) + len(rose) + len(held) + len(recut)
    if recut:
        print("  re-marked - universe changed : %d" % len(recut))
        for doc, was, isnow in recut[:10]:
            print("      %-46s x/%s -> x/%d" % (doc[:46], was, isnow))
    verdict = ("FAIL" if fell else
               "UNMEASURED" if (unmeasured or (new and not compared)) else "PASS")

    print("ratchet_google - Google Docs, benchmarks/gverify")
    print("  records                 : %d" % len(store))
    print("  compared against a mark : %d" % compared)
    print("  new - first mark        : %d" % len(new))
    print("  not compared            : %d" % len(unmeasured))
    print("  held                    : %d" % len(held))
    print("  rose                    : %d" % len(rose))
    print("  FELL                    : %d" % len(fell))

    if fell:
        print()
        print("  A DOCUMENT GOT WORSE. This is the one thing that may not happen:")
        for doc, checks, engine in fell[:25]:
            print("      %-46s now fails %s" % (doc[:46], ", ".join(checks)))
        if len(fell) > 25:
            print("      ... and %d more" % (len(fell) - 25))
    if rose:
        for doc, checks in rose[:10]:
            print("      rose  %-46s no longer fails %s" % (doc[:46], ", ".join(checks)))
    if unmeasured:
        print()
        print("  NOT COMPARED - a document that was not compared has not held its bar:")
        for doc, why in unmeasured[:15]:
            print("      %-46s %s" % (doc[:46], why))
        if len(unmeasured) > 15:
            print("      ... and %d more" % (len(unmeasured) - 15))

    if not a.check and (new or rose):
        write_json(MARKS, marks)
        print("  marks written to %s (%d total)" % (os.path.basename(MARKS), len(marks)))

    waived = bool(a.allow_stale and not fell)
    if waived:
        write_json(os.path.join(HERE, "WAIVER-GOOGLE.json"), {
            "reason": a.reason.strip(), "written_at": now(),
            "not_compared": {d: w for d, w in unmeasured},
            "counts": {"compared": compared, "not_compared": len(unmeasured)},
        })
        print("  waiver recorded: %s" % os.path.basename(os.path.join(HERE, "WAIVER-GOOGLE.json")))

    write_json(LEDGER, {
        "verdict": verdict, "waived": waived, "reason": a.reason.strip(), "written_at": now(),
        "store": os.path.relpath(STORE, ROOT),
        "counts": {"records": len(store), "compared": compared, "new": len(new),
                   "not_compared": len(unmeasured), "held": len(held),
                   "rose": len(rose), "fell": len(fell)},
        "fell": [{"doc": d, "checks": c} for d, c, _e in fell],
        "not_compared": {d: w for d, w in unmeasured},
    })

    if fell:
        print()
        print("  FAIL - %d document(s) fell. Nothing may be committed through this." % len(fell))
        return 1
    if unmeasured or (new and not compared):
        print()
        if waived:
            print("  PASS WITH WAIVER - %d document(s) compared, none fell; %d could not be"
                  % (compared, len(unmeasured)))
            print("  compared and that gap is accepted in writing. Ledger: %s"
                  % os.path.basename(LEDGER))
            return 0
        print("  UNMEASURED - nothing fell, but this is not a pass: %d document(s) were"
              % (len(unmeasured) + (len(new) if not compared else 0)))
        print("  never asked. Ledger: %s" % os.path.basename(LEDGER))
        return 3
    print()
    print("  PASS - %d document(s) compared against their Google high-water mark, none fell."
          % compared)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
