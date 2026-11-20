# P2W Google Verify - Run Report

**21 Nov 2026 · 01:28 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 7; LibreOffice on 108.

## Measured

| | |
|:--|--:|
| scored | **192** |
| refused on page count | **21** |
| clean in Google | **7** |
| clean in LibreOffice | **108** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `32\_stroke\_lines` | **145** | 1 |
| `05\_chars\_extra` | **141** | 7 |
| `18\_displacement` | **125** | 19 |
| `04\_chars\_missing` | **67** | 7 |
| `25\_invisible\_text` | **49** | 1 |
| `59\_shape\_anchor` | **58** | 10 |
| `13\_text\_colours` | **32** | 1 |
| `45\_char\_accuracy` | **38** | 7 |

The first row is the class to take: `32\_stroke\_lines`, 145 documents in Google against 1 in LibreOffice.


## What this run did

Stage was `classify`, which is this cron's stage. Both tables were regenerated from the tools that own them, then committed and pushed as `82b78f3`:

- `benchmarks/GOOGLE-VS-LIBREOFFICE.md` from `gverify.py --matrix` - every count in it identical to the previous commit.
- `benchmarks/DEFECT-CLASSES-GOOGLE.md` from `classify_google.py` - every row identical.

No engine code was touched. The pre-commit gate reported no engine change.

## Stage and what is next

`stage.py` prints `classify`, and its next line reads `classify 185 failing documents - the table is older than the results`. That gate compares file timestamps, not content: the committed class table is newer than the committed results, and regenerating it from the measurement this run changed only its timestamp line. A fresh clone rewrites every timestamp, so the next run will read `classify` again for the same reason. Nothing in this cron's own stages is left to do; the class table already names a class for every failing document.
