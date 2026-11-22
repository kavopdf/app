# The `18_displacement` prize: how many documents go fully clean?

Read-only analysis of `gverify/` (213 per-document verification JSONs) and `CENSUS.csv` (62 rows). Every number below is computed by script from those two inputs; nothing is carried over from any prior leverage table.

## 1. Corpus and status

| status | documents |
|---|---|
| ok | 190 |
| page_count_refused | 23 |
| **total** | 213 |

- **MEASURED (status `ok`) documents: 190** — these are the only documents that carry a `failed` list, so all failure analysis below is over n = 190.
- **`page_count_refused`: 23** — these JSONs carry `name`, `status`, `pages`, `want` only. They have **no `failed` list at all**, so their check status is *not stated* and they cannot be counted as clean or dirty. Every count below is therefore a count over the 190 measured documents only.
- Failure-count distribution over the 190 measured docs: 0 failures: 28, 1 failure: 20, 2 failures: 16, 3 failures: 16, 4 failures: 31, 5 failures: 20, 6 failures: 24, 7 failures: 20, 8 failures: 6, 9 failures: 4, 10 failures: 5.
- **28 documents already pass every check** (0 failures) before any fix.
- **Check universe actually seen in `failed` lists: 33 distinct check names** (listed in §5). Caveat: the per-document `total` check count is not constant — {42: 126, 44: 2, 47: 62} — so the denominator varies by document; `passed + len(failed) == total` holds for all 190 measured docs.

## 2. Documents failing `18_displacement`

**109 of 190 measured documents (57.4%) fail `18_displacement`.** Of those, 12 fail it and nothing else, 9 fail it plus exactly one other check, and 88 fail it alongside two or more other checks.

### 2a. The 21 documents with ≤ 2 failures (the entire prize zone)

| document | #fail | full failed set | pages |
|---|---|---|---|
| 16_right_aligned_amounts_txtpos | 1 | 18_displacement | not stated |
| 31_times_body_arial_headings | 1 | 18_displacement | 1 |
| 362_price_list_dense | 1 | 18_displacement | not stated |
| 68_journal_wide_table_spanning | 1 | 18_displacement | 1 |
| 71_invoice_space_aligned_no_rules | 1 | 18_displacement | 1 |
| 72_bank_statement_no_rules_right_amounts | 1 | 18_displacement | not stated |
| balance-sheet-two-columns-of-figures | 1 | 18_displacement | not stated |
| bus-timetable-station-left-times-right | 1 | 18_displacement | not stated |
| insurance-policy-schedule | 1 | 18_displacement | not stated |
| mobile-bill | 1 | 18_displacement | 1 |
| table-with-no-header-row | 1 | 18_displacement | not stated |
| two-tables-stacked-with-no-gap | 1 | 18_displacement | not stated |
| 23_timetable_grid_txtpos | 2 | 18_displacement, 59_shape_anchor | 1 |
| 303_discharge_summary | 2 | 18_displacement, 25_invisible_text | not stated |
| 30_mixed_font_sizes_one_baseline_txtpos | 2 | 18_displacement, 59_shape_anchor | not stated |
| 325_demat_holdings_statement | 2 | 18_displacement, 25_invisible_text | not stated |
| 370_offer_letter | 2 | 18_displacement, 60_text_column_right_edge | 1 |
| 393_spectrum_peak_table | 2 | 18_displacement, 60_text_column_right_edge | not stated |
| 402_calendar_month_grid | 2 | 05_chars_extra, 18_displacement | not stated |
| 412_page_labels_roman | 2 | 18_displacement, 27_text_off_page | not stated |
| 416_many_tiny_pages | 2 | 18_displacement, 27_text_off_page | not stated |

### 2b. The remaining documents failing `18_displacement` (binned, full counts)

| failures on that document | documents failing 18_displacement |
|---|---|
| 1 | 12 |
| 2 | 9 |
| 3 | 7 |
| 4 | 25 |
| 5 | 15 |
| 6 | 19 |
| 7 | 14 |
| 8 | 5 |
| 10 | 3 |
| **total** | 109 |

The 88 documents in the 3+ bin are listed in full in the appendix (their complete failed sets are there too), because clearing `18_displacement` alone cannot make any of them clean — each still carries two or more other failures.

## 3. The real prize: clearing `18_displacement` alone

