# Census - what was lost, and where

Every document the ranking calls defective, with what the SOURCE holds beside
what the OUTPUT holds. The counts are facts. The `signal` is a candidate
mechanism and it is deliberately conservative: it fires only when the evidence
is unambiguous. `none-identified` means the counts do not point at one cause,
and that is a real answer - a wrong mechanism sends the fixer after a patch
that cannot work.

**62 defective documents censused.**

| signal | documents | total share@5 | worst document |
|---|---|---|---|
| rules-not-tables | 1 | 0.1% | 391_survey_questionnaire_grid 0.1%@5 p1 |
| text-missing | 8 | 25.7% | academic-paper-ieee-2col-abstract 5.7%@5 p2 |
| annotations-present | 1 | 62.5% | 600_reviewed_invoice_with_annotati 62.5%@5 p1 |
| none-identified | 52 | 672.7% | 041122-Account_Opening_Form 98.7%@5 p9 |

## Where the ink went, in points

`dx` positive = the output ink sits right of the source; `dy` positive = below it.
A whole page shifted one way is an offset or margin bug. Signs scattered is a
layout bug. `moved_gt20` is the share of ink that moved more than 20 pt.

| document | share@5 | dx | dy | explains | still >20pt |
|---|---|---|---|---|---|
| 041122-Account_Opening_Form | 98.65 | 38.8 | -36.9 | 1.0 | 70.0% |
| Account_Opening_Form_Fillable_fill | 97.62 | 3.4 | -6.7 | 2.0 | 66.0% |
| one-page-rotated-180-degrees | 81.64 | 0.0 | 0.0 | 0.0 | 23.0% |
| 600_reviewed_invoice_with_annotati | 62.46 | 0.0 | 105.6 | 25.0 | 1.0% |
| 601_fillable_admission_form | 52.39 | 0.0 | 30.2 | 14.0 | 9.0% |
| itr-computation-with-slab-table | 42.33 | 0.0 | 0.5 | 4.0 | 1.0% |
| table-inside-two-column-page | 35.87 | 0.0 | 0.0 | 0.0 | 0.0% |
| 360_restaurant_menu | 34.43 | 0.0 | 0.0 | 0.0 | 3.0% |
| text-held-twice-shadow-text | 30.29 | 0.0 | 0.0 | 0.0 | 28.0% |
| 71_invoice_space_aligned_no_rules | 26.88 | 0.0 | 1.4 | 4.0 | 0.0% |
| 03_stamp_vertical_90deg | 16.98 | 0.0 | 0.0 | 0.0 | 0.0% |
| 68_journal_wide_table_spanning | 12.09 | 0.0 | 0.0 | 0.0 | 0.0% |
| 77_arabic_rtl_document | 11.89 | 0.5 | 0.5 | 16.0 | 0.0% |
| 363_warranty_card | 10.58 | 0.0 | 0.0 | 0.0 | 0.0% |
| 40_devanagari_shaping_font | 10.48 | 0.5 | 0.5 | 7.0 | 0.0% |
| 76_devanagari_table | 7.91 | 0.0 | 0.0 | 0.0 | 0.0% |
| 75_merged_header_cell_three_column | 7.62 | 0.5 | 0.0 | 0.0 | 0.0% |
| journal-2col-with-footnotes | 6.34 | 0.0 | 0.0 | 0.0 | 0.0% |
| 374_org_chart | 5.92 | 0.0 | 0.0 | 0.0 | 0.0% |
| academic-paper-ieee-2col-abstract | 5.66 | 0.0 | 0.1 | 2.0 | 0.0% |
| payslip-label-left-amount-right | 5.59 | 0.0 | 0.0 | 0.0 | 0.0% |
| 417_rotate180_and_mirrored | 5.5 | 0.7 | 0.0 | 3.0 | 0.0% |
| 23_timetable_grid_txtpos | 5.16 | 0.0 | 0.0 | 0.0 | 4.0% |
| table-of-contents-dot-leaders | 4.97 | -0.5 | 0.0 | 1.0 | 0.0% |
| 330_cad_drawing_sheet | 4.91 | 0.0 | 0.0 | 0.0 | 0.0% |
| 33_sans_nondefault_body | 4.49 | 0.0 | 0.0 | 0.0 | 1.0% |
| 14_stamp_chars_positioned_td | 3.89 | 0.0 | 0.0 | 0.0 | 0.0% |
| 64_newspaper_uneven_columns_ad_box | 3.46 | 0.0 | 1.0 | 3.0 | 0.0% |
| 406_passport_mrz_page | 3.45 | 0.0 | 0.0 | 0.0 | 0.0% |
| annual-review-2col-uneven-columns | 3.0 | 0.0 | 0.0 | 0.0 | 0.0% |


## rules-not-tables (1 documents)

| document | share@5 | worst page | src img | docx img | src chars | docx chars | src draws | docx cells |
|---|---|---|---|---|---|---|---|---|
| 391_survey_questionnaire_grid | 0.11 | 1 | 0 | 0 | 556 | 546 | 81 | 0 |

