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


def combine(record, visual_json, only="", verified_json=""):
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

    # Where the verified findings are available, the decision is made on those. A raw
    # benchmark number and a raw eight-question verdict are claims; only the verified ones
    # have been checked against the PDF, and a comparison between two unchecked claims is
    # a comparison between two opinions.
    verified = {}
    if verified_json and os.path.isfile(verified_json):
        for f in json.load(open(verified_json, encoding="utf-8")):
            if f.get("verdict") != "VERIFIED":
                continue
            verified.setdefault(f.get("document"), []).append(f)

    numbers = {}
    if verified_json and os.path.isfile(verified_json):
        # only VERIFIED measure findings count against a document
        for doc, fs in verified.items():
            measure = [f for f in fs if f.get("kind") == "measure"]
            numbers[doc] = not measure
    elif visual_json and os.path.isfile(visual_json):
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
        if verified:
            # The eye's FAIL counts only when a claim on that page was verified. An eye
            # finding that the verifier refuted is not a defect, and counting it would
            # make the eye look more reliable than it is.
            vpages = {f.get("page") for f in verified.get(doc, [])
                      if f.get("kind") == "visual"}
            eye_fail = [p for p in eye_fail if p["page"] in vpages]
            if eye_fail:
                pending = []
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


def emit_findings(record, visual_json, out_path):
    """Build the findings file the verifier reads.

    This was the missing link in the pipeline. verify.py reads --findings and no tool
    wrote one, so step 10 had no input and the order had a hole in it. A human was
    expected to type the file by hand, which means in practice it would be skipped.

    Two sources, both already produced by earlier steps:

      LOOKED.tsv    the eye's verdict per page. A FAIL carries structured claims
                    separated by " | " - breaks:<text>, moved:<text>, count:<text>.
      visual.json   the eight computed questions. The ones that failed and have a claim
                    type become measure findings: order, pagecount, shapes.

    A claim the verifier does not understand is still emitted, so it comes back
    UNVERIFIABLE and is visible rather than silently dropped.
    """
    import json

    findings = []
    n = 0
    if os.path.isfile(record):
        for line in open(record, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            f = line.split("\t")
            if len(f) < 6 or f[4].strip().upper() != "FAIL":
                continue
            doc, page, note = f[0], f[1], f[5].strip()
            for part in note.split("|"):
                claim = part.strip()
                if not claim:
                    continue
                # "pagecount - this page should not exist" and friends: keep the token
                claim = claim.split(" - ")[0].strip()
                # pagecount is a MEASURE claim. Emitted as visual it cannot be checked at
                # all: the extra page does not exist in the PDF, so the verifier has no
                # page to compare it against and answers UNVERIFIABLE. The claim is about
                # the document, not about a page.
                kind = "measure" if claim.split(":")[0].strip() == "pagecount" else "visual"
                n += 1
                findings.append(("V%d" % n, doc, page, kind, claim))

    if visual_json and os.path.isfile(visual_json):
        # the computed questions that failed and can be expressed as a claim
        MEASURE = {"reading order": "order", "page count": "pagecount", "charts": "shapes"}
        for r in json.load(open(visual_json, encoding="utf-8")):
            doc = r.get("doc")
            if not doc:
                continue
            if not r.get("page_count_ok", True):
                n += 1
                findings.append(("M%d" % n, doc, 1, "measure", "pagecount"))
            for pg in r.get("answers", []):
                for qname, qa in (pg.get("answers") or {}).items():
                    if qa.get("verdict") != "no":
                        continue
                    claim = MEASURE.get(qname)
                    if not claim:
                        continue
                    n += 1
                    findings.append(("M%d" % n, doc, pg.get("page", 1), "measure", claim))

    # one row per distinct finding - the verifier dedupes too, but a file that already
    # says a thing once is easier to read than one that says it three times
    seen = set()
    rows = []
    for fid, doc, page, kind, claim in findings:
        key = (doc, page, kind, claim)
        if key in seen:
            continue
        seen.add(key)
        rows.append((fid, doc, page, kind, claim))

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("# id\tdocument\tpage\tkind\tclaim\n")
        for fid, doc, page, kind, claim in rows:
            fh.write("%s\t%s\t%s\t%s\t%s\n" % (fid, doc, page, kind, claim))

    print("%d findings written to %s" % (len(rows), out_path))
    for fid, doc, page, kind, claim in rows:
        print("   %-5s %-34s p%-2s %-7s %s" % (fid, doc[:34], page, kind, claim[:44]))
    return 0 if rows else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", required=True)
    ap.add_argument("--document", default="")
    ap.add_argument("--combine", action="store_true",
                    help="the document verdict, eye first, numbers as evidence")
    ap.add_argument("--visual-json", default="")
    ap.add_argument("--emit-findings", default="",
                    help="build the findings file verify.py reads, from this"
                         " record and the visual.py JSON")
    ap.add_argument("--verified", default="",
                    help="verify.py --json. When given, the decision is made on"
                         " findings that were CHECKED against the PDF, not on"
                         " the raw tool output")
    args = ap.parse_args()

    if args.emit_findings:
        return emit_findings(args.record, args.visual_json, args.emit_findings)
    if args.combine:
        return combine(args.record, args.visual_json, args.document, args.verified)
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
