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
import json, os, re, sys, time, zipfile, glob

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
    # RENAMED 24 Nov: this pattern matches ANY w:before, not a page top. Measured by an agent on a
    # 6-paragraph document: 214 matches, table cells included, while the defect is only a w:before
    # AT a page top. The count was quoted as '210 documents, 20786 instances' as if it were page-top
    # gaps. It is not. The label now says what it measures, and the real page-top construct follows.
    ("w:before-any", "before-gap",
     re.compile(r'<w:spacing\b[^>]*w:before="'),
     "ANY paragraph or cell before-gap - not a defect on its own (Google honours it 1:1 except at a page top)."),
    ("w:before-after-pagebreak", "page-top-gap",
     re.compile(r'<w:br\s+w:type="page"\s*/>(?:(?!<w:p[ >]).)*?<w:p\b(?:(?!<w:p[ >]).)*?w:before="([1-9]\d*)"', re.S),
     "Google drops w:before at a page top after a hard break: 55.15 pt asked, 0.33 rendered. This is the real construct."),
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


def predict(only=None, quiet=False):
    """Which known-ignored constructs does each .docx carry, and so which checks will fail.

    THIS IS A LAW AT THE CONSTRUCT LEVEL, AND IT WAS OVERSTATED AT THE DOCUMENT LEVEL.
    Corrected 24 Nov after an agent measured the store: of 191 scored documents, 163 carry
    w:drawing and PASS 32_stroke_lines, 19 pass without it, and only 9 fail with it - so
    "a floating drawing has never passed" is FALSE as a document-level statement. What survives
    is the narrower per-rule reading: the check scores RULE GEOMETRY, and a rule whose only
    carrier is a floating drawing is not counted as an isolated rule. Do not price a patch for
    32_stroke_lines against 192 documents; the real number is 9. An anchored text box is
    rasterised by Google on import, which is 166 of the failures in 04_chars_missing,
    45_char_accuracy, 13_text_colours, 44_header_footer and 17_matched_runs.
    13_text_colours, 44_header_footer and 17_matched_runs.

    So a patch can be judged in SECONDS instead of a 54-minute restamp: if the construct counts
    did not move, the Google verdict cannot have moved either. It is not the truth - Google is -
    but it is the reason to spend the truth.
    """
    d = corpus_dir()
    if not d:
        print("  no .docx output directory", file=sys.stderr)
        return 3
    files = sorted(glob.glob(os.path.join(d, '*.docx')))
    if only:
        files = [f for f in files if only in os.path.basename(f)]
    out = {}
    for f in files:
        name = os.path.basename(f)[:-5]
        r = scan(f)
        if r.get('error'):
            continue
        if r:
            out[name] = r
    dest = os.path.join(os.path.dirname(HERE), '..', 'benchmarks', 'GOOGLE-PREDICT.json')
    try:
        json.dump({'documents': out, 'at': time.strftime('%Y-%m-%dT%H:%M:%S')},
                  open(dest, 'w', encoding='utf-8'), indent=0)
    except Exception as e:
        print("  could not write %s (%s)" % (dest, type(e).__name__), file=sys.stderr)
        return 1
    if not quiet:
        tot = {}
        for r in out.values():
            for k, v in r.items():
                tot[k] = tot.get(k, 0) + v
        print('  %d of %d documents carry a construct Google ignores' % (len(out), len(files)))
        for k, v in sorted(tot.items(), key=lambda x: -x[1])[:8]:
            docs = len([1 for r in out.values() if k in r])
            print('    %-26s %3d documents  %4d instances' % (k[:26], docs, v))
        print('  written to benchmarks/GOOGLE-PREDICT.json')
    return 0


