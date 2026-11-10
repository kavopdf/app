# Google-render baseline

Every document, measured by `verify_google.py` against the PDF that Google Docs
itself exports. A document passes only when all 31 checks pass.

The instrument: the docx goes to Drive, Drive converts it to a Google Doc, that
document is exported as PDF, and the export is compared to the original. See
`VERIFY-GOOGLE.md` for the pipeline and `verify_google.py` for the checks.

This file is written by the hourly baseline cron. Rows are never deleted; a
re-run of a document replaces its own row.

| document | score | verdict | failed checks | measured |
|---|---|---|---|---|
| 01_stamp_rotated_15deg_upright | 15/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 07_table_rows, 09_font_names, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 25_invisible_text, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 02_stamp_rotated_15deg_upleft | 21/31 | FAIL | 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 19_worst_dy, 20_within_10pt, 22_reading_order, 25_invisible_text, 30_ink_where_blank_was | 2026-11-10 |
| 03_stamp_vertical_90deg | 13/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 11_bold_runs, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 04_stamp_180deg_upside_down | 11/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 06_table_columns, 07_table_rows, 09_font_names, 11_bold_runs, 16_numeric_runs, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 25_invisible_text, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 05_round_company_seal_curved_text | 13/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 06_table_columns, 07_table_rows, 09_font_names, 11_bold_runs, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 06_rect_paid_stamp_red_transparent | 15/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 16_numeric_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 26_text_overlap, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 07_stamp_over_table | 14/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 08_two_overlapping_stamps | 14/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 07_table_rows, 11_bold_runs, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 25_invisible_text, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 09_stamp_font_not_embedded | 22/31 | FAIL | 03_word_count, 04_words_missing, 09_font_names, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 10_stamp_as_image | 14/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 07_table_rows, 16_numeric_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 25_invisible_text, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 11_stamp_with_signature_image | 20/31 | FAIL | 03_word_count, 04_words_missing, 09_font_names, 11_bold_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 12_stamp_across_page_break | 17/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 07_table_rows, 11_bold_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 13_stamp_non_english | 22/31 | FAIL | 03_word_count, 04_words_missing, 09_font_names, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 14_stamp_chars_positioned_td | 23/31 | FAIL | 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 18_median_dy, 20_within_10pt, 22_reading_order, 25_invisible_text | 2026-11-10 |
| 15_stamp_on_scanned_page | 21/31 | FAIL | 03_word_count, 04_words_missing, 09_font_names, 10_font_sizes, 13_text_colours, 17_matched_runs, 20_within_10pt, 22_reading_order, 23_line_pitch, 31_pages_lost_their_text | 2026-11-10 |
| 16_right_aligned_amounts_txtpos | 15/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 17_three_column_widths_txtpos | 21/31 | FAIL | 02_text_run_count, 07_table_rows, 09_font_names, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 26_text_overlap, 29_blank_where_ink_was, 30_ink_where_blank_was | 2026-11-10 |
| 18_centred_heading_left_body_txtpos | 30/31 | FAIL | 18_median_dy | 2026-11-10 |
| 19_hanging_indent_txtpos | 29/31 | FAIL | 09_font_names, 23_line_pitch | 2026-11-10 |
| 20_numbered_list_separate_column_txtpos | 25/31 | FAIL | 09_font_names, 19_worst_dy, 20_within_10pt, 22_reading_order, 26_text_overlap, 29_blank_where_ink_was | 2026-11-10 |
| 21_form_labels_x60_values_x300_txtpos | 20/31 | FAIL | 01_page_count, 07_table_rows, 09_font_names, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 30_ink_where_blank_was | 2026-11-10 |
| 22_invoice_four_columns_txtpos |  |  |  |  |
| 23_timetable_grid_txtpos |  |  |  |  |
| 24_address_block_indents_txtpos |  |  |  |  |
| 25_signature_block_underscores_txtpos |  |  |  |  |
| 26_footnote_marker_bottom_note_txtpos |  |  |  |  |
| 27_two_column_left_short_txtpos |  |  |  |  |
| 28_value_overflows_cell_txtpos |  |  |  |  |
| 29_dot_leaders_txtpos |  |  |  |  |
| 300_prescription_rx |  |  |  |  |
| 301_lab_report_panel |  |  |  |  |
| 302_radiology_report |  |  |  |  |
| 303_discharge_summary |  |  |  |  |
| 304_package_insert_small_print |  |  |  |  |
| 305_vaccination_certificate |  |  |  |  |
| 306_clinical_protocol_synopsis |  |  |  |  |
| 30_mixed_font_sizes_one_baseline_txtpos |  |  |  |  |
| 310_court_judgment |  |  |  |  |
| 311_fir_police_form |  |  |  |  |
| 312_affidavit_stamp_paper |  |  |  |  |
| 313_power_of_attorney |  |  |  |  |
| 314_tender_rfp_boq |  |  |  |  |
| 315_gazette_notification |  |  |  |  |
| 316_contract_with_schedules |  |  |  |  |
| 317_rti_response |  |  |  |  |
| 318_court_summons_form |  |  |  |  |
| 31_times_body_arial_headings |  |  |  |  |
| 320_balance_sheet_statutory |  |  |  |  |
| 321_auditors_report |  |  |  |  |
| 322_mutual_fund_factsheet |  |  |  |  |
| 323_credit_card_statement |  |  |  |  |
| 324_loan_amortisation_schedule |  |  |  |  |
| 325_demat_holdings_statement |  |  |  |  |
| 326_itr_computation |  |  |  |  |
| 32_serif_nondefault_body |  |  |  |  |
| 330_cad_drawing_sheet |  |  |  |  |
| 331_pid_diagram |  |  |  |  |
| 332_bom_on_drawing |  |  |  |  |
| 333_datasheet_spec_tables |  |  |  |  |
| 334_patent_document |  |  |  |  |
| 335_msds_safety_data_sheet |  |  |  |  |
| 33_sans_nondefault_body |  |  |  |  |
| 340_bill_of_lading |  |  |  |  |
| 341_shipping_manifest |  |  |  |  |
| 342_packing_list |  |  |  |  |
| 343_air_waybill |  |  |  |  |
| 344_customs_declaration |  |  |  |  |
| 34_monospace_document |  |  |  |  |
| 350_question_paper |  |  |  |  |
| 351_omr_answer_sheet |  |  |  |  |
| 352_certificate_ornate_border |  |  |  |  |
| 353_admit_card |  |  |  |  |
| 35_four_typefaces_one_page |  |  |  |  |
| 360_restaurant_menu |  |  |  |  |
| 361_product_catalogue_grid |  |  |  |  |
| 362_price_list_dense |  |  |  |  |
| 363_warranty_card |  |  |  |  |
| 364_event_ticket |  |  |  |  |
| 365_recipe_card |  |  |  |  |
| 36_embedded_subset_font |  |  |  |  |
| 370_offer_letter |  |  |  |  |
| 371_experience_certificate |  |  |  |  |
| 372_timesheet_grid |  |  |  |  |
| 373_leave_application_form |  |  |  |  |
| 374_org_chart |  |  |  |  |
| 375_attendance_register |  |  |  |  |
| 37_font_not_embedded_substitution |  |  |  |  |
| 380_runbook_terminal_output |  |  |  |  |
| 381_incident_report_timeline |  |  |  |  |
| 382_architecture_diagram |  |  |  |  |
| 383_api_docs_page |  |  |  |  |
| 38_faux_bold_italic_synthesised |  |  |  |  |
| 390_wide_data_appendix |  |  |  |  |
| 391_survey_questionnaire_grid |  |  |  |  |
| 392_statistical_console_output |  |  |  |  |
| 393_spectrum_peak_table |  |  |  |  |
| 394_map_with_legend |  |  |  |  |
| 39_small_caps_letter_spacing |  |  |  |  |
| 400_comic_page_speech_bubbles |  |  |  |  |
| 401_trifold_brochure |  |  |  |  |
| 402_calendar_month_grid |  |  |  |  |
| 403_crossword_puzzle |  |  |  |  |
| 404_sudoku_grid |  |  |  |  |
| 405_sheet_music_lyrics |  |  |  |  |
| 406_passport_mrz_page |  |  |  |  |
| 407_id_card_front_back |  |  |  |  |
| 40_devanagari_shaping_font |  |  |  |  |
| 410_form_xobject_reused |  |  |  |  |
| 411_nested_xobject_transforms |  |  |  |  |
| 412_page_labels_roman |  |  |  |  |
| 413_tagged_pdf_actualtext |  |  |  |  |
| 414_transparency_softmask |  |  |  |  |
| 415_inline_images |  |  |  |  |
| 416_many_tiny_pages |  |  |  |  |
| 417_rotate180_and_mirrored |  |  |  |  |
| 41_coloured_headings_white_bg |  |  |  |  |
| 42_table_coloured_header_alternating_rows |  |  |  |  |
| 43_red_stamp_over_black_text |  |  |  |  |
| 44_coloured_underlined_hyperlinks |  |  |  |  |
| 45_coloured_callout_box |  |  |  |  |
| 46_chart_coloured_labels_body_text |  |  |  |  |
| 47_grey_body_black_headings |  |  |  |  |
| 48_form_coloured_border_coloured_values |  |  |  |  |
| 49_coloured_background_block_paragraph |  |  |  |  |
| 50_invoice_coloured_total_row |  |  |  |  |
| 51_two_cm_margins |  |  |  |  |
| 52_one_cm_margin_wide_body |  |  |  |  |
| 53_single_space_body_15_headings |  |  |  |  |
| 54_two_column_body_full_width_header_footer |  |  |  |  |
| 55_sidebar_box_beside_body |  |  |  |  |
| 56_table_indented_from_margin |  |  |  |  |
| 57_centred_title_page_left_body_pages |  |  |  |  |
| 58_header_rule_footer_rule |  |  |  |  |
| 59_landscape_mixed_portrait |  |  |  |  |
| 60_page_border |  |  |  |  |
| 61_two_col_abstract_spanning |  |  |  |  |
| 62_two_col_newsletter_pull_quote |  |  |  |  |
| 63_three_column_brochure |  |  |  |  |
| 64_newspaper_uneven_columns_ad_boxes |  |  |  |  |
| 65_two_col_full_width_figure_caption |  |  |  |  |
| 66_two_col_footnotes_bottom |  |  |  |  |
| 67_two_col_with_sidebar |  |  |  |  |
| 68_journal_wide_table_spanning |  |  |  |  |
| 69_two_col_legal_numbered_clauses |  |  |  |  |
| 70_magazine_drop_cap_photo_caption |  |  |  |  |
| 71_invoice_space_aligned_no_rules |  |  |  |  |
| 72_bank_statement_no_rules_right_amounts |  |  |  |  |
| 73_marksheet_subject_marks_grade |  |  |  |  |
| 74_balance_sheet_indented_subitems |  |  |  |  |
| 75_merged_header_cell_three_columns |  |  |  |  |
| 76_devanagari_table |  |  |  |  |
| 77_arabic_rtl_document |  |  |  |  |
| 78_mixed_english_devanagari_line |  |  |  |  |
| 79_inr_indian_digit_grouping_table |  |  |  |  |
| 80_gstin_pan_cin_ifsc_table |  |  |  |  |
| academic-paper-ieee-2col-abstract |  |  |  |  |
| admission-form-labels-left-boxes-right |  |  |  |  |
| admit-card |  |  |  |  |
| annual-review-2col-uneven-columns |  |  |  |  |
| balance-sheet-and-profit-loss |  |  |  |  |
| balance-sheet-two-columns-of-figures |  |  |  |  |
| bank-statement-5-pages |  |  |  |  |
| bank-statement-horizontal-rules-only |  |  |  |  |
| boq-horizontal-rules-only |  |  |  |  |
| boq-tender-bill-of-quantities |  |  |  |  |
| brochure-3col-with-sidebar-box |  |  |  |  |
| bus-timetable-station-left-times-right |  |  |  |  |
| delivery-challan |  |  |  |  |
| electricity-bill |  |  |  |  |
| eway-bill |  |  |  |  |
| form16-part-b |  |  |  |  |
| gst-invoice-3line-items |  |  |  |  |
| gst-invoice-horizontal-rules-only |  |  |  |  |
| gst-invoice-multipage-item-table |  |  |  |  |
| gst-invoice-with-qr-code |  |  |  |  |
| insurance-policy-schedule |  |  |  |  |
| invoice-line-items-qty-rate-amount |  |  |  |  |
| itr-computation-with-slab-table |  |  |  |  |
| journal-2col-with-footnotes |  |  |  |  |
| landscape-page-inside-portrait-document |  |  |  |  |
| magazine-2col-pullquote-spanning |  |  |  |  |
| marksheet-subject-left-marks-right |  |  |  |  |
| marksheet-university-consolidated |  |  |  |  |
| mobile-bill |  |  |  |  |
| mutual-fund-statement |  |  |  |  |
| newsletter-3col-header-footer |  |  |  |  |
| newspaper-2col-fullwidth-headline |  |  |  |  |
| one-page-rotated-180-degrees |  |  |  |  |
| payslip-label-left-amount-right |  |  |  |  |
| policy-2col-spanning-section-heading |  |  |  |  |
| price-list-2col-dense-right-aligned |  |  |  |  |
| price-list-right-aligned-amounts |  |  |  |  |
| product-catalogue-code-left-price-right |  |  |  |  |
| property-tax-receipt |  |  |  |  |
| purchase-order |  |  |  |  |
| question-paper-marks-right-margin |  |  |  |  |
| report-2col-table-spanning-both-columns |  |  |  |  |
| salary-slip-corporate |  |  |  |  |
| salary-slip-factory-wages |  |  |  |  |
| table-across-page-break-repeated-header |  |  |  |  |
| table-inside-two-column-page |  |  |  |  |
| table-of-contents-dot-leaders |  |  |  |  |
| table-with-merged-cells |  |  |  |  |
| table-with-no-header-row |  |  |  |  |
| table-with-rotated-header |  |  |  |  |
| text-held-twice-shadow-text |  |  |  |  |
| two-tables-stacked-with-no-gap |  |  |  |  |
| very-long-single-column-table |  |  |  |  |
