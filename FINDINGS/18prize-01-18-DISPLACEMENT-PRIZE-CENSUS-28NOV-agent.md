# `18_displacement` — the prize census: 46.56 clean documents, of which 18 are solo, and the one rule that can claim the largest part

**28 Nov 2026 · census run · repo `kavopdf/app` @ HEAD · no Java build, no corpus conversion, no Drive,
no network · every number below is computed from the committed `benchmarks/gverify/*.json` (214 files,
213 scored) and `benchmarks/DISP-TABLE.csv`, with `tools/p2w-bench/verify_google.py` read for the
check's own predicate and `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` read for the
constructs.**

Sources read: `benchmarks/gverify/*.json` (all 214), `benchmarks/DISP-TABLE.csv`,
`benchmarks/DEFECT-CLASSES-GOOGLE.md`, `tools/p2w-bench/classpick.py`, `verify_google.py`,
`DocxWriter.java`, `FINDINGS/18-displacement-*.md` (all 14), `FINDINGS/18dA-03-*.md`, `FINDINGS/18DISPLACEMENT-COUNT-0125-27NOV.md`,
`FINDINGS/18displacement-25-classification-27NOV.csv`, `FINDINGS/ROW-RUNG-IS-A-PER-DOCUMENT-TRADE-NOT-ONE-CONSTANT-28NOV.md`,
`FINDINGS/TABLE-GAP-IS-BEFORE-RUNG-IS-10-27NOV-fixer.md`, `FINDINGS/18-displacement-BASELINE-IN-BOX-MEASURED-IN-GOOGLE-27NOV-fixer.md`,
`tools/p2w-bench/FINDINGS/DOCS-ROOT-CAUSES-24NOV.md`.

---

## 0. The prize, stated the way `classpick.py --leverage` states it

The leverage rule (`classpick.py:214-270`): a document with `k` failing checks is worth `1/k` of a clean
document to each of its `k` checks. Computed here over the 206 `ok` rows plus the 8 `page_count_refused`
rows:

| check | worth, in clean documents |
|:--|--:|
| **`18_displacement`** | **46.56** |
| `60_text_column_right_edge` | 23.63 |
| `59_shape_anchor` | 15.64 |
| `04_chars_missing` | 11.21 |
| `47_margins` | 8.92 |

`46.56` is the "46.6 clean documents" in the leverage table — reproduced exactly, so the table's
arithmetic is sound on this row. Its decomposition is the whole point of this file:

    46.56 = 18.00 from the 18 documents that fail 18_displacement and NOTHING else
          + 28.56 from the 90 documents that fail it alongside something else

**108 documents fail `18_displacement` today** (engine `a05b20eb05fe0fc8`, all 213 scored rows, one
store, 27 Nov 12:12–22:35). 18 are solo; 90 are blocked. The class table in
`benchmarks/DEFECT-CLASSES-GOOGLE.md` says 108 and agrees.

---

## 1. Every document that fails `18_displacement`, classified

Checks offered per document are 42, 44 or 47 (not a fixed 42 — the catalogue grew), so "passed/total"
is the only comparable completeness figure. `med_dy` is signed and is the check's own number:
`dy = render baseline − source baseline` in reading space (`verify_google.py:5874`, `roy`), so
**positive = the built line sits LOWER on the page than the source drew it**, negative = higher.
`worst_dy` is `max|dy|` over the page's matched upright runs. `bad_pages` are 0-based.
"Other failures" is the COMPLETE remaining failure list for that document.

