# REMAINING-DEFECTS

The live parking record for the current round. A class that parks writes here - what
was tried, what was ruled out with numbers, what is still untested, what would settle
it. Old corpora are in REMAINING-DEFECTS-ARCHIVE.md and no run needs to read them.

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


## Class 20_within_10pt — OPEN, reopened 10 Nov; model measured, fix attempted and reverted

### Attempt 12 Nov — the advance mechanism measured, body-only conversion reverted

The 10 Nov reading was re-measured from scratch with three probes that differ only in how one
12 pt advance is written, and it holds exactly:

| probe | written | advance measured |
|---|---|---|
| A | `w:line=240` exact, `w:before=0` | **11.5 pt** (asked 12) |
| B | `w:line=14`, `w:before=226` | **11.99 pt** |
| C | `w:line=1`, `w:before=239` | 12.64 pt |

So the advance is `w:before + 0.069 em`, face-independent, and `w:line` is a multiple of the
substitute face's line height. A body line written the way the engine writes it today loses 4 %
of its pitch on every line, which is the drift: the flow creeps up the page and the deeper the
page, the further it has gone.

`DocxWriter.googleBox()` was added and applied to the two page-body emitters (`flowFromBox`,
`flowRow`) only, leaving the internal `before + line` accounting, the page-fit guard, the table
edge and the cell path untouched. Twenty documents went through Drive.

| document | `20_within_10pt` before | after | score |
|---|---|---|---|
| 62_two_col_newsletter_pull_quote | 7 | **100** | 41/59 |
| balance-sheet-and-profit-loss | 7 | **53** | 38/59 (was 39) |
| 362_price_list_dense | 1 | **15** | 51/59 (was 50) |
| 390_wide_data_appendix | 1 | 1 | 49/59 |
| electricity-bill | 6 | 6 | 45/59 |
| 57_centred_title_page_left_body_pages | 0 | 0 | 47/59 (was 48) |
| 311_fir_police_form | 3 | 7 | 45/59 (was 47) |
| 332_bom_on_drawing | 4 | 4 | 46/59 (was 48) |
| report-2col-table-spanning-both-columns | 4 | 7 | 47/59 (was 48) |
| 70_magazine_drop_cap_photo_caption | 4 | 4 | 46/59 (was 46) |
| 305_vaccination_certificate | 100 | 46 | 35/59 (was 36) |
| 325_demat_holdings_statement | 99 | 100 | 47/59 (was 51) |
| 15_stamp_on_scanned_page | 0 | 0 | 40/59 (was 42) |
| the eight remaining control documents | 100 | 100 | unchanged |

`classify.py --attempt` computed **3 of 18 moved (17 %) -> reverted**. Eight of the twenty scored
lower than baseline: the flow is placed 0.2 em lower than the model believes on every line, which
put 311 and 332 onto a second page (`01_page_count`, `24_page_breaks`, `55_orientation_mix`) and
cost `27_text_off_page`, `39_image_position`, `44_header_footer` elsewhere. The engine change was
reverted with `git checkout -- app/src`.

**What this rules out:** converting the page-body flow alone. The three documents that moved are
the three whose lines are body text; `electricity-bill` and `362_price_list_dense` are table
documents and barely moved, because their lines are `rowLineTw` cell paragraphs this change never
reached. **What is still untested:** the same hairline-plus-`w:before` model in the cell path,
together with a correction for the 0.2 em the box gives back when it becomes a hairline.

The largest open class in `BASELINE.md`: **107 of the 208 measured documents fail
`20_within_10pt`**. The 10 Nov closure of this class ("Google Docs has no exact line spacing") was
wrong and is withdrawn: Google Docs does have exact line spacing, it just does not read
`w:lineRule="exact"` the way Word does. What follows was measured through Drive on purpose-built
probes and then on real documents, and it replaces the earlier reading of the same evidence.

### The model, measured

A probe of one paragraph style, one face, eight identical lines, zero margins, rendered through
Drive and exported as PDF. Three variables were moved one at a time.

**1. `w:line` is a MULTIPLE of the face's own line height, not a height.**
At 10 pt Arial, boxes of 240/300/360/480/600 twips came back at 11.5/14.37/17.25/23.0/28.75 pt -
a constant 0.9583 of the value asked. The same probe at 14 pt came back at 1.3417 of it and at
20 pt at 1.9167. So

    rendered advance = (w:line / 240) * lineHeight(face, size)

