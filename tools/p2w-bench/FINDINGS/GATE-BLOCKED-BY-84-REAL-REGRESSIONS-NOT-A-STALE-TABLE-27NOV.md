# The gate is not blocked by a stale table - it is blocked by 84 real regressions

**Run 27 Nov 2026, fixer slot 22:00 IST.** Engine `a05b20eb05fe0fc8` (HEAD, clean tree, nothing of mine in it).

## What every previous run believed

Nine consecutive fixer reports recorded the same wall:

    ENGINE CHANGED (docx): table measured on d28ca7516c3f9165, the tree is a05b20eb05fe0fc8
    docx: no document worse than baseline
    REFUSED.

and read it as bookkeeping: "RANKING.csv is one engine old, re-measure and it will pass." The 20:09 run
said exactly that: *"What refuses is that RANKING.csv has not been re-measured on this engine."* This run
did that re-measurement - a full 212-document pass, six budgeted `gate.py` slices, ~26 minutes - and the
second line changed:

    docx: 96 REGRESSION(S)
    txt : no document worse than baseline
    REFUSED.

**The "no document worse than baseline" line was never a measurement of the current engine.** It was the
old table compared against the baseline it had been derived from. The gate was refusing correctly all
along, and the thing it was refusing was real.

## The measurement

Independent recomputation from `benchmarks/RANKING.csv` (new, engine `a05b20eb`) against
`benchmarks/RANKING-BASELINE.csv` (15 Nov), on `share5`, not read from `regress.py`:

| | count |
|:--|--:|
| documents compared | 212 |
| **worse than the 15 Nov baseline** | **84** |
| better | 47 |
| unchanged | 81 |
| median delta (all documents) | 0.00 |

`regress.py --check` counts **96** because it also refuses on `median_pt` movement; my 84 is the
`share@5` subset and the two are consistent, the tool's count being the stricter one.

Delta distribution among the 84: **18** worse by more than +10, **9** by +5..10, **39** by +1..5, **18** by
under +1.

## It is one construct, and it is tables

The worst fifteen are almost entirely documents whose content is a ruled table:

| document | 15 Nov | now | delta |
|:--|--:|--:|--:|
| `table-with-no-header-row` | 0.61 | 47.48 | **+46.87** |
| `boq-tender-bill-of-quantities` | 7.10 | 41.95 | +34.85 |
| `very-long-single-column-table` | 6.87 | 41.14 | +34.27 |
| `balance-sheet-and-profit-loss` | 6.20 | 36.69 | +30.49 |
| `price-list-2col-dense-right-aligned` | 2.69 | 27.89 | +25.20 |
| `table-across-page-break-repeated-header` | 9.41 | 33.52 | +24.11 |
| `electricity-bill` | 16.24 | 36.78 | +20.54 |
| `03_stamp_vertical_90deg` | 16.98 | 34.38 | +17.40 |
| `salary-slip-factory-wages` | 18.09 | 35.15 | +17.06 |
| `property-tax-receipt` | 10.78 | 27.45 | +16.67 |
| `360_restaurant_menu` | 34.43 | 50.18 | +15.75 |
| `mutual-fund-statement` | 12.05 | 27.80 | +15.75 |
| `form16-part-b` | 12.32 | 26.45 | +14.13 |
| `mobile-bill` | 18.48 | 30.09 | +11.61 |
| `bus-timetable-station-left-times-right` | 0.27 | 11.40 | +11.13 |

The improvements are a different construct and they are the mirror image: `415_inline_images`
89.04 -> 0.00, `411_nested_xobject_transforms` 31.05 -> 0.00, `itr-computation-with-slab-table`
68.82 -> 38.49. Image/xobject handling was fixed in this window; **table row placement went backwards**.
`price-list-2col-dense-right-aligned` and `74_balance_sheet_indented_subitems` are both documents the
20:09 run measured in Google for the `18_displacement` cell-before lead - they are regressions here on
`share5`, on the engine that patch was measured against.

## What this run did NOT do, deliberately

`regress.py --stamp` was **not** run, and the new `RANKING.csv` was **not** committed as the comparison
table.

`--stamp` would declare engine `a05b20eb` the measured engine. Its only effect on these 84 documents is to
make the gate stop naming them - it would ratify a 40-point loss on `table-with-no-header-row` as the new
floor and every later run would read "no document worse than baseline" over it. Non-negotiable 3 is "no
document gets worse"; a stamp that hides 84 is the exact mechanism by which a corpus quietly rots for 63
commits.

The measurement is kept as evidence instead: `FINDINGS/RANKING-a05b20eb05fe0fc8-FULL-CORPUS-27NOV.csv`.

## What the next run should do, in order

1. **Bisect the table regression, not the gate.** 63 engine commits landed unmeasured between
   `d28ca7516c3f9165` and `a05b20eb05fe0fc8`. Bisect on `table-with-no-header-row` (0.61 -> 47.48, the
   cleanest signal: it is a 48-point move and the document is a bare table). `git log --oneline -- ENGINE`
   gives the range; the corpus is warm and `gate.py --budget 250` scores a single document in seconds.
2. **Only then re-measure and stamp.** A stamp is honest when the engine is no worse than the baseline.
   Until the table construct is restored, `--stamp` is a ratification, not a measurement.
3. Do not re-run the `18_displacement` cell-before patch as a landable change on this engine - its two
   measured documents are in the 84.

## Reproduce

    bash tools/install-gate.sh                      # pod-prep converts the corpus, 214 docs, 4 slices of ~53
    python3 benchmarks/gate.py --budget 250         # repeat until "measured 212 of 212"
    python3 tools/p2w-bench/regress.py --check      # -> docx: 96 REGRESSION(S)

Do not skip step 2 with the reasoning "the table is only one engine old". That reasoning is what hid this
for nine runs.
