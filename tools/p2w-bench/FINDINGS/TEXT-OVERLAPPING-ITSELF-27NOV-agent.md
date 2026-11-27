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
