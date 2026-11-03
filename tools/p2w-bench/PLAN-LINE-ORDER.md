# Line order — where the work actually is, decided before touching code

Current: **90.33 %** on the 53-document corpus. Six files are behind it. This is what each
one actually is, established by instrumenting the engine, not by guessing.

## What the diagnosis found

The price-list file emits every block with `col=0`. **Column detection never ran.** Its
blocks are individual cells spread across the full page width:

    BLK P y=94 x=40   [ITEM]
    BLK P y=94 x=202  [PACK]
    BLK P y=94 x=243  [TRADE PRICE]
    BLK P y=94 x=309  [ITEM]          <- the second table's header
    BLK P y=94 x=471  [PACK]
    BLK P y=94 x=512  [TRADE PRICE]

Two price tables sit side by side, each with its own header on the same baseline. The
reference reads table one completely, then table two. We read them row by row, so both
headers come out first.

**Why the glyph projection cannot see this.** It looks for an x with *zero* glyph coverage.
Here cells cover x = 40 to 595 with no empty column anywhere, so there is nothing to find.
That is not a threshold problem — it is the wrong measurement for this page.

## The three classes, and why they need different fixes

### Class 1 — cells spread across the width, no column found (3 files)

    price-list-2col-dense-right-aligned   51.8
    product-catalogue-code-left-price     44.3
    balance-sheet-two-columns             61.1

The boundary is not an empty column, it is a **gap between blocks that repeats down the
page**. Find it from block extents, not glyphs: group blocks by baseline, take the gaps
inside each row, and keep an x that appears as a gap in at least a third of the rows.

Tried and reverted: a width-ratio test and a repeated-header test. Both failed because they
were applied at the wrong layer — the row-wise rule runs on paragraphs that were already
ordered, and the ordering here happens before that.

### Class 2 — the TOC, where we over-split (1 file)

    table-of-contents-dot-leaders   67.3

The reference keeps `01 Board of Directors ... 4` on one line. We split it into three. This
is the opposite failure to Class 1 and needs the opposite rule: a number, a long title and a
page number belong on one line, because the middle part is prose.

### Class 3 — a footnote block still covers the gutter (1 file)

    journal-2col-with-footnotes   69.9

The per-band projection found the gutter on three other files but not this one. The footnote
block is probably wide enough to fail the 62 % full-width exclusion, so it is still counted
as a normal line and still pollutes every band.

## What is not worth doing

Every remaining file is a **two-column or three-column layout**. Nine of the thirteen
benchmarks are at 95 % or above and six are at 98 % or above. Touching anything outside line
order risks the numbers that are already good.

## Order of work

1. Class 1 — block-level gutter. Three files, and the mechanism is now understood.
2. Class 3 — check whether the footnote block fails the full-width exclusion.
3. Class 2 — the TOC over-split, which is a different rule and can be done last.

Each one measured on both corpora before it is kept, and reverted if anything falls.
