# P2W Google Verify - Run Report

**24 Nov 2026 · 19:32 IST · stage fix**

> 191 of 213 measured in Google, 22 refused on page count. Google passes every check on 35; LibreOffice on 125 of the same 191.

| checks applied | **42, 44, 47 (mixed - a document is clean only against its own set)** |
| measured against the current set | **62 of 191** |
## Measured

| | |
|:--|--:|
| scored | **191** |
| refused on page count | **22** |
| clean in Google | **35** |
| clean in LibreOffice | **125** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **103** | 20 |
| `04\_chars\_missing` | **65** | 2 |
| `25\_invisible\_text` | **43** | 0 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `59\_shape\_anchor` | **45** | 9 |
| `45\_char\_accuracy` | **38** | 2 |
| `13\_text\_colours` | **32** | 1 |
| `44\_header\_footer` | **30** | 0 |

The first row is the class to take: `18\_displacement`, 103 documents in Google against 20 in LibreOffice.


## What this run did

The slot opened at `classify`, and the classify work is finished: the capability table and the class table were both regenerated from the committed results and committed through the gate, which passed on a corpus rebuilt on this pod. `stage.py` now reads `fix`, with 156 documents still failing a check, so the next work on these classes belongs to the fixer.
