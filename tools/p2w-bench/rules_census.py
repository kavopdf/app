#!/usr/bin/env python3
"""rules_census.py - how many rules each corpus document draws, and on how many pages.

WHY THIS EXISTS
    The floating-table carrier places ONE table per page, and a second one stacks under the first
    (measured, 21 Nov, 73_marksheet_subject_marks_grade). So the question that decides whether a
    carrier is worth building, and which carrier, is: how many rules does each page of each document
    actually draw? Nothing in the repo answered it, and two runs built the single-rule carrier and
    measured it on one-rule documents.

WHAT IT COUNTS
    The instrument's own definition, imported rather than re-implemented: verify_google._rules(page)
    - thin face <= RULE_THIN 4.0 pt, long face >= RULE_LONG 10 pt, isolated (not touching another
    segment within RULE_GAP 3 pt). A number from a second implementation would be a second opinion,
    not the instrument's answer.

    It reads the SOURCE PDF, so it says what the page draws, not what the engine emits. A rule the
    engine drops before it reaches the shape writer is still counted here.

USAGE
    python3 tools/p2w-bench/rules_census.py                        # /scratch/work/p2w/corpus
    python3 tools/p2w-bench/rules_census.py --corpus DIR --json OUT.json

EXIT 0 always - a census that cannot read one PDF records the error against that document.
"""
import argparse, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="/scratch/work/p2w/corpus")
    ap.add_argument("--json", default="/scratch/work/rules_census.json")
    a = ap.parse_args()

    import verify_google as vg
    import pymupdf
    pymupdf.TOOLS.mupdf_display_errors(False)

    out = {}
    for p in sorted(glob.glob(os.path.join(a.corpus, "*.pdf"))):
        stem = os.path.basename(p)[:-4]
        try:
            d = pymupdf.open(p)
        except Exception as e:
            out[stem] = {"err": str(e)}
            continue
        per = []
        for i in range(len(d)):
            try:
                per.append(len(vg._rules(d.load_page(i))))
            except Exception:
                per.append(0)
        d.close()
        out[stem] = {"pages": len(per), "rules": sum(per), "per_page": per,
                     "max_page": max(per) if per else 0}

    json.dump(out, open(a.json, "w"), indent=0)

    zero = [k for k, v in out.items() if v.get("rules", 0) == 0]
    one = [k for k, v in out.items() if v.get("max_page", 0) == 1]
    multi = [k for k, v in out.items() if v.get("max_page", 0) >= 2]
    print("documents                 %d" % len(out))
    print("no rule on any page       %d" % len(zero))
    print("has rules                 %d" % (len(out) - len(zero)))
    print("  busiest page has 1 rule %d" % len(one))
    print("  busiest page has >=2    %d" % len(multi))
    print("rules counted             %d" % sum(v.get("rules", 0) for v in out.values()))
    print("wrote %s" % a.json)


if __name__ == "__main__":
    main()
