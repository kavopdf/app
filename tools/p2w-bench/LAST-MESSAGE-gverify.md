**gverify — stage `classify`: both renderers are complete on the engine in the tree, table regenerated, nothing left to commit.**

`gverify.py --matrix` regenerates byte-identical to the committed `benchmarks/GOOGLE-VS-LIBREOFFICE.md`, and `benchmarks/gverify-lo/` already holds its partner for every scored document. Measuring work for this cron is finished; no commit was needed because the tree is clean.

| measurement | count |
|---|---:|
| verified through Google | 213 |
| pass every check offered | 42 |
| fail at least one check | 165 |
| refused (page count) | 6 |

**Capability table** — 207 documents scored in both renderers, LibreOffice 135 of 207 pass, Google 42 of 207 pass. Engine in the tree a4d8fca469bba636: Google on it 207 of 207 pairs, LibreOffice on it 207 of 207 pairs, so no stale half is hiding behind the comparison.

| top failing check | Google fails |
|---|---:|
| `18\_displacement` | 113 |
| `60\_text\_column\_right\_edge` | 62 |
| `04\_chars\_missing` | 54 |
| `59\_shape\_anchor` | 49 |
| `45\_char\_accuracy` | 33 |

**Next** — `stage.py` reads `classify`, 165 failing documents, because `benchmarks/DEFECT-CLASSES-GOOGLE.md` predates the newest results. That file is written by `classify_google.py` and belongs to the classifier cron; per the brief this cron regenerates the capability table and stops there. No engine code touched.
