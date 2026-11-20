# P2W Google Verify - Run Report

**20 Nov 2026 · 10:29 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 7; LibreOffice on 122.

Nothing needed moving this run: the Google side was already complete and the LibreOffice side already paired with it, so the capability table was regenerated from the committed results and committed, and the run stopped here for the classifier to take over.

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

