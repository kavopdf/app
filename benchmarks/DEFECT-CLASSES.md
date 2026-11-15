# Defect classes - what is wrong with each document, ranked by damage to the user

Documents measured: **211 of 211**

Built from `benchmarks/RANKING.csv` of this run: **211 rows, 211 distinct documents, every one of them scored**. Every number below is read from that file, or from `REALWORLD-RANKING.csv` where it is named as such. Nothing here is estimated and nothing here is a judgement: the class is the `problem` field the instrument wrote and the shape behind it is the `signature` field, both derived mechanically from the tolerance sweep. This document sorts those verdicts by damage. It does not re-derive, re-measure or overrule them.

`RANKING.csv` is the baseline cron's output and the only record of what was measured. This file never edits it, and neither should anything else.

## The class is not an opinion

    share@5px     fraction of source ink with no counterpart within 5 px   -> how much is wrong
    curve shape   share@1px -> share@10px                                 -> ABSENT or MOVED
    max_pt        furthest displaced ink, in points                       -> an outlier indicator ONLY

A flat curve means tolerance cannot help: the ink is not there. A falling curve means the ink is there and sitting somewhere else. The two fields agree on every row of this run - every `content-loss` document is a missing or replaced class, every `displacement` document is a present class, and `mixed` splits into the two partly-lost classes:

| signature | problem | documents |
|---|---|---|
| clean | none | 121 |
| content-loss | content-missing-nothing-in-its-place | 30 |
| content-loss | content-missing-partly-replaced | 14 |
| displacement | content-present-wholly-displaced | 15 |
| displacement | content-present-partly-displaced | 12 |
| displacement | single-element-far-out | 1 |
| mixed | content-partly-lost | 11 |
| mixed | content-partly-lost-and-displaced | 7 |
| **total** | | **211** |

## Damage ordering (highest damage per user first)

This order comes from what the user can recover, not from the size of the number and not from the number of documents in the class.

| # | class | documents | worst in class | why it sits here |
|---|---|---|---|---|
| 1 | content-missing-nothing-in-its-place | 30 | 415_inline_images 89.04 %@5 | highest - content gone, unrecoverable |
| 2 | content-missing-partly-replaced | 14 | one-page-rotated-180-degrees 81.64 %@5 | very high - content gone, replaced by something else |
| 3 | content-partly-lost | 11 | 411_nested_xobject_transforms 31.05 %@5 | high - part gone, rest moved |
| 3 | content-partly-lost-and-displaced | 7 | itr-computation-with-slab-table 68.82 %@5 | high - two defects on one page |
| 4 | content-present-wholly-displaced | 15 | 75_merged_header_cell_three_columns 27.62 %@5 | high - everything there, all of it moved |
| 5 | content-present-partly-displaced | 12 | table-of-contents-dot-leaders 10.72 %@5 | moderate - most right, part moved |
| 6 | single-element-far-out | 1 | newsletter-3col-header-footer 3.45 %@5 | low - one small element far from home |
| - | none | 121 | - | share@5px below 1 % |
| 7 | unmeasured | 0 | - | the document failed to measure |

**Do not rank by `max_pt`.** It is dominated by a single outlier pixel. In this run `electricity-bill` carries max_pt 100.8 at 16.24 %@5 with a median of 1.44 pt, and `mobile-bill` carries 75.36 at 18.48 %@5 with a median of 1.44 pt - the worst pixel says nothing about the page. A document with share@5px near zero and a large max_pt is nearly perfect: `344_customs_declaration` reads 0.61 %@5 with max_pt 49.92, and `416_many_tiny_pages` reads 0.00 %@5 with 300 pages.

## The status column, and what the gate does with it

`round.py` counts every table row that carries `OPEN` in a cell, and the round cannot close while any row says it. The vocabulary is exactly three words:

    OPEN      still to fix - the round cannot close while any row says this
    FIXED     the fixer measured it and the number improved
    PARKED    tried, could not be fixed, reason written beside it

This classification is step 2 of 3: it sorts, it never fixes. So no row here is `FIXED` - that status can only be written by a run that measured an improvement, and claiming it here would be a lie the next ratchet would expose. Rows that are not defects the engine can close are `PARKED`, with the reason in the row.

The `none` section carries no status cells at all, deliberately. A clean document has nothing for the fixer to act on; marking 121 clean rows `OPEN` would block every round for ever, and marking them `FIXED` would claim a fix nobody made. Absent beats a wrong word.

## Coverage: what this run measured, and the one gap in it

`measure_gate.py` expects **213** documents: 211 synthetic plus the PDFs sitting in `benchmarks/realworld/`. `RANKING.csv` holds **211** rows. The two nine-page bank forms are therefore **not rows in this run's ranking**, even though the PDFs ship in the repository and `REALWORLD-IN-CORPUS.md` states they are copied in by `corpus()`. Their numbers exist only in `REALWORLD-RANKING.csv`, and they are quoted from there in the real-world section below.

