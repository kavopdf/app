# content-missing-partly-replaced / B - the wrapped heading: renderer limit or our width?

Asked: our engine emits `wps:txbx` text boxes. On `041122-Account_Opening_Form.pdf` a heading
       comes out wrapped over ~20 lines in a box measured 11 pt wide (x 573.1-584.0), while the
       same heading also sits in a 58 pt wide box (x 513.9-571.5). Is the wrap a LibreOffice/DOCX
       renderer limit, or is the width we emit wrong? Three hand-written text-box variants of one
       heading, same anchor or same width, rendered with `soffice --headless --convert-to pdf`.

Claim: RENDERER, NOT ANCHOR. A text box wraps strictly to the width it is given and the anchor x
       has no effect on wrapping at all: 58 pt at the emitted x gives the same 4 lines as 58 pt at
       the source x, while 11 pt gives 25 lines. So the wrap in an 11 pt box is what any renderer
       must do and is not a defect of the renderer; the defect is in the WIDTH (and the indent that
       produces it), which is engine-side and fixable there.
       Measured correction to the premise: on this document the wrapping container is 58 pt, not
       11 pt. The 11 pt figure is an INK width, not a container width - see Evidence 3. The heading
       that actually wraps over 28 lines is the copy in the 58 pt column at x 513.9.

Evidence: 1. Controlled measurement, one heading, one page geometry, boxes 300 pt tall, 9 pt bold
       Arial, text "Annexure-1 Income-tax Rules, 1962 FORM NO.60". Each variant in its own docx,
       each rendered with `soffice --headless --convert-to pdf` (LibreOffice 7.4.7.2), line count
       from the rendered PDF's text layer (PyMuPDF):

         V1  width 58 pt, anchor x 513.9 (correct width, correct x) -> 4 lines
             y 41.3-81.3, ink x 514.0-569.0, widest line 54.96 pt
             "Annexure-1" / "Income-tax" / "Rules, 1962" / "FORM NO.60"
         V2  width 11 pt, anchor x 573.1 (the width we emit, at the x we emit) -> 25 lines
             y 41.3-298.7, ink x 573.2-584.2, widest line 10.98 pt, ~2 glyphs per line
         V3  width 58 pt, anchor x 573.1 (correct width, the x we emit) -> 4 lines
             y 41.3-81.3, ink x 573.2-599.7, widest line 26.48 pt
         V0  control, width 11 pt, anchor x 573.1, `wps:bodyPr wrap="none"` (exactly what the
             engine emits) -> 25 lines, byte-for-byte the same line breaks as V2

       V3 equals V1 in line count (4) and in line y positions (41.3-81.3) although the anchor is
       60 pt to the right. V3's ink runs to x 599.7, past the 595.5 pt page edge, and still does
       not wrap further: the renderer honours the box width, not the page or the anchor.

       2. `wrap="none"` does not save us. V0 carries the engine's own `bodyPr` attribute set
       (`wrap="none" lIns=0 tIns=0 rIns=0 bIns=0 anchor="t"`, `<a:noAutofit/>`) and wraps
       identically to V2. LibreOffice 7.4.7.2 ignores `wrap="none"` for text-box text flow, so the
       emitted attribute is not a guard against wrapping. Any width we emit is the width the text
       gets.

       3. The real geometry, read out of the docx the engine produced for 041122 (unzipped
       document.xml, this run). Both "boxes" in the question are table cells of the page-7 table,
       not `wps:txbx` shapes - document.xml contains no text box carrying this heading:
         cell 2: tcW 10636 dxa (531.8 pt), paragraph `<w:ind w:left="9452"/>` = 472.6 pt indent,
                 so the heading's usable width is 10636-9452 = 1184 dxa = 59.2 pt starting at
                 x 513.9. This is the "58 pt wide box". In the LibreOffice render it wraps over
                 **28 lines**, y 23.4-293.4 (copy A, measured on page 7).
         cell 3: tcW 456 dxa (22.8 pt), the right-hand margin column, starting at x 572.8. It
                 holds a SECOND copy of the same heading as separate 1 pt paragraphs
                 (`<w:sz w:val="2"/>` = 1 pt), 37 lines on page 7 and 42 on page 8. Its widest
                 rendered line is 10.9 pt - that is the "11 pt wide box (x 573.1-584.0)". It is a
                 22.8 pt cell holding 1 pt text; nothing there wraps at 11 pt.
       Source page 7 for comparison: "Annexure-1" alone at x 513.6-567.0, then "Income-tax Rules,
       1962" centred at x 253.7-355.7, "FORM NO.60" at 276.2-333.2, the proviso at 232.4-377.0 -
       i.e. the title is right-aligned in a 58 pt slot and the remaining heading lines are centred
       across the page. The engine instead merges the whole heading into one paragraph, indents it
       9452 dxa and lets it wrap in the 59 pt that is left.

How to test it: the four variant docx files are 30 lines of hand-written OOXML (anchors on page
       595.5x842.1, `wp:extent cx` = 58/11 pt, `positionH` = 513.9/573.1 pt). Rebuild them by
       writing the same four anchors, then
         soffice --headless --convert-to pdf v1.docx v2.docx v3.docx v0.docx
       and count lines from each PDF's text layer. The numbers above should reproduce to the line.
       To test the engine-side fix, change only the indent the converter emits for that paragraph
       (the `w:ind w:left="9452"` on the heading inside cell 2) and the 1 pt `w:sz` of the copy in
       cell 3, rebuild, convert 041122, and count the copy-A lines again: 28 is the number to move.

Confidence: high for the renderer claim - four variants, one variable each, line counts differ by
       6x and V3 is identical to V1 to the tenth of a point. High for the geometry (read from the
       docx this run produced and from both rendered PDFs). NOT measured: whether Word wraps the
       same way; LibreOffice 7.4.7.2 is the pipeline's renderer proxy and the only renderer used.

Ruled out: "a 58 pt box at the emitted anchor also wraps" - it does not (V3 = 4 lines = V1).
       "the anchor x is a factor in wrapping" - it is not; only width is.
       "`wrap="none"` protects an 11 pt box" - it does not (V0 = V2, 25 lines).
       "the 20-line wrap is inside a `wps:txbx` text box" - on this document it is not; both copies
       of the heading live in table cells, and the wrapping copy is 59 pt wide. The txbx premise
       came from the 11 pt ink width, which is a 1 pt font in a 22.8 pt cell.
       Still open: why the converter emits the heading twice (once indented 9452 dxa, once at 1 pt
       in the margin column). That duplication is not a width question and this measurement does
       not touch it.
Status: complete
