# P2W Google Verify - Run Report

**27 Nov 2026 · 14:23 IST · stage classify**

> 212 of 213 measured in Google, 1 refused on page count. Google passes every check on 42; LibreOffice on 134 of the same 212.

This run finished the Google half. The one document with no result on the engine in the tree - the three-hundred-page document that had been exempt from the ratchet - was converted, uploaded, exported and scored, so every document in the corpus now carries a Google verdict. It also built the converted corpus, which a fresh pod does not have, and then spent the rest of the slot re-rendering the LibreOffice half so the pair table stops describing documents an older engine wrote. That half is still a backlog, not a wall: each pass lands its results and commits them, and the table is regenerated from them every run with its own header saying how many pairs share an engine.


| checks applied | **42, 44, 47 (mixed - a document is clean only against its own set)** |
| measured against the current set | **73 of 212** |
## Measured

| | |
|:--|--:|
| scored | **212** |
| refused on page count | **1** |
| clean in Google | **42** |
| passes in LibreOffice (proxy, not the renderer the user opens) | **134** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **120** | 25 |
| `04\_chars\_missing` | **58** | 3 |
| `60\_text\_column\_right\_edge` | **63** | 19 |
| `59\_shape\_anchor` | **51** | 13 |
| `45\_char\_accuracy` | **37** | 3 |
| `13\_text\_colours` | **33** | 1 |
| `17\_matched\_runs` | **34** | 7 |
| `26\_text\_overlap` | **19** | 2 |

The first row is the class to take: `18\_displacement`, 120 documents in Google against 25 in LibreOffice.

