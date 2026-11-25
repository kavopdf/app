# Google verify - run report

This run measured 60 documents through Google on the current engine and committed every one of them. Before it, 22 of 213 stored results carried the current engine stamp and all 22 were page-count refusals - nothing in the corpus was scored against the engine as it stands. After it, 82 carry the stamp.

## Where the corpus stands

| measure | count |
|---|---:|
| results stamped with the current engine | 82 |
| pass every check offered | 24 |
| fail at least one check | 36 |
| refused - page count, not a score | 22 |

## Top failing checks

| check | documents |
|---|---:|
| `18\_displacement` | 18 |
| `47\_margins` | 12 |
| `60\_text\_column\_right\_edge` | 12 |
| `04\_chars\_missing` | 8 |
| `43\_within\_10pt\_x` | 6 |

## Capability table, both renderers on 191 documents

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| `18\_displacement` | 20 | 103 |
| `04\_chars\_missing` | 2 | 61 |
| `25\_invisible\_text` | 0 | 40 |
| `60\_text\_column\_right\_edge` | 18 | 56 |
| `59\_shape\_anchor` | 9 | 45 |

Passing every check offered: LibreOffice 125 of 191, Google 37 of 191. The table in `benchmarks/GOOGLE-VS-LIBREOFFICE.md` was regenerated from this output and committed.

## Stage and what is next

Stage is `classify`. The corpus holds 213 documents; 213 have a Google result on file - 191 scored, 22 refused - and 154 still fail a check. Next: classify those 154 failing documents, because the class table is older than the results.

The gap the numbers above expose: the stage count is a count of files, the report count is a count of results stamped with the current engine. That is why this run measured rather than wrote a table.

No engine code was touched.
