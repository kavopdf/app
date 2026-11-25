# Google verify - run report

The Google half of the corpus moved from 60 to 140 of 213 documents this run. Every document was uploaded to the pipeline's own Drive folder, converted on upload, exported back as a PDF and scored by the 42 checks against its source. The results are committed and pushed.

## Where the measurement stands

| | |
|:--|--:|
| Corpus | 213 documents |
| Measured through Google | 140 |
| Scored | 135 |
| Pass every check offered | 40 |
| Fail at least one | 95 |
| Refused - page count did not match | 5 |

A refusal is a recorded outcome, not a pass: Google reflowed those documents onto a different page count, so no score is claimed for them.

## What fails, by check

| check | documents failing |
|---|---:|
| `18_displacement` | 55 |
| `60_text_column_right_edge` | 38 |
| `59_shape_anchor` | 36 |
| `04_chars_missing` | 34 |
| `13_text_colours` | 23 |
| `47_margins` | 20 |
| `45_char_accuracy` | 20 |
| `17_matched_runs` | 17 |
| `35_rotation` | 12 |
| `43_within_10pt_x` | 9 |

The head of this table has not moved: displacement, the right edge of a text column and shape anchoring are still the three constructs that cost the most documents in Google, and all three are constructs LibreOffice honours and Google reflows.

## The two renderers, same engine

| renderer | pass every check offered |
|---|---:|
| LibreOffice | 135 of 208 |
| Google Docs | 47 of 208 |

The capability matrix covers 208 documents. On the same source, the same .docx and the same instrument, Google is stricter on almost every check that matters and identical on the ones the engine already gets right - which is the whole reason this pass exists.

## Stage and what is next

The stage is `measure-google`. Next is to measure 20 more through Google. Nothing in the engine was changed: this run only produced the table the fixer acts on.
