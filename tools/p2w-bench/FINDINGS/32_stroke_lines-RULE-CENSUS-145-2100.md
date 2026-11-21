# Rule census — how many horizontal rules each `32_stroke_lines` document draws

**Corpus:** the p2w corpus, fetched whole (`tools/p2w-bench/corpus-fetch.sh` → 213/213 PDFs, 0 missing
against `benchmarks/RANKING.csv`). **Scores:** the committed Google store, `benchmarks/gverify/*.json`
— 213 files, 192 scored (`status: ok`), 6 clean, **145 of the 192 fail `32_stroke_lines`**.
Nothing was converted, nothing was pushed to Google, and the 42-check scorer was not run.

Repo facts I had to establish first, because they gate the reading of every number below:

* Engine stamps in the store are exactly as stated: `462353f` 60 docs, `7112d76` 60 docs, absent/null 93
  (of which 72 are scored, 21 are `page_count_refused` or similar).
* `tools/p2w-bench/patches/rule-carrier-per-rule-2008.patch` **does not exist in the clone** — the only
  carrier in the tree is `rule-carrier-tblppr-2008.patch`. So this census prices the patch as it stands,
  one carrier per rule shape, and I could not read a per-rule (row-carrying) version.

---

## 1. The predicate

I did not invent a geometry test. The primary predicate is **the instrument's own rule definition**, the
one `32_stroke_lines` itself scores against, imported rather than re-implemented from
`tools/p2w-bench/verify_google.py`:

```python
import verify_google as vg            # the module the 42 checks use
rules = vg._rules(page, isolated=True)   # 32_stroke_lines' own rule set
```

which is, verbatim from the source, a straight **axis-aligned** segment on the page where

1. **thin face ≤ `RULE_THIN` = 4.0 pt.** Either a filled band (`re`/closed `l`/`qu` with a fill and no
   stroke) whose short side is ≤ 4.0 pt, or a stroked segment whose stroke width is ≤ 4.0 pt. A
   stroked line is recognised when it is horizontal within 0.8 pt (`|dy| ≤ 0.8`) or vertical within
   0.8 pt — so a zero-height hairline counts, and its thickness is the stroke width, not the bbox
   height (which is 0.00 for every stroked rule in this corpus);
2. **long face ≥ `RULE_LONG` = 10.0 pt**;
3. **isolated** — it does not cross, meet or abut another segment within `RULE_GAP` = 3.0 pt, in either
   axis. This is what keeps table grid lines, boxed frames and legend keys that touch their frame out
   of the count;
4. **it paints** — the colour (fill or stroke) is not white and its opacity is not ~0.

Counted over **all pages** of the source PDF; the document's rule count is the sum. I also kept a
per-page vector, because a carrier that is per-page cares about the busiest page, not the total.

**Why not the naive predicate in the brief.** The brief's sketch — "filled rects / lines whose height is
under ~2 pt and width over 20 pt" — is wrong on this corpus in two measured ways:

* **Every rule in the two calibration documents is stroked, not filled.** `73_marksheet` draws its two
  rules as single stroked paths with bbox height **0.00 pt**; a `0.5 pt`-tall-filled-rect test finds
  nothing at all. Thickness has to come from the stroke width, which is what the instrument does and
  what the engine does (`PdfToWord.emitStroke` turns a stroke into a filled band as thick as the
  stroke).
* **With no isolation test the count explodes into page furniture.** Run that way (no isolation,
  thickness < 2 pt, length > 20 pt) the corpus yields **6,314** "rules" and `394_map_with_legend`
  yields **26** — the four page-frame edges, the four borders of each of the five small boxes, the
  legend box's four edges, the two legend swatches and the scale bar. A count that includes the page
  frame cannot answer a question about rules.

So the primary predicate is the check's, and I report a second, wider one for the ambiguity section:

