# P2W Google Verify - Run Report

**20 Nov 2026 · 16:31 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 7; LibreOffice on 122.

This run's stage was classify, so the measuring work was already finished: I regenerated the capability table from both renderers and committed it, refreshed the LibreOffice side alongside it, and stopped there. Nothing was classified and no engine code was touched - the table is the last deliverable this cron owes, and the classifier cron reads it next.


## Measured

| | |
|:--|--:|
| scored | **192** |
| refused on page count | **21** |
| clean in Google | **7** |
| clean in LibreOffice | **122** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `32\_stroke\_lines` | **145** | 2 |
| `05\_chars\_extra` | **141** | 9 |
| `18\_displacement` | **125** | 21 |
| `04\_chars\_missing` | **67** | 9 |
| `25\_invisible\_text` | **49** | 1 |
| `59\_shape\_anchor` | **58** | 13 |
| `13\_text\_colours` | **32** | 1 |
| `45\_char\_accuracy` | **38** | 9 |

The first row is the class to take: `32\_stroke\_lines`, 145 documents in Google against 2 in LibreOffice.

