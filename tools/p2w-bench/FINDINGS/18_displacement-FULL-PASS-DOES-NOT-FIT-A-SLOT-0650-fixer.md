# A `--force` corpus pass costs ~105 minutes, so "start the slot with the 212-document pass" cannot be done in a 90-minute slot

**24 Nov 2026, fixer slot 11:15 IST.** Measured on this pod, with the uniform-pitch patch applied
(`git apply FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch`, `build-engine.sh` 53 s)
and `P2W_ENGINE_SRC=/scratch/work/CS`.

## The numbers, from the pass's own log lines

| phase | from | to | wall | documents | per document |
|:--|:--|:--|--:|--:|--:|
| convert (`--force`, 213 docx) | 06:03:49 | 06:41:33 | **38 min** | 209 | 11 s |
| measure + soffice prerender | 06:41:51 | 06:51:40 | **10 min** | 32 | 19 s |
| **extrapolated full pass** | | | **~105 min** | 212 | |

Conversion is charged once per `--force`, and `--force` is mandatory after an engine change. The
measurement phase prerenders twelve `.docx` through soffice before it measures any of them, so a
250-second `--budget` chunk converts-or-renders for most of its window and measures 8-20 documents.
Eight consecutive chunks took the corpus from `docx 4/213` to `docx 213/213` and `measured 36/212`.

105 minutes of pass does not fit a 90-minute slot that must also claim, deploy two agents, read the
last report, prove the change, stamp, commit and release. **Every run that is told to "start the slot
with the 212-document pass" will therefore end with an unstamped engine and a refused commit** - which
is exactly what happened here: `regress.py --check` says
`ENGINE CHANGED (docx): table measured on 3e7f7c44..., the tree is 0045c87a...` and
`REFUSED ... There is no override`.

## What the 36 measured documents say about the patch

The 36 smallest documents were measured on the patched engine and compared with `benchmarks/RANKING.csv`:

    36 compared · 36 identical median_pt · 0 worse · 0 better

That is consistent with the patch being inert where a table has no uniform pitch (the prior run measured
`electricity-bill` and `330_cad_drawing_sheet` byte-identical), and it is **not** a proof of no
regression: the documents with uniform-pitch tables are the longer ones, and none of them was reached.

## What would make the pass fit

1. **A conversion cache that survives the pod.** The 38 minutes of conversion are thrown away at the end
   of every run because `dist2/` and the `.docx` tree live in `/scratch/work`. Anything that persists
   them (or the `--force` becomes incremental per-document on an engine stamp) removes two-thirds of
   the cost.
2. **Measure without re-prerendering.** The prerender batches of twelve are inside the measurement
   window; the same 12-document batch is rendered and then measured, so a chunk pays soffice twice.
3. **Split the pass across two slots with a stamped partial** - but `--stamp` requires the whole table,
   so today a split pass can never be stamped, and the second slot restarts from zero.

Until one of those lands, the honest instruction to a fixer is: **do not start a full `--force` pass
in a 90-minute slot unless the tree is already converted.**
