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
| 12 Nov 10:09 | baseline | ratchet held (docx 160/208 scored, txt 61/208, backfill gap 99); measure gate NOT READY (48 rows unscored); slot released |
| 12 Nov 11:06 | started | phase measure |
| 12 Nov 11:08 | baseline | corpus 208 pdfs, engine built (2a68de6) |
| 12 Nov 11:09 | baseline | measured balance-sheet-two-columns-of-figures 40/59 docx, balance-sheet-two-columns-of-figures.txt 4/5 FAIL txt |
| 12 Nov 11:11 | baseline | measured bank-statement-5-pages 40/59 docx, bank-statement-5-pages.txt 4/5 FAIL txt |
| 12 Nov 11:11 | baseline | measured bank-statement-horizontal-rules-only 42/59 docx, bank-statement-horizontal-rules-only.txt 4/5 FAIL txt |
| 12 Nov 11:12 | baseline | measured boq-horizontal-rules-only 43/59 docx, boq-horizontal-rules-only.txt 4/5 FAIL txt |
| 12 Nov 11:12 | baseline | measured boq-tender-bill-of-quantities 51/59 docx, boq-tender-bill-of-quantities.txt 4/5 FAIL txt |
| 12 Nov 11:13 | baseline | measured brochure-3col-with-sidebar-box 38/59 docx, brochure-3col-with-sidebar-box.txt 4/5 FAIL txt |
| 12 Nov 11:14 | baseline | measured bus-timetable-station-left-times-right 51/59 docx, bus-timetable-station-left-times-right.txt 4/5 FAIL txt |
| 12 Nov 11:14 | baseline | measured delivery-challan 42/59 docx, delivery-challan.txt 4/5 FAIL txt |
| 12 Nov 11:15 | baseline | measured electricity-bill 45/59 docx, electricity-bill.txt 4/5 FAIL txt |
| 12 Nov 11:15 | baseline | measured eway-bill 47/59 docx, eway-bill.txt 4/5 FAIL txt |
| 12 Nov 11:16 | baseline | txt backfill: 10 more documents recorded (302_radiology_report, 303_discharge_summary, 304_package_insert_small_print, 305_vaccination_certificate, 306_clinical_protocol_synopsis, 30_mixed_font_sizes_one_baseline_txtpos, 310_court_judgment, 311_fir_police_form, 312_affidavit_stamp_paper, 313_power_of_attorney), gap 99 -> 89 |
| 12 Nov 11:16 | baseline | ratchet held (docx 170/208 scored, txt 81/208, backfill gap 89); measure gate NOT READY (38 rows unscored); slot released |
| 12 Nov 12:05 | started | phase measure |
| 12 Nov 12:10 | baseline | measured gst-invoice-3line-items 46/59 docx, gst-invoice-3line-items.txt 4/5 txt |
| 12 Nov 12:11 | baseline | measured gst-invoice-horizontal-rules-only 42/59 docx, gst-invoice-horizontal-rules-only.txt 4/5 txt |
| 12 Nov 12:12 | baseline | measured gst-invoice-multipage-item-table 45/59 docx, gst-invoice-multipage-item-table.txt 4/5 txt |
| 12 Nov 12:12 | baseline | measured gst-invoice-with-qr-code 43/59 docx, gst-invoice-with-qr-code.txt 4/5 txt |
| 12 Nov 12:13 | baseline | measured insurance-policy-schedule 48/59 docx, insurance-policy-schedule.txt 4/5 txt |
| 12 Nov 12:13 | baseline | measured invoice-line-items-qty-rate-amount 49/59 docx, invoice-line-items-qty-rate-amount.txt 4/5 txt |
| 12 Nov 12:14 | baseline | measured itr-computation-with-slab-table 43/59 docx, itr-computation-with-slab-table.txt 4/5 txt |
| 12 Nov 12:14 | baseline | measured journal-2col-with-footnotes 43/59 docx, journal-2col-with-footnotes.txt 5/5 txt |
| 12 Nov 12:15 | baseline | measured landscape-page-inside-portrait-document 47/59 docx, landscape-page-inside-portrait-document.txt 4/5 txt |
| 12 Nov 12:16 | baseline | txt backfill: 10 more documents recorded (314_tender_rfp_boq, 315_gazette_notification, 316_contract_with_schedules, 317_rti_response, 318_court_summons_form, 31_times_body_arial_headings, 320_balance_sheet_statutory, 321_auditors_report, 322_mutual_fund_factsheet, 323_credit_card_statement), gap now 79 |
| 12 Nov 12:16 | baseline | ratchet held (docx 180/208 scored, txt 101/208, backfill gap 79); measure gate NOT READY (28 rows unscored); slot released |
| 12 Nov 13:09 | started | phase measure |
| 12 Nov 13:11 | baseline | corpus 208 pdfs, engine built (2a68de6) |
| 12 Nov 13:13 | baseline | measured magazine-2col-pullquote-spanning 36/59 docx, magazine-2col-pullquote-spanning.txt 4/5 txt |
| 12 Nov 13:15 | baseline | measured marksheet-subject-left-marks-right 41/59 docx, marksheet-subject-left-marks-right.txt 4/5 txt |
| 12 Nov 13:15 | baseline | measured marksheet-university-consolidated 49/59 docx, marksheet-university-consolidated.txt 4/5 txt |
| 12 Nov 13:15 | baseline | measured mobile-bill 48/59 docx, mobile-bill.txt 4/5 txt |
| 12 Nov 13:15 | baseline | measured mutual-fund-statement 43/59 docx, mutual-fund-statement.txt 4/5 txt |
| 12 Nov 13:15 | baseline | measured newsletter-3col-header-footer 40/59 docx, newsletter-3col-header-footer.txt 4/5 txt |
| 12 Nov 13:15 | baseline | measured newspaper-2col-fullwidth-headline 37/59 docx, newspaper-2col-fullwidth-headline.txt 4/5 txt |
| 12 Nov 13:16 | baseline | measured one-page-rotated-180-degrees 40/59 docx, one-page-rotated-180-degrees.txt 3/5 txt |
| 12 Nov 13:16 | baseline | measured payslip-label-left-amount-right 37/59 docx, payslip-label-left-amount-right.txt 4/5 txt |
| 12 Nov 13:16 | baseline | measured policy-2col-spanning-section-heading 44/59 docx, policy-2col-spanning-section-heading.txt 3/5 txt |
| 12 Nov 13:18 | baseline | txt backfill: 10 more documents recorded (324_loan_amortisation_schedule, 325_demat_holdings_statement, 326_itr_computation, 32_serif_nondefault_body, 330_cad_drawing_sheet, 331_pid_diagram, 332_bom_on_drawing, 333_datasheet_spec_tables, 334_patent_document, 335_msds_safety_data_sheet), gap 79 -> 69 |
| 12 Nov 13:18 | baseline | ratchet held (docx 190/208 scored, txt 121/208, backfill gap 69); measure gate NOT READY (18 rows unscored); slot released |
| 12 Nov 14:10 | started | phase measure |
| 12 Nov 14:13 | baseline | measured price-list-2col-dense-right-aligned 35/59 docx, 3/5 txt |
| 12 Nov 14:13 | baseline | measured price-list-right-aligned-amounts 38/59 docx, 4/5 txt |
| 12 Nov 14:14 | baseline | measured product-catalogue-code-left-price-right 44/59 docx, 5/5 txt |
| 12 Nov 14:14 | baseline | measured property-tax-receipt 47/59 docx, 4/5 txt |
| 12 Nov 14:15 | baseline | measured purchase-order 44/59 docx, 4/5 txt |
| 12 Nov 14:15 | baseline | measured question-paper-marks-right-margin 47/59 docx, 4/5 txt |
| 12 Nov 14:16 | baseline | measured report-2col-table-spanning-both-columns 48/59 docx, 4/5 txt |
| 12 Nov 14:16 | baseline | measured salary-slip-corporate 39/59 docx, 4/5 txt |
| 12 Nov 14:17 | baseline | measured salary-slip-factory-wages 49/59 docx, 4/5 txt |
| 12 Nov 14:18 | baseline | measured table-across-page-break-repeated-header 49/59 docx, 4/5 txt |
| 12 Nov 14:19 | baseline | txt backfill: 10 more documents recorded (33_sans_nondefault_body, 340_bill_of_lading, 341_shipping_manifest, 342_packing_list, 343_air_waybill, 344_customs_declaration, 34_monospace_document, 350_question_paper, 351_omr_answer_sheet, 352_certificate_ornate_border), gap 69 -> 59 |
| 12 Nov 14:19 | baseline | ratchet held (docx 200/208 scored, txt 141/208, backfill gap 59); measure gate NOT READY (8 rows unscored); slot released |
| 12 Nov 15:05 | started | phase measure |
