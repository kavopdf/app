# The 84 gate-blocking documents, classified by Google check outcome — and what the debt actually is

**28 Nov 2026.** Read-only analysis of a fresh `--depth 1` clone of `kavopdf/app`. Every number below comes from one
of three committed sources, named in the table heading and the prose:

* `benchmarks/RANKING-BASELINE.csv` — the 15 Nov floor (213 data rows, 213 distinct documents).
* `benchmarks/RANKING.csv` — the current full-corpus measurement (213 data rows, 213 distinct documents).
* `benchmarks/gverify/*.json` — Google's per-document check results (214 files, one per corpus document, including
  `416_many_tiny_pages` which has no row in `RANKING.csv`).

## What was counted

The population is defined exactly as the commit gate defines it: a document is *worse than the 15 Nov baseline*
when its `share5` in `benchmarks/RANKING.csv` is **strictly greater** than its `share5` in
`benchmarks/RANKING-BASELINE.csv`. That test returns **84 documents**, and it is the test `tools/p2w-bench/regress.py`
actually applies (`if b is not None and c > b + 1e-9`), which is the tool that prints `docx: 84 REGRESSION(S)` and
refuses the commit.

One caveat worth recording, because two tools in this repository do not agree on it: `benchmarks/gate.py`'s
`ratchet()` uses a `delta > 0.5` deadband (`if delta > 0.5: reg.append(...)`). Eleven of the 84 sit in the
0 < delta <= 0.5 band (`25_signature_block_underscores_txtpos` +0.01 … `383_api_docs_page` +0.50), so
`gate.py --ratchet-only` would report **73** regressions where `regress.py` reports **84**. The 84 used here is the
strict count, i.e. `regress.py`'s, as instructed. The 11 band documents are all small deltas and none of them changes
a group's character, but a reader comparing the two tools' numbers should expect 84 vs 73, not a contradiction.

Each of the 84 was joined by document name to its `benchmarks/gverify/<document>.json`. All 84 have a gverify
record and **none of the 84 carries `status: "page_count_refused"`** — so no row is skipped and all 84 are
classified. `failed` is a list in every one of the 84 records; `len(failed)` is the Google failed count. The number
of checks actually run varies by document (`total` is 42 for 46 of the 84, 47 for 37 of them, and 44 for one), so
"passes every applicable check" means `len(failed) == 0` against whatever `total` that document was scored on.

## Headline

| class | documents | share of 84 |
|:--|--:|--:|
| (a) pass every applicable Google check (`failed == 0`) | **10** | 11.9% |
| (b) fail exactly 1 check | **19** | 22.6% |
| (b) fail exactly 2 checks | **15** | 17.9% |
| (b) fail 3 or more checks | **40** | 47.6% |
| **total** | **84** | 100% |

So **10 of the 84 pass every Google check they were scored on and are still worse than the 15 Nov floor.** They are:

* `electricity-bill` — 16.24 → 36.78 (+20.54), 47/47 passed, signature `displacement`
* `mobile-bill` — 18.48 → 30.09 (+11.61), 47/47 passed, signature `displacement`
* `insurance-policy-schedule` — 13.29 → 22.66 (+9.37), 47/47 passed, signature `displacement`
* `73_marksheet_subject_marks_grade` — 0.00 → 7.95 (+7.95), 42/42 passed, signature `displacement`
* `33_sans_nondefault_body` — 4.49 → 10.73 (+6.24), 42/42 passed, signature `displacement`
* `36_embedded_subset_font` — 0.00 → 4.91 (+4.91), 42/42 passed, signature `displacement`
* `16_right_aligned_amounts_txtpos` — 0.00 → 3.83 (+3.83), 42/42 passed, signature `displacement`
* `41_coloured_headings_white_bg` — 0.00 → 2.16 (+2.16), 42/42 passed, signature `displacement`
* `29_dot_leaders_txtpos` — 0.00 → 0.89 (+0.89), 42/42 passed, signature `clean`
* `362_price_list_dense` — 0.03 → 0.82 (+0.79), 42/42 passed, signature `clean`

