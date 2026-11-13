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
| 12 Nov 15:09 | baseline | measured table-inside-two-column-page 48/59 docx, 5/5 txt |
| 12 Nov 15:10 | baseline | measured table-inside-two-column-page, table-of-contents-dot-leaders 46/59 docx 4/5 txt |
| 12 Nov 15:10 | baseline | measured table-inside-two-column-page, table-of-contents-dot-leaders, table-with-merged-cells 51/59 docx 4/5 txt |
| 12 Nov 15:11 | baseline | measured table-inside-two-column-page, table-of-contents-dot-leaders, table-with-merged-cells, table-with-no-header-row 54/59 docx 4/5 txt |
| 12 Nov 15:12 | baseline | measured table-inside-two-column-page, table-of-contents-dot-leaders, table-with-merged-cells, table-with-no-header-row, table-with-rotated-header 46/59 docx 4/5 txt |
| 12 Nov 15:12 | baseline | measured table-inside-two-column-page, table-of-contents-dot-leaders, table-with-merged-cells, table-with-no-header-row, table-with-rotated-header, text-held-twice-shadow-text 43/59 docx 4/5 txt |
| 12 Nov 15:13 | baseline | measured table-inside-two-column-page, table-of-contents-dot-leaders, table-with-merged-cells, table-with-no-header-row, table-with-rotated-header, text-held-twice-shadow-text, two-tables-stacked-with-no-gap 54/59 docx 4/5 txt |
| 12 Nov 15:14 | baseline | measured table-inside-two-column-page, table-of-contents-dot-leaders, table-with-merged-cells, table-with-no-header-row, table-with-rotated-header, text-held-twice-shadow-text, two-tables-stacked-with-no-gap, very-long-single-column-table 46/59 docx 4/5 txt |
| 12 Nov 15:15 | baseline | txt backfill: 59 documents recorded (353_admit_card, 35_four_typefaces_one_page, 360_restaurant_menu, 361_product_catalogue_grid, 362_price_list_dense, 363_warranty_card, 364_event_ticket, 365_recipe_card, 36_embedded_subset_font, 370_offer_letter, 371_experience_certificate, 372_timesheet_grid, 373_leave_application_form, 374_org_chart, 375_attendance_register, 37_font_not_embedded_substitution, 380_runbook_terminal_output, 381_incident_report_timeline, 382_architecture_diagram, 383_api_docs_page, 38_faux_bold_italic_synthesised, 390_wide_data_appendix, 391_survey_questionnaire_grid, 392_statistical_console_output, 393_spectrum_peak_table, 394_map_with_legend, 39_small_caps_letter_spacing, 400_comic_page_speech_bubbles, 401_trifold_brochure, 402_calendar_month_grid, 403_crossword_puzzle, 404_sudoku_grid, 405_sheet_music_lyrics, 406_passport_mrz_page, 407_id_card_front_back, 40_devanagari_shaping_font, 410_form_xobject_reused, 411_nested_xobject_transforms, 412_page_labels_roman, 413_tagged_pdf_actualtext, 414_transparency_softmask, 415_inline_images, 416_many_tiny_pages, 417_rotate180_and_mirrored, 41_coloured_headings_white_bg, 42_table_coloured_header_alternating_rows, 43_red_stamp_over_black_text, 44_coloured_underlined_hyperlinks, 45_coloured_callout_box, 46_chart_coloured_labels_body_text, 47_grey_body_black_headings, 48_form_coloured_border_coloured_values, 49_coloured_background_block_paragraph, 50_invoice_coloured_total_row, 51_two_cm_margins, 52_one_cm_margin_wide_body, 53_single_space_body_15_headings, 54_two_column_body_full_width_header_footer, 55_sidebar_box_beside_body), gap 59 -> 0 |
| 12 Nov 15:16 | baseline | ratchet held (docx 208/208 scored, txt 208/208, backfill gap 0); measure gate READY; slot released |
| 12 Nov 15:16 | baseline | phase measure complete - advanced to classify |
| 12 Nov 18:41 | fixer | slot claimed - fixer running |
| 12 Nov 18:52 | fixer | round 1: class 20_within_10pt (+4), 3 probes through Drive confirmed the advance model (240 twips -> 11.5 pt, hairline+226 -> 11.99 pt) |
| 12 Nov 19:21 | fixer | 20 documents through Drive: 3 of 18 moved (62 7->100, balance-sheet 7->53, price-list 1->15), 8 of 20 below baseline; attempt recorded reverted, engine reverted |
| 12 Nov 19:24 | fixer | slot released; class left OPEN with 1 attempt |
| 12 Nov 19:46 | fixer | slot claimed - fixer running |
| 12 Nov 20:29 | fixer | round 1: 53_embedded_faces - extended DocxWriter faceName with a SUBSTITUTE map (Liberation Serif->Times New Roman, Liberation Mono->Courier New, DejaVu Serif->Times New Roman, DejaVu Sans->Verdana); 10 docs through Drive; 53 passed on 2 of 10, kept=0 on the other 8, 317 fell 56->55; engine reverted, RULED OUT recorded |
| 12 Nov 20:43 | fixer | slot claimed - fixer running |
| 12 Nov 21:47 | fixer | slot claimed - fixer running |
| 12 Nov 22:27 | fixer | slot released; 20_within_10pt (+4) left OPEN with 3 attempts. Calibration on 362_price_list_dense, 5 docx variants through Drive, only the table spacer varied: as emitted (w:line=276, mark sz=2) first-row dy -13.59, spacer deleted -16.75, w:line=1 -16.58, w:line=240 auto -14.00, w:before=276 + w:line=1 -2.78 (18_median_dy FAIL->pass, 51/59->53/59). Root cause CONFIRMED: w:line is a multiple of the paragraph mark's line height, so the spacer bought 3.16 pt of the 13.8 asked and every table rose 10.6 pt. Engine fix written and built, then reverted unmeasured: the 20-document Drive round was blocked (every staged upload rejected as expired), so no ratchet evidence existed. Patch kept at patches/table-spacer-before-not-line.patch - one append() in DocxWriter ~line 4157. Recorded 'error'; 2 confirmed hypotheses written; 5 Google Docs deleted |
| 12 Nov 22:46 | fixer | slot claimed - fixer running |
| 12 Nov 23:48 | fixer | slot claimed - fixer running |
| 13 Nov 00:46 | fixer | slot claimed - fixer running |
| 13 Nov 00:53 | fixer | round 1: applied the confirmed table-spacer patch (w:before carries the gap, w:line=1), 20 documents through Drive on 2a68de6-dc3d644: 20_within_10pt FAIL->pass on 362_price_list_dense (51->53) and balance-sheet-two-columns (40->44), 10 controls held; ratchet exit 1 with 4 regressions (362 44_header_footer, 316 59_shape_anchor newly failing; 40_devanagari 37->36, newsletter-3col 40->39), 3 of 18 moved; engine reverted |
| 13 Nov 00:57 | fixer | round 1, second attempt on the same class: refined the spacer patch so a zero scaled gap keeps the shipped shape, engine 2a68de6-d2a3183; 5 affected documents through Drive scored identically to the unrefined build (362 53, 316 55, 40_devanagari 36, newsletter-3col 39, balance-sheet 44) with the same 4 newly failing checks - zero-gap theory ruled out; engine reverted, 30 bench Docs deleted |
| 13 Nov 01:45 | fixer | slot claimed - fixer running |
| 13 Nov 02:18 | fixer | round 1, third attempt on 20_within_10pt (+4): applied the confirmed table-spacer patch AND the untested clamp (spacerTw capped by the page's own baseline arithmetic, (t.top - lastBaseline) - prevLine, when smaller than the flow-model gap), engine 2a68de6-df33807; 5 documents through Drive with Google PDF export: 362_price_list_dense 51->53 (20_within_10pt, 18_median_dy now pass, 44_header_footer newly fails), balance-sheet 40->44 (4 now pass, none newly fail), 40_devanagari 37->37 with NO newly failing check - the clamp removed that regression the unclamped patch had at 36, newsletter-3col 40->39 (14_filled_shapes newly failing), 316 54->55 (59_shape_anchor newly failing). Regressions fell 4->3 but the ratchet would still reject, so engine reverted, attempt recorded reverted (0 of 5 moved engine-relative). Clamp theory RULED OUT; new UNTESTED theory: the remaining three are band-crossing checks, not spacer height. 5 Google Docs deleted. |
| 13 Nov 02:50 | fixer | slot claimed - fixer running |
| 13 Nov 02:50 | fixer | round 1, 47_margins (new class, 0 attempts): diagnosed from the 208 recorded rows, no engine change. 47_margins is ONE element at the page's left edge, not a page shift - 186 rows report render x0=0 while x1 is +3 and y0 is within 10 pt on 178 of 189, and a real 56 pt shift would have moved x1 too. Converted all 208 documents and correlated against the recorded rows: the 12 documents with no table and no drawing reproduce the source's left edge exactly (57/57, 56/56, 28/28, 14/14, 62/62), while 0 of the 192 documents holding a table or a drawing pass. Body-flow placement is exact, so the defect is in the table or drawing emitter. 362_price_list_dense emits w:tblInd=600 (30 pt, equal to the source x0 of 30) and LibreOffice renders it at 30.1 - correct - while Google reports 0, so Google is not honouring tblInd with pgMar left=0. Two confirmed hypotheses and one untested fix written; no patch built and nothing measured on Google, so the attempt is recorded 'error' and the class stays OPEN. Slot released at 03:27, 37 minutes after the claim. |
| 13 Nov 03:44 | fixer | slot claimed - fixer running |
| 13 Nov 04:40 | fixer | slot claimed - fixer running |
| 13 Nov 05:41 | fixer | slot claimed - fixer running |
| 13 Nov 06:47 | fixer | slot claimed - fixer running |
| 13 Nov 06:57 | fixer | slot claimed - fixer running |
| 13 Nov 07:40 | fixer | slot claimed - fixer running |
| 13 Nov 08:40 | fixer | slot claimed - fixer running |
| 13 Nov 09:45 | fixer | slot claimed - fixer running |
| 13 Nov 11:05 | baseline | started | phase measure |
| 13 Nov 11:06 | baseline | slot claimed - baseline running |
| 13 Nov 11:08 | baseline | measured 600_reviewed_invoice_with_annotations 43/59 docx, 4/5 txt |
| 13 Nov 11:09 | baseline | measured 601_fillable_admission_form 44/59 docx, 4/5 txt |
| 13 Nov 11:10 | baseline | measured 602_bookmarked_annual_report 53/59 docx, 4/5 txt |
| 13 Nov 11:11 | baseline | released slot, advanced measure -> classify |