This is a measurement-coverage gap, not a classification decision. It is recorded here because the class file is the only place a reader would otherwise conclude the two forms had been measured and found unremarkable. The four one-page real documents (`property-tax-receipt`, `admit-card`, `delivery-challan`, `gst-invoice-3line-items`) **are** ordinary rows in `RANKING.csv` and are classified below like any other document.

## The classes, in damage order

### content-missing-nothing-in-its-place - 30 documents

**Damage rank 1.** The ink is ABSENT, not moved. Nothing was put where it sat, so no amount of reformatting recovers it. Flat tolerance curve.

Worst: `415_inline_images` at 89.04 %@5, 89.04 %@10, max 153.12 pt, text recall 100.0 %. 30 row(s) `OPEN`, 0 `PARKED`.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature | status | note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `415_inline_images` | 89.04 % | 89.04 % | 153.12 | 100.0 % | 1 | content-loss | OPEN | the only true deletion in the corpus: four bars of image ink absent, nothing put in their place, flat curve 89.04 %@1 -> 89.04 %@10 |
| 2 | `mobile-bill` | 18.48 % | 17.26 % | 75.36 | 100.0 % | 1 | content-loss | OPEN | - |
| 3 | `salary-slip-factory-wages` | 18.09 % | 17.49 % | 71.04 | 100.0 % | 1 | content-loss | OPEN | - |
| 4 | `two-tables-stacked-with-no-gap` | 17.2 % | 16.48 % | 45.12 | 100.0 % | 1 | content-loss | OPEN | - |
| 5 | `marksheet-university-consolidated` | 16.78 % | 16.18 % | 57.12 | 100.0 % | 1 | content-loss | OPEN | - |
| 6 | `electricity-bill` | 16.24 % | 15.29 % | 100.8 | 100.0 % | 1 | content-loss | OPEN | - |
| 7 | `insurance-policy-schedule` | 13.29 % | 12.87 % | 72.48 | 100.0 % | 1 | content-loss | OPEN | - |
| 8 | `landscape-page-inside-portrait-document` | 13.08 % | 12.55 % | 28.32 | 100.0 % | 3 | content-loss | OPEN | - |
| 9 | `form16-part-b` | 12.32 % | 11.95 % | 56.64 | 100.0 % | 2 | content-loss | OPEN | - |
| 10 | `mutual-fund-statement` | 12.05 % | 11.87 % | 32.64 | 100.0 % | 2 | content-loss | OPEN | - |
| 11 | `property-tax-receipt` | 10.78 % | 10.11 % | 55.68 | 100.0 % | 1 | content-loss | OPEN | - |
| 12 | `admit-card` | 10.68 % | 9.36 % | 57.12 | 100.0 % | 1 | content-loss | OPEN | - |
| 13 | `gst-invoice-multipage-item-table` | 10.44 % | 10.1 % | 52.32 | 100.0 % | 4 | content-loss | OPEN | - |
| 14 | `delivery-challan` | 10.26 % | 9.88 % | 39.84 | 100.0 % | 1 | content-loss | OPEN | - |
| 15 | `table-across-page-break-repeated-header` | 9.41 % | 9.35 % | 36.0 | 100.0 % | 3 | content-loss | OPEN | - |
| 16 | `gst-invoice-3line-items` | 7.15 % | 6.77 % | 20.16 | 100.0 % | 1 | content-loss | OPEN | - |
| 17 | `boq-tender-bill-of-quantities` | 7.1 % | 6.98 % | 28.8 | 100.0 % | 1 | content-loss | OPEN | - |
| 18 | `table-with-rotated-header` | 6.42 % | 5.35 % | 30.24 | 100.0 % | 1 | content-loss | OPEN | - |
| 19 | `balance-sheet-and-profit-loss` | 6.2 % | 6.07 % | 34.08 | 99.91 % | 2 | content-loss | OPEN | - |
| 20 | `annual-review-2col-uneven-columns` | 5.77 % | 4.69 % | 27.84 | 100.0 % | 1 | content-loss | OPEN | - |
| 21 | `purchase-order` | 5.3 % | 5.01 % | 38.4 | 100.0 % | 1 | content-loss | OPEN | - |
| 22 | `23_timetable_grid_txtpos` | 5.16 % | 5.06 % | 46.56 | 100.0 % | 1 | content-loss | OPEN | - |
| 23 | `invoice-line-items-qty-rate-amount` | 4.9 % | 4.54 % | 42.24 | 100.0 % | 1 | content-loss | OPEN | - |
| 24 | `marksheet-subject-left-marks-right` | 4.55 % | 4.32 % | 77.28 | 100.0 % | 1 | content-loss | OPEN | - |
| 25 | `bank-statement-5-pages` | 3.09 % | 2.71 % | 50.88 | 100.0 % | 5 | content-loss | OPEN | - |
| 26 | `69_two_col_legal_numbered_clauses` | 2.53 % | 2.51 % | 12.48 | 100.0 % | 1 | content-loss | OPEN | - |
| 27 | `35_four_typefaces_one_page` | 2.19 % | 1.94 % | 36.48 | 100.0 % | 1 | content-loss | OPEN | - |
| 28 | `31_times_body_arial_headings` | 2.11 % | 1.69 % | 38.4 | 100.0 % | 1 | content-loss | OPEN | - |
| 29 | `07_stamp_over_table` | 1.82 % | 1.67 % | 66.24 | 100.0 % | 1 | content-loss | OPEN | - |
| 30 | `312_affidavit_stamp_paper` | 1.07 % | 1.02 % | 53.76 | 100.0 % | 1 | content-loss | OPEN | - |

