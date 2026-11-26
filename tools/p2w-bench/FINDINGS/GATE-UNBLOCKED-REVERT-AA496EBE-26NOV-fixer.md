# The commit gate was closed by one unmeasured engine change. It is now open.

**26 Nov 2026, fixer run. Decision, evidence, and what it costs.**

## What was blocking

    python3 tools/p2w-bench/regress.py --check
      scope of the change: docx   (scope.py: DocxWriter.recordBaseline -> docx)
      ENGINE CHANGED (docx): table measured on a4de7df896875a39, the tree is 7e0de1abdeb221ae
      REFUSED. This commit would land a regression or an unmeasured engine.

    python3 tools/p2w-bench/measure_gate.py
      engine docx a4de7df896875a39, tree 7e0de1abdeb221ae -> NOT READY

No commit could land - not a fix, not a report - until the docx table was re-measured on
7e0de1abdeb221ae, which is a 212-document Google pass. That is why the pipeline looked dead.

## Which commit 7e0de1a is

`regress.engine_fingerprint()` computed per commit (same exclusion list, DOCX_EXCLUDES):

    aa496ebe   docx 7e0de1abdeb221ae   txt 025fe9deda5ac7b1   <- the tree
    9f0a8207   docx a4de7df896875a39   txt a4d8fca469bba636   <- the stamp, and the measured table

`aa496ebe` ("18_displacement: the page-top gap moves from w:before into w:pgMar w:top") is the ONLY
engine change after the state both tables were measured on. ENGINE-STAMP.json held
`docx a4de7df896875a39 / txt a4d8fca469bba636`; the tree was one commit past it and unstamped.

## The record that made this look un-revertable was wrong in its sign

ATTEMPTS.json and both reports carry:

    22:11  lead  0/208  aa496ebe re-measured across 208 of 212: newsletter 0.20->86.30,
                       600 54.30->62.46, but itr-computation 42.33->9.10 - a 33pt regression,
                       so the engine stays unstamped and the gate stays closed

`share5` is the share of a page's ink more than 5 px from where the original PDF drew it
(regress.py, "WHAT WORSE MEANS"). **LOWER IS BETTER.** `itr-computation-with-slab-table` going
42.33 -> 9.10 is a 33.23-point IMPROVEMENT, and it is the third-largest move in the corpus. It was
written up as the reason to refuse the commit. The next run's stated plan ("bisect aa496ebe on
itr-computation-with-slab-table") was aimed at protecting the best thing the commit did.

The commit's real damage is `newsletter-3col-header-footer` 0.20 -> 86.30 and
`600_reviewed_invoice_with_annotations` 54.30 -> 62.46 - 1-3 documents wrecked to buy 1-3.
That is still a trade nobody authorised, and it is still the right call to refuse it. But it is
refused for the correct reason.

## The decision

Restore `DocxWriter.java` to `9f0a8207` - the exact source both tables were measured and stamped on.

    git checkout 9f0a8207 -- app/src/main/java/com/kavopdf/app/engine/DocxWriter.java

Nothing is deleted. The change is kept as a re-landable patch:

    tools/p2w-bench/PATCHES/aa496ebe-pagetop-not-identity.patch   (229 lines)

Why this and not a 212-document re-measure: a re-measure costs a whole slot and buys nothing until
the newsletter break is fixed. Restoring the source makes the repository self-consistent again -
engine == the engine the tables describe - and the numbers in RANKING.csv become true statements
again in the same move.

## Result, measured

    docx tree fingerprint  a4de7df896875a39   == docx stamp
    txt  tree fingerprint  a4d8fca469bba636   == txt  stamp

    python3 tools/p2w-bench/regress.py --check
      scope of the change: docx
      docx: no document worse than baseline
      PASS - nothing got worse in the .docx only, and the table matches this engine.
      CHECKS THAT DID NOT RUN: google-safe - no .docx output directory

## Caveat, stated because it is real

`google_safe.py` did not run - the pod has no converted .docx output directory, so the PASS covers
the regression half only. The google-safe half of the gate is unproven in this clone. Building the
corpus (`pod-prep.sh` -> `build-engine.sh`) exceeded the 300 s sandbox ceiling on this cold pod, which
is the same reason `tools/install-gate.sh` did not finish installing the pre-commit hook.

## What the next run should do with the patch

`aa496ebe` moves the page-top gap from `w:before` into `w:pgMar w:top`. The sub-agent bisect
(/scratch/input/AA496EBE-BISECT.md) found the itr win and the newsletter break come from the same
clause, so the clause cannot be split by inspection alone. The testable hypothesis it proposed:
gate the clause on page count - a single-page document has no page-top gap to spend, so
`pageTopTw = 0` for pages == 1 - and measure `newsletter-3col-header-footer`,
`600_reviewed_invoice_with_annotations`, `601`, `401` (must not move) plus `itr-computation-with-slab-table`
and `bank-statement-5-pages` (must keep their gain). Six documents, one Google pass, decides it.
