# google verify - run report

Measured 26 documents through Google on the current engine. Every document that has a .docx staged now carries a current-engine result: the plan prints 0 to go on the 50 documents it can stage. Engine code untouched; the Google Docs created for this run were left in the test folder, nothing deleted.

## Where the corpus stands

| measure | count |
|---|---:|
| results carrying the current engine stamp | 108 |
| pass every check offered | 27 |
| fail at least one check | 59 |
| refused - page count, not a score | 22 |

The store holds 213 results for a corpus of 213 documents. The counts above are the ones stamped with the engine as it stands, which is the only set that can be called a measurement.

## Top failing checks in Google

| check | documents |
|---|---:|
| `18\_displacement` | 34 |
| `04\_chars\_missing` | 24 |
| `60\_text\_column\_right\_edge` | 19 |
| `13\_text\_colours` | 17 |
| `59\_shape\_anchor` | 17 |

## Capability table - 191 documents with both renders

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| `18\_displacement` | 20 | 103 |
| `04\_chars\_missing` | 2 | 60 |
| `60\_text\_column\_right\_edge` | 18 | 56 |
| `59\_shape\_anchor` | 9 | 45 |
| `13\_text\_colours` | 1 | 31 |

Passing every check offered: LibreOffice 125 of 191, Google 38 of 191. The table in `benchmarks/GOOGLE-VS-LIBREOFFICE.md` was regenerated from `gverify.py --matrix` and committed together with the results and the LibreOffice side.

## Stage and what is next

Stage is `classify`. The stage count is a count of files - 213 documents, 153 failing at least one check - while the report above counts results stamped with the current engine. The class table is older than these results, so the next cron groups the failures; this cron's measuring work is done.
