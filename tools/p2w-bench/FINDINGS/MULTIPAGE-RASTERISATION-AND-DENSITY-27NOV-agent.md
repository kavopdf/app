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

## Through Google, the last pages are not degraded - they are gone

The LibreOffice measurement above is withdrawn as a result. The same `.docx` exported through Google:

    10 source pages -> 11 rendered pages

    pg  source chars  google chars  recall   median offset
     1      1854          856        46.2%     168.6 pt
     2      4232          203         4.8%      42.9 pt
     3      3089          507        16.4%      79.2 pt
     4      1187          536        45.2%     364.1 pt
     5      2143         1746        81.5%      39.4 pt
     6      2104          292        13.9%     168.4 pt
     7      1568         1680       107.1%      63.8 pt
     8      2525         2577       102.1%      44.8 pt
     9      2286           35         1.5%     825.0 pt
    10      2233         2168        97.1%     198.3 pt

**46 percent of the text reaches the render. The median position error is 123.8 pt - one and a half inches.**

**And page 9 is visually blank.** Rendered side by side against the source, the source page holds a header, a
section heading, five stage boxes, six formulae, a code listing, a checklist table and two note columns. The
Google page holds a single horizontal rule and some fragments clipped at the top edge.

**This is not rasterisation and not degradation. The content is absent** - not present as text, not present as an
image, not present as anything.

### Why, and it is the mechanism this work suspected from the start

**Every paragraph is positioned absolutely by `w:before`. There is no flow.** When the accumulated vertical
position passes the page's height, **Google does not carry the content to the next page - it drops it.** A flowing
document would push it forward; an absolutely positioned one has nowhere to put it.

The fragments at the top of the blank page confirm the direction: content ended up at a **negative y**, above the
page origin, and was clipped.

**That also explains the extra page.** Some of the overflow does land on the following page, which is why the
render is 11 pages for a 10-page source while still losing half the text.

### What this means

**Absolute positioning turns an overflow into permanent data loss.** In a flowing document an overflow is a
pagination problem; here it is deletion. That is the whole difference between our output and Adobe's or
iLovePDF's, and it is why theirs degrades in pageless mode while ours destroys content in the default view.

**Every document long enough to overflow is affected. That is not a class of documents; it is any document with
more content than one page holds.**

## What actually happens to the lost page: a shift plus two deletions

Traced each block of the blank page through the render.

    google page 9     35 chars   only the footer, "8 / 10 | 27 November 2026"
    google page 10  2168 chars   "Process and specification"      <- this is SOURCE page 9
    google page 11  1096 chars   "Forms, seals and colophon"      <- this is SOURCE page 10

**So most of the page did not vanish - it moved down by one page, and page 9 was left holding nothing but its
footer.** That is the extra page: content shifted, nothing replaced it.

**But two blocks are gone entirely.** Searched every page of the render for them:

    PRE-PRESS CHECKLIST   ->  NOWHERE
    SOURCE LISTING        ->  NOWHERE

Both are on source page 9 - the checklist is a table and the listing is a shaded code block, and both are
visible in the source render.

### So the mechanism has two halves

1. **Plain paragraphs shift by one page.** Their `w:before` moves and they reappear on the next page. Nothing is
   lost, but a page is left empty and the document grows.
2. **Tables and textboxes are dropped.** They cannot shift, because moving a table means recomputing its row
   heights and cell positions, which an absolutely positioned document has no machinery for. So they are
   deleted.

**Half of this is recoverable by pagination and half is permanent.** That is why 46 percent of the text reaches
the render while the page count goes *up* rather than down - content is moving out and being deleted at the same
time.

### The rule, stated once

**In a flowing document an overflow paginates. In an absolutely positioned one it either shifts or is destroyed,
and which of the two depends on whether the object can be moved without recomputing its layout.**

## The source PDF is now in the repository

`benchmarks/corpus-extra/Prakashan_Print_Fidelity_Handbook.pdf` - 10 pages, all A4, uniform margins of 33.6 pt
top and 39.7 pt left on pages 2 to 10, digital throughout, 30 images per page, four fonts. It is the document
every measurement in this file was taken from.

## Where the non-editable text actually is: 53 percent of it is inside textboxes

Counted the containers in the `.docx`:

    wps:txbx                     352
    characters inside them    12,050   -> 53.2 percent of all text in the document
    size spread: 0 chars = 0, under 20 = 132, 20 to 100 = 214, over 100 = 6

**More than half the document's text sits inside a textbox, and Google rasterises `wps:txbx` - which was proved
earlier in this work on a matched export, where the textboxes' text vanished and images appeared in its place.**

**So the user's "much of the text is not editable" is 53.2 percent, and it is not the stamps.** Of the 352
textboxes, **214 hold between 20 and 100 characters** - that is a label, a value, a short line of body text, not
a stamp and not a decorative mark. Those are the ones costing editability.

**The engine is putting ordinary content into textboxes rather than into paragraphs.** That single choice is
what makes half the document uneditable, and it is the same choice that puts 505 `wp:anchor` elements into a
10-page file.

### This is not a separate defect from the overflow one

A textbox is an absolutely positioned object. **The same property that makes Google rasterise it is the property
that makes it impossible to move when the page overflows** - which is why the checklist and the code listing
were deleted rather than shifted, and why the paragraphs that could move did.

**One decision - put content in a textbox instead of a paragraph - produces both the rasterisation and the
deletion.**

## Still to do, and what it needs

- **The same test on the other multi-page documents in `benchmarks/`** - three of them, 9, 9 and 3 pages - to
  confirm the shift-plus-deletion mechanism is not specific to this one file. **Not run: the JDK and the built
  engine were lost when the sandbox was recycled, and both must be fetched and rebuilt first** (the build script
  fetches javac from Adoptium itself, so this is a two-command job).
- **Which PDF objects became the five page-sized images.** The extent query did not match the drawing structure
  and returned nothing, so this is unmeasured rather than empty.
