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

## Both corrections were built and both failed. Do not apply them blind.

The two corrections named above were implemented and measured through Google. Neither worked.

    06  offset +0.2,+0.2 -> +2.9,+2.9     size -0.7,-0.2 -> -5.5,-5.8     WORSE
    07  offset +0.0,+1.9 -> +0.0,+1.9     size +3.1 -> +3.1               unchanged

**06 got worse, not better** - the size deficit grew from 0.7 pt to 5.5 pt. And **07's numbers came back
identical to the run before it**, which is suspicious in itself: either the rebuilt file did not reach
Google, or the measurement read the same output twice. That has not been established.

**What is suspected, and is only a suspicion:** the self-correcting placement crops the render to its own
ink bounding box using a coverage threshold of 0.05. If that threshold clips the faint outer edge of a
thin stroke, the box comes out too small - and stretching a too-small box up to the stamp rect's size
magnifies the error instead of removing it. That would explain 06 going from 0.7 pt short to 5.5 pt short
while 07, whose strokes are heavier, did not move.

**What must happen before either correction is trusted:**

1. Verify the rebuilt file actually reaches Google and the export is new. 07 returning byte-identical
   measurements before and after is not credible on its own.
2. Measure the ink bounding box of the render against the stamp rect directly, in points, before any
   placement maths. If the box is short, the crop threshold is the cause and the answer is to lower it,
   not to stretch.
3. Only then re-run the placement.

**The honest position:** the method is proved - object identity removes foreign content where five colour
masks failed, on 06 and 07 both. **The geometry corrections are not proved and one of them made a
document worse.** Anyone picking this up should start from the render-vs-rect measurement, not from the
placement code.

## The geometry error is found, and it was never the threshold

The suspicion recorded above - that the crop threshold was clipping the edge - is **wrong**. The threshold
makes no difference at all: 0.05, 0.02 and 0.005 give the identical bounding box on both documents. The
error is somewhere else entirely and it is exact.

    document   stamp rect (SR)      rendered ink        error        stroke width
    06         147.62 x 114.13      152.64 x 119.16     +5.02, +5.03    4.89
    07         159.71 x  82.89      161.28 x  84.48     +1.57, +1.59    1.44

**The error equals the stroke width, on both.**

`get_drawings()` returns `rect` as the bounding box of the stroke's **centre path**, not of the ink. The
ink extends half the stroke width beyond the path on every side, so the true ink box is the path box
**plus the full stroke width** - half on each side.

Which means **the stamp rect used everywhere in this work was too small by one stroke width**, and every
size deficit measured today is that same error:

    -4.6, -5.0   on 06   (stroke 4.89)
    -3.4         on 02   (stroke 1.67)
    -2.2         on 07   (stroke 1.44)

**The fix is one line, and it belongs at the point where the stamp rect is built:**

    SR = union of drawing rects and stamp text bboxes
    SR = SR expanded by (max_stroke_width / 2) on every side      <-- the ink box, not the path box

Then place the image at that rect with that rect's size, and the geometry is right by construction. No
self-correcting placement, no crop-and-stretch, no threshold tuning - those were all attempts to repair a
rect that was wrong at the source.

**This also explains why the padding rule `(max stroke / 2) + 1 pt` helped but never made the size exact.**
That padding was applied to the *crop* so the render would not clip the border. It was never applied to
the *stamp rect* that the placement maths used. Two different numbers were needed and only one was
corrected.

**What to do first, before anything else in this file:** rebuild the stamp rect as the ink box, re-measure
one document, and check the size delta goes to zero. If it does, every geometry problem in this work was
this one line.

## The ink-box fix works. 06 is now within half a point.

Rebuilt the stamp rect as the ink box - path box expanded by half the stroke width on every side - and
measured again through Google.

**Local check first, before spending a Google export:** the render's ink bounding box against the new
rect came out within **0.09, 0.12, 0.02 and 0.15 pt** on 01, 02, 06 and 07, against errors of -1.2, -3.4,
-5.0 and -2.2 before. The line does what it was expected to do.

**Then through Google:**

    06  offset +0.5, +0.2   size -1.0, -0.5   ink  -7%    OK
        (was +2.9, +2.9, size -5.5, -5.8, ink +32%)

**06 is fixed** - position, size and ink all inside tolerance, and PAID's opacity measured at 0.55 and
applied, which is the semi-transparency the source actually has.

    07  offset +0.0, +1.9   size +0.0, +3.8   ink -52%   still wrong

