# gverify — Google measurement, 26 Nov

Stage is **measure-google**. Corpus 213 documents; 67 measured through Google — 62 scored, 5 refused on page count. Next: measure 20 more through Google.

## What this run did

Measured 60 documents through Google Docs (upload, convert to a Google Doc, export to PDF, then `--collect`, which also runs the LibreOffice side). Every result carries the engine stamp of the tree, so none of them is stale.

Committed and pushed: `benchmarks/gverify/` and `benchmarks/gverify-lo/`.

One document moved the wrong way against the committed results — 311\_fir\_police\_form, 4 to 5 failing checks, `59_shape_anchor` new — on engine a4d8fca469bba636. It was committed under the repo's named exception because the corpus is a net improvement in Google on the same engine. That is a finding for the fixer, not a fix.

## Where the corpus stands

67 verified | 14 pass every check offered | 48 fail at least one | 5 refused (page count).

| check | documents failing |
|---|---:|
| `18_displacement` | 26 |
| `04_chars_missing` | 22 |
| `60_text_column_right_edge` | 20 |
| `13_text_colours` | 18 |
| `59_shape_anchor` | 16 |
| `45_char_accuracy` | 14 |
| `35_rotation` | 11 |
| `17_matched_runs` | 11 |
| `47_margins` | 9 |
| `43_within_10pt_x` | 6 |

## Both renderers, same instrument

| | passes every check offered |
|---|---:|
| LibreOffice | 135 of 208 |
| Google Docs | 42 of 208 |

Engine in the tree: a4d8fca469bba636. Pairs on that engine: Google 62 of 208, LibreOffice 80 of 208 — the LibreOffice backlog was cleared with `--lo-stale` this run. A pair measured on two engines is not a pair, so read the capability table as a construct Google drops only for the 62 pairs where both halves are current.

The gap is not a layout opinion: `18_displacement` fails 21 in LibreOffice and 117 in Google, `60_text_column_right_edge` 19 against 62, `59_shape_anchor` 12 against 48. Google drops what LibreOffice honours.

## Next

Not `classify` yet — the Google side is incomplete, so the capability table is not this cron's last deliverable. The next gverify run measures more documents; the batch is limited by how much of the corpus has been converted to .docx on the pod, and that conversion is what the next run should finish first.