### content-missing-partly-replaced - 14 documents

**Damage rank 2.** Content is gone and something else sits where it was. Falling curve, high invention.

Worst: `one-page-rotated-180-degrees` at 81.64 %@5, 81.64 %@10, max 177.6 pt, text recall 100.0 %. 13 row(s) `OPEN`, 1 `PARKED`.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature | status | note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `one-page-rotated-180-degrees` | 81.64 % | 81.64 % | 177.6 | 100.0 % | 2 | content-loss | PARKED | medium mismatch: source is an upside-down scan, output is typeset text; text recall 100 %, nothing lost |
| 2 | `600_reviewed_invoice_with_annotations` | 63.08 % | 52.91 % | 62.88 | 100.0 % | 1 | content-loss | OPEN | annotation ink gone, something else where it sat |
| 3 | `601_fillable_admission_form` | 52.39 % | 44.76 % | 27.84 | 99.58 % | 1 | content-loss | OPEN | field boxes replaced; text recall 99.58 %, 2 chars missing |
| 4 | `table-inside-two-column-page` | 42.0 % | 33.62 % | 84.48 | 100.0 % | 1 | content-loss | OPEN | table ink replaced by reflowed text |
| 5 | `360_restaurant_menu` | 34.43 % | 28.56 % | 45.6 | 100.0 % | 1 | content-loss | OPEN | - |
| 6 | `text-held-twice-shadow-text` | 34.33 % | 32.22 % | 92.64 | 100.0 % | 1 | content-loss | OPEN | shadow copy dropped, real text placed once |
| 7 | `77_arabic_rtl_document` | 11.89 % | 10.75 % | 19.68 | 100.0 % | 1 | content-loss | OPEN | - |
| 8 | `academic-paper-ieee-2col-abstract` | 10.39 % | 8.36 % | 27.36 | 100.0 % | 2 | content-loss | OPEN | - |
| 9 | `journal-2col-with-footnotes` | 7.75 % | 6.62 % | 35.04 | 100.0 % | 1 | content-loss | OPEN | - |
| 10 | `370_offer_letter` | 3.47 % | 2.8 % | 31.68 | 100.0 % | 1 | content-loss | OPEN | - |
| 11 | `352_certificate_ornate_border` | 3.0 % | 2.92 % | 5.28 | 100.0 % | 1 | content-loss | OPEN | - |
| 12 | `11_stamp_with_signature_image` | 2.77 % | 2.67 % | 25.92 | 100.0 % | 1 | content-loss | OPEN | - |
| 13 | `317_rti_response` | 2.18 % | 1.78 % | 36.96 | 100.0 % | 1 | content-loss | OPEN | - |
| 14 | `gst-invoice-with-qr-code` | 1.24 % | 1.2 % | 16.32 | 100.0 % | 1 | content-loss | OPEN | - |

### content-partly-lost - 11 documents

**Damage rank 3.** Some content gone, the rest displaced. Two axes high, neither dominant.

Worst: `411_nested_xobject_transforms` at 31.05 %@5, 22.39 %@10, max 97.92 pt, text recall 100.0 %. 11 row(s) `OPEN`, 0 `PARKED`.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature | status | note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `411_nested_xobject_transforms` | 31.05 % | 22.39 % | 97.92 | 100.0 % | 1 | mixed | OPEN | nested xobject content partly gone, the rest displaced |
| 2 | `40_devanagari_shaping_font` | 10.48 % | 7.89 % | 24.0 | 100.0 % | 1 | mixed | OPEN | - |
| 3 | `76_devanagari_table` | 7.91 % | 5.53 % | 15.36 | 100.0 % | 1 | mixed | OPEN | - |
| 4 | `very-long-single-column-table` | 6.87 % | 4.79 % | 46.56 | 100.0 % | 3 | mixed | OPEN | - |
| 5 | `policy-2col-spanning-section-heading` | 5.37 % | 4.22 % | 24.96 | 100.0 % | 1 | mixed | OPEN | - |
| 6 | `salary-slip-corporate` | 5.09 % | 3.86 % | 35.04 | 100.0 % | 1 | mixed | OPEN | - |
| 7 | `33_sans_nondefault_body` | 4.49 % | 3.34 % | 36.0 | 100.0 % | 1 | mixed | OPEN | - |
| 8 | `magazine-2col-pullquote-spanning` | 3.49 % | 2.56 % | 21.6 | 100.0 % | 1 | mixed | OPEN | - |
| 9 | `304_package_insert_small_print` | 3.41 % | 2.3 % | 21.12 | 100.0 % | 1 | mixed | OPEN | - |
| 10 | `61_two_col_abstract_spanning` | 2.01 % | 1.21 % | 15.84 | 100.0 % | 1 | mixed | OPEN | - |
| 11 | `80_gstin_pan_cin_ifsc_table` | 2.01 % | 1.36 % | 13.44 | 100.0 % | 1 | mixed | OPEN | - |

