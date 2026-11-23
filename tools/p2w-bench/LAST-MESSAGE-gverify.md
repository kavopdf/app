# P2W Google Verify - Run Report

**24 Nov 2026 · 02:26 IST · stage classify**

> 190 of 213 measured in Google, 23 refused on page count. Google passes all 42 on 30; LibreOffice on 122.

The measuring is finished, so this run measured nothing new. It regenerated the capability table from the committed results and pushed it; the classifier cron picks it up from there.

## Measured

| | |
|:--|--:|
| scored | **190** |
| refused on page count | **23** |
| clean in Google | **30** |
| clean in LibreOffice | **122** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **101** | 20 |
| `04\_chars\_missing` | **65** | 2 |
| `25\_invisible\_text` | **48** | 0 |
| `32\_stroke\_lines` | **47** | 1 |
| `05\_chars\_extra` | **43** | 3 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `59\_shape\_anchor` | **45** | 9 |
| `45\_char\_accuracy` | **37** | 2 |

The first row is the class to take: `18\_displacement`, 101 documents in Google against 20 in LibreOffice.

