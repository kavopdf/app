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


## THE MEASUREMENT IS NOT TRUSTWORTHY YET - read this before you believe any class number

63 checks were audited on 13 Nov against seven defect shapes found in one of them. **15 were
fixed. About 15 are still open.** They are listed here so you know which numbers to distrust,
not so you fix them.

**DO NOT EDIT `verify_google.py` OR `verify_txt.py` TO MAKE A CLASS PASS.** The checks are the
measurement. A class that goes green because the ruler moved is worse than a class that stays
red, because nobody will ever look at it again. The remaining verifier defects are being fixed
as pipeline infrastructure, by whoever owns the pipeline, not by a fixer run.

### What was already fixed, and what that means for your numbers

Fifteen defects across ten checks, in commits 87a08d1, 62a1792, c4b379a, 57f521d and 229faa9:

    53_embedded_faces   seven defects - the check could not pass a correct conversion
    28_clipped_at_edge  failed a document against its own copy
    47_margins          a lone space at x=0 failed 182 of 187 documents
    08_image_count      counted the resource dictionary, not drawn images
    02_text_run_count   failed a document for splitting a run in two
    11_bold_runs        same
    39_image_position   a set numerator against a list denominator
    42_alignment_mix    every block gave a 'left' by construction
    44_header_footer    a hard boundary with no tolerance

**Consequence: every class number in DEFECT-CLASSES.md was produced by a ruler that was wrong in
at least one of those ways.** `47_margins` failed 182 of 187 documents partly because of a space.
`53_embedded_faces` read 141 because 10 Nov rows scored 100% and 11 Nov 99% against a blind
normaliser; on the 17 rows measured after the fix, 1 failed. Treat the current class list as a
starting point, not as fact, until the baseline re-measures on the current engine.

### Still open, and which class numbers they make suspect

| check | rows it decides | what is wrong | what a fix would have to decide |
|---|---|---|---|
| `59_shape_anchor` | 110 of 187 | pairs source runs to render runs **by index**, not by text. One rect with "Alpha"/"Beta" drawn in reverse order gives source=2 render=0 and fails, with the text unmoved and 18_median_dy at 0.0 | whether to pair by text like `_pair_runs` does, and what to do when a run has no match |
| `32_stroke_lines` | 145 of 233 | counts drawing **paths**, not rules. Seven hairlines as seven paths vs one path with seven subpaths gives 7 vs 1. Worse: `_strokes` keeps a drawing only if `color is not None`, so rules drawn as **filled** 0.8 pt rects count as zero and are invisible to 14, 32, 33 and 36 at once | whether a thin filled rect is a rule, and how to group subpaths |
| `41_block_spacing` | 81 of 233 | measures how the extractor **grouped blocks**, not the spacing. Identical glyph rows grouped as `[72,90,200,218]` vs `[72,90,200]` read 18 vs 110 | whether spacing can be measured from baselines instead of block tops |
| `45_char_accuracy` | 24 of 233 | drops whitespace-only spans and joins with no separator, so segmentation changes the answer; and `quick_ratio` is order-blind, so reordering cannot be seen | what "character accuracy" should mean when 22_reading_order already owns order |
| `t04_structure` | 137 of 208 | compares **baselines** against **txt lines**. A 20-row table transcribed to one line reads 20 vs 1 and passes; one baseline of 8 cells transcribed faithfully to 8 lines reads 1 vs 8 and fails | what the txt row unit is |
| `37_super_subscript` | 229 vacuous | only the superscript flag bit exists; PyMuPDF has no subscript bit, so a document whose only script text is subscript gives 0 and passes unconditionally | whether to detect subscript by baseline offset |
| `38_list_markers` | 3 | the marker must carry its trailing space inside one span, so a render that emits "1." and "First item" separately never counts; and two-digit markers never count on either side | how to detect a list marker across span boundaries |
| `34b_span_colour_match` | 3 | exact 24-bit int equality where the int encodes the colour space: CMYK black is 0x231f20, RGB black is 0x000000 | whether to compare perceptually |
| `54_image_dpi` | 10, unfixable | compares the original's dpi against Google's re-encode; every source above 160 dpi fails for ever | whether the check should exist |
| `56_rtl_runs` | 8, none the RTL doc | source reads 0 on 179 of 187, including the corpus's only Arabic document | whether direction is recoverable at all |
| `29/30` | unknown | a uniform 2.5 pt horizontal shift passes 18/19/20/21 but makes both fire, because the 24.79 pt lattice treats any offset above ~2.4 pt as every line vanishing | the lattice tolerance |
| `17_matched_runs` | unknown | `int(0.9*12)` is 10, so 12 runs with 10 matched passes against a stated 90% rule | the floor |
| `16_numeric_runs` | unknown | cannot fail a 3-span document: every digit lost still reads source 3, render 0, ok | the minimum sample |

