# Defect classes — GOOGLE's, not LibreOffice's

Generated from `benchmarks/gverify/` and `benchmarks/gverify-lo/`: **84 documents with both**

renders, same engine, same instrument.

Every other class table in this repository comes from `RANKING.csv`, which is a soffice render — a
renderer no user opens. **A check that LibreOffice passes and Google fails appears in no other
table, and the fixer can never be sent to fix it.**

## Ranked by GAP — how many more documents Google fails than LibreOffice

Not "only Google": `05_chars_extra` fails 6 in LibreOffice too, and its gap of 48 is the second
largest in the corpus. Ranking by "only" would have hidden it.

| check | LibreOffice | Google | gap | documents |
|---|---:|---:|---:|---:|
| `32_stroke_lines` | 0 | **53** | **53** | 53 |
| `05_chars_extra` | 6 | **54** | **48** | 54 |
| `18_displacement` | 4 | **46** | **42** | 46 |
| `04_chars_missing` | 6 | **30** | **24** | 30 |
| `59_shape_anchor` | 4 | **26** | **22** | 26 |
| `13_text_colours` | 0 | **18** | **18** | 18 |
| `25_invisible_text` | 1 | **17** | **16** | 17 |
| `47_margins` | 3 | **13** | **10** | 13 |
| `45_char_accuracy` | 6 | **15** | **9** | 15 |
| `17_matched_runs` | 7 | **16** | **9** | 16 |
| `27_text_off_page` | 3 | **7** | **4** | 7 |
| `43_within_10pt_x` | 3 | **6** | **3** | 6 |
| `60_text_column_right_edge` | 15 | **18** | **3** | 18 |
| `44_header_footer` | 4 | **7** | **3** | 7 |
| `34a_span_size_match` | 0 | **2** | **2** | 2 |
| `31_pages_lost_their_text` | 0 | **1** | **1** | 1 |
| `10_font_sizes` | 1 | **2** | **1** | 2 |
| `42_justification_edges` | 0 | **1** | **1** | 1 |
| `38_list_markers` | 0 | **1** | **1** | 1 |
| `46_text_crossing_rule` | 0 | **1** | **1** | 1 |
| `51_field_values` | 0 | **1** | **1** | 1 |

## The one fix behind the top two rows

`32_stroke_lines` (gap 53) and `05_chars_extra` (gap 48) are the same construct. A horizontal rule
is emitted as a floating `<w:drawing>`; Google does not lay out an imported floating drawing, so it
drops the shape and keeps the anchor — the missing rule is `32_stroke_lines`, and the anchor is the
`U+200B` that `05_chars_extra` counts.

See `FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`. **Do not treat them as two classes.** Fixing
the construct fixes both, and together they are the largest block in the corpus.

`13_text_colours` (gap 18) is the third: a colour Google drops on import. Nothing else in the
repository measures it, because LibreOffice carries every colour faithfully.

## Every check, with the documents that fail it

### `32_stroke_lines` — 53 documents (LibreOffice fails 0)

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `09_stamp_font_not_embedded`, `10_stamp_as_image`, `11_stamp_with_signature_image` …

### `05_chars_extra` — 54 documents (LibreOffice fails 6)

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `09_stamp_font_not_embedded`, `10_stamp_as_image`, `11_stamp_with_signature_image` …

### `18_displacement` — 46 documents (LibreOffice fails 4)

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `10_stamp_as_image`, `13_stamp_non_english`, `14_stamp_chars_positioned_td` …

### `04_chars_missing` — 30 documents (LibreOffice fails 6)

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `09_stamp_font_not_embedded`, `11_stamp_with_signature_image`, `13_stamp_non_english` …

### `59_shape_anchor` — 26 documents (LibreOffice fails 4)

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `09_stamp_font_not_embedded`, `10_stamp_as_image`, `13_stamp_non_english` …

### `13_text_colours` — 18 documents (LibreOffice fails 0)

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `09_stamp_font_not_embedded`, `11_stamp_with_signature_image`, `13_stamp_non_english` …

### `25_invisible_text` — 17 documents (LibreOffice fails 1)

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `04_stamp_180deg_upside_down`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `10_stamp_as_image`, `14_stamp_chars_positioned_td`, `300_prescription_rx`, `303_discharge_summary`, `306_clinical_protocol_synopsis` …

### `47_margins` — 13 documents (LibreOffice fails 3)

