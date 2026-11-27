# Text overlaps itself in table cells - reported, not yet reproduced

The user circled a region of a table where **two text runs sit on the same line and print over each other**:
`Total` collides with a figure, `₹6,857@6%` appears twice at the same y, and `Grand Total` collides with a
number. It is a different symptom from the clipping recorded in
`TEXT-CLIPPED-AT-THE-BOTTOM-EXACT-LINE-HEIGHT-27NOV-agent.md`, and it may or may not share the cause.

## What could not be done

**The document in the screenshot could not be matched to anything in the corpus.** The numbers visible are
`12000`, `6,857` and `6,54,40`. Searching every `.docx` in `p2w/out/` and every file built into
`/scratch/output/` for any two of those strings returns **no match**.

`07_stamp_over_table.docx` - which the screenshot's title names, and whose stamp (`QUALITY APPROVED`,
`KAVERI TEXTILES`) and column headings match - contains:

    CGST @ 6% 16,867.20
    SGST @ 6% 16,867.20
    Grand Total 3,14,854.40

**Different figures in the same layout.** So either a different version of that document is in use, or a
different document with the same template. **Until the actual file is supplied, this cannot be reproduced and
must not be diagnosed.** Guessing at a cause from a screenshot is how five wrong hypotheses were produced
earlier in this work.

## What the screenshot does establish

The layout, the stamp and the column headings are document 07's. Two runs at the same y in the totals block
means **two paragraphs starting at the same vertical position inside a table cell.**

`07_stamp_over_table.docx` is a real table - 36 rows, 63 cells - and its totals paragraphs carry:

    Total job work charges   w:before="238" w:line="12" w:lineRule="exact"   8.5 pt
    E. & O.E. Job work char  w:before="358" w:line="11" w:lineRule="exact"   8.0 pt
    CGST @ 6%                w:before="248" w:line="12" w:lineRule="exact"   8.5 pt
    SGST @ 6%                w:before="248" w:line="12" w:lineRule="exact"   8.5 pt
    Grand Total              w:before="487" w:line="13" w:lineRule="exact"   9.0 pt

**CGST and SGST carry the identical `w:before="248"` and `w:line="12"`.** If they ever land in the same cell
rather than successive cells, they print on top of each other - and the screenshot shows `₹6,857@6%` twice at
one y, which is exactly that shape.

**So the most likely mechanism is a row-span or cell-assignment error: two paragraphs that belong in
different cells are placed in the same cell, and the identical `w:before` puts them at the same y.**

**Most likely is not measured.** It needs the file.

## What to do when the file arrives

1. Find the two paragraphs that overlap, by text.
2. Check whether they are in the **same** `<w:tc>` or in two different ones.
3. If the same cell: the cell assignment is wrong, and the fix is in whatever maps PDF text to cells.
4. If different cells: the table's grid is wrong - check `<w:tblGrid>` column widths against the cell widths,
   because a cell narrower than its content can spill over its neighbour and produce this exact look.

**Neither branch has been checked. Do not patch either until it is.**