* **P1 (primary, reported everywhere unless stated):** `vg._rules(page, isolated=True)` as above.
* **P2 (the engine's own trigger, `DocxWriter.isRuleShape`, applied to PDF geometry):** thin side ≤ 4.0 pt,
  long side > 2.0 pt, and long ≥ 4 × thin, filled **or** stroked, **no isolation test**. This is the
  predicate that actually decides how many carriers get emitted, so it is the blast radius; it is not a
  good definition of "a rule", which is why it is not the primary.

---

## 2. Cross-check on the two known documents

| document | required | P1 | P2 | verdict |
|:--|--:|--:|--:|:--|
| `73_marksheet_subject_marks_grade` | 2 | **2** | **2** | ✅ pass |
| `394_map_with_legend` | 1 | **3** | **30** | ❌ **fail — the expected value is wrong, not the predicate** |

`73_marksheet` comes out 2 on every predicate I tried, and the two rules are exactly the two the
document is built from: a 483.3 × 0.90 pt navy rule at y = 84.0 and a 483.3 × 0.50 pt grey rule at
y = 793.9, both from x = 56.0 to x = 539.3. That is the document the stack was measured on, and 2 is
right.

`394_map_with_legend` does **not** come out 1, and I could not make it come out 1 without tuning a
threshold to the answer. It draws three isolated hairlines on its single page:

| # | page | y (pt) | x from → to | length | thickness | what it is |
|--:|--:|--:|:--|--:|--:|:--|
| 1 | 0 | 461.89 | 60.0 → 400.0 | 340.0 pt | 0.80 pt | the horizontal State-highway line in the map drawing (brown) |
| 2 | 0 | 691.89 | 395.28 → 415.28 | 20.0 pt | 1.60 pt | the "State highway" legend key |
| 3 | 0 | 707.89 | 395.28 → 415.28 | 20.0 pt | 3.00 pt | the "River" legend key |

A fourth candidate, the 2 km scale bar (100 pt at y = 761.89, with end ticks), is correctly excluded by
the isolation test because the vertical ticks at its two ends (x = 40 and x = 140, y 757.9–765.9) meet
it within 3 pt. The 340 pt highway line survives isolation because the only axis-aligned segments that
could touch it are the page-frame verticals at x = 20 and x = 575.3, and both lie outside its x-extent
(60 → 400); the diagonal highways are not axis-aligned within 0.8 pt, so `_rule_segments` never sees them
at all — which is also why the map's polygon edges do not appear in any count here. Dropping the
isolation test makes it worse (26–30), not better.

**The repo's own record says 3, and says it reached 42/42 with all three carried.** The javadoc of
`RULE_MAX_PT` in `rule-carrier-tblppr-2008.patch` reads:

> "measured on 394_map_with_legend, whose **third rule is a 20 x 3.0 pt legend swatch**. With 2.5 the
> document scored 41/42 in Google with exactly that one rule lost; the carrier is only worth what it
> covers, so it covers the instrument's own definition."

So `394_map_with_legend` is not a one-rule document: it has three rules, the carrier emitted three
floating tables, they stacked, and the document still scored 42/42 (it is 41/42 in the committed store,
failing `32` alone, and the 42/42 is the patch's own Google measurement). **That is a counter-example to
the premise "documents that could flip to clean are those with exactly one rule"** — and it is load-
bearing for the headline below, so I am flagging it rather than papering over it: the single-rule gate is
sufficient but not necessary, and the census cannot tell a rule the check scores from a rule it does not.

Independent validation of the pipeline: P1 reproduces the prior in-repo census
(`FINDINGS/32_stroke_lines-ONE-RULE-PER-PAGE-IS-ONE-DOCUMENT-2115-relay.md`) exactly — **1,170 rules**
across the corpus, **53** documents with no rule, **160** with at least one, **146** whose busiest page
holds two or more. Two independent implementations of the same definition agreeing to the unit is the
strongest check available here.

---

## 3. The census — the 145 documents that fail `32_stroke_lines`

Bucket totals over the 145 (P1, whole document):

| rules in the document | documents |
|:--|--:|
| 0 | 0 |
| 1 | 11 |
| 2 | 56 |
| 3 or more | 78 |
| **total** | **145** |

Under P2 (the engine's trigger, no isolation) the same 145 split as 0: 0, 1: 2, 2: 25, 3+: 118 — which is
the ambiguity section in one line.

### 3a. The eleven documents with exactly one rule (P1)

| document | engine stamp | rules (P1) | hairlines (P2) | failing checks |
|:--|:--|--:|--:|:--|
| `311_fir_police_form` | `462353f` | 1 | 104 | 04_chars_missing, 18_displacement, 32_stroke_lines, 45_char_accuracy, 60_text_column_right_edge |
| `325_demat_holdings_statement` | `462353f` | 1 | 109 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines |
| `334_patent_document` | `462353f` | 1 | 15 | 05_chars_extra, 32_stroke_lines |
| `33_sans_nondefault_body` | `462353f` | 1 | 12 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor |
| `365_recipe_card` | `7112d76` | 1 | 1 | 18_displacement, 32_stroke_lines, 47_margins, 60_text_column_right_edge |
| `371_experience_certificate` | `7112d76` | 1 | 1 | 04_chars_missing, 13_text_colours, 17_matched_runs, 32_stroke_lines, 45_char_accuracy, 59_shape_anchor, 60_text_column_right_edge |
| `40_devanagari_shaping_font` | `7112d76` | 1 | 12 | 05_chars_extra, 18_displacement, 32_stroke_lines, 34a_span_size_match, 38_list_markers, 47_margins |
| `52_one_cm_margin_wide_body` | null | 1 | 12 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor |
| `academic-paper-ieee-2col-abstract` | null | 1 | 14 | 04_chars_missing, 05_chars_extra, 17_matched_runs, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 47_margins, 60_text_column_right_edge |
| `admission-form-labels-left-boxes-right` | null | 1 | 97 | 05_chars_extra, 25_invisible_text, 32_stroke_lines |
| `electricity-bill` | null | 1 | 49 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines |

### 3b. Full table — all 145 documents

Sorted by rule count then name. "hairlines (P2)" is the engine's own trigger count, included because it
is the number of carriers the patch would actually emit.

| document | engine stamp | rules (P1) | hairlines (P2) | pages | failing checks |
|:--|:--|--:|--:|--:|:--|
| `311_fir_police_form` | `462353f` | 1 | 104 | 1 | 04_chars_missing, 18_displacement, 32_stroke_lines, 45_char_accuracy, 60_text_column_right_edge |
| `325_demat_holdings_statement` | `462353f` | 1 | 109 | 1 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines |
| `334_patent_document` | `462353f` | 1 | 15 | 1 | 05_chars_extra, 32_stroke_lines |
| `33_sans_nondefault_body` | `462353f` | 1 | 12 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor |
| `365_recipe_card` | `7112d76` | 1 | 1 | 1 | 18_displacement, 32_stroke_lines, 47_margins, 60_text_column_right_edge |
| `371_experience_certificate` | `7112d76` | 1 | 1 | 1 | 04_chars_missing, 13_text_colours, 17_matched_runs, 32_stroke_lines, 45_char_accuracy, 59_shape_anchor, 60_text_column_right_edge |
| `40_devanagari_shaping_font` | `7112d76` | 1 | 12 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 34a_span_size_match, 38_list_markers, 47_margins |
| `52_one_cm_margin_wide_body` | null | 1 | 12 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor |
| `academic-paper-ieee-2col-abstract` | null | 1 | 14 | 2 | 04_chars_missing, 05_chars_extra, 17_matched_runs, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 47_margins, 60_text_column_right_edge |
| `admission-form-labels-left-boxes-right` | null | 1 | 97 | 1 | 05_chars_extra, 25_invisible_text, 32_stroke_lines |
| `electricity-bill` | null | 1 | 49 | 1 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines |
| `03_stamp_vertical_90deg` | `462353f` | 2 | 31 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 32_stroke_lines, 35_rotation, 59_shape_anchor, 62_table_columns, 63_table_rows |
| `06_rect_paid_stamp_red_transparent` | `462353f` | 2 | 19 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 32_stroke_lines, 35_rotation, 59_shape_anchor |
| `11_stamp_with_signature_image` | `462353f` | 2 | 2 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 17_matched_runs, 32_stroke_lines, 35_rotation, 45_char_accuracy |
| `13_stamp_non_english` | `462353f` | 2 | 13 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 17_matched_runs, 18_displacement, 32_stroke_lines, 35_rotation, 45_char_accuracy, 59_shape_anchor |
| `17_three_column_widths_txtpos` | `462353f` | 2 | 2 | 1 | 05_chars_extra, 32_stroke_lines |
| `18_centred_heading_left_body_txtpos` | `462353f` | 2 | 2 | 1 | 05_chars_extra, 32_stroke_lines |
| `19_hanging_indent_txtpos` | `462353f` | 2 | 2 | 1 | 05_chars_extra, 32_stroke_lines |
| `23_timetable_grid_txtpos` | `462353f` | 2 | 21 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor |
| `24_address_block_indents_txtpos` | `462353f` | 2 | 2 | 1 | 05_chars_extra, 32_stroke_lines |
| `25_signature_block_underscores_txtpos` | `462353f` | 2 | 2 | 1 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 45_char_accuracy, 60_text_column_right_edge |
| `28_value_overflows_cell_txtpos` | `462353f` | 2 | 13 | 1 | 04_chars_missing, 05_chars_extra, 32_stroke_lines, 43_within_10pt_x, 45_char_accuracy, 47_margins, 59_shape_anchor, 60_text_column_right_edge |
| `300_prescription_rx` | `462353f` | 2 | 70 | 1 | 18_displacement, 25_invisible_text, 32_stroke_lines, 59_shape_anchor |
| `302_radiology_report` | `462353f` | 2 | 2 | 1 | 18_displacement, 32_stroke_lines, 60_text_column_right_edge |
| `31_times_body_arial_headings` | `462353f` | 2 | 2 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `32_serif_nondefault_body` | `462353f` | 2 | 2 | 1 | 05_chars_extra, 32_stroke_lines |
| `34_monospace_document` | `462353f` | 2 | 2 | 1 | 05_chars_extra, 32_stroke_lines |
| `35_four_typefaces_one_page` | `7112d76` | 2 | 14 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor |
| `36_embedded_subset_font` | `7112d76` | 2 | 14 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor |
| `37_font_not_embedded_substitution` | `7112d76` | 2 | 2 | 1 | 05_chars_extra, 32_stroke_lines |
| `38_faux_bold_italic_synthesised` | `7112d76` | 2 | 12 | 1 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 60_text_column_right_edge |
| `39_small_caps_letter_spacing` | `7112d76` | 2 | 2 | 1 | 05_chars_extra, 25_invisible_text, 26_text_overlap, 32_stroke_lines, 43_within_10pt_x, 47_margins |
| `41_coloured_headings_white_bg` | `7112d76` | 2 | 2 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `42_table_coloured_header_alternating_rows` | null | 2 | 15 | 1 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines, 59_shape_anchor |
| `43_red_stamp_over_black_text` | `7112d76` | 2 | 2 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 17_matched_runs, 32_stroke_lines, 35_rotation |
| `45_coloured_callout_box` | `7112d76` | 2 | 6 | 1 | 05_chars_extra, 32_stroke_lines |
| `46_chart_coloured_labels_body_text` | null | 2 | 12 | 1 | 04_chars_missing, 05_chars_extra, 32_stroke_lines, 44_header_footer, 45_char_accuracy |
| `47_grey_body_black_headings` | `7112d76` | 2 | 2 | 1 | 05_chars_extra, 32_stroke_lines |
| `50_invoice_coloured_total_row` | null | 2 | 14 | 1 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines, 59_shape_anchor |
| `53_single_space_body_15_headings` | `7112d76` | 2 | 2 | 1 | 05_chars_extra, 32_stroke_lines |
| `54_two_column_body_full_width_header_footer` | `7112d76` | 2 | 2 | 1 | 04_chars_missing, 13_text_colours, 25_invisible_text, 32_stroke_lines, 44_header_footer, 45_char_accuracy |
| `55_sidebar_box_beside_body` | null | 2 | 6 | 1 | 04_chars_missing, 05_chars_extra, 32_stroke_lines, 44_header_footer, 45_char_accuracy |
| `56_table_indented_from_margin` | null | 2 | 16 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 60_text_column_right_edge |
| `601_fillable_admission_form` | `7112d76` | 2 | 46 | 1 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 51_field_values, 53_embedded_faces, 59_shape_anchor |
| `62_two_col_newsletter_pull_quote` | null | 2 | 7 | 1 | 04_chars_missing, 05_chars_extra, 25_invisible_text, 32_stroke_lines, 44_header_footer, 45_char_accuracy |
| `67_two_col_with_sidebar` | null | 2 | 6 | 1 | 04_chars_missing, 32_stroke_lines, 44_header_footer, 45_char_accuracy |
| `70_magazine_drop_cap_photo_caption` | null | 2 | 6 | 1 | 04_chars_missing, 18_displacement, 32_stroke_lines, 44_header_footer |
| `71_invoice_space_aligned_no_rules` | `7112d76` | 2 | 2 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `72_bank_statement_no_rules_right_amounts` | null | 2 | 2 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `73_marksheet_subject_marks_grade` | `7112d76` | 2 | 2 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `74_balance_sheet_indented_subitems` | `7112d76` | 2 | 2 | 1 | 05_chars_extra, 32_stroke_lines |
| `75_merged_header_cell_three_columns` | null | 2 | 28 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 43_within_10pt_x, 47_margins, 59_shape_anchor, 64_table_span_across, 65_table_span_down |
| `79_inr_indian_digit_grouping_table` | null | 2 | 12 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 60_text_column_right_edge |
| `80_gstin_pan_cin_ifsc_table` | null | 2 | 22 | 1 | 04_chars_missing, 17_matched_runs, 18_displacement, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 59_shape_anchor |
| `annual-review-2col-uneven-columns` | null | 2 | 2 | 1 | 05_chars_extra, 25_invisible_text, 32_stroke_lines |
| `eway-bill` | null | 2 | 47 | 1 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines |
| `journal-2col-with-footnotes` | null | 2 | 2 | 1 | 05_chars_extra, 26_text_overlap, 32_stroke_lines, 37_super_subscript |
| `mobile-bill` | null | 2 | 48 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `policy-2col-spanning-section-heading` | null | 2 | 2 | 1 | 04_chars_missing, 05_chars_extra, 10_font_sizes, 13_text_colours, 17_matched_runs, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 59_shape_anchor, 60_text_column_right_edge |
| `report-2col-table-spanning-both-columns` | null | 2 | 19 | 1 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 44_header_footer |
| `table-inside-two-column-page` | null | 2 | 15 | 1 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 44_header_footer |
| `table-of-contents-dot-leaders` | `7112d76` | 2 | 2 | 1 | 04_chars_missing, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 47_margins |
| `table-with-merged-cells` | null | 2 | 24 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 60_text_column_right_edge |
| `table-with-no-header-row` | null | 2 | 38 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `table-with-rotated-header` | null | 2 | 29 | 1 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 45_char_accuracy, 47_margins, 59_shape_anchor |
| `text-held-twice-shadow-text` | `7112d76` | 2 | 16 | 1 | 05_chars_extra, 13_text_colours, 18_displacement, 25_invisible_text, 32_stroke_lines, 60_text_column_right_edge |
| `two-tables-stacked-with-no-gap` | null | 2 | 31 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `01_stamp_rotated_15deg_upright` | `462353f` | 3 | 26 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 25_invisible_text, 32_stroke_lines, 35_rotation, 59_shape_anchor |
| `04_stamp_180deg_upside_down` | `462353f` | 3 | 27 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 25_invisible_text, 32_stroke_lines, 35_rotation, 59_shape_anchor |
| `07_stamp_over_table` | `462353f` | 3 | 17 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 25_invisible_text, 26_text_overlap, 32_stroke_lines, 35_rotation, 43_within_10pt_x, 47_margins, 59_shape_anchor |
| `08_two_overlapping_stamps` | `462353f` | 3 | 13 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 17_matched_runs, 18_displacement, 25_invisible_text, 32_stroke_lines, 35_rotation, 45_char_accuracy, 59_shape_anchor |
| `09_stamp_font_not_embedded` | `462353f` | 3 | 3 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 32_stroke_lines, 35_rotation, 59_shape_anchor |
| `10_stamp_as_image` | `462353f` | 3 | 15 | 1 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines, 59_shape_anchor |
| `14_stamp_chars_positioned_td` | `462353f` | 3 | 15 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 25_invisible_text, 32_stroke_lines, 45_char_accuracy, 59_shape_anchor, 60_text_column_right_edge |
| `26_footnote_marker_bottom_note_txtpos` | `462353f` | 3 | 3 | 1 | 05_chars_extra, 32_stroke_lines |
| `27_two_column_left_short_txtpos` | `462353f` | 3 | 3 | 1 | 04_chars_missing, 32_stroke_lines, 44_header_footer |
| `29_dot_leaders_txtpos` | `462353f` | 3 | 3 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `30_mixed_font_sizes_one_baseline_txtpos` | `462353f` | 3 | 14 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor |
| `330_cad_drawing_sheet` | `462353f` | 3 | 87 | 1 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 45_char_accuracy, 47_margins |
| `391_survey_questionnaire_grid` | `7112d76` | 3 | 116 | 1 | 05_chars_extra, 17_matched_runs, 32_stroke_lines |
| `394_map_with_legend` | `7112d76` | 3 | 30 | 1 | 32_stroke_lines |
| `49_coloured_background_block_paragraph` | `7112d76` | 3 | 3 | 1 | 05_chars_extra, 32_stroke_lines |
| `57_centred_title_page_left_body_pages` | `7112d76` | 3 | 3 | 2 | 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer |
| `600_reviewed_invoice_with_annotations` | null | 3 | 31 | 1 | 05_chars_extra, 18_displacement, 28_clipped_at_edge, 32_stroke_lines, 45_char_accuracy, 47_margins, 62_table_columns |
| `61_two_col_abstract_spanning` | null | 3 | 3 | 1 | 04_chars_missing, 32_stroke_lines, 44_header_footer |
| `69_two_col_legal_numbered_clauses` | null | 3 | 3 | 1 | 04_chars_missing, 05_chars_extra, 10_font_sizes, 13_text_colours, 17_matched_runs, 32_stroke_lines, 38_list_markers, 44_header_footer, 45_char_accuracy |
| `boq-tender-bill-of-quantities` | null | 3 | 38 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 60_text_column_right_edge |
| `gst-invoice-with-qr-code` | null | 3 | 35 | 1 | 05_chars_extra, 18_displacement, 25_invisible_text, 26_text_overlap, 32_stroke_lines, 66_table_cell_width |
| `insurance-policy-schedule` | null | 3 | 46 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `itr-computation-with-slab-table` | null | 3 | 61 | 1 | 05_chars_extra, 18_displacement, 26_text_overlap, 32_stroke_lines, 63_table_rows |
| `marksheet-university-consolidated` | null | 3 | 52 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 60_text_column_right_edge |
| `newsletter-3col-header-footer` | null | 3 | 3 | 1 | 04_chars_missing, 05_chars_extra, 25_invisible_text, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 59_shape_anchor |
| `property-tax-receipt` | null | 3 | 39 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 32_stroke_lines |
| `salary-slip-factory-wages` | null | 3 | 47 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 60_text_column_right_edge |
| `02_stamp_rotated_15deg_upleft` | `462353f` | 4 | 28 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 25_invisible_text, 32_stroke_lines, 35_rotation, 59_shape_anchor |
| `20_numbered_list_separate_column_txtpos` | `462353f` | 4 | 4 | 1 | 04_chars_missing, 17_matched_runs, 32_stroke_lines, 44_header_footer, 45_char_accuracy |
| `22_invoice_four_columns_txtpos` | `462353f` | 4 | 4 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `352_certificate_ornate_border` | `7112d76` | 4 | 12 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 17_matched_runs, 32_stroke_lines, 45_char_accuracy, 60_text_column_right_edge |
| `59_landscape_mixed_portrait` | null | 4 | 15 | 2 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor |
| `65_two_col_full_width_figure_caption` | null | 4 | 16 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 17_matched_runs, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 59_shape_anchor, 60_text_column_right_edge |
| `66_two_col_footnotes_bottom` | null | 4 | 4 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 17_matched_runs, 32_stroke_lines, 44_header_footer, 45_char_accuracy |
| `68_journal_wide_table_spanning` | null | 4 | 16 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `admit-card` | null | 4 | 35 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 32_stroke_lines, 45_char_accuracy, 59_shape_anchor |
| `balance-sheet-and-profit-loss` | null | 4 | 65 | 2 | 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 60_text_column_right_edge |
| `gst-invoice-3line-items` | null | 4 | 40 | 1 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines, 60_text_column_right_edge |
| `invoice-line-items-qty-rate-amount` | null | 4 | 25 | 1 | 05_chars_extra, 18_displacement, 25_invisible_text, 26_text_overlap, 32_stroke_lines |
| `magazine-2col-pullquote-spanning` | null | 4 | 4 | 1 | 04_chars_missing, 10_font_sizes, 13_text_colours, 17_matched_runs, 32_stroke_lines, 43_within_10pt_x, 44_header_footer, 45_char_accuracy, 47_margins, 60_text_column_right_edge |
| `marksheet-subject-left-marks-right` | null | 4 | 23 | 1 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines |
| `mutual-fund-statement` | null | 4 | 86 | 2 | 05_chars_extra, 18_displacement, 25_invisible_text, 27_text_off_page, 32_stroke_lines, 60_text_column_right_edge, 66_table_cell_width |
| `newspaper-2col-fullwidth-headline` | null | 4 | 4 | 1 | 04_chars_missing, 05_chars_extra, 18_displacement, 26_text_overlap, 32_stroke_lines, 45_char_accuracy |
| `one-page-rotated-180-degrees` | null | 4 | 42 | 2 | 04_chars_missing, 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 43_within_10pt_x, 44_header_footer, 60_text_column_right_edge, 62_table_columns, 63_table_rows |
| `purchase-order` | null | 4 | 28 | 1 | 05_chars_extra, 18_displacement, 25_invisible_text, 26_text_overlap, 32_stroke_lines, 60_text_column_right_edge |
| `question-paper-marks-right-margin` | null | 4 | 4 | 1 | 05_chars_extra, 32_stroke_lines, 60_text_column_right_edge |
| `315_gazette_notification` | `462353f` | 5 | 5 | 1 | 05_chars_extra, 32_stroke_lines |
| `360_restaurant_menu` | `7112d76` | 5 | 85 | 1 | 18_displacement, 32_stroke_lines, 43_within_10pt_x, 47_margins, 60_text_column_right_edge |
| `balance-sheet-two-columns-of-figures` | null | 5 | 5 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `delivery-challan` | null | 5 | 23 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 25_invisible_text, 26_text_overlap, 32_stroke_lines, 60_text_column_right_edge |
| `12_stamp_across_page_break` | `462353f` | 6 | 22 | 2 | 05_chars_extra, 27_text_off_page, 32_stroke_lines |
| `58_header_rule_footer_rule` | `7112d76` | 6 | 6 | 2 | 04_chars_missing, 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer |
| `63_three_column_brochure` | null | 6 | 6 | 1 | 05_chars_extra, 25_invisible_text, 32_stroke_lines |
| `form16-part-b` | null | 6 | 51 | 2 | 04_chars_missing, 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 60_text_column_right_edge |
| `landscape-page-inside-portrait-document` | null | 6 | 28 | 3 | 05_chars_extra, 18_displacement, 32_stroke_lines, 60_text_column_right_edge |
| `salary-slip-corporate` | null | 6 | 38 | 1 | 05_chars_extra, 17_matched_runs, 18_displacement, 25_invisible_text, 32_stroke_lines, 53_embedded_faces |
| `table-across-page-break-repeated-header` | null | 6 | 90 | 3 | 04_chars_missing, 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer, 60_text_column_right_edge |
| `very-long-single-column-table` | null | 6 | 129 | 3 | 04_chars_missing, 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer, 60_text_column_right_edge |
| `44_coloured_underlined_hyperlinks` | `7112d76` | 7 | 7 | 1 | 05_chars_extra, 32_stroke_lines, 40_link_targets, 46_text_crossing_rule |
| `payslip-label-left-amount-right` | null | 8 | 8 | 1 | 05_chars_extra, 17_matched_runs, 18_displacement, 25_invisible_text, 32_stroke_lines, 53_embedded_faces |
| `bank-statement-5-pages` | null | 10 | 175 | 5 | 05_chars_extra, 18_displacement, 25_invisible_text, 27_text_off_page, 32_stroke_lines, 44_header_footer, 59_shape_anchor |
| `brochure-3col-with-sidebar-box` | null | 12 | 16 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor |
| `331_pid_diagram` | `462353f` | 13 | 38 | 1 | 04_chars_missing, 10_font_sizes, 13_text_colours, 17_matched_runs, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 47_margins, 59_shape_anchor |
| `48_form_coloured_border_coloured_values` | `7112d76` | 13 | 17 | 1 | 05_chars_extra, 32_stroke_lines, 59_shape_anchor |
| `gst-invoice-multipage-item-table` | null | 14 | 100 | 4 | 05_chars_extra, 18_displacement, 25_invisible_text, 26_text_overlap, 27_text_off_page, 32_stroke_lines, 44_header_footer |
| `gst-invoice-horizontal-rules-only` | null | 16 | 16 | 1 | 04_chars_missing, 05_chars_extra, 18_displacement, 26_text_overlap, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 60_text_column_right_edge |
| `16_right_aligned_amounts_txtpos` | `462353f` | 17 | 17 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `21_form_labels_x60_values_x300_txtpos` | `462353f` | 21 | 21 | 1 | 05_chars_extra, 32_stroke_lines, 43_within_10pt_x, 47_margins |
| `product-catalogue-code-left-price-right` | null | 21 | 21 | 1 | 05_chars_extra, 32_stroke_lines, 47_margins |
| `340_bill_of_lading` | `462353f` | 29 | 98 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 60_text_column_right_edge |
| `323_credit_card_statement` | `462353f` | 31 | 142 | 1 | 04_chars_missing, 05_chars_extra, 13_text_colours, 17_matched_runs, 18_displacement, 25_invisible_text, 32_stroke_lines, 45_char_accuracy, 60_text_column_right_edge, 66_table_cell_width |
| `343_air_waybill` | `462353f` | 31 | 90 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 60_text_column_right_edge |
| `bus-timetable-station-left-times-right` | null | 36 | 36 | 1 | 05_chars_extra, 18_displacement, 32_stroke_lines |
| `353_admit_card` | `7112d76` | 37 | 93 | 1 | 04_chars_missing, 05_chars_extra, 18_displacement, 25_invisible_text, 26_text_overlap, 32_stroke_lines, 44_header_footer, 59_shape_anchor |
| `364_event_ticket` | `7112d76` | 39 | 48 | 1 | 04_chars_missing, 18_displacement, 25_invisible_text, 32_stroke_lines, 45_char_accuracy, 59_shape_anchor |
| `price-list-right-aligned-amounts` | null | 41 | 41 | 1 | 05_chars_extra, 17_matched_runs, 18_displacement, 25_invisible_text, 32_stroke_lines, 53_embedded_faces |
| `407_id_card_front_back` | `7112d76` | 46 | 46 | 1 | 32_stroke_lines |
| `400_comic_page_speech_bubbles` | `7112d76` | 47 | 63 | 1 | 04_chars_missing, 10_font_sizes, 13_text_colours, 17_matched_runs, 32_stroke_lines, 45_char_accuracy, 59_shape_anchor |

---

## 4. The headline

| question | answer |
|:--|--:|
| Documents failing `32_stroke_lines` in the committed Google store (of 192 scored) | **145** |
| … with **exactly one** rule in the source PDF (P1) | **11** |
| … with **exactly two** | 56 |
| … with **three or more** | 78 |
| … with **none** (a `32` failure no carrier can reach) | 0 |

**Upper bound on documents the per-rule carrier could deliver: 11 of 145.**

**Of those 11, how many fail only `32`, `05_chars_extra` and/or `18_displacement` — i.e. could actually
reach 42/42: 1 document, `334_patent_document`** (fails `05_chars_extra`, `32_stroke_lines`; engine
stamp `462353f`). That is the whole priceable value of the patch as it stands, and it agrees with the
prior in-repo measurement, which named the same single document.

For context on the shape of the opportunity: the reachable class — documents failing *only* within
`{05, 18, 32}`, the class's own ceiling — is **32 documents**, and their rule counts are
1 with one rule, 19 with two, 12 with three or more. So the per-rule carrier covers 1 of 32 (3%) of the
class it was built for, and 1 of 145 (0.7%) of the `32` failures.

Two further readings that change how that number should be priced:

* **The other ten one-rule documents are not one-rule documents for the carrier.** Only
  `365_recipe_card` and `371_experience_certificate` have a single hairline by the engine's own trigger
  (P2 = 1). The rest carry 12–109 thin strokes the engine's `isRuleShape` also matches — table cell
  borders and form boxes that the check's isolation test excludes but the carrier does not. On those, the
  patch emits 12–109 floating tables that stack. `311_fir_police_form` (104) and
  `325_demat_holdings_statement` (109) are the extreme cases.
* **Neither of the two strictly-single-hairline documents would reach 42/42.** `365_recipe_card` also
  fails `18_displacement`, `47_margins`, `60_text_column_right_edge`; `371_experience_certificate` fails
  six others. So on the strictest reading of "exactly one rule" the carrier delivers **zero** clean
  documents, and the single deliverable document in the census above is `334_patent_document`, which is
  one rule by the check's definition and fifteen hairlines by the engine's.

---

## 5. Where the count is ambiguous, and why

1. **The predicate, not the document, decides "exactly one" for 9 of the 11.** P1 says 1 rule, P2 says
   12–109 hairlines, on the same page of the same PDF. Both are defensible and they answer different
   questions: P1 is what the check scores, P2 is what the patch converts. Any pricing that uses "exactly
   one rule" as a safety gate is only safe under P1, and only if the carrier is narrowed to P1 — which is
   the change the prior finding already asked for (`isRuleShape` needs the isolation test).
2. **`academic-paper-ieee-2col-abstract` is a per-page question.** One rule in the document, on page 1,
   page 0 has none — total 1, busiest page 1. Safe for a per-document carrier; for a per-page carrier it
   depends on which page the carrier lands on. I counted document totals; the per-page vector is in
   `rules_census.json`.
3. **`394_map_with_legend` (P1 = 3) is ambiguous in the opposite direction** — the prior finding calls it
   3 and the patch's javadoc calls the third one a legend swatch, yet it reached 42/42. Whether a legend
   key or a map road *is* a rule is a judgement the geometry cannot make. It is not in the 145's one-rule
   bucket either way, but it is the reason the bucket is not a ceiling.
4. **A rule the engine drops before it reaches the shape writer is still counted here.** This is a census
   of the *source PDF*, not of the `.docx`. `394`'s scale bar is excluded by isolation and its diagonal
   map edges are never segments at all, but a hairline that the engine never emits as a shape cannot be
   carried by any patch, and
   nothing in the PDF tells the two apart. That biases the counts up, never down.
5. **The scores are committed, not fresh.** 72 of the 192 scored documents carry **no engine stamp**,
   and the prior report recorded 21 Google/LibreOffice pairs measured on different stamps. The 145 is a
   count of what the files say, crossed with what the PDFs draw today — not a re-measurement of HEAD.

## Reproducing

```bash
bash tools/p2w-bench/corpus-fetch.sh        # 213/213 PDFs, 0 missing
python3 /scratch/work/census_rules.py       # -> rules_census.json (P1/P2/P3, per page, per segment)
python3 /scratch/work/analyse.py            # cross with benchmarks/gverify/*.json
```
