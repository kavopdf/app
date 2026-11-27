**gverify run — 27 Nov 2026**

Stage: `measure-google`. The corpus is 213 documents; 212 now have a Google result — 211 scored, 1 refused on page count. 1 document is left.

The corpus had to be rebuilt first: this pod started with 42 of the 213 `.docx` converted, so the run finished the remaining conversions before it could measure anything.

## Where the corpus stands

| | documents |
|---|---:|
| Google result, scored | 211 |
| Google result, refused (page count) | 1 |
| pass every check offered | 42 |
| fail at least one check | 169 |

## Top five failing checks

| check | Google fails |
|---|---:|
| 18\_displacement | 119 |
| 60\_text\_column\_right\_edge | 63 |
| 04\_chars\_missing | 58 |
| 59\_shape\_anchor | 51 |
| 45\_char\_accuracy | 37 |

## Capability table — both renderers

| renderer | pass every check offered |
|---|---:|
| LibreOffice | 134 of 212 |
| Google Docs | 42 of 212 |

Google on the tree engine: 211 of 212 pairs. LibreOffice on the tree engine: 13 of 212 pairs — the LibreOffice backlog is the open work, and `gverify.py --lo-stale` is the tool that clears it.

## One instrument defect found and fixed (tools, not engine)

The corpus stamp and the two readers hashed different sets of engine files. `corpus-convert.py` stamps the corpus with the `.docx` engine — every `.java` except `TxtWriter.java`, which no `.docx` byte depends on — and `gvbatch.py` writes the Google verdicts from that stamp. `gverify.py` and `verify_google.py` hashed every `.java`, so after the rebuild the store held 211 rows on one hash and the readers computed another, and `plan()` saw 2 of 213. The LibreOffice half carried the all-`.java` hash too, which is why the matrix read 0 pairs on the tree engine.

Both readers now compute the same quantity the store is stamped with. No check was changed, no engine code touched, no result re-stamped by hand.

## Next

Measure the last document, then clear the LibreOffice backlog so every row is a pair on one engine. `stage.py` still says `measure-google`; the capability table is not due yet.
