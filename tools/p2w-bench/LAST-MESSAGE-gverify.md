**gverify: stage is `classify`, so nothing was measured this run — the capability table was regenerated from the committed results and landed.**

`stage.py` reads `classify`: 213 of 213 documents measured through Google (190 scored, 23 refused), 155 still failing, and the live table `DEFECT-CLASSES-GOOGLE.md` older than the results it summarises. Measurement and the LibreOffice half are both done, so this slot did the one action its stage allows — write the capability table from the tool's own output, commit, stop. No document was uploaded, no engine code was touched, nothing was classified.

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| `18_displacement` | 20 | 102 |
| `04_chars_missing` | 2 | 65 |
| `60_text_column_right_edge` | 18 | 56 |
| `59_shape_anchor` | 9 | 45 |
| `25_invisible_text` | 0 | 43 |
| `45_char_accuracy` | 2 | 37 |
| `13_text_colours` | 1 | 32 |
| `44_header_footer` | 0 | 30 |
| `17_matched_runs` | 4 | 30 |
| `47_margins` | 15 | 25 |

LibreOffice passes 124 of 190 documents, Google passes 35 of 190, and 35 pass every check offered in Google. The table's header used to say "pass all 42"; the tool now says "every check offered", which is the corrected claim, and the counts did not move.

**The commit gate was refusing everything, and this run found out why.** Since the gate began failing on an unbuildable corpus, no run on a fresh pod could commit: `corpus-convert.py` spawns one JVM per document, which does not finish inside a single call and writes no stamp, so every retry started from nothing. One `ConvertAll` over the whole corpus directory — which reuses a single JVM — converted all 213 documents with 0 failed, the stamp then read WARM, and `regress.py --check` printed PASS. Recorded in `BLOCKERS.md` with what would overturn it.

Next stage is `classify`: 155 failing documents need a row in `DEFECT-CLASSES-GOOGLE.md` from the classifier, which is not this cron.
