# One cause, 28 documents: a rule is a drawing, and Google drops drawings

Measured on the first 50 documents verified against Google's renderer
(`benchmarks/gverify/`, instrument `verify_google.py`, 42 checks).

    05_chars_extra      30 docs
    32_stroke_lines     28 docs      <- the same documents, almost exactly
    18_displacement     19 docs

`05` and `32` co-occur. That is not two defects; it is one thing the engine emits that the page did
not, and it is the largest single lever in the table.

## What the two checks actually report

Taken on `18_centred_heading_left_body_txtpos`:

    05_chars_extra    source=0    render=1
    32_stroke_lines   source=2    render=2      (the second field is LOST, not rendered)

    words only in the render: {'\u200b': 1}
    words only in the source: {}

    horizontal rules   source 2    render 0

One zero-width space appears that the page never had, and both rules the page drew are gone.

## Where they come from

The .docx for that document contains:

    <w:pBdr>            0
    <w:tcBorders>       0
    <w:tbl>             0
    U+200B              0
    <w:drawing>         2

So the rules are neither paragraph borders nor table cell borders nor a table. They are **floating
drawings** - one per rule, matching the two rules the page draws.

Google Docs does not lay out floating drawings from an imported .docx. It drops the shape and leaves
the anchor: a `U+200B` where the drawing was anchored. That is the extra character `05` counts, and
the vanished rule is what `32` counts. One construct, two checks, 28 documents.

## What the fix has to be

A horizontal rule that spans a width at a y the page drew should be emitted as a paragraph border -
an otherwise empty paragraph carrying `<w:pBdr><w:bottom w:val="single" w:sz=... w:color=.../>` with
the paragraph's indents set to the rule's x range. Word, LibreOffice and Google Docs all honour
`w:pBdr`; none of them reliably honours a floating drawing imported from a .docx.

This is an engine change in `DocxWriter`, it touches every document that draws a rule, and it needs
the full-corpus gate before it lands. It is not in this commit.

## Ruled out

- Paragraph borders: the engine emits none, so this is not a border Google is ignoring.
- Table cell borders: no `<w:tbl>` in the document at all.
- A stray U+200B written by the engine: the .docx contains none. The one in the render is Google's
  anchor artefact, which is why it appears only in the documents that carry a drawing.

## What would prove this wrong

A document with `<w:drawing>` rules that passes both 05 and 32 in Google, or a document with `w:pBdr`
rules that fails them. Among the 50 verified so far, every 05+32 pair carries drawings.
