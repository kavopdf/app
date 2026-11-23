# p2w.py: `--force` compared the tree against another clone's binary

**Instrument defect. Measured 23 Nov 2026, fixer slot claimed 15:02 IST.**

## What I believed, and what is now true

I believed `P2W_ENGINE_SRC=<tree>` made a corpus pass measure `<tree>`. It makes the pass *build* and
*run* `<tree>`'s engine — but `--force`'s staleness test read

    _eng = REPO + "/tools/engine-verify/out/com/kavopdf/app/engine/PdfToWord.class"

`REPO` is `/scratch/work/p2w/repo`, the clone `p2w.py` syncs to `origin/main`. So with the working tree
set as the engine, the "has this build already written this document" clock was **another clone's
binary**. Measured: the tree's class was built at 09:33 UTC, the 213 documents were written 09:38–10:32
by that other clone's unpatched engine, and `--force` skipped **all 213** as newer than the engine.

## Why it matters beyond this run

It is the same failure as the render-cache-keyed-by-name bug already documented twenty lines below it
in the same file: a cache that outlives the thing it caches. It cost this run five conversion calls
(about 22 minutes) producing a corpus that described an engine nobody had chosen, and the only reason
it was caught is that the `.docx` was read directly instead of trusting the run's own log line.

## The fix

    _eng = ENGINE_SRC + "/tools/engine-verify/out/com/kavopdf/app/engine/PdfToWord.class"

One identifier. After it, `--force` rebuilt 213/213 on the patched tree and the structural A/B on
`361_product_catalogue_grid` came back 124 → 40 paragraphs as the finding predicted.

## Second gap, not fixed, worth one line of judgement

`gate.py` has no `--force` flag and does not pass one to `p2w.py`, so after an engine change
`gate.py --budget N` re-*measures* the old `.docx` and reports a table for the old engine. The workaround
is to run `p2w.py --force --budget N` first and `gate.py --budget N` after; that is what this run did.
A `gate.py --force` that forwards the flag would make the honest sequence the obvious one.

## What would prove this wrong

A run where `--force` with `P2W_ENGINE_SRC` set skips a document that the tree's own engine has not
written. That would mean the mtime comparison is not the mechanism and something else is skipping it.