### What is left on 07, and it is the opacity estimator again

The estimator returned **0.88** for both of 07's text spans, and 07's text is fully opaque in the source.
The span's bounding box includes background pixels, so the median of the covered pixels is dragged below
1.0 - and drawing fully-opaque text at 0.88 makes it lighter, which is the -52 percent ink.

**Clamp it:** if the median comes out above about 0.85, the text is opaque and the estimate is measuring
its own background. Use 1.0. The clamp is needed because the estimator cannot tell "text drawn at 88
percent" from "opaque text in a box that is 12 percent background", and the second is far more common.

### Where the stamp work now stands

    proved     object identity removes foreign content - 06 and 07 both clean of ghost and holes
    proved     the ink-box rect - local error under 0.15 pt on all four documents
    proved     measured opacity - 06's PAID at 0.55, applied, ink -7%
    fixed      06 end to end through Google: +0.5/+0.2, size -1.0/-0.5, ink -7%
    open       07: opacity over-estimated at 0.88 against a true 1.0; clamp and re-run
    open       02: font-metric drift, about 4 pt
    open       10, 12, 14: the three shapes the flow cannot enter
    open       the count of affected documents

## The clamp works on colour. The geometry still does not, and it is the font.

The opacity clamp - treat anything above 0.85 as opaque - did what it was meant to:

    07  ink -52%  ->  -17%      opacity 0.88 -> 1.00

So colour is now in hand: 06's PAID at its true 0.55, 07's text at its true 1.0.

**Geometry did not move, and the same two numbers keep appearing:**

    07  offset +0.0, +1.9    size +0.0, +3.8     unchanged by the clamp, unchanged by the ink box
    02  offset +0.7, +4.6    size -1.2, -4.6     unchanged by the ink box

**The cause is the font, not the rect.** Both documents' stamp text is drawn with `Liberation Serif Bold`
substituted for the PDF's own subset font. The substitute has different ascent and descent, so the
rendered text is **shorter** than the text bounding box the PDF reports - by about 4 pt at 15 pt type.

The image is stretched to the stamp rect's size, but its own ink does not fill that box, because the text
inside it is too short. So the ink measures short by exactly that font difference, and the top of the
stamp sits low because the ascent is smaller.

**Cropping the image to its own ink and stretching that to the rect does not fix it** - that was tried, and
02 came back at -4.6 again. Cropping cannot invent the missing ascent; it can only redistribute what is
there.

### What actually fixes it

**Use the PDF's own font, not a substitute.** `page.get_fonts()` lists the embedded fonts with their xrefs;
`doc.extract_font(xref)` returns the bytes. Embedding the stamp's real font removes the metric difference
at its source, and then the text sits in its own bounding box and the geometry follows.

**This is the same conclusion as the operator-copying note above, arriving from a different direction:**
reconstruction loses what the API does not hand over, and the font is one more thing it does not hand
over by default. Copying the operators loses nothing - not the alpha, not the cap and join, and not the
font metrics either.

### Where it stands

    fixed      06 end to end: +0.5/+0.2, size -1.0/-0.5, ink -7%, PAID at its true 0.55
    colour     07 at its true opacity, ink -52% -> -17%
    open       07 and 02 geometry, about 4 pt, caused by font substitution
    open       02 needs the embedded font; both need the operator-copy path
    open       10, 12, 14
    open       the count

## The reconstruction is exact to 0.15 pt. The error is in the placement, and 06 proves it can work.

Two suspicions were tested and both were wrong, which is worth recording so neither is chased again.

**Suspicion 1 - the substituted font's metrics cause the shortfall.** Measured by rendering the same text
with the system `LiberationSerif-Bold` and with the PDF's own embedded subset, then comparing against the
span bbox the PDF reports:

    02  system font 137.01 x 16.61   embedded subset 129.56 x 20.43   PDF reports 136.64 x 51.50
    07  system font 120.19 x 14.39   embedded subset 112.48 x 17.71   PDF reports 120.55 x 39.06

The system font is **closer** to the PDF's width than the embedded subset is. Embedding the PDF's font
would make the fit worse, not better. **The font is not the cause.**

**Suspicion 2 - the rotated text's axis-aligned bbox inflates the stamp rect.** The reported bbox height
is 51.50 pt for 15 pt text, which looked like the answer. Measured against a rect built from the drawings
alone:

    01  with text bbox 206.0 x 104.7   drawings only 207.5 x 106.2
    02  with text bbox 162.9 x  95.7   drawings only 164.6 x  97.3
    06  with text bbox 147.6 x 114.1   drawings only 152.5 x 119.0
    07  with text bbox 159.7 x  82.9   drawings only 161.2 x  84.3

