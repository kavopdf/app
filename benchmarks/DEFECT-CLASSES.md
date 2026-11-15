# Defect classes — what is wrong with each document, ranked by damage to the user

Built from `benchmarks/RANKING.csv` of this run: **211 documents, 211 rows**. Every number
below is read from that file. Nothing here is estimated, and nothing here is a judgement:
the class is the `problem` field the instrument wrote, and the shape behind it is the
`signature` field. Both are derived mechanically from the tolerance sweep. This document
sorts those verdicts by damage. It does not re-derive, re-measure or overrule them.

`RANKING.csv` is the baseline cron's output and the only record of what was measured.
This file never edits it, and neither should anything else.

## The two axes, and why the class is not an opinion

    share@5px   fraction of source ink with no counterpart within 5 px   -> how much is wrong
    curve shape share@1px -> share@10px                                  -> whether it is ABSENT or MOVED
    max_pt      furthest displaced ink, in points                        -> an outlier indicator ONLY

A flat curve means tolerance cannot help: the ink is not there. A falling curve means the
ink is there and sitting somewhere else. The `signature` field records that shape; the
`problem` field refines it with invention and distance. Their joint distribution in this
run is consistent — every `content-loss` document is a missing or replaced class, every
`displacement` document is a present class, and `mixed` splits into the two partly-lost
classes:

| signature | problem | documents |
|---|---|---|
| MEASURE-ERROR | unmeasured | 1 |
| clean | none | 120 |
| content-loss | content-missing-nothing-in-its-place | 30 |
| content-loss | content-missing-partly-replaced | 14 |
| displacement | content-present-wholly-displaced | 15 |
| displacement | content-present-partly-displaced | 12 |
| displacement | single-element-far-out | 1 |
| mixed | content-partly-lost | 11 |
| mixed | content-partly-lost-and-displaced | 7 |
| **total** | | **211** |

## Damage ordering (highest damage per user first)

This order comes from what the user can recover, not from the size of the number and not
from the count of documents in the class.

| # | class | documents | worst in class | why it sits here |
|---|---|---|---|---|
| 1 | content-missing-nothing-in-its-place | 30 | 415_inline_images 89.04 %@5 | The source ink has no counterpart at any tolerance and almost nothing new was put down. |
| 2 | content-missing-partly-replaced | 14 | one-page-rotated-180-degrees 81.64 %@5 | Content is gone and something else sits where it was. |
| 3 | content-partly-lost | 11 | 411_nested_xobject_transforms 31.05 %@5 | Part of the page is gone, the rest is displaced. |
| 3 | content-partly-lost-and-displaced | 7 | itr-computation-with-slab-table 68.82 %@5 | Both loss and displacement, neither dominant. |
| 4 | content-present-wholly-displaced | 15 | 75_merged_header_cell_three_columns 27.62 %@5 | Every mark is present and every mark is in the wrong place. |
| 5 | content-present-partly-displaced | 12 | table-of-contents-dot-leaders 10.72 %@5 | Most of the page is right; a part of it moved. |
| 6 | single-element-far-out | 1 | newsletter-3col-header-footer 3.45 %@5 | Almost the whole page is correct and one small thing — a stamp, a seal — is far from home. |
| — | none | 120 | — | share@5px below 1 %. |
| 7 | unmeasured | 1 | — | The document failed to measure. |

**Do not rank by `max_pt`.** It is dominated by a single outlier pixel. In this run
`mobile-bill` carries max_pt 75.4 with a median of 1.44 pt, and
`landscape-page-inside-portrait-document` carries max_pt 28.3 at 13.08 %@5 — both are
low-share documents whose worst pixel says nothing about the page. A document at
share@5px near zero with a large max_pt is nearly perfect.

## content-missing-nothing-in-its-place — 30 documents

**Damage rank 1.** The source ink has no counterpart at any tolerance and almost nothing new was put down. The ink is ABSENT, not moved: no amount of reformatting recovers it. This is the worst class.

