# 18_displacement — the cell-before patch, measured in Google at last

**27 Nov 2026, relay fixer slot 19:18 IST.** The 18:00 run left this as its one open question:
`PATCHES/18-small-dy-cellbefore.patch` moves `w:before` exactly as its arithmetic predicts, and the
LibreOffice instrument (`screen.py`) is blind to a 1.7–3.2 pt move (share5 counts ink > 5 px away).
It asked for a Google render of HEAD vs patch. This run made it, on the three documents the store's
own census named as "fail 18_displacement and nothing else".

## What was measured

Engine `a05b20eb05fe0fc8` (HEAD) → `f4ce54f257d15f1c` (patch applied, `javac` rebuilt, same corpus
PDFs). Same three documents, same Drive folder, Google's own PDF export, `gverify.py --collect`,
`verify_google.py` 42 checks.

| Document | HEAD | after patch | med_dy | worst_dy | verdict |
|:--|:--|:--|:--|:--|:--|
| `74_balance_sheet_indented_subitems` | 41/42, fail `18` | **42/42** | 1.5 → **0.6** | 4.6 → **2.5** | **CLEAN** |
| `bus-timetable-station-left-times-right` | 41/42, fail `18` | 41/42, fail `46_text_crossing_rule` | 4.2 → **1.1** | 5.9 → **3.0** | 18 fixed, **new failure** |
| `72_bank_statement_no_rules_right_amounts` | 41/42, fail `18` | 41/42, fail `18` | **−1.0 → −3.0** | 3.5 → 5.2 | **worse** |

The XML moves exactly as the patch's arithmetic says (`w:before` 170→136 on 74, 317→254 on
bus-timetable, 348→278 on 72). So the change reaches the render. What Google then does with it is
**not one law**:

- On `74_balance_sheet_indented_subitems` (box 170 tw of a 340 tw row, two tables) Google moves the
  baseline by the full predicted amount and the document goes CLEAN. This is the branch's own case.
- On `bus-timetable` (33 rows, 328 tw row, hairline box ≈ 13 tw) the displacement improves by
  3.1 pt as predicted but the raised cell's text now crosses a rule — `46_text_crossing_rule`, a
  failure that was not there before. Google-visible regression.
- On `72_bank_statement` the same edit moves dy the *wrong way* (−1.0 → −3.0). The raw shortfall
  (`rowHeightTw − cellBoxTw`) was closer to what Google does on that document than the
  `LINE_BASE × shortfall` form.

## Why it was not landed

`regress.py --check` refuses a Google regression, and rule 3 of the charter refuses one on the merits:
one document becomes CLEAN, one trades its failure for a different one, one gets worse. A net of
−1 is not a fix. The patch stays in `PATCHES/`; the engine is unchanged in the tree and the three
`benchmarks/gverify/*.json` rows were restored to their HEAD measurement, because a row measured on
`f4ce54f257d15f1c` describes an engine that is not in the tree.

## What this settles, and the next experiment

Settled: **the branch is a real defect** (the arithmetic in the previous run's report is confirmed
against a renderer the user opens, not just against the XML), and **a class-wide form of it is
wrong** — the correction is right for a cell that fills its row and wrong for a hairline cell.

Untested, and the next run's first experiment: gate the new form on the cell filling its row —
`cellBoxTw * 2 >= rowHeightTw`. It applies to `74` (170 of 340) and not to `bus-timetable` (13 of
328) or `72`, so the prediction is **74 stays CLEAN, bus-timetable and 72 are untouched**. Cost: one
build, three conversions, one Google round trip — the same 8 minutes this run spent. If it holds,
the class is worth re-censusing with the same predicate: the store's only-18 list has 24 names and
`DISP-TABLE.csv` carries `declared_row_pt` for each, so the box-vs-row ratio can be read before any
document is converted.