`07_stamp_over_table`, `21_form_labels_x60_values_x300_txtpos`, `28_value_overflows_cell_txtpos`, `317_rti_response`, `318_court_summons_form`, `330_cad_drawing_sheet`, `331_pid_diagram`, `380_runbook_terminal_output`, `392_statistical_console_output`, `40_devanagari_shaping_font` …

### `45_char_accuracy` — 15 documents (LibreOffice fails 6)

`08_two_overlapping_stamps`, `11_stamp_with_signature_image`, `13_stamp_non_english`, `14_stamp_chars_positioned_td`, `15_stamp_on_scanned_page`, `20_numbered_list_separate_column_txtpos`, `25_signature_block_underscores_txtpos`, `28_value_overflows_cell_txtpos`, `311_fir_police_form`, `318_court_summons_form` …

### `17_matched_runs` — 16 documents (LibreOffice fails 7)

`08_two_overlapping_stamps`, `11_stamp_with_signature_image`, `13_stamp_non_english`, `15_stamp_on_scanned_page`, `20_numbered_list_separate_column_txtpos`, `312_affidavit_stamp_paper`, `318_court_summons_form`, `322_mutual_fund_factsheet`, `323_credit_card_statement`, `331_pid_diagram` …

### `27_text_off_page` — 7 documents (LibreOffice fails 3)

`12_stamp_across_page_break`, `324_loan_amortisation_schedule`, `412_page_labels_roman`, `417_rotate180_and_mirrored`, `57_centred_title_page_left_body_pages`, `58_header_rule_footer_rule`, `602_bookmarked_annual_report`

### `43_within_10pt_x` — 6 documents (LibreOffice fails 3)

`07_stamp_over_table`, `21_form_labels_x60_values_x300_txtpos`, `28_value_overflows_cell_txtpos`, `318_court_summons_form`, `77_arabic_rtl_document`, `78_mixed_english_devanagari_line`

### `60_text_column_right_edge` — 18 documents (LibreOffice fails 15)

`14_stamp_chars_positioned_td`, `25_signature_block_underscores_txtpos`, `28_value_overflows_cell_txtpos`, `302_radiology_report`, `311_fir_police_form`, `312_affidavit_stamp_paper`, `313_power_of_attorney`, `314_tender_rfp_boq`, `316_contract_with_schedules`, `317_rti_response` …

### `44_header_footer` — 7 documents (LibreOffice fails 4)

`15_stamp_on_scanned_page`, `20_numbered_list_separate_column_txtpos`, `27_two_column_left_short_txtpos`, `322_mutual_fund_factsheet`, `331_pid_diagram`, `57_centred_title_page_left_body_pages`, `58_header_rule_footer_rule`

### `34a_span_size_match` — 2 documents (LibreOffice fails 0)

`40_devanagari_shaping_font`, `76_devanagari_table`

### `31_pages_lost_their_text` — 1 documents (LibreOffice fails 0)

`15_stamp_on_scanned_page`

### `10_font_sizes` — 2 documents (LibreOffice fails 1)

`15_stamp_on_scanned_page`, `331_pid_diagram`

### `42_justification_edges` — 1 documents (LibreOffice fails 0)

`314_tender_rfp_boq`

### `38_list_markers` — 1 documents (LibreOffice fails 0)

`40_devanagari_shaping_font`

### `46_text_crossing_rule` — 1 documents (LibreOffice fails 0)

`44_coloured_underlined_hyperlinks`

### `51_field_values` — 1 documents (LibreOffice fails 0)

`601_fillable_admission_form`

### `35_rotation` — 12 documents (LibreOffice fails 12)

`01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down`, `06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`, `09_stamp_font_not_embedded`, `11_stamp_with_signature_image`, `13_stamp_non_english` …

### `63_table_rows` — 3 documents (LibreOffice fails 3)

`03_stamp_vertical_90deg`, `314_tender_rfp_boq`, `326_itr_computation`

### `62_table_columns` — 1 documents (LibreOffice fails 1)

`03_stamp_vertical_90deg`

### `66_table_cell_width` — 1 documents (LibreOffice fails 1)

`323_credit_card_statement`

### `40_link_targets` — 1 documents (LibreOffice fails 1)

`44_coloured_underlined_hyperlinks`

### `53_embedded_faces` — 1 documents (LibreOffice fails 1)

`601_fillable_admission_form`

### `52_outline` — 1 documents (LibreOffice fails 1)

`602_bookmarked_annual_report`

### `26_text_overlap` — 4 documents (LibreOffice fails 9)

`07_stamp_over_table`, `322_mutual_fund_factsheet`, `77_arabic_rtl_document`, `78_mixed_english_devanagari_line`

