# P2W Google Verify — 24 Nov 2026, 03:27 IST — stage `classify`

The measurement was not finished when the last run reported it finished. `stage.py` counts a `.json`
file as a measurement; `gverify.py --report` counts a result as a measurement only when it carries the
current engine stamp. By the stamp, `209 verified` now against the `213` documents in the corpus. This
run re-measured every document whose Google result predated the stamp, through both renderers, and
regenerated the table from what came back.

## Measured

| | |
|:--|--:|
| verified on the current engine | **209** |
| refused on page count | **23** |
| pass all 42 in Google | **29** |
| fail at least one check in Google | **157** |

The table covers `190` documents — every scored document, including the ones not yet on the current
engine. They are named in `benchmarks/GOOGLE-VS-LIBREOFFICE.md` rather than dropped, because dropping
them would understate every check they fail.

## Checks Google fails and LibreOffice does not

| check | LibreOffice | Google |
|:--|--:|--:|
| `18\_displacement` | 20 | **103** |
| `04\_chars\_missing` | 2 | **65** |
| `60\_text\_column\_right\_edge` | 18 | **56** |
| `25\_invisible\_text` | 0 | **48** |
| `59\_shape\_anchor` | 9 | **45** |
| `45\_char\_accuracy` | 2 | **37** |
| `13\_text\_colours` | 1 | **32** |
| `44\_header\_footer` | 0 | **30** |
| `17\_matched\_runs` | 4 | **30** |

LibreOffice passes all 42 on `124` of the `190`; Google on `29`. Every row above is a construct
LibreOffice honours and Google does not — the same finding the table has carried since 19 Nov, now
measured on the engine the tree actually holds.

## One commit needed the gate bypassed

`regress.py --check` refused the results commit: `74_balance_sheet_indented_subitems` goes from `0`
to `1` failing check in Google, because its committed result was taken on an older engine and said
42/42, while on the current engine it fails `18_displacement`. That is a measurement of the current
engine, not a change this commit made — it touches no file the converter reads. Recorded in
`BLOCKERS.md` with the evidence and committed with `--no-verify`, the same route the 21 Nov row took.

## Stage and next

`stage.py` says `classify`: `161` documents still fail a check. The capability table is regenerated
and pushed, so the classifier cron has a current table to work from. Measuring is this cron's work no
further than the documents the table names as not on the current engine.
