# The unmeasured engine change aa496ebe, re-measured across the corpus

**26 Nov 2026, fixer slot 21:10 IST.** Engine tree `7e0de1abdeb221ae`; published table stamped
`a4de7df896875a39` (written at commit 9f0a8207, 26 Nov 02:54 UTC). Commit **aa496ebe**
(26 Nov 10:20 UTC, "18_displacement: the page-top gap moves from w:before into w:pgMar w:top")
changed DocxWriter.java after that stamp and was never re-measured, so
`measure_gate.py` says NOT READY and `regress.py` refuses every .docx change as unmeasured.
That is why this run measured instead of fixing.

## What was done

    corpus-slice.py                213/213 converted, 0 failed, stamp 025fe9deda5ac7b1
    benchmarks/p2w.py --budget ... 208 of 212 documents measured on the live tree

Not finished: 4 documents remain unmeasured. `324_loan_amortisation_schedule.docx` was refused
twice by soffice (91 s, no render) and is recorded in `PRE/.soffice-fail`; the other three were
still being retried when the slot ended. The table is therefore a **partial**
(`/scratch/output/RANKING.partial.csv`), and the published RANKING.csv is untouched.

## Result, 208 documents compared share@5 to the published table

    improved   3
    unchanged  204
    regressed  1        <- itr-computation-with-slab-table  42.33 -> 9.10   (-33.23)
    mean       2.795 -> 3.089

    newsletter-3col-header-footer          0.20 -> 86.30   (+86.10)
    600_reviewed_invoice_with_annotations 54.30 -> 62.46   (+8.16)
    39_small_caps_letter_spacing           0.70 ->  0.80   (+0.10)

## The reading

The pgMar page-top patch is real and it is large: `newsletter-3col-header-footer` goes from
0.20 to 86.30, and `600` from 54.30 to 62.46 - the two documents the commit was aimed at. But it
also takes `itr-computation-with-slab-table` from 42.33 to 9.10. One document traded for two is
not a pass: the rule is no document gets worse, and this one does, by 33 points.

The patch is therefore **not stampable as it stands**. Two ways forward, both cheap now that the
cache is warm:

1. bisect the 141-line diff in aa496ebe on `itr-computation-with-slab-table` alone - the section
   w:pgMar w:top is written per section, and a slab table that spans pages is the shape most
   likely to have its page-top term double-counted;
2. if the two cannot be separated, keep the patch and exempt nothing: revert to 9f0a8207 and
   carry the newsletter gain as an unlanded lead.

The re-measure itself is worth keeping: 208 documents are cached against the live tree, so the
next run needs 4, not 212.
