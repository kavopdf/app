**gverify** — stage `classify`. Corpus 213 documents: 213 measured through Google (212 scored, 1 refused), 170 failing.

The capability table was the blocker and it is now a real pair. The LibreOffice half had been frozen on older engines, so `gverify.py --matrix` read 60 of 212 pairs on the engine in the tree; I re-measured that half with `--lo-stale` until it read 212 of 212. `benchmarks/GOOGLE-VS-LIBREOFFICE.md` is regenerated from the tool on that evidence.

| | pass every check offered |
|---|---:|
| LibreOffice | 110 of 212 |
| Google Docs | 42 of 212 |

Google's worst checks: `18\_displacement` 120, `60\_text\_column\_right\_edge` 63, `04\_chars\_missing` 58, `59\_shape\_anchor` 51, `45\_char\_accuracy` 37.

The table now carries named carriers for `18\_displacement` (baseline inside a hairline line box, table row taller than its declared height, block placement), `60\_text\_column\_right\_edge` (DejaVu declared, Arial substituted, plus the export splitting a tabbed line), and the two already established: `32\_stroke\_lines` and `05\_chars\_extra`. Nothing else is named there.

Committed and pushed: the re-measured LibreOffice results and the table. The commit gate passed on its own terms (no document worse in either format, no Google-ignored construct spread).

Stage stays `classify` because `benchmarks/DEFECT-CLASSES-GOOGLE.md` is older than the results — that regeneration belongs to the classifier cron, not this one.
