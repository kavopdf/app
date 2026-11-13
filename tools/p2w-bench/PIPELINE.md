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
   12. LEDGER          add this run's verify.py counts to CLAIM-LEDGER.md
   13. DECIDE          looked.py --combine --verified - on VERIFIED findings only
   14. FIX             only findings that came back VERIFIED. Three tries, one for a stamp
   15. RE-CHECK        after a fix: convert, render, LOOK, re-measure, G2 again
   16. COMMIT          precommit.sh, then commit, then confirm the file landed
   17. LOGS            defects, scores, baselines, the batch log

## The commands, in order

    python3 tools/p2w-bench/gate.py --corpus DIR --out OUT \
            --baseline tools/p2w-bench/base208.json --check
    python3 tools/p2w-bench/reflow.py --dir OUT
    python3 tools/p2w-bench/txt-guard.py snapshot --dir OUT --save S.json
    soffice --headless --convert-to pdf --outdir REND OUT/*.docx
    # THE RENDERER IS A MEASUREMENT CHOICE, NOT A DETAIL (13 Nov). Everything this pipeline scores
    # is LibreOffice's output. Every number stored before 13 Nov came from a Google Docs export.
    # They are NOT comparable: one 211-document round split the same total into engine +230,
    # instrument -1833 and renderer +1634. Google's export cannot be produced from this sandbox
    # (the Drive upload path rejects a local file), so the renderer question is OPEN and any score
    # must name the renderer that produced it.
    # TRACE.md is written by build-engine.sh on every run. Do not commit it.
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
    # step 12: add VERIFIED.json's counts to tools/p2w-bench/CLAIM-LEDGER.md
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

## The claim ledger — why a refuted finding is still worth keeping

A finding that comes back REFUTED is not a document defect. The pipeline correctly does not
fix it. But it is not nothing either: a claim type that is refuted again and again is
telling you about the TOOL.

    the eye misreads the image        -> the eye's instruction is wrong
    the verifier's check is wrong     -> the tool has a bug
    the claim is too loosely worded   -> the claim vocabulary is missing something

All three are fixable, and all three are invisible if the refuted finding is dropped.
CLAIM-LEDGER.md is one table - claim type, verified, refuted, unverifiable - and step 12
adds the run's counts to it.

THE RULE: a document is never left FAIL on a claim type the verifier itself refutes. If it
is, the problem is the claim or the check, not the page. Stop fixing documents on that
claim type, work out which of the three causes it is, fix that, and say so in the run.

A claim type with UNVERIFIABLE counts is not checkable at all: either the claim is worded
too loosely - "looks wrong" instead of "moved:Resident Medical Officer" - or the verifier
has no check for it. Both are fixable.

## The Run column — three numbers the report could not give before

Every row in VISUAL-SCORE.md carries the start time of the run that produced it, HH:MM, in
the Run column. That is the whole reason the column exists:

    documents per run     group the rows by Run and count them
    minutes per document  the run's duration divided by its rows
    minutes per problem   the run's duration divided by the findings that run verified

Write it as the run's start time, not the time you finished the document - one value per run
is what makes the grouping work.

Do not estimate it. If you do not know the start time, leave the column as `-` rather than
inventing one; a wrong number here is worse than an empty one, because the report presents
it as measured.

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
    rotated:<text>   the PDF draws <text> on a slanted baseline and the render level
                     (added 9 Nov; 1 degree, full turn - 180 is not 0)

A claim the verifier does not understand comes back UNVERIFIABLE and is not fixed.

## A stamp is rasterised, not rebuilt as text

A rotated stamp is not written as text. `PdfToWord.stampPictures` finds the rotated paragraphs
on a page, takes the union of their boxes plus three points of padding, renders that area of the
PDF page at 300 dpi, crops it, and puts it in the page's blocks as an anchored picture in place
of the text.

Why, in one line each, because five attempts were measured before this was accepted:

- written upright, the text lands where the page did not put it;
- `<a:xfrm rot>` is written and ignored - LibreOffice drops rotation on a text box, and its
  documented limit is that bitmaps rotate only in 90-degree steps;
- the outline and the text were two objects with two position calculations, and they drifted.

A picture has none of those failure modes: outline, text, angle, size and position are the
page's own by construction.

**Two things follow for anyone reading a converted file.**

1. The stamp's words are no longer in the text layer. They are written as the picture's alt text
   (`descr` on `wp:docPr`), so a screen reader reads them and a search finds them.
2. `gate.py` folds that alt text into the document's word list before comparing, so a rasterised
   stamp is neither missing nor extra. If you add a comparison that reads the document as text,
   fold the alt text in the same way or every stamp document will look like it lost words.


## What changed on 8 Nov, for anyone running this pipeline

Read this before touching a measurement or a threshold. Every item below cost a wrong guess.

**1. `gate.py`'s `nobg` no longer means what its name says.** It used to check for
`<w:background w:color="FFFFFF"/>`. That background was added so a dark reader would not show
black text on a black page, and it caused a worse problem: Google Docs dark mode paints the
white back over the inverted page, so every table came out under white patches. The colour now
lives on the text as a document default, so `nobg` checks for `<w:color w:val="000000"/>` in
`docDefaults`. A run that reports `nobg` rising is reporting a missing default colour, not a
missing background.

**2. `gate.py` folds picture alt text into its word comparison.** A rasterised stamp keeps its
words as `descr` on `wp:docPr`, and `_alt_text` reads them. Any new comparison that reads the
document as text must fold that in the same way, or every stamp document will look like it lost
words.

**3. Do not try to rotate a stamp's text box.** Five attempts were measured and all five failed:
written upright the text lands in the wrong place; `<a:xfrm rot>` is written and LibreOffice
ignores it on a text box; angle 0 on a rotated line (the 180-degree case) is written and still
ignored; binding the outline to the box fixes the drift and not the rotation; `behindDoc="1"` is
correct on its own account and does not change the render. The stamp is rasterised. That is the
answer, and D-16 tabulates the five failures.

**4. Before editing a condition, print the count at the point of suspicion.** Four hypotheses
about why an invoice table was missing were each plausible from reading the code and each died
on a measurement: the row height, the `vs.size() < 2` guard (23 horizontal and 12 vertical rules
were found), the solidity filter (it never ran), and the `containsAnother` filter (no candidates
reached it). The answer came from printing the rule groups, which showed `xs=2 rows=18 cols=1`
and named the line `if (cols < 2) continue`. One print would have saved an afternoon.

**5. Two commits are worth knowing about when reading a diff.** `6624a3a` superseded the
row-height fix with a sharper statement of the same problem - a cell's line is a line of text,
not the row's pitch - and measured page-count mismatches 20 to 16. `8320115` re-recorded
`base208.json`, so the stored baseline is newer than any note written before it.

