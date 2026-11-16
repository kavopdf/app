# Defect classes - round 1

Documents measured: **212 of 213**

Ranked by damage, then by the number of documents the class holds: one mechanism
fixed once clears every document under it. share@5px is the ranking measure -
max_pt is reported but never ranks, because a single outlier pixel dominates it.

## Classes

| signature | problem | documents |
|---|---|---|
| content-loss | content-missing-nothing-in-its-place | 30 |
| content-loss | content-missing-partly-replaced | 16 |
| mixed | content-partly-lost-and-displaced | 7 |
| mixed | content-partly-lost | 11 |
| displacement | content-present-wholly-displaced | 15 |
| displacement | content-present-partly-displaced | 12 |
| displacement | single-element-far-out | 1 |
| clean | none | 120 |

## Documents

| # | document | problem | share5 | max_pt | worst_page | status | note |
|---|---|---|---|---|---|---|---|
| 1 | `415_inline_images` | content-missing-nothing-in-its-place | 89.04 | 153.12 | 1 | OPEN | - |
| 2 | `mobile-bill` | content-missing-nothing-in-its-place | 18.48 | 75.36 | 1 | OPEN | - |
| 3 | `salary-slip-factory-wages` | content-missing-nothing-in-its-place | 18.09 | 71.04 | 1 | OPEN | - |
| 4 | `two-tables-stacked-with-no-gap` | content-missing-nothing-in-its-place | 17.20 | 45.12 | 1 | OPEN | - |
| 5 | `marksheet-university-consolidated` | content-missing-nothing-in-its-place | 16.78 | 57.12 | 1 | OPEN | - |
| 6 | `electricity-bill` | content-missing-nothing-in-its-place | 16.24 | 100.80 | 1 | OPEN | - |
| 7 | `insurance-policy-schedule` | content-missing-nothing-in-its-place | 13.29 | 72.48 | 1 | OPEN | - |
| 8 | `landscape-page-inside-portrait-document` | content-missing-nothing-in-its-place | 13.08 | 28.32 | 2 | OPEN | - |
| 9 | `form16-part-b` | content-missing-nothing-in-its-place | 12.32 | 56.64 | 2 | OPEN | - |
| 10 | `mutual-fund-statement` | content-missing-nothing-in-its-place | 12.05 | 32.64 | 1 | OPEN | - |
| 11 | `property-tax-receipt` | content-missing-nothing-in-its-place | 10.78 | 55.68 | 1 | OPEN | - |
| 12 | `admit-card` | content-missing-nothing-in-its-place | 10.68 | 57.12 | 1 | OPEN | - |
| 13 | `gst-invoice-multipage-item-table` | content-missing-nothing-in-its-place | 10.44 | 52.32 | 1 | OPEN | - |
| 14 | `delivery-challan` | content-missing-nothing-in-its-place | 10.26 | 39.84 | 1 | OPEN | - |
| 15 | `table-across-page-break-repeated-header` | content-missing-nothing-in-its-place | 9.41 | 36.00 | 3 | OPEN | - |
| 16 | `gst-invoice-3line-items` | content-missing-nothing-in-its-place | 7.15 | 20.16 | 1 | OPEN | - |
| 17 | `boq-tender-bill-of-quantities` | content-missing-nothing-in-its-place | 7.10 | 28.80 | 1 | OPEN | - |
| 18 | `table-with-rotated-header` | content-missing-nothing-in-its-place | 6.42 | 30.24 | 1 | OPEN | - |
| 19 | `balance-sheet-and-profit-loss` | content-missing-nothing-in-its-place | 6.20 | 34.08 | 1 | OPEN | - |
| 20 | `annual-review-2col-uneven-columns` | content-missing-nothing-in-its-place | 5.77 | 27.84 | 1 | OPEN | - |
| 21 | `purchase-order` | content-missing-nothing-in-its-place | 5.30 | 38.40 | 1 | OPEN | - |
| 22 | `23_timetable_grid_txtpos` | content-missing-nothing-in-its-place | 5.16 | 46.56 | 1 | OPEN | - |
| 23 | `invoice-line-items-qty-rate-amount` | content-missing-nothing-in-its-place | 4.90 | 42.24 | 1 | OPEN | - |
| 24 | `marksheet-subject-left-marks-right` | content-missing-nothing-in-its-place | 4.55 | 77.28 | 1 | OPEN | - |
| 25 | `bank-statement-5-pages` | content-missing-nothing-in-its-place | 3.09 | 50.88 | 2 | OPEN | - |
| 26 | `69_two_col_legal_numbered_clauses` | content-missing-nothing-in-its-place | 2.53 | 12.48 | 1 | OPEN | - |
| 27 | `35_four_typefaces_one_page` | content-missing-nothing-in-its-place | 2.19 | 36.48 | 1 | OPEN | - |
| 28 | `31_times_body_arial_headings` | content-missing-nothing-in-its-place | 2.11 | 38.40 | 1 | OPEN | - |
| 29 | `07_stamp_over_table` | content-missing-nothing-in-its-place | 1.82 | 66.24 | 1 | OPEN | - |
| 30 | `312_affidavit_stamp_paper` | content-missing-nothing-in-its-place | 1.07 | 53.76 | 1 | OPEN | - |
| 31 | `041122-Account_Opening_Form` | content-missing-partly-replaced | 98.65 | 937.92 | 9 | OPEN | - |
| 32 | `Account_Opening_Form_Fillable_filled` | content-missing-partly-replaced | 97.62 | 358.08 | 7 | OPEN | - |
| 33 | `one-page-rotated-180-degrees` | content-missing-partly-replaced | 81.64 | 177.60 | 2 | OPEN | - |
| 34 | `600_reviewed_invoice_with_annotations` | content-missing-partly-replaced | 63.08 | 62.88 | 1 | OPEN | - |
| 35 | `601_fillable_admission_form` | content-missing-partly-replaced | 52.39 | 27.84 | 1 | OPEN | - |
| 36 | `table-inside-two-column-page` | content-missing-partly-replaced | 42.00 | 84.48 | 1 | OPEN | - |
| 37 | `360_restaurant_menu` | content-missing-partly-replaced | 34.43 | 45.60 | 1 | OPEN | - |
| 38 | `text-held-twice-shadow-text` | content-missing-partly-replaced | 34.33 | 92.64 | 1 | OPEN | - |
| 39 | `77_arabic_rtl_document` | content-missing-partly-replaced | 11.89 | 19.68 | 1 | OPEN | - |
| 40 | `academic-paper-ieee-2col-abstract` | content-missing-partly-replaced | 10.39 | 27.36 | 2 | OPEN | - |
| 41 | `journal-2col-with-footnotes` | content-missing-partly-replaced | 7.75 | 35.04 | 1 | OPEN | - |
| 42 | `370_offer_letter` | content-missing-partly-replaced | 3.47 | 31.68 | 1 | OPEN | - |
| 43 | `352_certificate_ornate_border` | content-missing-partly-replaced | 3.00 | 5.28 | 1 | OPEN | - |
| 44 | `11_stamp_with_signature_image` | content-missing-partly-replaced | 2.77 | 25.92 | 1 | OPEN | - |
| 45 | `317_rti_response` | content-missing-partly-replaced | 2.18 | 36.96 | 1 | OPEN | - |
| 46 | `gst-invoice-with-qr-code` | content-missing-partly-replaced | 1.24 | 16.32 | 1 | OPEN | - |
| 47 | `itr-computation-with-slab-table` | content-partly-lost-and-displaced | 68.82 | 133.92 | 1 | OPEN | - |
| 48 | `table-with-merged-cells` | content-partly-lost-and-displaced | 4.93 | 13.92 | 1 | OPEN | - |
| 49 | `14_stamp_chars_positioned_td` | content-partly-lost-and-displaced | 3.89 | 25.44 | 1 | OPEN | - |
| 50 | `newspaper-2col-fullwidth-headline` | content-partly-lost-and-displaced | 3.46 | 24.48 | 1 | OPEN | - |
| 51 | `321_auditors_report` | content-partly-lost-and-displaced | 2.62 | 24.48 | 1 | OPEN | - |
| 52 | `313_power_of_attorney` | content-partly-lost-and-displaced | 2.29 | 40.32 | 1 | OPEN | - |
| 53 | `310_court_judgment` | content-partly-lost-and-displaced | 1.73 | 18.72 | 1 | OPEN | - |
| 54 | `411_nested_xobject_transforms` | content-partly-lost | 31.05 | 97.92 | 1 | OPEN | - |
| 55 | `40_devanagari_shaping_font` | content-partly-lost | 10.48 | 24.00 | 1 | OPEN | - |
| 56 | `76_devanagari_table` | content-partly-lost | 7.91 | 15.36 | 1 | OPEN | - |
| 57 | `very-long-single-column-table` | content-partly-lost | 6.87 | 46.56 | 3 | OPEN | - |
| 58 | `policy-2col-spanning-section-heading` | content-partly-lost | 5.37 | 24.96 | 1 | OPEN | - |
| 59 | `salary-slip-corporate` | content-partly-lost | 5.09 | 35.04 | 1 | OPEN | - |
| 60 | `33_sans_nondefault_body` | content-partly-lost | 4.49 | 36.00 | 1 | OPEN | - |
| 61 | `magazine-2col-pullquote-spanning` | content-partly-lost | 3.49 | 21.60 | 1 | OPEN | - |
| 62 | `304_package_insert_small_print` | content-partly-lost | 3.41 | 21.12 | 1 | OPEN | - |
| 63 | `61_two_col_abstract_spanning` | content-partly-lost | 2.01 | 15.84 | 1 | OPEN | - |
| 64 | `80_gstin_pan_cin_ifsc_table` | content-partly-lost | 2.01 | 13.44 | 1 | OPEN | - |
| 65 | `75_merged_header_cell_three_columns` | content-present-wholly-displaced | 27.62 | 21.60 | 1 | OPEN | - |
| 66 | `71_invoice_space_aligned_no_rules` | content-present-wholly-displaced | 26.88 | 9.12 | 1 | OPEN | - |
| 67 | `report-2col-table-spanning-both-columns` | content-present-wholly-displaced | 22.58 | 49.92 | 1 | OPEN | - |
| 68 | `03_stamp_vertical_90deg` | content-present-wholly-displaced | 16.98 | 5.76 | 1 | OPEN | - |
| 69 | `78_mixed_english_devanagari_line` | content-present-wholly-displaced | 13.51 | 18.24 | 1 | OPEN | - |
| 70 | `66_two_col_footnotes_bottom` | content-present-wholly-displaced | 13.03 | 8.64 | 1 | OPEN | - |
| 71 | `68_journal_wide_table_spanning` | content-present-wholly-displaced | 12.83 | 8.64 | 1 | OPEN | - |
| 72 | `363_warranty_card` | content-present-wholly-displaced | 10.58 | 4.32 | 1 | OPEN | - |
| 73 | `brochure-3col-with-sidebar-box` | content-present-wholly-displaced | 6.84 | 21.12 | 1 | OPEN | - |
| 74 | `gst-invoice-horizontal-rules-only` | content-present-wholly-displaced | 6.72 | 9.60 | 1 | OPEN | - |
| 75 | `374_org_chart` | content-present-wholly-displaced | 5.92 | 4.80 | 1 | OPEN | - |
| 76 | `payslip-label-left-amount-right` | content-present-wholly-displaced | 5.59 | 4.32 | 1 | OPEN | - |
| 77 | `417_rotate180_and_mirrored` | content-present-wholly-displaced | 5.50 | 5.76 | 2 | OPEN | - |
| 78 | `product-catalogue-code-left-price-right` | content-present-wholly-displaced | 1.71 | 8.16 | 1 | OPEN | - |
| 79 | `316_contract_with_schedules` | content-present-wholly-displaced | 1.26 | 27.36 | 1 | OPEN | - |
| 80 | `table-of-contents-dot-leaders` | content-present-partly-displaced | 10.72 | 26.40 | 1 | OPEN | - |
| 81 | `64_newspaper_uneven_columns_ad_boxes` | content-present-partly-displaced | 9.11 | 11.04 | 1 | OPEN | - |
| 82 | `bank-statement-horizontal-rules-only` | content-present-partly-displaced | 6.89 | 6.24 | 1 | OPEN | - |
| 83 | `330_cad_drawing_sheet` | content-present-partly-displaced | 4.91 | 14.88 | 1 | OPEN | - |
| 84 | `65_two_col_full_width_figure_caption` | content-present-partly-displaced | 4.91 | 9.12 | 1 | OPEN | - |
| 85 | `406_passport_mrz_page` | content-present-partly-displaced | 3.45 | 15.84 | 1 | OPEN | - |
| 86 | `price-list-2col-dense-right-aligned` | content-present-partly-displaced | 2.69 | 7.20 | 1 | OPEN | - |
| 87 | `315_gazette_notification` | content-present-partly-displaced | 1.96 | 8.64 | 1 | OPEN | - |
| 88 | `price-list-right-aligned-amounts` | content-present-partly-displaced | 1.79 | 5.76 | 1 | OPEN | - |
| 89 | `27_two_column_left_short_txtpos` | content-present-partly-displaced | 1.62 | 7.68 | 1 | OPEN | - |
| 90 | `392_statistical_console_output` | content-present-partly-displaced | 1.61 | 4.32 | 1 | OPEN | - |
| 91 | `70_magazine_drop_cap_photo_caption` | content-present-partly-displaced | 1.49 | 10.56 | 1 | OPEN | - |
| 92 | `newsletter-3col-header-footer` | single-element-far-out | 3.45 | 77.28 | 1 | OPEN | - |
| 93 | `34_monospace_document` | none | 0.93 | 4.80 | 1 | FIXED | no defect |
| 94 | `eway-bill` | none | 0.91 | 31.20 | 1 | FIXED | no defect |
| 95 | `67_two_col_with_sidebar` | none | 0.80 | 11.52 | 1 | FIXED | no defect |
| 96 | `28_value_overflows_cell_txtpos` | none | 0.74 | 15.36 | 1 | FIXED | no defect |
| 97 | `79_inr_indian_digit_grouping_table` | none | 0.74 | 9.12 | 1 | FIXED | no defect |
| 98 | `39_small_caps_letter_spacing` | none | 0.72 | 4.80 | 1 | FIXED | no defect |
| 99 | `326_itr_computation` | none | 0.63 | 13.92 | 1 | FIXED | no defect |
| 100 | `344_customs_declaration` | none | 0.61 | 49.92 | 1 | FIXED | no defect |
| 101 | `table-with-no-header-row` | none | 0.61 | 11.52 | 1 | FIXED | no defect |
| 102 | `37_font_not_embedded_substitution` | none | 0.58 | 14.40 | 1 | FIXED | no defect |
| 103 | `balance-sheet-two-columns-of-figures` | none | 0.57 | 5.76 | 1 | FIXED | no defect |
| 104 | `question-paper-marks-right-margin` | none | 0.44 | 14.88 | 1 | FIXED | no defect |
| 105 | `413_tagged_pdf_actualtext` | none | 0.38 | 3.84 | 1 | FIXED | no defect |
| 106 | `383_api_docs_page` | none | 0.30 | 19.68 | 1 | FIXED | no defect |
| 107 | `bus-timetable-station-left-times-right` | none | 0.27 | 12.96 | 1 | FIXED | no defect |
| 108 | `404_sudoku_grid` | none | 0.27 | 3.36 | 1 | FIXED | no defect |
| 109 | `364_event_ticket` | none | 0.25 | 2.88 | 1 | FIXED | no defect |
| 110 | `343_air_waybill` | none | 0.23 | 14.88 | 1 | FIXED | no defect |
| 111 | `admission-form-labels-left-boxes-right` | none | 0.21 | 4.32 | 1 | FIXED | no defect |
| 112 | `05_round_company_seal_curved_text` | none | 0.19 | 5.28 | 1 | FIXED | no defect |
| 113 | `boq-horizontal-rules-only` | none | 0.13 | 8.64 | 1 | FIXED | no defect |
| 114 | `350_question_paper` | none | 0.11 | 16.80 | 1 | FIXED | no defect |
| 115 | `08_two_overlapping_stamps` | none | 0.11 | 11.04 | 1 | FIXED | no defect |
| 116 | `391_survey_questionnaire_grid` | none | 0.11 | 4.32 | 1 | FIXED | no defect |
| 117 | `333_datasheet_spec_tables` | none | 0.07 | 6.24 | 1 | FIXED | no defect |
| 118 | `340_bill_of_lading` | none | 0.07 | 3.36 | 1 | FIXED | no defect |
| 119 | `300_prescription_rx` | none | 0.06 | 21.60 | 1 | FIXED | no defect |
| 120 | `60_page_border` | none | 0.06 | 8.16 | 1 | FIXED | no defect |
| 121 | `12_stamp_across_page_break` | none | 0.05 | 3.36 | 2 | FIXED | no defect |
| 122 | `45_coloured_callout_box` | none | 0.05 | 3.36 | 1 | FIXED | no defect |
| 123 | `401_trifold_brochure` | none | 0.03 | 10.56 | 1 | FIXED | no defect |
| 124 | `25_signature_block_underscores_txtpos` | none | 0.03 | 10.08 | 1 | FIXED | no defect |
| 125 | `15_stamp_on_scanned_page` | none | 0.03 | 3.36 | 1 | FIXED | no defect |
| 126 | `362_price_list_dense` | none | 0.03 | 3.36 | 1 | FIXED | no defect |
| 127 | `390_wide_data_appendix` | none | 0.03 | 3.36 | 1 | FIXED | no defect |
| 128 | `74_balance_sheet_indented_subitems` | none | 0.03 | 3.36 | 1 | FIXED | no defect |
| 129 | `301_lab_report_panel` | none | 0.02 | 7.20 | 1 | FIXED | no defect |
| 130 | `44_coloured_underlined_hyperlinks` | none | 0.02 | 3.84 | 1 | FIXED | no defect |
| 131 | `20_numbered_list_separate_column_txtpos` | none | 0.02 | 2.88 | 1 | FIXED | no defect |
| 132 | `365_recipe_card` | none | 0.02 | 2.88 | 1 | FIXED | no defect |
| 133 | `13_stamp_non_english` | none | 0.01 | 3.84 | 1 | FIXED | no defect |
| 134 | `26_footnote_marker_bottom_note_txtpos` | none | 0.01 | 3.84 | 1 | FIXED | no defect |
| 135 | `375_attendance_register` | none | 0.01 | 3.84 | 1 | FIXED | no defect |
| 136 | `393_spectrum_peak_table` | none | 0.01 | 3.36 | 1 | FIXED | no defect |
| 137 | `38_faux_bold_italic_synthesised` | none | 0.01 | 2.88 | 1 | FIXED | no defect |
| 138 | `46_chart_coloured_labels_body_text` | none | 0.01 | 2.88 | 1 | FIXED | no defect |
| 139 | `342_packing_list` | none | 0.00 | 3.36 | 1 | FIXED | no defect |
| 140 | `407_id_card_front_back` | none | 0.00 | 3.36 | 1 | FIXED | no defect |
| 141 | `56_table_indented_from_margin` | none | 0.00 | 3.36 | 1 | FIXED | no defect |
| 142 | `02_stamp_rotated_15deg_upleft` | none | 0.00 | 2.88 | 1 | FIXED | no defect |
| 143 | `323_credit_card_statement` | none | 0.00 | 2.88 | 1 | FIXED | no defect |
| 144 | `325_demat_holdings_statement` | none | 0.00 | 2.88 | 1 | FIXED | no defect |
| 145 | `335_msds_safety_data_sheet` | none | 0.00 | 2.88 | 1 | FIXED | no defect |
| 146 | `353_admit_card` | none | 0.00 | 2.88 | 1 | FIXED | no defect |
| 147 | `381_incident_report_timeline` | none | 0.00 | 2.88 | 1 | FIXED | no defect |
| 148 | `403_crossword_puzzle` | none | 0.00 | 2.88 | 1 | FIXED | no defect |
| 149 | `01_stamp_rotated_15deg_upright` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 150 | `10_stamp_as_image` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 151 | `16_right_aligned_amounts_txtpos` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 152 | `17_three_column_widths_txtpos` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 153 | `18_centred_heading_left_body_txtpos` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 154 | `19_hanging_indent_txtpos` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 155 | `21_form_labels_x60_values_x300_txtpos` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 156 | `29_dot_leaders_txtpos` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 157 | `306_clinical_protocol_synopsis` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 158 | `311_fir_police_form` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 159 | `314_tender_rfp_boq` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 160 | `318_court_summons_form` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 161 | `320_balance_sheet_statutory` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 162 | `324_loan_amortisation_schedule` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 163 | `331_pid_diagram` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 164 | `332_bom_on_drawing` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 165 | `341_shipping_manifest` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 166 | `36_embedded_subset_font` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 167 | `373_leave_application_form` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 168 | `402_calendar_month_grid` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 169 | `42_table_coloured_header_alternating_rows` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 170 | `50_invoice_coloured_total_row` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 171 | `51_two_cm_margins` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 172 | `52_one_cm_margin_wide_body` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 173 | `55_sidebar_box_beside_body` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 174 | `62_two_col_newsletter_pull_quote` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 175 | `63_three_column_brochure` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 176 | `72_bank_statement_no_rules_right_amounts` | none | 0.00 | 2.40 | 1 | FIXED | no defect |
| 177 | `04_stamp_180deg_upside_down` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 178 | `06_rect_paid_stamp_red_transparent` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 179 | `24_address_block_indents_txtpos` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 180 | `302_radiology_report` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 181 | `303_discharge_summary` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 182 | `334_patent_document` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 183 | `351_omr_answer_sheet` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 184 | `371_experience_certificate` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 185 | `394_map_with_legend` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 186 | `43_red_stamp_over_black_text` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 187 | `49_coloured_background_block_paragraph` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 188 | `53_single_space_body_15_headings` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 189 | `57_centred_title_page_left_body_pages` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 190 | `59_landscape_mixed_portrait` | none | 0.00 | 1.92 | 1 | FIXED | no defect |
| 191 | `09_stamp_font_not_embedded` | none | 0.00 | 1.44 | 1 | FIXED | no defect |
| 192 | `22_invoice_four_columns_txtpos` | none | 0.00 | 1.44 | 1 | FIXED | no defect |
| 193 | `305_vaccination_certificate` | none | 0.00 | 1.44 | 1 | FIXED | no defect |
| 194 | `30_mixed_font_sizes_one_baseline_txtpos` | none | 0.00 | 1.44 | 1 | FIXED | no defect |
| 195 | `322_mutual_fund_factsheet` | none | 0.00 | 1.44 | 1 | FIXED | no defect |
| 196 | `400_comic_page_speech_bubbles` | none | 0.00 | 1.44 | 1 | FIXED | no defect |
| 197 | `41_coloured_headings_white_bg` | none | 0.00 | 1.44 | 1 | FIXED | no defect |
| 198 | `48_form_coloured_border_coloured_values` | none | 0.00 | 1.44 | 1 | FIXED | no defect |
| 199 | `58_header_rule_footer_rule` | none | 0.00 | 1.44 | 1 | FIXED | no defect |
| 200 | `73_marksheet_subject_marks_grade` | none | 0.00 | 1.44 | 1 | FIXED | no defect |
| 201 | `32_serif_nondefault_body` | none | 0.00 | 0.96 | 1 | FIXED | no defect |
| 202 | `372_timesheet_grid` | none | 0.00 | 0.96 | 1 | FIXED | no defect |
| 203 | `380_runbook_terminal_output` | none | 0.00 | 0.96 | 1 | FIXED | no defect |
| 204 | `405_sheet_music_lyrics` | none | 0.00 | 0.96 | 1 | FIXED | no defect |
| 205 | `410_form_xobject_reused` | none | 0.00 | 0.96 | 1 | FIXED | no defect |
| 206 | `47_grey_body_black_headings` | none | 0.00 | 0.96 | 1 | FIXED | no defect |
| 207 | `54_two_column_body_full_width_header_footer` | none | 0.00 | 0.96 | 1 | FIXED | no defect |
| 208 | `602_bookmarked_annual_report` | none | 0.00 | 0.96 | 1 | FIXED | no defect |
| 209 | `361_product_catalogue_grid` | none | 0.00 | 0.00 | 1 | FIXED | no defect |
| 210 | `382_architecture_diagram` | none | 0.00 | 0.00 | 1 | FIXED | no defect |
| 211 | `412_page_labels_roman` | none | 0.00 | 0.00 | 1 | FIXED | no defect |
| 212 | `414_transparency_softmask` | none | 0.00 | 0.00 | 1 | FIXED | no defect |

## Parked

`416_many_tiny_pages` is **PARKED**, not OPEN and not FIXED: it is the 213th row of
`RANKING.csv` and it carries no score. It is exempted in `tools/p2w-bench/EXEMPT.json` -
300 pages, one whole-document measurement exceeds the per-command budget, so the run is
killed mid-document and no result is written. It cannot appear in the table above, which
holds exactly the 212 documents that were measured; a row for it there is a phantom that
the classify gate rejects as an unscored document. The real fix is resumable
page-by-page measurement, the same fix the nine-page forms need.
