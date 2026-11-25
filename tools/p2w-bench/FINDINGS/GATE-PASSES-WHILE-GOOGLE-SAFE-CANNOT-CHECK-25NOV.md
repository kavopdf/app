# The commit gate prints PASS on a line that says it could not check

Run on the 10:10 relay's tree:

    engine fingerprint : 981ff1fa35e2cf67
    scope of the change: docx, txt   (scope.py: both)
    docx: no document worse than baseline
    txt : no document worse than baseline
    google-safe : no .docx output directory - cannot check
    PASS - nothing got worse in both formats, and the table matches this engine.

The verdict is PASS and one of the four lines inside it says the google-safe check never ran. A reader
takes the PASS; the caveat sits above it in the same block.

This is the vacuous pass the 08:14 run reported fixing - "the commit gate's google-safe line stopped
printing 'no .docx output directory - cannot check' and started checking. It passed." It checked then
because that pod had a converted corpus. It does not now, so the line is back and the gate is green
again on three checks instead of four.

## Why it matters here specifically

The 10:10 run's whole safety argument is "blast radius: one document". That argument was made by
scanning the corpus PDFs with PyMuPDF, not by the gate. The gate cannot corroborate it while google-safe
is dark, so the one check that would confirm a Google-side regression is the one that did not run.

## The rule

A gate that cannot run one of its checks is not a pass. Either it refuses, or it prints PASS and names
the checks that did not run in the verdict line itself - not three lines above it, where the eye stops.

## Verified, not changed

regress.py was not edited. The missing .docx are a pod state (213 corpus PDFs present, output directory
empty), and corpus-convert.py rebuilds them. What is recorded is that a green gate currently means three
checks, and the fourth is silent.