That is the single most important fact in this file: the debt is **not** a Google-check debt. For 10 of the 84 the
only thing that moved is the repository's own `share@5px` metric, against a floor set by a different engine
(`ead0d0e`, per `FINDINGS/GATE-84-REGRESSIONS-ARE-FIVE-CONSTRUCTS-AND-THE-RUNG-WAS-JUDGED-AGAINST-THE-WRONG-TABLE-28NOV-relay.md`).
A fix aimed only at the failing Google checks cannot clear the gate; it would leave these 10 in place.

Across the 84 the summed delta is **+547.79 share5 points**. The 10 pass-all documents account for **+68.29** of it;
the other 74 account for **+479.50**. The 18 documents with a delta above 10 points account for **+367.82**, i.e. 67%
of the total delta sits in 21% of the documents.

## Groups

The clone carries only six PDFs (`benchmarks/realworld/`, `benchmarks/corpus-extra/`) and none of them is one of the
84, so the *content* of the 84 documents is not in the repository and could not be read. Grouping therefore uses the
document name, cross-checked against the `signature`, `problem` and `pages` columns of `benchmarks/RANKING.csv`.
Names were matched to one group only, in a fixed priority order (stamps, then tables, then money, then forms, then
typography, then the remainder), so the counts below partition the 84 and sum to 84. The exact name patterns used for
each group are listed with the group descriptions, and the same patterns are reproduced in the derivation note at the
end, so anyone can re-derive or contest a group assignment.

| group | documents | pass all | fail 1 | fail 2 | fail 3+ | summed delta | largest delta | most-failed check |
|:--|--:|--:|--:|--:|--:|--:|:--|:--|
| Ruled tables | 26 | 1 | 6 | 6 | 13 | +247.04 | `table-with-no-header-row` +46.87 | `18_displacement` (21/26) |
| Invoices/amounts | 21 | 4 | 7 | 3 | 7 | +164.25 | `price-list-2col-dense-right-aligned` +25.20 | `18_displacement` (13/21) |
| Stamps | 10 | 0 | 1 | 0 | 9 | +41.38 | `03_stamp_vertical_90deg` +17.40 | `04_chars_missing` (9/10) |
| Forms/records | 14 | 1 | 3 | 4 | 6 | +45.77 | `form16-part-b` +14.13 | `18_displacement` (10/14) |
| Typography/page | 11 | 4 | 2 | 2 | 3 | +30.68 | `35_four_typefaces_one_page` +6.91 | `18_displacement` (6/11) |
| Menu/diagram | 2 | 0 | 0 | 0 | 2 | +18.67 | `360_restaurant_menu` +15.75 | `18_displacement` (2/2) |
| **total** | **84** | **10** | **19** | **15** | **40** | **+547.79** | — | `18_displacement` (59/84) |

What each group is, by name:

* **Ruled tables (26)** — `table-*`, `*-table`, `boq-*`, `*_boq`, `balance-sheet-*`, `74_balance_sheet_*`, `marksheet-*`,
  `*_marksheet_*`, `timetable`, `*_grid`, `*_timesheet_*`, `attendance_register`, `*_datasheet_*`, `*_appendix`,
  `*_bom_on_drawing`, `crossword_puzzle`, `sudoku_grid`, `79_inr_*_table`, `80_gstin_*_table`, `gst-invoice-multipage-item-table`.
  This is the heaviest group on every measure: 26 documents, 13 failing 3+ checks, and +247.04 of the +547.79 delta.
* **Invoices, bills & right-aligned amount columns (21)** — `*invoice*`, `*-bill`, `price-list-*`, `payslip-*`, `salary-slip-*`,
  `*statement*`, `property-tax-receipt`, `purchase-order`, `eway-bill`, `326_itr_computation`, `question-paper-marks-right-margin`,
  `16_right_aligned_amounts_txtpos`, `362_price_list_dense`.
* **Stamps & seals (10)** — every document with `stamp` in the name that is worse than baseline: rotated 15° upright and
  up-left, vertical 90°, 180° upside-down, rectangular red-transparent, over-table, two overlapping, image, non-English,
  chars-positioned-via-`Td`. Nine of the ten fail 3+ checks, and the failed checks are almost invariant across the group
  (`04_chars_missing` 9, `13_text_colours` 9, `35_rotation` 8, `18_displacement` 7).
