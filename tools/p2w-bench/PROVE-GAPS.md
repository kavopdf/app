# PROVE-CHECKS: 30 checks whose firing is not demonstrated

`prove_checks.py` mutates a real corpus document in a way the check is supposed to catch, and
reports whether the check fired. Run on the 208-document corpus on 13 Nov:

    P2W_CORPUS=<208 pdfs> python3 tools/p2w-bench/prove_checks.py
    -> 37 proven, 21 unproven of 58      (was 33 and 25 before the relative mutations)

**An unproven check is not a proven check.** It may work perfectly and simply lack a test; it may
also never fire at all, and the difference decides whether the corpus numbers mean anything. This
file records, for each of the 30, why the current mutation cannot prove it, so each can be fixed
one at a time rather than guessed at.

## The three shapes of the defect

**(a) The mutation is inside the check's own tolerance.** It cannot fire by construction.
Fixed in this commit: `43_within_10pt_x` and `47_margins` both shifted the page by 10 pt, and 43
passes while 90 % of pairs are within 10 pt, 47 while all four edges are within 12. Both now use
20 pt, and both fire.

**(b) The mutation does not change the quantity the check measures.** A uniform page shift moves
everything, so it cannot change a *relative* measure - spacing, alignment, direction, order. Seven
of the remaining checks are in this group.

**(c) The mutation changes the wrong object.** `mut_rule` draws a rule; it does not create an
underline, a subscript, a list marker or a border-over-text. `mut_rotate` rotates the PAGE, while
35_rotation reads the text matrix, so the check correctly sees nothing. `mut_image_shrink` shrinks
an image; it does not move one and does not necessarily change its dpi.

## The 30, with what each actually needs

| check | current mutation | why it cannot prove the check | what it needs |
|---|---|---|---|
| `28_clipped_at_edge` | `mut_clip` | ran but did not fire - the mutation's clip is on the wrong axis or inside the 2 pt allowance | clip by more than the allowance, on the axis the check reads |
| `30_ink_where_blank_was` | `mut_rule` | adds a rule; the check reads 24-cell occupancy, and one rule rarely occupies a cell | fill a whole cell, or move text into an empty cell |
| `32_stroke_lines` | `mut_rule` | adds ONE rule to a document with many, inside the 80 % floor | REMOVE most rules, or add many |
| `35_rotation` | `mut_rotate` | rotates the page; 35 reads `line.dir`, the text matrix, which a page rotation does not touch | draw the text with a rotated matrix |
| `36_underline_rules` | `mut_rule` | a rule is not an underline - it must sit within 2.5 pt of a span's bottom | draw a rule at a span's baseline |
| `37_super_subscript` | `mut_rule` | only the superscript flag exists; a rule sets no flag | raise a run and set the flag |
| `38_list_markers` | `mut_rule` | needs a leading "1. " or bullet INSIDE one span | retype a line's first span |
| `39_image_position` | `mut_image_shrink` | shrinks; the check compares position | move the image without resizing |
| `41_block_spacing` | **PROVEN** - `mut_block_gap` moves one block | a uniform shift left every gap unchanged | done: see "The four relative measures" below |
| `42_alignment_mix` | **PROVEN** - `mut_alignment` centres every multi-line block | a uniform shift left the alignment counts identical | done: see below |
| `44_header_footer` | `mut_header` | ran but did not fire; the band is 0.11/0.89 of page height | add a block inside the band |
| `48_image_area` | `mut_image_shrink` | ran but did not fire; the floor is 50 % of the source area | shrink below half |
| `53_embedded_faces` | `mut_font` | ADDS a face; the check counts families that were LOST | drop a drawn family |
| `54_image_dpi` | `mut_image_shrink` | resizing does not change pixels per inch | re-encode the image at a lower density |
| `56_rtl_runs` | **PROVEN** - `mut_rtl` draws a reversed run on the source side | a shift does not change text direction | done: see below |
| `59_shape_anchor` | none written | no case exists | move a run out of its enclosing shape |
| `46_text_crossing_rule` | `mut_rule` | same as 33 - a duplicate of it | see 33 |
| `33_border_over_text` | `mut_rule` | ran but did not fire; needs a THIN stroke crossing a span | see `_strokes`: a filled band, not a stroked line |
| `50/51/52` | source-side drops | unproven on this corpus - it has no annotations, widgets or outline to drop | a document that has them |
| `40_link_targets` | `mut_wrong_link` | unproven - the corpus document has no external URI | a document with one |
| `45_char_accuracy` | - | proven by the same mutation as 03/04, not independently | reorder without losing a character |
| `49_page_size` | `mut_pagesize` | proven | - |
| `29_blank_where_ink_was` | `mut_blank` | proven | - |

## A second weakness, separate from the count

Every mutation reports "(N other checks moved too)". `mut_shift` moves the whole page, so it fires
18/19/20/21/23/41/43/47 at once. That proves each of them *can* fire, but not that any of them is
specific - a check that fires on everything is as useless as one that never fires. A mutation that
isolates its target would prove both.

## The four relative measures (proven 13 Nov)

`41_block_spacing`, `42_alignment_mix`, `56_rtl_runs` and `23_line_pitch` all measure a
RELATIVE quantity, and `mut_shift` - a uniform page translation - is invariant on every one of
them. All four now have a mutation that changes the measured quantity itself, and all four fire.
`23_line_pitch` had no row in this table before, although the harness reported it unproven - and
it was not alone: fourteen of the 30 unproven checks had no row here at all, including
`05_words_extra`, `24_page_breaks`, `26_text_overlap`, `27_text_off_page` and `28_clipped_at_edge`.
The table was never a complete account of the 30 it claims to account for.

