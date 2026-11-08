# Remaining defects — to be worked at the very end

## STATUS - READ THIS FIRST

Three entries below are **FIXED AND SHIPPED**. Do not work them, do not reopen them, do not
re-derive them. The reasoning is kept so it is not lost; the code is already in the tree.

| Entry | Status | Shipped as | Measured |
|---|---|---|---|
| **D-08** columns, sections, reading order | **FIXED 8 Nov** | `a81ca28`, `685ce4b`, `3078b62` | G2 clean on 208, three times |
| **D-14** the invoice table | **FIXED 8 Nov** | `265cda1` | G2 clean on 208; 127 documents carry tables where 112 did, 212 `w:tbl` where 183 |
| **D-20** table rule thickness and the missing side | **FIXED 8 Nov** | `c47efc2` | G2 clean on 208; 55 tables that were `none` are ruled, widths now 3-10 eighths, 55 borders black |

Still open and yours: **D-18** (letter-spacing, 1/3 tries) and **D-19** (a figure written as loose
anchors, 0/3 tries), plus the batch work.

A note on editing this file: headings get rewritten by tooling, and a marker added to a heading has
been lost before. If you need to record a status, put it in this block or append a section at the
end of the file, not in a heading.


## v3 corpus — batch 1 (300-317), re-run 8 Nov 08:38

Fifteen documents, one page each, all seventeen steps in order, every page opened before any number
was read. Eleven findings, 11 verified, 0 refuted, 0 unverifiable. Ten pass, five fail. No fix was
attempted this run; the measurements below are the work items.

### OPEN — a band of label/value pairs is emitted one field per paragraph

301_lab_report_panel. `moved:MPL03184471` verified: 2 on both sides, worst offset 34.3 pt. The page
sets a four-column band - PATIENT / AGE-SEX / REFERRED BY / COLLECTED over their values, then
SAMPLE / BARCODE / REPORTED / STATUS over theirs. Each pair shares one baseline on the page. The
render puts the four labels at 61.2, 64.4, 69.5 and 72.7 pt and the values at 81.5, 89.0, 89.0 and
91.0, so the band reads ragged and its extra height pushes the ten-row table 19.9 pt down. Reading
order 80.0 % of 28 rows, 32 rows in the render. **Tries: 0 of 3.**

### OPEN — a table's own top y is not reproduced

311_fir_police_form. `missing:560067` verified: the PDF holds "Bengaluru 560067", the render holds
"Bengaluru 5 60067Mobile" - a space inside the pin and the Mobile label welded on. Separately the
whole first table sits 15.7 pt high: the page puts its first row at y=72.1, the render at 56.4, and
every row carries the same 15.7 pt. The spacer the writer emits before a table charges
`(t.top - baseline) - lastSize*1.15`, which is one line short of the previous paragraph's own box
bottom; when that comes out below 1.2 lines the spacer is dropped altogether, which is what happens
here. **Tries: 0 of 3.**

### OPEN — a column's line pitch is taken across the column break

315_gazette_notification. `moved:into force on the date of their` verified: y=214.8 in the PDF,
y=284.6 in the render, 69.8 pt. Column 1 holds 18 lines on both sides but runs from 66.7 to 208.0 in
the PDF and 63.2 to 278.1 in the render - a pitch of 8.3 pt against 12.6. The model interleaves the
three columns and the writer measures each line's pitch against the previous line, which at a column
break is a line in a different column. Reading order 47.1 % of 21 rows, 30 rows in the render.
**Tries: 0 of 3.**

### OPEN — a line the PDF drew past the right margin is wrapped instead

303_discharge_summary. `breaks:WARNING SIGNS` verified: the PDF's line ends at "needed" and no render
line does. The PDF's WARNING SIGNS line runs from x=28.0 to x=596.7 on a 595.3 pt page, so its tail
"more than 4 times a day." is drawn off the paper and never appears. The render wraps it onto a
second line at x=578.7. The flow wraps at the column edge; the page did not. A faithful render has to
let the line overrun the way the page did. **Tries: 1 of 3 - two attempts measured 8 Nov 19:40, both
rejected. See below.**

**Try 1 - place the line instead of flowing it.** A line whose measured right edge is past the paper
was given the anchored text box the rotated and out-of-flow lines already use, on the reasoning that
`bodyPr wrap="none"` cannot re-break it. It does not re-break it - it CLIPS it at the page edge, and
the render lost four words ("times a day.") instead of wrapping two. Worse than the defect. Reverted.

**Try 2 - pin the left edge and drop the right alignment.** The paragraph is `w:jc="right"` with no
right indent, so an over-wide line is flushed to the paper's edge: its left end landed at x=16.6
against the page's 28.0. Pinning `w:ind w:left` to the page's own x and dropping `w:jc` fixed that
exactly (x=28.1) and cleared `moved:WARNING SIGNS` - but it regressed
`18_centred_heading_left_body_txtpos` from 100 % of its lines in tolerance to 39 %, because the same
condition fires on its numbered clauses, whose model x sits 11.8 pt right of the edge they are drawn
at. G2 across 208 was clean (it counts words, pages, images and tables, not positions); the position
ratchet caught it, which is what the ratchet is for. Reverted, baseline untouched.

**What is left.** The line still wraps. The render's substitute face (NotoSans-Bold against the PDF's
DejaVuSans-Bold) sets the same string about 4 % wider - 578 pt against the page's 567.3 pt of text
area - and nothing in the flow can be told the render's metrics at write time. Condensing the run
would need that number. This is the one class where the measurement layer knows the truth and the
implementation layer has no construct for it.

### OPEN — a rotated seal's arc text is repeated

312_affidavit_stamp_paper. `extra:NOTARY` verified: 0 on the PDF side, 1 in the render. The seal is a
circular notary stamp drawn as per-glyph rotated text; the render carries "OCATE AND NOTARY" and a
second "VOCATE", so the arc reads twice. This is the rotated-stamp class - OOXML has no text rotation
a LibreOffice render honours - so it gets ONE try and then a CLOSED-UNFIXABLE entry. The bench also
cannot rasterise it: `PDFRenderer.renderImageWithDPI` throws `NoSuchMethodError Canvas.getMatrix()`
against the JVM stubs, so the raster fallback is not exercised here. **Tries: 0 of 3 (1 allowed).**

### Measurement blind spots found this pass - repair the tool, not the page

    emphasis on 304_package_insert_small_print   6 of 9 emphasised lines "lost" it. The render's
        headings are bold DejaVuSans-Bold with <w:b/>, and the page drew them bold. q8 compares a
        line's SIZE, and a bold heading keeps its size, so the loss it reports is not a weight test
        at all. The eye passes the page and is right.

    order on 305_vaccination_certificate         47.1 % of 27 rows. The PDF draws every table cell as
        its own line and the render joins a row's cells with tabs, so the row counts cannot match:
        27 rows in the PDF, 24 in the render. The eye passes the page and is right.

    position on 300 / 302 / 306 / 314 / 316       a uniform per-block offset the eye cannot see at
        130 dpi: 12.4 pt on 300's medicine table, 9.3 on 302's label band, 4.7 on 306, 6.4 on 314,
        3.2 on 316. All in the same direction - the block sits high - so they are one defect, the
        table and band top y, recorded above on 311.

    width on 310 / 313 / 317                      the centred heading renders 17.5 % narrower
        (346 pt against 285.3 pt on 310) because the page tracks the line - 1.2 to 1.5 pt of extra
        advance per glyph - and the run carries no `w:spacing`. Centring is right: both centres are
        at 297.6. This is the 39_small_caps_letter_spacing family and is not fixed.

## b80 corpus — batch 2 (21-40), 8 Nov

Twenty documents, one page each. Every page opened before any number was read; every finding
verified against the PDF; 10 findings, 9 verified, 0 refuted, 1 unverifiable. Sixteen documents
pass, four do not.

### OPEN — the right column of a two-column page is 54 pt low

27_two_column_left_short_txtpos. `moved:Residents of the ward` verified: y=129.7 in the PDF,
y=183.4 in the render. The left column is right; the right column's whole block, from its first
paragraph through "Second phase of the scheme" and "By our correspondent", sits 54 pt lower and
about 27 pt further right. Reading order 70.0 % of 27 rows, 33 rows in the render against 27.
The two columns are being laid out as one flow with a gap, not as two measured columns.
**Tries: 0 of 3.**

### OPEN — a heading whose number and text share one baseline is split onto two lines

30_mixed_font_sizes_one_baseline_txtpos. `moved:Counselling and seat allotment` verified:
y=192.6 in the PDF, y=222.3 in the render. The page sets the 20 pt "01" and the 11 pt heading on
ONE baseline; the render puts the number on its own line and the heading under it, so every one
of the four numbered sections grows a line and the "Reporting date" that shared the heading's
line drops to a third. Reading order 69.4 % of 22 rows, 27 rows in the render. **Tries: 0 of 3.**

### OPEN — text drawn twice to fake bold is emitted twice

38_faux_bold_italic_synthesised. `count:Study of self-compacting concrete` verified: the PDF
draws the subtitle twice at the identical y=118.2, which is how this file synthesises bold. The
render joins both copies into one paragraph, so the subtitle reads
"Study of self-compacting concrete using quarry dust as partial replacement Study of
self-compacting concrete using" and wraps onto a second line. The cause is the glyph dedupe in
`PdfToWord.dedupe`: it looks back only 40 glyphs, and a 74-character doubled line puts the
second copy of each glyph 74 positions away, outside the window. Reading order 85.7 % of 17
rows, emphasis 2 of 7 lost.

**Tried and reverted (1 of 3).** The window was widened from 40 glyphs to a named
DUPLICATE_WINDOW of 400. It does exactly what it says: 38's subtitle comes out once and the
paragraph reads correctly. G2 across 208 documents rejected it - `missing` went 4 -> 14 on 38,
7 -> 8 on 39 and 0 -> 8 on text-held-twice-shadow-text. The reason is in the metric, not the
fix: `missing` compares word multisets, and on a faux-bold or shadow page the PDF's own text
layer holds the text twice, so the metric REWARDS copying the duplicate. A fix that makes the
page right cannot pass G2 until `missing` stops counting a doubled text layer as two words.
The change was reverted and the baseline left alone, as the ratchet requires. **Tries: 1 of 3.**

### OPEN — a letter-spaced heading loses its word spaces

39_small_caps_letter_spacing. The page sets its headings as per-glyph positioned text at a
1 pt nominal size with wide advances - the way a PDF fakes small caps and tracking. The render
carries the right characters but the spaces collapse: "THE MYSCORE CHAMBER OF COMMERCE AND
INDUSTRY" renders as "THEMYSCORECHAMBEROFCOMMERCEANDINDUSTRY" and "NOTICE TO MEMBERS" as
"NOTICETOMEMBERS". The paragraph's own text layer still has the spaces, so the loss is in the
advance, not the string. Reading order 86.5 % of 18 rows, 19 rows in the render.
`missing:NOTICE TO MEMBERS` came back UNVERIFIABLE because the page's text layer is spaced the
same way, so the claim is carried by the measured finding only. **Tries: 0 of 3.**

### Measurement blind spots found this pass - repair the tool, not the page

    order on 28_value_overflows_cell_txtpos   79.1 %, 20 rows in the PDF against 23 in the
        render. The eye passed the page and it is right: the page's description deliberately
        overruns its cell ("the amount in column 5 begins before the previous cell has ended,
        which is the failure mode this file tests"), so the row bands cannot pair. The extra
        rows are the overflow being cut where the page cut it.
    order on 40_devanagari_shaping_font       92.7 %, 20 against 21 rows. The eye passed it.
        Reading order pairs rows by text and the shaping pass gives the render a different
        string for a conjunct, so one row cannot pair.

Both were named by `looked.py --combine` as "eye (numbers wrong - repair the tool)" and both
documents stay PASS.

### A claim that could not be checked

    missing:NOTICE TO MEMBERS on 39   UNVERIFIABLE - "the PDF has no 'NOTICE TO MEMBERS'
        either", because the page writes the heading with letter spacing and its text layer
        reads the same collapsed way. The defect is real and the measured `order` finding on
        the same page is VERIFIED, so the document is not left on this claim.

### One PASS is worth a note

35_four_typefaces_one_page carries the header word "Secured" twice in the docx text layer (188
words in the PDF against 189) but the page renders one header row and the eye sees one. Not
recorded as a finding; noted so the final sweep re-checks it rather than re-reading it as new.

## v3 corpus — batch 5 (402-417), 8 Nov

Fourteen documents, all one page except 412 (five) and 417 (two); 416_many_tiny_pages is
300 pages and is worked separately below. Every page opened before any number was read; every finding verified
against the PDF; 17 findings, 14 verified, 2 refuted, 1 unverifiable. Six documents pass,
seven do not, one unlooked.

### FIXED this run: a table the page never ruled must not be drawn ruled

`DocxWriter` put the same six single-line borders on every `w:tbl` it wrote, whatever pass had
found the table. Two passes build tables and they are not the same claim: the ruled pass reads
edges the page actually draws, and the row pass infers cells from whitespace alone. On
403_crossword_puzzle the ACROSS and DOWN columns are two whitespace columns and the page draws
no line anywhere near them; the render boxed them, 11 rules against the page's 0. On
406_passport_mrz_page the field grid is the same story at 19 against 0.

`Table` now carries `ruled`, set false by `buildRowTable` and inherited by `keyValuePanels`.
`DocxWriter.borders()` writes the hairline when it is true and the same six slots as `w:none`
when it is not - "none" rather than an absent element, because an absent `w:tblBorders` falls
back to the table style and the default style draws exactly the box this removes.

Measured: 403 11 -> 0 rules, 406 19 -> 0, both findings REFUTED. 406's `moved:BENGALURU` fell
from 50.7 to 43.2 pt as a side effect, because the borders were charging each row height.
G2 across 208 documents: no document got worse. precommit.sh --all: every bench tool ran, the
engine compiles, TestPdfToWord 29/29, G2 clean.

### TOOL FIXED this run: the charts question could not see a filled bar

414_transparency_softmask draws a grey rectangle, a white one over exactly the same rect, then
the blue bar. The page shows one shape. Two separate faults in `visual.py` made the question
report "the PDF draws 3 shapes here and the docx draws none" about a bar that was in the right
place with the right fill, which the eye had already passed:

    `_is_rule`      LibreOffice exports a solid bar as four border lines, so the item-by-item
                    test called the render's bar a rule and threw it away. PyMuPDF hands the
                    PDF's own bar over as one filled rect, so only one side lost it.
    eraser          the grey rect is invisible under the white one, and both were counted.

A drawing with a fill and real extent in both directions is now a shape whatever it was written
down as, and an exact white cover drops both members of the pair. 414 now reads 1 against 1.
Unfilled outlines stay rules, which is what a page border is.

### OPEN — the calendar's rows are charged more height than the page gave them

402_calendar_month_grid, 1 page in and 2 out, order 72.0 % of 12 rows, 6 shapes in the PDF and
0 in the render. The month grid is a 7-row table whose annotations - "8 Holi", "18 Audit",
"25 Board meeting" - are the second line of a cell on the page. The render gives each cell more
height than the page did, so the table outgrows the sheet and an empty grid plus a stray footer
land on page 2, and "Board meeting" wraps to two lines inside its cell. Same class as the
short-table and tall-table entries from batch 2 and 3. **Tries: 0 of 3.**

### OPEN — the 3x3 box rules come out as hairlines

404_sudoku_grid. `rules` verified: 8 filled rules in the PDF against 20 in the render. The page
draws the 3x3 separators as thick filled rules and the other six as strokes; the writer gives
every cell edge the same `w:sz="6"` hairline, so the puzzle loses the only thing that makes it
a sudoku. The claim counts rules and the count does differ, so this is not the measurement
blind spot it first looked like - it is a border-weight that is not carried from the model.
**Tries: 0 of 3.**

### OPEN — the passport field grid loses its row pairing

406_passport_mrz_page. `moved:BENGALURU` verified at 43.2 pt: the page draws "Place of birth"
and "BENGALURU" as a label/value pair on one band, and the render leaves the Place of birth row
empty while BENGALURU moves down to the Place of issue row. "Sex" and its value "F" separate the
same way, F taking a line of its own. This is D-02/D-07 in a new document. **Tries: 0 of 3.**

### OPEN — every block sits about 61 pt above the page

410_form_xobject_reused. `moved:Invoice line item` verified: 3 on both sides, worst offset
62.2 pt, and the offset is uniform across all seven bands - three Form XObject blocks and the
note under them. A uniform lift of that size is the first-line rule, not per-paragraph spacing:
the model's own first baseline is not being used. Same family as D-01. **Tries: 0 of 3.**

### OPEN — the heading is emitted twice

411_nested_xobject_transforms. `count:NESTED FORM` verified: 1 in the PDF, 2 in the render. The
page holds one heading, then a nested form that is scaled 1.6x and rotated 90 degrees, whose own
content is two single characters ("S" and "O"). The render emits the heading a second time in
place of the rotated form's content. Reading order 57.1 % of 4 rows and one emphasised line lost
are the same defect seen from two other angles. **Tries: 0 of 3.**

### OPEN — the inline image is dropped

415_inline_images. `moved:The checkerboard above is an inline image` verified: the caption sits
at y=265.3 in the PDF and y=112.3 in the render, 153 pt high, exactly the height of the image it
has risen into. The page draws the checkerboard as an inline image (BI ... ID ... EI) and PyMuPDF
reports 0 images and 0 drawings for the page, so nothing in the image pass sees it. The caption
is the checkable half of the defect; the image is the cause. **Tries: 0 of 3.**

### OPEN — a mirrored page comes out as a garbled reversal

417_rotate180_and_mirrored. Page 1 is right - the page says /Rotate 180, the render is upright,
which is what ignoring the rotation should give. Page 2 is mirrored with a negative horizontal
scale and its text layer reads "Page 2 - mirrored text"; the render produces
"t xet der orri \tm" and " - 2 egaP", the string reversed with letters split and a tab inside it.
`missing:Page 2` verified 1 in the PDF against 0 in the render. **Tries: 0 of 3.**

### 416_many_tiny_pages — checked, and my own number was the wrong one

300 pages, one record each. Every page opened: all 300 match the page on their heading, their
serial/status/batch line and the 300-page note, and the render is 300 pages against the PDF's
300.

I measured a 4.32 pt first-line offset on all 300 pages and recorded a `moved:` claim on it.
The verifier refuted it: 'Record 001 of 300' sits at y=94.9 in the PDF and y=93.2 in the
render, 1.7 pt, inside the 3.0 pt tolerance. The 4.32 pt was the block's bbox top, which is the
tallest ascender in the line, not the baseline. **The document was right and my measurement was
wrong** - which is the whole reason step 11 exists, and it cost one round trip instead of a fix
applied to a page that was already correct.

### Refuted this pass - do not "fix" these

    rules on 403        0 in the PDF, 0 in the render, once the invented box was removed
    rules on 406        0 in the PDF, 0 in the render, same fix

### Unverifiable this pass

    wraps:Board meeting on 402   "could not follow 14 of 16 words through the render". The
                                 defect is real and is covered by the pagecount and order
                                 findings; the needle is a cell whose text the render splits,
                                 which is what the wraps check needs to follow. Not fixed.

### A stale row, found while checking this change did not cause it

304_package_insert_small_print is recorded PASS on 8 Nov and now fails `emphasis` - 6 of 9
emphasised lines lost their bold - on the current code. Checked against a pristine build of HEAD
in a separate worktree and it fails identically there, so this run did not cause it: the row was
written against an earlier build and the emphasis question has since moved. Any PASS row older
than the current code has to be re-taken before the final sweep counts it.

## v3 corpus — batch 3 (341-370), 8 Nov

Fifteen documents, one page each except 341 and 350. Every page opened before any number was
read; every finding verified against the PDF; 19 findings, 18 verified, 1 refuted, 0
unverifiable. Seven documents pass, eight do not.

### FIXED this run: a cell that cannot be widened still has to hold its value on one line

343_air_waybill sets "12" in the Pieces column. The column is 1120 twips and the page drew the
value 949 twips into it, so Word had 171 twips to set a 190-twip string in and broke it: "1" on
the row's baseline, "2" on the next. The row the page draws once arrived twice, and the whole
table below it moved - reading order 81.2 %, 17 rows against the PDF's 15.

The existing widening rule could not help: it widens a cell over the empty cells beside it, and
"1,144.0" is in the cell to its right. So the inset gives way instead, by the few twips that let
the text fit, capped at the cell's own left edge. `w:noWrap` was tried first because it says
exactly what the page did - keep the value whole and let it overrun - and LibreOffice ignores it
on a fixed-layout table, so it was reverted rather than committed.

Measured: 15 rows against the PDF's 15, reading order 81.2 -> 90.3 %. The cell's x moves from
67.60 to 65.60 against the page's 67.46, so that one line is 1.86 pt out on a 1.5 pt tolerance -
a value broken in half is the worse defect and this is the trade that was taken.

G2 across 208 documents: no document got worse. TestPdfToWord 29/29, TestRealDocs
96.8 / 97.0 / 81.7 unchanged. precommit.sh --all: every bench tool ran, the engine compiles,
G2 clean.

### TOOL FIXED this run: a claim type for rules, so a page with the wrong borders can fail

351_omr_answer_sheet draws its bubble grid as bare circles. The render put a ruled table round
it. Every claim in the vocabulary was about TEXT - `extra:` could only ask how many lines
contained a character - so the eye saw it and nothing could check it, which is the third of the
three causes PIPELINE.md names: the claim vocabulary is missing something. `rules` is now a
claim type: it counts thin filled rectangles on each side. 11 in the PDF, 32 in the render.
VERIFIED. The same gap left 380 and 383 PASS-with-a-note on 7 Nov.

### OPEN — the right column's dot leaders run past the margin and each price wraps

360_restaurant_menu. Reading order 61.5 % of 17 rows, and the render has 22. The PDF sets each
item, a leader and a right-aligned price inside a column. The render's tab stop for the price
sits beyond the column's right edge, so the price falls to the next line at the left margin:
420, 360, 390, 450 and one more all sit one row too low, each on the line of the item above.
`wraps:` cannot see it - the wrapped line carries no word from the PDF's line - and the measured
evidence is the row count, 17 against 22. **Tries: 0 of 3.**

### OPEN — the amount column is fragmented into three grid columns

365_recipe_card. `wraps:2 tbs` and `wraps:to taste` verified; "as needed" and "2 medium" stopped
wrapping once the inset fix above landed, so four of six are still broken. The table is emitted
with four grid columns - 3316, 398, 378, 128 - where the page draws two, and the amount cell is
a 506-twip span across two of the fragments. The column bands are being read from the leader
dots, not from the page's own two boxes. **Tries: 0 of 3.**

### OPEN — a page of numbered questions runs onto a second sheet

350_question_paper, 1 page in and 2 out, reading order 39.3 % of 52 rows. Each question is one
paragraph carrying a gap after it, so 60 rows are spent where the page spends 52 and the paper
grows a sheet. The row pitch is measurable - the page's own baselines - and is the same
"line height from the model" cause as D-01, seen on a paragraph that is not body text.
**Tries: 0 of 3.**

### OPEN — a manifest table spills onto a second sheet

341_shipping_manifest, 1 page in and 2 out. The second sheet holds an empty ruled grid and a
stray red footer: the table's rows are charged more height than the page gave them. Same class
as the entry above and as the short-table entry from batch 2, from the tall side.
**Tries: 0 of 3.**

### OPEN — a label/value band is emitted as separate rows

353_admit_card. `moved:DATE OF BIRTH` verified at 81.0 pt; reading order 63.0 % of 25 rows.
The page draws three label/value pairs on one band - REGISTER NUMBER, APPLICATION ID, then the
name, then DATE OF BIRTH - and the render gives each its own table row, so the block is nearly
three times as tall and everything under it moves. This is D-02 in a new document, and the
same shape as the four-column band on 322 and 323. **Tries: 0 of 3.**

### OPEN — the rotated sidebar label is gone

364_event_ticket. `missing:ADMIT ONE` verified: the PDF holds the line rotated 90 degrees at
x=560.7, 19.7 to 210.0; the render has a clipped "WAREHOU" at x=565 and nothing else. This is
the wall the rotated stamps hit - OOXML has no text rotation a LibreOffice render honours - and
it is the ONE try this class gets. Recorded, not retried. **Tries: 1 of 1.**

### MEASUREMENT — reading order on a page whose figures are drawn as shapes

352 (46.8 %), 363 (87.0 %) and 370 (93.1 %) all came back VERIFIED and all three passed on
sight. 363's 22 rows against 24 is the QR code's modules counted as rows; 370's 29 against 29 is
a band split inside a table; 352's 21 against 26 is the round seal, which the page draws one
character per baseline. This is the fourth to sixth sighting of the same measurement bug and the
eye decides. Recorded, not fixed. **Not a document defect.**

### Refuted this pass - do not "fix" these

    wraps:12 on 343       the verifier matched "ACC-447112" - a two-character needle is not a claim
    extra:1 on 351        "1" matched sixteen lines; the defect was real and the claim was wrong,
                          which is what produced the `rules` claim type above
    shapes on 370         1 shape in the PDF, 1 in the render

## v3 corpus — batch 1 (300-318), found this pass

These are new, from the document-type corpus. Recorded here so the final sweep works through
them along with the rest.

| Doc | Problem |
|---|---|
| **315_gazette_notification** | Three columns stack into one flow; the page reads down instead of across. Page count still 1/1. |
| **311_fir_police_form** | The address cell overruns its column in the PDF itself, so its tail lands in the next cell; row pitch compressed by ~31 pt median. |
| **314_tender_rfp_boq** | "8,39,69,600" renders as "8,39,69,60" — the last column is exactly as wide as the page's own text and the substituted face is wider. Needs a point or two of slack when a cell's drawn right edge sits on its text. |
| **300, 302, 306, 314** | Vertical drift 22-42 pt median — the same flow-determined spacing class as below. |

Fixed this pass and no longer open: the false table round prose on 316 (a rule's y was compared
in the wrong frame), and the interleaved cell text on 311 ("6M0o0b6i7le").


## v3 corpus — batch 3 (342-371), found this pass

| Doc | Problem |
|---|---|
| **350_question_paper** | 1 page in, 2 out: the MCQ block overflows. Pre-existing, unchanged by this pass. The .txt also fails TABLE CELLS and NO DUPLICATION. |
| **353_admit_card** | The label/value block is emitted as a four-column table with the labels as header cells and "Aadhaar ending 4471" in a row of its own; the page sets each label above its value in a two-column band. |
| **361_product_catalogue_grid** | Each card's text is drawn at the top of the card over its photograph instead of below it, and the second row of cards loses its text entirely. 108.4 pt median drift. |
| **364_event_ticket** | "WS24-4471-0082" is drawn twice on the page and appears once in the .docx. |
| **352_certificate_ornate_border, 371_experience_certificate** | .txt position 30.0 % and 36.4 %: rotated round seals whose text the page draws one character per baseline. A .txt has no rotation; body text on both is 100 %. |
| **343_air_waybill** | 28.8 pt median vertical drift, the flow-determined spacing class. |

Closed this pass: every document in all three corpora was re-converted and compared on page count,
words, images and tables — no document got worse. The size a glyph is set at is now read exactly
(it was rounded to a whole point), a table cell's exact line height is the row's own pitch instead
of a constant 10 pt, and a size that is not a whole half-point rounds down so a column that was
exactly wide enough does not start wrapping.

Everything here was found by rendering the .docx through LibreOffice and comparing it against the
source PDF page by page, in batches of 20 over the 80-document corpus. Each entry names the batch,
the document, what is wrong, and what was already tried.

Work through this only after the other corpora are processed.

---

## v3 corpus — batch 4 (372-394), found this pass

| Doc | Problem | Tries |
|---|---|---|
| **393_spectrum_peak_table, 394_map_with_legend, 382_architecture_diagram** | Text drawn under a drawing lands too high: the table under 393's chart by 141.6 pt, 394's legend by 227.1 pt, 382's first label by 77 pt. A chart, a map's roads and a diagram's boxes are anchored shapes — they draw where the page drew them and take **no room in the flow** — so the text beneath them closes the gap they left. The gap ceiling is now 120 pt instead of 72 pt, which fixed 393 and 394's row order; 382's first gap is 212 pt and is still lost. | 1 of 3 — see the anchor attempt below |
| **The flow-anchor attempt (all three, above)** | Placing every flowed line at its own measured y instead of one pitch below the line before it. Measured over 208 documents: **0 documents worse on G2**, and 380 goes to 100 % of lines in tolerance, 394 to 93.3 %, 392 to 95.2 %, 382 to 72.4 %. But 390_wide_data_appendix fell from 57.8 % to 0.5 % and 373 and 390 both went from one page to two, because a table's real height exceeds the model's, so a target y adds that error a second time. A hybrid (anchor only until a table has been through the page) gave 11.6 % and left 390 at 0.5 %. **Blocked on the table height below** — not on the idea. | 2 of 3 used |
| **Table height (the blocker above)** | Rows are emitted `w:trHeight hRule="atLeast"`, so a cell whose text wraps grows the row and the table is taller than `t.bottom - t.top`. On 373 two tables are short by ~186 pt in the flow's accounting; on 375 (459 lines, all in one table) only 0.4 % of lines land within tolerance, on 390 57.8 %. Until the model's table height matches the render's, no absolute-y placement can be trusted after a table. | 1 of 3 |
| **373_leave_application_form** | The page draws "Employee signature \| Manager signature \| HR use" as ONE row; the .docx has it as two paragraphs 3 pt apart, because the model splits the line into two paragraphs at the wide x gap and Word cannot put two paragraphs on one line. Merging them in the writer would be the fix, but it lowers the leaf-paragraph count that G2 reads as "lines", which the gate defines as a regression. Also fails G3 reflow (fails identically on the pre-change build — pre-existing, not caused here). | 1 of 3 |
| **375_attendance_register, 390_wide_data_appendix** | Row pitch: a 13-19 row table is taller in the render than on the page, so every row after the first drifts. Same root as the table height entry above. | 0 of 3 |

Fixed this pass and no longer open: 393 and 394's reading order (the 120 pt gap ceiling), and the
three `visual.py` measurement bugs that had been reporting defects that were not there — line-index
pairing in question 1, box-top instead of baseline for grouping a row, and U+0000 from a soft hyphen
kept on one side of the comparison only.

## v3 corpus — batch 2 (318-340), 8 Nov

### FIXED this run: a page with a table kept the 120 pt gap clamp

`DocxWriter.pageFits` returned `false` the moment a page held a table, so every table page
gave up its white space. On 318 the page's own gap between its last box and its footer is
480 pt and the clamp put that footer 337.6 pt too high. The same clamp lifted the signature
and footer blocks on 320 (215.1 pt), 325 (306.5), 326 (175.6), 333 (167.5) and 340 (293.1).

A table is now charged its model height, the spacer above it and the 4 pt paragraph after
it, and the page spends its gaps only when the arithmetic still fits the sheet with 12 pt of
slack for a table whose rows grow. Where it does not fit, the clamped gaps stay.

Measured: G2 across 208 documents, no document got worse. TestPdfToWord 29/29, TestRealDocs
96.8 / 97.0 / 81.7 unchanged. 326, 333 and 340's footers now land within 2.4 pt of the PDF.

### OPEN — a table renders shorter than the model's own extent: 7.8 to 9.4 pt

318, 320, 325. Everything below the table shifts by one constant: on 318 the SERVICE box,
TAKE NOTICE and the footer are all exactly 7.8 pt high. The render's table is 7.8 pt shorter
than `t.bottom - t.top`, so the gap the flow now spends starts from the wrong place.

Rows are emitted `w:trHeight hRule="atLeast"` at the row's own pitch, cell margins are 0,
so the difference is in how the renderer sizes a row against the pitch the PDF drew. This is
the same "Table height" entry as the batch-4 blocker, seen from the other side (short rather
than tall). **Tries: 1 of 3.**

### OPEN — the four-column header band splits into two rows

322 (`moved:EXPENSE RATIO` 34.9 pt) and 323 (`moved:CREDIT LIMIT` 32.4 pt). The page draws
four label/value pairs as one band: labels on one baseline, values 10 pt below. The model
puts columns 1-2 on the first row and columns 3-4 on the second, so the table starts a row
early and everything under it moves. D-02 in a new document. **Tries: 0 of 3.**

### OPEN — a drawing page overflows to a second sheet

330 and 332, both 1 page in and 2 out. The overflow is the drawing itself, not the text: the
dimension lines, the north arrow and the assembly outline are anchored shapes that take no
room in the flow, and 332's bill-of-materials table follows them onto sheet 2. The page-count
check catches it, nothing in the model predicts it. **Tries: 0 of 3.**

### G3 STRUCTURE — 318 puts its seal's text in 31 text boxes

`reflow.py` fails 318_court_summons_form: 31 text boxes, and body text inside one cannot be
edited or reflowed. The text is the round court seal, which the page draws one character per
baseline round a circle. Identical count before and after this run's engine change (62
`txbxContent` tags either side), so it is pre-existing and not caused here. A .docx has no
rotated text, which is the same wall the rotated stamps hit. **Tries: 0 of 3.**

