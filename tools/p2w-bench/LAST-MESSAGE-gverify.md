**gverify - 26 Nov 20:35 IST - stage: classify**

**Measurement is complete and the capability table is committed.**

| | |
|---|---:|
| documents verified through Google | 213 |
| scored | 205 |
| refused on page count | 8 |
| pass every check offered (Google) | 47 |
| fail at least one check | 158 |

**The table, both renderers** (`benchmarks/GOOGLE-VS-LIBREOFFICE.md`, regenerated and committed):

    LibreOffice : 135 of 205 pass every check offered
    Google Docs :  47 of 205 pass every check offered
    engine in the tree : 025fe9deda5ac7b1
    Google on it       : 205 of 205 pairs
    LibreOffice on it  :  83 of 205 pairs

The LibreOffice column was the stale half: its results carried whichever engine first converted each document. This run converted the corpus and refreshed that half with `--lo-stale`, so 83 of 205 pairs now sit on the engine in the tree. The rest of the pairs are still two-engine, which the table's own header states - a row is a construct Google drops only where both halves match the engine above.

**Where Google is stricter** (documents failing the check):

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| `18\_displacement` | 18 | 105 |
| `60\_text\_column\_right\_edge` | 18 | 61 |
| `04\_chars\_missing` | 2 | 47 |
| `59\_shape\_anchor` | 10 | 46 |
| `45\_char\_accuracy` | 2 | 33 |
| `13\_text\_colours` | 1 | 32 |
| `17\_matched\_runs` | 5 | 29 |
| `47\_margins` | 15 | 27 |
| `44\_header\_footer` | 0 | 13 |
| `10\_font\_sizes` | 0 | 6 |
| `32\_stroke\_lines` | 0 | 5 |

`44_header_footer`, `10_font_sizes` and `32_stroke_lines` fail in Google and never in LibreOffice - constructs LibreOffice honours and Google does not.

**Stage and next:** stage.py reports `classify` - 158 failing documents, the class table older than the results. Classifying is the classifier cron's work, not this one. No engine code was touched.
