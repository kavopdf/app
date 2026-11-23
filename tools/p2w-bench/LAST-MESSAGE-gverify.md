# P2W Google Verify - Run Report

**23 Nov 2026 · 08:31 IST · stage classify**

> 190 of 213 measured in Google, 23 refused on page count. Google passes all 42 on 30; LibreOffice on 122.

This run's stage was classify, so it measured nothing new and changed no engine code. It regenerated the capability table from the committed results, and replaced the header's "same engine" claim with a computed coverage table: the engine on HEAD has moved since the last measurement, so the table is a record of what the two renderers do to these documents, not a statement about HEAD. The classifier cron owns the class table from here.

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
| `32\_stroke\_lines` | **50** | 1 |
| `25\_invisible\_text` | **48** | 0 |
| `05\_chars\_extra` | **45** | 3 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `59\_shape\_anchor` | **45** | 9 |
| `45\_char\_accuracy` | **37** | 2 |

The first row is the class to take: `18\_displacement`, 101 documents in Google against 20 in LibreOffice.

