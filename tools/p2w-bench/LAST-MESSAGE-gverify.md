# P2W Google Verify - Run Report

**27 Nov 2026 · stage fix · this slot ran the classify stage**

> 206 of 214 measured in Google, 8 refused on page count. Google passes every check on 46; LibreOffice on 102 of the same 206.

## Coverage

| | |
|:--|--:|
| checks applied | **42, 44, 47 (mixed - a document is clean only against its own set)** |
| measured against the current set | **71 of 206** |

## Measured

| | |
|:--|--:|
| scored | **206** |
| refused on page count | **8** |
| clean in Google | **46** |
| passes in LibreOffice (proxy, not the renderer the user opens) | **102** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `04\_chars\_missing` | **54** | 2 |
| `18\_displacement` | **108** | 64 |
| `60\_text\_column\_right\_edge` | **62** | 18 |
| `13\_text\_colours` | **32** | 1 |
| `45\_char\_accuracy` | **33** | 2 |
| `59\_shape\_anchor` | **50** | 23 |
| `17\_matched\_runs` | **30** | 5 |
| `44\_header\_footer` | **19** | 0 |

The first row is the class to take: `04\_chars\_missing`, 54 documents in Google against 2 in LibreOffice.


## What this slot did

The stage was `classify`: the Google class table was older than the results it summarises, so it was regenerated from the store by `classify_google.py` - it is a build product and is never edited by hand. The capability table was checked against `gverify.py --matrix` and is already identical to it.

The regenerated table exposed one false sentence, and it came from the reader rather than the store. `classify_google.py` hashed every `engine/*.java`, so it printed "0 of the 206 Google results were measured on the engine in the tree" over 206 results that all are. The hash differed by `TxtWriter.java`, a file the .docx pipeline never reads. `gverify.py` and `report.py` were given the same scope on 27 Nov; this reader was missed, and it now uses the quantity the store is stamped with. Class table and capability table name the same engine.

Both are committed, and `stage.py` now reads `fix` - not this cron's stage, so the slot stops here.