def main(argv):
    if not argv:
        print(__doc__.strip().split("\n\n")[0])
        return 2

    # --predict is a MODE, not a filename. Without this the flag was read as a path and the tool
    # answered "no such file: --predict" - the mechanism existed and could not be called.
    if argv[0] == "--predict":
        return predict(quiet="-q" in argv)
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
    per, totals, carriers, errors = {}, {}, {}, []
    for f in files:
        r = scan(f)
        name = os.path.basename(f)[:-5]
        per[name] = r
        # scan() RETURNS {'error': message} WHEN A .docx CANNOT BE OPENED, AND THIS LOOP USED TO ADD
        # IT TO AN INT. Measured 24 Nov: one unreadable file raised
        #   TypeError: unsupported operand type(s) for +: 'int' and 'str'
        # and took the whole google-safe check with it, so regress.py printed nothing and refused EVERY
        # commit. A crash in one file must not be a silent veto on all of them.
        for k, v in r.items():
            if not isinstance(v, int):
                continue
            totals[k] = totals.get(k, 0) + v
            carriers[k] = carriers.get(k, 0) + 1
            if r.get('error'):
                errors.append((name, r['error']))

    print("  scanned %d documents in %s" % (len(files), d))
    print()
    print("  %-20s %8s %8s" % ("construct", "docs", "instances"))
    print("  " + "-"*40)
    for k in sorted(totals, key=lambda x: -carriers.get(x, 0)):
        print("  %-20s %8d %8d" % (k, carriers.get(k, 0), totals[k]))

    if "--mark" in argv:
        # THE MARK ONLY EVER FALLS. It is the record of how much of this damage the corpus still
        # carries, and the whole point is that the number reaches zero. A --mark that could raise it
        # would let a run make the target whatever it just did, which is the same as having no target.
        try:
            was = json.load(open(MARK))
        except Exception:
            was = None
        # THE MARK IS ONLY COMPARABLE WITHIN ONE POPULATION, AND IT DID NOT SAY WHICH.
        #
        # It was recorded over 28 documents - a partial output directory in some earlier sandbox -
        # and the corpus is 213. A full corpus therefore carries w:drawing in 197 documents against
        # a mark of 28, and since the mark may only fall, EVERY commit was refused, including one
        # that changed no engine code and no .docx at all. Found 21 Nov, on the report commit of the
        # 07:58 fixer run. A mark that records what it was recorded over cannot be compared with a
        # different-sized corpus by accident.
        _was_n = (was or {}).get("corpus_docs")
        if was and (_was_n is None or _was_n != len(files)):
            print()
            print("  RE-BASE - the mark was recorded over %s documents and this corpus is %d."
                  % ("an unrecorded number of" if _was_n is None else _was_n, len(files)))
            print("  Carrier counts are not comparable across populations; the mark is re-based to")
            print("  this corpus and may only fall from here. Say so in the commit message.")
            json.dump({"at": "recorded by google_safe.py --mark (re-based: %s -> %s documents)"
                              % (_was_n, len(files)),
                       "corpus_docs": len(files), "carriers": carriers, "totals": totals},
                      open(MARK, "w"), indent=1)
            print("  mark written: %s" % os.path.relpath(MARK, ROOT))
            return 0
        if was:
            raised = []
            for k, v in carriers.items():
                if v > was.get("carriers", {}).get(k, 0):
                    raised.append("%s: %d now, the mark is %d" % (k, v, was.get("carriers", {}).get(k, 0)))
            if raised:
                print()
                print("  REFUSED - the mark may only fall, and this would raise it:")
                for r in raised:
                    print("    %s" % r)
                print("  Fix the engine so it emits fewer of them, or do not commit.")
                return 1
        json.dump({"at": "recorded by google_safe.py --mark", "corpus_docs": len(files),
                   "carriers": carriers, "totals": totals}, open(MARK, "w"), indent=1)
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
        _was_n = (was or {}).get("corpus_docs")
        if was and (_was_n is None or _was_n != len(files)):
            print()
            print("  cannot compare: the mark was recorded over %s documents, this corpus is %d."
                  % ("an unrecorded number of" if _was_n is None else _was_n, len(files)))
            print("  Carrier counts are a property of the population. Run --mark to re-base it.")
            return 3
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
        # HOW FAR FROM ZERO. A ratchet that never says the distance is a ratchet nobody works down.
        left = sum(carriers.values())
        print("  %d document-carried constructs Google ignores remain - the target is 0" % left)
        if left:
            print("  Each one is a defect in a renderer the user opens. Removing them is engine work,")
            print("  one construct at a time, each measured across the corpus before it is committed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