The border already encloses the text on all four, so the text bbox changes nothing. **Also not the cause.**

### What the measurements do say

**The reconstruction itself is accurate to 0.15 pt on all four documents**, once the rect is the ink box:

    rendered ink vs ink box:  +0.09  +0.07  +0.01  +0.12 pt

And yet through Google, 06 lands at +0.5/+0.2 with size -1.0/-0.5 while 02 sits at +0.7/+4.6 and 07 at
+0.0/+1.9 with size +3.8.

**So the image is right and the placement is not, for 02 and 07 but not for 06.** That is the shape of the
remaining problem and it is the next thing to measure: compare the anchor's `posOffset` and `extent` in
the .docx against the ink box in points, for 06 (which works) and 02 and 07 (which do not), and find what
differs. It is a two-minute comparison and it has not been done.

**Do not chase the font and do not chase the rotated bbox.** Both were measured and both are innocent.

## Found it: the placement was always right. The measurement was wrong.

The comparison that was supposed to take two minutes, did. The .docx anchor is **exactly** the ink box on
all three documents:

    06  ink box 131.52, 332.39  152.51 x 119.02    docx anchor 131.52, 332.39  152.51 x 119.02
    02  ink box 144.27, 455.34  164.57 x  97.32    docx anchor 144.27, 455.34  164.57 x  97.32
    07  ink box 235.49, 261.63  161.16 x  84.33    docx anchor 235.49, 261.63  161.16 x  84.33

So the placement code was never wrong. The error was in **how the result was measured.**

The measurement finds the stamp by colour distance with a tolerance of 120. On 02 and 07 that tolerance
also catches neighbouring ink of a similar colour, and the bounding box jumps:

    02   tolerance  60: 164.4 x 97.2      tolerance 120: 180.5 x 110.6
    07   tolerance  60: 161.0 x 84.0      tolerance 120: 193.2 x 108.5

**Every "+4.6" and "+3.8" reported today was the measurement window growing, not the stamp moving.**

### Measured at tolerance 60, where the box stops growing

    01  offset +0.0, +0.0   size -0.2, +0.0   ink  -9%    ok
    02  offset +0.2, +0.2   size -0.7, -0.2   ink -10%    ok
    06  offset +0.5, +0.2   size -1.0, -0.5   ink  -5%    ok
    07  offset +0.2, +0.2   size -0.2, -0.5   ink +69%    position and size ok, ink not

**Four documents, position and size inside 1 pt on every one.** 01 is exact at +0.0, +0.0.

### 07's ink figure is also a measurement artefact, not a defect

At tolerance 60 only pixels very close to the pure colour are counted. 07's text is semi-transparent, so
**the original's own text is not counted while the rebuilt opaque text is** - which is why the figure reads
+69 percent. The real opacity sits between the 0.88 the estimator produced (which gave -52 percent) and the
1.0 the clamp forced. Neither figure is a defect in the document; both are the metric failing on
semi-transparent ink.

**The lesson, and it is the fifth time today:** a number is only as good as the region and the threshold it
was taken with. Every geometry "failure" in this work was the stamp being measured with a window that
included things which were not the stamp.

### Where it stands now

    fixed      all four documents: position and size inside 1 pt through a real Google export
    fixed      06: PAID at its true opacity 0.55, ink -5%
    proved     object identity removes foreign content - no ghost, no holes on any of the four
    open       07's opacity: between 0.88 and 1.0, needs an estimator that works on semi-transparent ink
    open       10, 12, 14: the three shapes the flow cannot enter
    open       the count of affected documents

## The opacity question settled, and the ink metric is the last thing that is wrong

Measured peak coverage inside the ink box on all four:

    document                         p50   p90   p99   max
    01_stamp_rotated_15deg_upright  0.93  1.00  1.00  1.00
    02_stamp_rotated_15deg_upleft   0.96  1.00  1.00  1.00
    06_rect_paid_stamp_red_transparent 1.00 1.00 1.00  1.00
    07_stamp_over_table             0.91  1.00  1.00  1.00

**Every stamp's border is fully opaque, and so is every stamp's text.** The medians below 1.00 are the
background inside the box dragging them down, not semi-transparent ink. So:

