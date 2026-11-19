# Google Docs vs LibreOffice — the 42 checks, same 50 documents, same engine

`verify_google.py`'s 42 named checks run twice per document: once against the .docx rendered by
`soffice --headless`, once against the PDF Google Docs itself exports. Same source PDF, same
.docx, same instrument. Only the renderer differs.

    49 documents compared
    LibreOffice: 23 pass all 42
    Google Docs: 7 pass all 42

## Where the two renderers disagree

| check | LibreOffice fails | Google fails | who is stricter |
|---|---:|---:|---|
| `32_stroke_lines` | 0 | 28 | **Google** |
| `05_chars_extra` | 5 | 30 | **Google** |
| `18_displacement` | 1 | 19 | **Google** |
| `47_margins` | 0 | 7 | **Google** |
| `59_shape_anchor` | 2 | 6 | **Google** |
| `04_chars_missing` | 6 | 10 | **Google** |
| `13_text_colours` | 0 | 3 | **Google** |
| `27_text_off_page` | 2 | 5 | **Google** |
| `34a_span_size_match` | 0 | 2 | **Google** |
| `43_within_10pt_x` | 0 | 2 | **Google** |
| `46_text_crossing_rule` | 0 | 1 | **Google** |
| `38_list_markers` | 0 | 1 | **Google** |
| `51_field_values` | 0 | 1 | **Google** |
| `52_outline` | 1 | 1 | same |
| `35_rotation` | 3 | 3 | same |
| `40_link_targets` | 1 | 1 | same |
| `25_invisible_text` | 2 | 2 | same |
| `53_embedded_faces` | 1 | 1 | same |
| `17_matched_runs` | 7 | 6 | LibreOffice |
| `10_font_sizes` | 1 | 0 | LibreOffice |
| `28_clipped_at_edge` | 1 | 0 | LibreOffice |
| `61_blank_not_filled` | 1 | 0 | LibreOffice |
| `44_header_footer` | 4 | 2 | LibreOffice |
| `45_char_accuracy` | 6 | 2 | LibreOffice |
| `60_text_column_right_edge` | 12 | 8 | LibreOffice |
| `26_text_overlap` | 8 | 2 | LibreOffice |

## The checks only Google fails

* `32_stroke_lines` — 28 documents
* `47_margins` — 7 documents
* `13_text_colours` — 3 documents
* `34a_span_size_match` — 2 documents
* `43_within_10pt_x` — 2 documents
* `46_text_crossing_rule` — 1 documents
* `38_list_markers` — 1 documents
* `51_field_values` — 1 documents

## The checks only LibreOffice fails

* `10_font_sizes` — 1 documents
* `28_clipped_at_edge` — 1 documents
* `61_blank_not_filled` — 1 documents

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
| Liberation Serif / Sans | installed | absent, but engine maps to Times New Roman / Arial, metric-identical | `DocxWriter.BASE14` |
