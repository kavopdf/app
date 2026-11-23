# 60_text_column_right_edge — the stale-engine hypothesis is refuted on all four documents that share it

**23 Nov 2026 · fixer slot 18:58 → · engine at HEAD, unchanged · live Google round trips this slot**

## What was tested

24 documents sit **one check from clean** in the committed table, and 21 of them were last measured on
an engine that is not this one (`5beb8b9d`, `462353f`, `98be7c3c`). An earlier finding in this class
(`05_chars_extra-GOOGLE-TABLE-IS-STALE-…-0545-f1x.md`) had found three of three documents already
passing on HEAD where the table said they failed. The hypothesis: some of the 24 are already clean and
only the record is stale.

The cheapest test is the group that shares one check — **four documents all failing only
`60_text_column_right_edge`**, worth 17.0 clean documents across the class.

## Result — the table was right, all four times

| document | committed | re-measured on this engine |
|:--|--:|--:|
| `302_radiology_report` | 41/42, `60_text_column_right_edge` | **41/42**, `60_text_column_right_edge` |
| `313_power_of_attorney` | 41/42, `60_text_column_right_edge` | **41/42**, `60_text_column_right_edge` |
| `316_contract_with_schedules` | 46/47, `60_text_column_right_edge` | **46/47**, `60_text_column_right_edge` |
| `321_auditors_report` | 41/42, `60_text_column_right_edge` | **41/42**, `60_text_column_right_edge` |

Four of four reproduce exactly. The four `gverify/*.json` records have been re-stamped with the current
engine (`b7699196`) so the class is now a **current-engine** class and the next run does not re-derive
that.

## The signature, which is the useful part

All four report the identical pair: **`source=0`, `render=1`**. Not 0 → 40, not 3 → 90. **One** piece of
text crosses the column's right edge in Google and none does in the source, on four documents of four
different kinds (a radiology report, a power of attorney, a contract with schedules, an auditor's
report). A one-unit overshoot repeated across unrelated layouts reads as a constant, not a layout
failure — the same shape as the `w:line` charge law that produced a flat 0.78 pt on every table in
`18_displacement`.

That is the next test for this class, and it is cheap: the check already knows which text crosses the
edge, so the next run should print the crossing element's x and the column's right edge on one of these
four before proposing anything. **Nothing was changed in the engine this attempt — 0 moved, recorded as
`lead`.**