Worst: `415_inline_images` at 89.04 %@5, 89.04 %@10, max 153.1 pt, text recall 100.0 %.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature |
|---|---|---|---|---|---|---|---|
| 1 | `415_inline_images` | 89.04 % | 89.04 % | 153.1 | 100.0 % | 1 | content-loss |
| 2 | `mobile-bill` | 18.48 % | 17.26 % | 75.4 | 100.0 % | 1 | content-loss |
| 3 | `salary-slip-factory-wages` | 18.09 % | 17.49 % | 71.0 | 100.0 % | 1 | content-loss |
| 4 | `two-tables-stacked-with-no-gap` | 17.20 % | 16.48 % | 45.1 | 100.0 % | 1 | content-loss |
| 5 | `marksheet-university-consolidated` | 16.78 % | 16.18 % | 57.1 | 100.0 % | 1 | content-loss |
| 6 | `electricity-bill` | 16.24 % | 15.29 % | 100.8 | 100.0 % | 1 | content-loss |
| 7 | `insurance-policy-schedule` | 13.29 % | 12.87 % | 72.5 | 100.0 % | 1 | content-loss |
| 8 | `landscape-page-inside-portrait-document` | 13.08 % | 12.55 % | 28.3 | 100.0 % | 3 | content-loss |
| 9 | `form16-part-b` | 12.32 % | 11.95 % | 56.6 | 100.0 % | 2 | content-loss |
| 10 | `mutual-fund-statement` | 12.05 % | 11.87 % | 32.6 | 100.0 % | 2 | content-loss |
| 11 | `property-tax-receipt` | 10.78 % | 10.11 % | 55.7 | 100.0 % | 1 | content-loss |
| 12 | `admit-card` | 10.68 % | 9.36 % | 57.1 | 100.0 % | 1 | content-loss |
| 13 | `gst-invoice-multipage-item-table` | 10.44 % | 10.10 % | 52.3 | 100.0 % | 4 | content-loss |
| 14 | `delivery-challan` | 10.26 % | 9.88 % | 39.8 | 100.0 % | 1 | content-loss |
| 15 | `table-across-page-break-repeated-header` | 9.41 % | 9.35 % | 36.0 | 100.0 % | 3 | content-loss |
| 16 | `gst-invoice-3line-items` | 7.15 % | 6.77 % | 20.2 | 100.0 % | 1 | content-loss |
| 17 | `boq-tender-bill-of-quantities` | 7.10 % | 6.98 % | 28.8 | 100.0 % | 1 | content-loss |
| 18 | `table-with-rotated-header` | 6.42 % | 5.35 % | 30.2 | 100.0 % | 1 | content-loss |
| 19 | `balance-sheet-and-profit-loss` | 6.20 % | 6.07 % | 34.1 | 99.9 % | 2 | content-loss |
| 20 | `annual-review-2col-uneven-columns` | 5.77 % | 4.69 % | 27.8 | 100.0 % | 1 | content-loss |
| 21 | `purchase-order` | 5.30 % | 5.01 % | 38.4 | 100.0 % | 1 | content-loss |
| 22 | `23_timetable_grid_txtpos` | 5.16 % | 5.06 % | 46.6 | 100.0 % | 1 | content-loss |
| 23 | `invoice-line-items-qty-rate-amount` | 4.90 % | 4.54 % | 42.2 | 100.0 % | 1 | content-loss |
| 24 | `marksheet-subject-left-marks-right` | 4.55 % | 4.32 % | 77.3 | 100.0 % | 1 | content-loss |
| 25 | `bank-statement-5-pages` | 3.09 % | 2.71 % | 50.9 | 100.0 % | 5 | content-loss |
| 26 | `69_two_col_legal_numbered_clauses` | 2.53 % | 2.51 % | 12.5 | 100.0 % | 1 | content-loss |
| 27 | `35_four_typefaces_one_page` | 2.19 % | 1.94 % | 36.5 | 100.0 % | 1 | content-loss |
| 28 | `31_times_body_arial_headings` | 2.11 % | 1.69 % | 38.4 | 100.0 % | 1 | content-loss |
| 29 | `07_stamp_over_table` | 1.82 % | 1.67 % | 66.2 | 100.0 % | 1 | content-loss |
| 30 | `312_affidavit_stamp_paper` | 1.07 % | 1.02 % | 53.8 | 100.0 % | 1 | content-loss |

## content-missing-partly-replaced — 14 documents

**Damage rank 2.** Content is gone and something else sits where it was. Part of what the user had is unrecoverable and what replaced it is not what they wrote.

