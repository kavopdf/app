# Census - what was lost, and where

Every document the ranking calls defective, with what the SOURCE holds beside
what the OUTPUT holds. The counts are facts. The `signal` is a candidate
mechanism and it is deliberately conservative: it fires only when the evidence
is unambiguous. `none-identified` means the counts do not point at one cause,
and that is a real answer - a wrong mechanism sends the fixer after a patch
that cannot work.

**117 defective documents censused.**

| signal | documents | total share@5 | worst document |
|---|---|---|---|
| images-mostly-missing | 1 | 98.2% | Prakashan_Print_Fidelity_Handbook 98.2%@5 p9 |
| rules-not-tables | 1 | 0.1% | 391_survey_questionnaire_grid 0.1%@5 p1 |
| text-missing | 12 | 45.4% | table-with-rotated-header 9.6%@5 p1 |
| annotations-present | 1 | 61.9% | 600_reviewed_invoice_with_annotati 61.9%@5 p1 |
| none-identified | 102 | 1413.1% | 041122-Account_Opening_Form 98.7%@5 p9 |

## Where the ink went, in points

`dx` positive = the output ink sits right of the source; `dy` positive = below it.
A whole page shifted one way is an offset or margin bug. Signs scattered is a
layout bug. `moved_gt20` is the share of ink that moved more than 20 pt.

| document | share@5 | dx | dy | explains | still >20pt |
|---|---|---|---|---|---|
| 041122-Account_Opening_Form | 98.65 | 38.6 | -39.8 | 1.0 | 70.0% |
| Prakashan_Print_Fidelity_Handbook | 98.19 | -0.1 | 11.5 | 0.0 | 27.0% |
| Account_Opening_Form_Fillable_fill | 97.62 | 3.1 | -17.8 | 2.0 | 66.0% |
| one-page-rotated-180-degrees | 81.64 | 0.0 | 0.0 | 0.0 | 23.0% |
| 600_reviewed_invoice_with_annotati | 61.86 | 0.0 | 102.2 | 22.0 | 1.0% |
| 601_fillable_admission_form | 52.39 | 0.0 | 26.9 | 15.0 | 8.0% |
| 360_restaurant_menu | 50.18 | 0.0 | 0.0 | 0.0 | 16.0% |
| table-with-no-header-row | 47.48 | 0.0 | 0.0 | 0.0 | 0.0% |
| boq-tender-bill-of-quantities | 41.95 | 0.5 | 0.0 | 1.0 | 0.0% |
| very-long-single-column-table | 41.14 | 0.0 | 0.0 | 0.0 | 0.0% |
| itr-computation-with-slab-table | 38.49 | 0.0 | 0.0 | 0.0 | 0.0% |
| electricity-bill | 36.78 | 0.0 | -1.4 | 1.0 | 0.0% |
| balance-sheet-and-profit-loss | 36.69 | 0.0 | 0.0 | 0.0 | 0.0% |
| salary-slip-factory-wages | 35.15 | 0.0 | 0.0 | 0.0 | 0.0% |
| 03_stamp_vertical_90deg | 34.38 | 0.0 | 0.0 | 0.0 | 0.0% |
| table-across-page-break-repeated-h | 33.52 | 0.0 | 0.0 | 0.0 | 0.0% |
| table-inside-two-column-page | 30.72 | 0.0 | 0.0 | 0.0 | 0.0% |
| mobile-bill | 30.09 | 0.0 | 0.0 | 0.0 | 0.0% |
| text-held-twice-shadow-text | 29.15 | 0.0 | 0.0 | 0.0 | 28.0% |
| price-list-2col-dense-right-aligne | 27.89 | 0.0 | 0.0 | 0.0 | 0.0% |
| mutual-fund-statement | 27.8 | 0.0 | 0.0 | 0.0 | 0.0% |
| property-tax-receipt | 27.45 | 0.0 | 0.0 | 0.0 | 0.0% |
| marksheet-university-consolidated | 27.14 | 0.0 | 0.0 | 0.0 | 0.0% |
| 71_invoice_space_aligned_no_rules | 26.99 | 0.0 | 3.4 | 5.0 | 0.0% |
| 75_merged_header_cell_three_column | 26.77 | 0.0 | 0.0 | 0.0 | 0.0% |
| form16-part-b | 26.45 | 0.0 | 0.0 | 0.0 | 0.0% |
| insurance-policy-schedule | 22.66 | 0.0 | 0.0 | 0.0 | 0.0% |
| two-tables-stacked-with-no-gap | 21.93 | 0.0 | 0.0 | 0.0 | 0.0% |
| purchase-order | 14.34 | 0.0 | 0.0 | 0.0 | 0.0% |
| bank-statement-5-pages | 14.14 | 0.0 | 0.0 | 0.0 | 0.0% |


## images-mostly-missing (1 documents)

| document | share@5 | worst page | src img | docx img | src chars | docx chars | src draws | docx cells |
|---|---|---|---|---|---|---|---|---|
| Prakashan_Print_Fidelity_Handbook | 98.19 | 9 | 300 | 33 | 23231 | 10995 | 1280 | 316 |

## rules-not-tables (1 documents)

| document | share@5 | worst page | src img | docx img | src chars | docx chars | src draws | docx cells |
|---|---|---|---|---|---|---|---|---|
| 391_survey_questionnaire_grid | 0.11 | 1 | 0 | 0 | 556 | 546 | 81 | 0 |

