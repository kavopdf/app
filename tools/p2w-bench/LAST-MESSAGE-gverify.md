# P2W Google Verify - Run Report

**23 Nov 2026 · 20:25 IST · stage classify**

> The Google measurement is finished: 190 documents scored, 23 refused on page count. Google passes all 42 on 30 of them, LibreOffice on 122.

## Measured

| | |
|:--|--:|
| scored through Google | **190** |
| refused on page count | **23** |
| clean in Google | **30** |
| clean in LibreOffice | **122** |

## Stage

| | |
|:--|:--|
| stage | classify |
| corpus | 212 documents |
| still failing a check | 160 documents |
| next | classify the 160 failing documents - the table is older than the results |

This run did the classify half that belongs to it: the capability table was regenerated from the committed results and committed. No engine code was touched and no document was re-measured - the Google side is complete, so `stage.py` no longer asks for more measurement.

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **101** | 20 |
| `04\_chars\_missing` | **65** | 2 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `25\_invisible\_text` | **48** | 0 |
| `32\_stroke\_lines` | **47** | 1 |
| `59\_shape\_anchor` | **45** | 9 |
| `05\_chars\_extra` | **43** | 3 |
| `45\_char\_accuracy` | **37** | 2 |
| `13\_text\_colours` | **32** | 1 |
| `44\_header\_footer` | **31** | 0 |

The class to take first is `18\_displacement`: 101 documents in Google against 20 in LibreOffice.

## The current-engine subset

`gverify.py --report` counts only the results carrying the engine on HEAD, so it prints a smaller set than the table above: 86 verified, 13 pass all 42, 50 fail at least one, 23 refused. That is why the class table and the capability table quote different counts for the same corpus - one is a measurement of HEAD, the other a record of what the two renderers do to these documents.
