#!/usr/bin/env python3
"""Documents that have a .docx score but no .txt score.

Two different questions, and they need two different answers.

  --count                     THE BACKFILL GAP. Documents that appear in RESULTS.jsonl and
                              never in RESULTS-TXT.jsonl, at any round or engine. This is
                              the hole left by the day the .txt half wrote into a directory
                              that did not exist: those documents have a word row and no text
                              row, STEP 2 never revisits a filled row, and nothing else in
                              the pipeline would ever go back for them.

  --count --round R --engine E
                              THE ROUND GAP. Documents measured for the word file in round R
                              on engine E that have no text row for that same round and
                              engine. The backfill gap cannot see this one: after round 1 the
                              document is in both stores, so the doc-set gap reads 0 while a
                              round-2 .txt measurement has quietly failed and left round 1's
                              score standing in for it. A regression would then be invisible
                              to the .txt ratchet.

  --list N                    The first N documents of whichever gap was asked for.
  --all                       Ignore the limit.
  --exempt                    How many documents are exempted, per half.

A document listed under "txt" in EXEMPT.json is never counted in either gap. That file
exists so a document whose .txt genuinely cannot be produced cannot hold the pipeline
open forever: STEP 6 refuses to advance while a gap is non-zero, so one impossible
document would otherwise deadlock every round after it.

Exit 0 always: a gap of zero is a result, not a failure.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(HERE, "RESULTS.jsonl")
TXT = os.path.join(HERE, "RESULTS-TXT.jsonl")
EXEMPT = os.path.join(HERE, "EXEMPT.json")


def rows(path):
    """Every row in a store, as dicts. A missing store is an empty one."""
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("doc"):
                out.append(row)
    return out


def exempt_txt():
    """{document: reason} for the text half. Missing or broken file means none."""
    if not os.path.exists(EXEMPT):
        return {}
    try:
        with open(EXEMPT, encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError):
        return {}
    part = data.get("txt") or {}
    return part if isinstance(part, dict) else {}


def arg(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return default


def main(argv):
    want_round = arg(argv, "--round")
    want_engine = arg(argv, "--engine")
    limit = int(arg(argv, "--list", "10"))
    exempt = exempt_txt()

    docx_rows = rows(DOCX)
    txt_rows = rows(TXT)

    if want_round is not None or want_engine is not None:
        # Round gap: compare the same (round, engine, doc) triples.
        def key(r):
            return (str(r.get("round", "")), r.get("engine", ""), r["doc"])

        def keep(r):
            if want_round is not None and str(r.get("round", "")) != str(want_round):
                return False
            if want_engine is not None and r.get("engine", "") != want_engine:
                return False
            return True

        have = {key(r) for r in txt_rows if keep(r)}
        want = {key(r) for r in docx_rows if keep(r)}
        missing = sorted(doc for (_rnd, _eng, doc) in (want - have) if doc not in exempt)
    else:
        # Backfill gap: the document sets, ignoring round and engine.
        have = {r["doc"] for r in txt_rows}
        want = {r["doc"] for r in docx_rows}
        missing = sorted(d for d in (want - have) if d not in exempt)

    if "--exempt" in argv:
        print(len(exempt))
        return 0

    if "--count" in argv:
        print(len(missing))
        return 0

    if "--all" in argv:
        limit = len(missing)
    for name in missing[:limit]:
        print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