### content-partly-lost-and-displaced - 7 documents

**Damage rank 3.** Two defects on one page: loss and displacement together.

Worst: `itr-computation-with-slab-table` at 68.82 %@5, 55.04 %@10, max 133.92 pt, text recall 100.0 %. 7 row(s) `OPEN`, 0 `PARKED`.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature | status | note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `itr-computation-with-slab-table` | 68.82 % | 55.04 % | 133.92 | 100.0 % | 1 | mixed | OPEN | content present, geometry systematically off; rules and column edges a few px out across the page |
| 2 | `table-with-merged-cells` | 4.93 % | 3.94 % | 13.92 | 100.0 % | 1 | mixed | OPEN | - |
| 3 | `14_stamp_chars_positioned_td` | 3.89 % | 3.08 % | 25.44 | 100.0 % | 1 | mixed | OPEN | - |
| 4 | `newspaper-2col-fullwidth-headline` | 3.46 % | 2.11 % | 24.48 | 100.0 % | 1 | mixed | OPEN | - |
| 5 | `321_auditors_report` | 2.62 % | 1.93 % | 24.48 | 100.0 % | 1 | mixed | OPEN | - |
| 6 | `313_power_of_attorney` | 2.29 % | 1.47 % | 40.32 | 100.0 % | 1 | mixed | OPEN | - |
| 7 | `310_court_judgment` | 1.73 % | 1.17 % | 18.72 | 100.0 % | 1 | mixed | OPEN | - |

### content-present-wholly-displaced - 15 documents

**Damage rank 4.** Every mark is present and every mark is in the wrong place. Loss equals invention.

Worst: `75_merged_header_cell_three_columns` at 27.62 %@5, 11.53 %@10, max 21.6 pt, text recall 100.0 %. 15 row(s) `OPEN`, 0 `PARKED`.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature | status | note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `75_merged_header_cell_three_columns` | 27.62 % | 11.53 % | 21.6 | 100.0 % | 1 | displacement | OPEN | loss and invention equal - every mark there, all of it moved |
| 2 | `71_invoice_space_aligned_no_rules` | 26.88 % | 12.28 % | 9.12 | 100.0 % | 1 | displacement | OPEN | space-aligned columns reflowed; nothing lost |
| 3 | `report-2col-table-spanning-both-columns` | 22.58 % | 7.61 % | 49.92 | 100.0 % | 1 | displacement | OPEN | - |
| 4 | `03_stamp_vertical_90deg` | 16.98 % | 0.78 % | 5.76 | 100.0 % | 1 | displacement | OPEN | - |
| 5 | `78_mixed_english_devanagari_line` | 13.51 % | 2.85 % | 18.24 | 100.0 % | 1 | displacement | OPEN | - |
| 6 | `66_two_col_footnotes_bottom` | 13.03 % | 1.7 % | 8.64 | 100.0 % | 1 | displacement | OPEN | - |
| 7 | `68_journal_wide_table_spanning` | 12.83 % | 0.6 % | 8.64 | 100.0 % | 1 | displacement | OPEN | - |
| 8 | `363_warranty_card` | 10.58 % | 0.0 % | 4.32 | 100.0 % | 1 | displacement | OPEN | - |
| 9 | `brochure-3col-with-sidebar-box` | 6.84 % | 3.17 % | 21.12 | 100.0 % | 1 | displacement | OPEN | - |
| 10 | `gst-invoice-horizontal-rules-only` | 6.72 % | 0.19 % | 9.6 | 100.0 % | 1 | displacement | OPEN | - |
| 11 | `374_org_chart` | 5.92 % | 0.0 % | 4.8 | 100.0 % | 1 | displacement | OPEN | - |
| 12 | `payslip-label-left-amount-right` | 5.59 % | 0.0 % | 4.32 | 100.0 % | 1 | displacement | OPEN | - |
| 13 | `417_rotate180_and_mirrored` | 5.5 % | 0.17 % | 5.76 | 100.0 % | 2 | displacement | OPEN | - |
| 14 | `product-catalogue-code-left-price-right` | 1.71 % | 0.85 % | 8.16 | 100.0 % | 1 | displacement | OPEN | - |
| 15 | `316_contract_with_schedules` | 1.26 % | 0.66 % | 27.36 | 100.0 % | 1 | displacement | OPEN | - |

### content-present-partly-displaced - 12 documents

**Damage rank 5.** Most of the page is right; a part of it moved.

