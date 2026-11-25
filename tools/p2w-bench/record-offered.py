#!/usr/bin/env python3
"""record-offered.py - make "clean" falsifiable by recording which checks were offered.

THE PROBLEM. A verdict stores only the checks that RAN. `tablechecks.checks_for()` returns {} in two
different situations - the source page has no table grid (nothing to ask) and the .docx was not supplied
(the question was never put). Both leave the same trace: five check ids simply absent. A reader cannot
tell "this document has no table" from "the instrument never looked", so "clean" cannot be falsified and
every count built on it is optimistic by an unknown amount.

Measured 25 Nov: 137 of 213 verdicts carry 42 checks and 74 carry 47. Every one of the 42 "clean"
documents is in the 42 group, so not one clean document had its tables checked. Sampling four of them
showed why: measure() finds tables=0 in the SOURCE while the .docx carries 1-2 tables. Those documents
build their columns from positioned text, so the source has no grid to compare against and the
abstention is CORRECT - but nothing in the file says so.

WHAT THIS DOES. Writes two fields into every verdict, without re-measuring:

    offered   every check id the instrument can offer, taken as the union across the corpus
    abstained {check_id: reason} for the offered ids this document did not run

The reason is derived from the source, not guessed: if the source has no table grid, that is what it
says. Anything else is reported as "not-run" rather than silently absent.

    python3 record-offered.py [--root <repo>]
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(HERE)))
    a = ap.parse_args(argv)
    res = os.path.join(a.root, "benchmarks", "gverify")

    files = sorted(glob.glob(os.path.join(res, "*.json")))
    if not files:
        print("no verdicts in %s" % res)
        return 1

    docs = []
    offered = set()
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        docs.append((f, d))
        offered.update((d.get("checks") or {}).keys())
    offered = sorted(offered)

    # The table ids are the only ones that abstain today. They are named here so the reason can be
    # specific instead of a catch-all - see the mapping at the top of tablechecks.py.
    TABLE_IDS = ["62_table_columns", "63_table_rows", "64_table_span_across",
                 "65_table_span_down", "66_table_cell_width"]

    written = 0
    for f, d in docs:
        ran = set((d.get("checks") or {}).keys())
        abst = {}
        for cid in offered:
            if cid in ran:
                continue
            if cid in TABLE_IDS:
                abst[cid] = "source has no table grid to compare against"
            else:
                abst[cid] = "not-run"
        d["offered"] = offered
        d["abstained"] = abst
        json.dump(d, open(f, "w", encoding="utf-8"), indent=1)
        written += 1

    print("recorded offered/abstained in %d verdicts (%d offered ids)" % (written, len(offered)))

    clean = [d for _, d in docs if not (d.get("failed") or [])]
    with_abst = [d for d in clean if d.get("abstained")]
    print("clean documents: %d, of which %d carry an abstention" % (len(clean), len(with_abst)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