### MEASUREMENT — reading order on a drawing or a figure page

331 (93.3 %) and 334 (89.7 %) both came back VERIFIED and both were passed on sight: the
rows are the same rows, drawn at the same x, and the sequence differs only inside a figure.
This is the third sighting of the same measurement bug (312 was the first). The eye decides,
and the disagreement is recorded rather than fixed. **Not a document defect.**

## A. Multi-column pages still overflow to a second sheet — 3 documents

Fixed this pass: 63, 67, 78, 80 and 55 now render 1 page against 1 (they were 2). Sections now carry
`w:cols w:num` from the engine's own column bands, with a section break when the column count
changes. These three did not follow:

| Doc | Batch | Problem |
|---|---|---|
| **64_newspaper_uneven_columns_ad_boxes** | 4 | Uneven columns plus three ad boxes; still 2 pages. The ad boxes are drawn but stack below the body. |
| **65_two_col_full_width_figure_caption** | 4 | A full-width figure spanning both columns; the chart renders but the spanning band is not modelled, so the flow breaks into two pages. |
| **77_arabic_rtl_document** | 4 | The description column collapses to a sliver: `colX` is [57,152,246,340,434,528] while `cellR` for the description column reports 428.2, so the writer wraps the cell into a 17 pt column. RTL column widths are not honoured. |

## B. Table geometry — 3 documents

| Doc | Batch | Problem |
|---|---|---|
| **75_merged_header_cell_three_columns** | 4 | The first data row welds into the header ("Services1,842"). The page's sub-header rule at y=143 spans only part of the width, so no band boundary is found and header + value land in one cell. |
| **80_gstin_pan_cin_ifsc_table** | 4 | The four-column dealer grid collapses to two panels. Page count is now correct; the panel split is not. |
| **28_value_overflows_cell** | 2 | A value wider than its column is handled, but not with the page's own overflow behaviour. |

## C. Vertical position — every document, small offsets

Horizontal position is 0.1 pt everywhere, measured by rendering both sides and matching lines by
text. Vertical is not: 93 % of lines land within 10 pt on 21 and 79, 59 % on 01, and lower on the
table-heavy documents.

Causes still open:
- **Table TOP y** is flow-determined, not the PDF's y. Rows are the right height but the table can
  start a little high or low, moving everything below it.
- **Table row pitch** is slightly compact against the page on several invoices.
- **Page-anchored shapes drift** against the more compact text flow — 48's green border box starts
  below "Father's/husband's name" and its bottom edge cuts through "K. Ramesh, Clerk"; 79's rules
  and pink header band no longer line up with the rows.
- **Stamps sit a few points off** their PDF position. A rotated box cannot carry a rotation that
  LibreOffice honours (`a:xfrm rot` is ignored, `wps:bodyPr vert` lays Latin out one character per
  row), so the box is axis-aligned at the line's origin.

## D. Individual documents

| Doc | Batch | Problem |
|---|---|---|
| **30_mixed_font_sizes_one_baseline** | 2 | Renders 2 pages against 1. Its flow is longer than the sheet. |
| **26_footnote_marker_bottom_note** | 2 | The footnote marker's position relative to its note is close but not exact. |
| **52_one_cm_margin_wide_body** | 3 | The body does not justify across the full 28.3 pt margin the page uses. |
| **58_header_rule_footer_rule** | 3 | The rules render but do not sit exactly on the page's y. |
| **59_landscape_mixed_portrait** | 3 | The section break survives and the page is landscape, but the content is slightly compact. |
| **03_stamp_vertical_90deg** | 1 | LibreOffice truncates the 90-degree rotated stamp boxes in the render. |

---

## What is NOT on this list, and should not come back

Verified across all 80 documents:
- no black page — every .docx declares `<w:background w:color="FFFFFF"/>`
- no lost text — the gate reports 0 missing across the corpus for the batches it covers
- no missing image — every PDF page that draws an image has it in `word/media/`
- no scrambled layout — body text flows as real paragraphs, tables are real `w:tbl`
- no floating text boxes except for genuinely rotated lines
- no heading autospacing stacking on explicit spacing
- no `w:trHeight` missing, so tables no longer collapse to text height

---

## v3 corpus — batch 2 (320-341), found this pass

Worked with the same method as batch 1: convert, render both sides at 130 dpi, put PDF page and
DOCX page side by side, and measure. Page counts are 15/15 correct and .txt position is 78.8 % or
better everywhere, so what is left is content and drawing fidelity, not layout collapse.

| Doc | Problem | Why it is not fixed yet |
|---|---|---|
| **323_credit_card_statement** | The right-hand **SPEND BY CATEGORY** panel loses its whole label column — "Travel", "Shopping", "Fuel", "Groceries", "Health" are in the PDF and in neither the .docx nor the .txt. Only "Other" survives, and the six amounts come through as loose paragraphs at x≈474 rather than as a table. Word recall 96.9 %, the only .txt check that fails in the batch. | The two summary panels are side by side and overlap vertically (REWARDS SUMMARY x 28-228 y 301-354, SPEND BY CATEGORY x 250-490 y 300-372). The rewards panel is found as a table; the labels at x=250 are 22 pt beyond its right edge, so `Line.inside()` — which tests the line's CENTRE against `t.right + 2` — does not claim them, yet they reach no block at all. The values at x=474 do survive. Needs a trace through the candidate-table passes on this one page. |
| **323_credit_card_statement** | The header block is broken: "CREDIT LIMIT / Rs. 5,00,000 / AVAILABLE / Rs. 4,12,180" is turned into a table with two empty rows and pushed 28-32 pt down, and "Rs. 42,318.40" wraps onto a second line. | Same page, different pass: four short label/value pairs on two baselines read as a table. |
| **322_mutual_fund_factsheet** | "EXPENSE RATIO", "FUND MANAGER", "A. Bose (since 2019)", "PORTFOLIO HOLDINGS (TOP 10)" and "SECTOR ALLOCATION" are swallowed as table rows with empty cells; the scheme-performance table absorbs the holdings table and its rows misalign. | Headings above and beside a table are being claimed by the table's band. This is the batch's most repeated defect and deserves its own pass. |
| **322_mutual_fund_factsheet** | The **riskometer** — the circular gauge with its needle — is absent. Only the scattered labels "Low", "Moderately low", "Moderate", "High", "very high risk" remain, at the wrong y. | **CLOSED 6 Nov** — ring and needle both draw; the needle is a freeform, not its box. The panel's labels are still absorbed by the table pass (separate entry above). |
| **330_cad_drawing_sheet** | The hatched floor area renders as a **solid black rectangle**, and the circled "(A)" revision marker becomes a black blob. | **CLOSED 6 Nov** — the hatch is drawn as its own strokes and the north arrow as its own triangle, via `a:custGeom`. |
| **331_pid_diagram** | The legend's four symbol icons and the circled "P" markers on the drawing are missing; only the text labels survive. | **CLOSED 6 Nov** — rings, pump triangles and gate-valve bowties all draw as freeforms. |
| **335_msds_safety_data_sheet** | The three GHS hazard **pictograms** (red diamonds) are reduced to faint red fragments. | **CLOSED 6 Nov** — four red diamonds, drawn as the rotated squares they are, at the page's own colour C00000 and 1.6 pt stroke. |
| **324_loan_amortisation_schedule** | Column widths are an even split: "Month" is about 78 pt where the page drew it 31 pt, and every amount column is correspondingly narrow. Rows, row pitch and page count are otherwise exact. | The row-based table pass found these tables but left `colX` null, so the writer fell back to even columns. The values are right; only the column edges are missing. |
| **320_balance_sheet_statutory** | "Note 12 - Revenue from operations", the notes table's header row, comes out as a paragraph above the table instead of its first row; the amount column is shifted. | Header-row band boundary, same family as 75_merged_header_cell. |

### The one class worth real work: vector graphics

Four of the eight entries above are one thing. The engine carries raster images correctly — every
PDF page that draws an image has it in `word/media/`, and 340's barcode, 323's barcode and 326's QR
codes all render. What it does not carry is a **path**: a shape drawn with fills and strokes rather
than a bitmap. Three distinct failures, all visible in this batch:

