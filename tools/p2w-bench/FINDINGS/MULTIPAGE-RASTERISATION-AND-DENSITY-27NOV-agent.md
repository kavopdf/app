# A 10-page PDF becomes a 4.3 MB docx that is 98 percent pictures

Converted the user's 10-page handbook through the engine, built from the repo, on the JVM. **This is the first
end-to-end conversion done by hand in this work - the engine had only ever been measured, never run locally.**

## What the engine said

    Prakashan_Print_Fidelity_Handbook  pages=10  paragraphs=349  zeroGap=15  zeroGapWorst=128.7  images=33

## What the docx actually contains

    source PDF           2.9 MB
    output .docx         4.3 MB
    images in package      33        4.2 MB   -> 98 percent of the file
    real text            22,630 characters
    paragraphs            1,281
    wp:anchor               505
    wps:txbx                352
    w:lineRule="exact"    1,281      -> every paragraph

    largest images: image1 1335 KB, image15 536 KB, image14 511 KB, image13 505 KB, image12 450 KB

**Five images account for 3.3 MB and they are page-sized.** Whatever text lies under them is pixels, not
characters - it cannot be edited, searched, copied or scaled.

## This is the "much of the text is not editable" the user reported

The user opened the file in Google Docs and said exactly that. **Two mechanisms, both measured here:**

- **5 page-sized images** covering large regions of the page
- **352 textboxes** - and `wps:txbx` content is rasterised by Google, which was proved earlier in this work on a
  matched export

**So the non-editable share is not a rendering accident at the end; it is written into the `.docx`.**

## And every paragraph carries the clipping construct

**1,281 of 1,281 paragraphs use `w:lineRule="exact"`.** The measured behaviour of that construct: a 0.6 pt line
box around 8.5 pt text, which clips descenders and, in a table cell, gives only a 6.3 pt floor against an 11.07 pt
glyph.

**The engine also reported `zeroGap=15` with `zeroGapWorst=128.7` on its own** - fifteen places where it knew
content had no room and placed it anyway.

## What I got wrong in the same session, recorded so it is not repeated

**I measured the converted file with LibreOffice and reported an 11-page render with page 9 emptied to 34
characters.** The user opened the same `.docx` in Google Docs and it was **10 pages**, with no such collapse.
**LibreOffice was not the official renderer and the numbers taken from it did not describe what the user sees.**

**Two lessons, both already in this repository and both ignored by me:**

- **Google is the renderer that counts.** A measurement taken through LibreOffice is a hypothesis about Google,
  not a result.
- **A number is only as good as the instrument.** The page-9 catastrophe may exist in Google or may not; **it is
  not established either way and must not be quoted as a finding.**

## What to measure next, in this order

1. **The Google export of this exact file**, and the same per-page text and position comparison. That is the only
   version of the page-9 question worth asking.
2. **What the 5 page-sized images cover** - which PDF objects became pictures. That is the "not editable" share.
3. **The 352 textboxes** - how many of them hold body text rather than a stamp or a label.