| `very-long-single-column-table` | 42/47 | -3.0 | 650.5 | 0,1,2 | 511 | higher | blocked | 04_chars_missing, 27_text_off_page, 44_header_footer, 60_text_column_right_edge |
| `table-across-page-break-repeated-header` | 42/47 | -38.4 | 399.6 | 1,2 | 466 | higher | blocked | 04_chars_missing, 27_text_off_page, 44_header_footer, 60_text_column_right_edge |
| `bank-statement-5-pages` | 42/47 | -54.1 | 350.0 | 5 pages (0,1,2,3,...) | 585 | higher | blocked | 25_invisible_text, 27_text_off_page, 44_header_footer, 59_shape_anchor |
| `324_loan_amortisation_schedule` | 44/47 | -2.7 | 275.2 | 7 pages (0,1,2,3,...) | 1496 | higher | blocked | 27_text_off_page, 59_shape_anchor |
| `601_fillable_admission_form` | 37/42 | +25.9 | 238.3 | 0 | 21 | lower | blocked | 04_chars_missing, 51_field_values, 53_embedded_faces, 59_shape_anchor |
| `one-page-rotated-180-degrees` | 40/47 | -1.1 | 201.2 | 1 | 121 | higher | blocked | 04_chars_missing, 27_text_off_page, 43_within_10pt_x, 60_text_column_right_edge, 62_table_columns, 63_table_rows |
| `gst-invoice-multipage-item-table` | 42/47 | -52.2 | 164.6 | 1,2,3 | 373 | higher | blocked | 25_invisible_text, 26_text_overlap, 27_text_off_page, 44_header_footer |
| `balance-sheet-and-profit-loss` | 44/47 | -15.9 | 160.0 | 0,1 | 172 | higher | blocked | 27_text_off_page, 60_text_column_right_edge |
| `form16-part-b` | 43/47 | -0.7 | 160.0 | 1 | 113 | higher | blocked | 04_chars_missing, 27_text_off_page, 60_text_column_right_edge |
| `602_bookmarked_annual_report` | 38/42 | -69.2 | 144.1 | 1,2 | 24 | higher | blocked | 04_chars_missing, 27_text_off_page, 52_outline |
| `600_reviewed_invoice_with_annotations` | 37/44 | +100.5 | 124.0 | 0 | 56 | lower | blocked | 05_chars_extra, 28_clipped_at_edge, 32_stroke_lines, 45_char_accuracy, 47_margins, 62_table_columns |
| `mutual-fund-statement` | 42/47 | +0.2 | 123.0 | 0,1 | 256 | lower | blocked | 25_invisible_text, 27_text_off_page, 60_text_column_right_edge, 66_table_cell_width |
| `bank-statement-horizontal-rules-only` | 40/42 | +9.3 | 107.3 | 0 | 197 | lower | blocked | 45_char_accuracy |
| `416_many_tiny_pages` | 40/42 | -89.0 | 89.1 | 299 pages (1,2,3,4,...) | 900 | higher | blocked | 27_text_off_page |
| `330_cad_drawing_sheet` | 43/47 | -30.9 | 82.6 | 0 | 38 | higher | blocked | 04_chars_missing, 45_char_accuracy, 47_margins |
| `57_centred_title_page_left_body_pages` | 39/42 | -34.0 | 69.4 | 1 | 30 | higher | blocked | 27_text_off_page, 44_header_footer |
| `table-inside-two-column-page` | 46/47 | +8.0 | 69.2 | 0 | 64 | lower | **SOLO** | — |
| `412_page_labels_roman` | 40/42 | -61.0 | 61.1 | 1,2,3,4 | 15 | higher | blocked | 27_text_off_page |
| `417_rotate180_and_mirrored` | 38/42 | +0.3 | 60.9 | 1 | 7 | lower | blocked | 04_chars_missing, 17_matched_runs, 27_text_off_page |
| `academic-paper-ieee-2col-abstract` | 39/47 | -58.4 | 60.0 | 1 | 81 | higher | blocked | 04_chars_missing, 17_matched_runs, 27_text_off_page, 44_header_footer, 45_char_accuracy, 47_margins, 60_text_column_right_edge |
| `64_newspaper_uneven_columns_ad_boxes` | 39/42 | -23.7 | 58.6 | 0 | 77 | higher | blocked | 23_line_pitch, 26_text_overlap |
| `58_header_rule_footer_rule` | 38/42 | +0.1 | 47.2 | 1 | 19 | lower | blocked | 04_chars_missing, 27_text_off_page, 44_header_footer |
| `360_restaurant_menu` | 38/42 | -6.4 | 37.1 | 0 | 66 | higher | blocked | 43_within_10pt_x, 47_margins, 60_text_column_right_edge |
| `68_journal_wide_table_spanning` | 40/42 | -32.6 | 35.5 | 0 | 74 | higher | blocked | 59_shape_anchor |
| `77_arabic_rtl_document` | 40/47 | +11.1 | 34.3 | 0 | 22 | lower | blocked | 17_matched_runs, 26_text_overlap, 43_within_10pt_x, 47_margins, 59_shape_anchor, 60_text_column_right_edge |
| `newsletter-3col-header-footer` | 39/42 | +1.2 | 26.5 | 0 | 128 | lower | blocked | 26_text_overlap, 59_shape_anchor |
| `71_invoice_space_aligned_no_rules` | 41/42 | +2.9 | 26.3 | 0 | 72 | lower | **SOLO** | — |
| `80_gstin_pan_cin_ifsc_table` | 35/42 | -12.3 | 24.6 | 0 | 62 | higher | blocked | 04_chars_missing, 17_matched_runs, 23_line_pitch, 44_header_footer, 45_char_accuracy, 59_shape_anchor |
| `341_shipping_manifest` | 45/47 | +2.4 | 21.4 | 0 | 304 | lower | blocked | 60_text_column_right_edge |
| `320_balance_sheet_statutory` | 46/47 | +7.2 | 16.2 | 0 | 73 | lower | **SOLO** | — |
| `322_mutual_fund_factsheet` | 39/47 | +3.9 | 16.1 | 0 | 77 | lower | blocked | 04_chars_missing, 13_text_colours, 17_matched_runs, 26_text_overlap, 44_header_footer, 45_char_accuracy, 60_text_column_right_edge |
| `323_credit_card_statement` | 40/47 | +4.4 | 15.8 | 0 | 71 | lower | blocked | 04_chars_missing, 13_text_colours, 17_matched_runs, 45_char_accuracy, 60_text_column_right_edge, 66_table_cell_width |
| `25_signature_block_underscores_txtpos` | 38/42 | -1.3 | 15.0 | 0 | 37 | higher | blocked | 04_chars_missing, 45_char_accuracy, 60_text_column_right_edge |
| `13_stamp_non_english` | 35/42 | -12.5 | 13.6 | 0 | 25 | higher | blocked | 04_chars_missing, 13_text_colours, 17_matched_runs, 35_rotation, 45_char_accuracy, 59_shape_anchor |
| `373_leave_application_form` | 43/47 | -8.4 | 11.3 | 0 | 32 | higher | blocked | 23_line_pitch, 59_shape_anchor, 60_text_column_right_edge |
| `374_org_chart` | 39/42 | +0.1 | 11.0 | 0 | 21 | lower | blocked | 26_text_overlap, 59_shape_anchor |
| `403_crossword_puzzle` | 41/42 | -7.7 | 10.6 | 0 | 27 | higher | **SOLO** | — |
| `76_devanagari_table` | 43/47 | +5.9 | 10.2 | 0 | 56 | lower | blocked | 17_matched_runs, 34a_span_size_match, 47_margins |
| `56_table_indented_from_margin` | 39/42 | -7.0 | 9.9 | 0 | 51 | higher | blocked | 59_shape_anchor, 60_text_column_right_edge |
| `333_datasheet_spec_tables` | 44/47 | +4.9 | 9.6 | 0 | 122 | lower | blocked | 59_shape_anchor, 66_table_cell_width |
| `404_sudoku_grid` | 43/47 | -0.0 | 8.9 | 0 | 33 | level | blocked | 23_line_pitch, 47_margins, 59_shape_anchor |
| `406_passport_mrz_page` | 38/42 | -5.9 | 8.9 | 0 | 30 | higher | blocked | 26_text_overlap, 59_shape_anchor, 60_text_column_right_edge |
| `boq-horizontal-rules-only` | 40/42 | +4.4 | 8.9 | 0 | 152 | lower | blocked | 45_char_accuracy |
| `301_lab_report_panel` | 45/47 | +1.6 | 8.8 | 0 | 88 | lower | blocked | 60_text_column_right_edge |
| `price-list-2col-dense-right-aligned` | 41/42 | +5.8 | 8.8 | 0 | 253 | lower | **SOLO** | — |
| `price-list-right-aligned-amounts` | 39/42 | +4.3 | 8.1 | 0 | 163 | lower | blocked | 17_matched_runs, 53_embedded_faces |
| `381_incident_report_timeline` | 43/47 | +3.5 | 8.0 | 0 | 63 | lower | blocked | 04_chars_missing, 59_shape_anchor, 60_text_column_right_edge |
| `78_mixed_english_devanagari_line` | 36/42 | +4.2 | 8.0 | 0 | 38 | lower | blocked | 05_chars_extra, 17_matched_runs, 26_text_overlap, 43_within_10pt_x, 47_margins |
| `325_demat_holdings_statement` | 45/47 | +2.2 | 7.9 | 0 | 84 | lower | blocked | 59_shape_anchor |
| `75_merged_header_cell_three_columns` | 43/47 | +4.2 | 7.2 | 0 | 50 | lower | blocked | 59_shape_anchor, 64_table_span_across, 65_table_span_down |
| `gst-invoice-horizontal-rules-only` | 36/42 | +4.3 | 6.9 | 0 | 80 | lower | blocked | 04_chars_missing, 26_text_overlap, 44_header_footer, 45_char_accuracy, 60_text_column_right_edge |
| `326_itr_computation` | 43/47 | +3.9 | 6.7 | 0 | 73 | lower | blocked | 59_shape_anchor, 60_text_column_right_edge, 63_table_rows |
| `306_clinical_protocol_synopsis` | 46/47 | -0.4 | 6.6 | 0 | 75 | higher | **SOLO** | — |
| `332_bom_on_drawing` | 42/47 | -6.5 | 6.5 | 0 | 50 | higher | blocked | 26_text_overlap, 47_margins, 59_shape_anchor, 60_text_column_right_edge |
| `04_stamp_180deg_upside_down` | 37/42 | -4.4 | 6.3 | 0 | 48 | higher | blocked | 04_chars_missing, 13_text_colours, 35_rotation, 59_shape_anchor |
| `bus-timetable-station-left-times-right` | 41/42 | +4.2 | 5.9 | 0 | 177 | lower | **SOLO** | — |
| `405_sheet_music_lyrics` | 39/42 | +2.3 | 5.7 | 0 | 37 | lower | blocked | 45_char_accuracy, 46_text_crossing_rule |
| `340_bill_of_lading` | 40/42 | -4.2 | 5.6 | 0 | 50 | higher | blocked | 60_text_column_right_edge |
| `353_admit_card` | 42/47 | -3.5 | 5.6 | 0 | 44 | higher | blocked | 04_chars_missing, 26_text_overlap, 44_header_footer, 59_shape_anchor |
| `300_prescription_rx` | 45/47 | -4.4 | 5.4 | 0 | 49 | higher | blocked | 59_shape_anchor |
| `383_api_docs_page` | 41/47 | +2.3 | 5.4 | 0 | 56 | lower | blocked | 04_chars_missing, 47_margins, 59_shape_anchor, 60_text_column_right_edge, 66_table_cell_width |
| `22_invoice_four_columns_txtpos` | 40/42 | -1.1 | 5.2 | 0 | 71 | higher | blocked | 46_text_crossing_rule |
| `newspaper-2col-fullwidth-headline` | 38/42 | +4.6 | 5.1 | 0 | 61 | lower | blocked | 04_chars_missing, 26_text_overlap, 45_char_accuracy |
| `40_devanagari_shaping_font` | 43/47 | +0.8 | 5.0 | 0 | 57 | lower | blocked | 34a_span_size_match, 38_list_markers, 47_margins |
| `salary-slip-corporate` | 45/47 | +0.5 | 5.0 | 0 | 153 | lower | blocked | 53_embedded_faces |
| `23_timetable_grid_txtpos` | 45/47 | -3.1 | 4.9 | 0 | 66 | higher | blocked | 59_shape_anchor |
| `question-paper-marks-right-margin` | 40/42 | +2.6 | 4.9 | 0 | 65 | lower | blocked | 60_text_column_right_edge |
| `marksheet-subject-left-marks-right` | 44/47 | -3.2 | 4.8 | 0 | 109 | higher | blocked | 46_text_crossing_rule, 60_text_column_right_edge |
| `02_stamp_rotated_15deg_upleft` | 37/42 | -3.0 | 4.7 | 0 | 87 | higher | blocked | 04_chars_missing, 13_text_colours, 35_rotation, 59_shape_anchor |
| `311_fir_police_form` | 43/47 | -3.2 | 4.7 | 0 | 68 | higher | blocked | 04_chars_missing, 45_char_accuracy, 60_text_column_right_edge |
| `eway-bill` | 46/47 | -2.7 | 4.7 | 0 | 129 | higher | **SOLO** | — |
| `74_balance_sheet_indented_subitems` | 41/42 | +1.5 | 4.6 | 0 | 54 | lower | **SOLO** | — |
| `boq-tender-bill-of-quantities` | 45/47 | +0.8 | 4.5 | 0 | 157 | lower | blocked | 60_text_column_right_edge |
| `344_customs_declaration` | 43/47 | -3.8 | 4.4 | 0 | 63 | higher | blocked | 04_chars_missing, 13_text_colours, 60_text_column_right_edge |
| `07_stamp_over_table` | 34/42 | -4.0 | 4.3 | 0 | 77 | higher | blocked | 04_chars_missing, 13_text_colours, 26_text_overlap, 35_rotation, 43_within_10pt_x, 47_margins, 59_shape_anchor |
| `363_warranty_card` | 40/42 | -0.8 | 4.3 | 0 | 30 | higher | blocked | 60_text_column_right_edge |
| `14_stamp_chars_positioned_td` | 36/42 | -3.0 | 4.2 | 0 | 49 | higher | blocked | 04_chars_missing, 13_text_colours, 45_char_accuracy, 59_shape_anchor, 60_text_column_right_edge |
| `30_mixed_font_sizes_one_baseline_txtpos` | 41/42 | +2.3 | 4.2 | 0 | 38 | lower | **SOLO** | — |
| `59_landscape_mixed_portrait` | 40/42 | -1.3 | 4.2 | 1 | 55 | higher | blocked | 59_shape_anchor |
| `364_event_ticket` | 38/42 | -3.7 | 4.1 | 0 | 20 | higher | blocked | 04_chars_missing, 45_char_accuracy, 59_shape_anchor |
| `42_table_coloured_header_alternating_rows` | 40/42 | +2.1 | 4.1 | 0 | 61 | lower | blocked | 59_shape_anchor |
| `brochure-3col-with-sidebar-box` | 40/42 | +0.9 | 4.1 | 0 | 87 | lower | blocked | 59_shape_anchor |
| `375_attendance_register` | 43/47 | -0.2 | 4.0 | 0 | 459 | higher | blocked | 43_within_10pt_x, 47_margins, 59_shape_anchor |
| `balance-sheet-two-columns-of-figures` | 41/42 | -0.5 | 4.0 | 0 | 94 | higher | **SOLO** | — |
| `table-with-no-header-row` | 46/47 | +0.7 | 4.0 | 0 | 215 | lower | **SOLO** | — |
| `03_stamp_vertical_90deg` | 38/44 | -1.2 | 3.9 | 0 | 95 | higher | blocked | 04_chars_missing, 13_text_colours, 35_rotation, 62_table_columns, 63_table_rows |
| `351_omr_answer_sheet` | 40/42 | +1.2 | 3.8 | 0 | 66 | lower | blocked | 59_shape_anchor |
| `admit-card` | 43/47 | +1.7 | 3.8 | 0 | 70 | lower | blocked | 04_chars_missing, 13_text_colours, 45_char_accuracy |
| `372_timesheet_grid` | 45/47 | -2.9 | 3.6 | 0 | 68 | higher | blocked | 59_shape_anchor |
| `72_bank_statement_no_rules_right_amounts` | 41/42 | -1.0 | 3.5 | 0 | 80 | higher | **SOLO** | — |
| `52_one_cm_margin_wide_body` | 40/42 | +0.4 | 3.4 | 0 | 38 | lower | blocked | 59_shape_anchor |
| `35_four_typefaces_one_page` | 41/42 | -2.8 | 3.3 | 0 | 52 | higher | **SOLO** | — |
| `393_spectrum_peak_table` | 44/47 | -1.3 | 3.3 | 0 | 24 | higher | blocked | 59_shape_anchor, 60_text_column_right_edge |
| `343_air_waybill` | 40/42 | +0.5 | 3.2 | 0 | 38 | lower | blocked | 60_text_column_right_edge |
| `10_stamp_as_image` | 41/42 | -1.8 | 3.1 | 0 | 52 | higher | **SOLO** | — |
| `303_discharge_summary` | 46/47 | +0.9 | 3.1 | 0 | 45 | lower | **SOLO** | — |
| `335_msds_safety_data_sheet` | 45/47 | +0.5 | 3.1 | 0 | 47 | lower | blocked | 60_text_column_right_edge |
| `70_magazine_drop_cap_photo_caption` | 41/42 | +2.9 | 3.1 | 0 | 24 | lower | **SOLO** | — |
| `landscape-page-inside-portrait-document` | 45/47 | -1.6 | 3.1 | 1 | 124 | higher | blocked | 60_text_column_right_edge |
| `342_packing_list` | 45/47 | +0.4 | 3.0 | 0 | 51 | lower | blocked | 60_text_column_right_edge |
| `payslip-label-left-amount-right` | 38/42 | -0.4 | 3.0 | 0 | 93 | higher | blocked | 17_matched_runs, 46_text_crossing_rule, 53_embedded_faces |
| `gst-invoice-3line-items` | 45/47 | -1.9 | 2.9 | 0 | 106 | higher | blocked | 60_text_column_right_edge |
| `property-tax-receipt` | 44/47 | +0.1 | 2.9 | 0 | 104 | lower | blocked | 04_chars_missing, 13_text_colours |
| `two-tables-stacked-with-no-gap` | 46/47 | -1.2 | 2.9 | 0 | 72 | higher | **SOLO** | — |
| `delivery-challan` | 42/47 | +0.7 | 2.8 | 0 | 83 | lower | blocked | 04_chars_missing, 13_text_colours, 26_text_overlap, 60_text_column_right_edge |
| `journal-2col-with-footnotes` | 39/42 | +2.6 | 2.8 | 0 | 71 | lower | blocked | 26_text_overlap, 37_super_subscript |
| `318_court_summons_form` | 39/47 | -2.1 | 2.6 | 0 | 26 | higher | blocked | 04_chars_missing, 13_text_colours, 17_matched_runs, 43_within_10pt_x, 45_char_accuracy, 47_margins, 60_text_column_right_edge |
| `marksheet-university-consolidated` | 45/47 | -0.6 | 2.6 | 0 | 164 | higher | blocked | 60_text_column_right_edge |

