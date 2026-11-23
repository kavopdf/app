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
    """How many documents the corpus should hold: 211 synthetic + the real ones, MINUS the exempt.

    AN EXEMPT DOCUMENT IS NOT IN THE TABLE, SO IT IS NOT MISSING FROM IT.
    This returned SYNTHETIC + real and nothing else, so it demanded 213 rows from a table that
    gate.py deliberately publishes with 212: gate.py re-applies EXEMPT.json after the copy and
    DROPS 416_many_tiny_pages rather than writing a share5 of 0.0 that means "unknown". The same
    file already reads EXEMPT.json twice - exempt() feeds `blocked`, which correctly skips the
    exempt document - so the gate held two answers to one question and refused the honest table
    with "the corpus should hold 213". Measured 23 Nov: 212 scored, 1 exempt, 0 blocking, and
    still NOT READY. A gate that cannot accept its own publisher's table blocks every engine
    change, which is the shape of the two runs that measured a fix and could not land it.
    """
    real = os.path.join(ROOT, "benchmarks", "realworld")
    n = 0
    if os.path.isdir(real):
        n = len([f for f in os.listdir(real) if f.lower().endswith(".pdf")])
    return SYNTHETIC + n - len(exempt()["docx"])


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

    # A COMPLETE TABLE CAN STILL BE FROM THE WRONG ENGINE, AND THIS GATE NEVER LOOKED.
    # It compared round stamps and row counts only, so on 22 Nov it printed "213/213 scored ...
    # READY - every document measured" for a table measured on 21 Nov 01:44, before commit
    # 2d44a3a2 changed how a doubled line is drawn. The docx stamp said 6c6cf642e13b7ed2 and the
    # tree was 226f7f2df3013ad7. A fixer reading READY has no way to learn why regress.py then
    # refused every .docx change as unmeasured, which is exactly what three runs in a row did.
    # The phase is 'measure' for a real reason and this is that reason, so it belongs in the gate.
    _stamp_docx = _live_docx = None
    try:
        import regress as _regress
        _stamp_docx = (_regress.load_stamp() or {}).get("docx")
        _live_docx = _regress.engine_fingerprint("docx")
    except Exception as _e:
        sys.stderr.write("measure_gate: cannot compare the docx engine (%s: %s) - the engine "
                         "check is SKIPPED for this run\n" % (type(_e).__name__, _e))
    if _stamp_docx and _live_docx and _stamp_docx != _live_docx:
        problems.append(
            "RANKING.csv was measured on docx engine %s and the tree is %s - the corpus has "
            "not been measured on this engine, so 'every document measured' is not true yet"
            % (_stamp_docx, _live_docx))
    # A MISSING STAMP IS NOT A PASS. The condition above needs both sides truthy, so an absent stamp
    # skipped the comparison entirely and the gate printed "READY - every document measured" for a
    # corpus nobody had claimed to measure. Measured 23 Nov: with the docx stamp removed the gate still
    # said READY, because "no claim" was read as "no problem". A table with no engine stamp cannot be
    # known to describe this engine, so it is not ready.
    if _live_docx and not _stamp_docx:
        problems.append(
            "RANKING.csv carries no docx engine stamp - there is no evidence it was measured on this "
            "engine (%s), so 'every document measured' is not true yet" % _live_docx)

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
        print("engine docx %s, tree %s" % (_stamp_docx or "?", _live_docx or "?"))
        for p in problems:
            print("  - %s" % p)
        print("READY - every document measured" if ok else "NOT READY")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
