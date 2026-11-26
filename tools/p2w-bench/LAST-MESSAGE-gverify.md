# P2W Google Verify - Run Report

**26 Nov 2026 · 19:06 IST · stage measure-google**

> 207 of 213 measured in Google, 6 refused on page count. Google passes every check on 47; LibreOffice on 135 of the same 207.

This run measured sixty fresh documents through Google and committed every one of them, so the measurement is no longer behind the engine. It also began the LibreOffice refresh the two-engine table needed, and that half is still the long pole.

| checks applied | **42, 44, 47 (mixed - a document is clean only against its own set)** |
| measured against the current set | **72 of 207** |
## Measured

| | |
|:--|--:|
| scored | **207** |
| refused on page count | **6** |
| clean in Google | **47** |
| passes in LibreOffice (proxy, not the renderer the user opens) | **135** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **107** | 20 |
| `04\_chars\_missing` | **51** | 2 |
| `60\_text\_column\_right\_edge` | **62** | 18 |
| `59\_shape\_anchor` | **47** | 11 |
| `13\_text\_colours` | **32** | 1 |
| `45\_char\_accuracy` | **33** | 2 |
| `17\_matched\_runs` | **29** | 5 |
| `26\_text\_overlap` | **19** | 3 |

The first row is the class to take: `18\_displacement`, 107 documents in Google against 20 in LibreOffice.

