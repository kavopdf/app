# Google Docs vs LibreOffice - the 42 checks, 191 documents, same engine

Same source PDF, same .docx, same instrument. Only the renderer differs.

    LibreOffice : 125 of 191 pass every check offered
    Google Docs : 37 of 191 pass every check offered

## Where they disagree

| check | LibreOffice fails | Google fails | who is stricter |
|---|---:|---:|---|
| `18_displacement` | 20 | 103 | **Google** |
| `04_chars_missing` | 2 | 61 | **Google** |
| `25_invisible_text` | 0 | 40 | **Google** |
| `60_text_column_right_edge` | 18 | 56 | **Google** |
| `59_shape_anchor` | 9 | 45 | **Google** |
| `45_char_accuracy` | 2 | 35 | **Google** |
| `13_text_colours` | 1 | 31 | **Google** |
| `44_header_footer` | 0 | 27 | **Google** |
| `17_matched_runs` | 4 | 30 | **Google** |
| `27_text_off_page` | 2 | 17 | **Google** |
| `26_text_overlap` | 2 | 16 | **Google** |
| `47_margins` | 15 | 25 | **Google** |
| `10_font_sizes` | 0 | 6 | **Google** |
| `32_stroke_lines` | 1 | 6 | **Google** |
| `43_within_10pt_x` | 7 | 12 | **Google** |
| `23_line_pitch` | 0 | 3 | **Google** |
| `31_pages_lost_their_text` | 0 | 1 | **Google** |
| `46_text_crossing_rule` | 0 | 1 | **Google** |
| `38_list_markers` | 1 | 2 | **Google** |
| `28_clipped_at_edge` | 1 | 1 | same |
| `51_field_values` | 1 | 1 | same |
| `66_table_cell_width` | 4 | 4 | same |
| `63_table_rows` | 3 | 3 | same |
| `40_link_targets` | 1 | 1 | same |
| `05_chars_extra` | 3 | 3 | same |
| `34a_span_size_match` | 2 | 2 | same |
| `64_table_span_across` | 1 | 1 | same |
| `52_outline` | 1 | 1 | same |
| `53_embedded_faces` | 4 | 4 | same |
| `37_super_subscript` | 1 | 1 | same |
| `65_table_span_down` | 1 | 1 | same |
| `62_table_columns` | 3 | 3 | same |
| `35_rotation` | 12 | 12 | same |
| `14_filled_shapes` | 2 | 0 | LibreOffice |

## Constructs LibreOffice honours and Google does not

* `25_invisible_text` - 40 documents
* `44_header_footer` - 27 documents
* `10_font_sizes` - 6 documents
* `23_line_pitch` - 3 documents
* `31_pages_lost_their_text` - 1 documents
* `46_text_crossing_rule` - 1 documents

## Constructs Google honours and LibreOffice does not

* `14_filled_shapes` - 2 documents

