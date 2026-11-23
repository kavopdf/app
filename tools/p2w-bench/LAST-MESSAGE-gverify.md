# P2W Google Verify - Run Report

**23 Nov 2026 · 06:26 IST · stage classify**

> 190 of 213 measured in Google, 23 refused on page count. Google passes all 42 on 28; LibreOffice on 122.

This run did the table, not the measuring: the LibreOffice half was already complete, so it regenerated the capability table from the committed results and committed it. The table now carries the engine coverage it is computed over, because most pairs in it were rendered on older engines and a pair from two engines names the engines, not a construct. Recorded in BLOCKERS; the classifier cron takes the next slot.

## Measured

| | |
|:--|--:|
| scored | **190** |
| refused on page count | **23** |
| clean in Google | **28** |
| clean in LibreOffice | **122** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **109** | 20 |
| `32\_stroke\_lines` | **85** | 1 |
| `05\_chars\_extra` | **79** | 3 |
| `04\_chars\_missing` | **66** | 2 |
| `25\_invisible\_text` | **47** | 0 |
| `59\_shape\_anchor` | **52** | 9 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `45\_char\_accuracy` | **37** | 2 |

The first row is the class to take: `18\_displacement`, 109 documents in Google against 20 in LibreOffice.

