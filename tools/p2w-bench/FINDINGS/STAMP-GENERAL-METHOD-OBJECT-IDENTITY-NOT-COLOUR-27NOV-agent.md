# The stamp method, stated generally

This is a tool. Every user brings different documents with different stamps - different colours, shapes,
opacities, rotations and positions. **A method that works on three sample documents and nothing else is
not a method.** Everything below is written to hold for any stamp, and nothing in it names a document.

The five mask variants recorded in the companion finding are all the same mistake in different clothes:
they decide what a pixel *looks like*. That decision cannot generalise, because what a stamp looks like
changes with every document. What does not change is that **the PDF knows which object each pixel came
from.** That is the only fact stable enough to build a tool on.

---

## The principle

**Separate by object identity, not by appearance.**

A rendered page is a bag of pixels and it has forgotten where they came from. A PDF has not. Every
drawing, every glyph run, every image is a distinct object with its own identity, and the page's content
stream records the order in which they are painted.

Two objects can paint the same pixel - a stamp over body text does exactly that - and the resulting pixel
is a blend that records **nothing** about how much of each contributed. No colour distance, saturation
floor, residual, ordering test or darkening test can recover that, because the information was never in
the image. This is not a tuning problem. It is an information problem.

So the method never asks "does this pixel look like stamp ink". It asks "**which object painted this
pixel**", and the answer is already recorded.

---

## The algorithm

### 1. Find the stamp's objects

A stamp is a cluster of vector objects - drawings and glyph runs - that is **not part of the body text
grid**. That is the one property every stamp shares, whatever it looks like:

- its strokes are not aligned to the document's baseline grid
- it is usually rotated, often enclosed by a closed path, frequently a colour no body text uses
- it is painted **after** the body text it covers

None of those is a colour test, and none depends on the stamp's appearance.

Locate it by the cluster, not by looking for a container to start from. The current flow begins at a
`wps:txbx` anchor and that is why it cannot enter documents whose stamp is a picture, a set of bare
shapes, or text with no border - the stamp is found in the **PDF** first, and the anchors are then
matched to it. An anchor belongs to the stamp when it overlaps the stamp's rect and the overlap is at
least half the area of the smaller of the two rectangles. That test is appearance-free and it works
whether the anchor is a textbox, a shape or a picture.

### 2. Render only those objects, onto a blank page

Create an empty page the size of the stamp's bounding box, draw **only the stamp's own objects** into it,
and render that at 600 dpi.

This is the step that makes the whole method work, and it works for one reason: **the body text is not on
that page.** No overlap, so no blend, so nothing to separate. The stamp comes out complete and alone by
construction - not by threshold, not by tolerance, and with no per-document tuning of any kind.

It is also colour-blind, which is what a tool needs:

| stamp | why it works |
|---|---|
| any colour, including black | no colour test is made |
| multi-colour | every object of the cluster is drawn |
| semi-transparent | the object's own alpha is preserved by the renderer |
| any shape, rotation, position | the objects carry their own geometry |
| a stamp that is already a raster image | the image object is drawn as it is |
| a stamp made only of glyphs, no border | glyph runs are objects too |

### 3. Place it as one anchored image

Emit the render as a single floating anchor, `relativeFrom="page"`, `posOffset` at the stamp's rect
corner, `wrapNone` so it never pushes text. This part is already proved: measured through a real Google
export at dx 0.0 to 0.7 pt on ten documents, with the alpha preserved (`smask` present in the export).

The image carries the stamp's own alpha, so a transparent interior stays transparent and the body text
behind it shows through exactly as it does in the source - which is faithful, and is also why the image
must not contain that text.

---

## Where the object-level render has to happen

`PyMuPDF` renders **pages**, not individual objects, so it cannot do step 2. The options:

- **PDFBox** - `PDFStreamEngine` with a custom `DrawObject` filter, or copy the relevant content-stream
  operators into a fresh page. Java, which is where the engine already lives.
- **MuPDF's own object API** - walk the page's display list and re-run only the chosen objects.
- **Copy the operator subset** - read the content stream, keep only the operators that paint the stamp's
  objects, write them to a new page, render that.

The third is the most portable and the least clever, which is usually the right trade. It also makes the
guarantee checkable: the new page contains a known subset of operators, so what it renders is known.

---

## The acceptance test, which is also general

For any document, not just these:

1. **Isolation** - render the page with the stamp's objects present and again with them absent; the
   difference must equal the stamp image. Any pixel that differs but is not in the image, or any pixel in
   the image that does not differ, is a failure. This is a proof, not a threshold.
2. **Completeness** - the image's ink bounding box must match the stamp's rect in the PDF to within 1 pt
   on every side.
3. **Position** - after a Google export, the stamp's ink must sit within 1 pt of where the source PDF has
   it.
4. **Nothing else** - the image must contain no pixel that is not attributable to a stamp object.

Test 1 is the one that matters and the one none of the five colour variants could ever pass, because they
were all trying to infer the difference instead of measuring it.

---

## Ruled out - all five measured, all five failed, do not retry