* **Forms, declarations & record cards (14)** — `form16-part-b`, `311_fir_police_form`, `344_customs_declaration`,
  `370_offer_letter`, `363_warranty_card`, `364_event_ticket`, `365_recipe_card`, `300_prescription_rx`,
  `302_radiology_report`, `306_clinical_protocol_synopsis`, `383_api_docs_page`, `406_passport_mrz_page`,
  `351_omr_answer_sheet`, `insurance-policy-schedule`.
* **Typography, page-shape & positioning (11)** — `25_signature_block_underscores_txtpos`, `29_dot_leaders_txtpos`,
  `30_mixed_font_sizes_one_baseline_txtpos`, `33_sans_nondefault_body`, `35_four_typefaces_one_page`,
  `36_embedded_subset_font`, `38_faux_bold_italic_synthesised`, `40_devanagari_shaping_font`,
  `41_coloured_headings_white_bg`, `52_one_cm_margin_wide_body`, `59_landscape_mixed_portrait`. This is the *cleanest*
  group: 4 of 11 pass every Google check.
* **Menus & diagram layouts (2)** — `360_restaurant_menu`, `374_org_chart`.

## The full 84, ranked by delta against the 15 Nov floor

`baseline` and `current` are `share5` from `benchmarks/RANKING-BASELINE.csv` and `benchmarks/RANKING.csv`; `delta` is
current minus baseline; `G` is `len(failed)` from `benchmarks/gverify/<document>.json`, followed by the failing check
names. A dash in the checks column means `failed` was empty.