**The 18 solo documents** (would be CLEAN the moment `18_displacement` passed — no other check is in
their way):

`table-inside-two-column-page`, `71_invoice_space_aligned_no_rules`, `320_balance_sheet_statutory`,
`403_crossword_puzzle`, `price-list-2col-dense-right-aligned`, `306_clinical_protocol_synopsis`,
`bus-timetable-station-left-times-right`, `eway-bill`, `74_balance_sheet_indented_subitems`,
`30_mixed_font_sizes_one_baseline_txtpos`, `balance-sheet-two-columns-of-figures`,
`table-with-no-header-row`, `72_bank_statement_no_rules_right_amounts`, `35_four_typefaces_one_page`,
`10_stamp_as_image`, `303_discharge_summary`, `70_magazine_drop_cap_photo_caption`,
`two-tables-stacked-with-no-gap`.

Every one of the 18 is **one page with `bad_pages: [0]`** (`DISP-TABLE.csv` `src_pages` = 1 on all 18).
That single fact kills construct A (a dropped `w:before` after a page break) as a candidate for any of
them: there is no page break to follow. It also kills the page-top half of the mechanism below, which is
why the `w:pgMar w:top` patch — measured, `git apply --check` clean, 3/3 PASS in Google — would clear
**zero** of these 18 today.

