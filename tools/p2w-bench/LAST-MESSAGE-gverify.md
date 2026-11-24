# P2W Google Verify - Run Report

**24 Nov 2026 · 08:28 IST · stage classify**

> 190 of 213 measured in Google, 23 refused on page count. Google passes all 42 on 34; LibreOffice on 124.

This run measured nothing new: the evidence on disk already put the pass at the table stage, so the capability table was regenerated from the committed results on both renderers and pushed. It had drifted from what the file on disk said, so the fixer cron now reads the current pair rather than a stale one. Classifying those failures is the next cron's work, not this one's.

## Measured

| | |
|:--|--:|
| scored | **190** |
| refused on page count | **23** |
| clean in Google | **34** |
| clean in LibreOffice | **124** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **103** | 20 |
| `04\_chars\_missing` | **65** | 2 |
| `25\_invisible\_text` | **43** | 0 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `59\_shape\_anchor` | **45** | 9 |
| `45\_char\_accuracy` | **37** | 2 |
| `13\_text\_colours` | **32** | 1 |
| `44\_header\_footer` | **30** | 0 |

The first row is the class to take: `18\_displacement`, 103 documents in Google against 20 in LibreOffice.

