# 18_displacement / B - the engine construct behind the upward page shift

Asked: what construct does the engine use to place a page's content vertically, and which of
       those constructs does Google Docs honour differently from LibreOffice - such that on 14 of
       15 UNIFORM PAGE SHIFT pages the whole block, header included, sits 48.5-67.6 pt HIGHER in
       Google while LibreOffice renders the same .docx within tolerance, the magnitude being
       constant in points rather than proportional to font size?

Claim: A page's content is placed vertically by PARAGRAPH SPACING on a zero-margin page - a
       per-paragraph `w:spacing w:before` (the gap) plus `w:spacing w:line` (the line box) with
       `w:lineRule="exact"` - and the one place where a LARGE vertical distance is written into
       `w:line` instead of `w:before` is the empty table-spacer paragraph at
       `DocxWriter.java:5823-5828`, which writes `w:before="0"` and puts the whole gap into
       `w:line="<gapTw>" w:lineRule="exact"` under a 1 pt paragraph mark (`<w:sz w:val="2"/>`).
       Google Docs does not implement `lineRule="exact"`: it reads `w:line` as 240ths of the
       substitute face's line height for that 1 pt mark, so it buys a small fraction of the gap
       (measured in this repo at 3.16 pt of 13.8 pt asked), and every row of the table below the
       spacer - its header row included - rises by the missing amount. The loss is a fixed number
       of points because the mark is a fixed 1 pt, not the page's type size. LibreOffice honours
       `exact` and puts the gap back.

Evidence:

