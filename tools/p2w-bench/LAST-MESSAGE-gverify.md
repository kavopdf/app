# P2W Google Verify - Run Report

**23 Nov 2026 · 17:26 IST · stage classify**

> 190 of 213 measured in Google, 23 refused on page count. Google passes all 42 on 30; LibreOffice on 122.

## Measured

| | |
|:--|--:|
| scored | **190** |
| refused on page count | **23** |
| clean in Google | **30** |
| clean in LibreOffice | **122** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **100** | 20 |
| `04\_chars\_missing` | **65** | 2 |
| `25\_invisible\_text` | **48** | 0 |
| `32\_stroke\_lines` | **48** | 1 |
| `05\_chars\_extra` | **44** | 3 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `59\_shape\_anchor` | **45** | 9 |
| `45\_char\_accuracy` | **37** | 2 |

The first row is the class to take: `18\_displacement`, 100 documents in Google against 20 in LibreOffice.


## What this run did, and what the table is worth

The stage is `classify`, so this run's measuring work is finished: it regenerated the capability table from the committed results and committed it. The numbers in the table are unchanged - the regenerated file differs from the last one only in the order of rows that carry equal counts.

One caveat the fixer needs. `gverify.py --report`, which counts only results carrying the current engine stamp, prints 0 pass all 42 and 0 fail at least one, with 23 verified - and those 23 are the page-count refusals. The 190 scored results carry earlier engine stamps than the tree holds now, so none of them is a measurement of the current engine, and every one has to be re-measured before a class is taken from this table.

Next, per the stage: classify 160 failing documents - the table is older than the results.