| # | document | group | baseline | current | delta | G | failing checks (gverify) |
|--:|:--|:--|--:|--:|--:|--:|:--|
| 1 | `table-with-no-header-row` | Ruled tables | 0.61 | 47.48 | +46.87 | 1 | `18_displacement` |
| 2 | `boq-tender-bill-of-quantities` | Ruled tables | 7.10 | 41.95 | +34.85 | 2 | `18_displacement`, `60_text_column_right_edge` |
| 3 | `very-long-single-column-table` | Ruled tables | 6.87 | 41.14 | +34.27 | 5 | `04_chars_missing`, `18_displacement`, `27_text_off_page`, `44_header_footer`, `60_text_column_right_edge` |
| 4 | `balance-sheet-and-profit-loss` | Ruled tables | 6.20 | 36.69 | +30.49 | 3 | `18_displacement`, `27_text_off_page`, `60_text_column_right_edge` |
| 5 | `price-list-2col-dense-right-aligned` | Invoices/amounts | 2.69 | 27.89 | +25.20 | 1 | `18_displacement` |
| 6 | `table-across-page-break-repeated-header` | Ruled tables | 9.41 | 33.52 | +24.11 | 5 | `04_chars_missing`, `18_displacement`, `27_text_off_page`, `44_header_footer`, `60_text_column_right_edge` |
| 7 | `electricity-bill` | Invoices/amounts | 16.24 | 36.78 | +20.54 | 0 | — |
| 8 | `03_stamp_vertical_90deg` | Stamps | 16.98 | 34.38 | +17.40 | 6 | `04_chars_missing`, `13_text_colours`, `18_displacement`, `35_rotation`, `62_table_columns`, `63_table_rows` |
| 9 | `salary-slip-factory-wages` | Invoices/amounts | 18.09 | 35.15 | +17.06 | 1 | `60_text_column_right_edge` |
| 10 | `property-tax-receipt` | Invoices/amounts | 10.78 | 27.45 | +16.67 | 3 | `04_chars_missing`, `13_text_colours`, `18_displacement` |
| 11 | `360_restaurant_menu` | Menu/diagram | 34.43 | 50.18 | +15.75 | 4 | `18_displacement`, `43_within_10pt_x`, `47_margins`, `60_text_column_right_edge` |
| 12 | `mutual-fund-statement` | Invoices/amounts | 12.05 | 27.80 | +15.75 | 5 | `18_displacement`, `25_invisible_text`, `27_text_off_page`, `60_text_column_right_edge`, `66_table_cell_width` |
| 13 | `form16-part-b` | Forms/records | 12.32 | 26.45 | +14.13 | 4 | `04_chars_missing`, `18_displacement`, `27_text_off_page`, `60_text_column_right_edge` |
| 14 | `mobile-bill` | Invoices/amounts | 18.48 | 30.09 | +11.61 | 0 | — |
| 15 | `bus-timetable-station-left-times-right` | Ruled tables | 0.27 | 11.40 | +11.13 | 1 | `18_displacement` |
| 16 | `bank-statement-5-pages` | Invoices/amounts | 3.09 | 14.14 | +11.05 | 5 | `18_displacement`, `25_invisible_text`, `27_text_off_page`, `44_header_footer`, `59_shape_anchor` |
| 17 | `price-list-right-aligned-amounts` | Invoices/amounts | 1.79 | 12.37 | +10.58 | 3 | `17_matched_runs`, `18_displacement`, `53_embedded_faces` |
| 18 | `marksheet-university-consolidated` | Ruled tables | 16.78 | 27.14 | +10.36 | 2 | `18_displacement`, `60_text_column_right_edge` |
| 19 | `insurance-policy-schedule` | Forms/records | 13.29 | 22.66 | +9.37 | 0 | — |
| 20 | `purchase-order` | Invoices/amounts | 5.30 | 14.34 | +9.04 | 2 | `26_text_overlap`, `60_text_column_right_edge` |
| 21 | `73_marksheet_subject_marks_grade` | Ruled tables | 0.00 | 7.95 | +7.95 | 0 | — |
| 22 | `invoice-line-items-qty-rate-amount` | Invoices/amounts | 4.90 | 12.06 | +7.16 | 1 | `26_text_overlap` |
| 23 | `79_inr_indian_digit_grouping_table` | Ruled tables | 0.74 | 7.77 | +7.03 | 2 | `59_shape_anchor`, `60_text_column_right_edge` |
| 24 | `35_four_typefaces_one_page` | Typography/page | 2.19 | 9.10 | +6.91 | 1 | `18_displacement` |
| 25 | `06_rect_paid_stamp_red_transparent` | Stamps | 0.00 | 6.90 | +6.90 | 3 | `04_chars_missing`, `13_text_colours`, `35_rotation` |
| 26 | `33_sans_nondefault_body` | Typography/page | 4.49 | 10.73 | +6.24 | 0 | — |
| 27 | `311_fir_police_form` | Forms/records | 0.00 | 5.59 | +5.59 | 4 | `04_chars_missing`, `18_displacement`, `45_char_accuracy`, `60_text_column_right_edge` |
| 28 | `36_embedded_subset_font` | Typography/page | 0.00 | 4.91 | +4.91 | 0 | — |
| 29 | `payslip-label-left-amount-right` | Invoices/amounts | 5.59 | 10.47 | +4.88 | 4 | `17_matched_runs`, `18_displacement`, `46_text_crossing_rule`, `53_embedded_faces` |
| 30 | `74_balance_sheet_indented_subitems` | Ruled tables | 0.03 | 4.80 | +4.77 | 1 | `18_displacement` |
| 31 | `two-tables-stacked-with-no-gap` | Ruled tables | 17.20 | 21.93 | +4.73 | 1 | `18_displacement` |
| 32 | `10_stamp_as_image` | Stamps | 0.00 | 4.68 | +4.68 | 1 | `18_displacement` |
| 33 | `80_gstin_pan_cin_ifsc_table` | Ruled tables | 2.01 | 6.45 | +4.44 | 7 | `04_chars_missing`, `17_matched_runs`, `18_displacement`, `23_line_pitch`, `44_header_footer`, `45_char_accuracy`, `59_shape_anchor` |
| 34 | `370_offer_letter` | Forms/records | 3.47 | 7.63 | +4.16 | 1 | `60_text_column_right_edge` |
| 35 | `56_table_indented_from_margin` | Ruled tables | 0.00 | 4.13 | +4.13 | 3 | `18_displacement`, `59_shape_anchor`, `60_text_column_right_edge` |
| 36 | `16_right_aligned_amounts_txtpos` | Invoices/amounts | 0.00 | 3.83 | +3.83 | 0 | — |
| 37 | `02_stamp_rotated_15deg_upleft` | Stamps | 0.00 | 3.68 | +3.68 | 5 | `04_chars_missing`, `13_text_colours`, `18_displacement`, `35_rotation`, `59_shape_anchor` |
| 38 | `22_invoice_four_columns_txtpos` | Invoices/amounts | 0.00 | 3.49 | +3.49 | 2 | `18_displacement`, `46_text_crossing_rule` |
| 39 | `59_landscape_mixed_portrait` | Typography/page | 0.00 | 3.47 | +3.47 | 2 | `18_displacement`, `59_shape_anchor` |
| 40 | `404_sudoku_grid` | Ruled tables | 0.27 | 3.63 | +3.36 | 4 | `18_displacement`, `23_line_pitch`, `47_margins`, `59_shape_anchor` |
| 41 | `406_passport_mrz_page` | Forms/records | 3.45 | 6.79 | +3.34 | 4 | `18_displacement`, `26_text_overlap`, `59_shape_anchor`, `60_text_column_right_edge` |
| 42 | `390_wide_data_appendix` | Ruled tables | 0.03 | 3.23 | +3.20 | 3 | `47_margins`, `59_shape_anchor`, `66_table_cell_width` |
| 43 | `eway-bill` | Invoices/amounts | 0.91 | 4.08 | +3.17 | 1 | `18_displacement` |
| 44 | `table-with-rotated-header` | Ruled tables | 6.42 | 9.56 | +3.14 | 4 | `04_chars_missing`, `45_char_accuracy`, `47_margins`, `59_shape_anchor` |
| 45 | `13_stamp_non_english` | Stamps | 0.01 | 3.00 | +2.99 | 7 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `18_displacement`, `35_rotation`, `45_char_accuracy`, `59_shape_anchor` |
| 46 | `374_org_chart` | Menu/diagram | 5.92 | 8.84 | +2.92 | 3 | `18_displacement`, `26_text_overlap`, `59_shape_anchor` |
| 47 | `332_bom_on_drawing` | Ruled tables | 0.00 | 2.83 | +2.83 | 5 | `18_displacement`, `26_text_overlap`, `47_margins`, `59_shape_anchor`, `60_text_column_right_edge` |
| 48 | `363_warranty_card` | Forms/records | 10.58 | 13.29 | +2.71 | 2 | `18_displacement`, `60_text_column_right_edge` |
| 49 | `42_table_coloured_header_alternating_rows` | Ruled tables | 0.00 | 2.39 | +2.39 | 2 | `18_displacement`, `59_shape_anchor` |
| 50 | `41_coloured_headings_white_bg` | Typography/page | 0.00 | 2.16 | +2.16 | 0 | — |
| 51 | `30_mixed_font_sizes_one_baseline_txtpos` | Typography/page | 0.00 | 1.90 | +1.90 | 1 | `18_displacement` |
| 52 | `38_faux_bold_italic_synthesised` | Typography/page | 0.01 | 1.86 | +1.85 | 3 | `04_chars_missing`, `46_text_crossing_rule`, `60_text_column_right_edge` |
| 53 | `314_tender_rfp_boq` | Ruled tables | 0.00 | 1.59 | +1.59 | 3 | `42_justification_edges`, `60_text_column_right_edge`, `63_table_rows` |
| 54 | `52_one_cm_margin_wide_body` | Typography/page | 0.00 | 1.59 | +1.59 | 2 | `18_displacement`, `59_shape_anchor` |
| 55 | `72_bank_statement_no_rules_right_amounts` | Invoices/amounts | 0.00 | 1.57 | +1.57 | 1 | `18_displacement` |
| 56 | `14_stamp_chars_positioned_td` | Stamps | 3.89 | 5.45 | +1.56 | 6 | `04_chars_missing`, `13_text_colours`, `18_displacement`, `45_char_accuracy`, `59_shape_anchor`, `60_text_column_right_edge` |
| 57 | `364_event_ticket` | Forms/records | 0.25 | 1.64 | +1.39 | 4 | `04_chars_missing`, `18_displacement`, `45_char_accuracy`, `59_shape_anchor` |
| 58 | `302_radiology_report` | Forms/records | 0.00 | 1.36 | +1.36 | 1 | `60_text_column_right_edge` |
| 59 | `365_recipe_card` | Forms/records | 0.02 | 1.30 | +1.28 | 2 | `47_margins`, `60_text_column_right_edge` |
| 60 | `01_stamp_rotated_15deg_upright` | Stamps | 0.00 | 1.27 | +1.27 | 3 | `04_chars_missing`, `13_text_colours`, `35_rotation` |
| 61 | `333_datasheet_spec_tables` | Ruled tables | 0.07 | 1.23 | +1.16 | 3 | `18_displacement`, `59_shape_anchor`, `66_table_cell_width` |
| 62 | `gst-invoice-multipage-item-table` | Ruled tables | 10.44 | 11.56 | +1.12 | 5 | `18_displacement`, `25_invisible_text`, `26_text_overlap`, `27_text_off_page`, `44_header_footer` |
| 63 | `306_clinical_protocol_synopsis` | Forms/records | 0.00 | 1.11 | +1.11 | 1 | `18_displacement` |
| 64 | `375_attendance_register` | Ruled tables | 0.01 | 1.07 | +1.06 | 4 | `18_displacement`, `43_within_10pt_x`, `47_margins`, `59_shape_anchor` |
| 65 | `balance-sheet-two-columns-of-figures` | Ruled tables | 0.57 | 1.61 | +1.04 | 1 | `18_displacement` |
| 66 | `08_two_overlapping_stamps` | Stamps | 0.11 | 1.12 | +1.01 | 6 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `35_rotation`, `45_char_accuracy`, `59_shape_anchor` |
| 67 | `04_stamp_180deg_upside_down` | Stamps | 0.00 | 0.96 | +0.96 | 5 | `04_chars_missing`, `13_text_colours`, `18_displacement`, `35_rotation`, `59_shape_anchor` |
| 68 | `07_stamp_over_table` | Stamps | 1.82 | 2.75 | +0.93 | 8 | `04_chars_missing`, `13_text_colours`, `18_displacement`, `26_text_overlap`, `35_rotation`, `43_within_10pt_x`, `47_margins`, `59_shape_anchor` |
| 69 | `29_dot_leaders_txtpos` | Typography/page | 0.00 | 0.89 | +0.89 | 0 | — |
| 70 | `362_price_list_dense` | Invoices/amounts | 0.03 | 0.82 | +0.79 | 0 | — |
| 71 | `40_devanagari_shaping_font` | Typography/page | 10.48 | 11.23 | +0.75 | 4 | `18_displacement`, `34a_span_size_match`, `38_list_markers`, `47_margins` |
| 72 | `50_invoice_coloured_total_row` | Invoices/amounts | 0.00 | 0.75 | +0.75 | 1 | `59_shape_anchor` |
| 73 | `326_itr_computation` | Invoices/amounts | 0.63 | 1.36 | +0.73 | 4 | `18_displacement`, `59_shape_anchor`, `60_text_column_right_edge`, `63_table_rows` |
| 74 | `383_api_docs_page` | Forms/records | 0.30 | 0.80 | +0.50 | 6 | `04_chars_missing`, `18_displacement`, `47_margins`, `59_shape_anchor`, `60_text_column_right_edge`, `66_table_cell_width` |
| 75 | `300_prescription_rx` | Forms/records | 0.06 | 0.51 | +0.45 | 2 | `18_displacement`, `59_shape_anchor` |
| 76 | `23_timetable_grid_txtpos` | Ruled tables | 5.16 | 5.58 | +0.42 | 2 | `18_displacement`, `59_shape_anchor` |
| 77 | `403_crossword_puzzle` | Ruled tables | 0.00 | 0.38 | +0.38 | 1 | `18_displacement` |
| 78 | `344_customs_declaration` | Forms/records | 0.61 | 0.98 | +0.37 | 4 | `04_chars_missing`, `13_text_colours`, `18_displacement`, `60_text_column_right_edge` |
| 79 | `372_timesheet_grid` | Ruled tables | 0.00 | 0.22 | +0.22 | 2 | `18_displacement`, `59_shape_anchor` |
| 80 | `question-paper-marks-right-margin` | Invoices/amounts | 0.44 | 0.62 | +0.18 | 2 | `18_displacement`, `60_text_column_right_edge` |
| 81 | `71_invoice_space_aligned_no_rules` | Invoices/amounts | 26.88 | 26.99 | +0.11 | 1 | `18_displacement` |
| 82 | `323_credit_card_statement` | Invoices/amounts | 0.00 | 0.09 | +0.09 | 7 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `18_displacement`, `45_char_accuracy`, `60_text_column_right_edge`, `66_table_cell_width` |
| 83 | `25_signature_block_underscores_txtpos` | Typography/page | 0.03 | 0.04 | +0.01 | 4 | `04_chars_missing`, `18_displacement`, `45_char_accuracy`, `60_text_column_right_edge` |
| 84 | `351_omr_answer_sheet` | Forms/records | 0.00 | 0.01 | +0.01 | 2 | `18_displacement`, `59_shape_anchor` |

