# Google verify - run report

**Stage: `classify` closed, the evidence now says `fix`.** The Google defect class table was last committed an hour before the results it summarises, so the pipeline had been sitting on `classify` all day. Regenerating it from the results on disk cleared that, and `stage.py` moved on to `fix`.

## The measurement

`gverify.py --report` on the committed results:

| | |
|---|---:|
| documents verified through Google | 213 |
| pass all 42 checks | 6 |
| fail at least one check | 186 |
| refused, page count | 21 |

## Both renderers, same engine

`gverify.py --matrix`, over the 192 documents that have a render in each:

| renderer | pass all 42 |
|---|---:|
| LibreOffice | 122 of 192 |
| Google Docs | 6 of 192 |

Where they disagree, the biggest gaps - a check LibreOffice passes and Google fails is a construct Google drops:

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| `32\_stroke\_lines` | 1 | 145 |
| `05\_chars\_extra` | 3 | 141 |
| `18\_displacement` | 20 | 124 |
| `04\_chars\_missing` | 2 | 66 |
| `59\_shape\_anchor` | 9 | 58 |
| `60\_text\_column\_right\_edge` | 18 | 58 |
| `25\_invisible\_text` | 0 | 49 |
| `45\_char\_accuracy` | 2 | 37 |
| `44\_header\_footer` | 0 | 32 |
| `13\_text\_colours` | 1 | 32 |

## What this run did

- Regenerated `benchmarks/DEFECT-CLASSES-GOOGLE.md` from `benchmarks/gverify/` and `benchmarks/gverify-lo/`; `classify_google.py --check` now reports it up to date.
- Committed and pushed that table. No engine code touched.

## Next

The fixer takes one class at a time, smallest first, and changes the engine only where a before/after measurement says it helps. The 186 documents still failing a check are its queue, and `32\_stroke\_lines` alone accounts for 145 of them.
