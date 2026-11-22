# `05_chars_extra`: 109 of the recorded failures are stale - the check was fixed, the rows were not

**22 Nov 2026, fixer slot 19:00.** Measured with a live Google round trip, not read off a file.

`verify_google.py`'s `norm_text()` now strips **U+200B** from both sides (the exporter writes one for
every `<w:tab/>`, so every tab used to read as an added character). `benchmarks/gverify/*.json` still
carries the verdicts written **before** that change.

| document | recorded | re-measured through Google today |
|:--|:--|:--|
| `01_stamp_rotated_15deg_upright` (16 `<w:tab/>`) | 34/42, `05_chars_extra` **FAILS** | **36/42, `05_chars_extra` PASSES** |

The other two documents re-measured today reproduce their recorded verdict exactly
(`two-tables-stacked-with-no-gap` 46/47 `18_displacement`; `313_power_of_attorney` 41/42
`60_text_column_right_edge`), so the difference is the check, not the engine. A fourth measurement
confirmed the engine stamp is a truncation artefact and not staleness: the 157 rows stamped `462353f`
and the 35 stamped `462353f9` are the same commit, and `gverify.py _done()` already prefix-matches them.

## What it does and does not change

* It does **not** make a document clean on its own: **no document fails `05_chars_extra` and nothing
  else** (the 21 one-check-away documents split 16 `18_displacement`, 2 `60_text_column_right_edge`,
  2 `32_stroke_lines`, 1 `47_margins`). Removing a phantom `05` from a document with two failures
  leaves it with one.
* It **does** change the class arithmetic. `classpick.py --leverage` prices `05_chars_extra` at **21.2
  clean documents** from a table in which 109 rows are failing it wrongly. That number is not a
  measurement any more. `18_displacement` is worth more than 38.7 in the corrected table, not less.
* It is the reason the recorded headline is "6 clean of 192": the `05` column has to be re-measured
  before any count of clean documents means anything. The pipeline's own `_done()` will re-measure
  them; a fixer cannot, because one document costs three Drive calls and the platform `upload` tool,
  so this slot could afford four.