## The biggest lever

Counted over the 74 documents that fail at least one check, the failing checks are:

| check | documents failing it (of 84) | documents failing it (of the 74 that fail anything) |
|:--|--:|--:|
| `18_displacement` | 59 | 80% |
| `59_shape_anchor` | 29 | 39% |
| `60_text_column_right_edge` | 28 | 38% |
| `04_chars_missing` | 22 | 30% |
| `13_text_colours` | 12 | 16% |
| `47_margins` | 10 | 14% |
| `45_char_accuracy` | 9 | 12% |
| `35_rotation` | 8 | 11% |
| `27_text_off_page` | 7 | 9% |
| `26_text_overlap` | 7 | 9% |

**The biggest lever is `18_displacement`.** It fails in **59 of the 84** documents — more than the next two checks
combined (`59_shape_anchor` 29, `60_text_column_right_edge` 28) — and it
is the *only* failing check in 14 of them. Those 14 include the largest delta in the corpus, `table-with-no-header-row`
(+46.87, fails nothing but 18), plus `price-list-2col-dense-right-aligned` (+25.20) and
`bus-timetable-station-left-times-right` (+11.13); it is also one of the failures in the next two by size,
`boq-tender-bill-of-quantities` (+34.85) and `balance-sheet-and-profit-loss` (+30.49). It is present in every group's
failure profile, so no group-specific fix removes it.