Worst: `one-page-rotated-180-degrees` at 81.64 %@5, 81.64 %@10, max 177.6 pt, text recall 100.0 %.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature |
|---|---|---|---|---|---|---|---|
| 1 | `one-page-rotated-180-degrees` | 81.64 % | 81.64 % | 177.6 | 100.0 % | 2 | content-loss |
| 2 | `600_reviewed_invoice_with_annotations` | 63.08 % | 52.91 % | 62.9 | 100.0 % | 1 | content-loss |
| 3 | `601_fillable_admission_form` | 52.39 % | 44.76 % | 27.8 | 99.6 % | 1 | content-loss |
| 4 | `table-inside-two-column-page` | 42.00 % | 33.62 % | 84.5 | 100.0 % | 1 | content-loss |
| 5 | `360_restaurant_menu` | 34.43 % | 28.56 % | 45.6 | 100.0 % | 1 | content-loss |
| 6 | `text-held-twice-shadow-text` | 34.33 % | 32.22 % | 92.6 | 100.0 % | 1 | content-loss |
| 7 | `77_arabic_rtl_document` | 11.89 % | 10.75 % | 19.7 | 100.0 % | 1 | content-loss |
| 8 | `academic-paper-ieee-2col-abstract` | 10.39 % | 8.36 % | 27.4 | 100.0 % | 2 | content-loss |
| 9 | `journal-2col-with-footnotes` | 7.75 % | 6.62 % | 35.0 | 100.0 % | 1 | content-loss |
| 10 | `370_offer_letter` | 3.47 % | 2.80 % | 31.7 | 100.0 % | 1 | content-loss |
| 11 | `352_certificate_ornate_border` | 3.00 % | 2.92 % | 5.3 | 100.0 % | 1 | content-loss |
| 12 | `11_stamp_with_signature_image` | 2.77 % | 2.67 % | 25.9 | 100.0 % | 1 | content-loss |
| 13 | `317_rti_response` | 2.18 % | 1.78 % | 37.0 | 100.0 % | 1 | content-loss |
| 14 | `gst-invoice-with-qr-code` | 1.24 % | 1.20 % | 16.3 | 100.0 % | 1 | content-loss |

## content-partly-lost — 11 documents

**Damage rank 3.** Part of the page is gone, the rest is displaced. Two failures to explain, not one.

Worst: `411_nested_xobject_transforms` at 31.05 %@5, 22.39 %@10, max 97.9 pt, text recall 100.0 %.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature |
|---|---|---|---|---|---|---|---|
| 1 | `411_nested_xobject_transforms` | 31.05 % | 22.39 % | 97.9 | 100.0 % | 1 | mixed |
| 2 | `40_devanagari_shaping_font` | 10.48 % | 7.89 % | 24.0 | 100.0 % | 1 | mixed |
| 3 | `76_devanagari_table` | 7.91 % | 5.53 % | 15.4 | 100.0 % | 1 | mixed |
| 4 | `very-long-single-column-table` | 6.87 % | 4.79 % | 46.6 | 100.0 % | 3 | mixed |
| 5 | `policy-2col-spanning-section-heading` | 5.37 % | 4.22 % | 25.0 | 100.0 % | 1 | mixed |
| 6 | `salary-slip-corporate` | 5.09 % | 3.86 % | 35.0 | 100.0 % | 1 | mixed |
| 7 | `33_sans_nondefault_body` | 4.49 % | 3.34 % | 36.0 | 100.0 % | 1 | mixed |
| 8 | `magazine-2col-pullquote-spanning` | 3.49 % | 2.56 % | 21.6 | 100.0 % | 1 | mixed |
| 9 | `304_package_insert_small_print` | 3.41 % | 2.30 % | 21.1 | 100.0 % | 1 | mixed |
| 10 | `61_two_col_abstract_spanning` | 2.01 % | 1.21 % | 15.8 | 100.0 % | 1 | mixed |
| 11 | `80_gstin_pan_cin_ifsc_table` | 2.01 % | 1.36 % | 13.4 | 100.0 % | 1 | mixed |

## content-partly-lost-and-displaced — 7 documents

**Damage rank 3.** Both loss and displacement, neither dominant. Two defects on one page.

Worst: `itr-computation-with-slab-table` at 68.82 %@5, 55.04 %@10, max 133.9 pt, text recall 100.0 %.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature |
|---|---|---|---|---|---|---|---|
| 1 | `itr-computation-with-slab-table` | 68.82 % | 55.04 % | 133.9 | 100.0 % | 1 | mixed |
| 2 | `table-with-merged-cells` | 4.93 % | 3.94 % | 13.9 | 100.0 % | 1 | mixed |
| 3 | `14_stamp_chars_positioned_td` | 3.89 % | 3.08 % | 25.4 | 100.0 % | 1 | mixed |
| 4 | `newspaper-2col-fullwidth-headline` | 3.46 % | 2.11 % | 24.5 | 100.0 % | 1 | mixed |
| 5 | `321_auditors_report` | 2.62 % | 1.93 % | 24.5 | 100.0 % | 1 | mixed |
| 6 | `313_power_of_attorney` | 2.29 % | 1.47 % | 40.3 | 100.0 % | 1 | mixed |
| 7 | `310_court_judgment` | 1.73 % | 1.17 % | 18.7 | 100.0 % | 1 | mixed |

