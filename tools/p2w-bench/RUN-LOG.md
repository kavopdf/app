# Run log

One line per stage, written and committed by the baseline cron as it works. It exists
because a run that dies before its first commit leaves no trace: on 11 Nov ten runs in a
row measured ten documents each and committed nothing, and there was no way to tell
whether they died in the conversion, in Drive, in the record step or in the commit
itself. The cron keeps no output of its own, so this file is the only witness.

A stage with no line is a stage that was never reached. That is the answer.

| when | run | stage |
|---|---|---|
| 12 Nov probe | probe | commit test |
| 12 Nov 07:25 | size-probe | testing a 796 KB commit payload |
| 12 Nov 08:02 | baseline | started | phase measure |
| 12 Nov 08:04 | baseline | corpus 208 pdfs unpacked, engine built |
| 12 Nov 08:11 | baseline | 10 documents measured, each committed (56_table_indented_from_margin, 57_centred_title_page_left_body_pages, 58_header_rule_footer_rule, 59_landscape_mixed_portrait, 60_page_border, 61_two_col_abstract_spanning, 62_two_col_newsletter_pull_quote, 63_three_column_brochure, 64_newspaper_uneven_columns_ad_boxes, 65_two_col_full_width_figure_caption) |
| 12 Nov 08:13 | baseline | txt backfill: 10 more documents recorded (01_stamp_rotated_15deg_upright .. 10_stamp_as_image), gap 129 -> 119 |
| 12 Nov 08:13 | baseline | note: pre-existing 'probe-commit-test' text file left in KavoPDF-Verify by an earlier probe run; not created by this run, left in place |
| 12 Nov 08:14 | baseline | ratchet held (docx 140/208 scored, txt 21/208); slot released |
| 12 Nov 09:06 | baseline | started | phase measure |
| 12 Nov 09:45 | baseline | 10 documents measured, each committed (66_two_col_footnotes_bottom, 67_two_col_with_sidebar, 68_journal_wide_table_spanning, 69_two_col_legal_numbered_clauses, 70_magazine_drop_cap_photo_caption, 71_invoice_space_aligned_no_rules, 72_bank_statement_no_rules_right_amounts, 73_marksheet_subject_marks_grade, 74_balance_sheet_indented_subitems, 75_merged_header_cell_three_columns) |
| 12 Nov 09:47 | baseline | txt backfill: 10 more documents recorded (11_stamp_with_signature_image, 12_stamp_across_page_break, 13_stamp_non_english, 14_stamp_chars_positioned_td, 15_stamp_on_scanned_page, 16_right_aligned_amounts_txtpos, 17_three_column_widths_txtpos, 18_centred_heading_left_body_txtpos, 19_hanging_indent_txtpos, 20_numbered_list_separate_column_txtpos), gap 119 -> 109 |
| 12 Nov 09:48 | baseline | ratchet held (docx 150/208 scored, txt 41/208, backfill gap 109); measure gate NOT READY (58 rows unscored); slot released |
| 12 Nov 10:01 | started | phase measure |
| 12 Nov 10:03 | baseline | corpus 208 pdfs, engine built (2a68de6) |
| 12 Nov 10:04 | baseline | measured 76_devanagari_table 45/59 docx, 4/5 txt |
| 12 Nov 10:05 | baseline | measured 77_arabic_rtl_document 36/59 docx, 77_arabic_rtl_document.txt               1/5 FAIL txt |
| 12 Nov 10:05 | baseline | measured 78_mixed_english_devanagari_line 41/59 docx, 78_mixed_english_devanagari_line.txt     4/5 FAIL txt |
| 12 Nov 10:06 | baseline | measured 79_inr_indian_digit_grouping_table 46/59 docx, 79_inr_indian_digit_grouping_table.txt   3/5 FAIL txt |
| 12 Nov 10:06 | baseline | measured 80_gstin_pan_cin_ifsc_table 42/59 docx, 80_gstin_pan_cin_ifsc_table.txt          4/5 FAIL txt |
| 12 Nov 10:07 | baseline | measured academic-paper-ieee-2col-abstract 46/59 docx, academic-paper-ieee-2col-abstract.txt    5/5 PASS txt |
| 12 Nov 10:07 | baseline | measured admission-form-labels-left-boxes-right 46/59 docx, admission-form-labels-left-boxes-right.t 5/5 PASS txt |
| 12 Nov 10:07 | baseline | measured admit-card 46/59 docx, admit-card.txt                           4/5 FAIL txt |
| 12 Nov 10:08 | baseline | measured annual-review-2col-uneven-columns 45/59 docx, annual-review-2col-uneven-columns.txt    5/5 PASS txt |
| 12 Nov 10:08 | baseline | measured balance-sheet-and-profit-loss 39/59 docx, balance-sheet-and-profit-loss.txt        4/5 FAIL txt |
| 12 Nov 10:09 | baseline | txt backfill: 10 more documents recorded (21_form_labels_x60_values_x300_txtpos, 22_invoice_four_columns_txtpos, 23_timetable_grid_txtpos, 24_address_block_indents_txtpos, 25_signature_block_underscores_txtpos, 26_footnote_marker_bottom_note_txtpos, 27_two_column_left_short_txtpos, 28_value_overflows_cell_txtpos, 29_dot_leaders_txtpos, 301_lab_report_panel), gap 109 -> 99 |
