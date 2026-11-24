# P2W Google Verify - Run Report

**24 Nov 2026 · 10:28 IST · stage classify**

> 190 of 213 measured in Google, 23 refused on page count. Google passes all 42 on 35; LibreOffice on 124.

This run measured nothing: both sides of the corpus were already on disk, so the stage is
classify and the measuring work is finished. The capability table was regenerated from the committed
results and committed unchanged in substance - the check counts are the same as the table it
replaced - and the run stopped there. Grouping the failures into classes belongs to the classifier
cron, and changing the engine belongs to the fixer; neither is this cron's to do.

## Measured

| | |
|:--|--:|
| scored | **190** |
| refused on page count | **23** |
| clean in Google | **35** |
| clean in LibreOffice | **124** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **102** | 20 |
| `04\_chars\_missing` | **65** | 2 |
| `25\_invisible\_text` | **43** | 0 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `59\_shape\_anchor` | **45** | 9 |
| `45\_char\_accuracy` | **37** | 2 |
| `13\_text\_colours` | **32** | 1 |
| `44\_header\_footer` | **30** | 0 |

The first row is the class to take: `18\_displacement`, 102 documents in Google against 20 in LibreOffice.

