# P2W Google Verify - Run Report

**23 Nov 2026 · 23:24 IST · stage classify**

> 190 of 213 measured in Google, 23 refused on page count. Google passes all 42 on 30; LibreOffice on 122.

This run's stage is classify, so the measuring side had nothing to add: I regenerated the capability table from the committed results and it came back with the same counts, so the tree stays clean. The table is the handoff - the classifier cron takes the classes from here.

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