### 3a. Fail `18_displacement` and nothing else → clearing it makes them FULLY CLEAN: **12 documents**

| document | pages | in CENSUS.csv? | census problem |
|---|---|---|---|
| 16_right_aligned_amounts_txtpos | not stated | **no** | — |
| 31_times_body_arial_headings | 1 | yes | content-partly-lost-and-displaced |
| 362_price_list_dense | not stated | **no** | — |
| 68_journal_wide_table_spanning | 1 | yes | content-present-wholly-displaced |
| 71_invoice_space_aligned_no_rules | 1 | yes | content-present-wholly-displaced |
| 72_bank_statement_no_rules_right_amounts | not stated | **no** | — |
| balance-sheet-two-columns-of-figures | not stated | **no** | — |
| bus-timetable-station-left-times-right | not stated | **no** | — |
| insurance-policy-schedule | not stated | **no** | — |
| mobile-bill | 1 | yes | content-present-partly-displaced |
| table-with-no-header-row | not stated | **no** | — |
| two-tables-stacked-with-no-gap | not stated | **no** | — |

### 3b. Fail `18_displacement` plus exactly one other check: **9 documents**

| the other check | documents | which documents |
|---|---|---|
| 59_shape_anchor | 2 | 23_timetable_grid_txtpos, 30_mixed_font_sizes_one_baseline_txtpos |
| 25_invisible_text | 2 | 303_discharge_summary, 325_demat_holdings_statement |
| 60_text_column_right_edge | 2 | 370_offer_letter, 393_spectrum_peak_table |
| 27_text_off_page | 2 | 412_page_labels_roman, 416_many_tiny_pages |
| 05_chars_extra | 1 | 402_calendar_month_grid |
| **total** | 9 |  |

The other check is spread thin: no partner accounts for more than 2 of the 9. So the ≤2-failure prize is **12 documents for free and 2 more per partner check** — clearing `18_displacement` + any one of `59_shape_anchor`, `25_invisible_text`, `60_text_column_right_edge` or `27_text_off_page` buys 14 clean documents; adding `05_chars_extra` as well would reach 15. Beyond that, each extra check has to be fixed for a single document.

## 4. Census join: is the 18_displacement signature a constant offset or a tail?

**Coverage caveat, stated plainly:** `CENSUS.csv` has only 62 rows against 190 measured documents, so it joins to 39 of the 109 `18_displacement` documents and 20 of the 81 other measured documents. Worse for this question: `dx_pt`/`dy_pt` are **blank on 32 of the 62 census rows** (those rows also have blank `explains` and `moved_gt20`), so the displacement estimate exists for only 23 of the 109 `18_displacement` documents and 5 of the 81 others. The comparison below is therefore **23 vs 5 documents**, not 109 vs 81 — it is indicative, not conclusive.

`share5` and `max_pt` are populated on all 39 / 20 joined rows, so those two comparisons are the solid ones.

| group | field | n | min | q1 | median | q3 | max |
|---|---|---|---|---|---|---|---|
| 18_displacement | share5 | 39 | 0.01 | 1.84 | 5.16 | 11.99 | 81.64 |
| 18_displacement | max_pt | 39 | 2.88 | 7.68 | 14.88 | 20.88 | 177.60 |
| 18_displacement | dy_pt | 23 | -0.50 | 0.00 | 0.00 | 0.30 | 102.70 |
| 18_displacement | dx_pt | 23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.70 |
| all other measured | share5 | 20 | 0.11 | 1.80 | 2.50 | 3.00 | 6.34 |
| all other measured | max_pt | 20 | 4.32 | 8.52 | 14.16 | 26.04 | 66.24 |
| all other measured | dy_pt | 5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| all other measured | dx_pt | 5 | -0.50 | 0.00 | 0.00 | 0.00 | 0.00 |

### Tolerance shares on |dy_pt| and |dx_pt|

