# P2W Google Verify - Run Report

**21 Nov 2026 · 10:29 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 7; LibreOffice on 108.

This run added nothing to the corpus: both halves are already complete, so the stage left is classify. I regenerated the capability table from the committed results - the counts match the table already in the repository row for row, so there was nothing to commit there. The table is current; the next move belongs to the classifier.


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

