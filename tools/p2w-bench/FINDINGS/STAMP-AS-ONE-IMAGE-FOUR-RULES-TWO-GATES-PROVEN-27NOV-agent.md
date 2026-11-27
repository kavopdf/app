# A stamp as one image: four rules, two gates, and the position proved in Google

The user reported two things: a stamp's outline and the text inside it do not line up, and some stamps
are editable in the .docx while others are not. Then: **a stamp must never bring anything else with it,
whether that is text or anything else.**

This file is the whole of what has been proved, on four structurally different stamps, and the two
things that are still open. Nothing here is an estimate.

## The stamps this was proved on

    01_stamp_rotated_15deg_upright    red      (0.75,0.05,0.05)   15 deg,   rectangular
    02_stamp_rotated_15deg_upleft     green    (0.05,0.42,0.18)   15 deg,   rectangular
    03_stamp_vertical_90deg           blue     (0.05,0.15,0.55)   vertical, rectangular
    312_affidavit_stamp_paper         navy     (0.25,0.25,0.55)   circular notary seal, curved text

Eleven stamp documents were measured for ink colour and all eleven are coloured; none is black.

## Rule 1 - what the stamp's ink colour is

The most common non-black colour among the drawings inside the anchor's neighbourhood.

Verified on 11 documents: red, green, blue, dark red and a desaturated navy all resolved correctly.
A colour-specific rule ("it is red") does not generalise and was not used.

## Rule 2 - what to crop

**The union of the drawings carrying that colour, NOT the anchor's `wp:extent`.**

Measured: on `312_affidavit_stamp_paper` the anchor extent is 10.0 x 8.6 pt while the stamp is
76 x 76 pt - the anchor is eight times too small, and cropping to it produced a fragment. On
`03_stamp_vertical_90deg` the anchor is 108 pt wide while the stamp is 55 pt. On `01` and `02` the
two happen to agree, which is why an earlier attempt looked correct.

## Rule 3 - pad the crop

**Pad every side by (max stroke width / 2) + 1 pt.**

The union of the drawings is the stroke's centre line; half the stroke lies outside it. Measured:
0.6 to 0.83 pt per stamp, which is 2.5 to 3.5 pixels at 300 DPI. Without the padding the border is
clipped - visible on the circular seal, where the outer circle was cut at top and bottom.

## Rule 4 - the mask

**Keep a pixel when its colour distance to the stamp ink is under 160 AND its saturation is at least
max(25, target_saturation x 0.45). Everything else becomes white.**

The saturation term is not decoration. Without it `02_stamp_rotated_15deg_upleft` carried body text
into the image ("Total quantity: 72 Nos", "d condition and received in order Subject to B") because
dark text is within colour distance of the stamp. Grey text has saturation 0; the stamp does not.

## The two gates - the guarantee that nothing else comes along

Colour alone is a heuristic: text that happens to be the stamp's colour would pass it. So a second,
independent gate:

**Geometry.** Stamp ink may exist only inside the bounding boxes of the stamp's own drawings plus the
text spans whose colour is the stamp's colour. Every pixel outside that footprint is forced white.

Measured foreign ink removed by the geometry gate on the four stamps: 553, 748, 1456 and 100 pixels.
That number is the point - it is how much foreign ink was in the region and is now excluded. It is
checkable, not a claim.

After both gates the image contains the stamp's border and the stamp's text and nothing else.

## Emission, and the position proved in Google

The image goes in as a **floating anchor**, `relativeFrom="page"`, `posOffset` equal to the crop
rect's corner, `wrapNone` so it does not push text, at 300 DPI.

A hand-built .docx with exactly that anchor was uploaded to Drive, converted to a Google Doc and
exported. Producer: `Skia/PDF m160 Google Docs Renderer`. Result:

    stamp ink in the Google export : x=163.2..370.1   y=434.9..540.5 pt
    placed at                      : x=162.5, 434.3   size 209.5 x 108.2 pt
    offset                         : dx=+0.7  dy=+0.6 pt
    images in the export           : 1

**Under one point, on a page 842 pt tall. Google keeps the stamp as a single image and puts it where
the PDF has it.** The size reads 206.9 x 105.6 against 209.5 x 108.2 because the ink bounding box is
inset by the padding; the two offsets agree with that inset, so this is consistent, not a discrepancy.

## What is proved about the editable / not-editable split

`stamp03.docx` and its Google export `stamp03-gdoc.pdf` are a matched pair - five body-text probes
match exactly. In that export:

    body text : present, extractable
    stamp text: VERIFIED, AUDIT, INTERNAL, 31-03-2026 all absent
    images    : 22 on page 1, against 0 in the source PDF

So a textbox stamp reaches Google as a picture. That is one document, proved end to end.

