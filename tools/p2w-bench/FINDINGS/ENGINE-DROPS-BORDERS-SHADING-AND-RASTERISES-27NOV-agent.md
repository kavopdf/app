# The engine drops table borders and shading, and rasterises 17 pieces of content

Found while checking a tab-stop fix against the source PDF. **These are not caused by that fix** - they are in
the engine's own output and they are far larger than the defect being chased.

## Measured, one document, one page

                        banner  drawings  filled  lines  shade-rects  images
    source PDF            yes      19        3      16       2          0
    engine .docx export   yes       2        1       1       0         17
    after a tab fix       yes       4        2       2       1         16

## Four defects, in order of how much they cost

**1. Table rules are gone.** The source draws **16 line segments** - the invoice's row rules and column rules.
The engine's export draws **1**. The table reads as an unruled list.

**2. Shading is gone.** `<w:shd` appears **zero times** in the `.docx`. The source has two shaded rectangles -
the header banner and the `Grand Total` row. Both are absent.

**3. The banner's text is invisible.** `TAX INVOICE — JOB WORK` **is** in the document - text extraction finds
it - but it is drawn in white on a background that has no shading, so it is white on white. **Text that exists
and cannot be seen is worse than text that is missing**, because every completeness check that reads the text
layer reports it as present.

**4. Seventeen images in a document that had none.** The source PDF contains **0 images**. The engine's output
contains **17**. Content that is vector in the source is being rasterised into pictures.

## Why 4 matters most

Rasterised content cannot be edited, cannot be searched, does not scale, and carries none of the original's
text. It also explains the other three: **if a rule or a shaded box is emitted as a picture rather than as a
`w:tcBorders` or a `w:shd`, then the numbers above are exactly what you would see** - 16 source rules become
1 drawn line plus pixels, two shaded rectangles become one, and the banner's white text sits on a picture that
did not render where it should.

**That is a hypothesis, not a measurement.** What is measured is the counts.

## What this means for the work being done

**The tab-stop defect that was being fixed is real and is now fixed** - 4 overlaps to 0, page count unchanged.
But it is a small defect next to these four, and the user's judgement that the two documents differ "a lot" is
correct and is about these, not about the tab.

**Do not measure this document by text extraction alone.** Every one of these four defects is invisible to a
text-layer check: the banner text is present, the table's words are present, the numbers are present. **They
are visible only in a render.**

## The check that would have caught all four

    render both to images, same DPI
    compare the count of distinct line segments
    compare the count of filled regions
    compare the count of rasterised regions against the source's
    then, and only then, compare text

**Three of those four are geometry and colour, and the existing text-based checks see none of them.**
