# The pass is ~55 min of compute on a 1.05-core box, and every chunk spent all of it converting

**24 Nov 2026, fixer slot 13:12 IST.** Measured first hand on this pod, engine built from the
repository head (`b97d8172ce642eb0`), corpus 213 PDFs fetched from the release zips.

## The cost, phase by phase

| phase | measured | per document | whole corpus |
|:--|:--|--:|--:|
| bare JVM start (`java ConvertOne` with no args) | 0.255 s | - | - |
| one conversion, cold page cache | 3.0-4.4 s | - | - |
| **conversion, sustained through the corpus** | 37 docs in 245 s | **6.6 s**, then 5 in 110 s and 10 in 110 s = **11 s** | **~39 min** |
| measurement, render already prerendered | 2.4-4.4 s | ~3-4 s | - |
| measurement, one 7-page bank form | 81.4 s | - | - |
| soffice prerender, batches of 12 | 8.2 s for 3 cold | ~1.7 s | ~6 min |
| **measurement, whole corpus** | | | **~15-20 min** |

A single-document timing on a warm page cache reads **3x fast**. The last run's 38-minute
conversion was right; a one-document `ConvertOne` is not a measurement of the pass.

## Parallelism cannot help: this pod is 1.05 cores

    /sys/fs/cgroup/cpu.max  ->  105000 100000      (1.05 CPUs)

`nproc` says 2, which is the host's cores, not the quota. Measured, not inferred: 10 documents
converted one at a time took 65.8 s (6.6 s/doc); the same 10 through 2 worker processes took
59.8 s (6.0 s/doc) - **1.10x**, and the `.txt` was **identical on 10 of 10**. So parallel
conversion is safe and buys nothing, and the same is true of parallel measurement (7 documents,
serial 21.5 s, pooled 21.2 s, 1.02x, every `median_pt` and `share5` identical). Both changes were
written, measured and **reverted**. Do not spend another slot on either.

## The defect that was actually stopping the pass

`main()` ran `docx(end); run(end)` with ONE deadline. `docx()` spends the whole budget converting,
so `run()` then found the deadline gone. Three consecutive chunks, verbatim:

    docx 37/213 -- converting 213 ... measured 0 of 212
    docx 42/213 -- converting 213 ... measured 0 of 212
    docx 52/213 -- converting 213 ... measured 0 of 212

**Every chunk converted and no chunk measured.** The last run saw the same shape from outside -
eight chunks to reach `docx 213/213` and only `36/212` measured - and read it as "the pass does
not fit a slot". True, but not the whole of it: the measurement phase was only ever entered on a
chunk that had already run out of time, so the pass could not have finished with unlimited slots
either. `rank()` already writes `RANKING.partial.csv` on a partial run and leaves the published
table alone, so a chunk that measures is safe.

## The change

`CONVERT_SHARE=0.55`: conversion gets 55% of the window, measurement gets the rest.

**Before / after, same engine, same corpus, one `--budget 250` chunk:**

| | measured |
|:--|--:|
| before | **0** of 212 |
| after | **24** of 212 |

That is the whole before-and-after: 24 documents that a chunk now measures and previously threw
away. It does not shorten the pass; it makes a chunk's work land.

## What a run that intends to finish the pass must do

1. Claim, read, deploy the two agents - **and nothing else**. No instrument investigation.
2. Six to seven back-to-back `--budget 250` chunks, ~30 min, no gaps between them.
3. `regress.py --check`, `--stamp`, commit.

Budget: ~39 min conversion + ~15-20 min measurement = **55-60 min of compute**, and the per-call
overhead is ~12 s (scipy instrument gate, engine check, soffice warm). A 90-minute slot fits it
with ~15 min for the claim and the report, and no room for a third thing.
