# P2W Google Verify - Run Report

**21 Nov 2026 · 03:22 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 7; LibreOffice on 108.

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

## Stage

`stage.py` says **classify**: 213 measured, 192 scored, 21 refused, 185 failing. Next: classify 185 failing documents - the table is older than the results.

Nothing was uploaded this run: the measurement is complete, and the capability table in `benchmarks/GOOGLE-VS-LIBREOFFICE.md` was rewritten from `gverify.py --matrix`. Its figures are the same as the copy already committed - only the order of rows inside equal-gap groups moved, because the tool sorts on the gap alone and leaves ties to set order. It is now written with a fixed hash seed, so the same run produces the same file.

The class table (`benchmarks/DEFECT-CLASSES-GOOGLE.md`) is the classifier's build product, not this cron's, and is untouched.