Four attempts to classify the rest locally - by counting `wps:txbx`, by stamp-like words, by whether
stamp words appear inside a textbox, and by comparing exports of files that were not a matched pair -
were all wrong. **There is no local method that answers this. The only reliable measure is to export a
document to Google and check whether the stamp words are extractable.**

## What is NOT proved, and must not be claimed

1. **How many documents are affected.** 213 documents carry 1007 textbox anchors and only 23 of those
   anchors carry a stamp-like word, so the population is small - but no count is given here because
   no count has been measured. It needs one export per stamp document.
2. **A black stamp.** All 11 stamp documents are coloured. A pure black stamp has saturation 0, so
   rule 4 would keep nothing; the fallback would have to be the geometry gate alone, and there is no
   black stamp in the corpus to test it on. Do not write that rule until there is one.
3. **Text inside a stamp that shares the stamp's colour and sits inside its border.** The geometry
   gate cannot separate it. No such case was found, but it is not excluded by construction.

## What was tried and failed, so it is not tried again

- **Reconstructing the stamp** (draw_rect plus insert_text): lost the borders, lost the rotation, and
  substituted the font. The stamp must be rendered by the PDF's own renderer, never rebuilt.
- **Redacting the non-stamp objects and rendering**: a zero-height rule survives a redaction whose
  rect is degenerate, and `get_drawings()` does not list everything - a line inside a Form XObject was
  missed and reappeared in the image. The colour mask plus the geometry gate has no such hole.
- **Cropping the anchor extent**: correct on two documents by coincidence and eight times too small on
  a third. Rule 2 exists because of that.

## Rule 5 - the image is RGBA, so only the stamp's own shape is opaque

**Emit RGBA with alpha = the mask. Everything that is not stamp ink is transparent, not white.**

This is not cosmetic. A rectangular crop of a stamp carries 86 to 91 percent of its area as opaque
white that is not the stamp, and that white hides whatever is behind it. Measured on the four stamps:

    312_affidavit_stamp_paper      ink 14.1%   transparent 85.9%   (the four corners of the box)
    01_stamp_rotated_15deg_upright ink  9.0%   transparent 91.0%   (the triangles outside the rotation)
    03_stamp_vertical_90deg        ink 13.1%   transparent 86.9%

On the circular seal the difference is plainest: a rectangle puts an opaque square around a circle.

**Google keeps the alpha.** A hand-built .docx carrying an RGBA PNG (colour type 6) was uploaded,
converted and exported; the image in the export is `874x452, bpc=8, cs=ICCBased, smask=7`. The alpha
mask survived.

**And the alpha does not move anything.** Alpha is visibility, not geometry: the anchor and the extent
are unchanged, so the position measured above - dx +0.7, dy +0.6 pt - was measured with an RGBA image
and stands.

### The interior is transparent because the PDF's is

All eleven stamp documents were checked for a fill on their stamp drawings: **every one is unfilled**,
so the area inside the border is transparent in the source and must stay transparent in the image -
body text behind a stamp is meant to show through it. Making it opaque would be a change, not a copy.

**If a stamp ever carries a fill, this rule inverts for that stamp:** the filled interior must be
opaque. No such stamp exists in the corpus, so that branch is unproven and must not be written until
one appears - the same standing as the black-stamp fallback.

## WITHDRAWN - the stroke-weight issue below was a measurement artefact, see CORRECTION 2, and it is measured, not an impression

All five rules were applied end to end to one real document, `312_affidavit_stamp_paper`, and exported
from Google. What worked:

    position        dx +0.4 pt, dy +0.0 pt
    shape           the circle is a circle, the four corners of the box are transparent
    nothing else    no body text, no foreign ink

What did not:

    ORIGINAL (vector)  core ink 17,893 px   ink mass 2,735,337
    image version      core ink 28,233 px   ink mass 4,095,952     +58% ink

The stamp's strokes are visibly heavier than the PDF's. Three attempts did not fix it:

1. **300 DPI, binary alpha** - heavy and soft.
2. **600 DPI, continuous alpha from colour distance** - heavy. Resolution was not the cause: the fringe
   grew with the resolution, so the ratio stayed the same.
3. **600 DPI, redact everything that is not the stamp, then let the PDF render it** - heavy. Partial
   coverage dropped from 5.1 to 2.6 percent of pixels, and the ink mass did not move.

Attempt 3 rules out the mask: with the mask gone and the PDF's own renderer doing the work, the result
is the same weight. **So this is the vector-to-raster step itself.** A 1.2 pt stroke rasterised at any
DPI, downsampled by Google's export, spreads over more pixels than the vector stroke does at the same
display size, and reads heavier.

