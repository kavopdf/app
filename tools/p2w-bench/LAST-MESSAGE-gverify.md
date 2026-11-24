# P2W Google Verify - Run Report

**24 Nov 2026 · 21:47 IST · stage classify**

> 191 of 213 measured in Google, 22 refused on page count. Google passes every check on 36; LibreOffice on 125 of the same 191.

This run's stage was classify, so it did no measuring. It regenerated the capability table from the committed results and pushed it: the table had been one result stale, and it now matches the corpus. The classifier cron takes it from here.

| checks applied | **42, 44, 47 (mixed - a document is clean only against its own set)** |
| measured against the current set | **62 of 191** |
## Measured

| | |
|:--|--:|
| scored | **191** |
| refused on page count | **22** |
| clean in Google | **36** |
| passes in LibreOffice (proxy, not the renderer the user opens) | **125** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **103** | 20 |
| `04\_chars\_missing` | **64** | 2 |
| `25\_invisible\_text` | **43** | 0 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `59\_shape\_anchor` | **45** | 9 |
| `45\_char\_accuracy` | **38** | 2 |
| `13\_text\_colours` | **32** | 1 |
| `44\_header\_footer` | **29** | 0 |

The first row is the class to take: `18\_displacement`, 103 documents in Google against 20 in LibreOffice.

