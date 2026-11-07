# The pipeline, in the order it runs

One document at a time. Every step is a gate, and a document is not fixed until it has
been through all of them and its findings have been verified.

    0. TOOLCHAIN       JDK, libraries, the engine compiles, the corpus is the right size
    1. CONVERT         PDF -> Result -> .docx and .txt
    2. G1 BUILD        javac + TestPdfToWord + TestRealDocs
    3. G2 REGRESSION   208 documents against base208.json - did anything get worse
    4. G3 STRUCTURE    reflow: body text in text boxes, layout at two widths
    5. G4 TXT          entry hashes inside the .docx - only when the txt changed
    6. G5 POSITION     render vs PDF, matched by text: x, y, size, name, colour
                       also writes the rendered/ PDFs that steps 10 and 14 read
    7. G6a THE EYE     sidebyside.py --record, then OPEN EVERY IMAGE and fill the verdict
    8. G6b NUMBERS     visual.py --json --verify - the eight questions, with evidence
    9. RECORD          looked.py - exit 0 only when every page has a verdict
   10. EMIT FINDINGS   looked.py --emit-findings - build the file step 11 reads
   11. VERIFY          verify.py --json - every finding, once, against the PDF
   12. DECIDE          looked.py --combine --verified - on VERIFIED findings only
   13. FIX             only findings that came back VERIFIED. Three tries, one for a stamp
   14. RE-CHECK        after a fix: convert, render, LOOK, re-measure, G2 again
   15. COMMIT          precommit.sh, then commit, then confirm the file landed
   16. LOGS            defects, scores, baselines, the batch log

## The commands, in order

    python3 tools/p2w-bench/gate.py --corpus DIR --out OUT \
            --baseline tools/p2w-bench/base208.json --check
    python3 tools/p2w-bench/reflow.py --dir OUT
    python3 tools/p2w-bench/txt-guard.py snapshot --dir OUT --save S.json
    soffice --headless --convert-to pdf --outdir REND OUT/*.docx
    python3 tools/p2w-bench/position.py --corpus DIR --out OUT --rendered REND \
            --baseline tools/p2w-bench/base208-position.json

    python3 tools/p2w-bench/sidebyside.py --corpus DIR --out OUT --doc NAME \
            --record LOOKED.tsv
        # then view _images/NAME/page-*.png and set PASS or FAIL with structured claims

    python3 tools/p2w-bench/visual.py --corpus DIR --out OUT --json VIS.json --verify
    python3 tools/p2w-bench/looked.py --record LOOKED.tsv
    python3 tools/p2w-bench/looked.py --record LOOKED.tsv --visual-json VIS.json \
            --emit-findings F.tsv
    python3 tools/p2w-bench/verify.py --findings F.tsv --corpus DIR --out OUT \
            --rendered REND --json VERIFIED.json
    python3 tools/p2w-bench/looked.py --record LOOKED.tsv --combine \
            --verified VERIFIED.json

## Why this order

LOOK BEFORE YOU MEASURE. Step 7 comes before step 8 so the eye forms its own opinion
before it is told what to think. An eye that has already been told "reading order 88.5 %"
is looking for a reason to agree.

VERIFY BEFORE YOU FIX. Steps 10 to 12 exist because on 7 Nov two of nine findings were
false alarms. A fix applied to a false alarm makes the document worse and hides the bug in
the tool.

THE EYE DECIDES. Step 12 makes the eye's verdict the document verdict. Measured on 7 Nov:
the eye was right 4 out of 4, the computed questions 3 out of 5 with 2 false alarms.

DECIDE ON VERIFIED DATA. Step 12 reads VERIFIED.json, not the raw tool output. A measure
finding counts against a document only when it was checked against the PDF and held; an
eye finding counts only when a visual claim on that page verified. Comparing two unchecked
claims is comparing two opinions.

ONE VERIFICATION PER FINDING. verify.py deduplicates on document, page, kind and claim, so
the same problem is checked once however many times it is listed.

## What must not be reordered

- G1 before G2. A build that does not compile makes G2 meaningless.
- G2 before recording a baseline. A baseline recorded on a run where a document got worse
  makes the regression permanent and invisible.
- The eye (7) before the numbers (8).
- EMIT (10) before VERIFY (11). verify.py reads a findings file and nothing else writes
  one; before step 10 existed the order had a hole in it.
- VERIFY (11) before DECIDE (12) and before FIX (13). Always.
- precommit (15) before commit, and the commit confirmed after.

## What can run less often

- G5 at the end of a batch, not after every fix - it needs a render of every document.
- G4 only when the .txt changed. G3 only when the .docx changed.
- G2 only when the engine changed, or at the end of a document.

## The claim types the eye may record

    wraps:<text>     the PDF has <text> on one line, the render puts it on more
    breaks:<text>    the same number of lines, broken at a different word
    moved:<text>     the render puts <text> further than the tolerance from the PDF
    count:<text>     how many times the PDF holds <text>, against the render
    missing:<text>   the PDF has <text> and the render does not
    extra:<text>     the render has <text> the PDF does not
    pagecount        the render has more or fewer pages than the PDF
    overlap          the render overlaps lines the PDF keeps apart
    shapes           the render has fewer shapes than the PDF

A claim the verifier does not understand comes back UNVERIFIABLE and is not fixed.