- the **clamp to 1.0 was correct** for 07, and the 0.88 the estimator produced was its own background
- **06's PAID at 0.55 is a different case** - that measurement was taken inside the PAID span alone, where
  the background fraction is small and the median is trustworthy. It is genuinely semi-transparent.

The rule that separates them: **measure inside the glyphs, not inside the span's bounding box.** A span box
is mostly background; a glyph's interior is not.

### The last thing that is wrong is the ink metric, not the documents

At tolerance 60, 07 reads +69 percent ink. That is not the document - at that tolerance only pixels very
close to the pure colour are counted, so **semi-transparent or antialiased pixels are excluded from the
count**. The original's own edges and the rebuilt image's edges are antialiased differently, and the count
swings wildly on a 12 percent difference in edge pixels.

**Count coverage, not pixels.** Sum the alpha-weighted coverage over the window instead of counting pixels
above a threshold. That is opacity-independent and edge-independent, and it is the only version of this
metric that can be trusted across documents.

### Final state of the four documents

    position and size   inside 1 pt on all four through a real Google export (01 exact at +0.0, +0.0)
    isolation           no ghost, no holes on any of the four
    opacity             06's PAID at its true 0.55; every other stamp text opaque at 1.0
    ink metric          still threshold-based and still unreliable - switch to coverage sum
    open                10, 12, 14: the three shapes the flow cannot enter
    open                the count of affected documents

## The three documents the flow cannot enter, and the one rule that opens all three

Measured what is actually on those pages:

    10_stamp_as_image            stamp (0.85, 0.36, 0.05)   1 drawing, 1 text span
    12_stamp_across_page_break   stamp (0.45, 0.03, 0.10)   2 drawings and 2-3 spans per page
    14_stamp_chars_positioned_td stamp drawing (0.06, 0.12, 0.32)
                                 stamp text    (0.05, 0.15, 0.55)   <- two different blues

    body text on all three: (0.35, 0.35, 0.35), appearing 5 to 7 times

**The pattern is the same on all three: the stamp's colour is rare, the body text's colour is common.**
The stamp appears one to three times per page; the body text appears five to seven.

So the locator does not need a container to start from, and does not need to guess which colour is the
stamp's. **The stamp's ink is every colour on the page that is rare and is not the body text colour.**

### And 14 explains why one colour was never enough

14's border is `(0.06,0.12,0.32)` and its text is `(0.05,0.15,0.55)`. Those are **two different blues**, a
Euclidean distance of 0.23 apart. Rule 1 takes the single most common drawing colour near the anchor -
correctly, the border - and then matches text spans within 0.02 per channel. **0.23 is not within 0.02, so
the text is never found, and the stamp looks like a border with nothing in it.**

**A stamp's ink is a set, not a colour.** Rules 1 and 4 both assume one colour and both break on any stamp
that draws its border and its lettering in different shades - which 14 does, and which any two-tone stamp
will.

    stamp inks = every colour C on the page such that
                   count(C) is small, and
                   C is not the body text colour

Everything downstream then runs per ink colour instead of for one: the crop is the union of the objects
drawn in any of them, the mask accepts a pixel matching any of them, and the alpha comes from whichever
one it is nearest.

### What this does not settle

- 12 spans a **page break**, so its stamp is split across two pages. That is a placement question, not a
  locator one, and it has not been looked at.
- 10's stamp is **already an image** - `1 image` on the page. Nothing needs rebuilding; the existing image
  needs to become the anchored stamp. Also not looked at.
- The rarity threshold is a judgement, not a measurement. It needs a number picked from the corpus, not
  guessed here.

**What is settled: all three are enterable, and the reason 14 was never enterable is that its ink is two
colours and the rules were written for one.**

## The rarity rule is disproved. Measured across sixteen documents, it does not separate anything.

The section above proposed that the stamp's ink is every colour that is rare and is not the body text
colour. That was a guess dressed as a rule. It was then measured on every stamp document in the corpus, and
it fails.

    stamp colour counts:  2 2 2 3 4 4 4 4 4 4 4 4 5 5 5 5 5 5
    body  colour counts:  4 4 5 5 5 6 7 8 8 8 8 9 11 16 18 18 32 32

**The two ranges overlap completely.** A stamp colour can appear five times; a body colour can appear four.
No threshold drawn anywhere separates them.

**Two documents break the rule outright:**

    15_stamp_on_scanned_page   body colour (0.75,0.05,0.05) x4   - the same as the stamp
    43_red_stamp_over_black_text  body colour (0.85,0.08,0.08) x5 - the same as the stamp

