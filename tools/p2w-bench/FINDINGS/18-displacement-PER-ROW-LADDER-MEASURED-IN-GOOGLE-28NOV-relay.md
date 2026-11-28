# Per-row ladder declaration: measured in Google, worst_dy 16.2 -> 4.5 pt, check 18 still fails

**Run:** relay fixer slot, 28 Nov 2026, engine in the tree `a05b20eb05fe0fc8`.
One engine change, built and measured end to end in Google, then reverted. **A lead, not a kept change.**

## What was built

The finding `GOOGLE-LOOP-PROVEN-TODAY-AND-RUNG-CONSTANT-INERT-28NOV-fixer.md` said the next change is not
another constant but choosing the under-declaration **per row** on Google's `0.75 pt` ladder,
`laid(d) = 0.75 * (round(d / 0.75) + 1)`. That is what this run built, in `DocxWriter.java`'s row loop:

1. `FOOT_ROOM_MIN_TW = 100 -> 75`, so the rows of a dense table are no longer refused the rung.
2. The fixed `rowHeightTw -= ROW_RUNG_UNDER_TW` (10 tw) is replaced by a search over
   `u = 0, 5, ... 40 tw` for the `u` that minimises `|laid((H-u)/20) - H/20|`, the smaller `u` winning a tie.

## What it emitted, before any Drive call

`320_balance_sheet_statutory` at HEAD declares `280 x16, 260 x5`. With the change it declares
**`275 x16, 245 x5`** — exactly the arithmetic the earlier finding predicted (+0.25 pt on a 14.00 pt pitch,
-0.25 pt on a 13.00 pt pitch). That prediction was written down before the build and the emitted twips matched
it, so the patch does what it claims.

## What Google laid out

Same document, same day, same three-call loop, three engines:

| engine | rows declared | passed | `med_dy` | `worst_dy` |
|---|:--|:--|--:|--:|
| HEAD `a05b20eb` | 280 / 260 | 46/47 | 7.2 | **16.2** |
| footRoom 75 only `31324da9` (previous run) | 270 / 250 | 46/47 | 0.4 | 5.2 |
| footRoom 75 + per-row d `31932038` (this run) | 275 / 245 | 46/47 | 0.4 | **4.5** |

`18_displacement` still fails. The residual is now the **unavoidable** ladder bias: 14.00 and 13.00 pt are not
on the ladder at all, so the best any single declaration can do is +0.25 pt per row, and 16 rows accumulate
`+4.0 pt` before the second table pulls it back. `worst_dy 4.5` sits just over the check's
`clamp(0.35*size, 1.5, 4.5)` tolerance on the last rows of table 1, and more runs are out than
`max(2, ceil(0.05*n))` allows.

## Why it is not committed

`regress.py --check` refuses an engine that has not been measured across the corpus, and the corpus-wide
Google re-measure (206 documents x 3 Drive calls) does not fit in a slot. The change was reverted, the engine
rebuilt to HEAD, `320` re-converted and **re-measured in Google at HEAD to restore its stored row**
(46/47, `med_dy 7.2`, `worst_dy 16.2`, engine `a05b20eb05fe0fc8`) so the table still describes the tree.

## What the next run should do

The remaining 4.0 pt is a **bias**, not a rung: cancel it by dithering the declaration instead of holding one
per table — take `-0.50 pt` (255 tw) on one row in every three, which cancels four `+0.25` rows exactly. That
is three lines in the same loop and one Google measurement on `320`. Only when `18_displacement` passes there
does the corpus-wide re-measure pay for itself: 19 documents fail that check alone.