Worst: `table-of-contents-dot-leaders` at 10.72 %@5, 3.69 %@10, max 26.4 pt, text recall 100.0 %. 12 row(s) `OPEN`, 0 `PARKED`.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature | status | note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `table-of-contents-dot-leaders` | 10.72 % | 3.69 % | 26.4 | 100.0 % | 1 | displacement | OPEN | dot leaders rebuilt at different positions |
| 2 | `64_newspaper_uneven_columns_ad_boxes` | 9.11 % | 4.65 % | 11.04 | 100.0 % | 1 | displacement | OPEN | - |
| 3 | `bank-statement-horizontal-rules-only` | 6.89 % | 0.93 % | 6.24 | 100.0 % | 1 | displacement | OPEN | - |
| 4 | `330_cad_drawing_sheet` | 4.91 % | 1.62 % | 14.88 | 100.0 % | 1 | displacement | OPEN | - |
| 5 | `65_two_col_full_width_figure_caption` | 4.91 % | 1.03 % | 9.12 | 100.0 % | 1 | displacement | OPEN | - |
| 6 | `406_passport_mrz_page` | 3.45 % | 1.94 % | 15.84 | 98.21 % | 1 | displacement | OPEN | - |
| 7 | `price-list-2col-dense-right-aligned` | 2.69 % | 0.22 % | 7.2 | 100.0 % | 1 | displacement | OPEN | - |
| 8 | `315_gazette_notification` | 1.96 % | 0.78 % | 8.64 | 100.0 % | 1 | displacement | OPEN | - |
| 9 | `price-list-right-aligned-amounts` | 1.79 % | 0.03 % | 5.76 | 100.0 % | 1 | displacement | OPEN | - |
| 10 | `27_two_column_left_short_txtpos` | 1.62 % | 0.89 % | 7.68 | 100.0 % | 1 | displacement | OPEN | - |
| 11 | `392_statistical_console_output` | 1.61 % | 0.0 % | 4.32 | 99.87 % | 1 | displacement | OPEN | - |
| 12 | `70_magazine_drop_cap_photo_caption` | 1.49 % | 0.48 % | 10.56 | 100.0 % | 1 | displacement | OPEN | - |

### single-element-far-out - 1 documents

**Damage rank 6.** Almost the whole page is correct and one small thing - a stamp, a seal - is far from home.

Worst: `newsletter-3col-header-footer` at 3.45 %@5, 1.51 %@10, max 77.28 pt, text recall 100.0 %. 1 row(s) `OPEN`, 0 `PARKED`.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature | status | note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `newsletter-3col-header-footer` | 3.45 % | 1.51 % | 77.28 | 100.0 % | 1 | displacement | OPEN | 97 % of the page correct; one header/footer element 77 pt from home |

### none - 121 documents (clean)

`share@5px` below 1 %: the output ink sits where the source put it. Nothing to fix, so these rows carry no status cell - see above. Listed so the corpus total adds up.

