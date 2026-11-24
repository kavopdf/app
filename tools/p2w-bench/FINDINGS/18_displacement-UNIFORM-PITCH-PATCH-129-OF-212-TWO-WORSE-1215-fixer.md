# 18_displacement uniform-pitch patch: measured 129 of 212, TWO documents worse by <=0.22 — cause not separated

**24 Nov 12:15 IST. The patch is `FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch`.**

## What I did

Applied the patch to `DocxWriter.java`, built the engine (`build-engine.sh`, 57 s), converted all 213
corpus documents one JVM per document (the p2w.py rule: a document's score must not depend on its
batch), and measured 129 of 212 before the slot ran out.

## What I measured

Against `benchmarks/RANKING.csv` on `share5`:

    worse   2     better  1     unchanged 126

    WORSE   404_sudoku_grid              0.27 -> 0.49
    WORSE   03_stamp_vertical_90deg     16.98 -> 17.20
    BETTER  406_passport_mrz_page        3.45 -> 3.15

The previous run's note (`ATTEMPTS.json`) says the same patch measured 200 of 212 with **zero worse**.
My measurement disagrees on 2 of 129. **The two runs did not use the same renderer**, and that is the
confound: this pod's `soffice.bin` converts nothing (see
`INSTRUMENT-soffice-bin-silently-converts-nothing-on-a-fresh-pod-1200-fixer.md`), so every number above
was produced through `/usr/bin/soffice` instead. A 0.22 difference on a rotated stamp is exactly the
size of difference a profile change can make.

## What is now true

* The patch is **not refuted**, and it is **not proven** either. It is unlanded and must stay unlanded
  until one run measures it with a renderer it has also measured the baseline with.
* The 0.22 delta is **not** automatically the patch's fault. `404_sudoku_grid` is a uniform-pitch grid,
  which is precisely the table class the guard admits — so it is also not automatically the renderer's.

## What would prove this wrong / settle it

Re-measure the **unpatched** engine on this pod with the wrapper, on `404_sudoku_grid`,
`03_stamp_vertical_90deg` and `406_passport_mrz_page`, and compare against the same three documents
measured with the patch. If the unpatched tree already reads 0.49 / 17.20 here, the delta is the
renderer and the patch is clean on 129. If it reads 0.27 / 16.98, the patch regresses two documents and
must not land without a guard that excludes a grid.