**Which checks block the other 90** (a document can appear in several rows):

| other failing check | documents |
|:--|--:|
| `60_text_column_right_edge` | 39 |
| `59_shape_anchor` | 36 |
| `04_chars_missing` | 32 |
| `45_char_accuracy` | 18 |
| `27_text_off_page` | 16 |
| `26_text_overlap` | 15 |
| `47_margins` | 14 |
| `13_text_colours` | 13 |
| `17_matched_runs` | 12 |
| `44_header_footer` | 11 |
| `43_within_10pt_x` | 7 |
| `35_rotation` | 5 |
| `46_text_crossing_rule`, `66_table_cell_width`, `23_line_pitch`, `53_embedded_faces` | 4 each |
| `62_table_columns`, `63_table_rows`, `25_invisible_text` | 3 each |
| `34a_span_size_match`, `05_chars_extra` | 2 each |
| `28_clipped_at_edge`, `32_stroke_lines`, `51_field_values`, `52_outline`, `64_table_span_across`, `65_table_span_down`, `37_super_subscript`, `38_list_markers` | 1 each |

---

## 2. The size of the prize, in documents

| statement | count |
|:--|--:|
| documents failing `18_displacement` | **108** |
| **solo** — `18_displacement` is the only failure | **18** |
| solo on `18_displacement` + exactly ONE other check | **28** |
| … of which the partner is `60_text_column_right_edge` | 12 |
| … `59_shape_anchor` | 10 |
| … `27_text_off_page` | 2 |
| … `45_char_accuracy` | 2 |
| … `46_text_crossing_rule` | 1 |
| … `53_embedded_faces` | 1 |
| leverage (`Σ 1/k`) — the leverage table's 46.6 | **46.56** |
| … contributed by the 18 solo documents | 18.00 |
| … contributed by the 90 blocked documents | 28.56 |

