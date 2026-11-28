# P2W Google Verify - Run Report

**28 Nov 2026 · 07:32 IST · stage classify**

> 206 of 214 measured in Google, 8 refused on page count. Google passes every check on 48; LibreOffice on 86 of the same 206.

This run converted the corpus documents the pod did not have and closed the LibreOffice backlog, so both halves of the table are now measured on the engine in the tree - the pair is real for the first time instead of a Google column beside an older engine's renders. No engine code was touched and nothing was classified; the table is committed and the classifier cron takes it from here.

| checks applied | **42, 44, 47 (mixed - a document is clean only against its own set)** |
| measured against the current set | **71 of 206** |
## Measured

| | |
|:--|--:|
| scored | **206** |
| refused on page count | **8** |
| clean in Google | **48** |
| passes in LibreOffice (proxy, not the renderer the user opens) | **86** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `04\_chars\_missing` | **54** | 2 |
| `60\_text\_column\_right\_edge` | **59** | 18 |
| `13\_text\_colours` | **32** | 1 |
| `45\_char\_accuracy` | **33** | 2 |
| `17\_matched\_runs` | **30** | 5 |
| `18\_displacement` | **108** | 89 |
| `44\_header\_footer` | **19** | 0 |
| `26\_text\_overlap` | **19** | 3 |

The first row is the class to take: `04\_chars\_missing`, 54 documents in Google against 2 in LibreOffice.