and the ratio is the face's line height over 12. It is the RUN's size that sets it, not the
paragraph mark's: a paragraph with mark 10 pt / run 10 pt and one with mark 20 pt / run 10 pt both
advance by 0.069 em of 10 pt, while mark 10 pt / run 20 pt advances by 0.069 em of 20 pt. The face
matters as much as the size - at 10 pt, `w:line`=240 measured 11.5 for Arial, 11.45 for Times New
Roman, 10.49 for Courier New, 11.7 for Times-Roman, 12.23 for Helvetica, 12.77 for Liberation
Serif - and those are the PDF's own font names, which Google substitutes. **No `w:line` value can
place a baseline without knowing the substitute face's line height.**

**2. `w:before` is honoured exactly, in points.** 20 pt came back 20 pt; 40/80/120/160 pt came
back 40/80/120/160 pt. It is the one vertical length Google reads as a length.

**3. With the box cut to a hairline, the advance is `before + 0.069 * size` - font-independent.**
`w:line="1"` with `w:before`=20 pt came back at 20.55 pt at 8 pt, 20.69 at 10 pt, 20.97 at 14 pt,
21.38 at 20 pt, and 20.68 for Courier New and 20.69 for Times New Roman at 10 pt: 0.069 em, to
0.01 pt, whichever face is substituted. A hairline box does not clip - 20 pt text in a 1-twip box
came back 22.34 pt tall, the face's full glyph height - and LibreOffice renders the same probe at
`before + 0.1` with full glyph height, so the two engines agree to a tenth of a point.

Also measured: the first baseline of a page sits 0.0565 em below the paper's top edge (0.45 pt at
8 pt, 0.56 at 10 pt, 1.13 at 20 pt), independent of the box height; and the first baseline of a
table cell sits 0.92 em below the row's top edge, which is where this writer has always put it.

### What that means for the two engines

    Word / LibreOffice   advance = w:before + w:line
    Google Docs          advance = w:before + (w:line/240) * lineHeight(face, size)

These are equal for every size and every face only when `w:line` is small enough to hit Google's
floor, i.e. a hairline box. The earlier note in this file concluded that "no `(w:line, w:before)`
pair is exact in both engines"; that is true of the pairs it tested and false of `w:line`=1, which
is why the class is open again rather than closed.

### The fix that was tried on 10 Nov, and why it was reverted

The flowing-line model in `DocxWriter` was rewritten to the measured one: every flowing line
carries a hairline box (`w:line = 0.069 em` in twips) and an absolute `w:before` measured from the
reader's real position, with the first line of a page placed at 0.0565 em and the first line of a
cell at 0.92 em. `precommit --no-corpus` exited 0 and the engine's own suite passed (81 + 188 + 41
+ 29 checks). Twenty documents - the ten that fail this check and little else, plus ten that
already scored well - were converted, put through Drive and scored.

| document | `20_within_10pt` before | after | other checks |
|---|---|---|---|
| 34_monospace_document | 14 % | **100 %** | 31/31 |
| 321_auditors_report | 56 % | **100 %** | 31/31 |
| 26_footnote_marker_bottom_note | 74 % | **100 %** | 30/31 |
| 18_centred_heading_left_body | 100 % | 100 % | 31/31 (median dy 4.7 -> 0.4) |
| 313_power_of_attorney | 100 % | 100 % | 31/31 (median dy 3.0 -> -1.1) |
| 316_contract_with_schedules | 57 % | 57 % | 30/31 (worst dy 16.3 -> 11.4) |
| 27_two_column_left_short | 94 % | 94 % | **lost** line_pitch, ink_where_blank |
| 31_times_body_arial_headings | 93 % | 66 % | **lost** text_overlap, blank_where_ink |
| 35_four_typefaces_one_page | 100 % | 50 % | **lost** within_10pt, blank_where_ink |
| 33_sans_nondefault_body | 49 % | 49 % | **lost** worst_dy |
| 361_product_catalogue_grid | 97 % | 97 % | **lost** text_overlap |
| 414 / 415 (image pages) | 0 % | 50 % | **lost** line_pitch |

Five of the ten failing documents went to a full 31/31 and two more improved their median dy by
3-4 pt, but seven documents got worse on at least one check (583 -> 583 checks passed overall),
so the change was reverted under the ratchet. The regressions are all in the paths the rewrite did
not reach: columns and table cells, where the cell's own flow state (`ctx.flowY`) and the
`afterTablePt` edge were only partly converted, and the image pages, where the first line's gap is
measured from an anchored shape rather than from a baseline.

**So the class is fixable and the mechanism is now measured; what is missing is the same model in
the cell, column and anchored-shape paths, and a pass that proves the 208-document corpus does not
move backwards.** A rewrite that reaches only the page body buys 5 documents and costs 7.