So the honest headline is two numbers: **18 documents are 18 whole documents away from clean**, and
**another 28 sit exactly one further check away** — of which 22 (12 + 10) sit behind
`60_text_column_right_edge` or `59_shape_anchor`, two checks that are themselves separately worked and
independently caused (`18` is vertical only: `|med_dx|` is 0.5 pt or less on all 18 solos, verified here).

---

## 3. The established mechanism, and what has already been tried and failed

**Mechanism (15 lines, each measured, sources named inline):**

1. The engine places every body line by `w:before` plus a hairline `w:line … lineRule="exact"`
   (`place()`/`resync()`), and on an ordinary paragraph Google honours `w:before` 1:1
   (`18_displacement-WBEFORE-IS-1TO1-GOOGLE-1005-agentA`; re-measured on
   `72_bank_statement_no_rules_right_amounts`: 1230/269/587/307/268 tw land at +0.17 to +0.23 pt).
2. **Google drops `w:before` on the first paragraph after an explicit page break.** `412_page_labels_roman`
   writes `w:before="1227"` (61.4 pt) on the first paragraph of every page: page 0 reads **+2.3 pt
   (honoured)**, pages 1-4 read **−58.8 pt (dropped)** — same value, same file, the only difference is
   the page break.
3. Over **332 continuation pages** the delivery is a constant translation, not scatter: residual sd
   **0.37 pt**, and **shift = 0.961 × gap − 0.58 pt, r = 0.975, median ratio 0.96**.
