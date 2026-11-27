# P2W Google Verify - Run Report

**27 Nov 2026 · 21:42 IST · stage classify**

> 206 of 214 measured in Google, 8 refused on page count. Google passes every check on 46; LibreOffice on 102 of the same 206.

This run finished the Google measurement: the last document the planner still listed was staged, converted in Google Docs and collected, and every document now carries a result. The LibreOffice half was then refreshed on the engine in the tree for every document this pod holds the converted .docx for, and the capability table was regenerated and committed. The pairs that refresh could not reach are recorded in BLOCKERS.md with the measurement beside them.

| checks applied | **42, 44, 47 (mixed - a document is clean only against its own set)** |
| measured against the current set | **71 of 206** |
## Measured

| | |
|:--|--:|
| scored | **206** |
| refused on page count | **8** |
| clean in Google | **46** |
| passes in LibreOffice (proxy, not the renderer the user opens) | **102** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `04\_chars\_missing` | **54** | 2 |
| `18\_displacement` | **108** | 64 |
| `60\_text\_column\_right\_edge` | **62** | 18 |
| `13\_text\_colours` | **32** | 1 |
| `45\_char\_accuracy` | **33** | 2 |
| `59\_shape\_anchor` | **50** | 23 |
| `17\_matched\_runs` | **30** | 5 |
| `44\_header\_footer` | **19** | 0 |

The first row is the class to take: `04\_chars\_missing`, 54 documents in Google against 2 in LibreOffice.

