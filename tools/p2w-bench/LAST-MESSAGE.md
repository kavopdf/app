# P2W Google Verify - Run Report

**20 Nov 2026 · 19:29 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 7; LibreOffice on 122.

This run measured nothing new: the Google side was already complete, and both result sets were on disk. It regenerated the capability table from those committed results and pushed it, so the classifier cron has a table that is newer than the measurements it describes.

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

