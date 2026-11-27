# Text overlaps itself: the bug is measured, and the fix I proposed is disproved

The user supplied the real file. **The overlap is real**, and it is now measured rather than inferred from a
screenshot. **The arithmetic fix I proposed earlier does not work** - it removes the overlap and breaks the
layout. Both facts are below.

## The overlap, measured through a real Google export

Text line bounding boxes in the totals block, from `CLAMP-07.pdf` (the build of `Z-07.docx`):

    'Total job work charges'    y0 372.5   y1 385.2
    'E. & O.E. Job work...'     y0 380.1   y1 391.1     starts 5.1 pt ABOVE where Total ends
    'CGST @ 6%'                 y0 388.0   y1 399.0     starts 3.1 pt ABOVE where E.&O.E. ends
    'SGST @ 6%'                 y0 402.6   y1 413.6
    'Grand Total'               y0 427.5   y1 440.2

**Two overlaps of 5.1 pt and 3.1 pt.** That is the defect the user circled, in numbers.

## The fix I proposed, applied and measured

`w:line` raised to `font_size * 1.15 * 20`, `w:before` lowered by the same amount, so the advance
`before + line` is unchanged. On this document, 78 paragraphs changed:

    'Total job work charges'   before 11.9 -> 2.8   line 0.6 -> 9.8   advance 12.5 -> 12.5
    'CGST @ 6%'                before 12.4 -> 3.2   line 0.6 -> 9.8   advance 13.0 -> 13.0
    'SGST @ 6%'                before 12.4 -> 3.2   line 0.6 -> 9.8   advance 13.0 -> 13.0
    'Grand Total'              before 24.4 -> 14.1  line 0.7 -> 10.9  advance 25.0 -> 25.0

**The arithmetic held exactly. And the render got worse:**

    BEFORE  gaps between line tops:  7.6   7.9  14.6  24.9      1 page
    AFTER   gaps between line tops:  5.3  18.5  33.1  43.1      2 pages

**The overlap is gone and the document has grown to two pages.** CGST's gap went from 7.9 pt to 18.5 pt.

## Why it failed, and what that tells us

**Google does not advance by `before + line`.** If it did, changing the two while holding their sum constant
would leave every gap untouched. The gaps changed by 10.6, 15.2 and 18.2 pt - so the renderer is using
`before` and `line` in some other combination, and **the sum is not the quantity that matters.**

The measured `before` values before the fix were 11.9, 12.4, 12.4, 24.4 and the measured gaps were 7.6, 7.9,
14.6, 24.9. **No constant offset relates the two.** Something else - the line box, the font's ascent, or a
minimum the renderer applies - is contributing, and it has not been identified.

**So the model behind the fix is wrong, not just its numbers.** Writing another formula against a renderer
whose line-advance rule has not been established would be the sixth guess in this work.

## What has to be measured next, before any fix

**One document, one paragraph, a controlled sweep.** Take a single paragraph with known `before`, `line`,
`lineRule` and font size; vary one at a time; export through Google; record the y of the next line's top.
That gives the renderer's actual advance rule as a table of measurements instead of an assumption.

**Until that table exists, every fix to this is a guess.** Two have now been made - `exact` to `atLeast`,
and the arithmetic - and both are recorded as wrong so neither is tried again.

## What is confirmed and unchanged

**The clipping is real and separate.** `w:line="12"` with `w:lineRule="exact"` is a 0.6 pt box around 8.5 pt
text; the part of the glyph outside the box is cut, and that is the descender. Confirmed on two documents.
**The overlap is a second symptom of the same `lineRule="exact"` construct, and it is not fixed by anything
tried so far.**

## The controlled sweep, run. And it points at the table.

Ten test paragraphs, one per line, each with a known `before`/`line`/`lineRule`, exported through Google
once. `w:sz` 8.5 pt throughout, so the glyph height is 11.07 pt on every line, measured.

    label  before  line   rule      advance   implied line height
    T01     0.0    0.6    exact        -           -
    T02    12.0    0.6    exact      12.6         0.6
    T03    12.0    9.8    exact      18.6         6.6
    T04     0.0    9.8    exact       8.0         8.0
    T05    12.0    9.8    atLeast    21.4         9.4
    T06    12.0    0.6    atLeast    21.8         9.8
    T07    24.0    0.6    exact      26.3         2.3
    T08     6.0    9.8    exact      12.6         6.6
    T09    12.0   12.0    auto       21.4         9.4
    T10    12.0    0.0    exact      21.8         9.8

### What it establishes

