# P2W Google Verify - Run Report

**27 Nov 2026 · 10:09 IST · stage measure-google**

> 205 of 213 measured in Google, 8 refused on page count. Google passes every check on 44; LibreOffice on 135 of the same 205.

This run rebuilt the corpus on a cold pod, took the next slice of documents through Drive and Google's own PDF export, and scored every one of them; the results are committed with the run. The LibreOffice column is now the backlog, since its results carry an older engine.

| checks applied | **42, 44, 47 (mixed - a document is clean only against its own set)** |
| measured against the current set | **71 of 205** |
## Measured

| | |
|:--|--:|
| scored | **205** |
| refused on page count | **8** |
| clean in Google | **44** |
| passes in LibreOffice (proxy, not the renderer the user opens) | **135** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **115** | 18 |
| `04\_chars\_missing` | **48** | 2 |
| `60\_text\_column\_right\_edge` | **60** | 18 |
| `59\_shape\_anchor` | **46** | 10 |
| `13\_text\_colours` | **32** | 1 |
| `45\_char\_accuracy` | **33** | 2 |
| `17\_matched\_runs` | **30** | 5 |
| `26\_text\_overlap` | **17** | 2 |

The first row is the class to take: `18\_displacement`, 115 documents in Google against 18 in LibreOffice.

