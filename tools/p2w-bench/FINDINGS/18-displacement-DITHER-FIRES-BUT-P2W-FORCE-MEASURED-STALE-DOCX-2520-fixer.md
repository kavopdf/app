# 18_displacement - the row-pitch dither fires and changes the .docx; `p2w.py --force` then measured the previous build

**Slot 25 Nov 01:00-02:30 IST. Outcome: `lead`, 0 documents moved. Engine reverted to HEAD.**

## What was tried

`patches/18-displacement-row-pitch-dither-ONLY.patch` - the row-pitch dither alone, with the
spacer hunk deliberately excluded because HEAD already supersedes it behind the room guard
(`DocxWriter.java:6092-6111`: a 1-twip hairline plus `spacerSplitTw`). The patch's spacer hunk
would have deleted that guard.

Applied clean to HEAD (`git apply --check` OK), compiled, and the engine ran.

## The dither is not a no-op - it fires, and it moves the row grid

Instrumented at `DocxWriter.java:6386` (`ditherOn = exactRows && !t.recut && ctx.squeeze == 1f`)
and converted four documents with `ConvertOne`:

    mobile-bill                        rows=5/8/11  exactRows=true recut=false squeeze=1.0
    table-with-no-header-row           rows=26      exactRows=true recut=false squeeze=1.0
    two-tables-stacked-with-no-gap     rows=13      exactRows=true recut=false squeeze=1.0
    362_price_list_dense               rows=29      exactRows=true recut=false squeeze=1.0

The gate is open on every one of them. The output changes accordingly - `w:trHeight` in
`mobile-bill.docx`:

    HEAD       24 rows: 360 x15, 380 x9        (18.0 / 19.0 pt - 380 is off the 0.75 pt grid)
    + dither   24 rows: 345 x15, 360 x6, 375 x3  (every value a multiple of 15 twips)

So the mechanism the patch claims - diffuse the pitch onto Google's measured 0.75 pt grid -
is doing what it says at the XML level. What is NOT established is whether it moves the page.

## The measurement that was supposed to answer that is invalid

`python3 benchmarks/p2w.py --force --budget 240` printed:

    docx 0/213 -- converting 213
    corpus 213/213  docx 213/213  measured 165/212

and the 165-document comparison against `benchmarks/RANKING.csv` came back **0 worse, 0 better,
165 identical to 0.01**. A clean null result - and it is a false one.

`/scratch/work/p2w/out/mobile-bill.docx` has mtime **19:57**, and `362_price_list_dense.docx`
**19:50**. The patch was applied at 19:59 and `p2w.py --force` ran at 20:06. The converter
reported "converting 213" and wrote nothing for at least these two documents, so the pass
measured the pre-patch build against the pre-patch table. `--force` is not forcing.

The proof that it is stale rather than merely subtle: the same document converted by hand at
20:29 with the dither on has 345/360/375, and the file `p2w.py` measured has 360/380.

## Why this matters more than the class

Every fixer run that changes the engine and then measures it through `p2w.py --force` may be
reading the previous build. That is the same shape as the two instrument defects already recorded
in this directory (a counter that counted result files as measurements; a stamp that trusted a
fossil). It is worth more than 39.6 documents, because it can turn any fix into a false "no change"
- which is what a run reports when it cannot land, and what this run would have reported if the
trHeight had not been read by hand.

**Next run, first:** reproduce the stale reuse on a two-document subset (`--force`, then compare
mtime and the trHeight list before and after), find the skip condition, and fix it. Then re-run
this dither through a measurement that is known to be fresh, and decide the class on that.

## Falsifier for the dither itself, unmeasured

The finding says `table-with-no-header-row` 46/47 and `mobile-bill` 46/47 should both reach 47/47,
with `362_price_list_dense` and `two-tables-stacked-with-no-gap` unchanged, and `mobile-bill` /
`insurance-policy-schedule` must not lose a page. None of that has been checked in Google. The
patch is NOT committed; the engine is at HEAD.

The `+0.70 pt/row` and `0.9634` factor quoted in the pending list does not appear in either patch
or in the finding file - only the 0.75 pt quantum, 0.40 pt lost per row, 5.2 pt at the foot of a
13-row table, and an 18.75/18.00 alternation. Treat the 0.9634 figure as unsourced until a file
carrying it is found.
