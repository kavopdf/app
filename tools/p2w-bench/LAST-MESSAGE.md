# P2W Google Verify - Run Report

**20 Nov 2026 · 17:23 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 7; LibreOffice on 122.

This run added no new measurements - both renderers already had a result for every document - so it regenerated the capability table from the committed results, committed it, and stopped there for the classifier. One caveat when reading the table: the LibreOffice column is counted over every document that has a LibreOffice result, the Google column only over the ones that scored, so the two columns do not share a denominator. The per-check table below compares only the documents that have both.

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