## content-present-wholly-displaced — 15 documents

**Damage rank 4.** Every mark is present and every mark is in the wrong place. Recoverable in principle — nothing is lost — but the page is not usable as-is.

Worst: `75_merged_header_cell_three_columns` at 27.62 %@5, 11.53 %@10, max 21.6 pt, text recall 100.0 %.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature |
|---|---|---|---|---|---|---|---|
| 1 | `75_merged_header_cell_three_columns` | 27.62 % | 11.53 % | 21.6 | 100.0 % | 1 | displacement |
| 2 | `71_invoice_space_aligned_no_rules` | 26.88 % | 12.28 % | 9.1 | 100.0 % | 1 | displacement |
| 3 | `report-2col-table-spanning-both-columns` | 22.58 % | 7.61 % | 49.9 | 100.0 % | 1 | displacement |
| 4 | `03_stamp_vertical_90deg` | 16.98 % | 0.78 % | 5.8 | 100.0 % | 1 | displacement |
| 5 | `78_mixed_english_devanagari_line` | 13.51 % | 2.85 % | 18.2 | 100.0 % | 1 | displacement |
| 6 | `66_two_col_footnotes_bottom` | 13.03 % | 1.70 % | 8.6 | 100.0 % | 1 | displacement |
| 7 | `68_journal_wide_table_spanning` | 12.83 % | 0.60 % | 8.6 | 100.0 % | 1 | displacement |
| 8 | `363_warranty_card` | 10.58 % | 0.00 % | 4.3 | 100.0 % | 1 | displacement |
| 9 | `brochure-3col-with-sidebar-box` | 6.84 % | 3.17 % | 21.1 | 100.0 % | 1 | displacement |
| 10 | `gst-invoice-horizontal-rules-only` | 6.72 % | 0.19 % | 9.6 | 100.0 % | 1 | displacement |
| 11 | `374_org_chart` | 5.92 % | 0.00 % | 4.8 | 100.0 % | 1 | displacement |
| 12 | `payslip-label-left-amount-right` | 5.59 % | 0.00 % | 4.3 | 100.0 % | 1 | displacement |
| 13 | `417_rotate180_and_mirrored` | 5.50 % | 0.17 % | 5.8 | 100.0 % | 2 | displacement |
| 14 | `product-catalogue-code-left-price-right` | 1.71 % | 0.85 % | 8.2 | 100.0 % | 1 | displacement |
| 15 | `316_contract_with_schedules` | 1.26 % | 0.66 % | 27.4 | 100.0 % | 1 | displacement |

## content-present-partly-displaced — 12 documents

**Damage rank 5.** Most of the page is right; a part of it moved. The commonest geometry defect and the cheapest to fix.

Worst: `table-of-contents-dot-leaders` at 10.72 %@5, 3.69 %@10, max 26.4 pt, text recall 100.0 %.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature |
|---|---|---|---|---|---|---|---|
| 1 | `table-of-contents-dot-leaders` | 10.72 % | 3.69 % | 26.4 | 100.0 % | 1 | displacement |
| 2 | `64_newspaper_uneven_columns_ad_boxes` | 9.11 % | 4.65 % | 11.0 | 100.0 % | 1 | displacement |
| 3 | `bank-statement-horizontal-rules-only` | 6.89 % | 0.93 % | 6.2 | 100.0 % | 1 | displacement |
| 4 | `330_cad_drawing_sheet` | 4.91 % | 1.62 % | 14.9 | 100.0 % | 1 | displacement |
| 5 | `65_two_col_full_width_figure_caption` | 4.91 % | 1.03 % | 9.1 | 100.0 % | 1 | displacement |
| 6 | `406_passport_mrz_page` | 3.45 % | 1.94 % | 15.8 | 98.2 % | 1 | displacement |
| 7 | `price-list-2col-dense-right-aligned` | 2.69 % | 0.22 % | 7.2 | 100.0 % | 1 | displacement |
| 8 | `315_gazette_notification` | 1.96 % | 0.78 % | 8.6 | 100.0 % | 1 | displacement |
| 9 | `price-list-right-aligned-amounts` | 1.79 % | 0.03 % | 5.8 | 100.0 % | 1 | displacement |
| 10 | `27_two_column_left_short_txtpos` | 1.62 % | 0.89 % | 7.7 | 100.0 % | 1 | displacement |
| 11 | `392_statistical_console_output` | 1.61 % | 0.00 % | 4.3 | 99.9 % | 1 | displacement |
| 12 | `70_magazine_drop_cap_photo_caption` | 1.49 % | 0.48 % | 10.6 | 100.0 % | 1 | displacement |

