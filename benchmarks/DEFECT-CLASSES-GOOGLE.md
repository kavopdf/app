# Defect classes — GOOGLE's, not LibreOffice's

Generated from `benchmarks/gverify/` and `benchmarks/gverify-lo/`: **84 documents with both**
renders, same engine, same instrument. Regenerated every classify run.

Every other class table comes from `RANKING.csv`, a soffice render — a renderer no user opens.
**A check LibreOffice passes and Google fails appears in no other table.**

`round.py --close-round` reads this file. A round cannot close while a row here says OPEN, which
is the point: the pipeline must not move on with 53 documents still broken in the renderer the
user actually opens.

## Classes, ranked by gap

| signature | problem | open | fixed | libreoffice | google |
|---|---|---:|---:|---:|---:|
| `32_stroke_lines` | 32_stroke_lines | 53 | 0 | 0 | 53 |
| `05_chars_extra` | 05_chars_extra | 54 | 0 | 6 | 54 |
| `18_displacement` | 18_displacement | 46 | 0 | 4 | 46 |
| `04_chars_missing` | 04_chars_missing | 30 | 0 | 6 | 30 |
| `59_shape_anchor` | 59_shape_anchor | 26 | 0 | 4 | 26 |
| `13_text_colours` | 13_text_colours | 18 | 0 | 0 | 18 |
| `25_invisible_text` | 25_invisible_text | 17 | 0 | 1 | 17 |
| `47_margins` | 47_margins | 13 | 0 | 3 | 13 |
| `45_char_accuracy` | 45_char_accuracy | 15 | 0 | 6 | 15 |
| `17_matched_runs` | 17_matched_runs | 16 | 0 | 7 | 16 |
| `27_text_off_page` | 27_text_off_page | 7 | 0 | 3 | 7 |
| `43_within_10pt_x` | 43_within_10pt_x | 6 | 0 | 3 | 6 |
| `60_text_column_right_edge` | 60_text_column_right_edge | 18 | 0 | 15 | 18 |
| `44_header_footer` | 44_header_footer | 7 | 0 | 4 | 7 |
| `34a_span_size_match` | 34a_span_size_match | 2 | 0 | 0 | 2 |
| `31_pages_lost_their_text` | 31_pages_lost_their_text | 1 | 0 | 0 | 1 |
| `10_font_sizes` | 10_font_sizes | 2 | 0 | 1 | 2 |
| `42_justification_edges` | 42_justification_edges | 1 | 0 | 0 | 1 |
| `38_list_markers` | 38_list_markers | 1 | 0 | 0 | 1 |
| `46_text_crossing_rule` | 46_text_crossing_rule | 1 | 0 | 0 | 1 |
| `51_field_values` | 51_field_values | 1 | 0 | 0 | 1 |

## The one fix behind the top two rows

`32_stroke_lines` and `05_chars_extra` are the same construct. A horizontal rule is emitted as a
floating `<w:drawing>`; Google drops the shape and keeps the anchor — the missing rule is
`32_stroke_lines`, the anchor is the `U+200B` that `05_chars_extra` counts.

**Fix them as one class.** See `FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md` and
`FINDINGS/RULES-PBDR-IMPLEMENTATION.md`.

## Documents per class

### `32_stroke_lines` — 53 documents

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `09_stamp_font_not_embedded`, `10_stamp_as_image`, `11_stamp_with_signature_image` …

### `05_chars_extra` — 54 documents

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `09_stamp_font_not_embedded`, `10_stamp_as_image`, `11_stamp_with_signature_image` …

### `18_displacement` — 46 documents

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `10_stamp_as_image`, `13_stamp_non_english`, `14_stamp_chars_positioned_td` …

### `04_chars_missing` — 30 documents

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `09_stamp_font_not_embedded`, `11_stamp_with_signature_image`, `13_stamp_non_english` …

### `59_shape_anchor` — 26 documents

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `09_stamp_font_not_embedded`, `10_stamp_as_image`, `13_stamp_non_english` …

### `13_text_colours` — 18 documents

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `09_stamp_font_not_embedded`, `11_stamp_with_signature_image`, `13_stamp_non_english` …

### `25_invisible_text` — 17 documents

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `04_stamp_180deg_upside_down`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `10_stamp_as_image`, `14_stamp_chars_positioned_td`, `300_prescription_rx`, `303_discharge_summary`, `306_clinical_protocol_synopsis` …

### `47_margins` — 13 documents

`07_stamp_over_table`, `21_form_labels_x60_values_x300_txtpos`, `28_value_overflows_cell_txtpos`, `317_rti_response`, `318_court_summons_form`, `330_cad_drawing_sheet`, `331_pid_diagram`, `380_runbook_terminal_output`, `392_statistical_console_output`, `40_devanagari_shaping_font` …

### `45_char_accuracy` — 15 documents

`08_two_overlapping_stamps`, `11_stamp_with_signature_image`, `13_stamp_non_english`, `14_stamp_chars_positioned_td`, `15_stamp_on_scanned_page`, `20_numbered_list_separate_column_txtpos`, `25_signature_block_underscores_txtpos`, `28_value_overflows_cell_txtpos`, `311_fir_police_form`, `318_court_summons_form` …

### `17_matched_runs` — 16 documents

`08_two_overlapping_stamps`, `11_stamp_with_signature_image`, `13_stamp_non_english`, `15_stamp_on_scanned_page`, `20_numbered_list_separate_column_txtpos`, `312_affidavit_stamp_paper`, `318_court_summons_form`, `322_mutual_fund_factsheet`, `323_credit_card_statement`, `331_pid_diagram` …

### `27_text_off_page` — 7 documents

`12_stamp_across_page_break`, `324_loan_amortisation_schedule`, `412_page_labels_roman`, `417_rotate180_and_mirrored`, `57_centred_title_page_left_body_pages`, `58_header_rule_footer_rule`, `602_bookmarked_annual_report`

### `43_within_10pt_x` — 6 documents

`07_stamp_over_table`, `21_form_labels_x60_values_x300_txtpos`, `28_value_overflows_cell_txtpos`, `318_court_summons_form`, `77_arabic_rtl_document`, `78_mixed_english_devanagari_line`

### `60_text_column_right_edge` — 18 documents

`14_stamp_chars_positioned_td`, `25_signature_block_underscores_txtpos`, `28_value_overflows_cell_txtpos`, `302_radiology_report`, `311_fir_police_form`, `312_affidavit_stamp_paper`, `313_power_of_attorney`, `314_tender_rfp_boq`, `316_contract_with_schedules`, `317_rti_response` …

### `44_header_footer` — 7 documents

`15_stamp_on_scanned_page`, `20_numbered_list_separate_column_txtpos`, `27_two_column_left_short_txtpos`, `322_mutual_fund_factsheet`, `331_pid_diagram`, `57_centred_title_page_left_body_pages`, `58_header_rule_footer_rule`

### `34a_span_size_match` — 2 documents

`40_devanagari_shaping_font`, `76_devanagari_table`

### `31_pages_lost_their_text` — 1 documents

`15_stamp_on_scanned_page`

### `10_font_sizes` — 2 documents

`15_stamp_on_scanned_page`, `331_pid_diagram`

### `42_justification_edges` — 1 documents

`314_tender_rfp_boq`

### `38_list_markers` — 1 documents

`40_devanagari_shaping_font`

### `46_text_crossing_rule` — 1 documents

`44_coloured_underlined_hyperlinks`

### `51_field_values` — 1 documents

`601_fillable_admission_form`

