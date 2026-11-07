# The pipeline, in the order it runs

One document at a time. Every step is a gate, and a document is not fixed until it has
been through all of them and its findings have been verified.

    0. TOOLCHAIN      JDK, libraries, the engine compiles, the corpus is the right size
    1. CONVERT        PDF -> Result -> .docx and .txt
    2. G1 BUILD       javac + TestPdfToWord + TestRealDocs
    3. G2 REGRESSION  208 documents against base208.json - did anything get worse
    4. G3 STRUCTURE   reflow: body text in text boxes, layout at two widths
    5. G4 TXT         entry hashes inside the .docx - only when the txt changed
    6. G5 POSITION    render vs PDF, matched by text: x, y, size, name, colour
    7. G6a THE EYE    sidebyside.py --record, then OPEN EVERY IMAGE and fill the verdict
    8. G6b NUMBERS    visual.py --verify - the eight questions, each with its evidence
    9. RECORD         looked.py - exit 0 only when every page has a verdict
   10. VERIFY         verify.py - every finding, once, against the PDF
   11. DECIDE         looked.py --combine - the eye first, the numbers as evidence
   12. FIX            only findings that came back VERIFIED. Three tries, one for a stamp
   13. RE-CHECK       after a fix: convert, render, LOOK, re-measure, G2 again
   14. COMMIT         precommit.sh, then commit, then confirm the file landed
   15. LOGS           defects, scores, baselines, the batch log

## Why this order

LOOK BEFORE YOU MEASURE. Step 7 comes before step 8 so the eye forms its own opinion
before it is told what to think. An eye that has already been told "reading order 88.5 %"
is looking for a reason to agree.

VERIFY BEFORE YOU FIX. Step 10 exists because on 7 Nov two of nine findings were false
alarms. A fix applied to a false alarm makes the document worse and hides the bug in the
tool.

THE EYE DECIDES. Step 11 makes the eye's verdict the document verdict and the numbers the
evidence. Measured on 7 Nov: the eye was right 4 out of 4, the computed questions 3 out of
5 with 2 false alarms.

ONE VERIFICATION PER FINDING. verify.py deduplicates on document, page, kind and claim, so
the same problem is checked once however many times it is listed. A finding verified three
times is the same answer three times.

## What must not be reordered

- G1 before G2. A build that does not compile makes G2 meaningless.
- G2 before recording a baseline. A baseline recorded on a run where a document got worse
  makes the regression permanent and invisible.
- The eye (7) before the numbers (8).
- Verify (10) before fix (12). Always.
- precommit (14) before commit, and the commit confirmed after.

## What can run less often

- G5 at the end of a batch, not after every fix - it needs a render of every document.
- G4 only when the .txt changed. G3 only when the .docx changed.
- G2 only when the engine changed, or at the end of a document.