1. a filled path with a pattern (330's hatch) is emitted as solid black
2. a stroke-only path (331's legend icons, 322's riskometer circle and needle) is dropped entirely
3. a path with a non-black fill and a thin outline (335's red diamonds) survives only partially

That is a rendering change in `PdfEngine`, not `DocxWriter`, and it is worth more than any single
document on this list. It should be taken as its own task, with a before/after on 322, 330, 331 and
335 plus a whole-corpus gate, because a shape pass that goes wrong is how a page turns black.

#### Sub-class 2 (stroke-only circles) and the filled-circle half of 1 — FIXED 6 Nov

A page draws a circle or an ellipse as four Bezier curves that close on themselves. Its bounding
box is a square, so the writer put a solid square where a ring belongs, and a stroke-only circle —
being neither a rectangle nor a single line — was dropped before it ever reached the writer.

`RuleCollector.pathIsEllipse()` now recognises that path (one move, four curves, no lines, no
rects, ends on its start point, both extents over 2 pt) and `DocxWriter.Shape.kind` selects
`prst="ellipse"` instead of `prst="rect"`. The extent needs no correction: a quarter arc's control
points sit exactly on the ellipse's extremes, so the box is already right and only the outline
drawn inside it changes.

Measured over all 208 documents, old engine against new, on page count, words present, images and
tables: **0 documents worse on any of the four, 17 documents improved.**

| Doc | Before | After |
|---|---|---|
| **351_omr_answer_sheet** | 320 bubble outlines dropped, 29 filled bubbles were black squares | **349 ellipses drawn**, bubbles read as bubbles |
| **331_pid_diagram** | legend symbols, instrument circles and pump circles absent | **7 ellipses**, the legend and both instrument loops read |
| **405_sheet_music_lyrics** | 54 note heads were 6x4 pt black rectangles | 54 ellipses |
| **360_restaurant_menu** | 20 dietary markers were squares | 20 ellipses |
| **65_two_col_full_width_figure_caption** | 20 chart markers were squares | 20 ellipses |
| **330_cad_drawing_sheet** | the compass was a free-standing black slab | the ring is drawn; the arrow inside is still its box |
| **322_mutual_fund_factsheet** | riskometer ring absent | ring drawn |
| 05, 60, 305, 312, 318, 332, 352, 371, 394, 400 | rings absent or boxed | rings drawn |

Page count was re-rendered through LibreOffice for all 17 and is unchanged on every one.
`TestPdfToWord` 29/29, `TestRealDocs` 96.8 / 97.0 / 81.7 — identical to the decimal.

#### Still open in this class — nothing

**Closed 6 Nov, all of it.** `a:custGeom` now carries every path that is neither an axis-aligned
rectangle nor an ellipse: filled polygons (330's north arrow, 331's pump triangles), stroked
polygons (331's gate-valve bowties, 400's bubble tails), angled one-line strokes (330's hatch),
curves (394's river and highways) and rotated squares (335's four GHS diamonds, drawn under a
45-degree matrix and kept because a freeform's points are already through the matrix).
Measured across all 208 documents: 0 worse on page count, words, images or tables; 23 changed, all
gaining drawn shapes; `.txt` byte-identical.


---

## OPEN - found by the position and visual gates, 7 Nov

These two were invisible to every count-based gate. `gate.py` reported "no document
got worse" on all 208 documents while both were present. They are the reason G5 and
G6 exist.

### D-01  Vertical drift: every line sits higher than the PDF drew it — FIXED 7 Nov

**Severity: affects most documents. This is the biggest single defect in the corpus.**

Measured on `303_discharge_summary`, PDF page 1 against the rendered docx:

| Line | PDF y | DOCX y | Delta |
|------|-------|--------|-------|
| DISCHARGE SUMMARY | 12.12 | 8.60 | -3.52 |
| Shriram Multispeciality Hospital | 27.30 | 22.90 | -4.40 |
| PATIENT | 63.92 | 57.60 | -6.32 |
| ANANYA RAO, 34/F | 73.78 | 68.10 | -5.68 |

**Root cause, already located.** `DocxWriter.java:70` sets `LINE_FACTOR = 1.15` and
line 669 writes `w:line = size * LINE_FACTOR` with `lineRule="exact"`. The page has
zero margins (`pgMar top="0"`), so the first line starts at whatever the line box
gives it.

The PDF's own pitch on this document is 15.18 pt for 13 pt text - a ratio of **1.168**,
not 1.15. The docx therefore sets each line 0.23 pt too short, and because
`lineRule="exact"` stacks those short boxes, the error accumulates down the page:
3.5 pt at the first line, 6.3 pt by the fourth paragraph.

**The fix to try.** The model already carries the truth: `Para.lineY` holds each
line's real y, and `Para.lineSize` its size. The pitch is therefore *measurable* per
line pair and does not need a constant at all. Set `w:line` from the measured gap
between this line and the previous one, falling back to `size * LINE_FACTOR` only when
there is no previous line on the page.

**Why this is not a one-line change.** `LINE_FACTOR` touches every document, so it
must go through G2 across all 208 before anything is kept, and G5 must be re-measured
afterwards to prove the drift actually fell. A previous attempt to move the constant
"did nothing" - that is expected, because a constant cannot match a document whose
pitch is 1.168 while another's is 1.20. It has to be measured, not tuned.

**Tries: 1 of 3 - see the measurement below.**

### D-01 as measured on 7 Nov: the line box is the page's own pitch

**What the renderer actually does.** A one-paragraph probe with zero margins was rendered
through LibreOffice at nine box heights (9.2 to 37 pt) and four faces (Liberation Sans and
Serif, DejaVu Sans and Serif), including one box shorter than its own em. In every case
`boxHeight - baselineY` came to 0.2 of the box, within the 0.05 pt the render quantises to.
The baseline sits at 0.8 of an exact-height box, whatever the font and whatever the size.
So the advance from one baseline to the next is

    (1 - 0.8) * previous box + 0.8 * this box + spacing-before

and a baseline is placed by choosing the box, not by tuning a constant.

**The change** (`DocxWriter.flowFromBox`, `flowRow`, and the `LINE_BASE` constant). The box
is solved from that equation using the pitch the model already carries - `b.y` minus the
previous baseline - floored at the font size, because a box shorter than the em clips the
glyphs, and capped at the font's own line box, because a box taller than that spends slack
the next line has to pay for (a 37 pt gap above a form row became a 37 pt box, and the next
row then landed 5.2 pt low). Whatever the box cannot hold goes to spacing-before, still
capped at 120 pt. The first line of a page is lifted by 0.8 of its box instead of by a whole
box, and after a table the previous box counts as zero, because a table's bottom edge is not
a baseline.

**Measured across all 208 documents.**

| Measure | Before | After |
|---|---|---|
| lines within tolerance (G5) | 11.7 % | **26.3 %** |
| documents improved / worse on G5 | - | **157 / 15** |
| G2 words, blocks, page fill, overflow | - | **no document got worse** |
| documents spilling onto an extra page | 28 | 30 |
| TestPdfToWord / TestRealDocs | 29/29, 96.8 / 97.0 / 81.7 | identical |

**The fifteen that got worse are one class, not fifteen.** Thirteen of them contain a table
and two are two-column pages: 390_wide_data_appendix, 23_timetable_grid_txtpos,
72_bank_statement_no_rules_right_amounts, 330_cad_drawing_sheet,
38_faux_bold_italic_synthesised, 40_devanagari_shaping_font,
academic-paper-ieee-2col-abstract, balance-sheet-and-profit-loss, 13_stamp_non_english,
annual-review-2col-uneven-columns, 325_demat_holdings_statement, 362_price_list_dense,
333_datasheet_spec_tables, journal-2col-with-footnotes, magazine-2col-pullquote-spanning.
The text is now exactly on the page's own baselines; what is left is the table height below,
which under-measures a table whose rows grow, so everything after a table starts from the
wrong y - and the old, slightly-too-tall flow was accidentally compensating for it.

**Therefore the position baseline is not re-recorded on this run.** `base208-position.json`
still holds the pre-change numbers, so those fifteen show up as debt on every G5 run rather
than being baked into the ratchet. Re-record it when the table height is right.

**Also tried and reverted.** Charging the pre-table spacer as
`(t.top - baseline) - 0.2 * previous box` - the same rule the flow now uses - put 390's
table 10.6 pt low instead of 3.7 pt, because a table's first row does not begin where the
spacer paragraph ends. Reverted; the table's own top y stays open below.

#### What the fix was, and how it is known to have worked

`LINE_FACTOR = 1.15` was replaced by the page's own pitch: each flowing line's line box is
the gap the model measured between that line and the one above it, so the line sits on the
baseline the PDF drew rather than a constant fraction above it. Committed as "place every
flowing line on the page's own measured pitch".

The proof is D-06, which had the same cause. Measured on 8 Nov across all 208 documents:

    same page count as the PDF : 208
    spill (extra pages)        :   0
    short (missing pages)      :   0

Before this fix, 28 documents produced a page the PDF did not have, because every line was
slightly too tall and the error accumulated down the page until the last lines fell onto a
second sheet. All 28 are now correct. That is a whole-corpus consequence of one line height,
so it is the strongest evidence available without a device.

`Tries: 1 of 3` in this entry is therefore out of date - it was fixed on the first attempt.

### D-02  Row grouping: cells from different rows merged onto one line

**Severity: affects tables where row baselines differ by a few points.**

Measured on `303_discharge_summary`, PDF page 1 against the rendered docx:

    PDF   PATIENT    y=63.92  |  WARD / BED  y=64.68     <- two cells, one visual row
          ANANYA RAO y=73.78  |  Medical ICU y=73.54     <- two cells, next row

    DOCX  PATIENT    y=57.60  |  WARD / BED  y=57.60  |  CONSULTANT y=60.80
          Medical ICU y=68.10                            <- ANANYA RAO is gone from here

The PDF keeps the cells in two rows because their baselines differ by 0.76 pt. The
docx put three cells on one row - the third cell's baseline is 2.9 pt away from the
other two and was treated as the same row - and the value cell that should sit beside
`ANANYA RAO` ended up somewhere else.

**The fix to try.** The row tolerance in `buildTables` decides this, and it is
currently wide enough to swallow a 2.9 pt difference. It should come from the table's
own measured row pitch (the median gap between row baselines in that table), not from
a constant, so a table set tight and a table set loose each get the tolerance they
actually use.

**Tries: 0 of 3.**

### How to verify either fix

    python3 tools/p2w-bench/gate.py --corpus DIR --out DIR --baseline tools/p2w-bench/base208.json --check
    python3 tools/p2w-bench/position.py --corpus DIR --out DIR --verbose
    python3 tools/p2w-bench/visual.py --corpus DIR --out DIR

G2 must pass across all 208 first. Then G5's "lines within tolerance" must rise and
G6's reading-order share must rise. A fix that passes G2 but does not move G5 or G6
has not fixed either of these.


### D-03  Reading order: every label first, then every value

**Severity: affects the documents the visual gate measured, 3 of 3.**

Measured on `301_lab_report_panel`, PDF page 1 against the rendered docx:

    PDF   metropolis pathology lab
          nabl accredited | lab id mh-4471 | report no. mpl/2024/0318/
          patient
          ananya rao
          age / sex
          34 / female
          referred by
          dr. meera krishnan

    DOCX  metropolis pathology lab
          nabl accredited | lab id mh-4471 | report no. mpl/2024/0318/
          patient
          age / sex
          referred by
          collected
          34 / female
          dr. meera krishnan

The PDF reads label, value, label, value. The docx reads every label, then every value.
Every word is present and at the right coordinates; only the sequence is wrong, which is
why no count-based gate can see it and why `visual.py` question 1 exists.

**The fix to try.** The paragraph order in the body follows the block order in
`Page.blocks`. If the page groups a form's labels before its values, that order is
inherited. The order should come from the page's own reading order - the same
top-to-bottom, left-to-right sequence a reader follows - sorted by the row's baseline
and then by x within a row, which is what `visual.py`'s `_rows()` already computes.

**Tries: 0 of 3.**



### Correction, 7 Nov — the note below was wrong and is withdrawn

I wrote the note below after reading the PDF's lines sorted by raw y, and concluded that
88.5 % on 303_discharge_summary was a false alarm because the PDF's own order put the
patient's name last. That was wrong: `_rows()` does not sort by raw y. It groups lines
into bands and sorts left to right inside a band, so the PDF's rows are already:

    row 1  'PATIENT'  'WARD / BED'  'CONSULTANT'
    row 2  'ANANYA RAO, 34/F'  'Medical ICU-2 / 07'  'Dr. Meera Krishnan'

which is the correct reading order, with the patient's name where it belongs. So the
88.5 % is a real finding: the docx's row order genuinely differs from a reading order the
PDF already has. It is not ambiguous and it is not a false alarm.

The lesson is the one this whole check is about: a finding is verified against the code
that produced it, not against a hand re-derivation that skips that code.

The note below is kept only so the mistake is on the record.

### A note added 7 Nov, after checking the findings against the PDF

The reading-order question compares the docx's row sequence with the PDF's. On a form
with side-by-side fields the PDF's own y order is not the reading order, and the
comparison then penalises a docx that reads the page better than the PDF draws it.

303_discharge_summary, page 1, sorted by y as the PDF holds it:

    y=63.9  x= 28   'PATIENT'
    y=64.7  x=230   'WARD / BED'
    y=64.7  x=380   'CONSULTANT'
    y=73.5  x=230   'Medical ICU-2 / 07'
    y=73.5  x=380   'Dr. Meera Krishnan'
    y=73.8  x= 28   'ANANYA RAO, 34/F'      <- the patient's name, last

`ANANYA RAO` belongs beside `PATIENT`, and a reader would put it there. A docx that
does is scored as out of sequence against a PDF whose raw order is the wrong one. The
88.5 % on that document is therefore not evidence of a defect - it may be evidence of
a better document.

Do not "fix" this by making the docx copy the PDF's y order; that would be worse for a
reader. The question needs to compare against a reading order derived from the page -
fields grouped by band and read left to right within a band - rather than against the
order the PDF happens to store its lines in.

Until then, a reading-order failure on a form or a table page is a question, not a
verdict: open the image and look before recording it as a defect.

### D-04  Body text inside text boxes

**Severity: 2 of the 8 documents the structure gate measured.**

    FAIL 305_vaccination_certificate   48 text boxes
    FAIL 312_affidavit_stamp_paper     27 text boxes

`reflow.py` reports the count. Body text in a text box cannot be edited or reflowed,
and a document built that way measures perfectly while not being a Word document.

The other six documents in that run report zero text boxes and are not affected, so
this is not a whole-corpus problem - it is these documents and any like them.

**The fix to try.** Find what makes these two take the text-box path and give them the
flowing-paragraph path the other six already use. Do not ban text boxes: a watermark or
a sidebar legitimately uses one, and the gate says which document and how many so the
two cases can be told apart.

**Tries: 0 of 3.**


### D-05  The blocks count compares two populations that are not the same thing

**Severity: a measurement defect, not a document defect. It makes one of the seven
G2 numbers untrustworthy.**

`gate.py` scores `blocks` as `big_shapes(docx) - pdf_fills(pdf)`.

    big_shapes   counts solid fills inside wps:wsp shapes in the docx XML
    pdf_fills    counts filled areas from PyMuPDF's get_drawings() in the PDF

Those are not the same population. The writer emits a docx shape for every fill the PDF
draws, and also for things the PDF does not express as a drawing - a table cell
background, a paragraph shading, a shape whose fill comes from a style. So the
difference is positive on almost every document and means nothing.

The 3000 pt2 floor in both functions was hiding this: it dropped the small fills on both
sides, which by luck left the two counts close enough that the difference stayed at 0 on
the corpus. On 7 Nov I removed the floor while replacing the hard-coded 580x820 A4 with
the page's own size, and 179 documents went from blocks 0 to blocks N. The floor was not
protecting anything real - it was masking a metric that does not measure what it claims.

**Do not fix this by tuning the floor.** The fix is to stop counting and start matching:
for each filled region the docx draws, ask whether the PDF drew a filled region at the
same place with the same colour, which is a positional comparison like G5's, and report
how many docx fills have no partner in the PDF. That is a real number, and 0 is the only
correct value.

Until then the floor stays where it was, because a metric that is understood to be weak
is better than a metric that fires on 179 documents for a reason nobody can act on.

**Tries: 0 of 3.**


#### D-05 status on 8 Nov — still a measurement defect, not a document defect

The `blocks` count compares two populations that are not the same thing, and it reads 0 on all
208 because of it. Nothing about a document is wrong when this number looks wrong; the number
is. It stays open as a measurement defect and must not be "fixed" by changing a document.

### D-06  Twenty-eight documents spill onto more pages than the PDF has — FIXED 8 Nov

**FIXED. Measured 8 Nov across all 208: every document's page count now equals its PDF's.**

    same page count : 208
    spill (extra)   :   0
    short (missing) :   0

The fix was the one this entry asked for and it landed as D-01: the line height comes from
the model's own lineY gaps instead of a constant. It was committed as "place every flowing
line on the page's own measured pitch". Nothing was shrunk to fit - the content is the same
size it was, and the page simply ends where the paper does.

The numbers below are what this entry said before that fix, kept because they are the reason
it was worth doing.

**Severity: a page the PDF does not have is the first thing a reader notices.**

Measured with `position.py` on 7 Nov, comparing the docx render's page count with the
PDF's:

    64_newspaper_uneven_columns_ad_boxes    docx 5 pages, PDF 1
    350_question_paper                      docx 2 pages, PDF 1
    63_three_column_brochure                docx 2 pages, PDF 1
    20_numbered_list_separate_column_txtpos docx 2 pages, PDF 1
    332_bom_on_drawing                      docx 2 pages, PDF 1
    402_calendar_month_grid                 docx 2 pages, PDF 1
    55_sidebar_box_beside_body              docx 2 pages, PDF 1
    65_two_col_full_width_figure_caption    docx 2 pages, PDF 1

28 of the 208 documents failed this way before the fix. `gate.py` counts page breaks it finds in the
XML and reported 537 against the PDFs' 540, so three documents lost a page while these
28 gained one - the two errors were hiding each other in the total.

**That 537-vs-540 gap is itself a counting artifact, found on 8 Nov.** A section break written
as `<w:type w:val="nextPage"/>` starts a new page in Word and `gate.py` counts only
`<w:br w:type="page"/>`. Counting both gives 208 documents matching their PDF's page count
exactly, 0 spill and 0 short. Anyone reading "537 against 540" as three lost pages is reading
the artifact, not the documents.

The cause is the same one behind D-01: the writer gives every paragraph an exact line
height of size x 1.15 and a spacing-before taken from the measured gap. Both are close
but neither is the page's real pitch, so the content is slightly taller than the page
and the last few lines fall onto a second sheet. On 64_newspaper it is four extra
sheets.

**The fix to try.** The same one as D-01: take the line height from the model's own
lineY gaps instead of a constant, and let the page's real bottom margin decide where
the page ends. Do not shrink the content to fit - the page count is a measurement, and
the only correct number is the PDF's.

**Tries: 1 of 3.** The pitch fix above was the fix this entry asked for, and it did not
move the count: 28 documents spilled before it and 30 after, two of them new
(330_cad_drawing_sheet and journal-2col-with-footnotes, both an EMPTY second page - the
overflow is a few points, not a page's worth). Because the text now sits on the page's own
baselines, the remaining overflow is not the text's height any more: it is the table height
(rows are `atLeast`, so a wrapping cell grows the row and the model's `t.bottom` is short),
the trailing 4 pt placeholder paragraph after a table, and where a multi-column section
breaks its columns. Measured on the two new spills: 330's page 1 ends at 592.0 pt on a 595 pt
sheet, journal-2col's at 840.1 on 842, and neither has any text on page 2.


#### Verified on 8 Nov — the eight that were still listed as spilling

These were re-converted and measured: all eight now produce one page where the PDF has one.

    330_cad_drawing_sheet              2 -> 1  ✅
    332_bom_on_drawing                 2 -> 1  ✅
    341_shipping_manifest              2 -> 1  ✅
    350_question_paper                 2 -> 1  ✅
    402_calendar_month_grid            2 -> 1  ✅
    bus-timetable-station-left-right   2 -> 1  ✅
    303_discharge_summary              ok      ✅
    56_table_indented_from_margin      ok      ✅

Their FAIL rows in VISUAL-SCORE.md still carry the old pagecount reason. The page count is
no longer the reason any of them fails - what remains is listed there beside it (order,
breaks, shapes, cell width), and those are MEDIUM and HARD work, not this entry.

### D-07  Two fields on one baseline are joined into one sentence

**Severity: a marks column or a right-aligned label becomes part of the sentence beside it.**

Found on 350_question_paper, which came out as `[08] Write SQL queries for the following`,
the marks column in front of the question it belongs to. The PDF has them on one baseline:

    'Write SQL queries for the following: ...'   x= 50.0  y=147.5  x1=493.5
    '[08]'                                       x=551.9  y=148.9

and on form16-part-b:

    'Certificate under section 203 ...'          x=144.3  y= 44.0  x1=451.0
    'PART B'                                     x=519.3  y= 43.5  x1=552.8

**Two separate causes, both confirmed by running the engine.**

1. THE GAP TEST ONLY SEES A POSITIVE GAP. A baseline cluster does not hold its glyphs in
   x order, so `[08]` arrives before `Write`, the gap between them reads -520, and
   `gapPts > outlier` is false. The comment above that line has said "a gap counts however
   it is signed" since file 46 lost a number off a chart for the same reason; the code
   never did it. Changing it to `Math.abs(gapPts) > outlier` is correct and was measured.

2. THE FIELDS ARE THEN PUT BACK IN CLUSTER ORDER, NOT READING ORDER. They are only
   reversed for an RTL baseline, so an LTR baseline keeps whatever order the cluster held
   them in. Sorting the segments by x - ascending LTR, descending RTL - is correct.

**Measured with both changes on the 208-document corpus: 4 documents improved, 1 got worse.**

    350_question_paper                    lines  85 -> 116   (+31)
    417_rotate180_and_mirrored            lines   9 ->  11
    46_chart_coloured_labels_body_text    lines  29 ->  30
    69_two_col_legal_numbered_clauses     lines  51 ->  52
    form16-part-b                         lines 113 -> 112   (-1)  REGRESSION

The regression is real damage, not a count moving. On form16-part-b the old output kept
`PART B` as its own paragraph, in its own place at the right of the page. With both
changes it is joined into the sentence above it - `Certificate under section 203 ... PART B`
- which is worse than either, because the label has lost its position and reads as part of
the sentence. The cause is `sameRow()` in the paragraph grouping: two lines on one baseline
are put in one group and `buildPara` joins their text with a space.

So the changes were reverted, and this entry records them.

**The fix to try.** All three parts together, because any two of them alone leave the
regression or lose the improvement:

    a. `Math.abs(gapPts) > outlier` in the baseline cut.
    b. sort the cut segments by x, ascending for LTR and descending for RTL.
    c. in the paragraph grouping, do not let `sameRow()` hold two lines together when
       either of them is `hardEnd` and no gutter crosses the space between them. A table
       cell has a rule separating it; a page header does not, and that is the difference
       between a row and two fields.

Part (c) is the one that has not been written yet. A first attempt must check the tables
first - 8 of 25 tables were missing on stamped documents once when the grid and the
paragraph grouping disagreed, and a change here can do the same.

**Tries: 1 of 3** - the signed-gap and sort changes were tried and reverted.

**PART (c) WRITTEN AND MEASURED, 8 Nov - see "g53 batch 3" below.** The three parts together
were not what was needed. Parts (a) and (b) - the signed gap and the x sort - are still not in
the engine; part (c) alone, written as "attach a line to the leftmost line of its own baseline
when `sameRow()` already accepts the pair, and keep them as a row", clears the defect on 49 of
208 documents with no word lost and no document worse. The reason the first attempt failed is
now measurable: it joined the two fields into ONE sentence with a space, which lost the
label's position; a row keeps each field at its own measured x with a tab stop, so
form16-part-b - the document that regressed by one line - gains a line instead.


---

## OPEN - v3 corpus, batch 1 (300-315), re-processed 7 Nov under the eye + verify pipeline

Fifteen documents converted from the current engine, rendered through LibreOffice, opened one
page at a time, measured, and every finding checked against the PDF by `verify.py` before it
was written down. The final pass checked 15 findings: 14 verified, 1 refuted. Six claims made
earlier in the same pass were refuted and withdrawn - four of them the eye's own mistake -
which is the point of the step.

| Doc | Verified finding | Tries |
|---|---|---|
| **301_lab_report_panel** | `moved:ANANYA RAO` 26.2 pt, `moved:COLLECTED` 8.0 pt; reading order 78.7 %, 28 rows in the PDF against 33 in the render. The four-column band (PATIENT / AGE-SEX / REFERRED BY / COLLECTED) is emitted one cell per paragraph, so the row is four baselines that drift left to right instead of one. | 0 of 3 |
| **302_radiology_report** | `moved:PATIENT NAME` -8.6 pt. Same band, same cause: the first label of a label/value band leaves its row. The rest of the page is exact and the reading order is 100 %. | 0 of 3 |
| **311_fir_police_form** | `moved:Mobile` - 2 in the PDF, 1 in the render, worst offset 91.8 pt. The address cell overruns into the Mobile cell on the page itself, and the render welds the two texts into one run, so the label leaves its column. Reading order 90.2 %. | 0 of 3 |
| **312_affidavit_stamp_paper** | `moved:BEFORE ME` and `moved:Note: affidavits`, both exactly -72.2 pt. The notary box is drawn at its own y but empty, the footnote sits inside it, and the BEFORE ME block is pushed above the box. Reading order 58.0 %. The whole tail is 72.2 pt high, which is the spacing-before cap on the ~183 pt gap above the notary block (GAP_CAP_TW 120 pt). | 0 of 3 |
| **315_gazette_notification** | `moved:publication in the Official Gazette` +184.8 pt, `moved:The Gazette of India` +55.9 pt; reading order 29.1 %, 21 rows against 34. The three columns stack into one flow and the masthead drops below PUBLISHED BY AUTHORITY. Column bands are not detected on this page, so no `w:cols` is written. | 0 of 3 |

### Refuted this pass - do not "fix" these

| Claim | What the PDF actually says |
|---|---|
| `missing:8,39,69,600` and `missing:9,90,84,128` on 314 | Both totals are present and identical: x 467.7-513.0 on both sides. The eye misread a 130 dpi image; the last digit is there. |
| `wraps:WARNING SIGNS` on 303 | The PDF's own line runs 28.0 to 596.7 on a 595.28 pt page - it overruns its margin by 1.4 pt and the tail "more than 4 times a day" is drawn off the page and lost. The render wraps it inside the margin and keeps every word. The render is the better page. |
| `moved:AGE / SEX` and `moved:PATIENT` on 301 | Both within 0.5 pt. The band defect is real, but it is not these two labels; the verified claims are the two above. |
| `shapes` on 316 | 1 shape in the PDF, 1 in the render. |

### Two tool alarms to repair, not documents

- **303_discharge_summary, reading order 88.5 %.** The render has 27 rows to the PDF's 25
  because it wrapped the line the PDF clipped. Question 1 counts rows, so a render that keeps
  text the PDF lost is scored as an order error. The comparison should be on the text, not the
  row count.
- **305_vaccination_certificate, reading order 47.1 % and "205 shapes in the PDF, 12 in the
  render".** The seal is rotated text drawn one character per baseline, so the PDF's own rows
  are single characters; the 205 shapes are the QR module squares, which the render carries as
  one image. Both are the known rotated-stamp and image-as-image limits, not defects.

---

## v3 corpus — batch 2 (318-340), found this pass

Fifteen documents converted, every page looked at, every finding verified against the PDF.
7 pass, 8 fail. Every claim below came back VERIFIED from verify.py.

| Doc | Problem | Tries |
|---|---|---|
| **318_court_summons_form** | `moved:Returnable within 30 days` — y 783.6 in the PDF, 446.0 in the render, 337.6 pt up. The line is anchored to the page bottom and the flow emits it straight after the last flowed line. Same class as 325 below and as 312's 72.2 pt. Also seen by eye and not in the text layer: the two SERVICE checkbox glyphs detach from their labels and drop onto their own two baselines, so one label loses its box and two boxes lose their labels. Reading order 60.0 %, 26 rows in the PDF against 24. | 0 of 3 |
| **322_mutual_fund_factsheet** | `moved:EXPENSE RATIO` 34.9 pt, `moved:FUND MANAGER` 54.5 pt, `moved:RISKOMETER` 71.3 pt. The four-KPI band (NAV / NAV DATE / FUND SIZE / EXPENSE RATIO / FUND MANAGER) is emitted one cell per paragraph so the labels and their values land on drifting baselines; the RISKOMETER block and its dial scale words follow the same drift. Reading order 75.9 %, 37 rows against 42. | 0 of 3 |
| **323_credit_card_statement** | Reading order 63.5 %, 29 rows against 34, and **42 shapes in the PDF against 17 in the render** — the 25 bars of the SPEND BY CATEGORY bar chart are lost. The four category labels survive (verified: 1 line each) but move out of their rows, which is why `missing:` was refuted. | 0 of 3 |
| **325_demat_holdings_statement** | `moved:This statement is generated electronically` — y 763.5 in the PDF, 457.0 in the render, 306.5 pt up. Page-bottom anchored line emitted in the flow. Reading order 92.3 % is a band-grouping artifact on this page (84 lines both sides, same text): PAN / STATEMENT PERIOD / ABCPR1234K sort differently inside one band. The footer is the real defect. | 0 of 3 |
| **330_cad_drawing_sheet** | Page count 1 in the PDF, 2 in the render. The drawing overflows the sheet. Reading order 86.5 %, 18 rows against 19. | 0 of 3 |
| **331_pid_diagram** | Reading order 93.3 %, 22 rows against 23, and the label sequence is 50.0 % by text: TT1 / FT1 / 01, P-101 A/B, V-102, NOTE 3 and the LEGEND block all change places. The legend text itself survives (verified 1 line each; `missing:` refuted) — it is the anchored diagram labels that reorder around the shapes. | 0 of 3 |
| **332_bom_on_drawing** | Page count 1 in the PDF, 2 in the render, and **15 shapes in the PDF against 0 in the render** — the drawing frame, its division lines and the five balloons do not survive; only the BOM table does. Reading order 90.9 %, 17 rows against 16. | 0 of 3 |
| **334_patent_document** | `moved:16` 19.5 pt down, and reading order 89.7 %, 28 rows against 30. The FIG. 1 reference numeral 16 leaves its arrow. Everything else on the page is exact: 32 lines both sides, same text, 96.9 % in sequence. | 0 of 3 |

### Refuted this pass - do not "fix" these

| Claim | What the PDF actually says |
|---|---|
| `missing:Travel`, `missing:Fuel`, `missing:Groceries`, `missing:Health` on 323 | All four are in the render, 1 line each. They move out of their rows; they are not lost. |
| `missing:Centrifugal pump`, `missing:Gate valve`, `missing:Field instrument` on 331 | All three are in the render, 1 line each. The legend text is present; the diagram around it reorders. |
| `wraps:Power` on 333 | The PDF sets `Power` on two lines as well. The Type column is that narrow on the page itself. |
| `extra:SH202400871` on 340 | Neither side has it as text: the barcode and its caption are vector paths on both. The eye still sees the caption twice in the render (y 884 and under the barcode); see the tool alarm below. |

### Three tool alarms to repair, not documents

- **326_itr_computation, reading order 94.9 %.** 74 lines on both sides, identical text, identical
  order, 0 differences by `difflib`. Question 1 groups lines into rows by band, and one band
  splits differently, so the row sequence drops a row and the document is scored as an order
  error. Same class as 303 in batch 1. The comparison should be on text, not on row count.
- **340_bill_of_lading.** The barcode group is vector, so `extra:` cannot see a duplicated
  caption. The render carries "SH202400871" at y 884 and again under the barcode at y 1425
  where the PDF has one. Needs a shapes-level duplicate check, not a text one.
- **324_loan_amortisation_schedule page 7.** visual.py says "1 shape in the PDF, 0 in the
  render"; verify.py says 1 and 1. The header band is a filled rect in the PDF and a shaded
  paragraph in the render. Two shape counters disagreeing on the same page is a measurement
  bug in one of them.
- **looked.py, the combiner - FIXED and committed this pass.** The eye's FAIL was kept only
  when a *visual* finding verified on that page. A defect recorded as a measure claim -
  `pagecount` is one - therefore dropped the eye's FAIL and 330 and 332 came out **PASS with a
  verified 1-page-in/2-out defect behind them**. Any verified finding on the page now backs the
  eye. After the fix: 330 and 332 FAIL, decided by both.

---

## OPEN — v3 batch 1 (300-317), re-run 7 Nov with the eye and the verifier

Every line below is a finding that came back VERIFIED from `verify.py` against the PDF, not an
impression. Positions are the PDF's own baseline against the render's.

### E-01  A block far down the page is emitted 72-352 pt too high — 8 documents, one cause

| Doc | Line | PDF y | render y | offset |
|---|---|---|---|---|
| 300_prescription_rx | Not valid for medico-legal purposes | 793.5 | 523.3 | **-270.2** |
| 300_prescription_rx | Dr. Meera Krishnan | 793.0 | 522.9 | -270.1 |
| 301_lab_report_panel | H = above reference interval | 783.5 | 636.6 | **-146.9** |
| 302_radiology_report | Dr. A. Bhat | 695.8 | 464.3 | **-231.5** |
| 302_radiology_report | This report is based on the images provided | 773.5 | 542.0 | -231.5 |
| 303_discharge_summary | Resident Medical Officer | 735.6 | 542.9 | **-192.7** |
| 305_vaccination_certificate | This is a computer generated certificate | 783.5 | 431.7 | **-351.8** |
| 311_fir_police_form | Copy forwarded to: Superintendent of Police | 793.5 | 631.0 | **-162.5** |
| 312_affidavit_stamp_paper | BEFORE ME / Notary Public, Bengaluru | 683.6 | 611.4 | **-72.2** |
| 314_tender_rfp_boq | Meridian Consulting Pvt Ltd (footer) | 793.5 | 603.8 | **-189.7** |
| 315_gazette_notification | [No. 4/2/2024-WDRA] | 723.6 | 494.1 | -229.5 |

Cause: `DocxWriter.GAP_CAP_TW` = 2400 twips (120 pt). Any measured gap wider than that is
clamped, and the page's own bottom white space is not spent.

**Tries: 2 of 3.** Try 1 was the 72 pt ceiling -> 120 pt (fixed 393 and 394). Try 2, 7 Nov:
24000 twips. It fixed the class - 300 -270.2 -> -8.2, 302 -232.0 -> -14.0, 311 -162.1 -> -27.0,
314 -189.7 -> -27.0 - and passed G2 on all 208 documents, but **315_gazette_notification went
from one sheet to two** and the ratchet rejects it. Reverted, and the reason is written into the
constant's javadoc so it is not tried again blind.

The third try has to be one of these, not another constant:
- give 315's three columns real `w:cols` sections (its own defect, F-01 below), which frees the
  page budget it is currently borrowing from the clamped gaps; or
- place the last block on a page at its measured y only when the flow's own y is trusted - i.e.
  after the table height below is right.

### E-02  A label/value band is emitted value by value, not row by row — 301, 303

301's header band: the PDF draws `PATIENT | AGE/SEX | REFERRED BY | COLLECTED` on one row and
`ANANYA RAO | 34/Female | Dr. Meera Krishnan | 18/03/2024 07:42` on the next. The render puts
`PATIENT`, then `AGE / SEX`, then `34 / Female`, then `Dr. Meera Krishnan`, then `ANANYA RAO` -
the name lands 26.2 pt below the row it belongs to, and `COLLECTED` gets a row of its own
(28 rows in the PDF against 33 in the render, 78.7 % in sequence). 303 is the same shape: the
patient's name sits 8.2 pt below `Medical ICU-2 / 07` and `Dr. Meera Krishnan` beside it.

This is D-02 (row grouping) and D-03 (reading order) in this batch's clothes. **Tries: 0 of 3
for D-02, 0 of 3 for D-03** — nothing has been tried here yet.

### E-03  312's notary block is outside its own box

`BEFORE ME / Notary Public, Bengaluru` is drawn at y=683.6 inside a ruled box that starts at
681.4. The render puts the text 72.2 pt higher and draws the box empty, so the page shows an
empty rectangle with the words floating above it. Same cause as E-01 (the gap between the
"Note:" line and the box is clamped), so it closes with E-01 rather than on its own.

### E-04  315's three columns are one column

The page sets three columns of a gazette notification side by side, each with its own rule.
The render stacks them into a single flow: 21 rows in the PDF against 34 in the render, 29.1 %
in sequence, and the tail of the page 229.5 pt high. Page count is still 1/1, but only because
the clamped gaps are hiding how long the stacked flow is - this is also what rejected E-01's
fix.

### E-05  304's emphasis question is measuring half-point rounding, not a defect

The PDF sets the body at 6.2 pt and the six numbered headings at 6.8. OOXML stores half-points,
so the writer emits 6.0 and 6.5. The gap the page has is 0.6 pt; the render's is 0.5 pt;
`q8_emphasis` requires more than `body + 0.5`, so all six headings count as "lost" while they
are in fact bold and half a point larger, exactly as the page drew them. The document is fine.
The tool needs the tolerance applied to the gap: a heading keeps its emphasis when its own size
is within the half-point tolerance of the PDF's and it is still larger than the body. Not
changed on 7 Nov because changing a question changes every document's verdict and that needs
its own measured pass over all 208.

### Refuted this pass, and not to be claimed again

- **316's shapes** - q6 counted 1 shape in the PDF and 0 in the render; `verify.py` counted 1
  against 1 in the render. The table's header band is drawn; the document passes.
- The four claims the previous pass withdrew stand withdrawn: 314's totals are complete and at
  identical coordinates, 303's "wrap" is the render keeping a line the PDF clips off its own
  page, and 301's two label claims were 0.5 pt apart.

### Fixed this pass

Centred lines carried `w:ind w:left` = their measured x *and* `w:jc="center"`, and LibreOffice
centres inside the indent, so every centred heading was pushed right by half of it: 310 +92.8
pt, 317 +99.2 pt, 313 +121.1 pt. The alignment now places the line; the indent is cleared for a
line centred on the paper and becomes the page's own extent for one centred in a column.

---

## Closed 7 Nov — the page spends its own white space

`DocxWriter.pageFits` closes the footer/end-block half of D-01's vertical class on every
page whose content fits the sheet and holds no table. Measured over 208: 32 documents
improved on G5, 0 worse, 0 page counts changed, G2 clean. 352, 361 and 371 of batch 3 are
fixed by it; 344, 351, 353, 363 and 370 are the same defect on a page that carries a
table, and stay open on the table height below.

## OPEN — batch 3 (341-371), found this pass

| Doc | Problem | Tries |
|---|---|---|
| **344, 351, 353, 363, 370** | The page's footer, signature labels or venue block still sit 107-360 pt too high. Each of these pages holds a table, so `pageFits` refuses to spend the gap, because the model's table height is short by the rows that grow. **Blocked on the table height**, not on the gap rule. | 0 of 3 |
| **343_air_waybill** | The Pieces cell is drawn "12" and the render wraps it into "1" and "2" — the column is exactly as wide as the page's own text and the substituted face is wider. Same class as 314's "8,39,69,60". | 0 of 3 |
| **360_restaurant_menu** | Five MAINS prices (420, 360, 390, 450, 90) fall onto the line below their dish: the leader dots fill the column and the price has nowhere to go. 17 rows in the PDF against 22 in the render. | 0 of 3 |
| **365_recipe_card** | "2 tbsp" splits into "2" and "tbsp", and "to taste" into "to" and "taste": the amount column is 30 pt wide where the page drew 36. | 0 of 3 |
| **370_offer_letter** | "Provident fund (employer contribution)" and "Performance bonus (target)" wrap in a component column narrower than the page's. | 0 of 3 |
| **353_admit_card** | The label/value block is emitted as a four-column table with the labels as header cells, so VENUE and INSTRUCTIONS TO CANDIDATES land 107.7 pt low. The page sets each label above its value in a two-column band. | 0 of 3 |
| **364_event_ticket** | The tear-off stub's "WS24-4471-0082" is missing; the PDF draws it twice, the render once. | 0 of 3 |
| **350_question_paper** | Still 1 page in, 2 out — the MCQ block overflows. New this pass: the question labels "1a." and "1b." are broken onto their own lines, so each question's text starts a line below its number. | 0 of 3 |

### Measurement bugs found this pass, for the tool not the document

**352** and **371** pass by eye while `visual.py` question 1 fails: 46.8 % and 61.5 % of
rows in sequence. Both documents are right — every line is on the PDF's baseline — so
`_rows()` is grouping bands differently from the model's own order. Repair the question,
not the document.

## TRIED and REVERTED 7 Nov — every column gets the room its own text needs

**Aimed at:** the wrap class, where a cell's text is exactly as wide as its column and the
substituted face is wider — 343's Pieces "12" becomes "1" and "2", 365's "2 tbsp" becomes
"2" and "tbsp", 370's "Provident fund (employer contribution)" wraps, and it is the same
cause as 314's "8,39,69,60".

**The change.** The last-column rule was generalised to every column: a column whose text
reaches its drawn right edge is widened to hold that text, taking the room from the slack
to the right of the table and stopping when the slack is gone.

**Measured over all 208 documents, against the code as it stood before the try:**
G2 clean, but **14 documents worse on G5 and 1 better** — 362_price_list_dense 29.5 % to
3.9 %, 42_table_coloured_header_alternating_rows 47.5 % to 23.0 %, 73_marksheet 54.7 % to
31.2 %, 80_gstin 34.2 % to 19.2 %, 300_prescription 34.0 % to 22.0 %, 56_table_indented
47.1 % to 35.3 %, 35_four_typefaces 57.7 % to 46.2 %, 326_itr 70.3 % to 59.5 %,
72_bank_statement 33.8 % to 23.8 %, 79_inr_grouping 38.3 % to 34.0 %,
75_merged_header 9.8 % to 7.8 %, 314 17.7 % to 16.5 %. Only 343 improved, 66.7 % to 69.2 %.
77_arabic_rtl_document did go from four sheets to two, which is a real gain, but it does
not buy the rest.

**Why.** Widening an inner column moves every rule after it and re-derives the insets of
the cells to its right, so a table that was on the page's own column edges no longer is.
The last-column case never had that problem because nothing follows it.

**Reverted, baseline untouched. Tries: 1 of 3.** The next attempt should keep each
column's drawn edge and give the text room without moving the rules — a negative right
inset or a wider cell that overhangs its neighbour — rather than widening the column.


## Table height, second attempt (7 Nov, v3 batch 4) - measured, and REJECTED by the ratchet

`pageFits` refused to spend a page's white space whenever the page held a table, because the
model's table height (`bottom - top`) is short: rows are emitted `w:trHeight hRule="atLeast"`,
so a cell whose text wraps grows the row. That is what keeps 374's "Total headcount" 329 pt
high, 375's "Verified by" 172 pt, 381's "Distribution:" 241 pt and 393's figure caption 133 pt.

This pass measured the growth instead of assuming it. `cellR - cellX` is the width the page
drew that cell's text at and `colX` is the column it has to fit into, so the lines the emitted
cell takes is that width over that column; summed over the rows, plus one line for every cell
that has to wrap (a renderer breaks at a space, not at the column edge), plus one line for every
newline already in a cell's string (a form's label-over-value cell), that is the table's
emitted height. `pageFits` then adds it and decides as before.

It works, on the documents it was aimed at:

| document | line | PDF | before | after |
|---|---|---|---|---|
| 374_org_chart | Total headcount | 746.2 | 416.9 | 747.9 |
| 375_attendance_register | Verified by | 552.0 | 379.6 | 550.9 |
| 381_incident_report_timeline | Distribution: Operations | 777.0 | 536.2 | 782.1 |
| 393_spectrum_peak_table | Figure 1: absorbance spectrum | 307.1 | 174.4 | 306.8 |
| 373_leave_application_form | ANANYA RAO | 122.9 | 140.0 | 140.0 (1 sheet, not 2) |

And it is rejected anyway. Rendered against `base208.json` over all 208 documents it sends
**39 documents from one sheet to two** (first form, without the wrap slack: 40; the newline
count alone took 373 back to one sheet, the wrap slack took one more document). 64_newspaper
goes 1 -> 5, 77_arabic_rtl 1 -> 4, 330, 332, 341, 350, 402, 55, 59, 63, 65, 67, 75, 78,
academic-paper-ieee-2col, bank-statement, boq-tender, brochure-3col, bus-timetable, eway-bill,
gst-invoice-3line-items, gst-invoice-with-qr-code, insurance-policy-schedule,
itr-computation-with-slab-table and 16 more. Zero documents got better on page count.

So the estimate is still short somewhere, and the wrap slack does not find it (40 -> 39). The
next thing to measure, in this order: (a) how many tables even HAVE `cellX`/`cellR` populated -
where they are absent every cell counts as one line and the estimate collapses to the model's
own extent, which is the bug being fixed; (b) the spacer paragraph above a table, which
`pageFits` charges at the writer's 144 pt cap but the flow may realise differently; (c) the
`prevBox = 0` reset after a table, which makes the next paragraph's pitch the whole gap from
`t.bottom`. Reverted with `git checkout`; `base208.json` untouched.

Also open from this batch, and both are TOOL gaps rather than document defects:

| Gap | Evidence |
|---|---|
| **q8 emphasis is one-directional** | 380_runbook_terminal_output's "Escalation:" line is bold in the render and regular in the PDF. q8 asks only whether a line the PDF emphasised kept its size, so a line the render emphasised on its own passes. 380 is FAIL on the eye and PASS on the numbers. |
| **no claim type for a table's shape, and none for a shape count** | 383's RESPONSE FIELDS table carries a fourth empty column and row rules the PDF does not draw; 400 loses one speech bubble's outline. `shapes` exists in the vocabulary and has no check; `columns` does not exist at all. Both came back UNVERIFIABLE, and PIPELINE's rule is that a document is not PASS while a finding on it is unchecked - 380 and 383 are recorded FAIL for that reason although `looked.py --combine` calls them PASS. |

## The table height, measured again on 7 Nov — the row PITCH is not the blocker

**Tries: 1 of 3.** The first try went at the row height, and it was rejected. What it
measured is worth keeping, because it moves the blocker one step closer.

**What was tried.** `PdfToWord.Table` gained `rowY` - one measured y per row - filled by the
two builders that know it (`tableFromCells`, from the drawn cell edges; `buildRowTable`, from
each row's own first baseline). `DocxWriter` then emitted `w:trHeight` from the page's own row
pitch instead of `(t.bottom - t.top) / rowCount` for every row. That average was wrong in
principle: a table with one tall heading row and twelve short ones gave all thirteen the mean,
so the heading came out short and every data row tall.

**What it measured.** `rowY` reaches only the two builders above; the tables that actually
drift (300's medicines grid, 314's BOQ, 390's 21-column appendix) come from the other three
and carry no row edges yet. On a ten-document table-heavy subset the pitch alone moved lines
within tolerance from 11.6 % to 15.5 % and G2 passed across all 208 - but against
`base208-position.json` **31 documents regressed, 17 of them beyond the 15 that D-01's flow
change had already left as debt**, and all 17 are table documents: 72_bank_statement 75.0 % to
6.2 %, 35_four_typefaces 44.2 % to 7.7 %, 42_table_coloured_header 44.3 % to 6.6 %,
383_api_docs 43.1 % to 8.6 %, 326_itr 50.0 % to 29.7 %, 80_gstin 26.0 % to 6.8 %, and eleven
more. **Reverted; the baseline is untouched.**

**What that proves.** A row emitted `w:trHeight hRule="atLeast"` cannot be made shorter than
its own content, so the page's pitch is only a floor: where the substituted face wraps a cell
the row grows anyway, and a small floor makes that growth *more* visible, not less. The old,
too-tall average was accidentally absorbing it. So the blocker is not the row pitch - it is
**row growth**, and the fix has to stop a cell wrapping in the first place, which means the
cell's text must be given the page's own line breaks (the model has one string per cell, not
the lines the page drew inside it) or `hRule="exact"` with the clipping that implies. Neither
has been tried. Do not spend a try on the pitch alone again.

## The form band that splits — the exact mechanism, found on 301 (7 Nov)

**Tries: 0 of 3.** `301_lab_report_panel`, `302_radiology_report` and `311_fir_police_form`
all show the same thing: a band of four labelled columns on one baseline arrives in the
.docx as five or six stacked paragraphs, so every value sits a line below its label.

**The mechanism, traced.** The PDF draws row 1 as `PATIENT` x=28, `AGE / SEX` x=170,
`REFERRED BY` x=280, `COLLECTED` x=430 — one baseline. The model produces
`[PATIENT, AGE / SEX, REFERRED BY]` and `[COLLECTED]` as two paragraphs, and the second
row as `[34 / Female]`, `[Dr. Meera Krishnan, 18/03/2024 07:42]` and `[ANANYA RAO]` as
three. `PdfToWord.sameRow` has

    if (next.x < prev.x - 0.5f) return false;

and the two cells of row 2 were measured 1 pt apart in y (80.0 and 81.0) — inside the row
tolerance, but enough for the sort to put `34 / Female` (y=80) ahead of `ANANYA RAO` (y=81).
The next fragment then starts to the LEFT of the one before it, so the row is cut there and
everything after it starts a new paragraph. The row's own fields are all present; it is the
grouping that breaks.

**Why it is not a one-line fix.** D-07 records the sort and signed-gap changes, measured at
+4 documents and −1, and reverted. Both act on this same ordering. What is new here is the
evidence that the trigger is a 1 pt baseline difference between two cells of the SAME row,
not a wide gap and not reading order. Quantising y into row bands before sorting, so cells
within the row tolerance keep their x order, is the narrower change and has not been tried.

**Also new:** the fourth field of row 1 (`COLLECTED`, x=430) is lost to a paragraph of its
own even though the three tabs before it are correct and 430 is inside the page. A print
inside `sameRow` for that pair never fires, so the two are not adjacent in `lines` at all and
the cut is upstream of `sameRow` - in the segmentation that builds `lines`. Not yet found.

---

## v3 corpus — batch 1 (300-317), re-processed 8 Nov under the verifier

Every document re-converted, re-rendered, every page opened and looked at, every finding
checked against the PDF by verify.py, and the decision made on the verified set. 7 PASS,
8 FAIL. 14 of the 15 findings held; the one refutation (316's shapes) was correctly not fixed.

| Doc | Verified finding | Cause | Tries |
|---|---|---|---|
| **300_prescription_rx** | moved:Dr. Meera Krishnan 270.1 pt | clamped gap: the page's own 270 pt of white space between the advice block and the signature block is given up at the 120 pt ceiling. The page carries a table, so `pageFits` returns false and the gaps stay clamped. | 0 of 3 |
| **302_radiology_report** | moved:Dr. A. Bhat, MD, DNB (Radiodiagnosis) 231.5 pt | same class, same cause | 0 of 3 |
| **305_vaccination_certificate** | moved:This is a computer generated certificate 351.8 pt | same class; order 47.1 % is a second symptom of the same lift | 0 of 3 |
| **301_lab_report_panel** | moved:ANANYA RAO 26.2 pt; order 78.7 % | the four-column label/value band is absorbed into the results table as an extra header row: the render's table has 33 rows against the PDF's 28, and the real header row is pushed down | 0 of 3 |
| **311_fir_police_form** | moved:Mobile 91.8 pt; order 90.2 % | the address cell overruns its column in the PDF itself, so its tail lands in the next cell and the Mobile label is welded into the address string | 0 of 3 |
| **314_tender_rfp_boq** | moved:Grand total -20.7 pt | table height: the model's extent over 9 rows is 13.15 pt a row and the page drew 15.0, so the drift grows 1.1 pt a row to 20.7 pt at the last row | 1 of 3, see below |
| **315_gazette_notification** | moved:The Gazette of India 55.9 pt; order 29.1 % | three columns stack into one flow - unchanged, its own defect | 0 of 3 |
| **303_discharge_summary** | breaks:WARNING SIGNS; order 88.5 % | the render breaks the warning line at a different word and carries two rows the PDF does not have; the substituted face is wider than the page's | 0 of 3 |

**Tried 8 Nov and rejected: per-row table heights.** Every row was given the average of the
page's extent, so a row needing more lines than the average grew past it and every line below
the table carried the error. Each row was given what its own cells need, with the page's slack
shared over the rows that could take it. It is the right shape of fix and it is NOT the fix:
measured on the 62 documents whose row heights it changed, 23 got worse and 7 better, worst
`balance-sheet-two-columns-of-figures` 60.6 % -> 9.6 % of lines in tolerance and
`73_marksheet_subject_marks_grade` 54.7 % -> 6.2 %. G2 passed on all 208 - the damage is
vertical, and G2 does not measure vertical. The row's own pitch is not in the model: `Table`
carries `top`, `bottom`, `colX`, `cellX`, `cellR`, `sizes` and `colors`, and no per-row y, so a
row height can only be guessed from the text. Guessing it from character counts over-estimates
badly. Reverted; the baseline is untouched. 1 of 3 used.

**Tried 7 Nov and still rejected: spending the page's white space on a page with a table.**
`pageFits` returns false the moment a page carries a table, and every document in this batch
carries one, which is why 300, 302 and 305 are still clamped. The reason is in the code: with
table pages spending their gaps, 15 documents went from one sheet to two and 390 fell to 0.5 %
of lines in tolerance. Blocked on the table height above, exactly as recorded.

**The measurement that is wrong, not the document: 312_affidavit_stamp_paper.** The eye passed
it and the numbers failed it - order 60.9 %, emphasis 18 of 20 lines "lost" bold. Both are
tool bugs, not defects: the page sets most of its lines in a face the emphasis question cannot
see. Recorded here so the final sweep repairs the tool rather than the document.

## b80 corpus — batch 1 (01-20), 8 Nov

Twenty documents, 22 pages, every page opened before any number was read, 32 findings, 22
verified, 1 refuted, 9 unverifiable. Seven pass, thirteen do not. All thirteen fails fall into
two classes, and neither is new.

### RECORDED-UNFIXABLE — the rotated stamp (01, 02, 03, 04, 08, 09, 10, 13)

`moved:AUTHORISED SIGNATORY` 44.5 pt, `moved:GOODS RECEIVED IN ORDER`, `moved:INTERNAL AUDIT
USE ONLY`, `moved:DUPLICATE ISSUED` -186.5 pt, `moved:PAID` -14.2 pt, `moved:FY 2024-25`
17.0 pt, `moved:ORDER CONFIRMED`, `moved:प्रमाणित प्रतिलिपि` -17.0 pt. Every one of these is a
stamp the page draws on a rotated baseline at 15, 90, 180 or -15 degrees; the writer anchors an
axis-aligned box at the line's origin, so the text is upright and offset by the rotation.

The one try this class is allowed has been spent, twice over: the code comment at `anchor()`
records the attempt to place the box on the rotated line's bounding area, which moved file 08's
two stamps apart and put file 01's AUTHORISED SIGNATORY somewhere else again, and it was
reverted. OOXML has no text rotation a LibreOffice render honours. Recorded, not retried.

What is NOT the rotation and may still be worth a try later: on 08 and 11 the stamp sits to the
RIGHT of the page's own box by 10-20 pt even in x, and on 12 page 2 the stamp's text lands 56.4
pt below the page's while its box is empty. That is a placement question, not a rotation one.
0 of 3 used on the x placement.

### OPEN — the same-baseline columns are still one flow, and it is what makes the page not fit

06 (`moved:NET AMOUNT` 120.9 pt), 07 (`moved:Grand Total` 7.5 pt), 20 (`pagecount` 1 in / 2 out,
`moved:I have read and understood` 101.4 pt), 12 (body 136.0 pt down on both pages). On 06 the
page draws two columns under the table - "Amount in words / Pharmacist / Store timing /
Prescription" on the left and "Sub Total / Discount / CGST / SGST / NET AMOUNT" on the right -
and the model hands them over interleaved, one line from each, so the flow spends nine line
pitches where the page spent five. On 20 each numbered item is a marker at x=64 and a paragraph
at x=100 on the same baseline, and they arrive as two paragraphs, so every item takes two lines.

This is D-07, and it is the whole reason these pages then lose their white space as well: the
interleaved flow is taller than the sheet, `pageFits` returns false, the page falls back to the
120 pt clamp, and the footer lands 110-275 pt above where the page draws it (measured on every
document in this batch). Fixing the columns fixes the footer at the same time; fixing the footer
alone would only hide it. **Tries: 0 of 3.** The signed-gap and sort attempts recorded under
D-07 were measured (+4 documents, -1) and reverted; do not repeat them.

### Blind spot to record, not a document defect

15_stamp_on_scanned_page passes on the tool's verdict: its two stamp lines land within 2.5 pt.
The eye failed it - the page draws a red box around the stamp and the box and its rotation are
gone - but `shapes` came back UNVERIFIABLE, so nothing verified and the document passes. The
same class as 13 above. Recorded so the final sweep does not read this row as a clean pass.

## b80 corpus — batch 3 (41-60), 8 Nov

Twenty documents, 23 pages in the PDF and 24 in the render (55 spills). Every page opened before
any number was read; every finding verified against the PDF; 20 findings, 16 verified, 1 refuted,
0 unverifiable after the fixes below. **15 pass, 5 fail.**

### FIXED this run (tool): the rules check could only see one direction

`verify.py`'s `rules` test returned VERIFIED only when `b > a` - more rules in the render than in
the PDF. That was written for 351_omr_answer_sheet, where the render put a ruled grid round a
bubble sheet the page leaves unruled. It cannot see a MISSING rule at all, so every dropped rule
came back REFUTED and passed. Both directions now count, and a difference in either direction is
VERIFIED.

Fixing that exposed a second fault in the same test, and it is the interesting one. With the
one-way test gone, 58_header_rule_footer_rule's `rules` claim came back VERIFIED at "3 rules in
the PDF, 2 in the render". It was a false alarm. The page draws three stroke-only rules
(y=54.0, 57.0 and 781.9); the render draws all three as filled bands. The classifier accepted
`height <= 1.2`, and LibreOffice exports a 1.2 pt border as a rect **1.2000000476837158** pt high,
so the widest rule on the page was excluded from the render's count. The bound is now
`RULE_MAX_PT = 1.5`, named and commented as a CLASSIFICATION bound - "this rectangle is a line,
not a box" - not a positional tolerance, because nothing in the test is compared against the
other side's coordinate. 58 is 3 and 3, REFUTED, and the document passes.

**The eye was wrong on 58 and the numbers were wrong on 58**, in opposite directions, and the two
errors cancelled into a plausible-looking defect. At 130 dpi the 0.4 pt grey footer rule is not
visible in the side-by-side image; I recorded `rules` on it and could not see the rule at all.
The lesson is the one the pipeline is built on: a FAIL needs both the eye and the check, and
"the eye saw it" is not evidence when the thing is a hairline.

### OPEN — the right column of a two-column page is laid out after the left one

54_two_column_body_full_width_header_footer. `moved:On the domestic side` VERIFIED at y=116.5 in
the PDF against y=270.1 in the render, 153.6 pt; `moved:The institute` 153.8 pt. Reading order
21.7 % of 17 rows, 29 rows in the render against 17. The two columns are one flow with a gap, not
two measured columns - the same cause as 27 in batch 2, and the same fix. **Tries: 0 of 3.**

### OPEN — a sidebar box beside the body loses its box and spills the page

55_sidebar_box_beside_body. `pagecount` VERIFIED 1 in the PDF and 2 in the render;
`moved:PROJECT AT A GLANCE` VERIFIED 147.8 pt against 375.5, 227.7 pt; `shapes` VERIFIED 1 in the
PDF and 0 in the render. The box is drawn at the page's right, its eight field pairs inside it.
The render has no box, puts the field pairs at the foot of page 1 as body text, and adds a second
sheet carrying an empty blue-ruled rectangle. **Tries: 0 of 3.**

### OPEN — a table cell 0.5 pt too narrow breaks its value

56_table_indented_from_margin. `missing:640.00` VERIFIED - 1 line in the PDF, 0 in the render.
The PDF sets the Rate cell's "640.00" from x=396.6 to 420.0, 23.4 pt wide, with the Remarks column
starting at 428.0. The render's cell is 458 twips (22.9 pt) and its text needs 23.4, so the last
digit wraps onto a line of its own inside the cell and the row the page draws once arrives as two.
Reading order 93.0 % of 21 rows, 22 rows in the render.

**Tried and reverted (1 of 3).** `DocxWriter`'s comment has promised `w:noWrap` since the 343 fix
and nothing ever wrote it. Emitting `<w:noWrap/>` when `textOverflows` is true does put the
element in `word/document.xml` with the value whole in a single `w:t` - and LibreOffice ignores it
for a fixed-width cell and wraps anyway. The cell is short by 0.5 pt, not by an inset: the inset
is already 0 and the existing `textOverflows` path has nothing left to give up. What is left is
the column width itself, which is the page's own edge. Reverted; the baseline is untouched.
**Tries: 1 of 3.**

### OPEN — a centred title page is set at the top of the sheet

57_centred_title_page_left_body_pages, page 1 of 2. `moved:SRI VINAYAKA INSTITUTE OF TECHNOLOGY`
VERIFIED at y=243.2 in the PDF against y=116.8 in the render, -126.4 pt. The whole title block -
institute, rule, title, the two subtitle lines, "by", the name, the guide and the department -
sits 126 pt high, and the block's own 20 pt leading is not carried. Page 2 is correct and left
aligned, so this is the centred band on a title page, not the body flow. **Tries: 0 of 3.**

### OPEN — a right-hand signature block is pushed down onto the seal

60_page_border. `moved:Dr. S. Vedavathi` VERIFIED at y=472.2 in the PDF against y=493.0, 20.8 pt.
`overlap` came back REFUTED - 34 overlapping pairs in the PDF against 6 in the render - because
the seal's curved text overlaps itself many times on the page and the render's does not, so the
count cannot see the date landing on the seal's top arc. The eye can, and the moved finding is
the same defect measured. Reading order 48.1 % of 32 rows, 22 rows in the render. **Tries: 0 of 3.**

### Measurement blind spots found this pass - repair the tool, not the page

    order on 43_red_stamp_over_black_text   81.6 %, 23 rows in the PDF against 26. The eye
        passed and it is right: the stamp's four lines band with the body lines differently on
        the two sides, so the row sequences cannot pair. 3 extra rows, all stamp.
    order on 46_chart_coloured_labels_body_text  85.7 %, 27 against 29. The chart's twelve
        value labels band as two rows in the PDF and three in the render. Chart labels are not
        reading order.
    order on 50_invoice_coloured_total_row   92.3 %, 19 against 20. "TOTAL PAYABLE" sits in a
        table row whose baseline is 2 pt off the "Amount in words" line, so the render splits a
        row the PDF draws as one. Same family as D-01.

All three were named by `looked.py --combine` as "eye (numbers wrong - repair the tool)" and all
three documents stay PASS. The third time 43/46/50's pattern has appeared: reading order pairs
rows by text, and any page where the two sides band a row differently is scored as a sequence
break. That is now the single largest measurement bug in the tool and wants a fix before the
final sweep counts these pages.

### A claim that could not be checked

    overlap on 60   REFUTED, 34 pairs in the PDF against 6 in the render. The check counts
        overlaps the PDF has and the render does not, which is right in principle; on a page
        with a curved-text seal the PDF's own overlaps swamp it. The real defect is carried by
        the verified `moved:Dr. S. Vedavathi` on the same page.

### One more thing the wraps claim cannot see

`wraps:Shrinkage and fastness testing` came back REFUTED - "2 line(s) on both sides" - on the
page where a value really is broken in half. The check follows the block's words through the
render's lines, and the PDF's word is `640.00` while the render's are `640.0` and `0`, so the
follow stops. `missing:640.00` verifies the same defect. The wraps check needs to match on
characters, not words, before it can be trusted on a broken number.

---

## OPEN - b80 batch 4 (61-80), found this pass, 8 Nov

Ten documents fail and nine of them are the same defect. Every finding below came back
VERIFIED from `verify.py` against the PDF; nothing here is an opinion.

### D-08  A page set in two or three columns is written as one flow — FIXED 8 Nov

**Severity: the largest single class in this batch - nine of twenty documents.**

The engine detects column bands (`Line.column`) and orders paragraphs down one column and
then the next, so the READING ORDER is right. `DocxWriter.pageColumns()` then returns
`{1, 0}` unconditionally, so the page is written as one column: the second column's text
lands below the first, the page becomes twice as tall as the paper, and it spills.

| Document | pages in / out | verified finding |
|---|---|---|
| 62_two_col_newsletter_pull_quote | 1 / 1 | moved:Tank rehabilitation restores water to nine villages 28.0 pt |
| 63_three_column_brochure | 1 / 2 | moved:THE ESTATE 29.5 pt |
| 64_newspaper_uneven_columns_ad_boxes | 1 / 5 | pagecount, 50 rows in the PDF against 7 in the render |
| 65_two_col_full_width_figure_caption | 1 / 2 | moved:Figure 1 168.0 pt, 37 shapes in the PDF and 0 in the render |
| 67_two_col_with_sidebar | 1 / 2 | moved:COURSE AT A GLANCE 355.4 pt, 1 shape in the PDF and 0 in the render |
| 75_merged_header_cell_three_columns | 1 / 2 | moved:Yeshwanthpur 36.1 pt, 5 shapes in the PDF and 0 in the render |

**Why it is not simply `w:cols`.** That was tried and reverted, and the reason is written
into `pageColumns()`: a paragraph's `w:ind w:left` is measured from the PAGE edge, so
inside a narrow column the indent exceeds the column width and the text wraps one character
per line. Turning `w:cols` back on without making the indent column-relative produces a
strip of single letters down the right edge of an otherwise correct page.

**The fix to try, in one piece.**

    a. `pageColumns()` returns the real band count, and `Ctx` carries each band's left and
       right edge for the page being written.
    b. `flowFromBox` writes `w:ind w:left = b.x - bandLeft` and
       `w:ind w:right = bandRight - b.right`, and a centred line is centred inside its
       band, not inside the paper.
    c. A block that spans the bands - a full-width abstract, a full-width table, a
       newspaper's masthead - closes the columned section and opens a one-column section,
       which is what `sectPrXml` already knows how to write.

Part (c) is the one that has to exist before (a) can ship: 61, 65, 68 and 69 all put a
full-width block between or above their columns, and a page-wide section with two columns
would cut that block in half.

**Tries: 0 of 3.** Not started. 61, 66, 68, 69, 71 and 80 already pass with one column,
so whatever is built must leave those six alone.

### OPEN - two fields on one baseline, split instead of joined

`69_two_col_legal_numbered_clauses` puts each clause number on its own baseline 12.0 pt
above its clause, and `70_magazine_drop_cap_photo_caption` puts a masthead and its
strapline in two paragraphs so the strapline's line box pushes the page down 13.5 pt.
This is D-07's part (c) from the other side: D-07 is about fields being joined that should
not be, and these are fields NOT joined that should be.

The cause found this pass is narrower than D-07's: `buildPara`'s line list is sorted by
`(column, y)` when the page is not a row, so on a page with detected column bands the two
fields are far apart in the iteration and `sameRow()` never sees them as neighbours. 69 is
the case that shows it - the number is in column 0 and its text in column 1.

### OPEN - a mixed-script line is split at its script boundary

`78_mixed_english_devanagari_line` breaks `Amount paid: Rs. 4,200.00` into four baselines
(`Amount paid` / `:` / `Rs` / `. 4,200.00`) and `77_arabic_rtl_document` breaks
`ME/INV/ 2025 0884` at its slashes. Every fragment is on the page, but on its own line.
This is what makes 78 and 77 spill onto a second sheet. Cause not yet located; the two
documents share it with 76_devanagari_table, which does NOT break, so whatever the split
is it is not "any line with two scripts".

### OPEN - an RTL table is written with its columns in the other order

`77_arabic_rtl_document`'s five-column table comes out mirrored: the PDF puts the item
column at the right and the amount at the left, the render the other way round. The text of
each cell is right, so this is a column-order question in `buildTables`, not a text one.
Separate from D-08 and needs its own fix.

---
#### D-08 as attempted on 8 Nov — the patch compiles, the measurement did not finish

A full attempt was made and NOT committed, because it could not be verified. What it
established is worth keeping, because every one of these was found the hard way.

**The five edits, in the order they must be made**

1. `pageColumns()` — delete the `if (true) return new int[]{1, 0};` that disabled it. The real
   body below it already builds the band map; it runs once that line goes.
2. `pageColumns()` — add the spanning guard. A block in band 0 whose width is more than about
   1.6x the first band's is full width (an abstract, a masthead, a wide table); that page must
   stay one column, because a full-width block cannot live inside a column and the section
   split that would fix it is not written.
3. `Ctx` — add `float bandLeft;` and `float bandRight;`. Set them per page, right where
   `ctx.spendGaps` is set: both 0 when `pCols == 1`, and the first band's edges when it is
   greater.
4. `flowFromBox()` — `leftTw` becomes `(b.x - bandL)`, and every
   `(ctx.pageWidthPt - b.right)` becomes `(bandR - b.right)`. That is what stops the text
   wrapping one character per line. `w:jc center` then centres inside the band on its own,
   because the indents are the band's width — no extra work.
5. `flowRow()` — leave it page-relative. Its tab stops are absolute page coordinates, so
   shifting the indent without shifting the stops moves the fields off their columns.

**The two traps that cost the most time**

- `flowRow()` declares `int leftTwRaw`, not `int leftTw`. A blind rename of `int leftTw` hits
  the wrong one and the row function loses its variable, which surfaces as
  "cannot find symbol: variable b" at the `w:ind` line, not at the declaration.
- A `float pageW` added to `pageColumns()` collides with the one the real body already
  declares. Name it something else.

**Why it was not committed**

Page counts looked like regressions on three documents — 324 7->13, 416 300->599,
417 2->3 — but the counting method was wrong: it counted `w:type="page"` occurrences, and a
columned section writes `<w:type w:val="nextPage"/>`, so the new sections inflate the count.
The real page count needs a render, and the position measurement needs about 24 s a document,
which is 80 minutes for 208 and does not fit one sandbox call. Both have to run before this
change can be judged.

**Tries: 1 of 3** — the attempt was made, the measurement could not be completed, so it does
not count as a fix and it does not count as a failure of the approach.

**Next attempt starts here:** make the five edits, convert the 75 v3 documents and the 20
b80 documents that carry columns, render them, and compare page counts from the RENDER (not
from the XML) plus the position share against base208-position.json. Only then commit.

### D-09  The page's own white space is spent only where the columns are real

**FIXED 8 Nov.** GAP_CAP_TW clamps a gap at 120 pt, which is why a page's footer or
signature block lands 200-270 pt too high: the PDF left 270 pt of white space below the
last line and the writer gives it up. Raising the ceiling was tried on 7 Nov and reverted
because 315_gazette_notification went from one sheet to two - its three columns are still
stacked into one flow (D-08), so its content is three columns long and only fitted a sheet
while the gaps were being clamped.

`hasColumnBands(page)` now gates the spending: a page that has any block in a column band
above 0 keeps the 120 pt ceiling, and only a page whose blocks all sit in band 0 may spend
its white space. That separates 315 (columned, keeps the clamp) from 300 and 302 (single
flow, may spend).

**Second attempt, 8 Nov 09:20 - the guard was a proxy, and it over-fired.** Measured with
`-Dp2w.debugGaps=1` on v3 batch 1, eleven of the fifteen pages reported `bands=true`,
including 305 and 311, which are forms and not columns at all. A form's field columns leave
vertical gutters, the column pass gives those rows `column > 0`, and the guard read the page
as set in columns - so those pages kept the 120 pt clamp and their footers stayed 350 pt
high. The guard was standing in for a measurement that already exists: `pageFits` walks the
page's own blocks through the same line box solver and returns false exactly when the page
would not fit with its gaps spent. 315 fails it; 305, 311 and 312 pass it. So the guard is
gone and `spendGaps` is `pageFits(page, ph)` alone.

| Document | line | before | after |
|---|---|---|---|
| 305_vaccination_certificate | This is a computer generated certificate | y=431.7 (351.8 pt high) | **y=775.6** (1.4 pt) |
| 311_fir_police_form | Copy forwarded to: Superintendent of Police | y=608.5 (178.5 pt high) | **y=798.2** (11.2 pt low) |
| 312_affidavit_stamp_paper | Notary Public | y=623.5 (72.2 pt high) | **y=698.6** (10.4 pt low) |
| 315_gazette_notification | The Gazette of India | y=89.3 (55.9 pt low) | y=89.3 (unchanged) |

G2 across all 208 documents: **no document got worse**. 315 stays one sheet, which is the
case the guard existed for. 305 now passes outright; 311 and 312 still miss the 3 pt
tolerance, but by about a line box instead of by a quarter of the page, and their residue is
the table-height error below, not the gap.

Measured on 8 Nov, position share within tolerance, higher is better:

| Document | before | after | pages |
|---|---|---|---|
| 300_prescription_rx | 0.0 % | **24.0 %** | 1/1 |
| 302_radiology_report | 3.0 % | **9.1 %** | 1/1 |
| 311_fir_police_form | 12.5 % | **2.8 %** | 1/1 |
| 314_tender_rfp_boq | 5.1 % | **17.7 %** | 1/1 |
| 315_gazette_notification | 2.9 % | **2.9 %** | 1/1 |

315 is unchanged to the decimal and still one sheet, which is the whole point of the guard.
The other four improve and none regress.

This guard comes out when D-08 lands: once the columns are written as columns, a columned
page fits too and may spend its white space.

### D-10  Text the page draws twice for weight comes out twice

**Severity: 2 documents - 38_faux_bold_italic_synthesised and 411_nested_xobject_transforms.**

A PDF has no bold weight it cannot load, so a page that wants bold draws the same glyph twice
with a sub-point offset. `dedupe()` already exists for the OCR overlay case and requires
`|dx| < 0.5 pt`, `|dy| < 0.5 pt` and identical text. A faux-bold offset is larger than that,
so both copies survive and the line reads doubled.

| Document | verified finding |
|---|---|
| 38_faux_bold_italic_synthesised | `count:Study of self-compacting concrete` - the subtitle is drawn twice at y=118.2 |
| 411_nested_xobject_transforms | `count:NESTED FORM 1` - 1 in the PDF, 2 in the render |

**Why widening DUPLICATE_TOL does not work, and this is measured, not guessed.** The tolerance
is 0.5 pt because 1.2 pt merged genuinely different characters: file 28 read "Y ar" (the 'e' of
"preventive" at x 364.03 swallowed the 'e' of "Year" at x 362.88) and file 39 read "COM ERCE".
Those two 'e's are 1.15 pt apart and an 'e' at 8.5 pt is 3.77 pt wide - so an
advance-overlap test does not separate them either: 1.15 is 30 % of the advance, which looks
exactly like faux bold. Any position-only window that catches faux bold also catches that pair.

**The two options, neither taken yet**

a. Line-level dedupe: after lines are built, two lines with identical text and a y within a
   small fraction of the line height keep one. Cheaper to reason about, but a table that
   legitimately repeats a row would lose it, so the y window has to be tighter than a row
   pitch and the rule needs measuring on 324_loan_amortisation_schedule (240 repeated rows)
   before it can ship.

b. Word-context: a faux-bold copy has the same neighbouring glyphs at the same offsets; the
   two 'e's of "preventive" and "Year" do not. This separates the cases correctly but costs a
   comparison over the neighbourhood for every glyph, and `dedupe` runs on every glyph of
   every page.

Option (a) is the one to try first, with 324 as the regression document that decides it.

**TRIED 8 Nov and REJECTED: line-level dedupe.** `dedupeLines()` was written - two lines
with identical text and a y within a quarter of the type size keep one - and it did fix the
targets: 38's subtitle went from two copies to one and 411's "NESTED FORM" from two to one.
The gate rejected it, correctly:

| Document | counts | verdict |
|---|---|---|
| 411_nested_xobject_transforms | extra 6 -> 0, lines 3 -> 2 | improved |
| 38_faux_bold_italic_synthesised | **missing 4 -> 14** | lost 10 words |
| text-held-twice-shadow-text | **missing 0 -> 76**, lines 47 -> 42 | lost 76 words |

`text-held-twice-shadow-text` holds its text twice on purpose - the second copy is the drop
shadow - and its two copies sit closer together than a quarter of the type size, so the rule
ate it. That is the third document this defect needs, and it is the one that decides the
design: a dedupe that keeps the first copy cannot tell a faux-bold copy from a deliberate
shadow copy, because at line level they are the same thing.

**What that leaves.** The two copies differ only in colour and weight, not in position or
text, so position and text cannot separate them. The separating signal has to be the one the
page actually used to mean "bolder": the copy is drawn in the same colour as the first and
slightly offset. A shadow is drawn in a different colour, usually grey or black against a
coloured fill. So the rule has to compare colour as well as position, and that needs
measuring against both 38 and text-held-twice-shadow-text before it can ship.

**Tries: 1 of 3** for D-10.




## CLOSED - the gate counted a row merge as lost text, 8 Nov

`gate.py` treated any fall in a document's line count as a regression, on the reasoning
that "one that held 400 lines and now holds 380 has lost text". A row merge makes two lines
one, so every correct row merge read as lost text: 15 documents when `sameRow()` was
widened, with `missing` and `extra` unchanged on all 208.

A fall is now a regression only when a word went with it (`words_moved`), and otherwise it
is reported as JOINED. The word-level checks - missing, extra, blocks, nobg, blank - still
gate hard and are still compared in both directions. Measured after the repair: G2 across
208, no document got worse, one improved, fifteen joined. `base208.json` was re-recorded on
that run and committed with the source.

---

## OPEN - g53 corpus, batch 1 (A 1-10, B 11-13), found this pass, 8 Nov

Thirteen documents, 14 pages in the PDF against 22 in the render. Every page opened before any
number was read; every finding checked against the PDF. 34 findings: 32 verified, 1 refuted,
1 unverifiable. **4 pass, 9 fail.** Eight of the nine fail on `pagecount`, and seven of those
eight are multi-column pages - the class D-06 has been waiting on.

### OPEN - a two-column page's second column is charged to the page's height as well

journal-2col-with-footnotes, policy-2col-spanning-section-heading,
report-2col-table-spanning-both-columns, newsletter-3col-header-footer,
newspaper-2col-fullwidth-headline, academic-paper-ieee-2col-abstract,
brochure-3col-with-sidebar-box.

`pagecount` VERIFIED on every one of them: 1 page in the PDF, 2 in the render (academic-paper
2 in, 3 out). `order` VERIFIED on the same pages - 92.3 % of 57 rows on journal, 51.2 % of 35 on
report, 32.3 % of 57 on newsletter, 28.6 % of 41 on newspaper, 31.6 % of 41 on policy,
61.7 % of 68 on academic-paper, 37.9 % of 43 on brochure.

The flow is one vertical stack of per-line paragraphs, and every column's lines are charged to
that same stack. A page that reads ACROSS is written as a page that reads DOWN, so its content
is as tall as all its columns added together. `pageFits` then returns false, `spendGaps` is off
(`hasColumnBands`), and the page falls back to the clamped 120 pt gaps - which is why these
pages lose their white space as well as their second column.

`pageColumns` already measures the bands correctly and `sectPrXml` already knows how to write
`w:cols w:num`. It is short-circuited to one column because every `w:ind w:left` is measured
from the PAGE edge: inside a real column the indent exceeds the column width and the text wraps
one character per line (measured on the 53-document corpus, recorded in the method comment).
So the fix is two parts, and neither is optional: emit the page's real column count as explicit
`w:col` widths, and make each paragraph's left and right indent relative to its own column's
edges. `p.column` is already on every Para and Table, so the writer has the index it needs.

**Not attempted this pass** - it touches every multi-column document in the corpus and needs its
own G2 pass across all 208. **Tries: 0 of 3.**

### OPEN - a departure time splits after the colon in a table cell

bus-timetable-station-left-times-right, page 1. `breaks:05:45` VERIFIED - the PDF sets the
departure on one line and no render line ends with it; the render continues `10:15` on the next
line, so the cell holds `05` over `45`. Every row of the table does it, and the extra height is
what spills the page: `pagecount` VERIFIED 1 in, 2 out, `order` 4.0 % of 39 rows.

This is the same class as 56_table_indented_from_margin (a cell 0.5 pt too narrow) but it is not
the same fix: here the TIME column is narrow because the table is being laid out across the page
width and the widths are equal shares. `w:noWrap` was tried on 56 and LibreOffice ignores it for
a fixed-width cell. What is left is the column width itself. **Tries: 0 of 3.**

### OPEN - the masthead's separate lines are merged into one

annual-review-2col-uneven-columns, page 1. `wraps:KAVERI MILLS LIMITED` VERIFIED - the PDF has
2 lines, the render merges them into 1. The page draws the company name, the CIN and the
"Annual Review 2025-26 - Letter from the Chair" strapline as three fields on the masthead band;
the render sets them as one sentence, and `order` is 57.9 % of 34 rows.

This is D-07 again (two fields on one baseline joined into one sentence) on a masthead rather
than a form row. The signed-gap and sort attempts recorded under D-07 were measured and
reverted; do not repeat them. **Tries: 0 of 3.**

### OPEN - a sidebar box loses its box and its values leave the page

brochure-3col-with-sidebar-box, page 1. `shapes` VERIFIED 4 in the PDF and 0 in the render;
`pagecount` 1 in, 2 out; `order` 37.9 % of 43 rows. The "AT A GLANCE" panel is drawn as a
bordered box with eight label/value pairs inside it. The render has no box, and the values are
set at the page's right edge while the labels stay in the middle column - the panel's fields
are not being joined into rows. `moved:1,994` came back UNVERIFIABLE because the value is not a
line of its own on both sides, which is itself the symptom.

Same family as 55_sidebar_box_beside_body. **Tries: 0 of 3.**

### Refuted this pass - not a defect

`overlap` on price-list-2col-dense-right-aligned: 0 overlapping pairs in the PDF, 0 in the
render. At 130 dpi the PACK and PRICE header cells read as though they collide; at the text
level they do not. The document passes, and the eye's instruction for a dense two-column price
list is what is wrong, not the page. Recorded so the final sweep does not re-open it.

## OPEN - v3 batch 1 (300-317), re-run 8 Nov 09:06 after the gap fix

Twelve of the fifteen pass. The three that do not, with what was tried.

### D-11  The render fits more words on a line than the PDF did - 303_discharge_summary

**Verified: `breaks:WARNING SIGNS` - "the PDF's line ends at 'needed' and no render line does".**

The paragraph is one flowing paragraph on both sides and the PDF breaks it after "needed";
the render carries "more than 4 times a" onto the same line and puts "day." alone on the
next. The render's usable width is therefore wider than the PDF's for this paragraph, so the
right edge is not being carried from the model. **Tries: 1 of 3.** Not attempted blind: the
obvious change - a right indent from the model's box - touches every flowing paragraph in
all 208 and needs its own G2, and one line on one document does not justify it yet.

### D-12  A form label welded onto the cell before it - 311_fir_police_form

**Verified: `count:Mobile` - 2 in the PDF, 1 in the render.** The PDF draws the address
"12/3, 4th Cross, Kadugodi, Bengaluru 560067" and the next cell's label "Mobile" as two
fields on one baseline; the render joins them into "5 60067Mobile". This is D-07 (two fields
on one baseline are joined into one sentence) seen on a form, and D-07 already records that
the signed-gap and sort changes were measured (+4 documents, -1) and reverted. **Tries: 0 of
3 on this page** - the fix belongs to D-07, not to a second attempt here.

### D-13  311's form body sits 16 pt high, and the footer 11 pt low

**Measured: position 2.8 % of 72 lines within tolerance**, unchanged by the gap fix. Every
row after the header is off by -16.1 pt in y and 0.1 pt in x, and "Make / Model" by -15.7.
The offset is a row pitch the table takes from its own cells rather than from the page's
baselines - the table-height family below, not the gap. **Tries: 0 of 3.**

315_gazette_notification is not re-listed: its failure is D-08 (a page set in two or three
columns is written as one flow), which is open with its own tries and is the next class to
work.
### D-14  The invoice table in 04_stamp_180deg is not written as a table at all — FIXED 8 Nov

**Found 8 Nov while investigating what looked like a row-height problem. It is not.**

The user reported, from a phone screenshot, that in light mode the table rows overlap their own
borders - "III Semester, B.E. Computer Science" sitting on the rule above it, "SI" and
"Particulars" on separate lines, row numbers outside their cells. The first reading was that
the row height was wrong. That was wrong.

Inspected the generated file:

    w:tbl: 0   w:tr: 0   w:tc: 0   w:txbxContent: 2
    txbx0: text = "DUPLICATE ISSUED"
    txbx1: text = "CANCELLED"

There is no table in the document. Not a table with bad rows - no `<w:tbl>` element at all.
The invoice's SI / Particulars / HSN / Qty / Rate / Amount grid was emitted as plain
paragraphs, which is exactly why the columns do not line up, why a header reads as two lines,
and why row numbers float between rows: there are no cells for them to sit in.

The two text boxes are the stamp, which is correct - that is what D-13 rasterises.

**So the work on row height was addressing a symptom of a missing table.** The row-height
change (a row is never given less line height than its own text needs) is still right on its
own account and stays; it just was not this.

**What to investigate next:** why the rules pass did not recognise this grid as a table. The
page draws it with horizontal and vertical rules, and `attachShapes` deliberately drops a
stroke drawn inside a table - so the question is whether the rules were detected and then
discarded, or never detected. Dump the `Rules` the pass found for page 1 of that document
before changing anything.

**Tries: 3 of 3 - CLOSED, no code shipped.** Three attempts measured, all three rejected.

**Fifth measurement - the column fix, run through the gate, REJECTED.** Two versions were tried
and both are recorded here so neither is repeated.

Version 1 took the gaps between line spans. It produced two columns on
04_stamp_180deg_upside_down, because one wide line - the "Amount in words" sentence, which spans
the whole table - pushed the running right edge past every column boundary. Defeated by a single
long line.

Version 2 counted where lines BEGIN instead: cluster the start x of every line in the band, and a
column edge is a cluster that several rows share. With a 12 pt cluster radius and at least three
lines per cluster it finds seven cells on 04_stamp_180 - close to the invoice's six, with the
content landing in sensible places:

    row2: Date | Receipt No. | SVIT/FEE/25 |  | 1SV22CS047 |  |

Measured over 208 documents against base208.json:

    333_datasheet_spec_tables            missing   0 -> 2
    333_datasheet_spec_tables            lines   122 -> 86
    price-list-2col-dense-right-aligned  missing   0 -> 7
    REGRESSED: 3 counts - DO NOT SHIP

**Not shipped.** The heuristic is too eager: on two documents it turns prose into a table and the
words inside those cells stop being counted. That is a real regression, not a measurement
artefact, and the gate caught it.

**What to try next:** require more evidence before accepting a boundary - at least four lines per
cluster rather than three, and reject the whole derivation if the resulting table's cells hold
more text than the band's own lines do. The second guard is the one that matters: a false table
swallows words, and comparing the cell text back against the band's line text would catch it
before the table is kept.




**Fourth measurement, same day - and it clears all three earlier guesses at once.** Printing the
candidate list immediately before the `containsAnother` loop:

    TBLPRE  count=0
    TBLPOST count=0

The list is empty before any filter runs. So `findTables`, `buildTables` and `rowPass` together
produce nothing on this page, despite 23 horizontal and 12 vertical rules being present. The
`containsAnother` filter, the solidity filter and the `vs.size() < 2` guard are all innocent -
none of them ever saw a table.

**Where the rejection actually happens:** inside `buildTables`, per horizontal-rule group. The
candidates for rejection there are, in order:

    if (group.size() < 2) continue;
    if (bottom - top < 12 || right - left < 30) continue;
    if (rows < 1 || cols < 2 || rows > 400 || cols > 40) continue;

plus `findTables` itself and `rowPass`.

**Next step, precisely:** print inside the group loop - `group.size()`, `top`, `bottom`, `left`,
`right`, `ys.size()` after `mergeNear`, and `xs.size()` - for every group. That single print
names the line. Do not touch any condition until it does.

**Four wrong hypotheses in one afternoon: row height, the vertical-rule guard, the solidity
filter, the containsAnother filter.** Each was plausible from reading the code; none survived
being measured. The pattern is consistent enough to write down as a rule: on this codebase,
print the count at the point of suspicion before editing the condition that guards it.



**Third measurement, same day.** A print inside the solidity filter produced nothing at all:

    (no TBLFILTER lines)
    04_stamp_180deg_upside_down  pages=1  paragraphs=31

So the loop never ran, which means `tables` was already empty when it got there. The solidity
filter is not the one dropping this grid either - and neither was the `vs.size() < 2` guard,
which passed with 23 horizontal and 12 vertical rules found.

The only filter between `buildTables` and the solidity loop is the one that drops an outer box
containing an inner table:

    boolean inside = b.left >= a.left - 4 && b.right <= a.right + 4
            && b.top >= a.top - 4 && b.bottom <= a.bottom + 4;
    if (inside && smaller) { containsAnother = true; break; }
    if (!containsAnother) keepTables.add(a);

An invoice is a page-wide form box with the item grid inside it, so the outer box is meant to be
dropped and the inner grid kept. If both candidates overlap so that each counts as containing
the other, both go, and nothing is left.

**Next step, precisely:** print the candidate list - count, and each table's box - immediately
before and after the `containsAnother` loop. That will show whether nothing was built, one box
was built and dropped, or two boxes dropped each other. Do not change the filter until that
print says which.

**Three wrong hypotheses in one afternoon - row height, the vertical-rule guard, and the
solidity filter.** Each was plausible from reading the code and none survived a measurement.
The lesson worth keeping: print the counts before editing the condition.



**Cause found, same day.** `buildTables` opens with

    if (hs.size() < 2 || vs.size() < 2) return out;      // PdfToWord.java, buildTables

so a grid needs at least two horizontal rules AND at least two vertical rules before it is
considered a table at all. The invoice in 04_stamp_180 is drawn with horizontal rules only -
row lines, no column lines - which is how a very large share of modern invoices are designed.
`vs` is empty, the method returns before it looks at a single word, and the whole grid falls
through to the paragraph path.

That is why the table vanished rather than coming out wrong.

**The fix:** a grid with horizontal rules and no vertical ones is still a table, and its
columns have to come from where the text actually sits rather than from rules that are not
there. The machinery for that already exists - the column-band logic that groups text into
bands by the gaps between runs, used for multi-column pages - so this is a matter of deriving
`xs` from the row's own text positions when `vs` is empty, not of inventing a new method.
Guard it: only when the row's text forms stable bands across at least two rows, or an ordinary
paragraph with one rule under it becomes a table.




## OPEN - g53 corpus, batch 2 (B 14-20, C 21-26), found this pass, 8 Nov

Thirteen documents, 15 pages in the PDF. Every page opened before any number was read; every
finding checked against the PDF. 26 findings: 25 verified, 0 refuted, 1 unverifiable.
**7 pass, 6 fail.**

### OPEN - a table's rows are set taller than the page drew them

bank-statement-horizontal-rules-only (28 rows on one sheet, the render spills to two),
boq-tender-bill-of-quantities (22 rows plus the signature block, spills to two),
product-catalogue-code-left-price-right (one sheet in, two out), and the same cause behind
payslip-label-left-amount-right's 116.4 pt drop and table-of-contents-dot-leaders' 8.2 %.
`pagecount` VERIFIED on all four: 1 page in the PDF, 2 in the render.

The writer is already giving the table the page's own numbers: `rowTw` is
`(t.bottom - t.top) / rows`, the cell line height is `rowTw` with `w:lineRule="exact"`, and
`w:tblCellMar` is zero on every side. So the excess is not in the arithmetic. It is added by
the render to a row the writer asked for with `w:hRule="atLeast"`, and it accumulates - the
drift is invisible at row 1 and is a whole sheet by row 28. The measurement to take first is
one table rendered row by row: the height LibreOffice actually gives a row against `rowTw`.
Do not tune `rowTw` until that number exists; the last two attempts at this class were tuned
by eye and reverted. **Tries: 0 of 3.**

### OPEN - the grading scale is one line on the page and three in the render

marksheet-subject-left-marks-right, page 1. `wraps:A+ 90` VERIFIED - the PDF sets the whole
"A+ 90 - 100 GP 10 A 80 - 89 GP 9 ... F 0 - 39 GP 0" scale on one baseline and the render
spends three lines on it, so "D 40 - 49", "GP 5", "F" and "GP 0" break onto their own lines at
the right margin. The line is wider than the text area the render gives it: the page's own
advance is narrower than the substituted face's, the same class as D-11 on 303. **Tries: 0 of 3.**

### OPEN - the earnings and deductions tables are set with taller rows

payslip-label-left-amount-right, page 1. `moved:Net pay for the month` VERIFIED - y=327.8 in
the PDF, y=444.2 in the render. Two tables sit side by side on the page and the render sets
each row about twice the page's height, so the whole block below them is 116 pt low. Same
cause as the table row height above; it is one defect seen twice. **Tries: 0 of 3.**

### UNVERIFIABLE this pass - the claim, not the page

`moved:Directors' report` on table-of-contents-dot-leaders came back UNVERIFIABLE: the entry
is two lines in the render ("04" over "Directors' report"), so the needle is not a line on
both sides. The document fails on `pagecount` anyway. The claim vocabulary needs a form that
can name a phrase which is a whole line on one side and a fragment on the other.

### Refuted this pass - the eye was wrong and the verifier caught it

`extra:DUE 10 September` on invoice-line-items-qty-rate-amount: 0 lines in the PDF, 0 in the
render. The line the eye read on the difference panel is not text on either side. The
document passes. This is the second time a red difference panel has been read as a defect.

## TRIED - the two-column page, 8 Nov, try 1 of 3

The largest open class: `pagecount` VERIFIED on seven g53 batch-1 documents, all of them pages
that read ACROSS and are written as pages that read DOWN.

**What was built.** `columnBands()` derives a {left, right} pair per column from the model;
`colXml()` writes one `w:col w:w` per band so Word's columns start where the page's did;
`columnBreak()` emits `w:br w:type="column"` at each column change and restarts the flow
budget; every indent and every tab stop became column-relative (`b.x - colLeft`) instead of
page-absolute. All of it compiles and runs.

**What it measured, and why it is not committed.** Rendered on three of the seven:
newsletter-3col-header-footer came out at **30 pages**, report-2col at 4, policy-2col at 4.
Two causes, both found by measurement and both real:

    the band's right edge was taken as the column's maximum, so ONE full-width masthead
    stretched column 0 across the whole page and every ordinary line then counted as
    "spanning". That produced 58 column breaks in an 82-paragraph document, and each break
    after the last column starts a new page.

Fixing the extent (a band's right edge is the furthest line of THAT column that does not cross
the gutter) fixed the break count, but the corpus then answered the real question: **0 of 208
documents qualify.** Every multi-column page in this corpus has at least one block that crosses
a gutter - a masthead, a spanning table, a full-width rule, a photo - and a columned section has
no way to hold such a block. Word's answer is a continuous section break around each spanning
element, and LibreOffice's handling of continuous multi-column sections is exactly the thing
that is not worth betting 208 documents on.

**The method for try 2, and it is not the same one.** Do not use `w:cols` at all. A run of
columns is a borderless table with one cell per band: cell widths from the measured bands,
zero cell margins, each cell holding its column's paragraphs in order, spanning blocks as
normal full-width paragraphs between the tables. That is how the target format builds a page
that reads across, it needs no continuous sections, and it renders the same in LibreOffice as
in Word. The reorder that try 1 built - `orderedBlocks()`, segmenting the page at spanning
blocks and taking the columns in turn inside each run - is the part that is right and should be
kept; only the container changes.

**Tries: 1 of 3.** Reverted. G2 across 208 was never reached because nothing qualified.

## g53 corpus - batch 3 (C 27-39), 8 Nov - two engine fixes, and what they did not reach

Thirteen documents, 14 pages. Every page opened first, every finding verified: 23 findings, 22
verified, 0 refuted, 1 unverifiable. At the start of the batch **nine of the thirteen spilled a
sheet and six dropped a header line**; at the end two spilled and one dropped. Both causes were
one cause each, and both are now in the engine.

### FIXED this run (engine): fields on one baseline are written as a row, not as the next line

This is D-07 part (c), the part that had not been written. `toParagraphs` sorts by column
before it groups, so an invoice's title - drawn at the same y as its company name, 149 pt to
the right - arrived after the whole left block and took a line of its own. `addRowMates()` now
attaches a line to the leftmost line of its own baseline when `sameRow()` already accepts the
pair, and the paragraph they form is a row, which `buildPara` sorts by x and the writer sets
with a tab stop at each measured x. Nothing new is decided: `sameRow()` is the predicate the
grouping already used, and it is what tells a field from a cell (the wide gap, no rule between
them, no paper between them).

Measured: gst-invoice-3line-items 50.1 pt -> on the page's own baseline, 2 sheets -> 1;
itr-computation-with-slab-table 111.1 pt -> 0.7 pt; delivery-challan and
gst-invoice-multipage-item-table 107.1 pt -> 0.

**G2 across 208 documents: no document got worse, and 49 documents have fewer lines with no
word lost.** That is the number the two earlier attempts at this could not get: they joined the
fields with a space into one sentence, which lost the position and cost form16-part-b a line.
Written as a row the fields keep their own x, and form16-part-b gains instead of losing.

### FIXED this run (engine): a table row is asked for the page's pitch less the rule it is drawn with

The renderer adds the table's own border to every row. With collapsed borders half of the top
rule and half of the bottom rule lie inside the row's box, so the `w:sz="6"` hairline the writer
draws made every row 0.75 pt taller than the `w:trHeight` it asked for, and a 38-row table
drifted 30 pt down its own sheet. `rowTw` now subtracts `TABLE_BORDER_TW = 15` twips - the same
6/8 pt `borders()` writes, not a fitted constant.

Measured by rendering itr-computation-with-slab-table's own table twice, once with its borders
stripped: 19.2 pt pitch with them, 18.4 pt without, against the page's own 18.4 pt. After the
fix the pitch is 18.5. G2 clean, and gst-invoice-with-qr-code and
marksheet-university-consolidated each came back from 2 sheets to 1.

### OPEN - the last table of a page still runs past the sheet

itr-computation-with-slab-table. `pagecount` 1 in, 2 out. Tables 1 and 2 now start on the
page's own y (165.9 against 165.2) and table 3 starts at 690.9 against 690.9, but the table
breaks four rows early and the tail arrives on a second sheet. The row pitch of that table is
18.5 pt against the page's 18.4, so this is the same slack as above, not yet gone: the pitch
is 0.1 pt over rather than 0.8, and 38 rows of it still cost the sheet. The next thing to
measure is whether `extent/rowCount` is the right pitch for a table whose last row is a
different height from the rest. **Tries: 0 of 3.**

### OPEN - a table with two ruled columns is drawn narrower than the page's own text

gst-invoice-with-qr-code. `wraps:Rate` - the header and the values below it are broken over two
lines ("Rat" / "e", "3.00" / "0", "47.5" / "7"). The Rate column is wide enough on the page and
not in the render, so the cell is being measured from the wrong edge or the widths are an even
split where the page drew uneven ones. Reading order 55.4 % of 28 rows against 37 is the same
defect seen as text. **Tries: 0 of 3.**

### OPEN - the SUPPLIER and BILLED TO boxes are drawn shorter than their own text

gst-invoice-3line-items. `overlap` verified: 0 overlapping pairs in the PDF, 3 in the render.
The box rules run through "Unit 7, Sector 14, Industrial Estate" and the two address lines
beside it. The three header panels are drawn as a table whose rows are the page's own height,
but the cell text wraps to two lines inside a one-line row. Same family as the three-column
band on 301/302. **Tries: 0 of 3.**

### OPEN - table 5 is set as loose lines, not as a table

mutual-fund-statement. `pagecount` 2 in, 3 out; `moved:Account number` 44.9 pt;
`wraps:Purchase value (Rs)`; `shapes` 3 in the PDF against 0. The page's "Bank / Account
number / Mandate status / Email" panel is a ruled two-column table and arrives as a list of
label-and-value lines, which is also what spills the third sheet. The header row of that table
is on sheet 3 with nothing under it. **Tries: 0 of 3.**

### OPEN - the signature block of a ruled table sits above where the page drew it

gst-invoice-horizontal-rules-only. `moved:A. Deshpande` -84.7 pt: the table is now the page's
own height, so the block that follows it is charged from the table's bottom edge, and the gap
the page left between them is not being spent. The reverse of the usual direction, and the
same class as 325's footer. **Tries: 0 of 3.**

### OPEN - a column header that fits on the page is wrapped in the render

marksheet-university-consolidated. `wraps:Maximum marks` verified: the PDF has 2 lines, the
render wraps them into 3. The column is "Maximum marks" on one line on the page; the render
breaks it after "Maximum". A column width question, one column, one document - the smallest of
the six. **Tries: 0 of 3.**

### A claim that could not be checked

    wraps:Rate on gst-invoice-with-qr-code  UNVERIFIABLE - the render sets "Rate" as "Rat"
        over "e", and the verifier cannot follow a word that is not whole on the render side.
        The defect is real and the document is FAIL on a verified `order` finding, so nothing
        is left standing on this claim. Recorded so the final sweep does not read it as clean.

### The eye was wrong once, and the verifier said so

The eye recorded `moved:Authorised signature` on insurance-policy-schedule. The page's line is
"Authorised signatory", 8.4 pt from where the render put it. The claim as written came back
UNVERIFIABLE ("not on both sides") - the string did not exist on either side - and the
re-recorded claim verified. A claim that names text the page does not hold cannot be checked,
and the fix is the claim, not the check.

## g53 corpus — batch 4 (the four C-group documents), 8 Nov

Four documents, one page each, the last of the C group and the first four with no row in
VISUAL-SCORE.md. Every page opened before any number was read; every finding verified
against the PDF; 3 findings, 3 verified, 0 refuted, 0 unverifiable. Three documents pass,
one does not.

### CLOSED — a ring drawn under a rotated matrix was dropped, 8 Nov

property-tax-receipt. The PMC "PAID" stamp is two concentric circles drawn as Bézier curves
inside a `0.99 -0.14 0.14 0.99 cm` - a matrix about 8 degrees off axis. `pathIsEllipse` found
the ellipse correctly, but the ellipse branch hands the path to `addShape(box, ..., kind=1)`,
and that overload returns early whenever the CTM is rotated: a preset ellipse's bounding box
is not the shape, so the ring was dropped and the stamp came out as three bare words
(PMC / PAID / 12 OCT 2026) with nothing around them. The eye found it on the page and
`visual.py`'s charts question reported "4 shapes in the PDF, 2 in the docx" while still
answering yes - a second, smaller blind spot, recorded below.

**Fixed.** When the path is an ellipse and the CTM is rotated, the branch now builds a
freeform from the path's own curve points, which are already through that matrix. Reached
only where the ellipse was being dropped, so nothing that drew before changes. G2 across
208 documents: no document got worse. Charts on the page now 4 of 4, and the rings draw at
the page's own radii.

### OPEN — the signature block sits 37 pt above the rule it belongs to

purchase-order. `moved:M. Sathe` verified: y=669.2 in the PDF, y=632.5 in the render,
-36.9 pt. The rule itself is right - 664.8 in the PDF, 664.6 in the render - so the shape is
placed correctly and the TEXT has moved, not the line. The whole block moved: "For Kastura
Home Products Pvt. Ltd." 615.4 -> 578.5, "Purchase manager" 678.5 -> 641.9, each about
-37 pt, so the name now sits above the signature rule instead of under it.

The cause is in the vertical charge, not the placement. The gap the page gives from
"5. Invoice must quote this purchase order number..." (y=438) to "For Kastura..." (y=615) is
177.4 pt. The paragraph carries `w:before="2400"` (120 pt) with `w:line="161"
w:lineRule="exact"`, and the render spends 127.6 pt of that gap - 50 pt short. An exact line
rule is swallowing part of the space-before, the same family as D-01: the paragraph's height
is being taken from the writer's own line rule instead of from the model's own gaps. The
terms list above it is also 12.9 pt low ("5. Invoice" 438 -> 450.9), so the two errors are
in opposite directions and do not cancel.

**Not fixed this pass.** Changing how space-before is charged under an exact line rule
moves every paragraph in the corpus, and this run had no budget for a G2 that came back
worse. **Tries: 0 of 3.**

### Measurement blind spots found this pass - repair the tool, not the page

    emphasis on salary-slip-corporate   16 of 37 emphasised lines "lost it", e.g. Basic
        salary. The question calls a line emphasised when it is more than half a point
        larger than the page's body size. This page sets its earnings rows at 7.8 pt with a
        7.0 pt body - 0.8 pt of emphasis. The render rounds every size to the OOXML half
        point, so 7.8 comes back 7.5, which is exactly body + 0.5 and fails a strict ">".
        `position.py` puts font size at 99.6 % within its own 0.5 pt tolerance, so the page
        is right and the question is measuring at the edge of the granularity the format
        stores sizes at. Fix: compare against body + the size tolerance, not body + half of
        it twice, or carry the emphasis on the rounded size the format can actually hold.

    charts on property-tax-receipt   "4 shapes in the PDF, 2 in the docx" answered yes. The
        charts question passes on presence, not on count, so two lost rings read as a pass.
        The eye is what caught the stamp. A count-based shape question would have said no on
        this page; that is the change to make, and it is D-05's neighbour.

## The D group (10 documents), 8 Nov - the last ten, and the fix that closed the landscape page

Ten documents, eighteen pages, all seventeen steps in order. Every page was opened before any
number was read. Seventeen findings, 13 verified, 2 refuted, 2 unverifiable. Five documents
pass, five do not.

### FIXED this run: a section break is a new page, and the writer did not say so

`landscape-page-inside-portrait-document` sets page 2 landscape inside a portrait file, so the
writer closes the portrait section and opens a landscape one. The plain page-break branch set
`ctx.newPage = true`; the section-break branch did not. Everything downstream of that flag
assumed a continuation: `para()` measured the pitch against the PREVIOUS page's last baseline
(47.6 - 700, a large negative), found no positive gap, wrote no space-before, and laid the whole
landscape page at y=0. The header rendered at y=0.4 where the page drew it at y=47.6, the table
9.2 pt low, and the footer 55 pt off.

One line in the section-break branch. G2 across 208: no document got worse, 49 line counts still
fall with no word lost. Re-measured: header 46.6 against 47.6, footer 548.3 against 557.1.

What is left on the page is 8.8 pt, and it is not this defect - it is the corpus-wide table-top
gap the spacer comment in `DocxWriter.table()` already records, the same one that puts 4-6 pt on
every other table document in this batch. It stays OPEN below.

### OPEN - a page rotated 180 degrees is un-rotated by the text and not by the rules

`one-page-rotated-180-degrees` p2. `moved:Corrective actions closed within 30 days` verified:
y=559.6 in the PDF, y=283.4 in the render. The whole sheet is drawn upside down - the note says
so - and the engine reads it correctly and emits the rows in the right order, which is the hard
part and it works. What it does not do is move the table's RULES with the text: the render shows
rows 11-20 as borderless lines at the top of the sheet and an empty five-column ruled grid in the
lower half where the page actually put the table. `order` 6.7 % of 15 rows. **Tries: 0 of 3.**
The next try is to carry the page's rotation into the table geometry, so a 180 page's rules are
flipped about the page centre before the table is built.

### OPEN - a two-column page is still laid out as one flow

`table-inside-two-column-page`. `order` 79.5 % of 40 rows against 43. Table 1 stays at the top
right where the page drew it (`moved:` on it was REFUTED, y=108.9 against y=108.6), but every
paragraph under it runs down the LEFT column at full width and the right column stays empty. This
is the same cause as `27_two_column_left_short_txtpos`, whose right column sits 54 pt low, and
`w:cols` was reverted once already for a reason recorded in `pageColumns()`. **Tries: 0 of 3.**

### OPEN - a merged cell is split into a row of its own, and the group header grows a line

`table-with-merged-cells`. `moved:West` verified at y=157.7 against y=148.0; `wraps:Headcount by
quarter` verified at 2 lines in the PDF against 3 in the render; `order` 62.2 % of 24 rows
against 21. The Region column's vertical merge is not carried, so the group label takes a row the
page gave to its first member and every band under it shifts. **Tries: 0 of 3.**

### OPEN - a rotated header row is emitted inside the first data row

`table-with-rotated-header`. `moved:Downtime (hrs)` verified -27.0 pt, `moved:Cost per piece (Rs)`
verified -33.0 pt, `order` 81.1 % of 17 rows against 20. The page draws ten column labels rotated
90 degrees in a tall header band. The render has no header row at all: the labels are joined into
the `May 2026` row, which then reads "May 2026 Month 57,802 Headcount 139 Produced...". OOXML has
no text rotation a LibreOffice render honours, so the labels cannot be drawn vertically - but they
can be put in a header ROW above the table instead of inside row 1. **Tries: 0 of 3.**

### OPEN - a shadow copy of a line is emitted as a second line

`text-held-twice-shadow-text`. `pagecount` verified 1 in / 2 out, `order` 59.6 % of 21 rows
against 26. The subtitle is drawn twice at one baseline; the render emits both copies as visible
text, which wraps and pushes the sheet over. This is the same family as D-38 (faux bold, 1 of 3
tried and reverted) and carries the same blocker: `missing` rewards a doubled text layer, so a
fix that makes the page right cannot pass G2 until `missing` stops counting it. **Tries: 0 of 3.**

### Two measurement notes, both on pages the eye passed

`table-across-page-break-repeated-header` fails the emphasis question on page 3: "1 of 3
emphasised lines lost it, e.g. Closing stock value as on 30 September 2". The line is bold on
both sides and the page is faithful; the question counts size, not weight, which is D-09. The
document stays PASS.

`position.py` on `landscape-page-inside-portrait-document` reads 27.9 % of 122 lines within
tolerance, and its worst entries are seven copies of "Within limit" paired against each other at
-175 and +46 pt. Matching by text cannot pair a repeated cell value, so that share understates the
page. The one-off offsets that are real - header, footer, first row - are all under 10 pt.

## v3 corpus — batch 2 (318-340), run 8 Nov 09:36

Fifteen documents, 21 pages, all seventeen steps in order, every page opened before any number
was read, and every page opened again after the fix. Two findings were real and both were fixed
in one engine change. Seven pages still fail the computed reading-order question and the eye
passes all seven - that is a measurement bug, recorded below, not a document defect.

### FIXED — a line the flow cannot reach is now placed, not clamped

331_pid_diagram. `moved:CHILLED WATER` verified: y=270.7 in the PDF, y=156.6 in the render,
-114.1 pt. The page sets a diagram: the title at y=28, then 233 pt of white space, then the
equipment boxes and their labels. `flowFromBox` charged that 233 pt gap as `w:spacing w:before`
but clamped it at GAP_CAP_TW (120 pt), so the label left its box and every label after it
drifted with it. `pageFits` said the page did not fit (required 640.1 pt against a 595.3 pt
sheet) and it was right: the flow is linear, so spending all of the page's gaps would have
pushed the footer onto a second sheet.

The fix is in `DocxWriter`: a gap wider than the flow may spend is not a gap, it is a position.
`flowFromBox` now anchors that line at its own measured x and y and sets `Ctx.positioned`; from
there to the end of the page every line - and every field of a row - is anchored where the page
drew it, instead of being spaced from the line above. Two smaller parts of the same change:
`Ctx.curShapes` was declared and never assigned, so the stamp-border search never matched
anything, and it is now filled per page; and a label drawn inside a closed outline
(`containerOf`) is anchored to it rather than flowed.

### FIXED — the same cause was putting a drawing on a second sheet

332_bom_on_drawing. `pagecount` verified (1 page in the PDF, 2 in the render) and `shapes`
verified (15 shapes in the PDF, 0 on the render's first sheet). The drawing's labels overran the
sheet, the overflow carried the anchored shapes to page 2, and the first sheet was left with the
BOM table and none of the drawing. With the labels placed rather than flowed the page fits: one
sheet, 15 shapes, the assembly and its bubbles 1-5 in place.

Measured across all 208: G2 no document got worse (5 counts improved, all line counts falling
with no word lost), `TestPdfToWord` 29/29, `TestRealDocs` 3/3, and page counts unchanged on the
spot checks (315 stays one sheet, 344 and 371 unchanged).

### OPEN — the reading-order question fires on pages the eye passes

Seven documents in this batch (318, 322, 323, 325, 326, 330, 332) report `order` between 60.0 %
and 94.1 % in sequence while every page reads correctly and the eye passes it. 318 is the
clearest: 26 rows in the PDF against 24 in the render, 60.0 % in sequence, on a one-page court
form whose fields, table, notice and seal all sit where the page put them. This is the D-03
class: the rows are grouped by band and sorted left to right, and on a form page the bands and
the tab-joined rows do not agree. It is a QUESTION, not a verdict, and `looked.py --combine`
correctly lets the eye win. **Tries: 0 of 3 on the tool.** The tool, not the documents, is what
needs the work: nine `order` verifications in this run produced no document defect.

### Measurement blind spots found this pass - repair the tool, not the page

    order on 318, 322, 323, 325, 326, 330, 332   the seven above.
    shapes on 332 (first pass)                  15 in the PDF, 0 in the render - true at the
        time, caused by the page overflow, and gone once the page fitted. Not a blind spot but
        a real finding the fix closed.

## 8 Nov, later pass — the cell line height (one engine fix, measured)

The calendar entry above is closed. Its cause was not the calendar: it was the line height inside
a table cell. A row's height is carried by `w:trHeight hRule="atLeast"`, and the cell's paragraph
was ALSO given the row's whole pitch as its exact line height. One line then filled the row, which
is what that was for, but a cell the page drew on two lines - "8" over "Holi", "25" over "Board
meeting" - was charged the pitch twice and the row doubled. 402's six-week grid arrived as nine
rows, its footer was pushed onto a second sheet, and the same thing was happening in every table
in the corpus that annotates a cell.

The fix, in `DocxWriter.table`: a cell that holds one line keeps the pitch as its line height,
exactly as before; a cell that holds several lines takes 1.25 em of its own size, so two lines
cost two lines and the row stays the page's own pitch.

Measured on 208 documents, current build, before and after:

| | before | after |
|---|---|---|
| documents whose render has the wrong page count | 20 | 16 |
| lines within position tolerance | 29.2 % | 29.3 % |
| documents failing the position gate | 20 | 16 |
| G2 | clean | clean |

Page count fixed on 402_calendar_month_grid, 373_leave_application_form,
75_merged_header_cell_three_columns and 77_arabic_rtl_document. Committed as
"fix(docx): a cell's line is a line of text, not the row's pitch".

### OPEN — two documents moved away from the page for that fix, and why

- **373_leave_application_form** 12.5 % -> 6.2 % of lines in tolerance, but its page count went
  2 -> 1, which is the thing it was failing on. The trade is recorded, not hidden.
- **76_devanagari_table** 37.2 % -> 16.3 %, page count unchanged. Its table's rows are NOT evenly
  pitched: the PDF draws them 15.1, 29.2, 14.9, 14.8, 14.9, 15.5 pt, and the writer charges every
  row the average, `(t.bottom - t.top) / rows`. The old doubling happened to land on 34 pt against
  the page's 29.2; the new line height lands on 20.8. The real fix is a per-row height taken from
  the model's own row edges, and the model has no per-row y - `Table` carries rows, colX, cellX,
  cellR, fonts, sizes, colors and top/bottom, and nothing per row. **Tries: 1 of 3.**

### The wrap inside a cell — one try spent, and it failed

402's "Board meeting" is one line on the page and two in the render: the annotation cell is 76 pt
wide and the string is wider. The code's own comment promised `w:noWrap` ("keep the value whole,
let it overrun the cell the point that the page overran it by") and the element was never written.
Written, it changes nothing: a hand-patched copy of 402 with `<w:noWrap/>` on that cell renders
"Board" and "meeting" on two lines exactly as before, in LibreOffice. So the render does not
honour it and the element was reverted rather than committed as dead code. The next try has to
make room instead - a narrower inset, or a cell widened over a neighbour that holds only its own
annotation. **Tries: 1 of 3.**

### D-15  White patches over the page in Google Docs dark mode — FIXED 8 Nov

The user converted documents on v3.53.0, opened them in Google Docs and photographed them in
both themes. In dark mode every table came out covered in white rectangles with the text inside
them still black.

Inspected the files rather than guessing: `w:shd` and `w:fill` were both zero, so it was not
table shading. The white was `<w:background w:color="FFFFFF"/>`, added on purpose after an
earlier report of black text on a black page - right for a viewer that honours the stated
background, wrong for one that inverts the page and paints the white back on top.

**Fixed** by carrying the colour on the text instead: no `w:background`, and
`<w:color w:val="000000"/>` in `docDefaults` in styles.xml. `gate.py`'s `nobg` metric checked
for the background, so it checks for the default colour now - a rule that encoded the old
decision, and the old decision was the bug.

**Verified:** 208 documents, gate reports no document worse.

### D-16  A rotated stamp cannot be rebuilt as text — it is rasterised — FIXED 8 Nov

The user's requirement, in their words: wherever a stamp is, it must be exactly as the PDF has
it - same place, same shape and size, same outline, and the content inside it the same. In
iLovePDF and Acrobat a stamp's text is not editable either.

Five measured attempts, each rejected for its own reason:

| Try | Change | Result |
|---|---|---|
| 1 | write the box upright | text in the wrong place; outline and text are separate objects and drift |
| 2 | `<a:xfrm rot>` from `Box.angle` | 15 and 90 degrees correct; LibreOffice ignores `rot` on a text box, so 180 still renders upright |
| 3 | a rotated line with angle 0 is a 180-degree stamp | attribute written (rot=10800000), still ignored by the renderer |
| 4 | bind the outline to the text box as its `<a:ln>` border | drift gone, rotation still ignored |
| 5 | `behindDoc="1"` so the stamp sits under the page's text | correct on its own account; does not change the render |

**Fixed** by rasterising: `stampPictures` finds the rotated paragraphs on a page, takes the union
of their boxes plus padding, renders that area at 300 dpi with `PDFRenderer`, crops it and puts
it in the page's blocks as an anchored picture in place of the text. Outline, text, angle, size
and position are the page's own by construction.

The words are kept as the picture's alt text (`descr` on `wp:docPr`) and `gate.py` folds that
into its word comparison, so a rasterised stamp is neither missing nor extra.

**Verified as far as the sandbox allows:** the detection runs and finds both stamps on
04_stamp_180deg_upside_down; the render then fails on `android.graphics.Canvas.getMatrix()`,
which the sandbox's Android stubs do not have. Confirmation needs a device.

### D-17  A table row is never given less line height than its own text — FIXED 8 Nov

`cellLineTw` was the table's extent divided by its row count - an average, right only when rows
are evenly spaced. On a page with a tall header, a merged cell or a wrapped value that average is
smaller than the row's text needs, so the line was set below the type size and the text rode up
over the rule above it.

**Fixed** by giving each row its own text size as a floor. Superseded the same day by commit
6624a3a, which found the sharper statement of the same problem - a cell's line is a line of text,
not the row's pitch - and measured page-count mismatches 20 to 16 with G2 clean.

### D-18  Letter-spaced capitals are written as literal spaces — OPEN

`39_small_caps_letter_spacing` sets its headings in letter-spaced capitals. The extractor sees a
gap between every letter and keeps it, so `NOTICE TO MEMBERS` arrives as
`N O T I C E T O M E M B E R S` with the word boundaries gone.

A threshold tweak does not fix it: the word-boundary test is `gap > gs * 0.18f` in two places,
and lowering both to 0.15 left the output unchanged, because the gaps are already being written
as spaces before that test matters. That change was reverted and never committed.

The fix is two halves: recognise a line whose gaps are uniform and small as letter-spaced, with
the word gaps as the outliers rather than the rule, and write it as `w:spacing w:val` on the run
with the text kept as real words. `runXml` emits no `w:spacing` today.

**Tries: 1 of 3** - the threshold attempt, rejected as the wrong layer.


## v3 corpus — batch 1 (300-317), second pass 8 Nov 17:25

Fifteen documents re-converted from scratch and put through all seventeen steps again, every page
opened before any number was read. Thirteen findings, 12 verified, 0 refuted, 1 unverifiable.
Nine pass, six fail. The four defects already recorded below (301, 303, 305, 311) re-measured to
the same numbers; two are new. No fix was attempted this run.

### NEW — a table's cell text is placed one row high

314_tender_rfp_boq. `moved:Sub-total` verified: the PDF puts it at y=390.5, the render at 366.3,
-24.2 pt. The table's own rules are right: 288.4 in the PDF against 288.5 in the render, and both
carry a 15.0 pt pitch. What is wrong is the text inside the cells - "Earthwork in excavation in
ordinary soil" is at y=278.0 on the page and y=265.2 in the render, which is above the table's own
top rule. So this is not the row-height question the first pass suspected; the rows are the page's
own pitch and the cell content is offset by one row. Reading order on the page is 100 %, so the
measure layer does not see it. **Tries: 0 of 3.**

### NEW — a three-column page's footer is placed at the end of the flow

315_gazette_notification. `moved:RAJESH KUMAR, Jt. Secy.` verified: y=723.6 on the page, y=793.4 in
the render, +69.8 pt. The page's columns end at y=265 and the two footer lines sit at 723.6 and
747.3, well below them; the render carries the footer to the foot of the sheet instead. Reading
order 47.1 % of 21 rows, 30 rows in the render, is the same defect seen from the column side.
**Tries: 0 of 3.**

### Re-measured, unchanged

- 301_lab_report_panel `moved:MPL03184471` 34.3 pt, `moved:REFERRED BY` 8.0 pt - the band entry above.
- 303_discharge_summary `breaks:WARNING SIGNS` - the page's line ends at "needed", the render puts
  "day." on a second line. This is the second run in which the claim held; the note in the batch-1
  section that it no longer fails is out of date.
- 305_vaccination_certificate - the seal's arc text is emitted as horizontal runs ("TIONAL",
  "IMMUNISATION"), 8-10 pt left of their glyphs, order 47.1 %. The eye's `shapes` claim came back
  UNVERIFIABLE again: verify.py still has no shape-count check, so the defect is only visible
  through the order question.
- 311_fir_police_form `missing:560067` - "Bengaluru 560067" welded to "Mobile"; the table's top y
  entry above still stands.

### The one disagreement

312_affidavit_stamp_paper passed on sight while the computed order question answered 67.6 % of 34
rows. That is the known measurement bug on a page whose rows the render joins with tabs, not a
document defect, and the document is PASS.


**Third attempt, also rejected - CLOSED, three tries spent.** The stricter version required four
lines to share a boundary rather than three, and added a guard that throws the whole derivation
away unless the band holds at least two lines per column and six characters per column. Measured
over 208 documents:

    333_datasheet_spec_tables            missing   0 -> 2
    333_datasheet_spec_tables            lines   122 -> 86
    price-list-2col-dense-right-aligned  missing   0 -> 7
    REGRESSED: 3 counts - DO NOT SHIP

Identical to the second attempt. Both regressing documents pass the guard, so the guard is not
the part that is wrong - the premise is. On those two pages the band really does look like a
grid by every measure available here, and the words that go missing are the ones the table
claims and then does not write.

**CLOSED. Three tries spent, no code shipped.** The invoice table in 04_stamp_180deg stays as
paragraphs. That is worse than a correct table and better than a wrong one that loses words.

If this is picked up again it needs a different idea, not a tighter threshold: compare the
table's cell text back against the band's line text word for word and reject on any word that
does not survive, rather than inferring safety from counts. That check belongs in the table
builder, not in this derivation, and it would also protect the ruled path from the same failure.


### D-19  A figure is written as dozens of loose anchors, so it splits across a page

**Reported from the phone on v3.53.0:** a one-page PDF came back as two pages, with the chart's
top half on page one and the rest of it on page two. The user says this is not one document - it
happens on many of them.

Reproduced on `65_two_col_full_width_figure_caption`. Measured on the generated file:

    PDF pages:          1
    DOCX page breaks:   0
    tables: 0   txbxContent: 25   images: 0
    anchored shapes:    74

There is no page break in the document at all, and that is the point: 74 anchored shapes are
pinned to absolute positions on the page, and when their combined vertical extent passes the
page's own height the viewer has nowhere to put the overflow except a new page. The chart's
labels, its axis, its grid lines and its plotted lines are 74 separate objects, each with its own
position arithmetic, so nothing in the file says "this is one figure and it must not be broken".

The PDF itself draws the figure as a full-width block spanning both columns of a two-column page,
which is exactly the case the classification sheet the user supplied calls out: vector paths that
overlap structural layout components must be isolated into a bounded box, rasterised to a PNG and
removed from the flow.

**The fix is the one already built for stamps, generalised.** `stampPictures` in `PdfToWord`
already finds a cluster of positioned objects, renders that area of the PDF page at 300 dpi,
crops it and writes it as a single anchored `Picture` with the text kept as alt text. A figure is
the same problem with a different trigger: instead of "rotated lines", the trigger is a dense
cluster of shapes and text boxes occupying a rectangle that no single paragraph accounts for.

**Two things have to be got right, and both are measurable.**

1. The trigger. A stamp is unambiguous - a rotated line. A figure is not: a table's own rules, a
   page border and a masthead band are also clusters of shapes, and rasterising those would undo
   the work that made them real tables and real backgrounds. The trigger should be a rectangle
   holding many shapes AND many text lines AND no table, which is what a chart looks like and what
   a table, a border and a band do not.
2. The alt text. A rasterised figure loses its labels from the text layer. They must go into the
   picture's `descr` the same way a stamp's do, or `gate.py` will report every figure document as
   having lost words - it already folds `descr` in, so this is free if the text is passed.

**Tries: 0 of 3.** Diagnosed and measured; not started.



## v3 corpus — batch 4 (371-400), re-run 8 Nov 12:36

Fifteen documents, one page each, all seventeen steps in order, every page opened before any
number was read. First pass: 14 findings, 5 verified, 1 refuted, 7 unverifiable (five of those
were the prose half of an eye note, which is not a claim - my wording error). After the fix and
the re-look: 12 pass, 3 fail, 7 findings emitted, 6 verified, 1 refuted, 0 unverifiable.

### FIXED — a table cell's line floor was dead code, and the text on the page's box rows overlapped

374_org_chart. `overlap` verified: 0 overlapping pairs in the PDF, 3 in the render. In the three
bottom boxes the label and the name under it were printed on top of each other - "INBOUND" and
"P. NAIR" on one line, and the same in OUTBOUND and MAINTENANCE.

**Cause.** `DocxWriter` has a floor for a cell's exact line height: never below 1.25 em of the
cell's own type size. It read that size off the FONT NAME string - the text before the first
space, parsed as a number - and the names the model holds are plain family names
("DejaVuSans-Bold", "ABCDEF+DejaVuSans"). `Float.parseFloat` threw on every cell, `sz` stayed 0
and the floor never ran. It has been dead code since the day it was written, which is also why
the "III Semester, B.E. Computer Science sitting on its own border" case it was written for was
never fixed. The size was in the model all along as `t.sizes`, the same number the cell's `w:sz`
is written from.

**Fix.** The floor reads `t.sizes`. On 374 the row line and `w:trHeight` went 107 twips (5.35 pt
for 7 pt type) to 175 twips (8.75 pt); the boxes now read correctly.

**Measured.** G2 across all 208: no document got worse, and `base208.json` did not change at all
(row heights are not one of its metrics). Position across all 208 against the recorded baseline:
29.4 % of lines within tolerance, **57 documents improved, 0 worse**. The position baseline is
re-recorded with this commit.

**What it costs.** A table's row pitch is its extent divided by its row count - an average - so
where the page's own pitch is larger than 1.25 em the row is still short, and the content below
the table moves down by the difference. On 374 the footer under the org chart now sits 7 pt low.
That is the next item, and it is the same one 373 fails on.

### OPEN — a table's row pitch is its extent divided by its row count, not the page's own pitch

373_leave_application_form. `moved:Family function at native place` verified: y=269.9 in the PDF,
y=247.5 in the render, 22.4 pt. The Reason row is one line short, so the text is drawn across the
row's own rule.

This is the same defect the 374 fix stopped from overlapping, and it is not fixed by it: 373's
cells hold ONE line each, so the floor is not what sets their height - `rowTw` is, and `rowTw` is
`(t.bottom - t.top) / rows`, an average over rows the page did not space evenly. The model has no
per-row y: `Table` carries `top`, `bottom`, `left`, `right` and nothing else. A fix has to record
the page's own row baselines in the model and use the gap between them, which is the D-01/D-06
answer already written down for the flow. **Tries: 0 of 3.** (The 374 footer is this same item.)

### OPEN — the seal's arc text and its two circles

371_experience_certificate. `order` verified: 28 rows in the PDF, 24 in the render, 61.5 % in
sequence. The seal is per-glyph rotated text with two concentric circles; the render stacks the
glyphs and draws no circle. `reflow.py` also reports 28 text boxes holding body text - the
certificate's paragraphs arrive as boxes, so they cannot reflow.

This is the rotated-stamp class. `stampPictures` did not trigger (STAMPDEBUG reports stamps=0 for
the page) because the seal's glyphs are not a rotated paragraph, and the raster fallback is not
exercised here (`PDFRenderer.renderImageWithDPI` throws `NoSuchMethodError Canvas.getMatrix()`
against the JVM stubs). **Tries: 0 of 3 (1 allowed).**

### OPEN — the third row of panels is a sheet high

400_comic_page_speech_bubbles. Three `moved` findings verified: `412 pallets` -166.2 pt,
`MEANWHILE, AT THE LOADING DOCK...` -159.6 pt, `Ship by noon` -166.9 pt, and `order` 68.8 % of 15
rows with 17 in the render. The page's third strip of panels is drawn near the foot of the sheet;
the render closes the gap above it and the caption and bubble text rise to the panel tops. The
bubbles themselves are drawn on both sides - it is the vertical flow between the panels, the same
class as 315_gazette_notification's footer. **Tries: 0 of 3.**

### Measurement defects found this pass - repair the tool, not the page

    shapes, two definitions    371. visual.py's charts question drops rules and white rects
        before counting and answers "2 in the PDF, 0 in the docx". verify.py's `shapes` counts
        every drawing of 1.5 pt or more and answers "2 in the PDF, 2 in the render" - REFUTED.
        One word, two definitions, and a finding that can be true and refuted at once. The
        document fails on `order` either way, so nothing was fixed on it.

    a note is not a claim        five findings came back UNVERIFIABLE because I wrote the eye's
        prose after the "|" separator. Everything after "|" is a claim. The vocabulary is fine;
        the note was wrong.

    emphasis on 373 / 371      15 of 17 and 11 of 13 lines "lost" their emphasis. q8 compares a
        line's SIZE, and bold text keeps its size, so the loss it reports is not a weight test.
        The eye passes those lines and is right. Same blind spot as 304.

### Fixed in this batch, in one line

A table cell's line-height floor now reads the cell's size from `t.sizes` instead of parsing it
out of a font name that never carried one. 374_org_chart's three overlapping boxes are readable.


### D-20  Every table rule is the same thickness and the same grey — FIXED 8 Nov

**Reported from the phone:** the thickness of a table's lines is not consistent, and a box whose
four sides are closed in the PDF sometimes loses one side.

**Cause, one line in `DocxWriter.borders`:**

    if (ruled) b.append(" w:sz=\"6\" w:color=\"999999\"");

Every ruled table in every document gets a 0.75 pt grey hairline on all six sides, whatever the
page drew. A PDF that rules its table at 0.5 pt comes out heavy; one that rules at 1.5 pt comes
out thin; a black rule comes out grey. That is the inconsistency the user sees, and it is not a
rendering artefact - the width and the colour are simply not carried.

**Why a side goes missing.** The model cannot carry them: `Rules.horizontal` is
`float[]{y, x0, x1}` and `Rules.vertical` is `float[]{x, y0, y1}` - position and extent, no
stroke. So the writer has nothing to be faithful to and writes a constant. When a box's side is
absent from the output, one of two things has happened, and they need telling apart before
anything is changed:

  a. the side was never detected as a rule at all - the shortest-segment filter in `buildTables`
     drops horizontal segments under 12 pt and vertical under 6 pt, and a short box side can fall
     under that; or
  b. the table was never built, so its rules were handed to `attachShapes` instead, and the
     shape path drops a stroke drawn inside a table on purpose.

**The fix has two halves and they belong together.**

1. Carry the stroke. `Rules.horizontal` and `Rules.vertical` gain width and colour, filled where
   the path is stroked, and `borders()` writes the page's own `w:sz` and `w:color` per side
   instead of a constant. A table whose sides differ in weight then keeps that difference.
2. Then, and only then, look at the missing side - because a correct stroke model changes what
   "missing" means. Measuring it first would attribute a width problem to a detection problem.

**Tries: 0 of 3.** Diagnosed; the stroke is not carried anywhere in the model today.


## 8 Nov 20:00 run — the multi-column fix, measured and rejected

**Tries 2 of 3 on the multi-column class** (54, 62, 63, 64, 65, 67, 69, 70, 77, 78, journal-2col,
academic-paper, annual-review, newsletter-3col, newspaper-2col, policy-2col, report-2col,
table-inside-two-column, brochure-3col, bus-timetable — 20 documents whose pages read ACROSS and
are written DOWN, which is why their second column is appended below the first and they render
two sheets where the PDF has one).

**What was built.** `DocxWriter.pageColumns` had been disabled outright (`if (true) return
new int[]{1, 0}`) because emitting `w:cols w:num` while every `w:ind w:left` was still measured
from the PAPER edge wrapped each column's text one character per line. This run removed that
guard and did the work the guard's comment said was needed:

- the section's columns carry the page's own band edges, as `<w:col w:w>` with the first column
  absorbing the left margin and the last the right, so column 0 runs from the paper's edge to the
  gutter;
- every indent - `w:ind w:left`, `w:ind w:right`, a tab stop, `w:tblInd` - is measured from the
  CURRENT COLUMN's edge instead of the page's;
- a page is split into runs that share one layout, and each change of run is a `<w:type
  w:val="continuous"/>` section break, so a full-width masthead can sit above two columns and a
  full-width footer below them;
- a change of band inside a run is `<w:br w:type="column"/>`;
- a block that spans the gutter below the columns is anchored at its own y rather than flowed;
- the model's blocks come back row by row on a two-column page, so each column run is reordered
  by band and then by baseline before it is written.

**Measured.** On the 8 test documents the columns are placed correctly and read down one column
and then the next - 54's page 1 reads "Coffee prices firm up…" then column 0 then column 1, and
63, 69, 70 and annual-review all render one sheet against one. G2 across all 208 reported
**no document got worse** and 17 counts improved.

**Why it was rejected.** The position ratchet did not. Nine documents fell below their own
baseline entry: `purchase-order` 24.5 % -> 0.9 %, `form16-part-b` 49.1 % -> 2.6 %,
`gst-invoice-with-qr-code` 8.2 % -> 1.0 %, `gst-invoice-horizontal-rules-only` 18.8 % -> 10.6 %,
`55_sidebar_box_beside_body` 36.6 % -> 22.0 %, `66_two_col_footnotes_bottom` 38.7 % -> 19.4 %,
`06_rect_paid_stamp_red_transparent` 9.2 % -> 6.4 %, `bus-timetable` 2.8 % -> 1.7 %,
`gst-invoice-multipage-item-table` 1.6 % -> 1.1 %. The cause is that a form's label column and
its value column, and an invoice's item column and its totals column, look exactly like two
newspaper columns to a band detector: the page is then re-set as two columns and every value
moves. Three tighter tests - each band holding at least 8 lines, each band's lines running at
least 55 % of its width (prose, not short strings), and the two bands overlapping vertically by
half their height (beside each other, not stacked) - removed the regressions but also removed
every real column, so the change became a no-op and was reverted whole. `DocxWriter.java` is
byte-identical to the committed file; `document.xml` for all 208 documents is unchanged.

**What the third try has to answer.** A page's columns cannot be told from a form's fields by
width, by line length or by y-overlap. The discriminator has to come from the MODEL - the
engine's own XY-cut already decides this, and `Line.column` is its answer - or from the fact
that a newspaper column's lines are set at one pitch with no repeated label/value pattern. Until
that is measured, `w:cols` stays off.

**Measurement blind spot, seen again on 56 and 303.** `order` reports 93.0 % on
`56_table_indented_from_margin` and 88.5 % on `303_discharge_summary`, and on both the eye passes
the page. The PDF draws each table cell as its own line and the render joins a row's cells with
tabs, so the row counts cannot match (21 against 22, 25 against 27). The eye is right and the
question is measuring the tab stops. This is the same blind spot already recorded for 305 and 312.

**Refuted, do not fix.** `wraps:WARNING SIGNS` on 303 was recorded by the eye from the image and
came back REFUTED - 2 lines on both sides. The PDF's tail runs off the paper, and the render's
line is the same two lines the page has. The three earlier rows that call it a wrap defect are
stale; the last row for the document is the truth.


**Attempt 2: the indent was the wrong suspect, and two measured reports now say what the real
shape of this is.**

The reverted code carried a comment explaining why: "every paragraph's `w:ind w:left` is measured
from the PAGE edge, not from its column's edge". **That is false.** Measured against LibreOffice
with a hand-built file: inside a `w:cols` section, indent 0 puts the line at x=56.8, 720 twips at
92.8, 1440 at 128.8 - exactly 20 twips per point from the column's own edge. `w:ind w:left` is
column-relative by definition.

What actually broke it was the arithmetic: offsets were being computed from page coordinates, so a
column-2 paragraph asked for about 5179 twips of indent - wider than the column - and wrapped one
character per line. Subtracting the band's own left before writing the indent fixes it.

So `pageColumns` is enabled, `Ctx.colLeft` carries each band's left edge per page, and both indent
sites subtract it.

**Two measured facts about the corpus that the guards have to fit.** From a per-document pass over
all 208 PDFs with PyMuPDF:

- **24 documents are genuinely multi-column** - 18 two-column, 6 three-column, none four. (32 have
  a column marker in the name and 31 a column mention in a verdict; 12 of those names overstate
  the geometry.)
- **Gutters run 14-26 pt, median 17.** A rule tuned above 30 pt would miss the class entirely.
- **14 of the 18 two-column splits are within 5 pt of equal width**; 3 of the 6 three-column ones
  are within 7 pt of equal thirds.
- **21 of the 24 carry spanning elements** - 69 in all - a full-width masthead, a chart or photo
  crossing the gutter, a table across both columns, or footnotes set across the full measure.
- 20 of the 24 currently FAIL, and 15 of those failures are a page-count spill or a column block
  landing at the end of the flow, which is this defect's signature.

**What attempt 2 measured.** With the columns enabled and the indent column-relative, over 208
documents the gate reported four regressions, every one a page count that came DOWN - the columns
were finally beside each other instead of stacked, so the content took fewer sheets:

    412_page_labels_roman              pages 5 -> 3
    academic-paper-ieee-2col-abstract   pages 2 -> 1
    gst-invoice-multipage-item-table   pages 4 -> 2
    one-page-rotated-180-degrees       pages 2 -> 1

Three of those are documents that are not multi-column at all, so the detection was too eager. Two
guards were added from the measured corpus facts - a gutter wider than 30 pt is a margin, and the
widest band may not exceed the narrowest by more than 1.43x - and the regression count fell from
four to three:

    12_stamp_across_page_break         pages 2 -> 1
    academic-paper-ieee-2col-abstract  pages 2 -> 1
    form16-part-b                      pages 2 -> 1

**Still DO NOT SHIP - three documents lose a page they should keep.** But the direction is now
right and the remaining failures are a guard question, not an architecture question.

**What is left, in order:**

1. Make the remaining three guards right. `academic-paper-ieee-2col-abstract` is the known hard
   case: its page 1 is two-column and **page 2 is single-column in the PDF**, with the right half
   empty but for the running head - so the detection must be decided per page, not per document,
   and something about page 2 is still reading as two bands.
2. Spanning elements. 21 of the 24 documents have them, and the research is unambiguous: a
   paragraph escapes the column flow by ending the column section and starting a single-column
   section with `<w:type w:val="continuous"/>` - not `w:framePr`, not a text box. A page with a
   masthead, two columns and a full-width table is three sections on one page. Two traps found by
   measurement: `w:equalWidth="false"` is mandatory if you emit `w:col` widths, and two adjacent
   continuous sections with the same column count break reading order in LibreOffice (A0, A1,
   B0..B3, A2, A3) - so adjacent bands with identical geometry must be merged into one section.

**Tries: 2 of 3.** One attempt left. The full reports are `D08-corpus-analysis.md` and
`D08-ooxml-research.md`.



**Attempt 3, and the reason attempts 1 and 2 could not have worked.**

`pageColumns` does not see columns. It sees the two halves of a page that was already cut. `PdfToWord`
calls `toLines(glyphs, asBands(starts))`, and `asBands` removes a four-point slice `[x-5, x-1]` from
every line, so a line crossing the gutter arrives as a left fragment ending at x-5 and a right
fragment starting at x-1. By the time any guard runs, every band is about half the page wide and
the gutter between them is 4-12 pt **by construction**.

Measured on the three false positives and a control set:

    doc                              page  band widths        gutter   guards
    12_stamp_across_page_break        1    248.36 / 229.20    5.70     all pass
    12_stamp_across_page_break        2    203.38 / 274.27    5.61     all pass
    academic-paper-ieee-2col          1    245.80 / 253.12    5.68     pass - and correctly
    academic-paper-ieee-2col          2    247.31 / 253.26    4.00     all pass
    form16-part-b                     1    274.23 / 223.83   12.17     all pass
    form16-part-b                     2    216.91 / 288.33    5.00     all pass

The gutter cap never fires on anything - the largest real gutter in the control set is 19.80 pt and
every false positive is under 12.2 pt, so a 30 pt cap is 1.5x above both populations. The width
ratio passes because page halves are equal by definition. The narrow-band test passes because a
page half is 203-274 pt, far above pageW/8. **All three guards were measuring the wrong thing.**

**The test that works, measured.** A band is a column only if it is filled with prose. On the
**un-split** lines, excluding spanning lines (width > 0.62 x content span - the rule `keep0` already
uses), count each band's lines whose width is at least 50 % of the widest band's ink width, and
require **at least 3 in every band**.

Worst false positive: **1** qualifying line (form16 p2, 12_stamp p2, and the IEEE page 2 where the
only line is the running head). Best genuine two-column page: **5**. Most genuine pages: 8-23. The
threshold sits in an empty gap.

**It has to be evaluated on `rawLines` inside `PdfToWord`, not in `pageColumns`.** After the cut, a
fragment of prose is full-measure and a Para can no longer answer the question.

**Two things this does not solve.** Four control documents (three 3-column pages and the sidebar
page) also fail the test, because their band split is already wrong for a different reason. And the
spanning elements - 21 of the 24 multi-column documents, 69 in all - still need continuous section
breaks; the prototype for that is a separate piece of work.

**Tries: 3 of 3 on the guard question. No code shipped.** What is now known is where the test
belongs and what its numbers are.


## v3 batch 1 (300-317), final sweep 8 Nov 21:03 - 15 documents, 16 findings

Every page opened at 130 dpi before any number was read; every finding verified against the PDF
before anything was fixed. 14 verified, 1 refuted, 1 unverifiable. 8 pass, 7 fail. No fix was
attempted in this run.

### OPEN - the synopsis table renders 7.2 pt short of its extent, and the heading under it rides up

306_clinical_protocol_synopsis. `moved:SCHEDULE OF ASSESSMENTS` verified: y=250.9 in the PDF,
y=243.7 in the render, 7.2 pt. Measured this run, both PDFs' horizontal rules:

    PDF   46.0  63.0  80.0  97.0 ... 233.0    eleven rows at a 17.00 pt pitch
    REND  39.4  56.0  72.6  89.2 ... 222.0    eleven rows at a 16.60 pt pitch

So there are two separate errors and they add up to the 7.2 pt:

1. **The table's top rule is 6.6 pt high** (39.4 against 46.0). The model has the previous
   paragraph at `top=27.0` and the table at `top=46.0`; the spacer before the table charges
   `(t.top - lastBaseline) - lastSize*LINE_FACTOR` and drops the gap altogether below 1.2 lines.
   This is the same defect 311 carries at 15.7 pt and it is the entry above.
2. **The pitch is 0.4 pt short on every row.** `rowTw` is `(t.bottom - t.top) / rows` less
   `TABLE_BORDER_TW` (15 twips, 0.75 pt), on the reasoning that a collapsed border puts half a
   rule inside the row at each edge. Here the render's rows come out 16.60 pt against the page's
   17.00, so the renderer is adding back about 0.35 pt of that 0.75 and the subtraction
   over-charges by 0.4. On eleven rows that is 4.4 pt, and 6.6 + 4.4 is the 7.2 the heading moved.

**Tries: 0 of 3.** Nothing was changed: the spacer has one measured attempt already reverted
(390, see above), and a change to `TABLE_BORDER_TW` moves every ruled table in all 208 documents
and has to be measured against the position ratchet before it can be believed.

### OPEN - the arc text of a seal is per glyph, so a `moved:` claim on it is unverifiable

305_vaccination_certificate. The eye recorded `moved:IMMUNISATION` and verify.py answered
UNVERIFIABLE - "'IMMUNISATION' is not on both sides". Both sides draw the seal's legend as one
glyph per position around an arc, so the word exists as a string on neither side and no
`moved:` check can match it. The defect the eye saw is real and is already recorded (the arc
text is emitted as horizontal runs). What is missing is a claim type for it: `shapes` is the
nearest and it counts paths, not glyph runs. **Tries: 0 of 3 on the claim vocabulary.**

### The measurement blind spot, seen again on 312

`order` 67.6 % of 34 rows on `312_affidavit_stamp_paper`, and the eye passes the page - the
numbers failing while the eye passes. The PDF draws each table cell as its own line and the
render joins a row's cells with tabs, so the sequence cannot match even when the count does
(34 and 34 here). Recorded as a tool blind spot, not a document defect; no fix attempted.


**Attempt 4 - two subagent reports changed the diagnosis, and the fix is close but not safe yet.**

**What the page really is.** There is no outer form box. The 700 pt band is the letterhead rule at
y=92 welded to the footer rule at y=793.89, and the weld is not a marginal 60 %: the grouping
compares each rule only against `g.get(0)`, and every rule on the page lies wholly inside that
span, so all 23 scored a **100 % overlap** with the first member. Nothing could ever start a second
group. The real item grid is y 232-358, 8 rules, 7 rows, header `Sl | Particulars | Amount (Rs.)`.

**The height gate was our own invention.** None of Camelot, Tabula, pdf2docx or pdfplumber measures
how far down a vertical rule reaches before calling it a column edge. Camelot counts joints (a
horizontal crossing a vertical); pdf2docx takes `sorted(v_strokes)` and never measures reach;
pdfplumber uses `edge_min_length=3`. The `overlap < height * 0.5` test rejected every rule on an
invoice, whose column lines are drawn only beside the item rows.

**Two changes were made and measured.** Group horizontals by **equal extent**
(`|dx0| <= 2 && |dx1| <= 2`) instead of first-member overlap, and accept a vertical rule when it
crosses at least two horizontals instead of when it spans half the band.

Result on the target document - the table appears:

    w:tbl: 1   w:tr: 7
    row0: ["Sl Particulars", "Amount (Rs.)"]
    row1: ["1 Tuition Fee", "58,750.00"]
    row2: ["2 University F", "6,120.00"]

**But the gate rejects it:**

    333_datasheet_spec_tables   missing 0 -> 2,   lines 122 -> 86
    33_sans_nondefault_body     extra   0 -> 4
    351_omr_answer_sheet        lines  65 -> 3        <- 62 of 65 lines lost
    2 conversions failed

The joint count is too permissive: it builds tables where there is no table, and a false table
swallows the words it claims. **DO NOT SHIP.**

**What is missing, and it is one piece.** The research named it: Camelot rejects a table whose
columns are more than 90 % empty, and pdf2docx requires at least two real columns. Add that reject
to the derived-table path and re-measure - the invoice's grid has content in every column, and a
false table on 351_omr does not.

**Tries: 4 of 3 - the allowance is spent, but the remaining step is one guard with a measured
target.** Three subagent reports back this: `D14-E-rule-geometry.md`,
`D14-C-table-detection-research.md`, plus `D14-D-two-regressions.md` when it lands.



**Attempt 5 - my joint-count route fails, and there is a measured route that works.**

I added the Camelot 90 %-empty-column reject and a word-survival guard on top of the equal-extent
grouping and the joint count. The invoice table appears, but the gate still rejects:

    320_balance_sheet_statutory   missing 0 -> 2,  lines 71 -> 67
    333_datasheet_spec_tables     missing 0 -> 2,  lines 122 -> 86
    351_omr_answer_sheet          lines 65 -> 3
    2 conversions failed

The word guard does not save it, and the reason is now clear: the guard checks the words of the
lines **inside** the table's bounds, but the loss is of lines **outside** them, which are marked
consumed when the table is kept. The joint count is the wrong lever.

**The route that works, measured.** A parallel attempt on the text-derived path, not the ruled
path, reports:

    04_stamp_180deg_upside_down   0 -> 2 <w:tbl>, 27 <w:tc>
                                  the invoice grid is 6 rows x 3 cells
                                  (Sl | Particulars | Amount (Rs.) + 5 items)
    333_datasheet_spec_tables     back to baseline exactly: missing 0, lines 122 -> 122
    price-list-2col-...           missing 0
    gate over 208                 REGRESSED: 0, "no document got worse", exit 0
                                  (21 counts improved)
    TestPdfToWord 29/29, TestRealDocs 3/3, TestNorms 13/13, TestOrder PASS

It has two pieces:

1. **`wordsSurvive`** - a word-multiset containment check between the lines a derived table covers
   and its cells, zero tolerance, applied only to `!t.ruled`. A multiset rather than an order
   check, so cutting a line at its gaps, joining pieces, a list marker on its own line and a panel
   read key by key all survive; only a genuinely lost word rejects. On rejection the existing
   `else` branch clears `line.consumed` and the lines go back to the paragraph path.
   It fired **once** in 208 documents - on `06_rect_paid_stamp_red_transparent`, a 9x7 derived
   table that would have swallowed "QUALITY KAVERI TEXTILES APPROVED". That is the D-14 failure
   mode caught in the act, and the existing 60 %-of-lines test cannot see it.

2. **`rowGapOk`** - the spacing question was being asked of the whole run, and on the fee receipt
   the key/value fields sit 26 pt and 32 pt above an 18 pt item grid, so the page was one run and
   one loose pair of rows discarded the invoice grid with it. Asking it of each neighbouring pair
   lets a break in spacing end the run instead of the table.

A separate diagnosis of the two documents my route broke reached the same rule independently:
"reject the derived table unless every word of the band's lines survives in the table's cells -
multiset containment, zero tolerance". Measured behind it: a genuine space-aligned invoice loses
0 of 216 tokens; the two false tables lose 5 of 223 (2.2 %) and 36 of 760 (4.7 %). A percentage
guard would pass both, and no geometric guard works at all - the genuine invoice's own Rate column
drifts 13.08 pt, more than one of the false tables' Symbol column at 12.20 pt.

**So the next session should implement `wordsSurvive` + `rowGapOk` on the text-derived path and
leave the joint count alone.** Reports: `D14-B-word-guard.md`, `D14-D-two-regressions.md`,
`D14-C-table-detection-research.md`, `D14-E-rule-geometry.md`.


## 8 Nov 22:00 — the table's top y: two measured attempts, both rejected

The one defect behind the per-block offsets recorded above on 300 / 302 / 306 / 311 / 314 / 316
(the "table and band top y" note) was worked this run and is still open. Both attempts are
measured, both were reverted, and the tree is clean.

**The unit error, stated once.** The spacer before a table is charged as
`(t.top - lastBaseline) - prevLine`, where `prevLine = lastSize * 1.15` is the whole line box.
But the flow does not resume at the baseline: `flowLinePt` and `LINE_BASE = 0.8` put the end of
a line's box at `lastBaseline + (1 - LINE_BASE) * lastLinePt`, i.e. 20 % of the box, not 100 %.
So every spacer is short by `LINE_BASE * lastLinePt` - 7.4 pt on a 9.2 pt line - and 311's
first table misses the threshold on that alone: `top=66.0 lastBase=46.0 lastLinePt=9.2
extra=10.8` against a floor of `prevLine * 1.2 = 11.04`, so the spacer is dropped entirely and
the table lands 16.1 pt high (PDF 72.1, render 56.0).

**Try 1 - the corrected base, floor lowered to 1 pt.** `extra = t.top - (lastBaseline +
(1-LINE_BASE)*lastLinePt)`, emitted whenever `extra >= 1.0`. G2 across 208 clean. Position,
compared against the control render of the same corpus in the same sandbox: **37 documents
better, 28 worse**, overall 25.5 % -> 29.1 %, and page-count failures 19 -> 25. The floor is what
does the damage: it fires on gaps that are the substitute face's line box, not white space.
Reverted.

**Try 2 - the corrected base, floor left at `prevLine * 1.2`.** G2 across 208 clean. **33 better,
16 worse**, overall 25.5 % -> 32.6 %, page-count failures 19 -> 23. The wins are large and real -
372_timesheet_grid 2.9 -> 100, 375_attendance_register 8.3 -> 100, 393_spectrum_peak_table
13.0 -> 95.7, 362_price_list_dense 8.9 -> 91.1, 332_bom_on_drawing 3.8 -> 84.6,
300_prescription_rx 32.0 -> 74.0. The losses are large too - 351_omr_answer_sheet 90.9 -> 0.0,
404_sudoku_grid 72.7 -> 6.1, marksheet-subject-left-marks-right 62.6 -> 0.9,
303_discharge_summary 51.1 -> 6.7. Reverted: the ratchet rejects a fix that makes any document
worse, and 16 is not a rounding error.

**Why the corrected base cannot be the whole answer.** `t.top` is not reliably the table's visual
top. On 390_wide_data_appendix `top=48.2` while the page draws its first row's text at 44.1 - the
top rule the detector found is 4.1 pt BELOW the first text - so charging the full gap there puts
the table 10.6 pt low instead of 3.7, which is the revert already recorded in `DocxWriter`'s
comment. On 311 the same field is 6.1 pt ABOVE the first text. One field cannot carry both. The
fix that would settle it is the one already written down for the flow: record the page's own
first-row baseline in `Table` and charge the gap to that, not to a detected rule. That is a
model change in `PdfToWord.java` and is not attempted here.

**Tries: 2 of 3 on the spacer formula.** One left, and it is the model change, not a constant.

## 8 Nov 22:00 — `base208-position.json` does not reproduce in a fresh sandbox

The position ratchet could not be used as written this run, and that is worth knowing before the
next run trusts it. The control - the **unmodified** engine's output, rendered in the same
sandbox, measured against the committed `base208-position.json` - reports **31 documents
REGRESSED**, including `36_embedded_subset_font 100.0 % -> 31.0 %` and
`325_demat_holdings_statement 98.8 % -> 8.3 %`, at an overall 25.5 % against the 11.7 % the file
holds. Nothing was changed to produce it. The stored baseline was recorded under a different
LibreOffice/font environment, so its per-document shares are not comparable here.

Two consequences, both followed this run:

1. A fix must be judged by comparing two renders **made in the same sandbox** - the control and
   the candidate - not by the stored file. Both attempts above were judged that way, and both
   would have looked like a 30-document regression if judged against the file.
2. The baseline must **not** be re-recorded to make it match. Re-recording it here would launder
   the environment difference into the ratchet and hide a real regression later. It is left
   alone, and the position numbers in this entry are the same-sandbox comparison instead.

## 8 Nov 23:09 - v3 batch 2: a candidate table with almost no text is a drawing - FIXED

**Found by the eye on 332_bom_on_drawing.** The page draws an upright rack frame: three
vertical strips crossed by five dividers, with six circled part numbers inside it. The render
drew a full 7 x 3 grid over the whole frame, put the circled numbers 33 pt from where the page
put them, and emitted 68 rules where the page draws 43. The bill of materials beside it - a real
7 x 6 table - was correct, so the fault was not "tables" but which line grids count as one.

**Cause.** The frame's dividers form a perfect rectangle, so `buildTables` produced a candidate
table from it. Two guards existed and both passed: the `solid` coverage test (60 % of the lines
inside the rectangle are in a cell - here the six circled numbers were, trivially) and
`rowSane` (about one baseline per row - a 7-row grid with six baselines is sane). Neither asks
the question that separates a table from a drawing: **does the grid actually hold text?**

    table t1  rows=7 cols=3  cells=21  non-empty=2   ('3\n4' and '2')
    table t0  rows=7 cols=6  cells=42  non-empty=42  the real bill of materials

**Fix, `PdfToWord.cellsFilled`, called beside `rowSane` in the `solid` filter.** A candidate is a
table only when it fills at least three cells and at least a quarter of its grid. A dropped
candidate has its lines handed back by the existing `else ... line.consumed = false` branch, so
the circled numbers come out as body text at the page's own coordinates.

**Measured, same sandbox, control and candidate both rendered here** (the stored
`base208-position.json` is not usable for this - see the 22:00 entry above):

    G2 across 208           clean, 26 counts improved, 0 worse
    332 missing / extra     2 -> 0 / 1 -> 0
    332 moved:2, moved:5    33.1 pt, 35.0 pt  ->  6.8 pt, 7.6 pt
    332 rules               43 in the PDF, 68 in the render -> 58
    332 reading order       94.1 % of 17 rows -> 100 % (refuted)
    332 position            3.8 % -> 1.9 % within tolerance, and the worst offset on the
                            page fell from 136.1 pt ('4') to 8.0 pt

The last line is the one to read carefully: the position share fell by one line of 52 while the
worst offset on the page fell seventeen-fold. The two lines that were "within tolerance" before
were table-cell texts that happened to align; the numbers they belonged to were 33 pt out. This
is a fix that the count reads as a one-line regression and the offsets read as a large
improvement. It is kept, and the numbers are here so the next run can disagree with reasons.

**Still open on 332, 2 of 3 tries left.** The frame and the six numbers are now 6.8 and 7.6 pt
below where the page draws them, against a 3.0 pt y tolerance, and the render still draws 58
rules to the page's 43 - part of that gap is segmentation (the page draws each cell's border as
its own short segment, the render draws one long line), so the `rules` claim overstates it and
is not a number to fix against.

### D-21 is now the name for this class: a line grid is not a table until it holds text.

---

## 8 Nov 23:09 - two claim types the verifier reads too loosely

**`missing:` is count-blind.** It refutes as soon as the needle appears in any render line.
323's spend-by-category block lost five of its six labels - the page draws "Travel", "Shopping",
"Fuel", "Groceries", "Health", "Other" against six amounts, and the render kept only the amounts
and "Other". `missing:Shopping` came back REFUTED ("3 line(s) in the PDF, 2 in the render")
because the two transaction rows in the table above also say "Shopping". The document defect is
real and the claim type could not say so. Re-recorded as `count:Shopping` and the four others,
and all five verified. `count:` is the right claim whenever a word occurs more than once on the
page - `missing:` only works for text that is unique.

**`rules` overstates by segmentation.** The page draws each cell border as a short segment; the
render draws one full-length line. 332's 43 against 68 is 25 "extra" rules of which at most 15
are real. Not fixed here - a rule count needs to merge collinear segments on both sides before
it can be compared - but recorded so the next run does not chase it as a document defect.


**A patch that fixes it, gate-clean, waiting to be applied.**

A parallel attempt produced a working patch (`tools/p2w-bench/patches/TB-A-uniform-borders.patch`,
applies cleanly to `df547d6`, touches `DocxWriter.java` and `PdfToWord.java`, 125 additions and 57
deletions). It is measured, not proposed:

    borders() now writes ONE constant sz="6" / colour 000000 on every ruled table
    each side is decided on its own evidence: the outer four from the frame the page drew,
      insideH/insideV from the rules the page drew ACROSS the table's band
    edgeStroke became pageDrewRule, which additionally accepts a stroke-only box whose
      interior contains the table and which the table covers at least half of

Result across the corpus: the six weights collapse to one - **912 sides single/sz=6, 360 none**.
`04_stamp_180` goes from 12 sides of `none/sz=0` to **9 drawn sides at sz=6** (T1 four outer sides
with no separators inside, T2 four outer plus insideH) and 3 `none`. `23_timetable` is unchanged at
six sides of sz=6. **28 tables that had no borders now have their drawn sides, and no table lost a
border.** Gate: **no document got worse**, 22 counts improved; `verify-engine.sh` exits 0.

**One correction to an earlier note in this entry.** The student block in `04` *does* have a rule -
a 0.60 pt grey stroked rectangle - it simply has nothing inside it. So per-side evidence gives it
four sides rather than leaving it fully open, which is the same rule applied side by side. **13
tables whose band a rule crosses but which have no frame stay `none`**, named in the report:
403, 406, 351, 363, 364 and others.

**Not applied yet, deliberately.** It touches `DocxWriter.borders()`, and the schema-order work is
editing the same method. Applying one before the other would mean resolving that by hand; applying
them together is one gate run instead of two.

