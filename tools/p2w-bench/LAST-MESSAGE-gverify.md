# Google verification - 187 of 213 measured

**Stage `measure-google`.** Corpus 213. 187 carry a Google result: 181 scored, 6 refused on page count. Next: measure 20 more.

| | count |
|---|---:|
| measured through Google | 187 |
| scored | 181 |
| refused (page count) | 6 |
| pass every check offered | 41 |
| fail at least one | 140 |

A refused document is not a pass: Google reflowed it and the score is not a score.

## Checks that cost the most documents

| check | documents failing |
|---|---:|
| `18_displacement` | 91 |
| `60_text_column_right_edge` | 51 |
| `04_chars_missing` | 47 |
| `59_shape_anchor` | 44 |
| `45_char_accuracy` | 30 |
| `13_text_colours` | 29 |
| `17_matched_runs` | 27 |
| `47_margins` | 25 |
| `26_text_overlap` | 16 |
| `44_header_footer` | 16 |

## Capability table - Google vs LibreOffice

207 documents have both halves. LibreOffice passes every check on 135 of 207; Google on 42 of 207. Engine in the tree a4d8fca469bba636 - Google is on it for 181 of 207 pairs, LibreOffice for 80, so read a row as a dropped construct only for those 80 pairs.

| check | LibreOffice fails | Google fails | stricter |
|---|---:|---:|---|
| `18_displacement` | 20 | 114 | Google |
| `60_text_column_right_edge` | 18 | 62 | Google |
| `04_chars_missing` | 2 | 54 | Google |
| `59_shape_anchor` | 11 | 49 | Google |
| `45_char_accuracy` | 2 | 33 | Google |
| `13_text_colours` | 1 | 32 | Google |
| `17_matched_runs` | 5 | 31 | Google |
| `47_margins` | 15 | 27 | Google |
| `26_text_overlap` | 3 | 19 | Google |
| `44_header_footer` | 0 | 18 | Google |

## What this run did

Corpus rebuilt in slices to 213 documents on the current engine, then each document uploaded, converted to a Google Doc, exported to PDF and scored with the 42 checks. The temporary Google Docs were deleted from the Drive folder after export; nothing of the user's was touched. The upload is the pace-setter, not Drive: it is one call per document and cannot be batched, so the run takes 60 documents rather than 20.