| group | tolerance | count | share |
|---|---|---|---|
| 18_displacement | abs(dy_pt) ≤ 1 | 20/23 | 87.0% |
| 18_displacement | abs(dy_pt) ≤ 2 | 21/23 | 91.3% |
| 18_displacement | abs(dy_pt) ≤ 5 | 21/23 | 91.3% |
| 18_displacement | abs(dx_pt) ≤ 1 | 23/23 | 100.0% |
| 18_displacement | abs(dx_pt) ≤ 2 | 23/23 | 100.0% |
| 18_displacement | abs(dx_pt) ≤ 5 | 23/23 | 100.0% |
| all other measured | abs(dy_pt) ≤ 1 | 5/5 | 100.0% |
| all other measured | abs(dy_pt) ≤ 2 | 5/5 | 100.0% |
| all other measured | abs(dy_pt) ≤ 5 | 5/5 | 100.0% |
| all other measured | abs(dx_pt) ≤ 1 | 5/5 | 100.0% |
| all other measured | abs(dx_pt) ≤ 2 | 5/5 | 100.0% |
| all other measured | abs(dx_pt) ≤ 5 | 5/5 | 100.0% |

Sorted |dy_pt| for the 23 `18_displacement` docs with a value: `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.5, 0.5, 0.5, 1.0, 1.4, 26.9, 102.7]`.

Sorted |dy_pt| for the 5 other measured docs with a value: `[0.0, 0.0, 0.0, 0.0, 0.0]`.

**The two large-|dy| outliers are these, and both are already deep in the failure tail:**

| document | #fail | dy_pt | dx_pt | max_pt | share5 | explains | moved_gt20 | signal |
|---|---|---|---|---|---|---|---|---|
| 600_reviewed_invoice_with_annotations | 7 | 102.7 | 0.0 | 62.88 | 62.46 | 28.0 | 1.0 | annotations-present |
| 601_fillable_admission_form | 7 | 26.9 | 0.0 | 27.84 | 52.39 | 15.0 | 8.0 | none-identified |

### Signature verdict (numbers only, no hand-waving)

- `dx_pt` is essentially exactly zero: all 23 `18_displacement` docs with a value have |dx| ≤ 0.7 pt, 19 of them at exactly 0.0. There is no horizontal component to chase.
- `dy_pt` is **not** a shared non-zero constant. The modal value is 0.0 (15 of 23 docs at exactly 0.0), and 19 of 23 sit within 0.5 pt, 20 within 1 pt, 21 within 2 pt and 21 within 5 pt of zero. Nothing in the set clusters at, say, 3 pt or 10 pt.
- Beyond 5 pt there are exactly **2 documents**: `601_fillable_admission_form` (26.9 pt) and `600_reviewed_invoice_with_annotations` (102.7 pt). Both have 7 failures, so neither becomes clean no matter what happens to `18_displacement`.
- `max_pt` does **not** separate the two groups at all (median 14.88 pt for `18_displacement` vs 14.16 pt for the others), so the 18 failures are not "bigger movements" than what other documents survive.
- `share5` is the one field that separates them: median 5.16% for `18_displacement` vs 2.50% for the others, with the 18 set spanning 0.01%–81.64% (q1 1.84%, q3 11.99%). That is a shift of the *mass* of characters, not a single constant.

**So: it is a tail, not a constant offset.** The distribution is one tight mode at |dy| ≈ 0 pt — which means the census's own rigid-shift estimate finds *no* systematic vertical displacement to explain most of these failures — plus a two-document far tail at 26.9 pt and 102.7 pt. Calling it "one constant vertical offset with a tolerance tail" would mis-describe it twice over: the constant is zero, not a shared non-zero shift, and the tail is 2 documents out of 23, both of which are unfixable by any single check. Equally important: |dy| ≈ 0 is **not** a clean discriminator either — all 5 other measured docs with a value are also at 0.0 pt and do *not* fail `18_displacement`. Whatever makes 19 zero-dy documents fail and 5 zero-dy documents pass is not a rigid vertical constant at all.

## 5. Independent clean-leverage table (all 190 measured documents)

Computed from scratch: (a) = documents whose failed set is exactly this one check; (b) = documents whose failed set contains this check and has size ≤ 2. Denominators: 190 measured docs; 20 have exactly 1 failure, 16 have exactly 2.

**(a) Top 8 by number of documents where the check is the ONLY failure**

| rank | check | only-failure docs (a) | only-or-exactly-two (b) | docs failing it at all |
|---|---|---|---|---|
| 1 | 18_displacement | 12 | 21 | 109 |
| 2 | 60_text_column_right_edge | 4 | 8 | 56 |
| 3 | 32_stroke_lines | 2 | 2 | 85 |
| 4 | 25_invisible_text | 1 | 5 | 47 |
| 5 | 47_margins | 1 | 4 | 24 |
| 6 | 27_text_off_page | 0 | 3 | 17 |
| 7 | 05_chars_extra | 0 | 2 | 79 |
| 8 | 04_chars_missing | 0 | 2 | 66 |