THE CONSTRUCT. The page box has no margins at all, so every vertical position is spacing:

  DocxWriter.java:2267-2269  (sectPrXml)
      return "<w:pgSz w:w=\"" + w + "\" w:h=\"" + h + "\"" + orient + "/>"
              + "<w:pgMar w:top=\"0\" w:right=\"0\" w:bottom=\"0\" w:left=\"0\""
              + " w:header=\"0\" w:footer=\"0\" w:gutter=\"0\"/>"

  DocxWriter.java:4098-4100  (flowTopPt) - the flow starts at the paper's top edge:
      if (ctx.newPage || ctx.flowY < 0f) return 0f;
      return ctx.flowY + (1f - LINE_BASE) * ctx.flowBoxPt;

  DocxWriter.java:4316-4318  (flowFromBox, the page's FIRST line) - the top gap is `w:before`:
      float topGap = b.y - LINE_BASE * linePt;
      if (topGap > 0f) {
          beforeTw = (int) Math.min((long) firstGapCapTw(ctx), Math.round(topGap * TWIPS_PER_PT));

  DocxWriter.java:149-153 (spacing()) - the shipped default construct for every flow paragraph:
      return "<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\""
              + beforeTw + "\" w:after=\"0\" w:line=\"" + lineTw
              + "\" w:lineRule=\"exact\"/>";

THE ONE PLACE A GAP IS CARRIED IN `w:line`. A table has no before-spacing of its own in OOXML, so
the writer holds the gap open with an empty paragraph - and puts the gap in the line box, with a
1 pt mark, not in `w:before`:

  DocxWriter.java:5778          if (!ctx.newPage && ctx.flowY >= 0f && !Float.isNaN(t.rowTopPt)) {
  DocxWriter.java:5798-5806     float extraAbs = t.rowTopPt - flowTopPt(ctx);
                                if (extraAbs >= 2f) {
                                    spacerTw = (int) Math.min(2880L, Math.round(extraAbs * TWIPS_PER_PT));
                                }
  DocxWriter.java:5823-5828     if (spacerTw > 0) {
                                    spacerTw = twScale(spacerTw, ctx.squeeze);
                                    sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                                            .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"")
                                            .append(spacerTw)
                                            .append("\" w:lineRule=\"exact\"/><w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr></w:p>");

The spacer is capped at 2880 twips (5823-5826: `Math.min(2880L, ...)`), i.e. 144 pt, so the gap it
can carry - and therefore the shift it can produce - is bounded at 144 pt. 48-68 pt is well
inside that bound.

EMITTED XML. No .docx was produced for this finding (no build and no corpus measurement were run,
by instruction), and the repository contains no .docx at all (`find . -name '*.docx'` is empty),
so the fragment below is RECONSTRUCTED BY CONCATENATING THE LITERALS AT 5825-5828 - it is what
that code path emits, not something captured from a conversion. For a 63 pt gap (spacerTw = 1260):

    <w:p><w:pPr><w:snapToGrid w:val="0"/>
      <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0"
                 w:before="0" w:after="0" w:line="1260" w:lineRule="exact"/>
      <w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>

Nothing in that paragraph is a length except `w:line`; `w:before` is 0. The 63 pt exists only as
a line box, and the box's owner is a paragraph mark of 1 pt.

WHY GOOGLE LOSES IT, AND LIBREOFFICE DOES NOT. The repo has already measured both halves of the
model, through Drive, on this writer's own output:

  tools/p2w-bench/REMAINING-DEFECTS.md:119-120
      Word / LibreOffice   advance = w:before + w:line
      Google Docs          advance = w:before + (w:line/240) * lineHeight(face, size)

  tools/p2w-bench/REMAINING-DEFECTS.md:103  "**2. `w:before` is honoured exactly, in points.**
      20 pt came back 20 pt; 40/80/120/160 pt came back 40/80/120/160 pt. It is the one vertical
      length Google reads as a length."

  tools/p2w-bench/RUN-LOG.md:83 (12 Nov 22:27, calibration on 362_price_list_dense, 5 docx
      variants through Drive, only the table spacer varied): "as emitted (w:line=276, mark sz=2)
      first-row dy -13.59, spacer deleted -16.75, w:line=1 -16.58, w:line=240 auto -14.00,
      w:before=276 + w:line=1 -2.78 ... Root cause CONFIRMED: w:line is a multiple of the
      paragraph mark's line height, so the spacer bought 3.16 pt of the 13.8 asked and every
      table rose 10.6 pt."

That is the mechanism measured on this exact construct: a 13.8 pt gap, carried as
`w:line="276"` under a 1 pt mark, bought 3.16 pt in Google and lost 10.6 pt. The same paragraph
written as `w:before="276" w:line="1"` came back at -2.78, i.e. inside tolerance. LibreOffice
honours `exact` on both forms, which is why the same .docx is clean there.

SCALING TO 48-68 pt. The fraction Google buys is set by the 1 pt mark, not by the gap, so the
LOSS grows with the gap. At the measured rate (23 % bought) a gap of 63-88 pt - spacerTw 1260-1760,
under the 2880 cap - loses 48-67 pt. That is the observed band, and it explains the two things
that a font-relative model cannot: (i) the magnitude is CONSTANT IN POINTS, because `w:sz w:val="2"`
is 1 pt on every page of every document whatever the body type is; (ii) it is UNIFORM down the
page, because everything below the spacer is laid out from the flow's position after it, and
nothing below it depends on its height.

WHY "HEADER INCLUDED" AND WHY ONLY TABLE PAGES. The spacer sits between the last paragraph above
the table and the table's top edge, so it carries every row below it - and on the pages in this
class the header is a table row (a repeated header row, or the statement header block the table
pass read as rows). The dy-shape finding already shows the contrast inside one document:
bank-statement-5-pages p0, whose header line is a paragraph ABOVE the table, reads header -0.05
while its table head reads -11.25, whereas p1-p4 - where the header is inside the table - move as
one block at -66.4..-49.8 (18_displacement-dy-shape-101323-4fa7.md, per-page table).

THE SECONDARY SHAPE IS A DIFFERENT CONSTRUCT, AND IT IS IN THE SAME FAMILY. Rows are floored by
`w:trHeight w:hRule="atLeast"` and their cells carry the row pitch as a `w:line` box:

  DocxWriter.java:6270-6273
      inner.append("<w:tr>");
      if (rowTwHere > 0) {
          inner.append("<w:trPr><w:trHeight w:val=\"").append(rowHeightTw)
               .append("\" w:hRule=\"atLeast\"/><w:cantSplit/></w:trPr>");

  DocxWriter.java:6121
      int cellLineHere = contentTwHere > 0 ? contentTwHere : 200;

`atLeast` is a floor Google is free to exceed when the row's content plus its rule exceeds it
(the rule is charged on top of content - measured at 5951-6060), which is a per-row charge that
accumulates: that is the +1.85 to +3.6 pt per 100 pt of depth, Google's rows being 2-3.6 % taller.

How to test it: the smallest patch is one append() in the spacer, at DocxWriter.java:5826-5828 -
move the gap out of the line box and into the before-gap, which Google reads as a length:

    .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"")
    .append(spacerTw)
    .append("\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")

and leave `w:sz w:val="2"` and the cap alone. Test it on a document from the uniform-shift class -
602_bookmarked_annual_report p1 (a = -67.4, drift 0.1: a pure top-move) and bank-statement-5-pages
p1 (median -56.9) are the two cleanest - with 362_price_list_dense as the calibration control
(RUN-LOG:83 already knows what that one does). Measure per-page dy the way
18_displacement-dy-shape-101323-4fa7.md did (Google export vs LibreOffice, check 18's own pairs).
The claim predicts, and this is the discriminator:
  (1) the uniform pages' median dy moves from -48..-68 to inside tolerance, and it moves by
      almost exactly the spacer's own height;
  (2) the paragraph ABOVE the spacer does not move at all - if the text line above the table
      moves too, this construct is not what is carrying that page and the finding is wrong;
  (3) pages whose header is a paragraph above the table (bank-statement p0, 302, 370, 52) show
      no change in their header's dy, only in the table below it;
  (4) the progressive-drift pages barely move, because their error is `w:trHeight`/cell `w:line`
      and not the spacer - that needs the second patch (row rule), not this one.
A cheaper first check that needs no build: grep the .docx of a failing document for
`w:line="1[0-9][0-9][0-9]"` with `w:sz w:val="2"` in the same paragraph. Every such paragraph is
one of these spacers, and its `w:line`/20 is the number of points that page stands to lose.

Confidence: medium. High that this is the only construct in the writer that puts a large vertical
distance into `w:line` instead of `w:before` (searched: every `w:line` emission in DocxWriter.java;
the others are hairlines - 668, 1057, 1077, 2088, 2427, 2734, 5399 - a text box's own line box,
3560 and 5153, or a cell's row-pitch box, 6121). High that Google under-reads `w:line` and honours `w:before`, because both
are measured through Drive on this writer's output (REMAINING-DEFECTS.md:103,119-120) and the
spacer itself was calibrated to 3.16 pt of 13.8 (RUN-LOG.md:83). Medium for it being the whole of
the 48-68 pt band: the 13.8 -> 63-88 pt extrapolation is an extrapolation, and the "header
included" part rests on the header being a table row rather than a paragraph - which the dy-shape
finding supports for bank-statement p1-p4 but does not prove for every page in the class.

Ruled out:
  PAGE MARGINS (`w:pgMar`). Written, at 2267-2269, and `w:top="0"` - all four margins zero plus
    `w:header="0" w:footer="0" w:gutter="0"`. Both renderers honour a zero margin identically, so
    it cannot produce a 48-68 pt difference in either direction. It is the reason every vertical
    position has to be spacing, not the cause of the shift.
  THE PAGE'S FIRST LINE's `w:before`. This is the construct that places a page's first TEXT line
    (4316-4318) and the engine's own comment records the failure it fixes - "on file 21 every line
    measured 46 pt high ... dy was -46.2, -48.3, -45.0, -46.6" (4232-4236) - which is the right
    magnitude. Rejected because Google honours `w:before` exactly: 20/40/80/120/160 pt all came
    back exact (REMAINING-DEFECTS.md:103). If it were being dropped, a 160 pt probe would have
    failed too.
  `w:spacing w:before` generally. Same measurement, same rejection. It is also the fix, not the
    fault: RUN-LOG.md:83 shows `w:before=276 w:line=1` landing at -2.78 where the shipped form
    lands at -13.59.
  `w:after` / `w:lineRule="auto"` / `w:line="240"`. The shipped default is `exact` (LINE_MODE
    default 0, 135-138); `auto` is an experiment flag and every emitted flow paragraph writes
    `w:after="0"` (149-153). `after` cannot shift a block upward and does not act above a
    paragraph at all.
  `docDefaults` / the `Normal` style. `w:pPrDefault` exists (7312) and carries
    `<w:spacing w:after="120"/>` only - no `w:line`, no `w:before` - and `Normal` declares no
    `w:pPr` at all (7314-7315). Since every flow paragraph writes its own `w:spacing` with
    `w:after="0"`, the default never reaches the page. Google applying its own default spacing
    where docDefaults is thin would push content DOWN and would accumulate per paragraph, which is
    the opposite sign and the opposite shape to a constant 48-68 pt lift of a whole page.
  `w:ind` (absolute indents). Used, but horizontally only - "The x becomes `w:ind w:left`; the gap
    to the previous line becomes `w:spacing w:before`" (4107-4108). It carries no y and cannot
    move a page.
  `w:framePr` TEXT FRAMES. Not used. The writer deliberately removed them - "it is not a frame -
    `w:framePr` pinned the flow but Google Docs ignores frame positioning" (PdfToWord.java:124-126),
    and the same note recurs at DocxWriter.java:3007, 3260, 4944. So the known Google-vs-LibreOffice
    `framePr` divergence is real but is not what these documents contain.
  FLOATING `<w:drawing>` SHAPES. Used, but only for stamps, pictures and text boxes, each in a
    one-twip carrier paragraph (5398-5400: `w:line="1" w:lineRule="exact"`, `w:sz w:val="2"`). A
    dropped anchor loses a stamp or a picture; it does not lift the page's text, and the pages in
    this class carry their failing runs in body flow and table cells.
  `w:docGrid w:linePitch="360"` (2271, in `sectPrXml`). Emitted without `w:type`, i.e. the
    default grid that snaps nothing; Google ignores `docGrid` entirely. No y is carried by it.
  A LIBREOFFICE-SIDE FAULT. Already excluded by measurement: the same .docx renders within 4.11 pt
    on all 28 pages (18_displacement-dy-shape-101323-4fa7.md). LibreOffice honours
    `w:lineRule="exact"` as a length, so the spacer works there.

Status: complete