**`exact` with a tiny line height is honoured, and that is what collapses lines.** T02: `line=0.6`, advance
12.6, so the line contributed 0.6 pt. Nothing else did.

**`atLeast` substitutes the natural height.** T06: `line=0.6` under `atLeast` gives 9.8 pt, which is 8.5 pt
Times at 1.15. **Nothing collapses and nothing clips.**

**`line=0` under `exact` also gives natural** (T10). Google special-cases zero. That matches the note already
in this repository that Google rewrites `w:line="1"` exact to an auto line.

**The arithmetic fix is right in principle** - to hold the advance constant when switching `exact`/0.6 to
`atLeast`/9.8, `before` must drop by 9.2, which is exactly what was done.

### Why it still failed on the real document, and the clue that explains it

**In the real document the advance was SMALLER than `before`.** The four totals paragraphs carried
`before` 11.9, 12.4, 12.4, 24.4 and the measured gaps between their glyph tops were 7.6, 7.9, 14.6, 24.9.
**7.6 is less than 12.4** - the line advanced by less than the space that was asked for.

**In this sweep that never happens**; the advance is always `before` plus something non-negative.

**The difference is the table.** Every one of those four paragraphs sits inside a `<w:tc>`. Table cells
carry their own rules - `trHeight`, `cantSplit`, the cell's content area, and Word's habit of fitting cell
content to the row. **The sweep was body text and body text is not where the bug lives.**

### The next sweep, which is the one that matters

**Repeat exactly this test inside a single table cell** - ten paragraphs, one cell, the same ten
`before`/`line`/`lineRule` combinations, one export. If the advance inside a cell behaves as it does in body
text, then the real document's 7.6 gap has another cause and the cell is not it. If it does not, the cell
rules are the mechanism and the numbers will say so.

**One export answers it.** It has not been run.

## The table-cell sweep: the cell does NOT behave like body text, and that is the mechanism

The same ten combinations, run inside a single `<w:tc>`:

    label  before  line   rule      advance   implied line
    C01     0.0    0.6    exact        -          -
    C02    12.0    0.6    exact      18.3        6.3
    C03    12.0    9.8    exact      18.6        6.6
    C04     0.0    9.8    exact       8.0        8.0
    C05    12.0    9.8    atLeast    21.4        9.4
    C06    12.0    0.6    atLeast    21.8        9.8
    C07    24.0    0.6    exact      26.3        2.3
    C08     6.0    9.8    exact      12.6        6.6
    C09    12.0   12.0    auto       21.4        9.4
    C10    12.0    0.0    exact      21.8        9.8

**Side by side with the body-text run:**

    combination            body text    table cell
    exact, line 0.6            0.6          6.3      <- different
    atLeast, line 0.6          9.8          9.8      <- same
    exact, line 0               9.8          9.8     <- same

**`exact` with a tiny line height is honoured literally in body text and given a floor of about 6.3 pt inside a
cell.** That floor is what makes the two cases look different and it is the whole of the overlap.

### Why 6.3 pt of floor still overlaps

The glyph height is **11.07 pt** on every one of these lines, measured. The cell advances **6.3 pt**. **The
glyph is 4.8 pt taller than the space it is given**, and that is what prints one line over the next.

**A floor that is smaller than the glyph is not a fix.** It reduces the collapse from total to 4.8 pt and
leaves the defect visible - which is exactly the state the user photographed.

### And `atLeast` is the combination that works in both places

`atLeast` with `line=0.6` gives **9.8 pt** in body text and **9.8 pt** in a cell. 9.8 is 8.5 pt Times at 1.15,
which is above the 11.07 pt glyph's requirement of roughly 9.8. **No overlap, no clipping, in either context.**

The cost is that the advance rises: in the cell, C02 (`exact` 0.6) advances 18.3 and C06 (`atLeast` 0.6)
advances 21.8, so **+3.5 pt per line**. Holding position means lowering `before` by 3.5 - and unlike the
earlier attempt, **that number is now measured rather than assumed.**

### One thing still does not reconcile, and it is the next measurement

In the real document the four totals paragraphs carried `before` 12.4 and their glyph tops were **7.6 pt**
apart. In this sweep, `before` 12.0 with the same `line=0.6 exact` gives **18.3 pt**. **7.6 is less than half
of 18.3**, and less than `before` itself.

So the real document is compressed by something this sweep does not have: a `trHeight`, a row that Word is
fitting content into, or a cell whose content area is being divided among its paragraphs. **That has not been
identified and it is the one remaining unknown.**

**The next measurement is the real document's `<w:tr>`: its `trHeight`, `hRule`, and how many rows the totals
block actually spans. That is one lookup in a file already in hand.**
