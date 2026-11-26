# Four Google round-trips that settle the textbox, rotation and resolution questions

Engine untouched. Every document below was hand-built, uploaded, converted to a Google Doc and exported
to PDF through Drive. All numbers are read out of Google's own export.

## Test 1 — does Google honour `<a:xfrm rot>`?

One document, two identical anchored shapes, same text. The first carries `rot="900000"` (15 degrees) on
its `<a:xfrm>`; the second carries no rotation attribute.

    images on page: 2
    "ROTATED TEXT" in the text layer: NO

The rendered page shows the first shape's text tilted 15 degrees and the second horizontal.

**Google honours `a:xfrm rot`.** Rotation can be carried by the attribute instead of by positioning every
character by hand — which is what the engine does today, and why `01_stamp_rotated_15deg_upright` carries
99 individually positioned characters and no `rot` at all.

But both shapes were rasterised anyway. The attribute fixes the angle, not the characters.

## Test 2 — does flow text survive as text, and land where asked?

One paragraph positioned by `w:ind w:left="3000"` and `w:spacing w:before="2400"`, and one anchored shape
holding the same text.

    images on page: 1
    FLOWTEXT   in text layer: YES   x = 206.7 pt
    BOXTEXT    in text layer: NO

And the x is not approximate: margin 1134 twips = 56.7 pt, indent 3000 twips = 150 pt, and
56.7 + 150 = **206.7 pt** — exactly where Google put it.

**Flow text keeps its characters AND lands on the computed position.** A textbox trades both away for the
ability to overlap.

## Test 3 — does Google re-sample an embedded image?

Two PNGs of the same text, both placed in a 2.00 inch box:

    96 dpi source   192 x 57 px
    300 dpi source  600 x 180 px

After the round-trip:

    image 0: 192x57 px    placed at 144.0 x 43.5 pt (2.00 inch)  =  96 dpi effective
    image 1: 600x180 px   placed at 144.0 x 43.5 pt (2.00 inch)  = 300 dpi effective

**Nothing is re-sampled.** A 300 dpi stamp stays 300 dpi after import, so zooming does not pixelate. Stamp
pixelation is a source choice, not a Google behaviour to work around.

## Test 4 — how many textboxes are there, and how big are they?

Measured on the 213 corpus documents, `word/document.xml` read directly:

    47 documents carry <w:txbxContent>     1007 text boxes in total

      1-2   (stamp-like)   18 documents      20 boxes
      3-10                 11 documents      51 boxes
      11-50                13 documents     382 boxes
      51+   (form-like)     5 documents     554 boxes

    behindDoc="1" present in: 47 of 47 documents

The distribution decides the fix. Twenty boxes across eighteen documents are stamps — one shape each, and
flow text plus `a:xfrm rot` can plausibly replace them. Nine hundred and eighty-seven boxes across
twenty-nine documents are form fields and column layouts scattered across the page, where flow text cannot
go: it cannot overlap and cannot sit at an arbitrary point without pushing everything after it down.

So: eighteen documents are fixable by removal, twenty-nine are not, and for those the fix has to be the
angle (proven) and the resolution (proven), not the removal.

## Why the regression gate does not catch any of this

`regress.py --check` compares check verdicts, not renders. Measured on the same day: 42 documents pass every
applicable check, 4 look 99% or better like their original, 10 at 95% or better, median SSIM 84.1. A document
can go from 41/42 to 41/42 while its entire text turns into a picture, and the gate prints PASS.

The gate is not wrong. It is answering the question it was given.

## Reproduce

    rot-test.docx   -> Google Doc -> PDF   test 1
    flow-test.docx  -> Google Doc -> PDF   test 2
    dpi-test.docx   -> Google Doc -> PDF   test 3
