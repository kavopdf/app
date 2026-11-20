# Google Docs vs LibreOffice - the 42 checks, 192 documents, same engine

Same source PDF, same .docx, same instrument. Only the renderer differs.

    LibreOffice : 108 of 192 pass all 42
    Google Docs : 7 of 192 pass all 42

## Where they disagree

| check | LibreOffice fails | Google fails | who is stricter |
|---|---:|---:|---|
| `32_stroke_lines` | 1 | 145 | **Google** |
| `05_chars_extra` | 7 | 141 | **Google** |
| `18_displacement` | 19 | 125 | **Google** |
| `04_chars_missing` | 7 | 67 | **Google** |
| `59_shape_anchor` | 10 | 58 | **Google** |
| `25_invisible_text` | 1 | 49 | **Google** |
| `45_char_accuracy` | 7 | 38 | **Google** |
| `13_text_colours` | 1 | 32 | **Google** |
| `60_text_column_right_edge` | 28 | 57 | **Google** |
| `44_header_footer` | 4 | 32 | **Google** |
| `17_matched_runs` | 9 | 30 | **Google** |
| `27_text_off_page` | 3 | 17 | **Google** |
| `47_margins` | 14 | 26 | **Google** |
| `26_text_overlap` | 10 | 17 | **Google** |
| `10_font_sizes` | 1 | 6 | **Google** |
| `43_within_10pt_x` | 7 | 11 | **Google** |
| `23_line_pitch` | 0 | 3 | **Google** |
| `34a_span_size_match` | 0 | 2 | **Google** |
| `38_list_markers` | 0 | 2 | **Google** |
| `31_pages_lost_their_text` | 0 | 1 | **Google** |
| `51_field_values` | 0 | 1 | **Google** |
| `46_text_crossing_rule` | 0 | 1 | **Google** |
| `42_justification_edges` | 0 | 1 | **Google** |
| `66_table_cell_width` | 4 | 4 | same |
| `63_table_rows` | 5 | 5 | same |
| `52_outline` | 1 | 1 | same |
| `35_rotation` | 12 | 12 | same |
| `64_table_span_across` | 1 | 1 | same |
| `65_table_span_down` | 1 | 1 | same |
| `62_table_columns` | 3 | 3 | same |
| `37_super_subscript` | 1 | 1 | same |
| `53_embedded_faces` | 4 | 4 | same |
| `40_link_targets` | 1 | 1 | same |
| `28_clipped_at_edge` | 2 | 1 | LibreOffice |
| `61_blank_not_filled` | 1 | 0 | LibreOffice |
| `14_filled_shapes` | 2 | 0 | LibreOffice |

## Constructs LibreOffice honours and Google does not

* `23_line_pitch` - 3 documents
* `34a_span_size_match` - 2 documents
* `38_list_markers` - 2 documents
* `31_pages_lost_their_text` - 1 documents
* `51_field_values` - 1 documents
* `46_text_crossing_rule` - 1 documents
* `42_justification_edges` - 1 documents

## Constructs Google honours and LibreOffice does not

* `14_filled_shapes` - 2 documents
* `61_blank_not_filled` - 1 documents