`benchmarks/RANKING.csv` agrees from the other side: of the 84, **63 carry signature `displacement`** and 36 carry
problem `content-present-wholly-displaced`, 23 `content-present-partly-displaced` — i.e. 59 of 84 are documents whose
content is *present* and merely in the wrong place. Nothing is missing; it is displaced. That is one construct.

The largest lever *by mass* is a subset of the same lever: the **26 ruled-table documents** hold +247.04 of the
+547.79 total delta (45%), and `18_displacement` fails in 21 of those 26. The stamp group is the most uniformly
broken (9 of 10 fail 3+ checks, with `04_chars_missing` + `13_text_colours` + `35_rotation` as a near-fixed triple),
but it is worth only +41.38 of delta — fixing stamps to perfection would still leave the gate refusing.

So: **one lever, `18_displacement`, worth up to 59 of the 84 documents; a second, smaller and genuinely separate
lever in the stamp cluster (10 documents, one construct, `04`/`13`/`35`); and a residual of 10 documents that no
Google-check fix touches at all** because they already pass everything and moved only on `share5` against the
15 Nov engine.

## What would prove this wrong

Each claim above is falsifiable from the same three files, in minutes:

1. **The population is 84.** Re-run the strict comparison of `share5` between the two CSVs. If it returns a number
   other than 84, or a document set that differs from the table above by even one row, the classification is void.
   A check on the definition: `tools/p2w-bench/regress.py` must print 84, and `benchmarks/gate.py --ratchet-only`
   must print 73 (its 0.5 deadband drops 11 rows). If `regress.py` prints 73, the strict comparison above is not the
   gate's comparison and this file is classifying the wrong population.