On those, the stamp's colour **is** the most common colour on the page. "Not the body text colour" cannot
identify it, because it is the body text colour.

**Saturation does not rescue it either.** 312's body text is `(0.25,0.25,0.55)`, saturation 0.30, against a
stamp at `(0.48,0.12,0.12)`, saturation 0.36. Six hundredths apart. Any threshold between them would be a
number fitted to one document.

### What this means

**Colour cannot locate the stamp. Not by rarity, not by saturation, not by hue.** Sixteen documents is
enough to say so with confidence, and it is the same conclusion this whole file keeps arriving at from
different directions: **appearance does not identify the stamp, because every stamp's appearance is
different and some stamps look exactly like the text around them.**

### The locator has to be geometric

What actually distinguishes a stamp on every one of the sixteen:

- it is **rotated**, or its glyphs sit off the document's baseline grid
- it **overlaps** body text rather than flowing with it
- it is painted **after** the text it covers

None of those is a colour. The locator should be: find the objects that are rotated or off-grid, and take
the cluster. That has not been built and it has not been measured - it is the next thing to try, and unlike
the rarity rule it is testable against the same sixteen documents.

**Do not build on the rarity rule. It was measured and it is wrong.**

## The geometric locator, measured: rotated text finds the stamp on fourteen of sixteen

Colour was disproved. Geometry was then measured on the same sixteen documents, and it works.

Every line of text carries a direction vector. Body text is `(1, 0)`. A stamp's text almost never is.
Counting spans whose direction is not `(1, 0)`:

    01  2      02  2      03  3      04  2      06  1      07  2
    08  4      09  2      11  3      13  4      14  2      15  2
    312 26     43  3

    **10  0**    stamp is already an image, so there is no stamp text to find
    **12  0**    stamp is shapes only, so there is no stamp text to find

**Fourteen of sixteen, from one signal that makes no assumption about colour, font, shape or position.**

The directions are also informative on their own: `(0.97,-0.26)` is 15 degrees up, `(0.97,0.26)` is 15
degrees down, `(0,-1)` is 90 degrees, `(-1,0)` is 180, and 312's seal gives `(-0.34,-0.94)` and friends,
which is per-letter placement around a circle.

### The rule, in order

1. **Rotated text spans** - if any exist, they are the stamp. This covers fourteen of sixteen.
2. **No rotated text, but the page carries an image** - the stamp is that image. Nothing to rebuild; it
   needs anchoring, not reconstructing. This is 10.
3. **No rotated text and no image** - the stamp is drawn as bare shapes. Locate it by drawings whose
   bounding box does not align to any text line's baseline. This is 12, and it is the only document in the
   sixteen that needs this branch.

**Branch 2 is worth noticing on its own:** if the stamp is already an image in the source PDF, the whole
reconstruction problem disappears. Copy the image, anchor it, done - no alpha to measure, no font to
substitute, no crop to get wrong. **Check for it first, before any of the hard work.**

### What remains unbuilt

The three branches are measured, not implemented. Branch 1 is straightforward. Branch 2 is easier than
what has been built so far. Branch 3 is the only one with real work in it, and it affects one document of
sixteen - which is the right thing to know before spending a day on it.

## The three-branch locator built and run: fifteen of sixteen

The rule from the section above was implemented and run across the corpus.

    branch 1  rotated text spans        14 documents
    branch 2  the page carries an image  1 document  (10_stamp_as_image)
    branch 3  bare shapes                1 document  (12_stamp_across_page_break)

**Fifteen of sixteen, and only one needs the branch that has real work in it.**

The stamp rects it produces look right: 03's is 35.2 x 105.4 pt, narrow and tall as a 90-degree stamp
should be; 14's is 216.2 x 65.2 pt with ink `(0.05,0.15,0.55)`, which is the document that was never
reachable before and now is.

### One caveat, measured and not glossed

**312 comes back with ink `(0.25,0.25,0.55)`, which is its body text colour, not its stamp's.** Its stamp is
`(0.48,0.12,0.12)`. 312's seal is drawn as 26 individually rotated letters, and some of the spans that carry
a non-`(1,0)` direction belong to something other than the seal.

So the branch-1 rule needs one more condition, and 312 is the document that proves it: **a rotated span is
part of the stamp only if it is not in the body text's colour, or only if it clusters spatially with the
other rotated spans.** 312's 26 spans are spread around a circle; the body text spans that got caught are
somewhere else on the page.