## text-missing (12 documents)

| document | share@5 | worst page | src img | docx img | src chars | docx chars | src draws | docx cells |
|---|---|---|---|---|---|---|---|---|
| table-with-rotated-header | 9.56 | 1 | 0 | 0 | 1080 | 851 | 30 | 143 |
| academic-paper-ieee-2col-abstract | 5.92 | 2 | 0 | 0 | 6480 | 3410 | 14 | 24 |
| 311_fir_police_form | 5.59 | 1 | 0 | 0 | 1417 | 1139 | 62 | 60 |
| 330_cad_drawing_sheet | 4.91 | 1 | 0 | 0 | 497 | 384 | 113 | 40 |
| 390_wide_data_appendix | 3.23 | 1 | 0 | 0 | 2579 | 2176 | 400 | 399 |
| 352_certificate_ornate_border | 3.0 | 1 | 1 | 2 | 484 | 409 | 16 | 0 |
| 66_two_col_footnotes_bottom | 2.92 | 1 | 0 | 0 | 1802 | 1325 | 4 | 0 |
| magazine-2col-pullquote-spanning | 2.58 | 1 | 1 | 1 | 2426 | 205 | 4 | 0 |
| 69_two_col_legal_numbered_clauses | 2.53 | 1 | 0 | 0 | 2068 | 665 | 3 | 0 |
| policy-2col-spanning-section-headi | 2.36 | 1 | 0 | 0 | 3384 | 283 | 3 | 0 |
| 65_two_col_full_width_figure_capti | 1.75 | 1 | 0 | 0 | 1932 | 1260 | 49 | 0 |
| 375_attendance_register | 1.07 | 1 | 0 | 0 | 1258 | 799 | 456 | 455 |

## annotations-present (1 documents)

| document | share@5 | worst page | src img | docx img | src chars | docx chars | src draws | docx cells |
|---|---|---|---|---|---|---|---|---|
| 600_reviewed_invoice_with_annotati | 61.86 | 1 | 0 | 0 | 776 | 831 | 23 | 50 |

## none-identified (102 documents)

| document | share@5 | worst page | src img | docx img | src chars | docx chars | src draws | docx cells |
|---|---|---|---|---|---|---|---|---|
| 041122-Account_Opening_Form | 98.65 | 9 | 1 | 1 | 48837 | 48623 | 2534 | 659 |
| Account_Opening_Form_Fillable_fill | 97.62 | 7 | 1 | 1 | 48936 | 48702 | 2534 | 659 |
| one-page-rotated-180-degrees | 81.64 | 2 | 0 | 0 | 1951 | 1923 | 42 | 59 |
| 601_fillable_admission_form | 52.39 | 1 | 0 | 0 | 562 | 539 | 13 | 0 |
| 360_restaurant_menu | 50.18 | 1 | 0 | 0 | 1778 | 2116 | 45 | 82 |
| table-with-no-header-row | 47.48 | 1 | 0 | 0 | 1731 | 1520 | 38 | 208 |
| boq-tender-bill-of-quantities | 41.95 | 1 | 0 | 0 | 2794 | 2643 | 38 | 156 |
| very-long-single-column-table | 41.14 | 3 | 0 | 0 | 5112 | 4611 | 129 | 495 |
| itr-computation-with-slab-table | 38.49 | 1 | 0 | 0 | 2041 | 1881 | 61 | 130 |
| electricity-bill | 36.78 | 1 | 0 | 0 | 1803 | 1684 | 265 | 120 |
| balance-sheet-and-profit-loss | 36.69 | 2 | 0 | 0 | 2775 | 2498 | 65 | 188 |
| salary-slip-factory-wages | 35.15 | 1 | 0 | 0 | 1637 | 1541 | 49 | 92 |
| 03_stamp_vertical_90deg | 34.38 | 1 | 0 | 0 | 1611 | 1467 | 23 | 108 |
| table-across-page-break-repeated-h | 33.52 | 2 | 0 | 0 | 4168 | 3712 | 90 | 450 |
| table-inside-two-column-page | 30.72 | 1 | 0 | 0 | 2522 | 2333 | 15 | 2 |
| mobile-bill | 30.09 | 1 | 0 | 0 | 1659 | 1553 | 221 | 101 |
| text-held-twice-shadow-text | 29.15 | 1 | 0 | 0 | 2165 | 2122 | 16 | 28 |
| price-list-2col-dense-right-aligne | 27.89 | 1 | 0 | 0 | 4164 | 3972 | 85 | 246 |
| mutual-fund-statement | 27.8 | 1 | 0 | 0 | 3995 | 3779 | 89 | 217 |
| property-tax-receipt | 27.45 | 1 | 0 | 0 | 1609 | 1490 | 43 | 99 |
| marksheet-university-consolidated | 27.14 | 1 | 0 | 0 | 1566 | 1404 | 54 | 151 |
| 71_invoice_space_aligned_no_rules | 26.99 | 1 | 0 | 0 | 1441 | 1464 | 2 | 58 |
| 75_merged_header_cell_three_column | 26.77 | 1 | 0 | 0 | 743 | 785 | 21 | 48 |
| form16-part-b | 26.45 | 2 | 0 | 0 | 2822 | 2664 | 51 | 124 |
| insurance-policy-schedule | 22.66 | 1 | 0 | 0 | 1817 | 1716 | 249 | 98 |
| ... 77 more | | | | | | | | |
