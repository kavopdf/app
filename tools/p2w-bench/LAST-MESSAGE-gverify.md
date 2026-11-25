# P2W Google Verify - Run Report

**26 Nov 2026 · 04:15 IST · stage measure-google**

> 211 of 213 measured in Google, 2 refused on page count. Google passes every check on 42; LibreOffice on 137 of the same 211.

| checks applied | **42, 44, 47 (mixed - a document is clean only against its own set)** |
| measured against the current set | **73 of 211** |
## Measured

| | |
|:--|--:|
| scored | **211** |
| refused on page count | **2** |
| clean in Google | **42** |
| passes in LibreOffice (proxy, not the renderer the user opens) | **137** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **121** | 21 |
| `04\_chars\_missing` | **57** | 3 |
| `60\_text\_column\_right\_edge` | **63** | 19 |
| `59\_shape\_anchor` | **50** | 11 |
| `45\_char\_accuracy` | **36** | 3 |
| `13\_text\_colours` | **32** | 1 |
| `17\_matched\_runs` | **34** | 7 |
| `44\_header\_footer` | **19** | 1 |

The first row is the class to take: `18\_displacement`, 121 documents in Google against 21 in LibreOffice.

