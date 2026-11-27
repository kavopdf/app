#!/usr/bin/env python3
"""Decompose the commit gate's refusal into the documents a candidate change would release.

    python3 tools/p2w-bench/gate_decompose.py
    python3 tools/p2w-bench/gate_decompose.py --candidate FINDINGS/RANKING-rung0-FULL-CORPUS-28NOV.csv

WHY. `regress.py --check` answers one question - "does any document score worse than the 15 Nov
baseline?" - and prints ten names. The fixer needs a different question answered: *which documents
does this candidate change release, which does it cost, and what is left*. Two tables answer it, and
until now the answer was recomputed by hand in prose, once per run, from a different pair of files
each time.

This reads the same two columns `regress.py` reads (`share5`, compared absolutely) so its counts
agree with the gate by construction, and it prints the set difference against a candidate table.

NOT A GATE. It exits 0 whatever it finds. It changes nothing and writes nothing.
"""
import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CUR = os.path.join(ROOT, "benchmarks", "RANKING.csv")
BASE = os.path.join(ROOT, "benchmarks", "RANKING-BASELINE.csv")
TOL = 1e-9  # regress.py's tolerance: none. A hundredth of a percent of ink counts.


def load(path):
    with open(path, newline="") as fh:
        return {r["document"]: r for r in csv.DictReader(fh)}


def share5(row):
    try:
        return float(row["share5"])
    except (KeyError, TypeError, ValueError):
        return None


def worse_than(rows, base):
    """Documents whose share5 is above the baseline's, plus rows missing from the baseline."""
    out, missing = [], []
    for doc, row in rows.items():
        cur = share5(row)
        if cur is None:
            continue
        if doc not in base:
            missing.append(doc)
            continue
        b = share5(base[doc])
        if b is None:
            missing.append(doc)
            continue
        if cur > b + TOL:
            out.append((doc, b, cur, cur - b))
    out.sort(key=lambda t: -t[3])
    return out, missing


def self_contradicting(base):
    """Rows whose own columns say ink sits beyond the 5 px radius while share5 reads 0.00.

    max_pt is the largest displacement on the worst page. 5 px at DPI 150 is 2.4 pt, so a row
    with max_pt > 2.4 and share5 == 0.00 cannot be right: the metric is the share of ink beyond
    5 px, and max_pt > 2.4 says at least one pixel is beyond it. Two-decimal rounding of a
    handful of pixels is what makes the zero, and a zero floor is unreachable by construction.
    """
    out = []
    for doc, row in base.items():
        s5 = share5(row)
        try:
            mx = float(row["max_pt"])
        except (KeyError, TypeError, ValueError):
            continue
        if s5 is not None and s5 == 0.0 and mx > 2.4:
            out.append((doc, mx))
    out.sort(key=lambda t: -t[1])
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", default=None,
                    help="a RANKING-shaped CSV to compare against, instead of only the gate")
    ap.add_argument("--names", action="store_true", help="print every document, not the top 10")
    args = ap.parse_args(argv)

    cur, base = load(CUR), load(BASE)
    gate, gate_missing = worse_than(cur, base)
    print("baseline : %s (%d rows)" % (os.path.relpath(BASE, ROOT), len(base)))
    print("current  : %s (%d rows)" % (os.path.relpath(CUR, ROOT), len(cur)))
    print("gate says: %d document(s) worse than the 15 Nov baseline on share5" % len(gate))
    if gate_missing:
        print("           %d row(s) not comparable (missing from the baseline): %s"
              % (len(gate_missing), ", ".join(sorted(gate_missing)[:5])))
    print()

    floor = [(d, b, c) for d, b, c, _ in gate if b == 0.0]
    sub1 = [(d, b, c) for d, b, c, _ in gate if 0.0 < b and c <= 1.0]
    print("  of those %d:" % len(gate))
    print("    %-3d have a baseline of exactly 0.00 - a floor no change can hold" % len(floor))
    print("    %-3d are still inside the corpus's own clean bar (share5 <= 1.0)" % len(sub1))
    print()

    shown = gate if args.names else gate[:10]
    print("  worst first (baseline -> current, delta):")
    for doc, b, c, d in shown:
        print("    %-46s %6.2f -> %6.2f  (+%5.2f)" % (doc[:46], b, c, d))
    if not args.names and len(gate) > len(shown):
        print("    ... %d more (--names for all)" % (len(gate) - len(shown)))
    print()

    bad = self_contradicting(base)
    print("baseline rows that contradict themselves (share5 == 0.00 but max_pt > 2.4 pt): %d"
          % len(bad))
    for doc, mx in bad[:12]:
        mark = " <- also refused by the gate" if doc in {g[0] for g in gate} else ""
        print("    %-46s max_pt %5.2f%s" % (doc[:46], mx, mark))
    print()

    if not args.candidate:
        return 0
    cand_path = args.candidate if os.path.isabs(args.candidate) else os.path.join(ROOT, args.candidate)
    if not os.path.exists(cand_path):
        print("no such candidate table: %s" % args.candidate)
        return 1
    cand = load(cand_path)
    after, after_missing = worse_than(cand, base)
    before_set = {g[0] for g in gate}
    after_set = {a[0] for a in after}
    released = sorted(before_set - after_set)
    cost = sorted(after_set - before_set)
    print("candidate: %s" % os.path.relpath(cand_path, ROOT))
    print("  gate would say: %d document(s) worse  (%+d vs %d now)"
          % (len(after), len(after) - len(gate), len(gate)))
    print("  RELEASED by the candidate: %d" % len(released))
    for d in released:
        print("    - %s" % d)
    print("  COST by the candidate: %d" % len(cost))
    for d in cost:
        b = share5(base[d])
        print("    + %-44s %6.2f -> %6.2f" % (d[:44], b, share5(cand[d])))
    print("  still refused: %d" % len(after_set & before_set))
    if after_missing:
        print("  not comparable under the candidate: %s" % ", ".join(sorted(after_missing)[:5]))
    print()
    if after_set:
        print("VERDICT: the candidate does not clear the gate. %d document(s) would still be worse "
              "than the 15 Nov baseline, so a commit of it is still refused." % len(after_set))
    else:
        print("VERDICT: the candidate clears the gate on share5.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