Colour distance with a saturation floor discarded pale lettering. Coverage alone let black body text
through at full alpha. The residual to the paper-to-ink line left a pale ghost. A small absolute
saturation floor cleaned two documents and not the third. Rejecting pixels darker than the pure ink
punched holes in the stamp's own letters - because rejecting foreign ink and deleting stamp ink are the
same operation when they share a pixel.

Every one of those is a heuristic on appearance. **None of them can generalise, because the appearance of
a stamp is exactly the thing that changes between users.** They are recorded so no run spends itself
rediscovering that.

---

## What is already proved and carries over

- the crop rect is the **union** of the stamp's drawings and its own text spans, padded by
  `(max stroke / 2) + 1 pt` - padding computed in **points**, never in pixels
- every anchor whose rect overlaps the stamp's rect belongs to it - textbox, shape or picture, all kinds,
  overlap >= half the smaller rect
- never redact: redaction deletes whatever else shares the rectangle
- emit RGBA, one floating anchor, `wrapNone`, 600 dpi
- position through a real Google export: dx 0.0 to 0.7 pt, alpha preserved

## What must not be claimed

That a stamp image is clean of foreign content until test 1 above passes on that document. On documents
where body text or rules cross the stamp, the current build is not clean, and no mask will make it so.

## The method built and measured, four documents

The general method above was implemented as a proof of concept in Python/PyMuPDF, replacing step 2's
object-level render with a reconstruction of the stamp's own objects onto a blank page. It is not the
final implementation - the engine should copy the operator subset - but it is enough to prove the
principle and to find what breaks.

**Result, measured through a real Google export against each source PDF:**

| document | ghost | holes | position | size | colour |
|---|---|---|---|---|---|
| 01 red 15 degree | none | none | dx +0.0 dy +0.2 | exact | exact |
| 02 green 15 degree | none | none | dx +0.2 dy +2.4 | -0.7, -3.4 | exact |
| 06 PAID | **none** (was ghosted) | none | **+2.2/+2.2 -> +0.2/+0.2** | **-4.6/-5.0 -> -0.7/-0.2** | **PAID too dark** |
| 07 QUALITY APPROVED | **none** | **none** (was holed) | **+0.0/-4.1 -> +0.0/+1.9** | -2.2 -> +3.1 | exact |

**The two documents that every colour mask failed on - 06 ghosted, 07 holed - are clean under object
reconstruction.** No ghost, no hole, because the body text is not on the page the stamp is drawn on.
That is the whole point of the method and it holds.

## Two things still wrong, and both are named precisely

### 1. Position and size are not exact - fix by not trusting the reconstruction

The reconstruction draws the objects approximately: line caps, joins and font metrics differ from the
PDF's own renderer, so the image's ink lands a few points off and a few points short. Measured: 07 came
out 3.1 pt taller than its source, 02 4.3 pt short.

**Do not correct these by tuning. Crop the rendered image to its own ink bounding box and place that
box at the stamp's rect with the stamp rect's exact size.** Then the ink lands on the stamp rect by
construction, whatever the reconstruction did:

    render the objects on a blank page
    find the ink bbox inside that render
    crop the image to that bbox
    place the cropped image at (stamp.x0, stamp.y0) with extent (stamp.width, stamp.height)

This is self-correcting and it is general - it assumes nothing about which objects were drawn or how
well. It removes reconstruction error from position and size entirely, leaving only colour to get right.

### 2. Colour saturation - the text's opacity is not in `get_text()`

`06`'s **PAID** comes out fully opaque when the source draws it at about 67 percent. `PyMuPDF` does not
report the alpha: `get_texttrace()` returns `alpha=None` for every span on that page, including PAID at
44 pt. The alpha lives in the content stream's `ExtGState`, which is not exposed per span.

**The opacity has to be measured from the render, not read from the API.** The stamp's ink colour is
known, so a pixel's coverage along the paper-to-ink line *is* the opacity it was drawn at:

    t = (255 - pixel) . (255 - ink) / |255 - ink|^2

For PAID that gives about 0.67. Apply it with `fill_opacity` when the text is drawn.

**A first attempt at this returned 1.0 for every span and was wrong.** The estimator took the 90th
percentile of `t` inside the span's bounding box, and PAID's box is close enough to the border that the
border's fully-opaque pixels dominated that percentile. **Use the median of the covered pixels, not a
high percentile**, so a mostly-opaque neighbour cannot outvote the text.

## What this proves and what it does not

**Proved:** separating by object identity removes foreign content completely, on the two documents where
five colour masks all failed. That was the open question and it is answered.

**Not proved:** that the reconstruction is pixel-exact. It is not, and it does not need to be - the
self-correcting placement absorbs the geometry error, and the measured opacity absorbs the colour error.
But neither of those corrections has been run end to end yet.

**The engine should still do the real thing** - copy the stamp's operators into a fresh page and render
that - rather than reconstructing from `get_drawings()` and `get_text()`. Reconstruction loses whatever
the API does not expose, and this work has now found two things it does not expose: the text's alpha,
and the exact stroke cap and join. Operator copying loses nothing.
