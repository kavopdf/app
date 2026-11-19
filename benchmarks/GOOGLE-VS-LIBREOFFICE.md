# Google Docs vs LibreOffice - the 42 checks, 84 documents, same engine

Same source PDF, same .docx, same instrument. Only the renderer differs.

    LibreOffice : 41 of 84 pass all 42
    Google Docs : 7 of 84 pass all 42

## Where they disagree

| check | LibreOffice fails | Google fails | who is stricter |
|---|---:|---:|---|
| `32_stroke_lines` | 0 | 53 | **Google** |
| `05_chars_extra` | 6 | 54 | **Google** |
| `18_displacement` | 4 | 46 | **Google** |
| `04_chars_missing` | 6 | 30 | **Google** |
| `59_shape_anchor` | 4 | 26 | **Google** |
| `13_text_colours` | 0 | 18 | **Google** |
| `25_invisible_text` | 1 | 17 | **Google** |
| `47_margins` | 3 | 13 | **Google** |
| `17_matched_runs` | 7 | 16 | **Google** |
| `45_char_accuracy` | 6 | 15 | **Google** |
| `27_text_off_page` | 3 | 7 | **Google** |
| `60_text_column_right_edge` | 15 | 18 | **Google** |
| `43_within_10pt_x` | 3 | 6 | **Google** |
| `44_header_footer` | 4 | 7 | **Google** |
| `34a_span_size_match` | 0 | 2 | **Google** |
| `10_font_sizes` | 1 | 2 | **Google** |
| `38_list_markers` | 0 | 1 | **Google** |
| `51_field_values` | 0 | 1 | **Google** |
| `46_text_crossing_rule` | 0 | 1 | **Google** |
| `31_pages_lost_their_text` | 0 | 1 | **Google** |
| `42_justification_edges` | 0 | 1 | **Google** |
| `40_link_targets` | 1 | 1 | same |
| `53_embedded_faces` | 1 | 1 | same |
| `35_rotation` | 12 | 12 | same |
| `66_table_cell_width` | 1 | 1 | same |
| `52_outline` | 1 | 1 | same |
| `62_table_columns` | 1 | 1 | same |
| `63_table_rows` | 3 | 3 | same |
| `61_blank_not_filled` | 1 | 0 | LibreOffice |
| `28_clipped_at_edge` | 1 | 0 | LibreOffice |
| `26_text_overlap` | 9 | 4 | LibreOffice |

## Constructs LibreOffice honours and Google does not

* `32_stroke_lines` - 53 documents
* `13_text_colours` - 18 documents
* `34a_span_size_match` - 2 documents
* `38_list_markers` - 1 documents
* `51_field_values` - 1 documents
* `46_text_crossing_rule` - 1 documents
* `31_pages_lost_their_text` - 1 documents
* `42_justification_edges` - 1 documents

## Constructs Google honours and LibreOffice does not

* `61_blank_not_filled` - 1 documents
* `28_clipped_at_edge` - 1 documents


## What each renderer honours — measured, not assumed

| construct | LibreOffice | Google Docs | evidence |
|---|---|---|---|
| `w:w` character scaling | **honoured** | ignored | `FINDINGS/GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md` |
| `w:spacing` character spacing | honoured | ignored | same |
| embedded `.odttf` face | ignored | ignored | `FINDINGS/...-FONT-143300-b7e2.md` |
| `w:fitText` | ignored | ignored | same |
| `w:pBdr` paragraph border | **honoured** | **honoured** — but placed by flow, not absolutely | `FINDINGS/RULES-PBDR-FIX-MEASURED.md` |
| floating `<w:drawing>` | honoured | **ignored** — shape dropped, anchor kept as U+200B | `FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md` |
| DejaVu Serif | installed | **absent** — substitutes Arial, 17 % narrower | same file |
| Liberation Serif / Sans | installed | absent, but mapped to Times New Roman / Arial, metric-identical | `DocxWriter.BASE14` |

**Read this table before proposing a construct change.** Every row was measured, and the four fixes in
`FINDINGS/GOOGLE-LAYOUT-THREE-FIXES-TRIED.md` were all tried because this table did not exist yet.

## The shape of the problem, in one line

LibreOffice honours nearly every construct this engine emits - 41 of 84 documents pass all 42 checks.
Google honours almost none of the ones that carry absolute placement - 7 of 84. **The limitation is
Google's, and it is a limitation of absolute placement in a flowing-text format, which is why the model
is flowing text.**

## The three classes that carry the gap

    32_stroke_lines   LO 0    Google 53    a rule is a floating drawing; Google drops it
    05_chars_extra    LO 6    Google 54    the anchor that drawing leaves behind, as U+200B
    18_displacement   LO 4    Google 46    absolute placement, which Google does not honour

The first two are the same construct - see `FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`. **Those
two rows are 53 documents and they are one fix, not two.**