**(b) Top 8 by number of documents where it is the only failure or one of exactly two**

| rank | check | only-or-exactly-two (b) | only-failure docs (a) | docs failing it at all |
|---|---|---|---|---|
| 1 | 18_displacement | 21 | 12 | 109 |
| 2 | 60_text_column_right_edge | 8 | 4 | 56 |
| 3 | 25_invisible_text | 5 | 1 | 47 |
| 4 | 47_margins | 4 | 1 | 24 |
| 5 | 27_text_off_page | 3 | 0 | 17 |
| 6 | 32_stroke_lines | 2 | 2 | 85 |
| 7 | 05_chars_extra | 2 | 0 | 79 |
| 8 | 04_chars_missing | 2 | 0 | 66 |

Full table (all 33 checks seen), sorted by (a):

| check | (a) only | (b) only-or-two | docs failing at all |
|---|---|---|---|
| 04_chars_missing | 0 | 2 | 66 |
| 05_chars_extra | 0 | 2 | 79 |
| 10_font_sizes | 0 | 0 | 6 |
| 13_text_colours | 0 | 0 | 32 |
| 17_matched_runs | 0 | 1 | 30 |
| 18_displacement | 12 | 21 | 109 |
| 23_line_pitch | 0 | 0 | 3 |
| 25_invisible_text | 1 | 5 | 47 |
| 26_text_overlap | 0 | 0 | 17 |
| 27_text_off_page | 0 | 3 | 17 |
| 28_clipped_at_edge | 0 | 0 | 1 |
| 31_pages_lost_their_text | 0 | 0 | 1 |
| 32_stroke_lines | 2 | 2 | 85 |
| 34a_span_size_match | 0 | 0 | 2 |
| 35_rotation | 0 | 0 | 12 |
| 37_super_subscript | 0 | 0 | 1 |
| 38_list_markers | 0 | 0 | 2 |
| 40_link_targets | 0 | 0 | 1 |
| 43_within_10pt_x | 0 | 1 | 11 |
| 44_header_footer | 0 | 1 | 32 |
| 45_char_accuracy | 0 | 0 | 37 |
| 46_text_crossing_rule | 0 | 0 | 1 |
| 47_margins | 1 | 4 | 24 |
| 51_field_values | 0 | 0 | 1 |
| 52_outline | 0 | 0 | 1 |
| 53_embedded_faces | 0 | 0 | 4 |
| 59_shape_anchor | 0 | 2 | 52 |
| 60_text_column_right_edge | 4 | 8 | 56 |
| 62_table_columns | 0 | 0 | 3 |
| 63_table_rows | 0 | 0 | 3 |
| 64_table_span_across | 0 | 0 | 1 |
| 65_table_span_down | 0 | 0 | 1 |
| 66_table_cell_width | 0 | 0 | 4 |

`18_displacement` is rank 1 on both measures — 12 only-failure documents against 4 for the next-best check (`60_text_column_right_edge`), and 21 ≤2-failure documents against 8. It is the single highest-leverage check in the corpus, and no other check is close.

## 6. Verdict

1. Clearing `18_displacement` alone makes exactly **12 of 190 measured documents fully clean** (6.3%): 16_right_aligned_amounts_txtpos, 31_times_body_arial_headings, 362_price_list_dense, 68_journal_wide_table_spanning, 71_invoice_space_aligned_no_rules, 72_bank_statement_no_rules_right_amounts, balance-sheet-two-columns-of-figures, bus-timetable-station-left-times-right, insurance-policy-schedule, mobile-bill, table-with-no-header-row, two-tables-stacked-with-no-gap.
2. A further **9 documents** sit one check away — 2 each from `59_shape_anchor`, `25_invisible_text`, `60_text_column_right_edge`, `27_text_off_page`, 1 from `05_chars_extra` — so the realistic ≤2-fix prize is 14–21 documents, not 12.
3. **The "single vertical-constant fix" premise is only weakly supported by the census.** `dx_pt` ≈ 0 everywhere (good), but `dy_pt` is 0.0–1.4 pt on 21 of the 23 documents that have a value — the census finds no shared non-zero vertical constant to fix.
4. What is left is a **2-document tail** (`601_fillable_admission_form` 26.9 pt, `600_reviewed_invoice_with_annotations` 102.7 pt), both 7-failure documents that no single check will clean.
5. And dy ≈ 0 does not discriminate: all 5 other measured docs with a dy value are at 0.0 pt yet pass `18_displacement`. Whatever the check is reacting to is mostly sub-pt or non-rigid.
6. Unmeasurable: the 23 `page_count_refused` documents have no `failed` list, so their clean/dirty status is not stated and the true clean count cannot be determined from these inputs — they are excluded from all counts above, and 131 of the 190 measured docs are absent from `CENSUS.csv` entirely.

