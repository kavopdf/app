# The overlap: label and value are emitted as two text lines at the same position

**This supersedes everything above it in this file.** Three earlier sections chased line height and row height.
They were wrong, and the reason they were wrong is at the bottom of this page.

## What the overlap actually is

Every totals line in the document is **two separate text lines printed on top of each other** - the label and
its figure, at the same x and nearly the same y:

    'Total job work charges '   y 372.5-385.2   x 357.0-447.1
    '2,81,120.00 '              y 374.9-385.9   x 357.0-404.4    overlap 10.4 pt

    'CGST @ 6% '                y 388.0-399.0   x 357.0-408.7
    '16,867.20 '                y 389.5-400.5   x 357.0-397.3    overlap  9.6 pt

    'SGST @ 6% '                y 402.6-413.6   x 357.0-408.2
    '16,867.20 '                y 404.1-415.1   x 357.0-397.3    overlap  9.6 pt

    'Grand Total '              y 427.5-440.2   x 362.2-417.6
    '3,14,854.40 '              y 429.5-440.9   x 362.2-414.9    overlap 10.7 pt

**The label and the value start at the same x.** They are not two columns and not a right-aligned value - they
are two runs laid on the same spot, one 1.5 to 2 pt below the other.

That is exactly what the user photographed: `Total` and the figure printing through each other so the line
reads as gibberish.

## The cause

**The PDF has the label and the value as separate text spans at slightly different baselines** - typical of an
invoice where the value is drawn right-aligned against the label's line. **The engine is emitting each span as
its own paragraph, both positioned absolutely, and neither knows about the other.**

So the defect is not spacing, not line height and not row height. **It is that a label and its value should
become one line - label, then a tab or a right-aligned run, then the value - and instead they become two lines
in the same place.**

## Why the earlier sections were wrong, and it is my measurement

**I measured y and ignored x.** `E. & O.E.` sits at x 56-284 and `Total job work charges` at x 357-447 - two
different cells of one row - and I reported them as "overlapping 5.2 pt" because 380.1 is less than 385.2.
**They are side by side and never touch.** Two of the four overlaps I reported were that mistake.

The real overlaps only became visible when x was included, and then all four are the same thing: label and
value in the same column at the same x.

**Sixth time in this work that a number described something other than the thing it was printed against.**

## What this means for the two "fixes" already recorded above

**Both are wrong as fixes for this defect and must not be applied.**

- `lineRule exact -> atLeast` with `before` reduced, and `trHeight hRule exact -> atLeast`, **applied together,
  turned a one-page document into two and displaced its content.** The user reported it and it is visible in
  `BOTHFIX-07.docx`, which should not be used.
- They were applied to a cause that was not the cause, so their failure is expected rather than surprising.

**The clipping they were aimed at is a real, separate defect** - a 0.6 pt line box around 8.5 pt text does cut
descenders, on 213 of 213 documents. **That is still true and still worth fixing.** But it is not this bug and
fixing it does not fix this bug.

## The fix for this one

**A label and its value on the same PDF line must become one paragraph**, with the value placed by a right
tab stop at the column's right edge - not two paragraphs at the same position.

**Verification is by x and y together**, not y alone: after the fix there must be exactly one text line where
there were two, and its width must span from the label's left edge to the value's right edge.

**Not applied. Not measured. This is the first correct statement of the cause.**
