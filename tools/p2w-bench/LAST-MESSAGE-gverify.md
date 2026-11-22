# gverify - capability table, stage `classify`

**Stage:** `classify`. The Google measurement is complete on disk, so this run's job was the table, not a
measurement: no document was measured and no engine code was touched.

## What this run did

Regenerated `benchmarks/GOOGLE-VS-LIBREOFFICE.md` from the committed results and committed it. The only
movement is the three `18_displacement` readings recorded since the last table: Google's pass count rose
and the documents failing `18_displacement` fell.

## The corpus

| | |
|:--|--:|
| Documents in corpus | 213 |
| Scored through Google | 192 |
| Refused (page count) | 21 |
| Failing at least one check | 166 |

## Pass rates, same engine, same source

| | |
|:--|--:|
| LibreOffice | 122 of 192 pass all 42 |
| Google Docs | 26 of 192 pass all 42 |

## Top failing checks - fix the class, not the document

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| `18_displacement` | 20 | 121 |
| `32_stroke_lines` | 1 | 113 |
| `05_chars_extra` | 3 | 109 |
| `04_chars_missing` | 2 | 66 |
| `59_shape_anchor` | 9 | 58 |

Seven constructs are honoured by LibreOffice and dropped by Google: `25_invisible_text`,
`44_header_footer`, `10_font_sizes`, `23_line_pitch`, `31_pages_lost_their_text`,
`46_text_crossing_rule` and `42_justification_edges`. One runs the other way: `14_filled_shapes`.

## Why `--report` prints a smaller number

`gverify.py --report` prints `21 verified | 0 pass all 42 | 0 fail at least one | 21 refused`. That is the
current-engine view: a result counts only when it carries the engine stamp of the engine on HEAD, and the
scored results were written before the last engine change, so the instrument sees the page-count refusals
and nothing else. The table above is computed from the committed results, which is the record the fixer
reads. Both numbers are real; they answer different questions.

## Next

`stage.py` says `classify`: 166 documents still fail at least one check and the class table is the
classifier cron's work, not this one's. This cron's measuring work is finished - the table is its last
deliverable, and it is committed.
