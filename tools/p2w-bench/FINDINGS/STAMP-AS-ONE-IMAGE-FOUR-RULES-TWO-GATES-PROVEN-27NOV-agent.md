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