### The one thing worth knowing above all of it

The seven shapes found in `53_embedded_faces` were all one of two mistakes:

    1. the number measured what the producer DECLARED, not what it DREW
    2. one side normalised and the other did not

Every defect in the table above is one of those two, in a check nobody had audited. When a class
looks impossible to move, the first question is not "what does the engine do wrong" but "is this
number a property of the document or a property of the tool that made it".

`47_margins` cost four attempts and a day. It was a space.

## Class `47_margins` - the three counts reconciled (13 Nov)

Three stores were being quoted for one class, and one of the three numbers was never this class's.
All of the figures below were measured on 13 Nov with the commands in EVIDENCE-style form:
`python3 -` over `BASELINE.md` and `RESULTS.jsonl`, counting documents whose `failed` column
contains `47_margins`.

| store | what it holds | documents | failing `47_margins` |
|---|---|---|---|
| `RESULTS.jsonl`, committed engine `2a68de6` only | 297 rows, 7 engine ids, one row per doc per engine | 208 | **203** |
| `RESULTS.jsonl`, last row per document, any engine | same file, dirty engines included | 211 | 204 |
| `BASELINE.md` | 211 rows, one per document, latest measurement | 211 | **205** |
| `DEFECT-CLASSES.md` | generated from `BASELINE.md` by `classify.py` | 211 | **205** |

**203 and 205 are both right and are not the same measurement.** The gap is three documents, and it
resolves exactly, document by document:

- `BASELINE.md` carries three documents that `RESULTS.jsonl` does not hold on engine `2a68de6`:
  `600_reviewed_invoice_with_annotations`, `601_fillable_admission_form`,
  `602_bookmarked_annual_report` - all three measured 13 Nov on the newer engine `eca9020`.
- Two of them (`600`, `601`) fail `47_margins`. The third (`602`) passes it.
- No document fails `47_margins` in `RESULTS.jsonl` and passes it in `BASELINE.md` - the difference
  is one-directional.

203 + 2 = 205. The 204 is not a count of anything: it is what you get by taking each document's
last row regardless of which attempt wrote it, which mixes four dirty (reverted) engine ids into a
count of what ships.

**Authoritative: `BASELINE.md`.** For three reasons, in order of weight:

1. It is the only store that is one row per document by construction - 211 rows, 211 distinct
   documents, 0 duplicates - so counting it needs no rule about which row wins. Counting
   `RESULTS.jsonl` needs an engine rule, and getting that rule wrong moves the answer (203 vs 204).
2. It is the store the verifier writes and the only one the classifier reads (`classify.py:118`,
   `read_baseline`), so every class number in `DEFECT-CLASSES.md` is derived from it. A count quoted
   from anywhere else will disagree with the file the fixer actually picks from.
3. `RESULTS.jsonl` is an append-only per-attempt log: four of its seven engine ids are `-d`/dirty
   builds from attempts that were reverted (`2a68de6-dc3d644`, `-dirty`, `-d80a524`, `-d5215cb`,
   `-df33807`). A row written by a reverted attempt describes an engine that does not ship.

**The caveat that matters more than the count.** 208 of the 211 `BASELINE.md` rows carry engine
`2a68de6` and only 3 carry `eca9020`; the 17 rows re-measured on 13 Nov under `2a68de6` still fail
`47_margins` 17 of 17. So **205 is the class size BEFORE the lone-space fix (`57f521d`) has been
measured on the corpus** - nothing in either store re-measures `47_margins` after it. Treat 205 as
the pre-fix size. It is not today's, and no run should quote it as if the space fix were in it.