4. **Google delivers only 5-10 pt of an exact line height asked of an empty spacer**, whatever was asked
   (five documents asking 15.2-23.9 pt). As a length it charges
   `2.5873 × max(L/240, 0.06)` = **21.6 % of the ask** — `330_cad_drawing_sheet` asks 143.95 pt and
   loses **110.1**; `68_journal` asks 144.0 and reads **−114.28**.
5. So a gap carried in `w:line` is a gap Google never draws: everything below it sits high by **0.784·G**,
   one-signed and cumulative.
6. **Rows:** Google re-quantises a declared `w:trHeight` onto a 0.75 pt (one CSS px) ladder and lays
   `laid(d) = 0.75 × (round(d/0.75) + 1)` — three values in one render: 300 tw → **15.75**, 280 tw →
   **15.00**, 260 tw → **13.50** (`ROW-GROWTH-075-QUANTUM-LAW`; R14 correction).
7. Consequence: a declaration equal to the source pitch lays up to **1 pt taller per row**, so the error
   accumulates down a dense table (11 published points fit the law).
8. Coverage at HEAD over 213 documents, constructs read from the emitted `word/document.xml`:
   spacers + page-top = **63 of 102**; adding row height = **94 of 102**; only 8 unexplained
   (`DOCS-ROOT-CAUSES-24NOV` §18_displacement).
9. **The encoding is sufficient, the engine is wrong:** the same `.docx` in LibreOffice reads `|dy|`
   median **0.59 pt** (p90 2.81) where Google reads **6.38** (p90 69.01); **83 of 102 fail in Google and
   pass in LibreOffice**. Page boxes are identical (595.3 × 841.9 vs 596 × 842), so it is not scaling.
10. The check is right in substance: per page, a budget of upright runs further than
    `clamp(0.35·size, 1.5, 4.5)` pt out must not exceed `max(2, ceil(5 %))`, no page may have every run
    out, and no single run may be more than 2× its own tolerance out (`verify_google.py:5863-5930`).
    `dy = render baseline − source baseline`; positive = built line sits lower.

**Tried and failed — do not repeat (each with the number that killed it):**

| # | attempt | the measurement that killed it |
|--:|:--|:--|
| 1 | `w:hRule` `atLeast` → `exact` on content rows | exported PDF position-for-position identical; `68_journal` 0.0 pt, `mobile-bill` 0.0, `bank5` 0.0 — Google does not read `hRule` |
| 2 | snap the row's border box to a 0.75 pt rung (`ROW_BOX_SNAP_TW=15`, ceiling only) | `320` `med_dy` +8.2 → +8.2, no check changed state; and the probe was void (292 tw and 280 tw lay the same rung) |
| 3 | `ROW_RUNG_UNDER_TW = 0` (full corpus) | **4 better, 63 worse**; `price-list-2col-dense-right-aligned` 2.69 → **27.89**; table kept as `RANKING-rung0-FULL-CORPUS-28NOV.csv`; reverted |
| 4 | cell content = row height (`w:before` raised to `w:trHeight`) | corpus mean `median_pt` 2.274 → **2.641**; 13 better, 91 worse |
| 5 | carry the page-top gap in a 1×1 `hRule="exact"` table row (`-Dp2w.gapcarrier`) | no document becomes clean; `mobile-bill` `worst_dy` 10.0 → **33.8** |
| 6 | `-Dp2w.lineRule=auto` on the flow | `31_times_body_arial_headings` +2.75 → **+4.57**, spread 8.8 pt (worse in median *and* spread) |
| 7 | `LINE_BASE`/`BASELINE_EM` 0.8 → 0.312 (move the gap from `w:before` into `w:line`) | 1 clean, **4 unmoved, 2 worse** (one gained `59_shape_anchor`); residual +1.71 pt, not 0 — patch kept as `…BASELINE-EM-SWAP-REFUTED-27NOV.patch`, reverted |
| 8 | subtract the constant from every paragraph's `w:before` | **−34.50 pt** median: `w:before` is a GAP, so the correction multiplies by the line index |
| 9 | `-Dp2w.lineRule=autoflow` | `electricity-bill` −7.2 → +0.08 but `72_bank_statement` +1.1 → **+3.51** — opposite signs |
| 10 | the hairline deficit (`w:line` short by 0–1.8 pt) as the solo-document orderer | measured 0–1.8 pt and it **does not order** them |
| 11 | `w:framePr` / `w:tblpPr` as the page-top carrier | 0 `framePr` in 213 emitted files (Google ignores it); `tblpPr` re-wraps the page's text (file 01's BILL TO moved x 64 → 528) |
| 12 | **100 %** of the table gap into `w:before` | `mobile-bill` +0.49 (at 70 %) → **+4.70 → FAIL**; the fraction is a per-document knob, not a law |
| 13 | `w:w` character scaling to move text | Google leaves the export byte-identical (446.6 pt in LO, 428.4 in Google) |
| 14 | the 2880-twip spacer cap raised to 4320 | correct, but a one-document change: only `68_journal` (148.07 pt) exceeds the cap; next largest spacer is 18.30 pt |

