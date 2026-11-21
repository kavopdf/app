#!/usr/bin/env python3
"""Which constructs in an emitted .docx does Google Docs ignore?

    python3 tools/p2w-bench/google_safe.py <file.docx>          # what is in this one
    python3 tools/p2w-bench/google_safe.py --corpus             # every .docx in the output dir
    python3 tools/p2w-bench/google_safe.py --corpus --check     # exit 1 if anything is over its mark
    python3 tools/p2w-bench/google_safe.py --corpus --mark      # record today's counts as the mark

WHY THIS IS A TOOL AND NOT A PARAGRAPH IN THE BRIEF.

The project has already lost once to a construct LibreOffice honours and Google does not: `w:framePr`
shipped as 3.53.5 and broke every stamp on the phone, with every CI count identical, because CI measured
LibreOffice. LESSONS.md has carried that lesson ever since and it has been re-learned five more times:

    w:w and w:spacing (character width)   Google ignores all of it      132 documents
    embedded .odttf faces                 Google ignores them
    floating <w:drawing> rules            Google drops the shape       143 documents
    w:before at the top of a page         Google renders 0.33 of 55 pt 104 documents

A rule a run has to remember is a rule a run skips. This is a check it cannot skip: it reads the bytes
that actually go into the .docx, so a construct is caught whether or not anyone remembered the lesson.

THE MARK IS A RATCHET, NOT A BAN. Every document already carries floating drawings, so a hard ban would
refuse the whole corpus on day one and change nothing. What is refused is a document that GAINS a
construct it did not have, or a corpus whose total goes up. That stops the next 3.53.5 while letting the
existing damage be worked down.
"""
import json, os, re, sys, zipfile, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MARK = os.path.join(HERE, "GOOGLE-SAFE-MARK.json")

# Every entry is a construct Google Docs does not honour, measured, with the finding that proves it.
IGNORED = [
    ("w:framePr", "framePr",
     re.compile(r"<w:framePr\b"),
     "PLAN-DECISIONS F2 / LESSONS.md: Google renders the paragraph as body text at the left margin. "
     "Shipped as 3.53.5 and broke every stamp."),
    ("w:drawing", "floating-drawing",
     re.compile(r"<w:drawing>"),
     "FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md: Google does not lay out floating drawings from "
     "an imported .docx. It drops the shape and leaves the anchor."),
    ("wp:anchor", "anchored-object",
     re.compile(r"<wp:anchor\b"),
     "Same as above: an anchored object is the wrapper a floating drawing arrives in."),
    ("w:w", "char-width",
     re.compile(r"<w:w\s+w:val="),
     "FINDINGS/GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md: measured four ways, Google honours no "
     "character-width control at all."),
    ("w:spacing-letter", "letter-spacing",
     re.compile(r"<w:spacing\b[^>]*w:val=\"-?\d+\""),
     "Same finding: w:spacing is ignored along with w:w."),
    ("w:position", "vertical-raise",
     re.compile(r"<w:position\b"),
     "Google ignores w:position; a raised or lowered run renders on the baseline."),
    ("w:before-page-top", "page-top-gap",
     re.compile(r"<w:spacing\b[^>]*w:before=\""),
     "FINDINGS/18_displacement-page-top-before-DROPPED: Google drops w:before at the top of a page - "
     "55.15 pt asked, 0.33 pt rendered."),
]

EMBEDDED_FONT = ("embedded-font", "FINDINGS/GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md: an embedded face is "
                                   "ignored, so the width it was chosen for is not the width Google uses.")


def scan(path):
    """{construct: count} for one .docx. Counts, not booleans - a ratchet needs a number."""
    out = {}
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            x = z.read("word/document.xml").decode("utf-8", "ignore")
    except Exception as e:
        return {"error": str(e)}
    for label, _short, pat, _why in IGNORED:
        n = len(pat.findall(x))
        if n:
            out[label] = n
    if any(n.startswith("word/fonts/") for n in names):
        out["embedded-font"] = 1
    return out


def corpus_dir():
    for d in ("/scratch/work/p2w/out", os.path.join(ROOT, "benchmarks", "out")):
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*.docx")):
            return d
    return None


def main(argv):
    if not argv:
        print(__doc__.strip().split("\n\n")[0])
        return 2

    if argv[0] not in ("--corpus",):
        path = argv[0]
        if not os.path.exists(path):
            print("refused: no such file: %s" % path, file=sys.stderr)
            return 3
        found = scan(path)
        if not found:
            print("  clean - carries no construct Google ignores")
            return 0
        print("  %s" % os.path.basename(path))
        for k, v in sorted(found.items()):
            why = next((w for lab, _s, _p, w in IGNORED if lab == k), EMBEDDED_FONT[1])
            print("    %-20s x%-4d  %s" % (k, v, why[:88]))
        return 0

    d = corpus_dir()
    if not d:
        print("refused: no .docx output directory - run p2w.py first", file=sys.stderr)
        return 3
    files = sorted(glob.glob(os.path.join(d, "*.docx")))
    per, totals, carriers = {}, {}, {}
    for f in files:
        r = scan(f)
        name = os.path.basename(f)[:-5]
        per[name] = r
        for k, v in r.items():
            totals[k] = totals.get(k, 0) + v
            carriers[k] = carriers.get(k, 0) + 1

    print("  scanned %d documents in %s" % (len(files), d))
    print()
    print("  %-20s %8s %8s" % ("construct", "docs", "instances"))
    print("  " + "-"*40)
    for k in sorted(totals, key=lambda x: -carriers.get(x, 0)):
        print("  %-20s %8d %8d" % (k, carriers.get(k, 0), totals[k]))

    if "--mark" in argv:
        json.dump({"at": "recorded by google_safe.py --mark", "carriers": carriers, "totals": totals},
                  open(MARK, "w"), indent=1)
        print()
        print("  mark written: %s" % os.path.relpath(MARK, ROOT))
        return 0

    if "--check" in argv:
        try:
            was = json.load(open(MARK))
        except Exception:
            print()
            print("  no mark - run --mark once to record today's counts")
            return 0
        bad = []
        for k, v in carriers.items():
            if v > was.get("carriers", {}).get(k, 0):
                bad.append("%s: %d documents carry it, the mark is %d"
                           % (k, v, was.get("carriers", {}).get(k, 0)))
        if bad:
            print()
            print("  REFUSED - a construct Google ignores has spread:")
            for b in bad:
                print("    %s" % b)
            return 1
        print()
        print("  no construct spread beyond the mark")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