## Appendix — every document failing `18_displacement` (all 109 rows, sorted by failure count ascending)

| # | document | #fail | sorted full failed set | pages |
|---|---|---|---|---|
| 1 | 16_right_aligned_amounts_txtpos | 1 | 18_displacement | not stated |
| 2 | 31_times_body_arial_headings | 1 | 18_displacement | 1 |
| 3 | 362_price_list_dense | 1 | 18_displacement | not stated |
| 4 | 68_journal_wide_table_spanning | 1 | 18_displacement | 1 |
| 5 | 71_invoice_space_aligned_no_rules | 1 | 18_displacement | 1 |
| 6 | 72_bank_statement_no_rules_right_amounts | 1 | 18_displacement | not stated |
| 7 | balance-sheet-two-columns-of-figures | 1 | 18_displacement | not stated |
| 8 | bus-timetable-station-left-times-right | 1 | 18_displacement | not stated |
| 9 | insurance-policy-schedule | 1 | 18_displacement | not stated |
| 10 | mobile-bill | 1 | 18_displacement | 1 |
| 11 | table-with-no-header-row | 1 | 18_displacement | not stated |
| 12 | two-tables-stacked-with-no-gap | 1 | 18_displacement | not stated |
| 13 | 23_timetable_grid_txtpos | 2 | 18_displacement, 59_shape_anchor | 1 |
| 14 | 303_discharge_summary | 2 | 18_displacement, 25_invisible_text | not stated |
| 15 | 30_mixed_font_sizes_one_baseline_txtpos | 2 | 18_displacement, 59_shape_anchor | not stated |
| 16 | 325_demat_holdings_statement | 2 | 18_displacement, 25_invisible_text | not stated |
| 17 | 370_offer_letter | 2 | 18_displacement, 60_text_column_right_edge | 1 |
| 18 | 393_spectrum_peak_table | 2 | 18_displacement, 60_text_column_right_edge | not stated |
| 19 | 402_calendar_month_grid | 2 | 05_chars_extra, 18_displacement | not stated |
| 20 | 412_page_labels_roman | 2 | 18_displacement, 27_text_off_page | not stated |
| 21 | 416_many_tiny_pages | 2 | 18_displacement, 27_text_off_page | not stated |
| 22 | 300_prescription_rx | 3 | 18_displacement, 25_invisible_text, 59_shape_anchor | not stated |
| 23 | 306_clinical_protocol_synopsis | 3 | 18_displacement, 25_invisible_text, 59_shape_anchor | not stated |
| 24 | 340_bill_of_lading | 3 | 18_displacement, 59_shape_anchor, 60_text_column_right_edge | not stated |
| 25 | 342_packing_list | 3 | 18_displacement, 25_invisible_text, 60_text_column_right_edge | not stated |
| 26 | 343_air_waybill | 3 | 18_displacement, 59_shape_anchor, 60_text_column_right_edge | not stated |
| 27 | 363_warranty_card | 3 | 18_displacement, 59_shape_anchor, 60_text_column_right_edge | 1 |
| 28 | 374_org_chart | 3 | 05_chars_extra, 18_displacement, 26_text_overlap | 1 |
| 29 | 25_signature_block_underscores_txtpos | 4 | 04_chars_missing, 18_displacement, 45_char_accuracy, 60_text_column_right_edge | not stated |
| 30 | 311_fir_police_form | 4 | 04_chars_missing, 18_displacement, 45_char_accuracy, 60_text_column_right_edge | not stated |
| 31 | 324_loan_amortisation_schedule | 4 | 18_displacement, 25_invisible_text, 27_text_off_page, 59_shape_anchor | not stated |
| 32 | 330_cad_drawing_sheet | 4 | 04_chars_missing, 18_displacement, 45_char_accuracy, 47_margins | 1 |
| 33 | 35_four_typefaces_one_page | 4 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor | 1 |
| 34 | 365_recipe_card | 4 | 18_displacement, 32_stroke_lines, 47_margins, 60_text_column_right_edge | not stated |
| 35 | 36_embedded_subset_font | 4 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor | not stated |
| 36 | 372_timesheet_grid | 4 | 18_displacement, 25_invisible_text, 59_shape_anchor, 60_text_column_right_edge | not stated |
| 37 | 373_leave_application_form | 4 | 05_chars_extra, 18_displacement, 23_line_pitch, 60_text_column_right_edge | not stated |
| 38 | 404_sudoku_grid | 4 | 18_displacement, 23_line_pitch, 47_margins, 59_shape_anchor | not stated |
| 39 | 406_passport_mrz_page | 4 | 05_chars_extra, 18_displacement, 59_shape_anchor, 60_text_column_right_edge | 1 |
| 40 | 417_rotate180_and_mirrored | 4 | 04_chars_missing, 17_matched_runs, 18_displacement, 27_text_off_page | 2 |
| 41 | 52_one_cm_margin_wide_body | 4 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor | not stated |
| 42 | 59_landscape_mixed_portrait | 4 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor | not stated |
| 43 | 602_bookmarked_annual_report | 4 | 04_chars_missing, 18_displacement, 27_text_off_page, 52_outline | not stated |
| 44 | 70_magazine_drop_cap_photo_caption | 4 | 04_chars_missing, 18_displacement, 32_stroke_lines, 44_header_footer | 1 |
| 45 | 76_devanagari_table | 4 | 17_matched_runs, 18_displacement, 34a_span_size_match, 47_margins | 1 |
| 46 | boq-tender-bill-of-quantities | 4 | 05_chars_extra, 18_displacement, 32_stroke_lines, 60_text_column_right_edge | not stated |
| 47 | brochure-3col-with-sidebar-box | 4 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor | 1 |
| 48 | electricity-bill | 4 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines | 1 |
| 49 | eway-bill | 4 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines | not stated |
| 50 | landscape-page-inside-portrait-document | 4 | 05_chars_extra, 18_displacement, 32_stroke_lines, 60_text_column_right_edge | 3 |
| 51 | marksheet-subject-left-marks-right | 4 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines | not stated |
| 52 | marksheet-university-consolidated | 4 | 05_chars_extra, 18_displacement, 32_stroke_lines, 60_text_column_right_edge | not stated |
| 53 | table-with-merged-cells | 4 | 05_chars_extra, 18_displacement, 32_stroke_lines, 60_text_column_right_edge | not stated |
| 54 | 360_restaurant_menu | 5 | 18_displacement, 32_stroke_lines, 43_within_10pt_x, 47_margins, 60_text_column_right_edge | 1 |
| 55 | 42_table_coloured_header_alternating_rows | 5 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines, 59_shape_anchor | not stated |
| 56 | 50_invoice_coloured_total_row | 5 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines, 59_shape_anchor | not stated |
| 57 | 56_table_indented_from_margin | 5 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 60_text_column_right_edge | not stated |
| 58 | 57_centred_title_page_left_body_pages | 5 | 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer | not stated |
| 59 | 64_newspaper_uneven_columns_ad_boxes | 5 | 05_chars_extra, 18_displacement, 23_line_pitch, 26_text_overlap, 59_shape_anchor | 1 |
| 60 | 79_inr_indian_digit_grouping_table | 5 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 60_text_column_right_edge | 1 |
| 61 | balance-sheet-and-profit-loss | 5 | 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 60_text_column_right_edge | not stated |
| 62 | gst-invoice-3line-items | 5 | 05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines, 60_text_column_right_edge | not stated |
| 63 | invoice-line-items-qty-rate-amount | 5 | 05_chars_extra, 18_displacement, 25_invisible_text, 26_text_overlap, 32_stroke_lines | not stated |
| 64 | itr-computation-with-slab-table | 5 | 05_chars_extra, 18_displacement, 26_text_overlap, 32_stroke_lines, 63_table_rows | 1 |
| 65 | property-tax-receipt | 5 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 32_stroke_lines | not stated |
| 66 | report-2col-table-spanning-both-columns | 5 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 44_header_footer | not stated |
| 67 | salary-slip-factory-wages | 5 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 60_text_column_right_edge | not stated |
| 68 | table-inside-two-column-page | 5 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 44_header_footer | 1 |
| 69 | 01_stamp_rotated_15deg_upright | 6 | 04_chars_missing, 13_text_colours, 18_displacement, 25_invisible_text, 35_rotation, 59_shape_anchor | not stated |
| 70 | 02_stamp_rotated_15deg_upleft | 6 | 04_chars_missing, 13_text_colours, 18_displacement, 25_invisible_text, 35_rotation, 59_shape_anchor | not stated |
| 71 | 04_stamp_180deg_upside_down | 6 | 04_chars_missing, 13_text_colours, 18_displacement, 25_invisible_text, 35_rotation, 59_shape_anchor | not stated |
| 72 | 344_customs_declaration | 6 | 04_chars_missing, 13_text_colours, 18_displacement, 25_invisible_text, 59_shape_anchor, 60_text_column_right_edge | not stated |
| 73 | 364_event_ticket | 6 | 04_chars_missing, 18_displacement, 25_invisible_text, 32_stroke_lines, 45_char_accuracy, 59_shape_anchor | not stated |
| 74 | 381_incident_report_timeline | 6 | 04_chars_missing, 05_chars_extra, 18_displacement, 25_invisible_text, 59_shape_anchor, 60_text_column_right_edge | not stated |
| 75 | 38_faux_bold_italic_synthesised | 6 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 60_text_column_right_edge | 1 |
| 76 | 40_devanagari_shaping_font | 6 | 05_chars_extra, 18_displacement, 32_stroke_lines, 34a_span_size_match, 38_list_markers, 47_margins | 1 |
| 77 | 58_header_rule_footer_rule | 6 | 04_chars_missing, 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer | not stated |
| 78 | 75_merged_header_cell_three_columns | 6 | 05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 64_table_span_across, 65_table_span_down | 1 |
| 79 | 78_mixed_english_devanagari_line | 6 | 05_chars_extra, 17_matched_runs, 18_displacement, 26_text_overlap, 43_within_10pt_x, 47_margins | 1 |
| 80 | form16-part-b | 6 | 04_chars_missing, 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 60_text_column_right_edge | not stated |
| 81 | gst-invoice-with-qr-code | 6 | 05_chars_extra, 18_displacement, 25_invisible_text, 26_text_overlap, 32_stroke_lines, 66_table_cell_width | not stated |
| 82 | newspaper-2col-fullwidth-headline | 6 | 04_chars_missing, 05_chars_extra, 18_displacement, 26_text_overlap, 32_stroke_lines, 45_char_accuracy | not stated |
| 83 | payslip-label-left-amount-right | 6 | 05_chars_extra, 17_matched_runs, 18_displacement, 25_invisible_text, 32_stroke_lines, 53_embedded_faces | 1 |
| 84 | price-list-right-aligned-amounts | 6 | 05_chars_extra, 17_matched_runs, 18_displacement, 25_invisible_text, 32_stroke_lines, 53_embedded_faces | 1 |
| 85 | purchase-order | 6 | 05_chars_extra, 18_displacement, 25_invisible_text, 26_text_overlap, 32_stroke_lines, 60_text_column_right_edge | not stated |
| 86 | salary-slip-corporate | 6 | 05_chars_extra, 17_matched_runs, 18_displacement, 25_invisible_text, 32_stroke_lines, 53_embedded_faces | 1 |
| 87 | text-held-twice-shadow-text | 6 | 05_chars_extra, 13_text_colours, 18_displacement, 25_invisible_text, 32_stroke_lines, 60_text_column_right_edge | 1 |
| 88 | 03_stamp_vertical_90deg | 7 | 04_chars_missing, 13_text_colours, 18_displacement, 35_rotation, 59_shape_anchor, 62_table_columns, 63_table_rows | 1 |
| 89 | 08_two_overlapping_stamps | 7 | 04_chars_missing, 13_text_colours, 17_matched_runs, 18_displacement, 25_invisible_text, 35_rotation, 45_char_accuracy | not stated |
| 90 | 13_stamp_non_english | 7 | 04_chars_missing, 13_text_colours, 17_matched_runs, 18_displacement, 35_rotation, 45_char_accuracy, 59_shape_anchor | not stated |
| 91 | 383_api_docs_page | 7 | 04_chars_missing, 18_displacement, 25_invisible_text, 47_margins, 59_shape_anchor, 60_text_column_right_edge, 66_table_cell_width | not stated |
| 92 | 600_reviewed_invoice_with_annotations | 7 | 05_chars_extra, 18_displacement, 28_clipped_at_edge, 32_stroke_lines, 45_char_accuracy, 47_margins, 62_table_columns | 1 |
| 93 | 601_fillable_admission_form | 7 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 51_field_values, 53_embedded_faces, 59_shape_anchor | 1 |
| 94 | 80_gstin_pan_cin_ifsc_table | 7 | 04_chars_missing, 17_matched_runs, 18_displacement, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 59_shape_anchor | 1 |
| 95 | admit-card | 7 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 32_stroke_lines, 45_char_accuracy, 59_shape_anchor | 1 |
| 96 | bank-statement-5-pages | 7 | 05_chars_extra, 18_displacement, 25_invisible_text, 27_text_off_page, 32_stroke_lines, 44_header_footer, 59_shape_anchor | not stated |
| 97 | gst-invoice-multipage-item-table | 7 | 05_chars_extra, 18_displacement, 25_invisible_text, 26_text_overlap, 27_text_off_page, 32_stroke_lines, 44_header_footer | not stated |
| 98 | mutual-fund-statement | 7 | 05_chars_extra, 18_displacement, 25_invisible_text, 27_text_off_page, 32_stroke_lines, 60_text_column_right_edge, 66_table_cell_width | not stated |
| 99 | table-across-page-break-repeated-header | 7 | 04_chars_missing, 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer, 60_text_column_right_edge | not stated |
| 100 | table-with-rotated-header | 7 | 04_chars_missing, 05_chars_extra, 18_displacement, 32_stroke_lines, 45_char_accuracy, 47_margins, 59_shape_anchor | not stated |
| 101 | very-long-single-column-table | 7 | 04_chars_missing, 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer, 60_text_column_right_edge | 3 |
| 102 | 323_credit_card_statement | 8 | 04_chars_missing, 13_text_colours, 17_matched_runs, 18_displacement, 25_invisible_text, 45_char_accuracy, 60_text_column_right_edge, 66_table_cell_width | not stated |
| 103 | 353_admit_card | 8 | 04_chars_missing, 05_chars_extra, 18_displacement, 25_invisible_text, 26_text_overlap, 32_stroke_lines, 44_header_footer, 59_shape_anchor | not stated |
| 104 | 77_arabic_rtl_document | 8 | 05_chars_extra, 17_matched_runs, 18_displacement, 26_text_overlap, 43_within_10pt_x, 47_margins, 59_shape_anchor, 60_text_column_right_edge | 1 |
| 105 | delivery-challan | 8 | 04_chars_missing, 05_chars_extra, 13_text_colours, 18_displacement, 25_invisible_text, 26_text_overlap, 32_stroke_lines, 60_text_column_right_edge | not stated |
| 106 | gst-invoice-horizontal-rules-only | 8 | 04_chars_missing, 05_chars_extra, 18_displacement, 26_text_overlap, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 60_text_column_right_edge | not stated |
| 107 | 322_mutual_fund_factsheet | 10 | 04_chars_missing, 13_text_colours, 17_matched_runs, 18_displacement, 25_invisible_text, 26_text_overlap, 44_header_footer, 45_char_accuracy, 59_shape_anchor, 60_text_column_right_edge | not stated |
| 108 | academic-paper-ieee-2col-abstract | 10 | 04_chars_missing, 05_chars_extra, 17_matched_runs, 18_displacement, 27_text_off_page, 32_stroke_lines, 44_header_footer, 45_char_accuracy, 47_margins, 60_text_column_right_edge | 2 |
| 109 | one-page-rotated-180-degrees | 10 | 04_chars_missing, 05_chars_extra, 18_displacement, 27_text_off_page, 32_stroke_lines, 43_within_10pt_x, 44_header_footer, 60_text_column_right_edge, 62_table_columns, 63_table_rows | 2 |

