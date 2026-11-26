# The white boxes are Google Docs dark mode compositing a transparent shape onto white

## What the user's screenshots show

Three screenshots of the same documents, from the Google Docs app:

    03_stamp_vertical_90deg, dark mode   the stamp sits on a clear WHITE RECTANGLE on a black page
    03_stamp_vertical_90deg, light mode  the same stamp, no visible box, page is white
    01_stamp_rotated_15deg_upright       the stamp's rectangle interrupts the table rules under it

The white rectangle matches the shape's bounding box exactly. It is not a colour anyone wrote — the
corpus has no white fill anywhere (nine patterns counted, all zero) and every shape declares a fill
(6831 `a:noFill`, 6326 `a:solidFill`, 0 with neither).

## What the export shows

`03_stamp_vertical_90deg.docx` uploaded, converted to a Google Doc, exported to PDF:

    22 images on page 1
    xref 4    139x164   SMask 6    transparent
    xref 27   661x332   SMask 28   transparent   <- the stamp shape
    the 659x1 rules      no SMask, opaque black   <- correct, those are table rules

    4 of 22 images carry an SMask; the rest are 1-pixel rules that should be opaque

Rendered ink 41312 on the control document, 0 images rasterised as white. The PDF export is clean.

## So the mechanism is

The shape is rasterised to a **transparent** image. On a white page a transparent image is invisible.
Google Docs **dark mode** inverts the page but composites the transparent image onto **white** instead of
onto the inverted background. The result is a white rectangle exactly the size of the shape.

This explains every measurement taken today:

    light mode          invisible        white on white
    dark mode           visible          white box on black page
    PDF export          absent           the export never composites onto white
    white fill search   0 hits           nothing paints white; the compositor does
    noFill shapes       0.0% white px    the image really is transparent

## What this means for the fix

Removing the shape removes the image, and removing the image removes the white box. There is no attribute
that makes Google Docs dark mode composite correctly — the fix is to stop producing a rasterised shape
where one is not needed.

    form fields   borderless positional table (proven, x = 206.7 pt, no visible borders)
    flow text     w:ind + w:spacing (proven, x = 206.7 pt)
    stamps        keep the shape, but it will keep the box in dark mode; 300 dpi + a:xfrm rot at least
                  makes it correct in light mode and in the exported PDF

## What is not proven

That the dark-mode composite is white for every shape. Only one document was round-tripped here. The
mechanism fits every measurement, but the corpus-wide count of affected documents was not taken.
