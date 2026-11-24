gverify run — 24 Nov 2026

Stage: classify. 213 measured through Google, 190 scored, 23 refused on page count. 35 pass all 42 checks, 151 fail at least one.

Capability table regenerated and committed (`benchmarks/GOOGLE-VS-LIBREOFFICE.md`, commit 1c95df1d). Same source, same engine, both renderers:

    LibreOffice : 124 of 190 pass all 42
    Google Docs : 35 of 190 pass all 42

The five checks that cost Google the most documents:

| check | Google fails | LibreOffice fails |
|---|---:|---:|
| `18_displacement` | 102 | 20 |
| `04_chars_missing` | 65 | 2 |
| `60_text_column_right_edge` | 56 | 18 |
| `59_shape_anchor` | 45 | 9 |
| `25_invisible_text` | 43 | 0 |

Every one of them is a construct LibreOffice honours and Google does not — absolute placement in a flowing-text format. The engine was not touched; no document was measured this run because the evidence puts the pipeline past `measure-google`.

Next: classify 155 failing documents — the table is older than the results. That is the classifier cron's slot, not this one.
