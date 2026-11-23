# P2W Google Verify - Run Report

**23 Nov 2026 · 05:30 IST · stage `classify`**

> 190 of 213 documents scored in Google, 23 refused on page count. Google passes all 42 on 28, LibreOffice on 122.

Stage `classify` is the table, not a measurement, so this run measured nothing and touched no engine code. It regenerated the capability table from the committed results and committed it.

## The corpus

| | |
|:--|--:|
| documents in corpus | **213** |
| scored through Google | **190** |
| refused on page count | **23** |
| clean in Google | **28** |
| clean in LibreOffice | **122** |

## The capability table, `benchmarks/GOOGLE-VS-LIBREOFFICE.md`

Regenerated from `gverify.py --matrix`. The five rows where Google is strictest and LibreOffice nearly clean:

| check | LibreOffice fails | Google fails |
|:--|--:|--:|
| `18\_displacement` | 20 | **109** |
| `32\_stroke\_lines` | 1 | **85** |
| `05\_chars\_extra` | 3 | **79** |
| `04\_chars\_missing` | 2 | **66** |
| `25\_invisible\_text` | 0 | **47** |

`32\_stroke\_lines` and `05\_chars\_extra` remain one construct, not two: a rule is emitted as a floating `<w:drawing>`, Google drops the shape and keeps the anchor, and the anchor is counted as a character. The table now says so in a construct section, with the two settled renderer facts and a pointer to the four measured fixes that did not work, so the next attempt starts from evidence.

## The current-engine view

`gverify.py --report` prints a narrower set, because it counts only results carrying the engine stamp of the engine on HEAD:

| | |
|:--|--:|
| verified | **81** |
| pass all 42 | **12** |
| fail at least one | **46** |
| refused on page count | **23** |

Its five largest failing checks:

| check | documents |
|:--|--:|
| `04\_chars\_missing` | **24** |
| `18\_displacement` | **24** |
| `59\_shape\_anchor` | **19** |
| `60\_text\_column\_right\_edge` | **19** |
| `13\_text\_colours` | **18** |

## Stage and next

`stage.py`: **classify**, 162 documents still failing, next action "classify 162 failing documents - the table is older than the results". That table is `DEFECT-CLASSES-GOOGLE.md`, the classifier cron's file. The capability table was this cron's last deliverable and it is committed.