## text-missing (8 documents)

| document | share@5 | worst page | src img | docx img | src chars | docx chars | src draws | docx cells |
|---|---|---|---|---|---|---|---|---|
| academic-paper-ieee-2col-abstract | 5.66 | 2 | 0 | 0 | 6480 | 3410 | 14 | 24 |
| 330_cad_drawing_sheet | 4.91 | 1 | 0 | 0 | 497 | 384 | 113 | 40 |
| 352_certificate_ornate_border | 3.0 | 1 | 1 | 2 | 484 | 409 | 16 | 0 |
| 66_two_col_footnotes_bottom | 2.92 | 1 | 0 | 0 | 1802 | 1325 | 4 | 0 |
| magazine-2col-pullquote-spanning | 2.58 | 1 | 1 | 1 | 2426 | 205 | 4 | 0 |
| 69_two_col_legal_numbered_clauses | 2.53 | 1 | 0 | 0 | 2068 | 665 | 3 | 0 |
| policy-2col-spanning-section-headi | 2.36 | 1 | 0 | 0 | 3384 | 283 | 3 | 0 |
| 65_two_col_full_width_figure_capti | 1.75 | 1 | 0 | 0 | 1932 | 1260 | 49 | 0 |

## annotations-present (1 documents)

| document | share@5 | worst page | src img | docx img | src chars | docx chars | src draws | docx cells |
|---|---|---|---|---|---|---|---|---|
| 600_reviewed_invoice_with_annotati | 62.46 | 1 | 0 | 0 | 776 | 831 | 23 | 50 |

## none-identified (52 documents)

| document | share@5 | worst page | src img | docx img | src chars | docx chars | src draws | docx cells |
|---|---|---|---|---|---|---|---|---|
| 041122-Account_Opening_Form | 98.65 | 9 | 1 | 1 | 48837 | 48623 | 2534 | 659 |
| Account_Opening_Form_Fillable_fill | 97.62 | 7 | 1 | 1 | 48936 | 48702 | 2534 | 659 |
| one-page-rotated-180-degrees | 81.64 | 2 | 0 | 0 | 1951 | 1923 | 42 | 59 |
| 601_fillable_admission_form | 52.39 | 1 | 0 | 0 | 562 | 539 | 13 | 0 |
| itr-computation-with-slab-table | 42.33 | 1 | 0 | 0 | 2041 | 1881 | 61 | 130 |
| table-inside-two-column-page | 35.87 | 1 | 0 | 0 | 2522 | 2333 | 15 | 2 |
| 360_restaurant_menu | 34.43 | 1 | 0 | 0 | 1778 | 2116 | 45 | 82 |
| text-held-twice-shadow-text | 30.29 | 1 | 0 | 0 | 2165 | 2122 | 16 | 28 |
| 71_invoice_space_aligned_no_rules | 26.88 | 1 | 0 | 0 | 1441 | 1464 | 2 | 58 |
| 03_stamp_vertical_90deg | 16.98 | 1 | 0 | 0 | 1611 | 1467 | 23 | 108 |
| 68_journal_wide_table_spanning | 12.09 | 1 | 0 | 0 | 1779 | 1723 | 14 | 49 |
| 77_arabic_rtl_document | 11.89 | 1 | 0 | 0 | 681 | 647 | 16 | 25 |
| 363_warranty_card | 10.58 | 1 | 0 | 0 | 1093 | 1067 | 222 | 16 |
| 40_devanagari_shaping_font | 10.48 | 1 | 0 | 0 | 891 | 865 | 12 | 14 |
| 76_devanagari_table | 7.91 | 1 | 0 | 0 | 919 | 876 | 13 | 30 |
| 75_merged_header_cell_three_column | 7.62 | 1 | 0 | 0 | 743 | 785 | 21 | 48 |
| journal-2col-with-footnotes | 6.34 | 1 | 0 | 0 | 4346 | 4311 | 2 | 0 |
| 374_org_chart | 5.92 | 1 | 0 | 0 | 335 | 338 | 31 | 12 |
| payslip-label-left-amount-right | 5.59 | 1 | 0 | 0 | 1491 | 1407 | 9 | 84 |
| 417_rotate180_and_mirrored | 5.5 | 2 | 0 | 0 | 411 | 403 | 0 | 0 |
| 23_timetable_grid_txtpos | 5.16 | 1 | 0 | 0 | 909 | 847 | 26 | 56 |
| table-of-contents-dot-leaders | 4.97 | 1 | 0 | 0 | 3358 | 3304 | 2 | 0 |
| 33_sans_nondefault_body | 4.49 | 1 | 0 | 0 | 1469 | 1438 | 11 | 18 |
| 14_stamp_chars_positioned_td | 3.89 | 1 | 0 | 0 | 956 | 873 | 14 | 35 |
| 64_newspaper_uneven_columns_ad_box | 3.46 | 1 | 0 | 0 | 2597 | 2805 | 7 | 6 |
| ... 27 more | | | | | | | | |
