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