**Until that condition is added, 312 is located wrongly and everything downstream of it will be wrong too.**
Fourteen of fifteen are clean; 312 is the exception and it is known.

### What is now settled about locating a stamp

- **Not by colour.** Measured and disproved on all sixteen.
- **Not by container.** Three of sixteen have no `wps:txbx` anchor at all.
- **By geometry.** Rotated text finds fourteen; an existing image finds one more; bare shapes are the last
  one and affect a single document.

That is a locator that holds for a tool rather than for a sample, which is what was asked for. It needs the
312 condition and it needs implementing in the engine, but the question of *how a stamp is found* is
answered.

## The 312 caveat resolved, and it was my measurement that was wrong again

Spatial clustering was added - join rotated spans whose gap is under 30 pt - and it changed nothing on 312.
All 26 of its spans are already within 30 pt of each other, because a circular seal puts every letter close
to its neighbours. The clustering is harmless but it is not the answer.

**The answer came from looking at what those 26 spans actually are.** Their colour is `(0.25,0.25,0.55)`.
Earlier in this file that same colour was recorded as 312's **body text** colour, appearing 32 times, and the
stamp was recorded as `(0.48,0.12,0.12)`.

**Both of those readings were wrong, and the reason is arithmetic:** the count of 32 for `(0.25,0.25,0.55)`
includes **the seal's own 26 letters**. It is not the body text colour at all - it is the seal's lettering
colour, plus a handful of body spans that happen to share it. And `(0.48,0.12,0.12)` is the seal's ring.

**312's seal is two colours: blue lettering and a dark red ring. Both are the stamp.** The locator was right
and the ink set was too narrow, because it was taken from the rotated spans alone and the ring is a drawing,
not a span.

### The correction

**After the stamp rect is located, its ink is every colour of every drawing and every text span inside that
rect** - not the colours of the rotated spans that found it. The rotated spans locate the stamp; they do not
define it.

That is one line and it fixes 312 without any special case. It also makes the two-tone problem in 14 fall
out for free, which was previously going to need its own rule.

### And the lesson, which is the same one as five times before

**A count of 32 was read as "the body text colour" when 26 of those 32 were the stamp.** The measurement
was of the right page and the right colour and it still described the wrong thing, because it did not ask
*which objects* the colour belonged to. **Counting colours cannot answer a question about objects.**

### Locator, final state

    branch 1  rotated text spans        14 documents, locates the rect correctly
    branch 2  the page carries an image  1 document
    branch 3  bare shapes                1 document, not built
    ink set   every colour inside the located rect, after locating

Fifteen of sixteen, with 312 now correct rather than excepted.

## Branch 3 built: document 12, and it is a stamp split across a page boundary

12 was the last document with no rotated text and no image. Its drawings on both pages:

    page 0   (0.75,0.75,0.75) w0.50  line     56.0,  52.0  483.3 x   0.0
             (0.75,0.75,0.75) w0.50  line     56.0, 793.9  483.3 x   0.0
             (0.45,0.03,0.10) w1.78  rect    300.0, 749.6  147.6 x  80.8
             (0.45,0.03,0.10) w0.60  rect    303.0, 752.6  141.6 x  74.8

    page 1   (0.75,0.75,0.75) w0.50  line     56.0,  52.0  483.3 x   0.0
             (0.35,0.35,0.35) w0.60  line     56.0, 430.0  180.0 x   0.0
             (0.35,0.35,0.35) w0.60  line    316.0, 430.0  180.0 x   0.0
             (0.75,0.75,0.75) w0.50  line     56.0, 793.9  483.3 x   0.0
             (0.45,0.03,0.10) w1.78  rect    300.0, -16.4  147.6 x  80.8
             (0.45,0.03,0.10) w0.60  rect    303.0, -13.4  141.6 x  74.8

**Two nested rectangles in the same colour, on both pages, at the same x and the same size.** The only
difference is y: 749.6 on page 0 and **-16.4 on page 1**. Negative, above the page top.

**So 12's stamp is not "across a page break" in the sense of being duplicated. It is one stamp drawn at a
position that falls partly off the bottom of page 0 and partly off the top of page 1**, and each page clips
its half. That is why the document was built and why it is hard: there is no page on which the whole stamp
exists.

### The branch-3 rule

**A stamp drawn as bare shapes is a closed path whose rect is tall and which does not align to any single
text baseline.** Measured against 12's page:

- the horizontal rules are `line` items with **height 0** - excluded by the height test
- the stamp is `rect` items at **80.8 pt tall** - kept
- none of the six align to a text baseline, so the baseline test alone would have kept the rules too

**Both conditions are needed:** closed path **and** height above a floor. Height 0 kills the rules; closed
path kills anything drawn as an open stroke.

### What 12 still needs, and it is not a locator problem

The stamp exists on neither page in full. Rendering it means **stitching the two halves across the page
boundary** - take page 0's rect at y 749.6 to 830.4, page 1's at y -16.4 to 64.4, and reconstruct the
80.8 pt tall stamp from two clips. That is a different kind of work from anything else in this file and it
affects exactly one document.

**Branch 3 locates 12 correctly. It does not solve 12.** Saying otherwise would be the same mistake as
everything else recorded above.

### Locator, complete

    branch 1  rotated text spans         14 documents
    branch 2  the page carries an image   1 document
    branch 3  closed tall path            1 document  (12, located but not renderable)
    ink set   every colour inside the located rect, taken after locating

**Sixteen of sixteen located. Fifteen of sixteen renderable.**

## The coverage metric: much better than pixel counting, and still not measuring the stamp

Pixel counting at a colour tolerance swung between -52 and +69 percent on the same documents depending on
where the tolerance was set. Summing alpha-weighted coverage instead gives:

    document                           coverage orig   coverage export   delta
    01_stamp_rotated_15deg_upright         50847            52776         +3.8%
    02_stamp_rotated_15deg_upleft          46190            52659        +14.0%
    06_rect_paid_stamp_red_transparent     76762            78469         +2.2%
    07_stamp_over_table                    50476            63021        +24.9%

**Stable, and it no longer cares about antialiasing or about the stamp's opacity.** 07's 69 percent swing
becomes 25. That is the metric working as intended.

### But every one is positive, and that is a real signal

All four read **higher** in the export than in the source, between 2 and 25 percent. Two explanations, and
the second is the likely one:

1. the reconstruction draws slightly heavier than the source - possible, since it redraws lines with a
   chosen cap and redraws text with a substitute font
2. **the measurement window still contains body text, and body text registers as coverage**

The second is more likely and it is checkable by arithmetic. The coverage of a pixel is its projection onto
the paper-to-ink line:

    t = (255 - pixel) . (255 - ink) / |255 - ink|^2

Grey body text at `(0.35,0.35,0.35)` against a green stamp at `(0.05,0.42,0.18)` gives a **non-zero t**,
because grey is not perpendicular to that line. So body text inside the window counts as stamp coverage, and
if the export renders that text a little differently from the source, the delta moves - which is exactly the
2 to 25 percent spread seen.

**So the metric is better but it is still not measuring the stamp.** It is measuring "stamp ink plus whatever
else lies along the same colour direction in this window", and that is the isolation problem wearing a
different hat.

### What the honest metric would be

**Coverage summed over pixels that belong to the stamp's own objects** - which means the metric depends on
the same object-level separation the method is built on. The measurement cannot be fixed before the
separation is, because it is asking the same question.

**Until then: use coverage sum rather than pixel count, treat anything under about 25 percent as "within the
measurement's own noise", and do not report an ink figure as a document defect without checking whether the
window contained body text.**

