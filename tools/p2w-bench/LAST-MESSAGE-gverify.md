# P2W Google Verify - Run Report

**24 Nov 2026 · stage classify · both renderers**

> 190 of 213 documents scored in Google, 23 refused on page count. Google passes every check on 35 of them; LibreOffice passes on 124 of the same 190.

## Measured

| | |
|:--|--:|
| scored | **190** |
| refused on page count | **23** |
| clean in Google | **35** |
| clean in LibreOffice | **124** |

## Where the two renderers disagree

| check | Google fails | LibreOffice fails |
|:--|--:|--:|
| `18\_displacement` | **102** | 20 |
| `04\_chars\_missing` | **65** | 2 |
| `25\_invisible\_text` | **43** | 0 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `59\_shape\_anchor` | **45** | 9 |
| `45\_char\_accuracy` | **37** | 2 |
| `13\_text\_colours` | **32** | 1 |
| `44\_header\_footer` | **30** | 0 |

Every check Google fails and LibreOffice passes is a construct LibreOffice honours and Google does not. Two are already known and were not re-derived: `32\_stroke\_lines` (a rule emitted as a floating drawing - Google drops the shape and keeps the anchor) and `05\_chars\_extra` (the same anchor, counted as a character).

## Stage

`stage.py` says **classify**, so this cron's measuring work is done and it stops here. The capability table `benchmarks/GOOGLE-VS-LIBREOFFICE.md` was regenerated from `gverify.py --matrix` and committed this run; its counts are identical to the copy it replaced - the only difference was the order of rows where the two renderers fail equally.

Next is the classifier cron: group the failing documents into classes in `DEFECT-CLASSES-GOOGLE.md`. Until that file's commit is newer than the results, the stage stays `classify`.

## One caveat this run found

209 of 213 carry the current engine stamp, not 213. 4 of the 190 scored results measure a previous engine: `15\_stamp\_on\_scanned\_page`, `magazine-2col-pullquote-spanning`, `newspaper-2col-fullwidth-headline` and `very-long-single-column-table`. `stage.py` counts them as measured; `gverify.py --plan` would not, but it cannot run in this slot - it lists documents from a corpus directory that no run of this cron builds, and it exits on `FileNotFoundError` for it. All 4 already fail, so the table's shape does not depend on them, but their rows are not current. Recorded in `BLOCKERS.md` with what would clear it: one corpus pass, then `--collect` on those four names.

No engine code was touched this run.
