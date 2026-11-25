# Google Docs vs LibreOffice - the 42 checks, 213 documents, same engine

Same source PDF, same .docx, same instrument. Only the renderer differs.

    LibreOffice : 138 of 213 pass every check offered
    Google Docs : 42 of 213 pass every check offered

## Where they disagree

| check | LibreOffice fails | Google fails | who is stricter |
|---|---:|---:|---|
| `18_displacement` | 22 | 122 | **Google** |
| `04_chars_missing` | 4 | 59 | **Google** |
| `60_text_column_right_edge` | 20 | 64 | **Google** |
| `59_shape_anchor` | 12 | 52 | **Google** |
| `45_char_accuracy` | 4 | 38 | **Google** |
| `13_text_colours` | 1 | 33 | **Google** |
| `17_matched_runs` | 8 | 36 | **Google** |
| `44_header_footer` | 2 | 20 | **Google** |
| `27_text_off_page` | 2 | 20 | **Google** |
| `26_text_overlap` | 2 | 19 | **Google** |
| `47_margins` | 17 | 29 | **Google** |
| `32_stroke_lines` | 2 | 12 | **Google** |
| `43_within_10pt_x` | 9 | 15 | **Google** |
| `10_font_sizes` | 2 | 8 | **Google** |
| `25_invisible_text` | 0 | 5 | **Google** |
| `23_line_pitch` | 0 | 4 | **Google** |
| `01_page_count` | 2 | 6 | **Google** |
| `55_orientation_mix` | 2 | 6 | **Google** |
| `38_list_markers` | 1 | 4 | **Google** |
| `46_text_crossing_rule` | 0 | 2 | **Google** |
| `34c_span_weight_match` | 0 | 1 | **Google** |
| `31_pages_lost_their_text` | 0 | 1 | **Google** |
| `39_image_position` | 1 | 2 | **Google** |
| `34b_span_colour_match` | 1 | 1 | same |
| `64_table_span_across` | 1 | 1 | same |
| `63_table_rows` | 5 | 5 | same |
| `65_table_span_down` | 3 | 3 | same |
| `40_link_targets` | 1 | 1 | same |
| `42_justification_edges` | 1 | 1 | same |
| `52_outline` | 1 | 1 | same |
| `37_super_subscript` | 3 | 3 | same |
| `66_table_cell_width` | 8 | 8 | same |
| `53_embedded_faces` | 5 | 5 | same |
| `05_chars_extra` | 5 | 5 | same |
| `51_field_values` | 2 | 2 | same |
| `35_rotation` | 12 | 12 | same |
| `62_table_columns` | 5 | 5 | same |
| `34a_span_size_match` | 4 | 4 | same |
| `61_blank_not_filled` | 1 | 0 | LibreOffice |
| `28_clipped_at_edge` | 2 | 1 | LibreOffice |
| `14_filled_shapes` | 5 | 2 | LibreOffice |

## Constructs LibreOffice honours and Google does not

* `25_invisible_text` - 5 documents
* `23_line_pitch` - 4 documents
* `46_text_crossing_rule` - 2 documents
* `34c_span_weight_match` - 1 documents
* `31_pages_lost_their_text` - 1 documents

## Constructs Google honours and LibreOffice does not

* `61_blank_not_filled` - 1 documents

