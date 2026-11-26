# 25 documents are one check from clean, and the largest single block is 18_displacement

**Measured 26 Nov 2026** from `benchmarks/gverify/*.json`, restricted to the 142 records whose
`engine` is this tree's `025fe9deda5ac7b1`. No new render was made; this is a census of what the
store already holds on the current engine.

## Failing-count histogram (142 documents on this engine)

| checks failing | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| documents | 42 | 25 | 24 | 12 | 15 | 9 | 4 | 6 | 1 | 4 |

## The 25 one-check-away documents, by the check they fail

| check | documents | documents named |
|:--|--:|:--|
| `18_displacement` | **9** | 16_right_aligned_amounts_txtpos, 303_discharge_summary, 31_times_body_arial_headings, 320_balance_sheet_statutory, 325_demat_holdings_statement, 362_price_list_dense, 36_embedded_subset_font, 402_calendar_month_grid, 403_crossword_puzzle, bank-statement-5-pages |
| `60_text_column_right_edge` | 5 | 302_radiology_report, 313_power_of_attorney, 316_contract_with_schedules, 321_auditors_report, 335_msds_safety_data_sheet |
| `59_shape_anchor` | 3 | 351_omr_answer_sheet, 48_form_coloured_border_coloured_values, 52_one_cm_margin_wide_body |
| `32_stroke_lines` | 2 | 407_id_card_front_back, 49_coloured_background_block_paragraph |
| `47_margins` | 2 | 380_runbook_terminal_output, 392_statistical_console_output |
| others | 4 | 17_matched_runs, 26_text_overlap, 52_outline, one each |

## 60_text_column_right_edge has no workable one-away document

Four of the five (302, 313, 316, 321) are the DejaVu-substitution set measured on 24 Nov in
`60_text_column_right_edge-GOOGLE-HAS-NO-DEJAVU-0830-fixer.md`: Google has no DejaVu, substitutes a
face 4.8 % wider, and neither naming a Google face nor embedding the source face moves the export
(both measured live). **`335_msds_safety_data_sheet` is new to that list and is the fifth of five:**

    python3 -c "import fitz; d=fitz.open('.../335_msds_safety_data_sheet.pdf'); ..."
    pages 1   fonts AAAAAA+DejaVuSans, AAAAAA+DejaVuSans-Bold, AAAAAA+DejaVuSerif, Helvetica

It fails only `60` at 46/47 with `med_dy -0.4 worst_dy 3.0 bad_pages []` — the layout is right and the
column edge moved, which is the same substitution signature. So the class's whole one-away population
is parked as *Google cannot do it*, and `60` is not where the clean documents are.

## The number this gives the next run

`18_displacement` holds **9 of the 25**, and six of those nine are within 6.5 pt at their worst run
(`31_times_body_arial_headings` 3.5, `36_embedded_subset_font` 3.5, `16_right_aligned_amounts_txtpos`
3.4, `303_discharge_summary` 4.1, `362_price_list_dense` 5.4, `402_calendar_month_grid` 6.5). With
`_tol = clamp(0.35*size, 1.5, 4.5)` those documents are failing on the **count clause**
(`n_out > max(2, ceil(5% of runs))`), not on the tail — three or four runs a point or two out is
enough. That is a different question from the spacer-spend arm the last two runs measured, which moved
`med_dy` and the tail.
