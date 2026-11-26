**gverify — Google pass complete: 213 of 213 measured**

The measurement is finished. Every document in the corpus now has a Google result, and the stage has
moved off `measure-google` for the first time.

| | count |
|---|---:|
| documents in the corpus | 213 |
| verified through Google | 213 |
| scored | 208 |
| refused (page count) | 5 |
| pass every check offered | 42 |
| fail at least one | 166 |

Refused is not a pass: the 5 page-count refusals are counted separately, never as verified.

**The five checks that cost the most documents**

| check | Google fails | LibreOffice fails |
|---|---:|---:|
| `18\_displacement` | 119 | 21 |
| `60\_text\_column\_right\_edge` | 62 | 19 |
| `04\_chars\_missing` | 55 | 3 |
| `59\_shape\_anchor` | 49 | 11 |
| `45\_char\_accuracy` | 34 | 3 |

`18\_displacement` alone costs 119 documents, and LibreOffice costs 21 on the same 208 documents with
both renders. That gap is the pass working: the check is not broken, the renderer is.

**The capability table is written and committed**

`benchmarks/GOOGLE-VS-LIBREOFFICE.md` is regenerated from all results, not edited by hand. On the 208
documents that have both renders:

| renderer | pass every check offered |
|---|---:|
| LibreOffice | 135 |
| Google Docs | 42 |

The construct classes it names — Google drops what LibreOffice honours — come from the same run, with
`18\_displacement`, `04\_chars\_missing` and `60\_text\_column\_right\_edge` the widest of them.

**Stage and what is next**

`stage.py` now reports `classify`: the results exist and the class table is older than them. Grouping
the 166 failing documents into classes is the classifier cron's stage, not this one. Measuring is done,
so this cron stops here.

Note on the batch size: the run measured in batches of ten and was not cut off at any point, so the
60-document ceiling was never the constraint — the upload step was, exactly as the brief says.
