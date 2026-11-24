# P2W Google Verify - Run Report

**24 Nov 2026 · 09:27 IST · stage classify**

> 190 of 213 measured in Google, 23 refused on page count. Google passes all 42 on 35; LibreOffice on 124.

This run found the measuring stage already finished, so nothing new went to Drive. It regenerated the capability table from the committed results and pushed it, so the classifier cron reads a table that matches the results it describes.

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

