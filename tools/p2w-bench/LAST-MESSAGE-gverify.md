# P2W Google Verify - Run Report

**21 Nov 2026 · 14:30 IST · stage fix · this run: classify**

The stage on arrival was `classify`. This run wrote the class table, committed it, and the evidence
moved the pipeline to `fix`. No engine code was touched.

## What this run did

`benchmarks/DEFECT-CLASSES-GOOGLE.md` was older than the measurement commit it summarises, which is
exactly what `stage.py` reports as `classify`. `classify_google.py` was re-run against the committed
results and the table regenerated - one row per failing check, ranked by the Google-minus-LibreOffice
gap - then committed together with `benchmarks/gverify`, `benchmarks/gverify-lo` and
`benchmarks/GOOGLE-VS-LIBREOFFICE.md`. `classify_google.py --check` now reports the table up to date.
The pre-commit gate passed with scope `nothing`: no engine change, so no document was re-measured.

## Measured

| | |
|:--|--:|
| scored in Google | **192** |
| refused on page count | **21** |
| clean in Google | **6** |
| clean in LibreOffice | **122** |
| still failing a check | **186** |

## Where Google loses what LibreOffice keeps

| check | Google fails | LibreOffice fails |
|:--|--:|--:|
| `32\_stroke\_lines` | **145** | 1 |
| `05\_chars\_extra` | **141** | 3 |
| `18\_displacement` | **124** | 20 |
| `04\_chars\_missing` | **66** | 2 |
| `25\_invisible\_text` | **49** | 0 |
| `59\_shape\_anchor` | **58** | 11 |
| `60\_text\_column\_right\_edge` | **58** | 18 |
| `45\_char\_accuracy` | **37** | 2 |

## Two counts that disagree, and which one the fixer should read

`gverify.py --report` counts **141** verified: **114** fail at least one check and **6** pass all 42,
beside **21** refused. It counts only results carrying the current engine stamp. `stage.py` counts
**213** documents measured and **192** scored, because it counts result files, some of which carry no
engine stamp.

The class table is built from the files, so its per-check counts are the wider set: **145** on
`32\_stroke\_lines` and **141** on `05\_chars\_extra`, against **76** and **76** in `--report`'s
current-engine list. The table names which checks to work on; the current-engine counts in `--report`
are the ones a fix has to move.

## Next

`fix` takes one class at a time, smallest first. The head of the gap is `32\_stroke\_lines`, **145**
documents in Google against **1** in LibreOffice.
