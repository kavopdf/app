# P2W Google Verify - Run Report

**20 Nov 2026 · 18:30 IST · stage classify**

> 213 documents measured through Google: 192 scored, 21 refused on page count. On the same 192, Google passes all 42 checks on 7 and LibreOffice on 108.

## Measured

| | |
|:--|--:|
| measured through Google | **213** |
| scored | **192** |
| refused on page count | **21** |
| clean in Google | **7** |
| clean in LibreOffice | **108** |
| failing at least one check | **185** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `32\_stroke\_lines` | **145** | 1 |
| `05\_chars\_extra` | **141** | 7 |
| `18\_displacement` | **125** | 19 |
| `04\_chars\_missing` | **67** | 7 |
| `25\_invisible\_text` | **49** | 1 |
| `59\_shape\_anchor` | **58** | 10 |
| `45\_char\_accuracy` | **38** | 7 |
| `13\_text\_colours` | **32** | 1 |

The first row is the class to take: `32\_stroke\_lines` fails 145 documents in Google and 1 in LibreOffice.

## Stage

The evidence says **classify**. The capability table has been regenerated from both renderers and committed as `benchmarks/GOOGLE-VS-LIBREOFFICE.md`; 185 documents still fail at least one check. Next is grouping those 185 into classes. This cron stops at the table and does not touch the engine.