| check | mutation | measured | fires |
|---|---|---|---|
| `41_block_spacing` | `mut_block_gap` - one block moved, everything else left in place | median gap 24.4 -> 86.1 pt | yes |
| `42_alignment_mix` | `mut_alignment` - every multi-line block re-laid centred | 42 matching lines -> 6 | yes |
| `56_rtl_runs` | `mut_rtl` - a reversed run added to the SOURCE side | source 1, render 0 | yes |
| `23_line_pitch` | `mut_line_pitch` - one block respaced about its own first baseline | median pitch 12.4 -> 24.8 pt | yes |

Three things were measured rather than assumed, and each one changed the design:

1. **A median can be pinned.** On the invoice (BASE) five block gaps are exactly 17.0 pt around
the median, and all 168 candidates (28 block tops x the 6 distances the mutator tries) leave the
median at 17.0 - simulated, not assumed. `mut_block_gap` therefore searches for the block and the
distance instead of assuming any move works, and the case runs on `34_monospace_document.pdf`
where one moved block takes the median from 24.4 to 86.1. On BASE the same mutator leaves the
median at 17.0 and the check does not fire - correctly.
2. **One centred line is not enough for a 70 % floor.** The check passes while 70 % of the
source's classified lines still match, so on a 42-line page thirteen must move. Measured: one
centred line leaves 42 of 42 matching, and the check does not fire.
3. **Redaction plus reinsertion must be per span.** Reinserting a whole line as one string loses
the gaps between spans (the invoice's `1 Hex` returned as `1Hex`) and a base-14 font drops the
glyphs it has no character for (the em dash and the bullet disappeared). `_reflow` therefore
redraws span by span at each span's own x, with DejaVu when the font file is present.

What `56_rtl_runs` actually counts: `dir[0] < 0` is any line whose x axis points left, which
includes text rotated 180 degrees. Ten of the 208 corpus documents have such lines and none of
them is right-to-left script - `04_stamp_180deg_upside_down.pdf` counts 2, from a `CANCELLED`
stamp. So the check is not RTL-specific; it is direction-reversal-specific, and its name says
otherwise. Its mutation proves the failure path, not that a real RTL document is measured well:
the corpus contains no RTL document to check that with.

## What this means for the corpus numbers

`BASELINE.md`, `DEFECT-CLASSES.md` and `RATCHET.json` are built from these 58 checks. For the 30 in
this table, the only evidence that they can fire is that they have fired on real documents - which
is weaker than a constructed proof, because a check that never fires and a check whose target never
occurs look identical from the outside. `47_margins` is the case in point: it fired on 205 of 211
documents, was treated as a real defect class through three fixer attempts, and nineteen separate
investigations then found it is measuring page-1 ink extents rather than margins.

## CORRECTION, 13 Nov - this table was stale when it was written

Three of the rows below are wrong, and one check no longer exists:

- **50_annotations, 51_form_fields, 52_outline and 40_link_targets were never unproven.** The
  harness does not need a corpus document that HAS the feature, because it does not drop the feature
  from the render - it ADDS it to the source (`prove_checks.py:318-320` marks them `("source", ...)`
  and then passes the mutated document as the source). They have been proven all along, and the 30
  actually unproven are: 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 23, 24, 26, 27, 28, 30, 32, 35,
  36, 37, 38, 39, 41, 42, 44, 48, 53, 54, 56, 59. (32/35/36/37/38 were fixed later in this same
  day's work and now fire; 28 became 33 proven.)
- **02_text_run_count has no row to be unproven on** - the check was dropped from the verifier on
  13 Nov and `--list-checks` no longer emits it. Its entry at `prove_checks.py:268` can never fire.
- **The 40 row's reason is wrong.** It says the corpus document has no external URI; it has five
  (`44_coloured_underlined_hyperlinks.pdf`, all `LINK_URI`).

## AND THE BIGGER FINDING: fan-out. 52 of 58 cases mutate ONE document.

Measured over all 58 cases, each against a 58/58 control:

    fan-out 0 : 24_page_breaks, 27_text_off_page, 39_image_position, 48_image_area,
                51_form_fields, 52_outline, 54_image_dpi
    fan-out 1 : 08_image_count, 15_links, 33_border_over_text, 40_link_targets,
                44_header_footer, 46_text_crossing_rule, 50_annotations
    fan-out 24: 03_word_count, 04_words_missing, 16_numeric_runs, 17_matched_runs,
                22_reading_order, 29_blank_where_ink_was, 31_pages_lost_their_text

**One mutation, `mut_blank`, is the sole evidence for SEVEN checks and moves 24 of them.** A blank
page is not a targeted probe; it is the whole suite reacting to one page disappearing. The tool
warns only above fan-out 8 (`prove_checks.py:426`), so seven proven checks with fan-out 5-8 print as
if they were isolated.

**`59_shape_anchor` has no case written and is collateral in 31 of the 58 mutations** - it pollutes
every fan-out measurement until it is characterised, and it is the single biggest unknown in the
table above.

Targeted replacements were built and measured, cutting the three worst from 24/17/12 to 3/1/1:
`mut_blank` becomes three mutations (redact one span; exchange two spans' text IN PLACE so order
changes without geometry moving; blank the LAST page of a 7-page document), `mut_landscape` becomes
a flip of a page that carries no text, and `mut_restyle` becomes one attribute at a time. All eight
verified firing with the lower fan-out.

**And a duplicate pair worth recording:** `33_border_over_text` and `46_text_crossing_rule` co-fire
in 16 of 58 cases. They are not two checks; they are one question asked twice.
