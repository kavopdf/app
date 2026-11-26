# Google Docs vs LibreOffice - the 42 checks, 207 documents

Same source PDF, same instrument. Only the renderer differs.

    LibreOffice : 135 of 207 pass every check offered
    Google Docs : 42 of 207 pass every check offered

## Which engine each half was measured on

    engine in the tree : a4d8fca469bba636
    Google on it       : 207 of 207 pairs
    LibreOffice on it  : 80 of 207 pairs

A pair whose two halves were measured on two engines is not a pair: the LibreOffice
column describes the .docx an older engine wrote. Read a row as a construct Google
drops only for the 80 pairs where both halves are on the engine above.

## Where they disagree

| check | LibreOffice fails | Google fails | who is stricter |
|---|---:|---:|---|
| `18_displacement` | 20 | 113 | **Google** |
| `04_chars_missing` | 2 | 54 | **Google** |
| `60_text_column_right_edge` | 18 | 62 | **Google** |
| `59_shape_anchor` | 11 | 49 | **Google** |
| `45_char_accuracy` | 2 | 33 | **Google** |
| `13_text_colours` | 1 | 32 | **Google** |
| `17_matched_runs` | 5 | 30 | **Google** |
| `44_header_footer` | 0 | 18 | **Google** |
| `26_text_overlap` | 3 | 19 | **Google** |
| `27_text_off_page` | 2 | 17 | **Google** |
| `47_margins` | 15 | 27 | **Google** |
| `43_within_10pt_x` | 7 | 13 | **Google** |
| `10_font_sizes` | 0 | 6 | **Google** |
| `32_stroke_lines` | 1 | 6 | **Google** |
| `25_invisible_text` | 1 | 5 | **Google** |
| `23_line_pitch` | 0 | 3 | **Google** |
| `46_text_crossing_rule` | 0 | 2 | **Google** |
| `38_list_markers` | 1 | 2 | **Google** |
| `31_pages_lost_their_text` | 0 | 1 | **Google** |
| `34b_span_colour_match` | 0 | 1 | **Google** |
| `34c_span_weight_match` | 0 | 1 | **Google** |
| `42_justification_edges` | 0 | 1 | **Google** |
| `35_rotation` | 12 | 12 | same |
| `66_table_cell_width` | 6 | 6 | same |
| `63_table_rows` | 5 | 5 | same |
| `53_embedded_faces` | 4 | 4 | same |
| `05_chars_extra` | 3 | 3 | same |
| `62_table_columns` | 3 | 3 | same |
| `34a_span_size_match` | 2 | 2 | same |
| `28_clipped_at_edge` | 1 | 1 | same |
| `37_super_subscript` | 1 | 1 | same |
| `40_link_targets` | 1 | 1 | same |
| `51_field_values` | 1 | 1 | same |
| `52_outline` | 1 | 1 | same |
| `64_table_span_across` | 1 | 1 | same |
| `65_table_span_down` | 1 | 1 | same |
| `14_filled_shapes` | 3 | 0 | LibreOffice |

## Constructs LibreOffice honours and Google does not

* `44_header_footer` - 18 documents
* `10_font_sizes` - 6 documents
* `23_line_pitch` - 3 documents
* `46_text_crossing_rule` - 2 documents
* `31_pages_lost_their_text` - 1 documents
* `34b_span_colour_match` - 1 documents
* `34c_span_weight_match` - 1 documents
* `42_justification_edges` - 1 documents

## Constructs Google honours and LibreOffice does not

* `14_filled_shapes` - 3 documents

