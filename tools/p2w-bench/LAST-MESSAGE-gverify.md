# P2W Google Verify - Run Report

**23 Nov 2026 · 15:26 IST · stage classify**

> 60 documents re-measured through Google and LibreOffice on engine `5beb8b9d`. 84 of 213 now carry a current-engine Google result: 23 pass all 42, 38 fail at least one, 23 refused on page count.

## Measured on the engine in the tree

| | |
|:--|--:|
| documents with a current-engine Google result | **84** |
| pass all 42 | **23** |
| fail at least one | **38** |
| refused on page count | **23** |

## Checks Google fails on those documents

| check | documents |
|:--|--:|
| `18\_displacement` | **20** |
| `47\_margins` | **12** |
| `60\_text\_column\_right\_edge` | **12** |
| `04\_chars\_missing` | **10** |
| `43\_within\_10pt\_x` | **6** |
| `25\_invisible\_text` | **6** |
| `17\_matched\_runs` | **6** |

## The whole corpus, both renderers

190 documents have both renders. LibreOffice passes all 42 on 122 of them, Google on 30. The widest gaps are `18\_displacement` (101 in Google against 20 in LibreOffice), `04\_chars\_missing` (65 against 2) and `25\_invisible\_text` (48 against 0).

## Held back

`74_balance_sheet_indented_subitems` still fails `18\_displacement` in Google on engine `5beb8b9d`, the same single check it failed on `98be7c3c`. The gate refuses a commit that lowers a document's Google score, so its committed result stays as it was and this run's reading sits in `FINDINGS/` beside the note that already explains it.

## Stage and next

`stage.py` says **classify**: 160 documents fail a check in the table. It also still reports 213 measured, because `measured()` counts every result file and never asks which engine wrote it - `gverify.py --plan` is the honest counter and says 84. That discrepancy is written up in `BLOCKERS.md`. The capability table is regenerated for this engine; grouping the failures into classes is the classifier cron's job, not this one's.
