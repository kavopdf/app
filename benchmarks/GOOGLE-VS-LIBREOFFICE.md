# Google Docs vs LibreOffice - the 42 checks, 190 documents, same engine

Same source PDF, same .docx, same instrument. Only the renderer differs.

    LibreOffice : 122 of 190 pass all 42
    Google Docs : 30 of 190 pass all 42

## Where they disagree

| check | LibreOffice fails | Google fails | who is stricter |
|---|---:|---:|---|
| `18_displacement` | 20 | 101 | **Google** |
| `04_chars_missing` | 2 | 65 | **Google** |
| `32_stroke_lines` | 1 | 50 | **Google** |
| `25_invisible_text` | 0 | 48 | **Google** |
| `05_chars_extra` | 3 | 45 | **Google** |
| `60_text_column_right_edge` | 18 | 56 | **Google** |
| `59_shape_anchor` | 9 | 45 | **Google** |
| `45_char_accuracy` | 2 | 37 | **Google** |
| `13_text_colours` | 1 | 32 | **Google** |
| `44_header_footer` | 0 | 31 | **Google** |
| `17_matched_runs` | 4 | 30 | **Google** |
| `27_text_off_page` | 2 | 17 | **Google** |
| `26_text_overlap` | 2 | 16 | **Google** |
| `47_margins` | 17 | 25 | **Google** |
| `10_font_sizes` | 0 | 6 | **Google** |
| `43_within_10pt_x` | 7 | 12 | **Google** |
| `23_line_pitch` | 0 | 3 | **Google** |
| `31_pages_lost_their_text` | 0 | 1 | **Google** |
| `38_list_markers` | 1 | 2 | **Google** |
| `46_text_crossing_rule` | 0 | 1 | **Google** |
| `37_super_subscript` | 1 | 1 | same |
| `62_table_columns` | 3 | 3 | same |
| `52_outline` | 1 | 1 | same |
| `35_rotation` | 12 | 12 | same |
| `66_table_cell_width` | 4 | 4 | same |
| `63_table_rows` | 3 | 3 | same |
| `40_link_targets` | 1 | 1 | same |
| `65_table_span_down` | 1 | 1 | same |
| `53_embedded_faces` | 4 | 4 | same |
| `28_clipped_at_edge` | 1 | 1 | same |
| `34a_span_size_match` | 2 | 2 | same |
| `51_field_values` | 1 | 1 | same |
| `64_table_span_across` | 1 | 1 | same |
| `14_filled_shapes` | 2 | 0 | LibreOffice |

## Constructs LibreOffice honours and Google does not

* `25_invisible_text` - 48 documents
* `44_header_footer` - 31 documents
* `10_font_sizes` - 6 documents
* `23_line_pitch` - 3 documents
* `31_pages_lost_their_text` - 1 documents
* `46_text_crossing_rule` - 1 documents

## Constructs Google honours and LibreOffice does not

* `14_filled_shapes` - 2 documents

## Engine coverage of this table

The rows above are computed from every document that has both renders. The header's "same engine"
is the instrument's own wording and it does not hold for the whole corpus. Read against the engine on
HEAD (`5beb8b9d`):

| | documents |
|:--|--:|
| both renders on the engine on HEAD | 0 |
| both renders on the same older engine | 142 |
| the two renders on two different engines | 6 |
| at least one side carries no engine stamp | 42 |

A pair whose two renders come from two different engines does not name a construct: it names the two
engines. Those documents need both halves measured again on one engine before their row is actionable.
`gverify.py --report` counts only the results carrying the engine on HEAD, which is why it prints a
smaller corpus than this table. **This table is a measurement of the engines its results carry, not of
HEAD** - it is the record of what the two renderers do to these documents, and it is regenerated from
the committed results every time the gverify cron reaches this stage.

## What carries each disagreement

The two rows that cost the most documents are one construct, not two. A rule is emitted as a floating
`<w:drawing>`; Google drops the shape and keeps its anchor, so `32_stroke_lines` loses the rule and
`05_chars_extra` gains a zero-width space from the same anchor. Measured on `18_centred_heading_left_body_txtpos`:
the .docx carries `<w:drawing>` twice, `<w:pBdr>` zero times, and the Google render shows the two rules
gone and one U+200B present. See `FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`.

What is settled about the two renderers, and not to be re-derived here:

* Google honours `w:pBdr`, but places it by flow, not at an absolute y.
* Google ignores `w:w`, `w:spacing`, embedded `.odttf`, `w:fitText` and floating drawings.
* No Google serif matches DejaVu Serif, which is what LibreOffice substitutes.

Construct-level fixes for these rows have already been tried and measured worse or neutral - `w:pBdr` for
rules, `w:pgMar` with indents, both together with spacing and offsets, and font metrics. All four are in
`FINDINGS/GOOGLE-LAYOUT-THREE-FIXES-TRIED.md`. The table is what makes the next attempt an informed one
instead of a fifth guess.

## How to read the two counts

This table is computed from every committed result that has both renders. `gverify.py --report` prints a
narrower number - only results carrying the engine stamp of the engine on HEAD - so the two are not
disagreeing about the corpus, they answer different questions: this table says what the renderers do to
these documents, `--report` says what has been measured on the engine as it stands now.
