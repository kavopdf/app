

## Reopened 2026-11-10

`20_within_10pt` was closed as unfixable with the reason "Google Docs has no exact
line spacing". A calibration run disproved it: documents written with `w:line` at
240, 360 and 480 twips came back from Drive at 11.3, 17.1 and 22.8 pt - proportional
and honoured, at about 95 % of the value asked. The class is open again and the
measurement is in `calibrate.py`.
