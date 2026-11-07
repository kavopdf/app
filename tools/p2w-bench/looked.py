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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", required=True)
    ap.add_argument("--document", default="")
    args = ap.parse_args()

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
