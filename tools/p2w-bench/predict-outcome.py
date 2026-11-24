#!/usr/bin/env python3
"""If a construct were fixed, how many documents would go CLEAN - before anything is built.

WHY THIS AND NOT "documents affected". Ranking by documents affected says 18_displacement is worth 103
documents. It is not: those documents each fail several checks, and losing one failure does not make a
document clean. The only number that matters is how many documents reach zero failures.

    predict-outcome.py

    construct                     docs carrying   would go CLEAN
    w:before-page-top                    210                 12
    wp:anchor                            194                  3
    ...

A document counts only when EVERY check it fails is one this construct is measured to cause. That is
deliberately strict: a document that also fails something else does not become clean, and counting it
would repeat the "documents affected" mistake in a new place.

The cause map is the same evidence diagnose.py uses - measured pairs with document counts, not
intuition. A construct with no mapped cause contributes nothing, and is listed with 0 rather than
guessed at.

Nothing is written. This is arithmetic over the committed store and the construct census.
"""
import json
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GV = os.path.join(ROOT, "benchmarks", "gverify")
PREDICT = os.path.join(ROOT, "benchmarks", "GOOGLE-PREDICT.json")

CAUSE = {
    "wp:anchor": {"04_chars_missing", "45_char_accuracy", "13_text_colours",
                  "44_header_footer", "17_matched_runs"},
    "w:drawing": {"04_chars_missing", "45_char_accuracy", "13_text_colours",
                  "44_header_footer", "17_matched_runs"},
    "w:before-page-top": {"18_displacement"},
    "w:spacing-letter": {"17_matched_runs"},
    "embedded-font": {"45_char_accuracy", "13_text_colours"},
}


def store():
    out = {}
    for f in glob.glob(os.path.join(GV, "*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if d.get("status") == "page_count_refused":
            continue
        out[os.path.basename(f)[:-5]] = set(d.get("failed") or [])
    return out


def main(argv):
    st = store()
    try:
        cons = json.load(open(PREDICT, encoding="utf-8")).get("documents") or {}
    except Exception:
        print("  no construct census - run google_safe.py --predict first", file=sys.stderr)
        return 3
    if not st:
        print("  no Google verdicts", file=sys.stderr)
        return 3
    rows = []
    for c in set(CAUSE) | {k for v in cons.values() for k in v}:
        carried = [n for n, v in cons.items() if c in v]
        if not carried:
            continue
        causes = CAUSE.get(c) or set()
        clean = [n for n in carried if n in st and st[n] and st[n] <= causes]
        rows.append((c, len(carried), len(clean)))
    rows.sort(key=lambda r: -r[2])
    print("  %-26s %13s %15s" % ("construct", "docs carrying", "would go CLEAN"))
    for c, n, k in rows:
        mark = "" if CAUSE.get(c) else "   (no measured cause)"
        print("  %-26s %13d %15d%s" % (c[:26], n, k, mark))
    total = len(st)
    clean_now = len([n for n in st if not st[n]])
    print("")
    print("  clean now: %d of %d" % (clean_now, total))
    print("  these are NOT additive: one document can carry several constructs, and a document that")
    print("  becomes clean from one is already counted for another. The single-construct column is the")
    print("  honest one; a combined figure would need the patches built together.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
