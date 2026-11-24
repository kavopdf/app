#!/usr/bin/env python3
"""step_txt.py - what to fix in the .txt, worst class first, in one call.

The .docx has step.py: it names a class, its worst documents, and the exact commands. The .txt
had no equivalent, so a run that wanted to improve the .txt had to read RANKING-TXT.csv and work
out the ranking itself - which is the kind of step a run skips.

This does the same job for the .txt, and only for the .txt. It reads the four records that
classify_txt.py writes and prints a short brief:

    the worst class, how many documents it holds, and the worst documents in it
    what each of those documents' own failing checks are
    the commands to score, ratchet and gate

    python3 tools/p2w-bench/step_txt.py            the brief
    python3 tools/p2w-bench/step_txt.py --limit 8  more documents per class
    python3 tools/p2w-bench/step_txt.py --class t13_amount_columns   one class only

Exit 0 always unless there is nothing to work on, which exits 1 - a run that has no .txt work
left should be told that rather than guessing.

It writes nothing. Everything it prints is read from tools/p2w-bench/txt/.
"""
import csv, json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(HERE, "txt")
RANK = os.path.join(TXT, "RANKING-TXT.csv")
CAUSES = os.path.join(TXT, "CAUSES-TXT.json")
MARKS = os.path.join(TXT, "RATCHET-TXT.json")
BASELINE = os.path.join(TXT, "RANKING-TXT-BASELINE.csv")


def load():
    if not os.path.exists(RANK):
        return None
    out = []
    for r in csv.DictReader(open(RANK, encoding="utf-8")):
        try:
            app, bad = int(r.get("applicable") or 0), int(r.get("failed") or 0)
        except ValueError:
            continue
        if app <= 0 or bad < 0:
            continue
        ids = [c for c in (r.get("failed_ids") or "").split() if c.startswith("t") and "_" in c]
        out.append({"document": r["document"], "applicable": app, "failed": bad, "ids": ids})
    return out


def main(argv):
    rs = load()
    if rs is None:
        print("no %s - score the .txt first:" % os.path.basename(RANK))
        print("    python3 tools/p2w-bench/txt_gate.py --score 60")
        return 1

    failing = [r for r in rs if r["failed"] > 0]
    if not failing:
        print("  every document passes every applicable .txt check. Nothing to fix here.")
        return 1

    by_check = Counter()
    for r in failing:
        for cid in r["ids"]:
            by_check[cid] += 1

    only = None
    if "--class" in argv:
        only = argv[argv.index("--class") + 1]
    limit = 6
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])

    # A document that fails several checks is reachable from each of them, so the worst class is
    # the one that unlocks the most documents - not the one with the highest single score.
    order = [(c, n) for c, n in sorted(by_check.items(), key=lambda kv: (-kv[1], kv[0]))
             if only is None or c == only]
    if not order:
        print("  no failing document carries class %r" % only)
        return 1

    causes = {}
    if os.path.exists(CAUSES):
        try:
            causes = json.load(open(CAUSES, encoding="utf-8"))
        except (ValueError, OSError):
            pass

    print("  .txt: %d scored, %d failing, %d clean" % (len(rs), len(failing), len(rs) - len(failing)))
    print("  worst class: %s - %d document(s)" % (order[0][0], order[0][1]))
    print()
    for cid, n in order[:3]:
        docs = sorted([r for r in failing if cid in r["ids"]],
                      key=lambda r: (-r["failed"], r["document"]))[:limit]
        print("  %s  (%d document%s)" % (cid, n, "" if n == 1 else "s"))
        for r in docs:
            c = (causes.get(r["document"]) or {}).get("cause", "")
            print("      %-44s %d/%d failing   %s"
                  % (r["document"][:44], r["failed"], r["applicable"],
                     ", ".join(r["ids"]) if len(r["ids"]) > 1 else c))
        print()

    missing = []
    if not os.path.exists(MARKS):
        missing.append("RATCHET-TXT.json (no marks - nothing to ratchet against)")
    if not os.path.exists(BASELINE):
        missing.append("RANKING-TXT-BASELINE.csv (no reference to compare with)")
    if missing:
        print("  BEFORE ANY FIX, restore the guards:")
        for m in missing:
            print("      MISSING %s" % m)
        print()

    print("  then:")
    print("      python3 tools/p2w-bench/txt_gate.py --snapshot      # before the change")
    print("      python3 tools/p2w-bench/txt_gate.py --score 60      # rescore, then ratchet")
    print("      python3 tools/p2w-bench/txt_gate.py --verify        # after: did the docx move?")
    print("      python3 tools/p2w-bench/classify_txt.py             # refresh the four records")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