## single-element-far-out — 1 document

**Damage rank 6.** Almost the whole page is correct and one small thing — a stamp, a seal — is far from home. Smallest share of ink, but it is the defect a user notices on a certificate.

Worst: `newsletter-3col-header-footer` at 3.45 %@5, 1.51 %@10, max 77.3 pt, text recall 100.0 %.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature |
|---|---|---|---|---|---|---|---|
| 1 | `newsletter-3col-header-footer` | 3.45 % | 1.51 % | 77.3 | 100.0 % | 1 | displacement |

## none — 120 documents

**Damage rank —.** share@5px below 1 %. Nothing to fix.

All 120 read share@5px below 1 %. Listed in full for completeness, worst first:

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature |
|---|---|---|---|---|---|---|---|
| 1 | `34_monospace_document` | 0.93 % | 0.00 % | 4.8 | 100.0 % | 1 | clean |
| 2 | `eway-bill` | 0.91 % | 0.86 % | 31.2 | 100.0 % | 1 | clean |
| 3 | `67_two_col_with_sidebar` | 0.80 % | 0.54 % | 11.5 | 100.0 % | 1 | clean |
| 4 | `28_value_overflows_cell_txtpos` | 0.74 % | 0.50 % | 15.4 | 100.0 % | 1 | clean |
| 5 | `79_inr_indian_digit_grouping_table` | 0.74 % | 0.35 % | 9.1 | 98.4 % | 1 | clean |
| 6 | `39_small_caps_letter_spacing` | 0.72 % | 0.00 % | 4.8 | 100.0 % | 1 | clean |
| 7 | `326_itr_computation` | 0.63 % | 0.46 % | 13.9 | 100.0 % | 1 | clean |
| 8 | `344_customs_declaration` | 0.61 % | 0.59 % | 49.9 | 100.0 % | 1 | clean |
| 9 | `table-with-no-header-row` | 0.61 % | 0.26 % | 11.5 | 100.0 % | 1 | clean |
| 10 | `37_font_not_embedded_substitution` | 0.58 % | 0.35 % | 14.4 | 100.0 % | 1 | clean |
| 11 | `balance-sheet-two-columns-of-figures` | 0.57 % | 0.06 % | 5.8 | 99.9 % | 1 | clean |
| 12 | `question-paper-marks-right-margin` | 0.44 % | 0.23 % | 14.9 | 100.0 % | 1 | clean |
| 13 | `413_tagged_pdf_actualtext` | 0.38 % | 0.00 % | 3.8 | 100.0 % | 1 | clean |
| 14 | `383_api_docs_page` | 0.30 % | 0.20 % | 19.7 | 100.0 % | 1 | clean |
| 15 | `bus-timetable-station-left-times-right` | 0.27 % | 0.13 % | 13.0 | 100.0 % | 1 | clean |
| 16 | `404_sudoku_grid` | 0.27 % | 0.00 % | 3.4 | 100.0 % | 1 | clean |
| 17 | `364_event_ticket` | 0.25 % | 0.00 % | 2.9 | 100.0 % | 1 | clean |
| 18 | `343_air_waybill` | 0.23 % | 0.16 % | 14.9 | 100.0 % | 1 | clean |
| 19 | `admission-form-labels-left-boxes-right` | 0.21 % | 0.00 % | 4.3 | 100.0 % | 1 | clean |
| 20 | `05_round_company_seal_curved_text` | 0.19 % | 0.01 % | 5.3 | 100.0 % | 1 | clean |
| 21 | `boq-horizontal-rules-only` | 0.13 % | 0.08 % | 8.6 | 100.0 % | 1 | clean |
| 22 | `350_question_paper` | 0.11 % | 0.10 % | 16.8 | 100.0 % | 1 | clean |
| 23 | `08_two_overlapping_stamps` | 0.11 % | 0.05 % | 11.0 | 100.0 % | 1 | clean |
| 24 | `391_survey_questionnaire_grid` | 0.11 % | 0.00 % | 4.3 | 99.6 % | 1 | clean |
| 25 | `333_datasheet_spec_tables` | 0.07 % | 0.02 % | 6.2 | 100.0 % | 1 | clean |
| 26 | `340_bill_of_lading` | 0.07 % | 0.00 % | 3.4 | 100.0 % | 1 | clean |
| 27 | `300_prescription_rx` | 0.06 % | 0.05 % | 21.6 | 100.0 % | 1 | clean |
| 28 | `60_page_border` | 0.06 % | 0.01 % | 8.2 | 100.0 % | 1 | clean |
| 29 | `12_stamp_across_page_break` | 0.05 % | 0.00 % | 3.4 | 100.0 % | 2 | clean |
| 30 | `45_coloured_callout_box` | 0.05 % | 0.00 % | 3.4 | 100.0 % | 1 | clean |
| 31 | `401_trifold_brochure` | 0.03 % | 0.01 % | 10.6 | 100.0 % | 1 | clean |
| 32 | `25_signature_block_underscores_txtpos` | 0.03 % | 0.01 % | 10.1 | 100.0 % | 1 | clean |
| 33 | `15_stamp_on_scanned_page` | 0.03 % | 0.00 % | 3.4 | 100.0 % | 1 | clean |
| 34 | `362_price_list_dense` | 0.03 % | 0.00 % | 3.4 | 100.0 % | 1 | clean |
| 35 | `390_wide_data_appendix` | 0.03 % | 0.00 % | 3.4 | 100.0 % | 1 | clean |
| 36 | `74_balance_sheet_indented_subitems` | 0.03 % | 0.00 % | 3.4 | 100.0 % | 1 | clean |
| 37 | `301_lab_report_panel` | 0.02 % | 0.01 % | 7.2 | 100.0 % | 1 | clean |
| 38 | `44_coloured_underlined_hyperlinks` | 0.02 % | 0.00 % | 3.8 | 100.0 % | 1 | clean |
| 39 | `20_numbered_list_separate_column_txtpos` | 0.02 % | 0.00 % | 2.9 | 100.0 % | 1 | clean |
| 40 | `365_recipe_card` | 0.02 % | 0.00 % | 2.9 | 100.0 % | 1 | clean |
| 41 | `13_stamp_non_english` | 0.01 % | 0.00 % | 3.8 | 100.0 % | 1 | clean |
| 42 | `26_footnote_marker_bottom_note_txtpos` | 0.01 % | 0.00 % | 3.8 | 100.0 % | 1 | clean |
| 43 | `375_attendance_register` | 0.01 % | 0.00 % | 3.8 | 100.0 % | 1 | clean |
| 44 | `393_spectrum_peak_table` | 0.01 % | 0.00 % | 3.4 | 100.0 % | 1 | clean |
| 45 | `38_faux_bold_italic_synthesised` | 0.01 % | 0.00 % | 2.9 | 98.0 % | 1 | clean |
| 46 | `46_chart_coloured_labels_body_text` | 0.01 % | 0.00 % | 2.9 | 100.0 % | 1 | clean |
| 47 | `342_packing_list` | 0.00 % | 0.00 % | 3.4 | 100.0 % | 1 | clean |
| 48 | `407_id_card_front_back` | 0.00 % | 0.00 % | 3.4 | 100.0 % | 1 | clean |
| 49 | `56_table_indented_from_margin` | 0.00 % | 0.00 % | 3.4 | 100.0 % | 1 | clean |
| 50 | `02_stamp_rotated_15deg_upleft` | 0.00 % | 0.00 % | 2.9 | 100.0 % | 1 | clean |
| 51 | `323_credit_card_statement` | 0.00 % | 0.00 % | 2.9 | 100.0 % | 1 | clean |
| 52 | `325_demat_holdings_statement` | 0.00 % | 0.00 % | 2.9 | 100.0 % | 1 | clean |
| 53 | `335_msds_safety_data_sheet` | 0.00 % | 0.00 % | 2.9 | 100.0 % | 1 | clean |
| 54 | `353_admit_card` | 0.00 % | 0.00 % | 2.9 | 100.0 % | 1 | clean |
| 55 | `381_incident_report_timeline` | 0.00 % | 0.00 % | 2.9 | 100.0 % | 1 | clean |
| 56 | `403_crossword_puzzle` | 0.00 % | 0.00 % | 2.9 | 100.0 % | 1 | clean |
| 57 | `01_stamp_rotated_15deg_upright` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 58 | `10_stamp_as_image` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 59 | `16_right_aligned_amounts_txtpos` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 60 | `17_three_column_widths_txtpos` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 61 | `18_centred_heading_left_body_txtpos` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 62 | `19_hanging_indent_txtpos` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 63 | `21_form_labels_x60_values_x300_txtpos` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 64 | `29_dot_leaders_txtpos` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 65 | `306_clinical_protocol_synopsis` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 66 | `311_fir_police_form` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 67 | `314_tender_rfp_boq` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 68 | `318_court_summons_form` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 69 | `320_balance_sheet_statutory` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 70 | `324_loan_amortisation_schedule` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 7 | clean |
| 71 | `331_pid_diagram` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 72 | `332_bom_on_drawing` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 73 | `341_shipping_manifest` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 74 | `36_embedded_subset_font` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 75 | `373_leave_application_form` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 76 | `402_calendar_month_grid` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 77 | `42_table_coloured_header_alternating_rows` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 78 | `50_invoice_coloured_total_row` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 79 | `51_two_cm_margins` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 80 | `52_one_cm_margin_wide_body` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 81 | `55_sidebar_box_beside_body` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 82 | `62_two_col_newsletter_pull_quote` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 83 | `63_three_column_brochure` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 84 | `72_bank_statement_no_rules_right_amounts` | 0.00 % | 0.00 % | 2.4 | 100.0 % | 1 | clean |
| 85 | `04_stamp_180deg_upside_down` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 86 | `06_rect_paid_stamp_red_transparent` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 87 | `24_address_block_indents_txtpos` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 88 | `302_radiology_report` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 89 | `303_discharge_summary` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 90 | `334_patent_document` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 91 | `351_omr_answer_sheet` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 92 | `371_experience_certificate` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 93 | `394_map_with_legend` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 94 | `43_red_stamp_over_black_text` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 95 | `49_coloured_background_block_paragraph` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 96 | `53_single_space_body_15_headings` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 1 | clean |
| 97 | `57_centred_title_page_left_body_pages` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 2 | clean |
| 98 | `59_landscape_mixed_portrait` | 0.00 % | 0.00 % | 1.9 | 100.0 % | 2 | clean |
| 99 | `09_stamp_font_not_embedded` | 0.00 % | 0.00 % | 1.4 | 100.0 % | 1 | clean |
| 100 | `22_invoice_four_columns_txtpos` | 0.00 % | 0.00 % | 1.4 | 100.0 % | 1 | clean |
| 101 | `305_vaccination_certificate` | 0.00 % | 0.00 % | 1.4 | 100.0 % | 1 | clean |
| 102 | `30_mixed_font_sizes_one_baseline_txtpos` | 0.00 % | 0.00 % | 1.4 | 100.0 % | 1 | clean |
| 103 | `322_mutual_fund_factsheet` | 0.00 % | 0.00 % | 1.4 | 100.0 % | 1 | clean |
| 104 | `400_comic_page_speech_bubbles` | 0.00 % | 0.00 % | 1.4 | 100.0 % | 1 | clean |
| 105 | `41_coloured_headings_white_bg` | 0.00 % | 0.00 % | 1.4 | 100.0 % | 1 | clean |
| 106 | `48_form_coloured_border_coloured_values` | 0.00 % | 0.00 % | 1.4 | 100.0 % | 1 | clean |
| 107 | `58_header_rule_footer_rule` | 0.00 % | 0.00 % | 1.4 | 100.0 % | 2 | clean |
| 108 | `73_marksheet_subject_marks_grade` | 0.00 % | 0.00 % | 1.4 | 100.0 % | 1 | clean |
| 109 | `32_serif_nondefault_body` | 0.00 % | 0.00 % | 1.0 | 100.0 % | 1 | clean |
| 110 | `372_timesheet_grid` | 0.00 % | 0.00 % | 1.0 | 100.0 % | 1 | clean |
| 111 | `380_runbook_terminal_output` | 0.00 % | 0.00 % | 1.0 | 100.0 % | 1 | clean |
| 112 | `405_sheet_music_lyrics` | 0.00 % | 0.00 % | 1.0 | 100.0 % | 1 | clean |
| 113 | `410_form_xobject_reused` | 0.00 % | 0.00 % | 1.0 | 100.0 % | 1 | clean |
| 114 | `47_grey_body_black_headings` | 0.00 % | 0.00 % | 1.0 | 100.0 % | 1 | clean |
| 115 | `54_two_column_body_full_width_header_footer` | 0.00 % | 0.00 % | 1.0 | 100.0 % | 1 | clean |
| 116 | `602_bookmarked_annual_report` | 0.00 % | 0.00 % | 1.0 | 100.0 % | 3 | clean |
| 117 | `361_product_catalogue_grid` | 0.00 % | 0.00 % | 0.0 | 100.0 % | 1 | clean |
| 118 | `382_architecture_diagram` | 0.00 % | 0.00 % | 0.0 | 100.0 % | 1 | clean |
| 119 | `412_page_labels_roman` | 0.00 % | 0.00 % | 0.0 | 100.0 % | 5 | clean |
| 120 | `414_transparency_softmask` | 0.00 % | 0.00 % | 0.0 | 100.0 % | 1 | clean |

