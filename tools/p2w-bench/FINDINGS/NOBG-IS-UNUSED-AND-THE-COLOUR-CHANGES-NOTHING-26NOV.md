# `nobg` demands a construct that changes nothing. It is also not used. Do not touch it.

## The question

`PIPELINE.md` (8 Nov) says the white patches were fixed by removing `<w:background w:color="FFFFFF"/>`
and moving the colour to a document default, and that `gate.py`'s `nobg` check now looks for
`<w:color w:val="000000"/>` in `docDefaults`.

Commit `5b6e24bb` (9 Nov) then removed that colour on purpose:

    // NO w:color here at all. It used to be 000000, which decided 325 of 414 runs
    // on 178 of 558, and neither writes a colour in docDefaults at all.

So the documentation describes one state and the code another. Which is right?

## What was measured

Two copies of a real corpus document, `310_court_judgment.docx`, identical except that one carries
`<w:color w:val="000000"/>` in `docDefaults` and the other does not. Both uploaded, converted to a
Google Doc and exported to PDF.

    variant     ink     white   chars  imgs  hash
    nocol     41312   913168    1380     0  d84691176da3
    withcol   41312   913168    1380     0  d84691176da3

**Byte-identical.** Zero ink difference, zero white difference, same hash. The colour is invisible to
Google's renderer.

So `5b6e24bb` was right: the colour buys nothing, and it decided the colour of 325 of 414 runs while it
was there, which is a real risk for no return.

## And `nobg` is not in the verdict

    verdicts on the current engine: 208
    nobg in any failed list:          0

`nobg` is a field `gate.py` computes for its own scoring. It never appears in the Google verdict that
the pipeline acts on. All 213 documents "fail" it and nothing happens.

## What follows

Nothing. `nobg` is not causing a false alarm in the pipeline because the pipeline does not read it.
Changing it would be a change with no measured effect, which is the same mistake as the colour it
describes.

What is still not explained: the user sees white patches in Google Docs on almost every document. They
are not in the PDF export — this document exports clean, 0 images, 1380 characters. The 8 Nov note names
the mechanism as Google Docs **dark mode** painting the white back over the inverted page. That is a UI
behaviour, not a render behaviour, and it cannot be measured through the export API. The next test has to
look at the Docs UI, not at a PDF.