| # | document | share@5px | share@10px | max_pt | text recall | pages | signature |
|---|---|---|---|---|---|---|---|
| 1 | `34_monospace_document` | 0.93 % | 0.0 % | 4.8 | 100.0 % | 1 | clean |
| 2 | `eway-bill` | 0.91 % | 0.86 % | 31.2 | 100.0 % | 1 | clean |
| 3 | `67_two_col_with_sidebar` | 0.8 % | 0.54 % | 11.52 | 100.0 % | 1 | clean |
| 4 | `28_value_overflows_cell_txtpos` | 0.74 % | 0.5 % | 15.36 | 100.0 % | 1 | clean |
| 5 | `79_inr_indian_digit_grouping_table` | 0.74 % | 0.35 % | 9.12 | 98.43 % | 1 | clean |
| 6 | `39_small_caps_letter_spacing` | 0.72 % | 0.0 % | 4.8 | 100.0 % | 1 | clean |
| 7 | `326_itr_computation` | 0.63 % | 0.46 % | 13.92 | 100.0 % | 1 | clean |
| 8 | `344_customs_declaration` | 0.61 % | 0.59 % | 49.92 | 100.0 % | 1 | clean |
| 9 | `table-with-no-header-row` | 0.61 % | 0.26 % | 11.52 | 100.0 % | 1 | clean |
| 10 | `37_font_not_embedded_substitution` | 0.58 % | 0.35 % | 14.4 | 100.0 % | 1 | clean |
| 11 | `balance-sheet-two-columns-of-figures` | 0.57 % | 0.06 % | 5.76 | 99.92 % | 1 | clean |
| 12 | `question-paper-marks-right-margin` | 0.44 % | 0.23 % | 14.88 | 100.0 % | 1 | clean |
| 13 | `413_tagged_pdf_actualtext` | 0.38 % | 0.0 % | 3.84 | 100.0 % | 1 | clean |
| 14 | `383_api_docs_page` | 0.3 % | 0.2 % | 19.68 | 100.0 % | 1 | clean |
| 15 | `bus-timetable-station-left-times-right` | 0.27 % | 0.13 % | 12.96 | 100.0 % | 1 | clean |
| 16 | `404_sudoku_grid` | 0.27 % | 0.0 % | 3.36 | 100.0 % | 1 | clean |
| 17 | `364_event_ticket` | 0.25 % | 0.0 % | 2.88 | 100.0 % | 1 | clean |
| 18 | `343_air_waybill` | 0.23 % | 0.16 % | 14.88 | 100.0 % | 1 | clean |
| 19 | `admission-form-labels-left-boxes-right` | 0.21 % | 0.0 % | 4.32 | 100.0 % | 1 | clean |
| 20 | `05_round_company_seal_curved_text` | 0.19 % | 0.01 % | 5.28 | 100.0 % | 1 | clean |
| 21 | `boq-horizontal-rules-only` | 0.13 % | 0.08 % | 8.64 | 100.0 % | 1 | clean |
| 22 | `350_question_paper` | 0.11 % | 0.1 % | 16.8 | 100.0 % | 1 | clean |
| 23 | `08_two_overlapping_stamps` | 0.11 % | 0.05 % | 11.04 | 100.0 % | 1 | clean |
| 24 | `391_survey_questionnaire_grid` | 0.11 % | 0.0 % | 4.32 | 99.58 % | 1 | clean |
| 25 | `333_datasheet_spec_tables` | 0.07 % | 0.02 % | 6.24 | 100.0 % | 1 | clean |
| 26 | `340_bill_of_lading` | 0.07 % | 0.0 % | 3.36 | 100.0 % | 1 | clean |
| 27 | `300_prescription_rx` | 0.06 % | 0.05 % | 21.6 | 100.0 % | 1 | clean |
| 28 | `60_page_border` | 0.06 % | 0.01 % | 8.16 | 100.0 % | 1 | clean |
| 29 | `12_stamp_across_page_break` | 0.05 % | 0.0 % | 3.36 | 100.0 % | 2 | clean |
| 30 | `45_coloured_callout_box` | 0.05 % | 0.0 % | 3.36 | 100.0 % | 1 | clean |
| 31 | `401_trifold_brochure` | 0.03 % | 0.01 % | 10.56 | 100.0 % | 1 | clean |
| 32 | `25_signature_block_underscores_txtpos` | 0.03 % | 0.01 % | 10.08 | 100.0 % | 1 | clean |
| 33 | `15_stamp_on_scanned_page` | 0.03 % | 0.0 % | 3.36 | 100.0 % | 1 | clean |
| 34 | `362_price_list_dense` | 0.03 % | 0.0 % | 3.36 | 100.0 % | 1 | clean |
| 35 | `390_wide_data_appendix` | 0.03 % | 0.0 % | 3.36 | 100.0 % | 1 | clean |
| 36 | `74_balance_sheet_indented_subitems` | 0.03 % | 0.0 % | 3.36 | 100.0 % | 1 | clean |
| 37 | `301_lab_report_panel` | 0.02 % | 0.01 % | 7.2 | 100.0 % | 1 | clean |
| 38 | `44_coloured_underlined_hyperlinks` | 0.02 % | 0.0 % | 3.84 | 100.0 % | 1 | clean |
| 39 | `20_numbered_list_separate_column_txtpos` | 0.02 % | 0.0 % | 2.88 | 100.0 % | 1 | clean |
| 40 | `365_recipe_card` | 0.02 % | 0.0 % | 2.88 | 100.0 % | 1 | clean |
| 41 | `13_stamp_non_english` | 0.01 % | 0.0 % | 3.84 | 100.0 % | 1 | clean |
| 42 | `26_footnote_marker_bottom_note_txtpos` | 0.01 % | 0.0 % | 3.84 | 100.0 % | 1 | clean |
| 43 | `375_attendance_register` | 0.01 % | 0.0 % | 3.84 | 100.0 % | 1 | clean |
| 44 | `393_spectrum_peak_table` | 0.01 % | 0.0 % | 3.36 | 100.0 % | 1 | clean |
| 45 | `38_faux_bold_italic_synthesised` | 0.01 % | 0.0 % | 2.88 | 98.01 % | 1 | clean |
| 46 | `46_chart_coloured_labels_body_text` | 0.01 % | 0.0 % | 2.88 | 100.0 % | 1 | clean |
| 47 | `342_packing_list` | 0.0 % | 0.0 % | 3.36 | 100.0 % | 1 | clean |
| 48 | `407_id_card_front_back` | 0.0 % | 0.0 % | 3.36 | 100.0 % | 1 | clean |
| 49 | `56_table_indented_from_margin` | 0.0 % | 0.0 % | 3.36 | 100.0 % | 1 | clean |
| 50 | `02_stamp_rotated_15deg_upleft` | 0.0 % | 0.0 % | 2.88 | 100.0 % | 1 | clean |
| 51 | `323_credit_card_statement` | 0.0 % | 0.0 % | 2.88 | 100.0 % | 1 | clean |
| 52 | `325_demat_holdings_statement` | 0.0 % | 0.0 % | 2.88 | 100.0 % | 1 | clean |
| 53 | `335_msds_safety_data_sheet` | 0.0 % | 0.0 % | 2.88 | 100.0 % | 1 | clean |
| 54 | `353_admit_card` | 0.0 % | 0.0 % | 2.88 | 100.0 % | 1 | clean |
| 55 | `381_incident_report_timeline` | 0.0 % | 0.0 % | 2.88 | 100.0 % | 1 | clean |
| 56 | `403_crossword_puzzle` | 0.0 % | 0.0 % | 2.88 | 100.0 % | 1 | clean |
| 57 | `01_stamp_rotated_15deg_upright` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 58 | `10_stamp_as_image` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 59 | `16_right_aligned_amounts_txtpos` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 60 | `17_three_column_widths_txtpos` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 61 | `18_centred_heading_left_body_txtpos` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 62 | `19_hanging_indent_txtpos` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 63 | `21_form_labels_x60_values_x300_txtpos` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 64 | `29_dot_leaders_txtpos` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 65 | `306_clinical_protocol_synopsis` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 66 | `311_fir_police_form` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 67 | `314_tender_rfp_boq` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 68 | `318_court_summons_form` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 69 | `320_balance_sheet_statutory` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 70 | `324_loan_amortisation_schedule` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 7 | clean |
| 71 | `331_pid_diagram` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 72 | `332_bom_on_drawing` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 73 | `341_shipping_manifest` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 74 | `36_embedded_subset_font` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 75 | `373_leave_application_form` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 76 | `402_calendar_month_grid` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 77 | `42_table_coloured_header_alternating_rows` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 78 | `50_invoice_coloured_total_row` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 79 | `51_two_cm_margins` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 80 | `52_one_cm_margin_wide_body` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 81 | `55_sidebar_box_beside_body` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 82 | `62_two_col_newsletter_pull_quote` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 83 | `63_three_column_brochure` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 84 | `72_bank_statement_no_rules_right_amounts` | 0.0 % | 0.0 % | 2.4 | 100.0 % | 1 | clean |
| 85 | `04_stamp_180deg_upside_down` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 86 | `06_rect_paid_stamp_red_transparent` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 87 | `24_address_block_indents_txtpos` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 88 | `302_radiology_report` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 89 | `303_discharge_summary` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 90 | `334_patent_document` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 91 | `351_omr_answer_sheet` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 92 | `371_experience_certificate` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 93 | `394_map_with_legend` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 94 | `43_red_stamp_over_black_text` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 95 | `49_coloured_background_block_paragraph` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 96 | `53_single_space_body_15_headings` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 1 | clean |
| 97 | `57_centred_title_page_left_body_pages` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 2 | clean |
| 98 | `59_landscape_mixed_portrait` | 0.0 % | 0.0 % | 1.92 | 100.0 % | 2 | clean |
| 99 | `09_stamp_font_not_embedded` | 0.0 % | 0.0 % | 1.44 | 100.0 % | 1 | clean |
| 100 | `22_invoice_four_columns_txtpos` | 0.0 % | 0.0 % | 1.44 | 100.0 % | 1 | clean |
| 101 | `305_vaccination_certificate` | 0.0 % | 0.0 % | 1.44 | 100.0 % | 1 | clean |
| 102 | `30_mixed_font_sizes_one_baseline_txtpos` | 0.0 % | 0.0 % | 1.44 | 100.0 % | 1 | clean |
| 103 | `322_mutual_fund_factsheet` | 0.0 % | 0.0 % | 1.44 | 100.0 % | 1 | clean |
| 104 | `400_comic_page_speech_bubbles` | 0.0 % | 0.0 % | 1.44 | 100.0 % | 1 | clean |
| 105 | `41_coloured_headings_white_bg` | 0.0 % | 0.0 % | 1.44 | 100.0 % | 1 | clean |
| 106 | `48_form_coloured_border_coloured_values` | 0.0 % | 0.0 % | 1.44 | 100.0 % | 1 | clean |
| 107 | `58_header_rule_footer_rule` | 0.0 % | 0.0 % | 1.44 | 100.0 % | 2 | clean |
| 108 | `73_marksheet_subject_marks_grade` | 0.0 % | 0.0 % | 1.44 | 100.0 % | 1 | clean |
| 109 | `32_serif_nondefault_body` | 0.0 % | 0.0 % | 0.96 | 100.0 % | 1 | clean |
| 110 | `372_timesheet_grid` | 0.0 % | 0.0 % | 0.96 | 100.0 % | 1 | clean |
| 111 | `380_runbook_terminal_output` | 0.0 % | 0.0 % | 0.96 | 100.0 % | 1 | clean |
| 112 | `405_sheet_music_lyrics` | 0.0 % | 0.0 % | 0.96 | 100.0 % | 1 | clean |
| 113 | `410_form_xobject_reused` | 0.0 % | 0.0 % | 0.96 | 100.0 % | 1 | clean |
| 114 | `416_many_tiny_pages` | 0.0 % | 0.0 % | 0.96 | 100.0 % | 300 | clean |
| 115 | `47_grey_body_black_headings` | 0.0 % | 0.0 % | 0.96 | 100.0 % | 1 | clean |
| 116 | `54_two_column_body_full_width_header_footer` | 0.0 % | 0.0 % | 0.96 | 100.0 % | 1 | clean |
| 117 | `602_bookmarked_annual_report` | 0.0 % | 0.0 % | 0.96 | 100.0 % | 3 | clean |
| 118 | `361_product_catalogue_grid` | 0.0 % | 0.0 % | 0.0 | 100.0 % | 1 | clean |
| 119 | `382_architecture_diagram` | 0.0 % | 0.0 % | 0.0 | 100.0 % | 1 | clean |
| 120 | `412_page_labels_roman` | 0.0 % | 0.0 % | 0.0 | 100.0 % | 5 | clean |
| 121 | `414_transparency_softmask` | 0.0 % | 0.0 % | 0.0 | 100.0 % | 1 | clean |