What *did* land and what it bought: `SPACER_SPEND_FRAC = 0.70` (`DocxWriter.java:58`, spent at `:6171`)
plus `ROW_RUNG_UNDER_TW = 10` / `FOOT_ROOM_MIN_TW = 100`. Of the 6 solo documents the full-spend patch
took to 42/42 in Google on 22 Nov (`16_right_aligned_amounts_txtpos`, `22_invoice_four_columns_txtpos`,
`29_dot_leaders_txtpos`, `41_coloured_headings_white_bg`, `68_journal_wide_table_spanning`,
`73_marksheet_subject_marks_grade`), **four are clean in today's store** (`16_right_aligned` 42/42,
`29_dot_leaders` 42/42, `41_coloured_headings` 42/42, `73_marksheet` 42/42), `68_journal` is 40/42 and
blocked by `59_shape_anchor`, and `22_invoice` is 40/42 and blocked by `46_text_crossing_rule`. So the
spacer half of the mechanism is **already spent**: the remaining 18 solos are a residue *after* it.

---

## 4. The three worst solo documents: what produces the gap

**No converted `.docx` exists in this session, so the literal `word/document.xml` could not be read.**
`/scratch/work/p2w/out` and `/scratch/work/p2w/fixout` (the two paths `tools/p2w-bench/cause.py:114`
searches) do not exist here, `find` over the whole filesystem returns no corpus `.docx`, and the repo
commits no built document — only `benchmarks/DOCX-HASHES.json` (hashes, not content). Producing one
would need a corpus conversion, which this run is barred from. What follows is therefore the **engine's
own emission code** (`DocxWriter.java`, read at HEAD) plus the committed per-document tables and the
measured 0.75 pt law — labelled as such, not presented as an unzipped file.

The engine's spacer paragraph, verbatim from `DocxWriter.java:6186-6191` (the split branch):

```
sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
  .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"")
  .append(spendTw)
  .append("\" w:after=\"0\" w:line=\"")
  .append(Math.max(spacerHairTw, spacerTw - spendTw))
  .append("\" w:lineRule=\"exact\"/><w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr></w:p>");
```

and the row declaration, `DocxWriter.java:6601`:

```
if (pitchBinds && footRoom && rowHeightTw > ROW_RUNG_UNDER_TW) rowHeightTw -= ROW_RUNG_UNDER_TW;
```

**Worst 3 solo documents by `|worst_dy|`:**

| # | document | worst_dy | med_dy | rows | source pitch | construct |
|--:|:--|--:|--:|--:|--:|:--|
| 1 | `table-inside-two-column-page` | **69.2 pt** | +8.0 | 7 | 19.0 pt | **something else** — `w:trHeight` off the ladder |
| 2 | `71_invoice_space_aligned_no_rules` | **26.3 pt** | +2.9 | 14 | 18.0 pt | **something else** — per-run tail, no gap involved |
| 3 | `320_balance_sheet_statutory` | **16.2 pt** | +7.2 | 21 | 14.0 pt | **something else** — `w:trHeight` off the ladder |

**1. `table-inside-two-column-page` — the row ladder, and the arithmetic reproduces the measurement.**
Pitch 19.0 pt; the engine declares `19.0 − 0.5 = 18.5` pt (`ROW_RUNG_UNDER_TW = 10` tw = 0.5 pt). The
ladder lays `0.75 × (round(18.5/0.75) + 1) = 0.75 × (25 + 1) = 19.5` pt — **+1.0 pt per row**, one-signed.
7 rows × 1.0 = **+7.0 pt**, against a measured `med_dy` of **+8.0**. Its `spacer_paragraphs` is 0 and it
is a single page with `bad_pages: [0]`, so neither the page-top drop nor a spacer can be its carrier.
What makes it the worst is the tail (69.2 pt on one run) riding on top of the rigid +8.0 — 64 runs
matched, 46/47.

**2. `71_invoice_space_aligned_no_rules` — not a gap at all.** `med_dy` +2.9 with `worst_dy` 26.3 means
one or a very few runs are ~23 pt out while the page as a whole is nearly right; `spacer_paragraphs` is
**0** and `unspent_spacer` 0, so there is no empty spacer to charge and no page break to drop. Its pitch
(18.0 pt) is a multiple of 0.75, and the engine declares 17.5 → the ladder lays exactly 18.00, residual
**0.00**. So the ladder does not explain it either: this is a per-run placement error (the invoice's
space-aligned amount column), and the committed data does not name the construct. Reporting it as
"w:before dropped" or "spacer w:line" would be an invention; it is **not stated** in any committed
measurement.

**3. `320_balance_sheet_statutory` — the ladder, partly, and the residual it cannot remove.** Pitch
14.0 pt (not a multiple of 0.75); engine declares 13.5 → ladder lays **14.25**, **+0.25 pt/row** × 21
rows = **+5.25 pt** of irreducible drift, against measured `med_dy` +7.2. 14.25 is also the *nearest
attainable* laid height to a 14.0 pt pitch (the grid has no 14.00), so no declaration removes this
residual — only charging the page the laid number does. Caveat, stated: the 27 Nov half-A build
(`ROW-HEIGHT-IS-CONTENT-DRIVEN`, declaring the row on the rung and measuring per row in Google) read
`med_dy` over the table rows **+10.30 → −0.70** on this same document, so a rung-only model does not
close it either; that build did not change the number the flow below the table is charged with.

