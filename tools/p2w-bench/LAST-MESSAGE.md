# P2W Google Verify - Run Report

**21 Nov 2026 · 09:25 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 7; LibreOffice on 108.

This run added no new measurements. The Google side and the LibreOffice side were already complete on disk, so the work was to regenerate the capability table from the committed results and commit it, which is this cron's last deliverable. Nothing in the engine was touched. The table is now newer than the results it is built from, and grouping the failing documents into classes passes to the classifier cron.

## Measured

| | |
|:--|--:|
| scored | **192** |
| refused on page count | **21** |
| clean in Google | **7** |
| clean in LibreOffice | **108** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `32\_stroke\_lines` | **145** | 1 |
| `05\_chars\_extra` | **141** | 7 |
| `18\_displacement` | **125** | 19 |
| `04\_chars\_missing` | **67** | 7 |
| `25\_invisible\_text` | **49** | 1 |
| `59\_shape\_anchor` | **58** | 10 |
| `13\_text\_colours` | **32** | 1 |
| `45\_char\_accuracy` | **38** | 7 |

The first row is the class to take: `32\_stroke\_lines`, 145 documents in Google against 1 in LibreOffice.

