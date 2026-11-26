# Google Docs vs LibreOffice - the 42 checks, 208 documents

Same source PDF, same instrument. Only the renderer differs.

    LibreOffice : 135 of 208 pass every check offered
    Google Docs : 42 of 208 pass every check offered

## Which engine each half was measured on

    engine in the tree : 981ff1fa35e2cf67
    Google on it       : 208 of 208 pairs
    LibreOffice on it  : 208 of 208 pairs

## Where they disagree

| check | LibreOffice fails | Google fails | who is stricter |
|---|---:|---:|---|
| `18_displacement` | 21 | 119 | **Google** |
| `04_chars_missing` | 3 | 55 | **Google** |
| `60_text_column_right_edge` | 19 | 62 | **Google** |
| `59_shape_anchor` | 12 | 49 | **Google** |
| `45_char_accuracy` | 3 | 34 | **Google** |
| `13_text_colours` | 1 | 32 | **Google** |
| `17_matched_runs` | 6 | 32 | **Google** |
| `44_header_footer` | 1 | 19 | **Google** |
| `26_text_overlap` | 3 | 19 | **Google** |
| `27_text_off_page` | 2 | 18 | **Google** |
| `47_margins` | 16 | 28 | **Google** |
| `43_within_10pt_x` | 8 | 14 | **Google** |
| `10_font_sizes` | 1 | 7 | **Google** |
| `32_stroke_lines` | 2 | 7 | **Google** |
| `25_invisible_text` | 1 | 5 | **Google** |
| `23_line_pitch` | 0 | 4 | **Google** |
| `38_list_markers` | 1 | 3 | **Google** |
| `46_text_crossing_rule` | 0 | 2 | **Google** |
| `31_pages_lost_their_text` | 0 | 1 | **Google** |
| `34c_span_weight_match` | 0 | 1 | **Google** |
| `42_justification_edges` | 0 | 1 | **Google** |
| `35_rotation` | 12 | 12 | same |
| `66_table_cell_width` | 7 | 7 | same |
| `53_embedded_faces` | 5 | 5 | same |
| `63_table_rows` | 5 | 5 | same |
| `05_chars_extra` | 4 | 4 | same |
| `62_table_columns` | 4 | 4 | same |
| `34a_span_size_match` | 3 | 3 | same |
| `37_super_subscript` | 2 | 2 | same |
| `51_field_values` | 2 | 2 | same |
| `65_table_span_down` | 2 | 2 | same |
| `01_page_count` | 1 | 1 | same |
| `34b_span_colour_match` | 1 | 1 | same |
| `39_image_position` | 1 | 1 | same |
| `40_link_targets` | 1 | 1 | same |
| `52_outline` | 1 | 1 | same |
| `55_orientation_mix` | 1 | 1 | same |
| `64_table_span_across` | 1 | 1 | same |
| `28_clipped_at_edge` | 2 | 1 | LibreOffice |
| `61_blank_not_filled` | 1 | 0 | LibreOffice |
| `14_filled_shapes` | 4 | 1 | LibreOffice |

## Constructs LibreOffice honours and Google does not

* `23_line_pitch` - 4 documents
* `46_text_crossing_rule` - 2 documents
* `31_pages_lost_their_text` - 1 documents
* `34c_span_weight_match` - 1 documents
* `42_justification_edges` - 1 documents

## Constructs Google honours and LibreOffice does not

* `61_blank_not_filled` - 1 documents