### Where this leaves the whole file

    solved      the method (object identity, not colour)
    solved      the stamp rect (the ink box, not the stroke's centre path)
    solved      the locator (rotated text, image, closed tall path) - 16 of 16
    solved      opacity (measure inside glyphs; 06's PAID is 0.55, everything else 1.0)
    measured    position and size inside 1 pt on all four test documents through a real Google export
    measured    five colour-mask variants, all failed, all recorded so they are not retried
    open        12's stitching across a page boundary
    open        the ink metric, which needs the same object separation as everything else
    open        the count of affected documents

## The count, and the locator has false positives. Do not quote 52.

The three-branch locator was run across all 213 documents:

    branch 1  rotated text spans   31 documents
    branch 2  the page has an image 12 documents
    branch 3  a closed tall path     9 documents
    none                           161 documents

**52 is not the number of documents with a stamp, and quoting it would be wrong.** Reading the lists shows
what the branches actually catch:

    branch 1 includes  table-with-rotated-header      11 rotated spans
                      60_page_border                  49 rotated spans
                      one-page-rotated-180-degrees    61 rotated spans
                      417_rotate180_and_mirrored       4 rotated spans
                      411_nested_xobject_transforms    2 rotated spans

    branch 2 includes  300_prescription_rx, 70_magazine_drop_cap_photo_caption,
                       407_id_card_front_back, 361_product_catalogue_grid ...
                       - photographs and logos, not stamps

    branch 3 includes  45_coloured_callout_box, 55_sidebar_box_beside_body,
                       51_two_cm_margins, 80_gstin_pan_cin_ifsc_table ...
                       - callout boxes and table borders, not stamps

**Rotated text is not a stamp. An image is not a stamp. A tall rectangle is not a stamp.** The branches find
the *candidate* region correctly - every one of the sixteen known stamp documents is inside them - but they
also find rotated tables, page borders, photographs and callout boxes.

**The corpus has 16 documents with a stamp. It has 52 with a rotated object, an image, or a tall box.** The
difference is the discrimination the locator does not yet make.

### What would separate a stamp from the other three

Not colour - disproved. Not rarity - disproved. What is left, and it is untested:

- a stamp **overlaps body text** rather than sitting in its own space. A rotated table header sits above its
  table; a callout box sits in the margin; a photograph has its own column. A stamp is laid *over* the text
  it marks.
- a stamp's rotated spans are **few and short** - a few words - where a rotated table header or a 180-degree
  page has many and long ones. 60_page_border gives 49 spans, one-page-rotated-180-degrees gives 61;
  the stamp documents give 1 to 4, with 312's seal at 26 and 05's curved seal at 69 as the two exceptions.

**The overlap test is the more promising of the two**, and it is the one the whole method already depends on:
the stamp is the thing painted over other content.

### So the honest count

**16 documents in the corpus carry a stamp.** That is measured - they were identified individually. **How many
of the other 197 might also carry one that the locator would miss is not known**, and the 161 "none" figure is
only as good as the branches are, which is to say it is a lower bound on nothing and an upper bound on
nothing.

**Do not report 52. Report 16, and report that discrimination is the open problem.**

## The overlap test fails too. Three discriminators tested, three failed.

The section above proposed that a stamp overlaps body text where a rotated table header, a callout box or a
photograph does not. Measured on the corpus - counting flat body spans that a rotated cluster overlaps by at
least a quarter of their area:

    STAMPS   7 of 15 have any overlap     values: 0 0 0 0 0 0 0 0 1 1 1 2 3 4 4
    OTHERS   5 of 16 have any overlap     values: 0 0 0 0 0 0 0 0 0 0 0 3 3 3 3 4

**The two distributions are indistinguishable, and the direction is wrong.** Eight of fifteen stamps overlap
**nothing** - they sit in clear space. Five of the sixteen non-stamps overlap three or four body spans.

**"A stamp is laid over the text it marks" is not true in this corpus.** It is a thing stamps *can* do, not a
thing they *do*.

### Three hypotheses, three measurements, three failures

    1  colour - the stamp's colour is rare and not the body's    ranges overlap completely; two documents
                                                                have the stamp colour AS the body colour
    2  rarity alone                                             same measurement, same failure
    3  overlap - the stamp sits over body text                   indistinguishable from non-stamps, and
                                                                eight of fifteen stamps overlap nothing

**All three were plausible. All three were measured. All three are dead.** They are recorded here so that
none of them is proposed again by anyone, including me.

### What this actually means for the count

**There is no automatic rule in this file that separates a stamp from rotated table headers, page borders,
photographs and callout boxes.** Every candidate has been tested and failed.

So the honest statement about the corpus is:

- **16 documents carry a stamp** - established by looking at each one individually, not by a rule
- **the locator finds 52 candidates** and cannot rank them
- **whether the other 197 documents contain stamps that no branch catches is unknown**

**Anyone reporting a stamp count from this locator would be reporting the count of rotated content, not the
count of stamps.** That is the state of it, and the file says so rather than putting a number on it.

### The one thing not tried

A stamp is **a picture of an object** - it has a closed border with something inside it, drawn as a unit. A
rotated table header is a row of glyphs with no container; a page border is four lines with nothing in them;
a callout box has a border but its content is in the normal flow.

**The test would be: a closed path that fully contains text or shapes that are not part of the page's flow.**
That is a containment question rather than an overlap one, and containment is not what was measured above -
what was measured was whether the stamp's bounding box covers body text, which is a different thing.

It is untested. It is the fourth hypothesis and there is no reason yet to believe it more than the first
three.
