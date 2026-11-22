# P2W Google Verify - Run Report

**22 Nov 2026 · 05:30 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 7; LibreOffice on 122.

Nothing needed measuring this run: the Google side and the LibreOffice side were already complete, so the capability table was regenerated from the committed results, committed, and the run stopped at classify. The classifier cron picks it up from here.

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
| `32\_stroke\_lines` | **145** | 1 |
| `05\_chars\_extra` | **140** | 3 |
| `18\_displacement` | **124** | 20 |
| `04\_chars\_missing` | **66** | 2 |
| `25\_invisible\_text` | **49** | 0 |
| `59\_shape\_anchor` | **58** | 9 |
| `60\_text\_column\_right\_edge` | **58** | 18 |
| `45\_char\_accuracy` | **37** | 2 |

The first row is the class to take: `32\_stroke\_lines`, 145 documents in Google against 1 in LibreOffice.

