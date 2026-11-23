# P2W Google Verify - Run Report

**23 Nov 2026 · 21:29 IST · stage classify**

> 190 of 213 measured in Google, 23 refused on page count. Google passes all 42 on 30; LibreOffice on 122.

This run did the classify stage's own step and nothing else. I regenerated the capability table from the two committed result directories and committed it, with the engine-coverage block recomputed against the engine on HEAD; no row in the comparison moved, so the table is the same measurement it was, now with its coverage stated honestly. I measured no documents, changed no engine code, and did not classify - that is the next cron's slot.

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

