**gverify — stage `classify`. The capability table is regenerated, is now a true same-engine pair, and is committed. Nothing left to measure.**

`stage.py` reports `classify`: `213` documents, `213` measured through Google (`207` scored, `6` refused), `165` failing. The next action belongs to the classifier cron — group those `165` failing documents into classes.

What this run added. The table's header had been admitting that the LibreOffice column was measured on an older engine — the Google half moved with every engine commit and the LibreOffice half never could, so the "where they disagree" section described a construct only for the pairs that happened to match. This run rebuilt the corpus and re-measured the LibreOffice side, and the table now says **LibreOffice on it: 207 of 207 pairs**, against **Google on it: 207 of 207 pairs**, engine `a4d8fca469bba636`. Every row below is a real pair.

| | LibreOffice | Google Docs |
|---|---:|---:|
| pass every check offered | 135 of 207 | 42 of 207 |

Top failing checks, from `gverify.py --report` and `gverify.py --matrix`:

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| `18\_displacement` | 20 | 113 |
| `60\_text\_column\_right\_edge` | 18 | 62 |
| `04\_chars\_missing` | 2 | 54 |
| `59\_shape\_anchor` | 11 | 49 |
| `45\_char\_accuracy` | 2 | 33 |
| `13\_text\_colours` | 1 | 32 |
| `17\_matched\_runs` | 5 | 30 |
| `47\_margins` | 15 | 27 |

The six refused documents are still refused on page count — a refused document is not a pass, and they are not counted in the `207`.

Committed and pushed: `benchmarks/gverify-lo/` (both halves on the engine in the tree) and `benchmarks/GOOGLE-VS-LIBREOFFICE.md`. The commit gate passed on the way in — nothing got worse in either format, and the table matches this engine. No engine code was touched; no document was classified; no fix was attempted.