## unmeasured — 1 document

**Damage rank 7.** The document failed to measure. There is no defect verdict here, only a measurement gap.

This document produced `MEASURE-ERROR` and no sweep. It is not a pass and it is not a
defect: it is a hole in the measurement. It must be measured before anyone judges it,
and it must never be counted as clean.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature |
|---|---|---|---|---|---|---|---|
| 1 | `416_many_tiny_pages` | — % | — % | — | — % | — | MEASURE-ERROR |

## Real-world documents — the class the corpus cannot represent

The 211-document corpus is synthetic and is not the product. The same instrument, on the
same engine, on nine real documents, reads median share@5px **10.3 %** against 0.3 %
synthetic, and two nine-page bank forms read **98.7 %** and **97.6 %**. That evidence
lives in `benchmarks/REALWORLD-FINDINGS.md` and `benchmarks/REALWORLD-RANKING.csv`.

| # | document | problem | share@5px | max_pt | text recall | pages |
|---|---|---|---|---|---|---|
| 1 | `041122-Account_Opening_Form` | content-missing-partly-replaced | 98.65 % | 937.9 | 99.7 % | 9 |
| 2 | `Account_Opening_Form_Fillable_filled` | content-missing-partly-replaced | 97.62 % | 358.1 | 99.7 % | 9 |
| 3 | `property-tax-receipt` | content-missing-nothing-in-its-place | 10.78 % | 55.7 | 100.0 % | 1 |
| 4 | `admit-card` | content-missing-nothing-in-its-place | 10.68 % | 57.1 | 100.0 % | 1 |
| 5 | `delivery-challan` | content-missing-nothing-in-its-place | 10.26 % | 39.8 | 100.0 % | 1 |
| 6 | `gst-invoice-3line-items` | content-missing-nothing-in-its-place | 7.15 % | 20.2 | 100.0 % | 1 |
| 7 | `350_question_paper` | none | 0.11 % | 16.8 | 100.0 % | 1 |
| 8 | `300_prescription_rx` | none | 0.06 % | 21.6 | 100.0 % | 1 |
| 9 | `311_fir_police_form` | none | 0.00 % | 2.4 | 100.0 % | 1 |

