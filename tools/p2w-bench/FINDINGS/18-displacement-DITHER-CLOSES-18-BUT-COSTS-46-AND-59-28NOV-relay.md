# Dithering the rung closes 18_displacement and costs two checks: 46_text_crossing_rule and 59_shape_anchor

**Run:** relay fixer slot, 28 Nov 2026, engine in the tree `a05b20eb05fe0fc8`.
Second measurement of the slot, built on the same row loop as
`18-displacement-PER-ROW-LADDER-MEASURED-IN-GOOGLE-28NOV-relay.md`. **A lead with a negative half.**

## What was built

The per-row ladder choice left a residual because 14.00 and 13.00 pt are not on Google's 0.75 pt ladder: the
nearest declaration is +0.25 pt and 16 rows of that is +4.0 pt. So the choice was made against the
**accumulated** error instead of each row's own: a `rungDriftPt` carried down the table, and each row declared
at the `u` in `0..60 tw` that leaves the smallest `|rungDriftPt + laid - pitch|`.

`320_balance_sheet_statutory` then declares `275, 260, 275, 275, 260, ...` (T1) and `245, 260, 245, 245, 260`
(T2) instead of `280 x16, 260 x5` — the `260` rows are the cancelling ones, `-0.50 pt` each.

## What Google laid out

| engine | declaration | passed | `med_dy` | `worst_dy` | fails |
|---|:--|:--|--:|--:|:--|
| HEAD `a05b20eb` | 280 / 260 | **46/47** | 7.2 | 16.2 | 18_displacement |
| per-row d `31932038` | 275 / 245 | 46/47 | 0.4 | 4.5 | 18_displacement |
| dither `1fbf4db6` | 275,260,... / 245,260,... | **45/47** | -0.6 | **2.8** | **46_text_crossing_rule, 59_shape_anchor** |

**`18_displacement` is solved by this construct**: `worst_dy 2.8` with `bad_pages []`, which is under the
`clamp(0.35*size, 1.5, 4.5)` tolerance on every run. The drift is gone.

**And it costs more than it buys.** `46_text_crossing_rule` and `59_shape_anchor` both fail, so the document
goes 46/47 -> 45/47. The `260` rows are 1.0 pt shorter than the page's 14.00 pt pitch, and the rule the page
drew no longer sits clear of the text in those rows; the shapes anchored to the rows move with them.

## The trade-off, stated as the thing the next run must solve

On this document the rows that must give up the rung have **4.25 pt (T1) and 3.75 pt (T2)** of clearance under
their lowest baseline. Cancelling `+0.25` needs a `-0.50` row, and a `-0.50` row is a 1.25 pt shrink — more
than the clearance those rows can spare without the text meeting the rule. So on `320` the ladder cannot be
cancelled and the row kept clear at the same time; the fix is not in the declaration alone.

## Why it is not committed

It is a net loss (46/47 -> 45/47) and it is measured on one document. Reverted; the engine rebuilt to HEAD,
`320` reconverted, and its stored row restored to the HEAD measurement taken earlier in this run
(46/47, `med_dy 7.2`, `worst_dy 16.2`, engine `a05b20eb05fe0fc8`, 11:14 today).

## What the next run should do

Do not spend another attempt on the declaration arithmetic — it is now bounded from both sides by measurement:
`+0.25` fails 18, `-0.50` passes 18 and fails 46 and 59. The lever that is left is the **rule**: if the row's
bottom rule is drawn from the row's own box rather than the page's, a shorter row moves its rule with its
text and 46 stops charging the shrink. That is a different construct in a different place, and it should be
proved on `320` with the three-call loop before anything else is built.
