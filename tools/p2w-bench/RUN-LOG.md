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
