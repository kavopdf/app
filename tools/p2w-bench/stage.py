#!/usr/bin/env python3
"""stage.py - the one file every cron reads to know what to do next.

FIVE CRONS RUN ON THE SAME REPOSITORY and until now each one decided for itself what phase it was in.
The baseline measured with LibreOffice, the classifier classified that table, the fixer fixed against
it, and a fifth cron measures the same documents through Google - and nothing in any of them said
which of those numbers the work should be aimed at. That is how a pipeline spends a month and never
converges.

This is the coordination point. One state file, written by whichever cron finished a stage, read by
every other cron before it does anything:

    python3 tools/p2w-bench/stage.py            # what stage are we in, and what is next
    python3 tools/p2w-bench/stage.py --set <s>  # advance, only if the condition holds

STAGES, in order. A stage is not left until its exit condition is measured, never asserted.

    measure-google   Google has a result for fewer than all documents. gverify.py measures 20 a run.
                     exit: measured == total
    classify         The classifier groups the Google failures into classes.
                     exit: DEFECT-CLASSES has a row for every failing document
    fix              The fixer takes ONE class at a time, smallest first, and changes the engine only
                     where a measurement says the change helps.
                     exit: no class left with an open document
    ship             Every round is finished and nothing has been published for this corpus.

WHAT THIS DELIBERATELY DOES NOT DO. It does not decide anything a measurement can decide. It does not
carry a list of classes, a list of documents or a list of checks - all three come from the results. It
only records which stage the evidence says we are in, so that five crons do not disagree about it.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
STATE = os.path.join(HERE, "STAGE.json")
GVERIFY = os.path.join(ROOT, "benchmarks", "gverify")
CORPUS = "/scratch/work/p2w/corpus"
RANKING = os.path.join(ROOT, "benchmarks", "RANKING.csv")

ORDER = ["measure-google", "classify", "fix", "ship"]


def _json(p, default=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save(d):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)


def _corpus_names():
    """The documents that exist. The corpus is whatever is on disk, never a number written down."""
    if os.path.isdir(CORPUS):
        n = [f[:-4] for f in os.listdir(CORPUS) if f.endswith(".pdf")]
        if n:
            return sorted(n)
    # A cron sandbox starts empty; fall back to the committed table, which lists the same documents.
    try:
        import csv
        with open(RANKING, encoding="utf-8") as f:
            return sorted(r["document"] for r in csv.DictReader(f) if r.get("document"))
    except Exception:
        return []


def measured():
    """How many documents have a Google result, and how many were refused rather than scored."""
    if not os.path.isdir(GVERIFY):
        return 0, 0
    ok = refused = 0
    for f in os.listdir(GVERIFY):
        if not f.endswith(".json"):
            continue
        d = _json(os.path.join(GVERIFY, f), {})
        if d.get("status") == "page_count_refused":
            refused += 1
        else:
            ok += 1
    return ok, refused


def failing():
    """Documents with at least one failing check, from the Google results."""
    out = []
    if not os.path.isdir(GVERIFY):
        return out
    for f in sorted(os.listdir(GVERIFY)):
        if not f.endswith(".json"):
            continue
        d = _json(os.path.join(GVERIFY, f), {})
        if d.get("status") == "page_count_refused":
            continue
        if d.get("failed"):
            out.append(f[:-5])
    return out


def compute():
    """Which stage the evidence says we are in. Nothing here is hard-coded except the order."""
    names = _corpus_names()
    total = len(names)
    ok, refused = measured()
    done = ok + refused
    bad = failing()

    if total and done < total:
        return {"stage": "measure-google", "total": total, "measured": done,
                "scored": ok, "refused": refused,
                "next": "measure %d more through Google" % min(20, total - done)}
    if bad:
        # Classification is done when the table names a class for every failing document.
        classes = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")
        have = os.path.getmtime(classes) if os.path.exists(classes) else 0
        newest = 0
        if os.path.isdir(GVERIFY):
            for f in os.listdir(GVERIFY):
                newest = max(newest, os.path.getmtime(os.path.join(GVERIFY, f)))
        if have < newest:
            return {"stage": "classify", "total": total, "measured": done,
                    "failing": len(bad),
                    "next": "classify %d failing documents - the table is older than the results"
                            % len(bad)}
        return {"stage": "fix", "total": total, "measured": done, "failing": len(bad),
                "next": "fix one class at a time; %d documents still fail a check" % len(bad)}
    return {"stage": "ship", "total": total, "measured": done, "failing": 0,
            "next": "every document passes all 42 checks - nothing to ship unless a release is due"}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--set")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    cur = compute()
    prev = _json(STATE, {}) or {}
    cur["previous"] = prev.get("stage")
    cur["changed"] = prev.get("stage") != cur["stage"]

    if a.set:
        # ADVANCING IS NOT SOMETHING A RUN MAY DO BY SAYING SO. The stage is computed from the
        # results every time; --set only records that this run acted on it, so the next run can say
        # what the one before it did.
        if a.set not in ORDER:
            print("unknown stage: %s (one of %s)" % (a.set, ", ".join(ORDER)))
            return 2
        if a.set != cur["stage"]:
            print("refused: the evidence says %s, not %s. Fix the evidence, not the label."
                  % (cur["stage"], a.set))
            return 1
        cur["acted_by"] = os.environ.get("STAGE_ACTOR", "unknown")
        _save(cur)
        print("%s recorded" % a.set)
        return 0

    _save(cur)
    if a.json:
        print(json.dumps(cur, indent=1))
        return 0

    print("stage   : %s%s" % (cur["stage"], "  (changed from %s)" % cur["previous"]
                              if cur["changed"] and cur["previous"] else ""))
    print("corpus  : %d documents" % cur["total"])
    print("measured: %d through Google (%d scored, %d refused)"
          % (cur["measured"], cur.get("scored", 0), cur.get("refused", 0)))
    if cur.get("failing"):
        print("failing : %d documents" % cur["failing"])
    print("next    : %s" % cur["next"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
