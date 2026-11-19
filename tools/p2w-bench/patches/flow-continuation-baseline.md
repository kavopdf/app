# flow-continuation-baseline

**Status: measured on its class, NOT KEPT. The engine is reverted; this patch is not applied.**

It passed its own screen (3 improved, none worse) and it could not be carried through the
corpus gate - not because of what it does, but because the committed `RANKING.csv` no longer
reproduces from its own engine (see
`FINDINGS/ratchet-stale-table-<time>.md`). The patch is saved here so the next run applies it
with one command instead of rediscovering it.

    git apply tools/p2w-bench/patches/flow-continuation-baseline.patch
    bash tools/p2w-bench/build-engine.sh
    python3 tools/p2w-bench/screen.py --class content-present-partly-displaced

## The bug

A row the page drew as **one baseline** is emitted by `DocxWriter` as **two or three
paragraphs**: the left columns, then the amount columns. The first paragraph is spaced to its y
by the pitch solver. The second is written with `w:before="0"` - there is no gap to give it -
and the flow, which has already spent the first paragraph's line box, places it one hairline
box lower than the shared baseline.

The pitch solver then reads `ctx.lastBaseline` as *the page's y* and computes every following
row's gap from a place the reader was never at. Nothing took the shift back, so it accumulated:
one hairline box per split row, all the way down the page.

Measured on `bank-statement-horizontal-rules-only` by subagent A (finding
`FINDINGS/content-present-partly-displaced-bankpitch-133100-d68d.md`): 17 row paragraphs at
`w:before="359" w:line="9"` (the row advance is right, 18.400 pt) and 12 amount paragraphs at
`w:before="0" w:line="9"`. Dates at 132.001 pt at the top of the page and 431.801 pt at the
bottom: a mean pitch of 18.7375 pt against the page's own 18.4 pt, +5.847 pt of drift by
y=421. Predicted and observed agree to 0.05 pt.

## The fix

`recordBaseline()` - one helper, called by both `flowRow` and `flowFromBox` where they record
`ctx.lastBaseline` / `ctx.lastLinePt` / `ctx.lastSize`. When a paragraph starts on the baseline
the flow is already at (a continuation of a split row, not a new line), the baseline it records
is the one the box ACTUALLY landed on:

    lastBaseline = lastBaseline + (1 - LINE_BASE) * lastLinePt + LINE_BASE * linePt

so the next row's pitch is relative to the page's next baseline again and the drift stops at
that one row instead of accumulating down the page.

Two constraints, both measured, both in the patch:

* the tolerance is a quarter of the SMALLER of the two boxes. Taking it from the new box alone
  let a 34 pt drop cap swallow the 9.2 pt line 7.7 pt above it and pushed
  `70_magazine_drop_cap_photo_caption` 3.4 pt down (1.49 -> 4.28).
* the base is the baseline already recorded, not the paragraph's own y. Measuring the second of
  three boxes from the shared y counted one continuation of two and left 0.65 pt of the 1.3 pt
  on `table-of-contents-dot-leaders` (8.52 -> 10.72 before this was fixed, 8.52 -> 4.97 after).

## What it measured

Screen, `content-present-partly-displaced`, 18 documents, 0 worse:

    bank-statement-horizontal-rules-only     6.89 -> 0.10
    table-of-contents-dot-leaders            8.52 -> 4.97
    65_two_col_full_width_figure_caption     4.91 -> 1.75

Measured directly with this engine on the stale-table documents:
`report-2col-table-spanning-both-columns` 15.22 -> 0.76 (its continuation drift was the whole
defect).

The residue is the continuation's own half-line: 0.46 pt at 6.6 pt type. Removing that needs
the two halves in ONE paragraph, which is the layout's job, not the flow's.
