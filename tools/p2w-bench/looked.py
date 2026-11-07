#!/usr/bin/env python3
"""Did anyone actually look at every page?

WHY
    "Look at every page" is an instruction, not a check. The eye is the only instrument
    for the defects no number measures - a line that wraps where the PDF kept one, a
    label sitting lower than the PDF drew it, a table squeezed into half its width. If
    nobody can prove the pages were opened, the strongest check in the pipeline is the
    one that quietly did not happen.

HOW IT IS PROVED
    sidebyside.py --record appends one row per page to a file: the document, the page,
    the share of pixels that differ, and the image path. The verdict starts as PENDING.
    You open the image, decide, and change PENDING to PASS or FAIL with what you saw.
    This script reads that file and lists every row still PENDING.

USAGE
    python3 tools/p2w-bench/looked.py --record tools/p2w-bench/LOOKED.tsv
    python3 tools/p2w-bench/looked.py --record FILE --document 303_discharge_summary

EXIT
    0  every recorded page has a verdict
    1  at least one page was never looked at
    2  the record file does not exist - nothing has been looked at
"""

import argparse
import os
import sys


def combine(record, visual_json, only=""):
    """The document verdict, with the eye first.

    The eye caught four problems out of four on 7 Nov. The computed questions caught
    three out of five and produced two false alarms. So the eye decides and the numbers
    are evidence - not the other way round.

    Where they disagree, the eye wins and the disagreement is named, because a
    disagreement is a bug in an instrument and the instrument gets repaired.
    """
    import json

    eye = {}
    for line in open(record, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) < 6:
            continue
        if only and f[0] != only:
            continue
        eye.setdefault(f[0], []).append({"page": int(f[1]), "verdict": f[4].strip().upper()})

    numbers = {}
    if visual_json and os.path.isfile(visual_json):
        for r in json.load(open(visual_json, encoding="utf-8")):
            numbers[r.get("doc")] = bool(r.get("ok"))

    docs = sorted(eye)
    if not docs:
        print("no verdicts recorded")
        return 2

    out = []
    for doc in docs:
        pages = eye[doc]
        pending = [p for p in pages if p["verdict"] == "PENDING"]
        eye_fail = [p for p in pages if p["verdict"] == "FAIL"]
        eye_pass = not pending and not eye_fail
        num_pass = numbers.get(doc)
        if num_pass is None:
            num_pass = True

        if pending:
            final, who = "UNLOOKED", "-"
        elif not eye_pass and not num_pass:
            final, who = "FAIL", "both"
        elif not eye_pass:
            final, who = "FAIL", "eye"
        elif not num_pass:
            final, who = "PASS", "eye (numbers wrong - repair the tool)"
        else:
            final, who = "PASS", "both"
        out.append((doc, final, who, len(pages), len(eye_fail)))

    print("%-38s %-9s %-40s %s" % ("document", "verdict", "decided by", "pages"))
    for doc, final, who, n, nf in out:
        print("%-38s %-9s %-40s %d (%d failed)" % (doc[:38], final, who[:40], n, nf))

    bad = [o for o in out if o[1] in ("FAIL", "UNLOOKED")]
    dis = [o for o in out if o[2].startswith("eye (")]
    print("")
    print("%d documents: %d pass, %d fail, %d unlooked"
          % (len(out), len(out) - len(bad),
             len([o for o in out if o[1] == "FAIL"]),
             len([o for o in out if o[1] == "UNLOOKED"])))
    if dis:
        print("")
        print("%d disagreement(s): the eye passed, the numbers failed. Those are measurement" % len(dis))
        print("bugs, not document defects - repair the tool, not the document:")
        for doc in dis:
            print("   " + doc[0])
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", required=True)
    ap.add_argument("--document", default="")
    ap.add_argument("--combine", action="store_true",
                    help="the document verdict, eye first, numbers as evidence")
    ap.add_argument("--visual-json", default="")
    args = ap.parse_args()

    if args.combine:
        return combine(args.record, args.visual_json, args.document)
    if not os.path.isfile(args.record):
        print("no record at %s - no page has been looked at yet" % args.record)
        return 2

    rows = []
    with open(args.record, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 6:
                continue
            rows.append(parts)

    if args.document:
        rows = [r for r in rows if r[0] == args.document]

    if not rows:
        print("no pages recorded%s" % (" for " + args.document if args.document else ""))
        return 2

    pending = [r for r in rows if r[4].strip().upper() == "PENDING"]
    passed = [r for r in rows if r[4].strip().upper() == "PASS"]
    failed = [r for r in rows if r[4].strip().upper() == "FAIL"]

    print("pages recorded: %d   passed: %d   failed: %d   never looked at: %d"
          % (len(rows), len(passed), len(failed), len(pending)))

    for r in pending[:40]:
        print("   NOT LOOKED AT  %-38s page %-3s  %.1f%% differs"
              % (r[0][:38], r[1], float(r[2]) if r[2] else 0.0))
    if len(pending) > 40:
        print("   ... and %d more" % (len(pending) - 40))

    if pending:
        print("")
        print("Open each image, decide, and replace PENDING with PASS or FAIL plus what")
        print("you saw. A page nobody opened cannot be reported as passing.")
        return 1

    print("every recorded page has a verdict")
    return 0


if __name__ == "__main__":
    sys.exit(main())