### unmeasured - 0 documents

Zero this run. The previous classification carried one `MEASURE-ERROR` row, `416_many_tiny_pages`; it scored this run at 0.00 %@5 across 300 pages and now sits in `none`. A document that failed to measure would rank last here regardless of how bad it looks: fix the measurement before judging the document.

| # | document | share@5px | note | status |
|---|---|---|---|---|
| - | none | - | every row of RANKING.csv carries a numeric share@5px | - |

## The real world outranks this corpus - and it is the highest-value defect in the project

This run's 211 rows read a median `share@5px` of **0.27 %**, with 121 of them clean - the synthetic set alone reads 0.3 %, as recorded in `REALWORLD-FINDINGS.md`. The nine real documents measured in that report read **median 10.3 %** on the same instrument and the same engine: 34x worse. Text recall is 99.7-100 % on every one of them. The words come through; the layout does not.

| # | document | problem | share@5px | max_pt | text recall | pages | status |
|---|---|---|---|---|---|---|---|
| 1 | `041122-Account_Opening_Form` | content-missing-partly-replaced | 98.65 % | 937.92 | 99.68 % | 9 | OPEN |
| 2 | `Account_Opening_Form_Fillable_filled` | content-missing-partly-replaced | 97.62 % | 358.08 | 99.67 % | 9 | OPEN |
| 3 | `property-tax-receipt` | content-missing-nothing-in-its-place | 10.78 % | 55.68 | 100.0 % | 1 | see class above |
| 4 | `admit-card` | content-missing-nothing-in-its-place | 10.68 % | 57.12 | 100.0 % | 1 | see class above |
| 5 | `delivery-challan` | content-missing-nothing-in-its-place | 10.26 % | 39.84 | 100.0 % | 1 | see class above |
| 6 | `gst-invoice-3line-items` | content-missing-nothing-in-its-place | 7.15 % | 20.16 | 100.0 % | 1 | see class above |
| 7 | `350_question_paper` | none | 0.11 % | 16.8 | 100.0 % | 1 | see class above |
| 8 | `300_prescription_rx` | none | 0.06 % | 21.6 | 100.0 % | 1 | see class above |
| 9 | `311_fir_police_form` | none | 0.0 % | 2.4 | 100.0 % | 1 | see class above |

