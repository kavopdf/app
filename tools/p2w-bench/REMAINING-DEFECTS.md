# Remaining defects — to be worked at the very end

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

### D-01  Vertical drift: every line sits higher than the PDF drew it, and the error grows down the page

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


### D-06  Twenty-eight documents spill onto more pages than the PDF has

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

28 of the 208 documents fail this way. `gate.py` counts page breaks it finds in the
XML and reports 537 against the PDFs' 540, so three documents lose a page while these
28 gain one - the two errors were hiding each other in the total.

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
