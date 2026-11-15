#!/usr/bin/env python3
"""Is the measure phase finished? One question, one answer.

WHY THIS FILE WAS REWRITTEN

It used to read BASELINE.md and RESULTS.jsonl, because those are what the old verifier
wrote. The measurement layer is now benchmarks/p2w.py and it writes benchmarks/RANKING.csv.
Nothing wrote the old files any more, so this gate was answering a question about a corpus
that no longer existed:

  rows()          returned []  -> 0 scored, 0 total
  store_rows()    returned []  -> 0 in the store
  consistent      (0 == 0 and no duplicates)  ->  TRUE, vacuously

A gate whose every check passes because it is reading nothing is not a gate. Worse, the
vacuous truth meant the phase could advance with no measurement done at all - and if the
old txt_gap.py happened to be absent, the same gate refused for ever instead. Both failure
modes look like the pipeline working from the outside.

WHAT IT READS NOW

  benchmarks/RANKING.csv    one row per document; share5 is the score
  EXEMPT.json               documents whose failure to measure is accepted, with a reason

The rules, unchanged in spirit:

  every row scored          a row with no share5 was not measured
  MEASURE-ERROR blocks      unless the document is exempted. It is recorded, never dropped,
                            and never silently counted as done.
  no duplicate documents    two rows for one document means one of them is a defect in the
                            pipeline, not a document to score
  a corpus must exist       zero documents is not a finished measure phase

    python3 tools/p2w-bench/measure_gate.py            # human answer, exit 0 or 1
    python3 tools/p2w-bench/measure_gate.py --quiet    # exit code only
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
RANKING = os.path.join(ROOT, "benchmarks", "RANKING.csv")
STATE = os.path.join(ROOT, "benchmarks", "STATE.json")
ROUND = os.path.join(HERE, "ROUND.json")
EXEMPT = os.path.join(HERE, "EXEMPT.json")

# The corpus is 211 synthetic documents plus whatever real ones sit in
# benchmarks/realworld/. The floor exists so that a corpus that failed to build - zero
# rows, or a handful - cannot be read as "everything measured".
SYNTHETIC = 211


def exempt():
    """Documents whose measurement failure is accepted. docx and txt are separate sets."""
    data = {"docx": {}, "txt": {}}
    if os.path.exists(EXEMPT):
        try:
            with open(EXEMPT, encoding="utf-8") as f:
                raw = json.load(f)
            for half in ("docx", "txt"):
                if isinstance(raw.get(half), dict):
                    data[half] = raw[half]
        except (ValueError, OSError):
            pass
    return data


def expected_docs():
    """How many documents the corpus should hold: 211 synthetic + the real ones."""
    real = os.path.join(ROOT, "benchmarks", "realworld")
    n = 0
    if os.path.isdir(real):
        n = len([f for f in os.listdir(real) if f.lower().endswith(".pdf")])
    return SYNTHETIC + n


def read_ranking():
    """[(document, score_or_None, problem)] from RANKING.csv."""
    out = []
    if not os.path.exists(RANKING):
        return out
    with open(RANKING, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            doc = (r.get("document") or "").strip()
            if not doc:
                continue
            raw = (r.get("share5") or "").strip()
            try:
                score = float(raw)
            except (TypeError, ValueError):
                score = None
            out.append((doc, score, (r.get("problem") or "").strip()))
    return out


def duplicates(names):
    seen, dups = set(), set()
    for n in names:
        if n in seen:
            dups.add(n)
        seen.add(n)
    return sorted(dups)


def round_stamp():
    """(state_round, phase_round) - which round the committed numbers belong to, and
    which round the machine is in.

    A closed round keeps its RANKING.csv, so "every row scored" survives the boundary and
    a new round would inherit the previous one's finished table. Comparing the two stamps
    is what forces a fresh measurement to happen before the phase can move again.
    """
    sr = pr = None
    try:
        sr = json.load(open(STATE, encoding="utf-8")).get("round")
    except (ValueError, OSError):
        pass
    try:
        pr = json.load(open(ROUND, encoding="utf-8")).get("round")
    except (ValueError, OSError):
        pass
    return sr, pr


def state():
    ex = exempt()
    ranking = read_ranking()
    total = len(ranking)
    scored = [d for d, s, _ in ranking if s is not None]
    unscored = [(d, p) for d, s, p in ranking if s is None]
    # An unscored row blocks unless the document is explicitly exempted.
    blocked = [(d, p) for d, p in unscored if d not in ex["docx"]]
    return {
        "total": total,
        "scored": len(scored),
        "expected": expected_docs(),
        "unscored": unscored,
        "blocked": blocked,
        "dup": duplicates([d for d, _, _ in ranking]),
        "exempt_docx": len(ex["docx"]),
        "exempt_txt": len(ex["txt"]),
    }


def main(argv):
    s = state()
    problems = []

    sr, pr = round_stamp()
    if pr is not None and sr != pr:
        problems.append(
            "the committed measurement is for round %s, the machine is in round %s - "
            "the baseline must re-measure before this round can advance"
            % (sr if sr is not None else "?", pr))

    if s["total"] == 0:
        problems.append("RANKING.csv is missing or empty - nothing has been measured")
    elif s["total"] < s["expected"]:
        problems.append("RANKING.csv holds %d documents, the corpus should hold %d - "
                        "the measurement did not cover the corpus"
                        % (s["total"], s["expected"]))

    if s["dup"]:
        problems.append("%d document(s) appear more than once in RANKING.csv: %s"
                        % (len(s["dup"]), ", ".join(s["dup"][:5])))

    if s["blocked"]:
        problems.append("%d document(s) could not be measured and are not exempted: %s"
                        % (len(s["blocked"]),
                           ", ".join("%s (%s)" % (d, p or "no problem name")
                                     for d, p in s["blocked"][:5])))

    ok = not problems

    if "--quiet" not in argv:
        print("docx   %d/%d scored, %d exempt, %d blocking, %d expected"
              % (s["scored"], s["total"], s["exempt_docx"], len(s["blocked"]),
                 s["expected"]))
        print("round  measurement %s, machine %s" % (sr if sr is not None else "?",
                                                     pr if pr is not None else "?"))
        for p in problems:
            print("  - %s" % p)
        print("READY - every document measured" if ok else "NOT READY")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
