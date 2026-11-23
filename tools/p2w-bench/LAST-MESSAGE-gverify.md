# Google verify - run report

**Stage moved `classify` -> `fix`.** The Google measurement is complete and the class table was older than the results, so this run regenerated it and committed it. Nothing after that stage is mine.

## The measurement, as the tools print it

| quantity | count |
|---|---:|
| documents in the corpus | 212 |
| measured through Google | 213 |
| scored | 190 |
| refused, page count did not match | 23 |
| documents failing at least one check | 160 |
| results carrying the current engine stamp | 86 |
| pass all 42 on that stamp | 13 |
| fail at least one on that stamp | 50 |

## Checks that cost the most documents

`gverify.py --report`, over the results carrying the current engine stamp:

| check | documents |
|---|---:|
| `18\_displacement` | 28 |
| `04\_chars\_missing` | 24 |
| `60\_text\_column\_right\_edge` | 21 |
| `25\_invisible\_text` | 19 |
| `59\_shape\_anchor` | 19 |
| `13\_text\_colours` | 18 |
| `45\_char\_accuracy` | 14 |
| `35\_rotation` | 10 |

## The capability table

`gverify.py --matrix`, over all 190 documents that have both renders:

| renderer | pass all 42 |
|---|---|
| LibreOffice | 122 of 190 |
| Google Docs | 30 of 190 |

| check | LibreOffice fails | Google fails | stricter |
|---|---:|---:|---|
| `18\_displacement` | 20 | 101 | **Google** |
| `04\_chars\_missing` | 2 | 65 | **Google** |
| `60\_text\_column\_right\_edge` | 18 | 56 | **Google** |
| `25\_invisible\_text` | 0 | 48 | **Google** |
| `32\_stroke\_lines` | 1 | 47 | **Google** |
| `59\_shape\_anchor` | 9 | 45 | **Google** |
| `05\_chars\_extra` | 3 | 43 | **Google** |
| `45\_char\_accuracy` | 2 | 37 | **Google** |
| `13\_text\_colours` | 1 | 32 | **Google** |
| `44\_header\_footer` | 0 | 31 | **Google** |

Constructs LibreOffice honours and Google does not: `25\_invisible\_text` 48, `44\_header\_footer` 31, `10\_font\_sizes` 6, `23\_line\_pitch` 3, `31\_pages\_lost\_their\_text` 1, `46\_text\_crossing\_rule` 1.

## Read the two failure counts as different questions

The same check shows a smaller count in the first table than the second, and that is the instruments, not an error: `--report` counts only results carrying the current engine stamp, while `--matrix` and the class table count every paired document whatever engine produced it. Neither is a score of HEAD; the class table says so in its own header.

## What this run did

Regenerated `benchmarks/DEFECT-CLASSES-GOOGLE.md` with `classify_google.py` - a build product, not hand-written - committed it, and pushed. The table still shows every class OPEN, with `18\_displacement` the largest at 101 documents. Next stage is `fix`: one class at a time, smallest first.
