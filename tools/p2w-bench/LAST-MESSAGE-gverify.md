# P2W Google Verify - Run Report

**26 Nov 2026 · 12:57 IST · stage classify**

> 207 of 213 measured in Google, 6 refused on page count. Google passes every check on 42; LibreOffice on 135 of the same 207.

This run closed the Google side: the documents still without a render were built from HEAD, converted in Drive, exported and scored, and both result sets plus the capability table are committed. The LibreOffice column still trails the engine on many pairs, so the table's own engine-coverage note is the honest reading guide until that backlog is filled.

| checks applied | **42, 44, 47 (mixed - a document is clean only against its own set)** |
| measured against the current set | **72 of 207** |
## Measured

| | |
|:--|--:|
| scored | **207** |
| refused on page count | **6** |
| clean in Google | **42** |
| passes in LibreOffice (proxy, not the renderer the user opens) | **135** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **113** | 20 |
| `04\_chars\_missing` | **54** | 2 |
| `60\_text\_column\_right\_edge` | **62** | 18 |
| `59\_shape\_anchor` | **49** | 11 |
| `13\_text\_colours` | **32** | 1 |
| `45\_char\_accuracy` | **33** | 2 |
| `17\_matched\_runs` | **30** | 5 |
| `44\_header\_footer` | **18** | 0 |

The first row is the class to take: `18\_displacement`, 113 documents in Google against 20 in LibreOffice.