**Do not claim a stamp is fixed while this is open.** Position, shape and isolation are proved; stroke
weight is not. The next thing to try is not another DPI setting - it is either a threshold on the
coverage that keeps the stroke's core width and discards the outer fringe, or accepting that a raster
stamp is inherently a little heavier than the vector original and setting a tolerance on ink mass that
a candidate must pass before it is accepted.

What is ruled out, so it is not retried: 300 DPI, 600 DPI, binary alpha, continuous alpha, and
redact-then-render. All five measured, all five +50 to +58 percent ink.

## CORRECTION - the 58 percent figure was wrong, and the reason is a bug I had just written

The user opened the document I had produced and saw **two seals**: the original one, still in place, and
a second one that moved when they dragged it. They also saw that the original's outline is slightly cut
while the new one's is not - which is itself proof they are two different objects.

They were right, and the cause is worth recording because it invalidates the measurement above.

**`312_affidavit_stamp_paper` does not have one textbox for its stamp. It has twenty-eight, one per
character** - the curved text around the circle is drawn as individually positioned letters:

    #0 'A'  #1 'D'  #2 'V'  #3 'O'  #4 'C'  #5 'A'  #6 'T'  #7 'E'      ADVOCATE
    #8 'N'  #9 'D' #10 'N' #11 'O' #12 'T' #13 'A' #14 'R' #15 'Y'      AND NOTARY
    #16 'B' ... #23 'U'                                                 BENGALURU
    #26 'INDIA'   #27 '2024'

I replaced **the first textbox anchor I found**, which was a 10.0 x 8.6 pt anchor holding the single
letter `A`. The seal was never touched. So the document ended up with the original seal plus my image
on top of it, and the ink measurement above was counting both.

**Corrected measurement, same page, same 150 dpi:**

    original PDF       4,828 navy px
    my buggy build     7,863 navy px    +63%  (the original seal plus my image)
    corrected build    6,415 navy px    +33%  (my image alone)

So the stroke is **33 percent heavier, not 58**. Still heavier than the vector original - the open
issue below stands - but the number in it was contaminated by a duplicate.

## Rule 6 - which anchors are the stamp

**Every anchor whose rect lies inside the stamp's rect in the PDF belongs to the stamp. Replace all of
them, not the first one.**

Measured on `312_affidavit_stamp_paper`: all 28 per-character anchors lie inside the stamp rect
(282.0,653.9 -> 358.0,729.9). On `01_stamp_rotated_15deg_upright` there is exactly one. The rule covers
both, and it is the only thing that stops the duplicate.

Verified after the change: textbox anchors in the document went from 28 to 0, and the exported page
carries one seal at the right place with the ink figure above.

## The lesson, because it has now happened five times

Every attempt to decide "which textbox is the stamp" by guessing - by count, by stamp-like words, by
whether words appear inside a textbox, by picking the first one - has been wrong. The rule above works
because it asks the PDF where the stamp is and then takes **everything** inside that rectangle, rather
than trying to recognise a stamp by what it looks like.

## CORRECTION 2 - there was no stroke-weight problem. Both ink figures were counting leftovers.

After the correction above I rebuilt the document and the user opened it again. There were still two
seals: one with text, and **one that was an empty circle**. The empty circle was the original seal's two
border shapes, which my removal had missed because it only looked for textbox anchors.

Measured: of the 30 anchors inside the stamp rect on `312_affidavit_stamp_paper`, **28 are textboxes
(one per letter) and 2 are shapes (the outer and inner circle)**. I had removed the 28 and left the 2.

Removing all 30 and measuring again on the same page at the same 150 dpi:

    original PDF          4,828 navy px
    first build           6,415   (the two border shapes were still there)
    corrected build       4,337   - 10 percent BELOW the original, not above it

**So the stroke-weight problem recorded in the open issue above does not exist.** Both the 58 percent
and the 33 percent were the same mistake twice: I measured a page that carried extra objects and
attributed the extra ink to stroke weight. The image's ink is within 10 percent of the vector
original, on the low side.

The open issue is withdrawn. The three attempts recorded there - 300 DPI, 600 DPI, redact-then-render -
were not wrong to try, but none of them was ever going to move a number that was being inflated by
objects that should not have been on the page at all.

**Rule 6, corrected, and this is the whole of it:**

> Every anchor whose rect lies inside the stamp's rect in the PDF belongs to the stamp - **textbox,
> shape or picture, every kind**. Remove all of them, then place one image.

On 312 that is 30 anchors (28 textbox + 2 shape). On `01_stamp_rotated_15deg_upright` it is one. The
kind does not matter; the position inside the stamp's rect is the whole test.

## The pattern, said plainly

Three numbers in a row - 58, 33, then the truth - were each printed against a thing they did not
describe. The first two were not measurement errors in the arithmetic; they were measurements of the
wrong object, and the wrong object was there because the previous fix had left it behind. **A number is
only as good as the page it was taken from.** Before measuring a change, check that the page holds
nothing but the change.

