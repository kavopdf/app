# Google-render baseline

Every document, measured by `verify_google.py` against the PDF that Google Docs
itself exports. A document passes only when all 31 checks pass.

The instrument: the docx goes to Drive, Drive converts it to a Google Doc, that
document is exported as PDF, and the export is compared to the original. See
`VERIFY-GOOGLE.md` for the pipeline and `verify_google.py` for the checks.

Newest rows were measured with engine **3651553** (v3.53.12). Every row carries the commit it
was measured with, because a score without a commit cannot tell a fix from a stale build.

This file is written by the hourly baseline cron. Rows are never deleted; a
re-run of a document replaces its own row.

A verdict of **CLOSED-UNFIXABLE** marks a document whose remaining failure is class
`20_within_10pt`, closed on 10 Nov: Google Docs has no exact line spacing, so it re-reads
`w:line` as a multiple of the paragraph mark's natural line height and no line box can be
placed where the page drew it. The measurement and the proof are in `REMAINING-DEFECTS.md`
under "Class 20_within_10pt — CLOSED UNFIXABLE". The score and the failed checks are left
as measured; only the verdict is closed.

| document | score | verdict | failed checks | engine | measured |
|---|---|---|---|---|---|
| 01_stamp_rotated_15deg_upright | 15/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 07_table_rows, 09_font_names, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 25_invisible_text, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 02_stamp_rotated_15deg_upleft | 21/31 | REOPENED | 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 19_worst_dy, 20_within_10pt, 22_reading_order, 25_invisible_text, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 03_stamp_vertical_90deg | 13/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 11_bold_runs, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 04_stamp_180deg_upside_down | 11/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 06_table_columns, 07_table_rows, 09_font_names, 11_bold_runs, 16_numeric_runs, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 25_invisible_text, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 05_round_company_seal_curved_text | 13/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 06_table_columns, 07_table_rows, 09_font_names, 11_bold_runs, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 06_rect_paid_stamp_red_transparent | 15/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 16_numeric_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 26_text_overlap, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 07_stamp_over_table | 14/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 08_two_overlapping_stamps | 14/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 07_table_rows, 11_bold_runs, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 25_invisible_text, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 09_stamp_font_not_embedded | 22/31 | REOPENED | 03_word_count, 04_words_missing, 09_font_names, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 10_stamp_as_image | 14/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 07_table_rows, 16_numeric_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 25_invisible_text, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 11_stamp_with_signature_image | 20/31 | REOPENED | 03_word_count, 04_words_missing, 09_font_names, 11_bold_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 12_stamp_across_page_break | 17/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 07_table_rows, 11_bold_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 13_stamp_non_english | 22/31 | REOPENED | 03_word_count, 04_words_missing, 09_font_names, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 14_stamp_chars_positioned_td | 23/31 | REOPENED | 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 18_median_dy, 20_within_10pt, 22_reading_order, 25_invisible_text — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 15_stamp_on_scanned_page | 21/31 | REOPENED | 03_word_count, 04_words_missing, 09_font_names, 10_font_sizes, 13_text_colours, 17_matched_runs, 20_within_10pt, 22_reading_order, 23_line_pitch, 31_pages_lost_their_text — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 16_right_aligned_amounts_txtpos | 15/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 17_three_column_widths_txtpos | 21/31 | REOPENED | 02_text_run_count, 07_table_rows, 09_font_names, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 26_text_overlap, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 18_centred_heading_left_body_txtpos | 30/31 | FAIL | 18_median_dy | 2a68de6 | 2026-11-10 |
| 19_hanging_indent_txtpos | 29/31 | FAIL | 09_font_names, 23_line_pitch | 2a68de6 | 2026-11-10 |
| 20_numbered_list_separate_column_txtpos | 25/31 | REOPENED | 09_font_names, 19_worst_dy, 20_within_10pt, 22_reading_order, 26_text_overlap, 29_blank_where_ink_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 21_form_labels_x60_values_x300_txtpos | 20/31 | REOPENED | 01_page_count, 07_table_rows, 09_font_names, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 22_invoice_four_columns_txtpos | 15/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 23_timetable_grid_txtpos | 23/31 | REOPENED | 09_font_names, 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 24_address_block_indents_txtpos | 25/31 | REOPENED | 09_font_names, 18_median_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 25_signature_block_underscores_txtpos | 16/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 27_text_off_page, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 26_footnote_marker_bottom_note_txtpos | 27/31 | REOPENED | 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 27_two_column_left_short_txtpos | 29/31 | REOPENED | 19_worst_dy, 20_within_10pt — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 28_value_overflows_cell_txtpos | 20/31 | REOPENED | 02_text_run_count, 06_table_columns, 07_table_rows, 09_font_names, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 29_dot_leaders_txtpos | 16/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 06_table_columns, 09_font_names, 16_numeric_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 27_text_off_page, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 300_prescription_rx | 18/31 | REOPENED | 01_page_count, 03_word_count, 04_words_missing, 05_words_extra, 14_filled_shapes, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 25_invisible_text, 26_text_overlap, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 301_lab_report_panel | 23/31 | REOPENED | 01_page_count, 02_text_run_count, 14_filled_shapes, 20_within_10pt, 22_reading_order, 24_page_breaks, 25_invisible_text, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 302_radiology_report | 25/31 | REOPENED | 03_word_count, 04_words_missing, 05_words_extra, 19_worst_dy, 20_within_10pt, 22_reading_order — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 303_discharge_summary | 20/31 | REOPENED | 02_text_run_count, 05_words_extra, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 25_invisible_text, 26_text_overlap, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 304_package_insert_small_print | 26/31 | REOPENED | 10_font_sizes, 19_worst_dy, 20_within_10pt, 23_line_pitch, 26_text_overlap — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 305_vaccination_certificate | 18/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 06_table_columns, 07_table_rows, 11_bold_runs, 14_filled_shapes, 17_matched_runs, 22_reading_order, 23_line_pitch, 24_page_breaks, 29_blank_where_ink_was | 2a68de6 | 2026-11-10 |
| 306_clinical_protocol_synopsis | 26/31 | REOPENED | 19_worst_dy, 20_within_10pt, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 30_mixed_font_sizes_one_baseline_txtpos | 14/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 06_table_columns, 07_table_rows, 09_font_names, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 310_court_judgment | 28/31 | FAIL | 03_word_count, 04_words_missing, 22_reading_order | 2a68de6 | 2026-11-10 |
| 311_fir_police_form | 24/31 | REOPENED | 03_word_count, 04_words_missing, 19_worst_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 312_affidavit_stamp_paper | 19/31 | REOPENED | 02_text_run_count, 03_word_count, 04_words_missing, 06_table_columns, 07_table_rows, 11_bold_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was — Google Docs has no exact line spacing, so no line box is honoured | 2a68de6 | 2026-11-10 |
| 313_power_of_attorney | 30/31 | FAIL | 18_median_dy | 2a68de6 | 2026-11-10 |
| 314_tender_rfp_boq | 27/31 | REOPENED | 19_worst_dy, 20_within_10pt, 25_invisible_text, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 315_gazette_notification | 26/31 | REOPENED | 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 26_text_overlap — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 316_contract_with_schedules | 29/31 | REOPENED | 19_worst_dy, 20_within_10pt — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 317_rti_response | 31/31 | PASS |  | a927365 | 2026-11-10 |
| 318_court_summons_form | 19/31 | REOPENED | 02_text_run_count, 03_word_count, 04_words_missing, 06_table_columns, 07_table_rows, 11_bold_runs, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 31_times_body_arial_headings | 28/31 | REOPENED | 19_worst_dy, 20_within_10pt, 22_reading_order — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 320_balance_sheet_statutory | 27/31 | REOPENED | 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 321_auditors_report | 29/31 | REOPENED | 19_worst_dy, 20_within_10pt — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 322_mutual_fund_factsheet | 19/31 | REOPENED | 02_text_run_count, 03_word_count, 04_words_missing, 11_bold_runs, 14_filled_shapes, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 323_credit_card_statement | 19/31 | REOPENED | 01_page_count, 03_word_count, 04_words_missing, 14_filled_shapes, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 324_loan_amortisation_schedule | 25/31 | REOPENED | 06_table_columns, 07_table_rows, 19_worst_dy, 20_within_10pt, 23_line_pitch, 25_invisible_text — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 325_demat_holdings_statement | 27/31 | FAIL | 02_text_run_count, 06_table_columns, 22_reading_order, 25_invisible_text | a927365 | 2026-11-10 |
| 326_itr_computation | 21/31 | REOPENED | 01_page_count, 02_text_run_count, 07_table_rows, 14_filled_shapes, 18_median_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 25_invisible_text, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 32_serif_nondefault_body | 26/31 | REOPENED | 18_median_dy, 19_worst_dy, 20_within_10pt, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 330_cad_drawing_sheet | 23/31 | REOPENED | 03_word_count, 04_words_missing, 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 331_pid_diagram | 20/31 | FAIL | 02_text_run_count, 03_word_count, 04_words_missing, 06_table_columns, 10_font_sizes, 11_bold_runs, 16_numeric_runs, 17_matched_runs, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was | a927365 | 2026-11-10 |
| 332_bom_on_drawing | 25/31 | REOPENED | 19_worst_dy, 20_within_10pt, 22_reading_order, 26_text_overlap, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 333_datasheet_spec_tables | 24/31 | REOPENED | 01_page_count, 19_worst_dy, 20_within_10pt, 24_page_breaks, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 334_patent_document | 24/31 | FAIL | 02_text_run_count, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 335_msds_safety_data_sheet | 24/31 | REOPENED | 02_text_run_count, 19_worst_dy, 20_within_10pt, 22_reading_order, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | a927365 | 2026-11-10 |
| 33_sans_nondefault_body | 29/31 | REOPENED | 20_within_10pt, 22_reading_order — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 340_bill_of_lading | 21/31 | REOPENED | 02_text_run_count, 07_table_rows, 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 26_text_overlap, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 341_shipping_manifest | 25/31 | REOPENED | 01_page_count, 19_worst_dy, 20_within_10pt, 24_page_breaks, 25_invisible_text, 29_blank_where_ink_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 342_packing_list | 21/31 | REOPENED | 03_word_count, 04_words_missing, 05_words_extra, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 25_invisible_text, 26_text_overlap, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 343_air_waybill | 19/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 07_table_rows, 14_filled_shapes, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 344_customs_declaration | 24/31 | REOPENED | 03_word_count, 04_words_missing, 19_worst_dy, 20_within_10pt, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 34_monospace_document | 29/31 | FAIL | 19_worst_dy, 20_within_10pt | 3651553 | 2026-11-10 |
| 350_question_paper | 13/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 06_table_columns, 07_table_rows, 16_numeric_runs, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 26_text_overlap, 27_text_off_page, 28_clipped_at_edge, 29_blank_where_ink_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 351_omr_answer_sheet | 25/31 | REOPENED | 01_page_count, 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 352_certificate_ornate_border | 14/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 06_table_columns, 07_table_rows, 11_bold_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 353_admit_card | 21/31 | REOPENED | 02_text_run_count, 11_bold_runs, 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 35_four_typefaces_one_page | 30/31 | FAIL | 22_reading_order | 392ce95 | 2026-11-10 |
| 360_restaurant_menu | 22/31 | REOPENED | 02_text_run_count, 06_table_columns, 14_filled_shapes, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 361_product_catalogue_grid | 28/31 | FAIL | 14_filled_shapes, 19_worst_dy, 25_invisible_text | 392ce95 | 2026-11-10 |
| 362_price_list_dense | 27/31 | REOPENED | 03_word_count, 04_words_missing, 20_within_10pt, 22_reading_order — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 363_warranty_card | 26/31 | REOPENED | 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 364_event_ticket | 22/31 | REOPENED | 03_word_count, 04_words_missing, 14_filled_shapes, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 25_invisible_text — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 365_recipe_card | 27/31 | REOPENED | 18_median_dy, 19_worst_dy, 20_within_10pt, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 36_embedded_subset_font | 20/31 | REOPENED | 01_page_count, 02_text_run_count, 07_table_rows, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 27_text_off_page, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 370_offer_letter | 26/31 | REOPENED | 02_text_run_count, 19_worst_dy, 20_within_10pt, 22_reading_order, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | 392ce95 | 2026-11-10 |
| 371_experience_certificate | 20/31 | FAIL | 02_text_run_count, 03_word_count, 04_words_missing, 06_table_columns, 07_table_rows, 11_bold_runs, 17_matched_runs, 18_median_dy, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was | c2616d5 | 2026-11-10 |
| 372_timesheet_grid | 27/31 | REOPENED | 19_worst_dy, 20_within_10pt, 25_invisible_text, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 373_leave_application_form | 22/31 | REOPENED | 02_text_run_count, 07_table_rows, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 26_text_overlap, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 374_org_chart | 20/31 | REOPENED | 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 375_attendance_register | 24/31 | REOPENED | 01_page_count, 19_worst_dy, 20_within_10pt, 21_median_dx, 24_page_breaks, 25_invisible_text, 29_blank_where_ink_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 37_font_not_embedded_substitution | 31/31 | PASS |  | c2616d5 | 2026-11-10 |
| 380_runbook_terminal_output | 27/31 | REOPENED | 14_filled_shapes, 19_worst_dy, 20_within_10pt, 25_invisible_text — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 381_incident_report_timeline | 24/31 | REOPENED | 02_text_run_count, 19_worst_dy, 20_within_10pt, 22_reading_order, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 382_architecture_diagram | 24/31 | REOPENED | 02_text_run_count, 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 383_api_docs_page | 26/31 | REOPENED | 14_filled_shapes, 19_worst_dy, 20_within_10pt, 25_invisible_text, 26_text_overlap — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 38_faux_bold_italic_synthesised | 16/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 390_wide_data_appendix | 26/31 | REOPENED | 01_page_count, 19_worst_dy, 20_within_10pt, 24_page_breaks, 25_invisible_text — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 391_survey_questionnaire_grid | 23/31 | REOPENED | 03_word_count, 04_words_missing, 05_words_extra, 11_bold_runs, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 392_statistical_console_output | 26/31 | REOPENED | 03_word_count, 04_words_missing, 19_worst_dy, 20_within_10pt, 23_line_pitch — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 393_spectrum_peak_table | 27/31 | REOPENED | 19_worst_dy, 20_within_10pt, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 394_map_with_legend | 24/31 | REOPENED | 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 39_small_caps_letter_spacing | 19/31 | REOPENED | 03_word_count, 04_words_missing, 06_table_columns, 07_table_rows, 10_font_sizes, 11_bold_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 400_comic_page_speech_bubbles | 21/31 | REOPENED | 02_text_run_count, 07_table_rows, 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 26_text_overlap, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 401_trifold_brochure | 15/31 | REOPENED | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 07_table_rows, 14_filled_shapes, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 21_median_dx, 22_reading_order, 23_line_pitch, 24_page_breaks, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 402_calendar_month_grid | 20/31 | REOPENED | 01_page_count, 02_text_run_count, 13_text_colours, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 29_blank_where_ink_was, 30_ink_where_blank_was — Google Docs has no exact line spacing, so no line box is honoured | c2616d5 | 2026-11-10 |
| 403_crossword_puzzle | 24/31 | FAIL | 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 404_sudoku_grid | 23/31 | FAIL | 01_page_count, 18_median_dy, 19_worst_dy, 20_within_10pt, 23_line_pitch, 24_page_breaks, 29_blank_where_ink_was, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 405_sheet_music_lyrics | 17/31 | FAIL | 01_page_count, 02_text_run_count, 06_table_columns, 07_table_rows, 14_filled_shapes, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 406_passport_mrz_page | 25/31 | FAIL | 03_word_count, 04_words_missing, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch | f679dde | 2026-11-10 |
| 407_id_card_front_back | 27/31 | FAIL | 14_filled_shapes, 19_worst_dy, 20_within_10pt, 23_line_pitch | f679dde | 2026-11-10 |
| 40_devanagari_shaping_font | 14/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 06_table_columns, 07_table_rows, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was | f679dde | 2026-11-10 |
| 410_form_xobject_reused | 27/31 | FAIL | 19_worst_dy, 20_within_10pt, 29_blank_where_ink_was, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 411_nested_xobject_transforms | 24/31 | FAIL | 03_word_count, 04_words_missing, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch | f679dde | 2026-11-10 |
| 412_page_labels_roman | 27/31 | FAIL | 19_worst_dy, 20_within_10pt, 23_line_pitch, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 413_tagged_pdf_actualtext | 31/31 | PASS | — | f679dde | 2026-11-10 |
| 414_transparency_softmask | 29/31 | FAIL | 19_worst_dy, 20_within_10pt | f679dde | 2026-11-10 |
| 415_inline_images | 29/31 | FAIL | 19_worst_dy, 20_within_10pt | f679dde | 2026-11-10 |
| 416_many_tiny_pages | 26/31 | FAIL | 19_worst_dy, 20_within_10pt, 23_line_pitch, 29_blank_where_ink_was, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 417_rotate180_and_mirrored | 22/31 | FAIL | 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 17_matched_runs, 18_median_dy, 20_within_10pt, 22_reading_order, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 41_coloured_headings_white_bg | 15/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 42_table_coloured_header_alternating_rows | 15/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 16_numeric_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 24_page_breaks, 25_invisible_text, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 43_red_stamp_over_black_text | 21/31 | FAIL | 03_word_count, 04_words_missing, 07_table_rows, 09_font_names, 11_bold_runs, 17_matched_runs, 18_median_dy, 20_within_10pt, 22_reading_order, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 44_coloured_underlined_hyperlinks | 23/31 | FAIL | 02_text_run_count, 07_table_rows, 09_font_names, 15_links, 18_median_dy, 20_within_10pt, 22_reading_order, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 45_coloured_callout_box | 30/31 | FAIL | 09_font_names | f679dde | 2026-11-10 |
| 46_chart_coloured_labels_body_text | 22/31 | FAIL | 02_text_run_count, 07_table_rows, 09_font_names, 14_filled_shapes, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 30_ink_where_blank_was | f679dde | 2026-11-10 |
| 47_grey_body_black_headings | 26/31 | FAIL | 09_font_names, 18_median_dy, 20_within_10pt, 23_line_pitch, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 48_form_coloured_border_coloured_values | 22/31 | FAIL | 02_text_run_count, 07_table_rows, 09_font_names, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 49_coloured_background_block_paragraph | 30/31 | FAIL | 09_font_names | 3651553 | 2026-11-10 |
| 50_invoice_coloured_total_row | 13/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 09_font_names, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 25_invisible_text, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 51_two_cm_margins | 29/31 | FAIL | 09_font_names, 20_within_10pt | 3651553 | 2026-11-10 |
| 52_one_cm_margin_wide_body | 16/31 | FAIL | 02_text_run_count, 03_word_count, 04_words_missing, 05_words_extra, 06_table_columns, 09_font_names, 16_numeric_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 53_single_space_body_15_headings | 27/31 | FAIL | 09_font_names, 18_median_dy, 20_within_10pt, 26_text_overlap | 3651553 | 2026-11-10 |
| 54_two_column_body_full_width_header_footer | 26/31 | FAIL | 03_word_count, 04_words_missing, 09_font_names, 22_reading_order, 25_invisible_text | 3651553 | 2026-11-10 |
| 55_sidebar_box_beside_body | 20/31 | FAIL | 02_text_run_count, 03_word_count, 04_words_missing, 09_font_names, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 26_text_overlap, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 56_table_indented_from_margin | 24/31 | FAIL | 02_text_run_count, 09_font_names, 19_worst_dy, 20_within_10pt, 22_reading_order, 29_blank_where_ink_was, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 57_centred_title_page_left_body_pages | 25/31 | FAIL | 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 29_blank_where_ink_was, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 58_header_rule_footer_rule | 23/31 | FAIL | 02_text_run_count, 07_table_rows, 19_worst_dy, 20_within_10pt, 22_reading_order, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 59_landscape_mixed_portrait | 16/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 09_font_names, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 60_page_border | 13/31 | FAIL | 01_page_count, 02_text_run_count, 03_word_count, 04_words_missing, 06_table_columns, 07_table_rows, 09_font_names, 11_bold_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 27_text_off_page, 29_blank_where_ink_was, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 61_two_col_abstract_spanning | 25/31 | FAIL | 02_text_run_count, 03_word_count, 04_words_missing, 19_worst_dy, 20_within_10pt, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 62_two_col_newsletter_pull_quote | 18/31 | FAIL | 02_text_run_count, 03_word_count, 04_words_missing, 07_table_rows, 12_italic_runs, 17_matched_runs, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 63_three_column_brochure | 21/31 | FAIL | 02_text_run_count, 09_font_names, 18_median_dy, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 25_invisible_text, 29_blank_where_ink_was, 30_ink_where_blank_was | 3651553 | 2026-11-10 |
| 64_newspaper_uneven_columns_ad_boxes | 21/31 | FAIL | 01_page_count, 09_font_names, 11_bold_runs, 17_matched_runs, 19_worst_dy, 20_within_10pt, 22_reading_order, 23_line_pitch, 24_page_breaks, 29_blank_where_ink_was | 3651553 | 2026-11-10 |
| 65_two_col_full_width_figure_caption |  |  |  |  |  |
| 66_two_col_footnotes_bottom |  |  |  |  |  |
| 67_two_col_with_sidebar |  |  |  |  |  |
| 68_journal_wide_table_spanning |  |  |  |  |  |
| 69_two_col_legal_numbered_clauses |  |  |  |  |  |
| 70_magazine_drop_cap_photo_caption |  |  |  |  |  |
| 71_invoice_space_aligned_no_rules |  |  |  |  |  |
| 72_bank_statement_no_rules_right_amounts |  |  |  |  |  |
| 73_marksheet_subject_marks_grade |  |  |  |  |  |
| 74_balance_sheet_indented_subitems |  |  |  |  |  |
| 75_merged_header_cell_three_columns |  |  |  |  |  |
| 76_devanagari_table |  |  |  |  |  |
| 77_arabic_rtl_document |  |  |  |  |  |
| 78_mixed_english_devanagari_line |  |  |  |  |  |
| 79_inr_indian_digit_grouping_table |  |  |  |  |  |
| 80_gstin_pan_cin_ifsc_table |  |  |  |  |  |
| academic-paper-ieee-2col-abstract |  |  |  |  |  |
| admission-form-labels-left-boxes-right |  |  |  |  |  |
| admit-card |  |  |  |  |  |
| annual-review-2col-uneven-columns |  |  |  |  |  |
| balance-sheet-and-profit-loss |  |  |  |  |  |
| balance-sheet-two-columns-of-figures |  |  |  |  |  |
| bank-statement-5-pages |  |  |  |  |  |
| bank-statement-horizontal-rules-only |  |  |  |  |  |
| boq-horizontal-rules-only |  |  |  |  |  |
| boq-tender-bill-of-quantities |  |  |  |  |  |
| brochure-3col-with-sidebar-box |  |  |  |  |  |
| bus-timetable-station-left-times-right |  |  |  |  |  |
| delivery-challan |  |  |  |  |  |
| electricity-bill |  |  |  |  |  |
| eway-bill |  |  |  |  |  |
| form16-part-b |  |  |  |  |  |
| gst-invoice-3line-items |  |  |  |  |  |
| gst-invoice-horizontal-rules-only |  |  |  |  |  |
| gst-invoice-multipage-item-table |  |  |  |  |  |
| gst-invoice-with-qr-code |  |  |  |  |  |
| insurance-policy-schedule |  |  |  |  |  |
| invoice-line-items-qty-rate-amount |  |  |  |  |  |
| itr-computation-with-slab-table |  |  |  |  |  |
| journal-2col-with-footnotes |  |  |  |  |  |
| landscape-page-inside-portrait-document |  |  |  |  |  |
| magazine-2col-pullquote-spanning |  |  |  |  |  |
| marksheet-subject-left-marks-right |  |  |  |  |  |
| marksheet-university-consolidated |  |  |  |  |  |
| mobile-bill |  |  |  |  |  |
| mutual-fund-statement |  |  |  |  |  |
| newsletter-3col-header-footer |  |  |  |  |  |
| newspaper-2col-fullwidth-headline |  |  |  |  |  |
| one-page-rotated-180-degrees |  |  |  |  |  |
| payslip-label-left-amount-right |  |  |  |  |  |
| policy-2col-spanning-section-heading |  |  |  |  |  |
| price-list-2col-dense-right-aligned |  |  |  |  |  |
| price-list-right-aligned-amounts |  |  |  |  |  |
| product-catalogue-code-left-price-right |  |  |  |  |  |
| property-tax-receipt |  |  |  |  |  |
| purchase-order |  |  |  |  |  |
| question-paper-marks-right-margin |  |  |  |  |  |
| report-2col-table-spanning-both-columns |  |  |  |  |  |
| salary-slip-corporate |  |  |  |  |  |
| salary-slip-factory-wages |  |  |  |  |  |
| table-across-page-break-repeated-header |  |  |  |  |  |
| table-inside-two-column-page |  |  |  |  |  |
| table-of-contents-dot-leaders |  |  |  |  |  |
| table-with-merged-cells |  |  |  |  |  |
| table-with-no-header-row |  |  |  |  |  |
| table-with-rotated-header |  |  |  |  |  |
| text-held-twice-shadow-text |  |  |  |  |  |
| two-tables-stacked-with-no-gap |  |  |  |  |  |
| very-long-single-column-table |  |  |  |  |  |
## Reopened 2026-11-10

90 rows were marked CLOSED-UNFIXABLE, most of them on the single claim that Google Docs has
no exact line spacing. That claim was tested and is false. Documents written with `w:line`
at 240, 360 and 480 twips came back from Drive at 11.3, 17.1 and 22.8 pt: proportional,
monotonic, honoured, at about 95 % of the value asked. The classes are open again.

`20_within_10pt` alone touches 36 of the first 41 documents measured, so this is the largest
open class in the corpus. The measurement lives in `calibrate.py`; the fix it implies is a
multiplier of 1/0.95 where the engine writes the line height.
