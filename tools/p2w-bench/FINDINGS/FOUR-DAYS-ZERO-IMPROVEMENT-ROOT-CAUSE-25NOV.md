# Why four days produced zero document improvement

The trend, read from PROGRESS.md:

    2026-11-22   docx open 59   txt failing 16   google 192   clean 23
    2026-11-23   docx open 59   txt failing 14   google 190   clean 30
    2026-11-24   docx open 59   txt failing 14   google 190   clean 35
    2026-11-25   docx open 59   txt failing 14   google 213   clean 42

docx open is 59 on all four rows. txt failing is 14 on three. Nothing improved.

`clean` rose 23 to 42, and that is not improvement: `google` measured rose 192 to 213 over the same days,
so more documents were seen. The documents did not get better; more of them got counted. A metric that
moves only because its population grew is the same defect this directory has spent the day removing.

## The cause, measured

Every fixer run ends the same way: 70 findings on 18_displacement, 0 documents moved. Patches are written,
measured on one or two documents, then reverted because regress.py --check refuses them - and it refuses
because the tree is unmeasured, which is true only because the corpus is not built on the pod.

On 25 Nov the pod held 143 of 213 .docx. With 143 the gate printed:

    google-safe : no .docx output directory - cannot check
    PASS

A PASS on three checks. Any engine patch lands against that and the fourth check never runs, so the gate
was either refused (unmeasured tree) or green without checking - and a run that sees green lands nothing
because it cannot prove the patch is safe.

## What was done about it

The corpus was completed in two slices: 143 -> 196 -> 213, stamp 981ff1fa35e2cf67. Then:

    docx        : no document worse than baseline
    txt         : no document worse than baseline
    google-safe : no construct Google ignores has spread
    PASS - nothing got worse in both formats, and the table matches this engine.

All four checks run. The gate is green for the right reason for the first time in four days, and an engine
patch that does not regress can now land.

## The lesson, in one line

A pipeline that measures everything and lands nothing is not being careful. It is missing the step
between measuring and landing, and that step was a corpus that nobody rebuilt because the measurement
that needed it kept passing without it.
