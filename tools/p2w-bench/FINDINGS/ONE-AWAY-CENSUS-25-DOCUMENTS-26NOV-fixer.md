# 42 documents are one check from clean, and 25 of them are `18_displacement`

**Measured 26 Nov 2026** from `benchmarks/gverify/*.json`, restricted to the 205 records that carry a
verdict on this tree's engine `025fe9deda5ac7b1` (the store was re-measured by the gverify cron while
this run was working: it held 142 such records at 20:40 IST and 205 at 21:05). No new render was made;
this is a census of what the store already holds.

## Failing-count histogram (205 documents on this engine)

| checks failing | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| documents | 47 | 42 | 42 | 19 | 19 | 13 | 7 | 9 | 2 | 5 |

## The 42 one-check-away documents, by the check they fail

| check | documents |
|:--|--:|
| `18_displacement` | **25** |
| `60_text_column_right_edge` | 6 |
| `59_shape_anchor` | 3 |
| `47_margins` | 3 |
| `32_stroke_lines` | 2 |
| `17_matched_runs`, `26_text_overlap`, `52_outline` | 1 each |

## `18_displacement`: 14 of the 25 are within 7 pt at their worst run

`worst_dy` and `med_dy` for every one of the 25, from each record's own `displacement` block:

| worst_dy | med_dy | runs | document |
|--:|--:|--:|:--|
| 3.3 | 3.0 | 24 | 70_magazine_drop_cap_photo_caption |
| 3.4 | -1.6 | 64 | 16_right_aligned_amounts_txtpos |
| 3.5 | 1.7 | 29 | 36_embedded_subset_font |
| 3.5 | 2.6 | 29 | 31_times_body_arial_headings |
| 3.8 | 1.8 | 177 | bus-timetable-station-left-times-right |
| 4.1 | -0.2 | 45 | 303_discharge_summary |
| 4.2 | 2.2 | 54 | 74_balance_sheet_indented_subitems |
| 4.8 | 1.1 | 80 | 72_bank_statement_no_rules_right_amounts |
| 5.1 | -2.3 | 94 | balance-sheet-two-columns-of-figures |
| 5.3 | 2.1 | 253 | price-list-2col-dense-right-aligned |
| 5.4 | -2.8 | 257 | 362_price_list_dense |
| 6.5 | 1.4 | 46 | 402_calendar_month_grid |
| 6.7 | 1.1 | 72 | 71_invoice_space_aligned_no_rules |
| 6.8 | 2.8 | 90 | report-2col-table-spanning-both-columns |
| 7.3 | 1.7 | 72 | two-tables-stacked-with-no-gap |
| 9.0 | -0.5 | 215 | table-with-no-header-row |
| 9.2 | -6.0 | 112 | mobile-bill |
| 9.8 | -6.3 | 107 | insurance-policy-schedule |
| 10.4 | -7.2 | 125 | electricity-bill |
| 10.8 | 1.6 | 468 | table-across-page-break-repeated-header |
| 12.2 | -10.2 | 27 | 403_crossword_puzzle |
| 18.5 | 8.0 | 64 | table-inside-two-column-page |
| 19.4 | 8.2 | 73 | 320_balance_sheet_statutory |
| 28.7 | -1.8 | 585 | bank-statement-5-pages |
| 38.1 | 3.8 | 84 | 325_demat_holdings_statement |

**The first 14 cannot be failing on the tail clause.** The tail fires at `|dy| > 2 * _tol`, and `_tol =
clamp(0.35*size, 1.5, 4.5)` — for a 9 pt run that is 3.15 and the tail needs 6.3, for a 10 pt run 3.5
and 7.0. A document whose *worst* run is 3.3-6.8 pt therefore has no run anywhere near its own tail
threshold on any run of ordinary size, and it is failing on the **count clause**:
`n_out > max(2, ceil(5% of runs))`, i.e. three or four runs a point or two out is enough. That is a
different question from the spacer-spend arm the last two runs measured, which moved `med_dy` and the
tail.

## `60_text_column_right_edge`: all six are the DejaVu set

Four (302, 313, 316, 321) are the set measured on 24 Nov in
`60_text_column_right_edge-GOOGLE-HAS-NO-DEJAVU-0830-fixer.md`: Google has no DejaVu, substitutes a
face 4.8 % wider, and neither naming a Google face nor embedding the source face moves the export
(both measured live). **`335_msds_safety_data_sheet` and `79_inr_indian_digit_grouping_table` are the
fifth and sixth, and `335` is new to the list — it is DejaVu too:**

    pages 1   fonts AAAAAA+DejaVuSans, AAAAAA+DejaVuSans-Bold, AAAAAA+DejaVuSerif, Helvetica
    verdict 46/47, med_dy -0.4 worst_dy 3.0 bad_pages []

The layout is right and the column edge moved, which is the substitution signature. So `60`'s
one-away population is parked as *Google cannot do it* and `60` is not where the clean documents are.