Read that table with three things in mind:

1. **The two nine-page bank forms are the highest-value defect in the project, and they outrank `415_inline_images`.** `415_inline_images` is one synthetic document. `041122-Account_Opening_Form` (98.65 %@5, max 937.92 pt - 33 cm, larger than the page) and `Account_Opening_Form_Fillable_filled` (97.62 %@5) are a document type users open constantly, and on them 98 % of the source ink has no counterpart in our output at 5 px.
2. **They are in the corpus but not in this run's `RANKING.csv`.** The PDFs ship in `benchmarks/realworld/`, so a future measurement will list them as ordinary rows. This run's ranking does not contain them - the numbers above come from `REALWORLD-RANKING.csv`. Do not average the two populations: synthetic median 0.3 %, real median 10.3 %.
3. **Never quote the synthetic median as if it described the product.** Quote both. A corpus of single-page synthetic tables cannot see a nine-page form with repeated field grids, which is exactly the shape that fails.

## One caveat this classification carries forward

`one-page-rotated-180-degrees` is classed `content-missing-partly-replaced` at 81.64 %@5 with **text recall 100 %**. Both facts are true and neither is wrong: the source page is an upside-down **scan** and our output is typeset text, so the ink cannot match because it is a different medium. Nothing was lost - the ink changed form. It is `PARKED` here for that reason. **Do not hand this to the fixer as an ink defect**: a fixer that chases 81 % of ink on this page will damage a document whose text is already complete.

## What this file does not say

It names the KIND of defect and sizes it. It does not say WHY the engine did it. "Inline images are not extracted" came from looking at a rendered pair (`p2w.py --diagnose`), not from these numbers. The name narrows the search; the fixer still has to find the cause. Nothing here is a fix, and nothing here may be read as one.

_Generated by the classify step of the PDF-to-Word pipeline. Measurement: `benchmarks/RANKING.csv` (this run). Engine untouched. Ranking untouched._
