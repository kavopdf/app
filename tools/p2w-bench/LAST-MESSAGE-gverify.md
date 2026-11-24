# gverify: stage classify — the capability table is regenerated and pushed

`stage.py` says **classify**. Google has a result for every document in the corpus and the LibreOffice half is complete, so this run's whole job was the capability table. It is regenerated from the committed results and pushed as 1644f895. Nothing was measured this run, and no engine code was touched.

## What the tools print

| quantity | value | tool |
|---|---:|---|
| corpus documents | 212 | `stage.py` |
| measured through Google | 213 | `stage.py` |
| scored | 190 | `stage.py` |
| refused, page count | 23 | `stage.py` |
| failing documents | 155 | `stage.py` |
| verified | 209 | `gverify.py --report` |
| pass all 42 | 35 | `gverify.py --report` |
| fail at least one | 151 | `gverify.py --report` |
| refused, page count | 23 | `gverify.py --report` |
| documents with both renders | 190 | `gverify.py --matrix` |
| LibreOffice pass all 42 | 124 | `gverify.py --matrix` |
| Google pass all 42 | 35 | `gverify.py --matrix` |

## The checks that cost the most documents

| check | documents | tool |
|---|---:|---|
| `18_displacement` | 100 | `gverify.py --report` |
| `04_chars_missing` | 61 | `gverify.py --report` |
| `60_text_column_right_edge` | 54 | `gverify.py --report` |
| `59_shape_anchor` | 44 | `gverify.py --report` |
| `25_invisible_text` | 43 | `gverify.py --report` |

## What the table says

On the 190 documents measured through both renderers, LibreOffice passes 124 of them on all 42 checks and Google passes 35. Where the two disagree, Google is stricter on `18_displacement`, `04_chars_missing`, `25_invisible_text`, `60_text_column_right_edge` and `59_shape_anchor`; LibreOffice is stricter on `14_filled_shapes` only. Every check Google fails that LibreOffice passes is a construct LibreOffice honours and Google does not.

The table is written by `gverify.py --matrix` into `benchmarks/GOOGLE-VS-LIBREOFFICE.md`, unchanged in its counts from the previous generation — only the row order of the ties moved.

## One caveat, stated rather than smoothed

`gverify.py --report` counts fewer verified results than `stage.py` counts measured, because a committed result is counted only when it carries the current engine stamp. A handful of documents in the corpus carry a result from an older engine and are not measurements of this one. They are counted by `stage.py` and excluded by `--report`; re-measuring them needs the platform upload tool, which this run did not have, so it is left for a run that does.

## Next

`stage.py` still reads classify, with this next line:

    classify 155 failing documents - the table is older than the results

That stage exits when the classifier cron writes its own class table, not when this table is regenerated. So the capability table is this run's last deliverable: the classifier cron groups the failures next, and the fixer acts on those classes one construct at a time. No classification, no fix and no engine change was done here.
