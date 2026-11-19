# flow-continuation-baseline

**Status: KEPT - applied to the engine on 19 Nov and measured across all 213 documents.**

The patch file beside this note is the same change, kept for the record; it is already in the
tree, so do not apply it again.

    git apply --reverse --check tools/p2w-bench/patches/flow-continuation-baseline.patch   # already applied

Full corpus, this engine: **13 documents improved, 0 worse, 198 unchanged**. The first attempt at
it was not kept - it passed its class screen but could not pass the corpus gate, because the
committed `RANKING.csv` did not reproduce from its own engine (ten stale rows, see
`FINDINGS/ratchet-stale-table-210500-9f2c.md`). Publishing the table the engine actually produces
cleared that, and the change was then measured properly.

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

Whole corpus, 213 documents, 0 worse:

    report-2col-table-spanning-both-columns   16.10 -> 0.76
    78_mixed_english_devanagari_line          13.51 -> 1.73
    66_two_col_footnotes_bottom               13.03 -> 2.92
    bank-statement-horizontal-rules-only       6.89 -> 0.10
    gst-invoice-horizontal-rules-only          6.72 -> 0.38
    table-of-contents-dot-leaders             10.72 -> 4.97
    65_two_col_full_width_figure_caption       4.91 -> 1.75
    newsletter-3col-header-footer              2.51 -> 0.20
    brochure-3col-with-sidebar-box             4.51 -> 2.30
    70_magazine_drop_cap_photo_caption         1.49 -> 1.16
    (+ 315_gazette_notification, 28_value_overflows_cell_txtpos, 39_small_caps_letter_spacing)

Two documents the FIRST version of this change broke, and the third constraint that fixed them:
`350_question_paper` 0.11 -> 19.59 and `67_two_col_with_sidebar` 0.80 -> 7.82. Both are pages
where two things sit at nearly the same y but are not one row - a sidebar label 0.85 pt off a
body line. The test is therefore exactness (0.2 pt, which is rounding), not a fraction of the em.

The residue is the continuation's own half-line: 0.46 pt at 6.6 pt type. Removing that needs
the two halves in ONE paragraph, which is the layout's job, not the flow's.
