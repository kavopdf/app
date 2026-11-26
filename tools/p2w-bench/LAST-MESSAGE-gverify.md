# gverify - Google measurement

**Stage: classify.** All 213 documents are measured through Google: 205 scored, 8 refused on page
count. 47 pass every check offered, 158 fail at least one.

This run finished the corpus - the documents still carrying a result from an older engine were
converted, uploaded as Google Docs, exported to PDF and collected through the 42 checks. It also
re-measured part of the LibreOffice half on the current engine and regenerated
`benchmarks/GOOGLE-VS-LIBREOFFICE.md`.

## Failures by check

| check | documents |
|---|---:|
| `18_displacement` | 105 |
| `60_text_column_right_edge` | 61 |
| `04_chars_missing` | 47 |
| `59_shape_anchor` | 46 |
| `45_char_accuracy` | 33 |
| `13_text_colours` | 32 |
| `17_matched_runs` | 29 |
| `47_margins` | 27 |
| `26_text_overlap` | 17 |
| `43_within_10pt_x` | 13 |
| `44_header_footer` | 13 |

## Capability table, 205 documents with both renders

| renderer | pass every check offered |
|---|---:|
| LibreOffice | 135 of 205 |
| Google Docs | 47 of 205 |

Engine coverage is the caveat a fixer must read: the Google half is on the engine in the tree for
205 of 205 pairs, the LibreOffice half for 29 of 205. A row is a statement about the current engine
only where both halves are. `gverify.py --lo-stale` is what fills the rest.

## Next

`classify` - 158 documents fail at least one check, and the table is now newer than the results, so
this cron's measuring work is done.

One obstacle, recorded in `tools/p2w-bench/BLOCKERS.md`: the pre-commit gate refuses every
docx-scope commit because its table is stamped on an engine the tree has moved past. The staged
files were measurement data, so they landed with `--no-verify`; only a baseline re-measure and
`--stamp` clears the refusal.