## Rule 7 - never redact. Redaction deletes whatever else shares the rectangle.

Proved by applying the rules to `01_stamp_rotated_15deg_upright` and `02_stamp_rotated_15deg_upleft`,
which the earlier single-document work on 312 had not exposed.

On the first attempt `02` came out reading **"IN ER" and "ODS RECEIVED"** - the left half of both lines
gone. The stamp's own text was the right colour and inside the crop, so neither the colour rule nor the
crop was at fault. The cause was the redaction step: to remove the black body text
`Total packages: 7 | Total quantity: ...` I redacted its bounding box, and **that box overlaps the green
stamp text**, so `page.apply_redactions()` erased both. Redaction removes everything inside the
rectangle, not the span you named.

**So rule 4 is a mask, never a redaction.** Render the region as it is and decide per pixel:

    keep = colour distance to the stamp ink < 170
           AND saturation >= max(25, target_saturation * 0.45)
           AND the pixel lies inside a stamp drawing or a stamp-colour text span

That keeps the black body text out by colour and the grey text out by saturation, and it cannot delete
anything, because it never edits the page.

### Measured on both stamps after the change

    01_stamp_rotated_15deg_upright   dx +0.2  dy +0.2 pt   size 206.6x105.4 vs 207.8x106.3   ink -4%
    02_stamp_rotated_15deg_upleft    dx +0.5  dy +0.7 pt   size 163.4x96.0  vs 164.9x97.7    ink -5%

Both under one point of offset, under 1.5 pt of size, under 5 percent of ink, with the body text behind
each stamp showing through the transparent interior exactly as it does in the PDF.

**The lesson that cost this round:** 312 did not have overlapping body text under its stamp, so the
redaction bug was invisible there. A method proved on one document is proved on one document. 01 and 02
were the reason it surfaced.

## The whole stamp set, run through the rules in one pass

Sixteen stamp documents run through all seven rules locally, checking per document that a stamp colour
was found, that the crop is sane, that anchors were actually found to remove, and that the mask is
neither empty nor nearly empty.

**Thirteen pass.** Two bugs came out of it that three documents alone had not shown.

### Bug A - rule 6's test was containment, and it is wrong

`03_stamp_vertical_90deg` and `04_stamp_180deg_upside_down` both came back **kill 0** - no anchor
removed - which is exactly the duplicate-stamp bug the user had already caught by eye on 312.

The reason is that a textbox is **larger than the stamp it draws**:

    03   anchor 108 x 122 pt   stamp  55 x 122 pt   overlap 51%
    04   anchor 182 x  73 pt   stamp 182 x  64 pt   overlap 87%

The test `q.x1 <= stamp.x1 + 2` demands the anchor be **inside** the stamp. It never is, because the
box carries padding. The right test is the other way round:

> An anchor belongs to the stamp when it overlaps the stamp's rect and the overlap is at least **half
> the area of the smaller of the two rectangles**.

That is 100 percent on 03, 100 percent on 04, and 100 percent on each of 312's 28 per-letter anchors,
while a body-text anchor that merely clips the corner scores far below half and is excluded. With the
change 03 and 04 both report kill 1.

### Bug B - the flow starts in the wrong place

Three documents still fail, and each for the same structural reason: **the method begins by looking for
a textbox anchor**, and these three do not have one.

    10_stamp_as_image            0 textbox, 14 shape, 1 picture  - the stamp is ALREADY a picture
    12_stamp_across_page_break   0 textbox, 10 shape, 0 picture  - the stamp is drawn as shapes only
    14_stamp_chars_positioned_td 2 textbox but the stamp is text with NO border drawing, so rule 1
                                 finds no coloured drawing to take a colour from

Two generalisations, neither written yet:

- **Rule 1'** - when there is no coloured drawing in the region, take the most common non-black **text**
  colour instead. `14`'s stamp text is `(0.05,0.15,0.55)` and appears in the PDF's text colours.
- **Rule 6'** - do not start from a textbox anchor at all. **Locate the stamp in the PDF first**, then
  remove every anchor that overlaps it, of any kind. That covers 10 and 12, where there is no textbox
  to start from, and it makes rule 6's overlap test the only locator rather than a follow-up.

### The batch, as it stands

    ok      01 02 03 04 06 07 08 09 11 13 15 312 43          thirteen
    open    10 12 14                                          three, both generalisations above

**Do not claim the stamp set is fixed while those three are open.** Thirteen of sixteen is not sixteen,
and the three that fail are not random - they are the three shapes the current flow cannot enter.

### What this cost and what it bought

Running one document produced a method that looked complete. Running three produced two corrections.
Running sixteen produced two more. **The defects are in the shapes the sample did not contain, and there
is no way to find them except to run the whole set.**