2. **The 10 pass-all documents really pass.** For any of the 10, show a `benchmarks/gverify/<doc>.json` with a
   non-empty `failed` list, or show that its `status` is not `ok`, and class (a) shrinks. Conversely, if any of the
   74 has an empty `failed` list in a gverify file newer than the ones in this clone, class (b) shrinks. The gverify
   files here are stamped (`at` field, 2026-11-27) and are measurements of a specific engine — a re-measure on a
   different engine is a different fact, not a contradiction.
3. **`18_displacement` is the lever, not merely the most common symptom.** Show that documents failing `18` and
   nothing else can be brought back under their baseline `share5` **without** changing displacement — e.g. by
   changing something else that the 5px metric responds to. `table-with-no-header-row` (+46.87, `18` only) is the
   clean test case: if a non-displacement change closes its 46.87-point gap, this section is wrong. The
   `ROW_RUNG_UNDER_TW = 0` measurement quoted in
   `FINDINGS/GATE-84-REGRESSIONS-ARE-FIVE-CONSTRUCTS-AND-THE-RUNG-WAS-JUDGED-AGAINST-THE-WRONG-TABLE-28NOV-relay.md`
   is the strongest existing evidence *for* the lever — that note claims the rung change alone removes 28 of the 84 —
   but the rung=0 `share5` table is **not** in this clone (`benchmarks/RANKING-25NOV.csv` is a gverify failure table,
   `document,n_failed,total,failed,engine`, not a ranking), so that 28 could not be re-derived here and is taken on the
   strength of the note, not verified. Re-deriving it from a rung=0 ranking is the cheapest way to strengthen or break
   this section.