**What this section does and does not establish.** It establishes that the top of the solo prize is
**not** the class's famous two constructs: all three worst documents are single-page with
`bad_pages: [0]`, so there is no page-break `w:before` to drop, and none of them has an unspent spacer
(`unspent_spacer` 0 on all three) — the spacer half has already been spent by `SPACER_SPEND_FRAC`.
It does **not** establish the per-run cause of `71_invoice` (26.3 pt tail with a 2.9 pt median), which
needs one `dy.py` per-run read on a Google export and is not answerable from committed files.

---

## 5. The one rule, and its falsifier

The census says the 18 solos are **not one construct**: 12 carry a rigid offset (`|med_dy| ≥ 1.5 pt`)
and 6 fail on a per-run tail with a near-zero median (`303_discharge_summary` +0.9, `306_clinical_protocol_synopsis`
−0.4, `72_bank_statement_no_rules_right_amounts` −1.0, `balance-sheet-two-columns-of-figures` −0.5,
`table-with-no-header-row` +0.7, `two-tables-stacked-with-no-gap` −1.2); of the 12 rigid ones **8 are
over-delivery** (built text sits *lower* than the source: `30_mixed`, `320`, `70_magazine`, `71_invoice`,
`74_balance_sheet`, `bus-timetable`, `price-list-2col`, `table-inside-two-column-page`) and **4 are
under-delivery** (`10_stamp_as_image`, `35_four_typefaces`, `403_crossword_puzzle`, `eway-bill`). No
fraction, rung constant or fraction-of-gap knob can be true of that mixture — which is exactly why every
one-constant attempt in §3 was refuted, and why the counts do not correlate with any committed predictor
(`|worst_dy|` vs `docx_table_rows` r = −0.12, vs `spacer_paragraphs` r = −0.32, vs `unspent_spacer`
r = −0.19, vs `google_per_row_growth_pt` r = +0.12).

> **The rule: every table row must be charged to the page — and every block below the table placed —
> at the height Google will actually lay, `0.75 × (round(d/0.75) + 1)`, never at the source pitch the
> row was drawn at.**

That is one expression, true of every document and every table (it is the ladder Google is measured to
apply, three for three: 300 tw → 15.75, 280 → 15.00, 260 → 13.50), and it is the only change on the table
that attacks the over-delivery block — 8 of the 18 solos, the largest single-direction group. Its
predicted reach is stated honestly: it **reduces** the off-ladder solos by exactly their per-row rung
(`table-inside-two-column-page` +1.00/row × 7 rows = the +7.0 of its measured +8.0; `320` +0.25/row × 21
rows = +5.25 of its +7.2; `74_balance_sheet_indented_subitems` +0.25/row), it **changes nothing** on the 6
solos whose pitch is already a multiple of 0.75 (`10_stamp_as_image`, `30_mixed`,
`71_invoice_space_aligned_no_rules`, `eway-bill`, `table-with-no-header-row`, `two-tables-stacked` — their
charge is already right and they drift anyway), and it cannot touch the 6 tail-only or the 4
under-delivery solos. So the rule's measured-arithmetic claim is "it removes the largest single explained
term from 4 of the 18 solos", not "it clears 18".

**The falsifier that would prove it wrong:** a document whose source pitch is a multiple of 0.75 pt — so
that the ladder's residual is exactly 0 by the law — which nonetheless drifts one-signed down its own
table, or any document whose `share5` in `RANKING.csv` rises when the laid height is charged instead of
the pitch (the exact falsifier the 28 Nov full-corpus run used to kill `ROW_RUNG_UNDER_TW = 0`: 4
better, 63 worse). Both halves are already half-visible in this census: six solos sit on-ladder and
drift anyway, which refutes the ladder as a *complete* explanation of the class while leaving it the
largest single claimable block.

---

## 6. What is not measured here

* No Google round trip, no build, no corpus conversion: every Google number is the committed store
  (engine `a05b20eb05fe0fc8`, 27 Nov), quoted, not re-measured.
* `benchmarks/DISP-TABLE.csv` is **stale against the store** on several rows (`72_bank_statement…`
  worst 32.0 vs 3.5 stored; `eway-bill` 107.4 vs 4.7; `71_invoice` 6.7 vs 26.3). It was used only for
  `attribution`, `docx_table_rows`, `declared_row_pt`, `spacer_paragraphs`, `unspent_spacer` and
  `src_pages`, which are structural and do not move with the engine; every `dy` in this file is the
  store's.
* The 18 solos' failing CLAUSE (budget vs tail vs all-runs-out) is not recorded in the store — only
  `bad_pages` and the two summaries — so the 12/6 rigid-vs-tail split is inferred from `med_dy` against
  `worst_dy`, and is labelled as such.
* `71_invoice_space_aligned_no_rules`'s 26.3 pt run has no named construct in any committed file.
* The gate question in the round's brief (`regress.py --check` refusing at HEAD on 84 rows) is untouched
  by this file: nothing here was built, so no `share5` was produced.

*Files produced: this one. Nothing committed, nothing else modified.*
