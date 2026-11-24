# P2W Google Verify - Run Report

**24 Nov 2026 · 13:30 IST · stage classify**

> 190 of 213 scored in Google, 23 refused on page count. Google passes every check on 35 of the 190, LibreOffice on 124 of the same 190. This run regenerated the capability table and committed it; not one count moved.

## Measured

| | |
|:--|--:|
| scored in Google | **190** |
| refused on page count | **23** |
| pass all 42 checks - Google | **35** |
| pass all 42 checks - LibreOffice | **124** |
| fail at least one check | **151** |
| scored, but on an older engine stamp | **4** |

## Where Google fails a check and LibreOffice passes it

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **102** | 20 |
| `04\_chars\_missing` | **65** | 2 |
| `25\_invisible\_text` | **43** | 0 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `59\_shape\_anchor` | **45** | 9 |
| `45\_char\_accuracy` | **37** | 2 |
| `13\_text\_colours` | **32** | 1 |
| `44\_header\_footer` | **30** | 0 |

Every row is a construct LibreOffice honours and Google does not. Two were settled earlier and were not re-derived: `32\_stroke\_lines` (a rule emitted as a floating drawing - Google drops the shape, keeps the anchor) and `05\_chars\_extra` (the same anchor counted as a character).

## What this run did

Regenerated `benchmarks/GOOGLE-VS-LIBREOFFICE.md` from `gverify.py --matrix` and committed it as `27bb458b`. Parsed both the old and the new file row by row: the same 34 check rows, the same 190 documents, and no row differs in either count column. The only difference is the order of rows where the two renderers fail equally - `--matrix` resolves those ties by iteration order, so two consecutive runs on identical results produce two different files. Recorded in `BLOCKERS.md` so the churn is not mistaken for movement.

## Stage

`stage.py` says **classify**, so this cron's measuring work is done and it stops here. Its next line reads: classify 155 failing documents.

The stage cannot advance from this side. Its exit condition is `benchmarks/DEFECT-CLASSES-GOOGLE.md` committed later than the Google results, and that file belongs to the classifier cron, whose own gate (`round.py --phase`) answers `fix` this run - so the classifier stops before writing it. The fixer is working, so the pipeline is moving; only this label is pinned. Until that file is rewritten, every gverify slot in classify regenerates a table whose counts cannot change.

The 4 stale results - `15_stamp_on_scanned_page`, `magazine-2col-pullquote-spanning`, `newspaper-2col-fullwidth-headline`, `very-long-single-column-table` - are still on an older engine stamp and still count as measured in `stage.py`. Clearing them needs the corpus converted with the current engine, which this slot cannot do: it has `soffice` but no `java`, and `gverify.py --plan` dies on the missing `/scratch/work/p2w/out`. They all fail already, so the table's shape does not rest on them.

No engine code was touched this run.
