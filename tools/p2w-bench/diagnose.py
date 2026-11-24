#!/usr/bin/env python3
"""For one document: which constructs it carries, which checks it fails, and which cause which.

THE JOIN THAT WAS MISSING. The store knows a class fails 65 documents. The construct census knows a
document carries 12 anchored boxes. Nothing joined them, so a patch had to be written from prose.

    diagnose.py 72_bank_statement_no_rules_right_amounts

prints the document's failed checks, the constructs it carries, and - for each construct - the checks
that construct is KNOWN to break, taken from the measured laws in FINDINGS/ and the capability matrix.
Where a construct explains a failure, the two are shown together; where nothing explains it, that is
said plainly rather than guessed.

WHY THE MAPPING IS EVIDENCE AND NOT A GUESS. Each pair below is a measurement with a document count,
not an intuition:
  wp:anchor / w:drawing  -> Google rasterises every anchored box on import. 166 failures across
                            04_chars_missing, 45_char_accuracy, 13_text_colours, 44_header_footer,
                            17_matched_runs.
  w:before-page-top      -> Google drops w:before at a page top after a hard break; 55.15 pt asked,
                            0.33 rendered. 18_displacement, 103 documents.
    a rule as a floating <w:drawing> -> CORRECTED 24 Nov: 163 of 191 scored documents carry
                              w:drawing and PASS 32_stroke_lines; only 9 fail. The old
                              "never passed" claim was false at the document level.
  embedded-font          -> Google ignores character width from an embedded face.
  w:spacing-letter       -> letter spacing is not honoured.

A construct with no known mapping is listed and left unexplained. Silence is not a verdict.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GV = os.path.join(ROOT, "benchmarks", "gverify")
PREDICT = os.path.join(ROOT, "benchmarks", "GOOGLE-PREDICT.json")

# construct -> checks it is MEASURED to break. Evidence in the docstring above.
CAUSE = {
    "wp:anchor": ["04_chars_missing", "45_char_accuracy", "13_text_colours",
                  "44_header_footer", "17_matched_runs"],
    "w:drawing": ["04_chars_missing", "45_char_accuracy", "13_text_colours",
                  "44_header_footer", "17_matched_runs"],
    "w:before-after-pagebreak": ["18_displacement"],
    "w:spacing-letter": ["17_matched_runs"],
    "embedded-font": ["45_char_accuracy", "13_text_colours"],
}


def _load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return {}


def one(name):
    g = _load(os.path.join(GV, name + ".json"))
    if not g:
        print("  no Google verdict for %s" % name, file=sys.stderr)
        return 3
    if g.get("status") == "page_count_refused":
        print("  %s was refused on page count - not scored, nothing to diagnose" % name)
        return 0
    failed = list(g.get("failed") or [])
    cons = (_load(PREDICT).get("documents") or {}).get(name) or {}
    print("  %s" % name)
    print("  %d of %s checks fail: %s" % (len(failed), g.get("total") or "?",
                                          ", ".join(failed) if failed else "none - CLEAN"))
    if not cons:
        print("  no construct census for this document - run google_safe.py --predict")
        return 0
    print("")
    print("  carries:")
    for k, v in sorted(cons.items(), key=lambda x: -x[1]):
        print("    %-24s %4d" % (k, v))
    explained, unexplained = {}, []
    for k in cons:
        for chk in CAUSE.get(k, []):
            if chk in failed:
                explained.setdefault(chk, []).append(k)
    for chk in failed:
        if chk in explained:
            print("")
            print("  %s" % chk)
            print("    caused by: %s" % ", ".join(sorted(set(explained[chk]))))
        else:
            unexplained.append(chk)
    if unexplained:
        print("")
        print("  NO MEASURED CAUSE for: %s" % ", ".join(unexplained))
        print("    A construct with no mapping is not a construct with no cause - it means nobody has")
        print("    measured this pair yet. Do not infer one.")
    return 0


def main(argv):
    if not argv:
        print(__doc__.strip().split("\n\n")[0])
        return 2
    if argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    return one(argv[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
