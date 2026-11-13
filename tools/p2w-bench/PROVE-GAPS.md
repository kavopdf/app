# PROVE-CHECKS: 30 checks whose firing is not demonstrated

`prove_checks.py` mutates a real corpus document in a way the check is supposed to catch, and
reports whether the check fired. Run on the 208-document corpus on 13 Nov:

    P2W_CORPUS=<208 pdfs> python3 tools/p2w-bench/prove_checks.py
    -> 28 proven, 30 unproven of 58      (was 26 and 32 before this commit)

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
| `41_block_spacing` | `mut_shift` | a uniform shift leaves every gap unchanged | change the gap between two blocks |
| `42_alignment_mix` | `mut_shift` (dx=10) | a uniform shift leaves the alignment counts identical | centre one line that was left-aligned |
| `44_header_footer` | `mut_header` | ran but did not fire; the band is 0.11/0.89 of page height | add a block inside the band |
| `48_image_area` | `mut_image_shrink` | ran but did not fire; the floor is 50 % of the source area | shrink below half |
| `53_embedded_faces` | `mut_font` | ADDS a face; the check counts families that were LOST | drop a drawn family |
| `54_image_dpi` | `mut_image_shrink` | resizing does not change pixels per inch | re-encode the image at a lower density |
| `56_rtl_runs` | `mut_shift` (dx=10) | a shift does not change text direction | draw text right-to-left |
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

## What this means for the corpus numbers

`BASELINE.md`, `DEFECT-CLASSES.md` and `RATCHET.json` are built from these 58 checks. For the 30 in
this table, the only evidence that they can fire is that they have fired on real documents - which
is weaker than a constructed proof, because a check that never fires and a check whose target never
occurs look identical from the outside. `47_margins` is the case in point: it fired on 205 of 211
documents, was treated as a real defect class through three fixer attempts, and nineteen separate
investigations then found it is measuring page-1 ink extents rather than margins.
