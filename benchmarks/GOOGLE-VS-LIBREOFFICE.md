# Google Docs vs LibreOffice - the 42 checks, 67 documents, same engine

Same source PDF, same .docx, same instrument. Only the renderer differs.

    LibreOffice : 30 of 67 pass all 42
    Google Docs : 7 of 67 pass all 42

## Where they disagree

| check | LibreOffice fails | Google fails | who is stricter |
|---|---:|---:|---|
| `32_stroke_lines` | 0 | 45 | **Google** |
| `05_chars_extra` | 6 | 45 | **Google** |
| `18_displacement` | 3 | 31 | **Google** |
| `04_chars_missing` | 6 | 22 | **Google** |
| `59_shape_anchor` | 3 | 17 | **Google** |
| `13_text_colours` | 0 | 13 | **Google** |
| `25_invisible_text` | 1 | 8 | **Google** |
| `47_margins` | 2 | 9 | **Google** |
| `17_matched_runs` | 7 | 11 | **Google** |
| `27_text_off_page` | 3 | 6 | **Google** |
| `43_within_10pt_x` | 2 | 4 | **Google** |
| `34a_span_size_match` | 0 | 2 | **Google** |
| `45_char_accuracy` | 6 | 8 | **Google** |
| `31_pages_lost_their_text` | 0 | 1 | **Google** |
| `38_list_markers` | 0 | 1 | **Google** |
| `51_field_values` | 0 | 1 | **Google** |
| `46_text_crossing_rule` | 0 | 1 | **Google** |
| `44_header_footer` | 4 | 5 | **Google** |
| `40_link_targets` | 1 | 1 | same |
| `52_outline` | 1 | 1 | same |
| `35_rotation` | 12 | 12 | same |
| `53_embedded_faces` | 1 | 1 | same |
| `63_table_rows` | 1 | 1 | same |
| `10_font_sizes` | 1 | 1 | same |
| `62_table_columns` | 1 | 1 | same |
| `28_clipped_at_edge` | 1 | 0 | LibreOffice |
| `61_blank_not_filled` | 1 | 0 | LibreOffice |
| `60_text_column_right_edge` | 12 | 9 | LibreOffice |
| `26_text_overlap` | 9 | 3 | LibreOffice |

## Constructs LibreOffice honours and Google does not

* `32_stroke_lines` - 45 documents
* `13_text_colours` - 13 documents
* `34a_span_size_match` - 2 documents
* `31_pages_lost_their_text` - 1 documents
* `38_list_markers` - 1 documents
* `51_field_values` - 1 documents
* `46_text_crossing_rule` - 1 documents

## Constructs Google honours and LibreOffice does not

* `28_clipped_at_edge` - 1 documents
* `61_blank_not_filled` - 1 documents


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

LibreOffice honours nearly every construct this engine emits. Google honours almost none of the ones
that carry absolute placement. **The limitation is Google's, and it is a limitation of absolute
placement in a flowing-text format — which is why the model is flowing text.**