4. **The groups are a partition and are assigned honestly.** The group assignment is name-based because the corpus
   content is not in the clone. If any of the 84 has content that contradicts its name — a "table" that is a
   letter, an "invoice" that is a table — the per-group counts move. Anyone with the built corpus can check all 84
   in an afternoon; nothing in this file depends on the grouping except the group table, the delta mass per group,
   and the ordering of the two levers.
5. **The delta mass figures.** The sums (+547.79 total, +68.29 for the 10, +247.04 tables, +41.38 stamps) are plain
   arithmetic on the `share5` columns. Recompute them; a different total means the join picked up the wrong rows.

## How this was derived

No file under `benchmarks/` or `app/` was modified; the clone is untouched. The steps, in order:

```
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS
cd benchmarks && python3  # then, per document name:
  cur  = {r['document']: float(r['share5']) for r in csv.DictReader(open('RANKING.csv'))}
  base = {r['document']: float(r['share5']) for r in csv.DictReader(open('RANKING-BASELINE.csv'))}
  worse = [d for d in cur if d in base and cur[d] > base[d]]          # -> 84
  g = json.load(open(f'gverify/{d}.json')); fails = len(g['failed'])    # skip if g['status']=='page_count_refused'
```

The group patterns, applied in this order (first match wins, case-insensitive, to the document name):

```
stamps  stamp|seal
tables  table|grid|boq|timetable|marksheet|datasheet|appendix|balance.sheet|crossword|sudoku|bom|attendance|timesheet|register
money   invoice|bill|receipt|payslip|salary|purchase.order|price.list|credit.card|statement|eway|gst|itr|computation|amounts|inr|tax|question.paper.marks
forms   form|fir|declaration|offer_letter|warranty|ticket|prescription|radiology|clinical|protocol|api_docs|recipe|041122|insurance|mrz|omr
type    font|typeface|devanagari|dot_leaders|margin|headings|mixed_font|faux|landscape|shaping|signature|sans|columns?_txtpos|space_aligned|right_aligned
other   everything left over  ->  360_restaurant_menu, 374_org_chart
```

Each CSV carries 213 distinct document names, and they are not the same 213. `416_many_tiny_pages` exists only in
`RANKING-BASELINE.csv`, as a `MEASURE-ERROR / unmeasured` row with an empty `share5`; `Prakashan_Print_Fidelity_Handbook`
exists only in `RANKING.csv`. Neither is in the 84, and neither affects any number above. `416_many_tiny_pages` does
have a gverify record, and it is the one gverify file with no counterpart row in `RANKING.csv`. `share5` is the metric
named in `gate.py` as the ratchet's basis (`read_rank()` reads exactly that column); the definition of the 5px
threshold itself is not stated in these three files.