**Two numbers that must stop being read as this class's size.**

- `182 of 187` (`REMAINING-DEFECTS.md:180` and `:189`) is a CAUSE share, not a class size: 182
  documents whose `47_margins` failure was the lone space at x=0, out of the 187 documents in the
  store when that was measured. Neither 187 nor 182 appears in any current store; both predate the
  corpus growing to 211.
- `203` is `20_within_10pt`'s size when `patches/README-2026-11-13.md` was written
  (the split-box heading in `patches/README-2026-11-13.md`), and `47_margins` was "never 203" as
  that heading says. It is 205 of
  211 now, and `20_within_10pt` is 190.

Reconciled figure for anything downstream: **`47_margins` = 205 of 211 documents, measured on
engine `2a68de6`, pre-`57f521d`** (`BASELINE.md`; `DEFECT-CLASSES.md:19`).

## The fourteen tail checks - what was measured, what was stale, what was retired (13 Nov)

Worked in order of the store's own document count. No corpus was available to this pass, so
every claim below is either a constructed pair through `compare()` (reproducible: the scripts
are `probe.py`/`probe2.py`/`probe3.py` in the session work dir, all built with PyMuPDF from
nothing), a line of code, or a query over `RESULTS.jsonl`.

**Two entries in the table at `:196-210` are STALE - the code already fixed them.** Do not
re-investigate:

- `34b_span_colour_match` (`:205`) - "exact 24-bit int equality where the int encodes the
  colour space". `colour_same()` is perceptual at HEAD (CIEDE2000 <= 6.0, plus the
  `CMYK_BLACK = 0x231f20` clause), landed in `995290a` 13:25. The 2 documents that fail 34b
  were measured BEFORE that (store snapshot `RATCHET-20261113-084751`, 08:47), so 414's 0 %
  is a pre-fix number. Same line in 13_text_colours was exact `Counter` equality; it uses
  `colour_same()` now.
- `38_list_markers` (`:204`) - "the marker must carry its trailing space inside one span ...
  two-digit markers never count". `NUM_MARK` handles both, `995290a` 13:25. Its 2 failures
  predate it.

**Three checks are RETIRED in this pass, each with a constructed proof that it cannot answer
its own question** - `11_bold_runs`, `16_numeric_runs`, `21_median_dx`. Reasons are in
`verify_google.py` beside where each one stood; the short form is that 11 reads the face NAME
where 34c reads the flag and is contradicted on 22 of its 26 documents, 16 counts runs
containing a digit (a changed digit reads 1 -> 1 and passes; three numeric runs may lose every
digit and pass), and 21's median is now a clause of 43.

**Two are REDEFINED**, so their old marks are not comparable and the body digest moves:
`42_alignment_mix` (shares, not counts - it failed by arithmetic whenever the render had fewer
than 70 % of the source's qualifying lines) and `13_text_colours` (a set compared with
`colour_same`, floor equality like 15/40, not a count).

**Kept, with the question stated, because the evidence does not condemn them:** `01_page_count`
(57 documents, nearly all src=1 render=2 - a real engine defect, the page budget, and the check
is a plain equality that no ruler change can improve), `27_text_off_page` (28 of 31 are exactly
ONE run past an edge - real, but the check reports no magnitude, so the tail cannot be
triaged), `28_clipped_at_edge` (4, real, already fixed once in `c4b379a`), `36_underline_rules`
(its 18 failures predate `_stroke_pictures`; a rule drawn as a raster band now reads 1 on both
sides - re-measure before touching it), `34a/34b/34c` (survivors; the 10_font_sizes duplicate
retirement is still OUTSTANDING - 10 is live at HEAD), `43_within_10pt_x` (the only per-span
horizontal check, now carrying 21's median clause).

**And one thing this pass could not do:** there is no measurement of these fourteen checks
anywhere in the repository that describes HEAD. `RESULTS.jsonl`'s 208 rows are engine
`2a68de6`, and every ruler fix of 13 Nov (10:08-15:34) landed after the last snapshot
(08:47). Every class number in `DEFECT-CLASSES.md` is therefore a pre-fix number, which that
file already says at `:163`.
