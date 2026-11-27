# Google Docs vs LibreOffice - the 42 checks, 212 documents

Same source PDF, same instrument. Only the renderer differs.

    LibreOffice : 110 of 212 pass every check offered
    Google Docs : 42 of 212 pass every check offered

## Which engine each half was measured on

    engine in the tree : d28ca7516c3f9165
    Google on it       : 212 of 212 pairs
    LibreOffice on it  : 212 of 212 pairs

## Where they disagree

| check | LibreOffice fails | Google fails | who is stricter |
|---|---:|---:|---|
| `18_displacement` | 55 | 120 | **Google** |
| `04_chars_missing` | 3 | 58 | **Google** |
| `60_text_column_right_edge` | 19 | 63 | **Google** |
| `59_shape_anchor` | 17 | 51 | **Google** |
| `45_char_accuracy` | 3 | 37 | **Google** |
| `13_text_colours` | 1 | 33 | **Google** |
| `17_matched_runs` | 7 | 34 | **Google** |
| `44_header_footer` | 1 | 19 | **Google** |
| `27_text_off_page` | 2 | 19 | **Google** |
| `26_text_overlap` | 3 | 19 | **Google** |
| `47_margins` | 16 | 28 | **Google** |
| `32_stroke_lines` | 1 | 12 | **Google** |
| `43_within_10pt_x` | 8 | 14 | **Google** |
| `10_font_sizes` | 1 | 7 | **Google** |
| `01_page_count` | 1 | 5 | **Google** |
| `25_invisible_text` | 1 | 5 | **Google** |
| `55_orientation_mix` | 1 | 5 | **Google** |
| `23_line_pitch` | 0 | 3 | **Google** |
| `38_list_markers` | 1 | 3 | **Google** |
| `46_text_crossing_rule` | 0 | 2 | **Google** |
| `05_chars_extra` | 4 | 5 | **Google** |
| `31_pages_lost_their_text` | 0 | 1 | **Google** |
| `34b_span_colour_match` | 0 | 1 | **Google** |
| `34c_span_weight_match` | 0 | 1 | **Google** |
| `39_image_position` | 0 | 1 | **Google** |
| `35_rotation` | 12 | 12 | same |
| `66_table_cell_width` | 7 | 7 | same |
| `63_table_rows` | 5 | 5 | same |
| `53_embedded_faces` | 4 | 4 | same |
| `62_table_columns` | 4 | 4 | same |
| `34a_span_size_match` | 3 | 3 | same |
| `37_super_subscript` | 2 | 2 | same |
| `65_table_span_down` | 2 | 2 | same |
| `28_clipped_at_edge` | 1 | 1 | same |
| `40_link_targets` | 1 | 1 | same |
| `42_justification_edges` | 1 | 1 | same |
| `51_field_values` | 1 | 1 | same |
| `52_outline` | 1 | 1 | same |
| `64_table_span_across` | 1 | 1 | same |
| `14_filled_shapes` | 4 | 1 | LibreOffice |

## Constructs LibreOffice honours and Google does not

* `23_line_pitch` - 3 documents
* `46_text_crossing_rule` - 2 documents
* `31_pages_lost_their_text` - 1 documents
* `34b_span_colour_match` - 1 documents
* `34c_span_weight_match` - 1 documents
* `39_image_position` - 1 documents


---

## What carries the disagreements

Both columns above are on one engine (`d28ca7516c3f9165`) for the first time since the engine moved:
the LibreOffice half was re-measured on it with `gverify.py --lo-stale`, so a row is a pair and not
two engines read as one. Named carriers, and where each was measured:

* **`18_displacement`** - vertical only (`med_dx` within 0.8 pt of zero on every one-check document).
  Three carriers: the baseline placed at `LINE_BASE` (0.8) of a hairline line box where Google puts
  it at about 0.31 em; a table row rendered taller than its declared `w:trHeight`, so the error
  compounds once per row; and whole blocks placed against a measured edge.
  `FINDINGS/18-displacement-TWO-CONSTRUCTS-27NOV.md`,
  `FINDINGS/18-displacement-DOMINANT-SUBCAUSE-27NOV-agent.md`.
* **`60_text_column_right_edge`** - the engine declares DejaVu and Google substitutes Arial/Verdana,
  so the line underruns the column; on the single-check documents two of five are the instrument
  re-grouping a line rather than an edge that moved. A right tab stop is honoured by the renderer
  (538.50 pt against a drawn 538.61) but the export splits the tabbed line, which also drops
  `17_matched_runs`. `FINDINGS/60-COLUMN-RIGHT-EDGE-CENSUS-27NOV-agent.md`,
  `FINDINGS/60-RIGHT-TAB-HONOURED-INSTRUMENT-BLIND-27NOV-fixer.md`.
* **`32_stroke_lines`** - a rule is emitted as a floating `<w:drawing>`; Google drops the shape and
  keeps the anchor. Already established; not re-derived here.
* **`05_chars_extra`** - the same anchor, counted as a character. Already established; not re-derived
  here.

The remaining checks in the table have no carrier named in this file. `benchmarks/DEFECT-CLASSES-GOOGLE.md`
is the class table the fixer works from; `FINDINGS/` holds what has been measured per check, including
refutations - read it before re-deriving one.