**The nine-page form is a class, not a document.** Two independent nine-page bank forms
both land at 97–99 % share@5px with the furthest mark 33 cm from home — larger than the
page — while text recall stays at 99.7 %. The words come through; the layout does not.
No synthetic document in the corpus has nine pages of repeated field grids, which is
exactly why the corpus reads clean on a document type users open constantly.

So this class outranks `415_inline_images`. That is one document; this is a class, and it
is the largest measured error anywhere in the project. The corpus cannot see it, and a
corpus-only ranking will always place it last by omission. Quote both medians, always.

Coverage note: 7 of the nine real documents are also rows in `RANKING.csv` (`property-tax-receipt`, `admit-card`, `delivery-challan`, `gst-invoice-3line-items`, `350_question_paper`, `300_prescription_rx`, `311_fir_police_form`), because they were added to the corpus. The two
worst — `041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled` — are still **absent from the corpus**.
Until they are in it, no corpus statistic describes the product.

## Caveat to carry forward: `one-page-rotated-180-degrees` is not an ink defect

It reads content-loss at 81.6 % share@5px with **text recall 100 %**. Both numbers are
true and they describe different things: the source page is an upside-down **scan**, and
our output is **typeset text**. The ink cannot match because it is a different medium, not
because ink went missing. In this run it lands in `content-missing-partly-replaced` with
invent5 78.8 % — the scan's ink was replaced by glyphs.

Do not hand this to the fixer as an ink defect. It is a scan-to-text conversion, and the
ink metric is not its judge. The same applies to `417_rotate180_and_mirrored`: the source
page carries `/Rotate 180` and the upright output is the correct result.

## What this file does not say

It says what KIND of defect each document has and how much damage that kind does. It does
not say WHY the engine produced it — causes come from `p2w.py --diagnose` and a rendered
side-by-side pair, not from these numbers. The name narrows the search; it does not
perform it. And it does not say the corpus is the product, because it is not.
