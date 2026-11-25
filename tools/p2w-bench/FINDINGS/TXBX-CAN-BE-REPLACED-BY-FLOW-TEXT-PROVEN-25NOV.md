# Two Google round-trips that settle how to fix the textbox problem

Engine untouched. Two hand-built .docx, uploaded, converted to a Google Doc and exported to PDF.

## Test 1 — does Google honour `<a:xfrm rot>` on an anchored shape?

One document, two identical shapes, same text. The first carries `rot="900000"` (15 degrees) on its
`<a:xfrm>`; the second carries no rotation attribute at all.

Result, read from Google's own PDF export:

    images on page: 2
    "ROTATED TEXT" appears in the text layer: NO

The rendered page shows the first shape's text **tilted 15 degrees** and the second **horizontal**.

So: **Google honours `a:xfrm rot`.** Rotation can be carried by the attribute instead of by
positioning every character by hand — which is what the engine does today, and why
`01_stamp_rotated_15deg_upright` carries 99 individually positioned characters and no `rot` at all.

But: **both shapes were rasterised anyway.** The rotation attribute does not save the text. A shape is
a shape.

## Test 2 — does flow text with indent + spacing survive as text, and land where asked?

One document, two runs of the same size:

    FLOW  a paragraph with <w:ind w:left="3000"/> and <w:spacing w:before="2400"/>
    BOX   an anchored shape at an absolute offset, holding the same text

Result, read from Google's own PDF export:

    images on page: 1
    FLOWTEXT   in text layer: YES   x = 206.7 pt
    BOXTEXT    in text layer: NO

And the x is not approximate. Left margin 1134 twips = 56.7 pt; indent 3000 twips = 150 pt;
56.7 + 150 = **206.7 pt**. Google placed it at **206.7 pt**.

So: **flow text keeps its characters AND lands exactly on the computed position.** A textbox trades
both away for the ability to overlap.

## What this settles

| problem | cause | fix | status |
|---|---|---|---|
| text turns into an image | text lives inside `<wps:txbx>` in an anchored shape | move it to flow text, position with `w:ind` + `w:spacing` | **proven** |
| white patches over content | the rasterised shape flattens onto white and covers what is under it | falls out of the same fix | **proven by construction** |
| stamp rotation wrong | rotation is baked into 99 per-character positions, no `rot` attribute | put `rot` on `<a:xfrm>` | **proven** |
| stamp pixelated | it is a raster, so it pixelates when zoomed | native resolution / 300+ dpi, or flow text where it can be text | not tested |

## What it does NOT settle

Whether every one of the 47 textbox documents can be expressed as flow text. A stamp must sit on top
of body text, and flow text cannot overlap — so a stamp whose position genuinely collides with body
content cannot be flow text. That is the one case where the shape has to stay, and there the fix is
`rot` for the angle and resolution for the pixels, not removal.

## Reproduce

    /scratch/work/rottest/rot-test.docx    -> Google Doc -> PDF
    /scratch/work/flowtest/flow-test.docx  -> Google Doc -> PDF

Both were built by hand in this session; the engine was not modified and was not involved.
