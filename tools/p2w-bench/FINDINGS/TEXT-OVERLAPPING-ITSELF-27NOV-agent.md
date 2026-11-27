# Text overlapping itself - the supplied file does not reproduce it, and its spacing is adequate

The user supplied `Z-07_2.docx` in response to the report. **It is not the document in the screenshot**, and
its paragraph spacing is adequate, so it would not produce the overlap.

## The file does not match the screenshot

The screenshot's visible figures are `12000`, `6,857` and `6,54,40`. In `Z-07_2.docx`:

    12000  -> not found
    6,857  -> not found
    6857   -> not found

Its totals block reads `2,81,120.00`, `16,867.20`, `16,867.20`, `3,14,854.40`. **Same template, different
figures.** The file in the screenshot is still not in hand.

## And in this file the spacing is sufficient, so it would not overlap

The `<w:tc>` containing `Grand Total` holds four paragraphs:

    'Total job work charges 2,81,120.00'  8.5 pt  before 11.9 pt  line 0.6 pt  advance 12.5 pt
    'CGST @ 6% 16,867.20'                 8.5 pt  before 12.4 pt  line 0.6 pt  advance 13.0 pt
    'SGST @ 6% 16,867.20'                 8.5 pt  before 12.4 pt  line 0.6 pt  advance 13.0 pt
    'Grand Total 3,14,854.40'             9.0 pt  before 24.4 pt  line 0.7 pt  advance 25.0 pt

**8.5 pt of text needs about 6.4 pt of vertical room. Every advance here is 12.5 pt or more.** The vertical
position comes from `w:before`, which is correct; `w:line` only sets the box height. **So these four lines
sit apart and do not print over each other.**

**Four paragraphs in one cell is unusual but not itself the bug** - it is one cell holding a stacked totals
block, which is a legitimate structure.

## What this file does confirm

**The clipping, with exact numbers.** `w:line="12"` with `w:lineRule="exact"` is a **0.6 pt** box around
**8.5 pt** text. The glyph extends well outside the box and the part outside is clipped - the descender. That
is `TEXT-CLIPPED-AT-THE-BOTTOM-EXACT-LINE-HEIGHT-27NOV-agent.md` reproduced here in a second document with
the same figures.

## So the overlap remains unexplained, and unexplained is the honest state

Two candidates were proposed and neither survives this file:

- **identical `w:before` putting two paragraphs at one y** - the values here are 11.9, 12.4, 12.4, 24.4, which
  are distinct and adequate
- **a table grid narrower than its content** - this table's grid is
  `639 1012 5137 988 1315 700` twips, six columns, and the cell holding the totals carries no `gridSpan` and
  no `vMerge`

**Neither can be blamed without the actual document.** The next step is the file in the screenshot, not
another hypothesis about it.
