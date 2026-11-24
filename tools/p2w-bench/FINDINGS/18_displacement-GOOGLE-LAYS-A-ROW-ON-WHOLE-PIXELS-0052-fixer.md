# Google lays a table row out on whole CSS pixels, and truncates the fraction

**Measured 24 Nov 2026, fixer slot 04:52.** A complete, before-and-after measurement of the mechanism
behind a large part of `18_displacement`. **Not landed** - the gate refuses it - see "what it costs"
at the end, which is the whole reason this is a finding and not a commit.

## The mechanism, proved three ways

`362_price_list_dense` is a 29-row price list, one page, no rules drawn (`w:tblBorders` all `nil`).
Its rows are declared `w:trHeight 168 w:hRule="atLeast"` - 168 twips = 8.40 pt.

The source PDF's row pitch is **8.40 pt**, 27 of 27 gaps. Google renders it at **8.25 pt**, 27 of 27
gaps. The document is 41/42 in Google, failing only `18_displacement`, `med_dy -2.8`, `worst_dy 5.4`.

8.40 pt is 11.2 CSS pixels (1 px = 0.75 pt at 96 dpi). 8.25 pt is exactly 11 px. Google truncated
the fraction, per row, and charged it 27 times.

| declared `w:trHeight` | px asked for | pitch Google rendered | check |
|---|---|---|---|
| 168 tw (8.40 pt) | 11.2 | **8.25 pt** (11 px) | 41/42 FAIL |
| 180 tw (9.00 pt) | 12.0 | **9.00 pt** (12 px) | 41/42 FAIL |
| 165/180 diffused (11/12 px) | 11.2 avg | 8.25 and 9.00 mixed | **42/42 PASS** |

Each probe was a hand edit of the same `.docx` (`word/document.xml`, the `w:trHeight` values only),
uploaded to Drive, converted to a Google Doc, exported as PDF and scored against the source with
`verify_google.py`. No engine rebuild was involved, so the probe measures Google and nothing else.

**Declaring every row a whole pixel is not the fix.** 180 twips renders at exactly 9.00 pt - Google
honours whole pixels exactly - but that overshoots 0.6 pt a row and fails the same check from the
other side.

**Carrying the fraction is the fix.** Snap the CUMULATIVE height to whole pixels and write each row
as the difference:

```
pxCumTw += rowHeightTw;
wantCumTw = 15 * round(pxCumTw / 15.0);
rowHeightOutTw = wantCumTw - pxDoneTw;   // 165 or 180, never 168
pxDoneTw += rowHeightOutTw;
```

Cumulative error is then bounded by half a pixel however many rows the table has. On this document
that is 11/11/12 px repeating, which Google rendered at 8.25 and 9.00 and passed 42 of 42.

## The engine change, and its result in Google

`DocxWriter.java`, the ordinary-table `w:trHeight` emit (the `rowHeightTw` that becomes
`w:trHeight ... hRule="atLeast"`), guarded by `ruleTwHere == 0`. Built, and
`ConvertOne` run on the source PDF alone (one document per JVM, as `p2w.py` requires):

```
trHeights: [240, 165, 165, 180, 165, 165, 165, 165, 180, ...]   sum 4950 tw = 247.5 pt
before   : [240, 168 x 28]                                      sum 4950 tw = 247.5 pt
```

The total is identical; only its distribution changed. In Google:

```
362_price_list_dense.pdf    42/42 PASS
18_displacement detail      med_dy -0.9   worst_dy 2.6   bad_pages []   runs_matched 257
before                      med_dy -2.8   worst_dy 5.4   bad_pages [0]
```

**This document moves from 41/42 to 42/42 in the renderer the user opens.** It is the whole prize
the class exists for, and it is one `18_displacement` away on nine other documents
(`16_right_aligned_amounts_txtpos`, `31_times_body_arial_headings`, `36_embedded_subset_font`,
`68_journal_wide_table_spanning`, `71_invoice_space_aligned_no_rules`,
`72_bank_statement_no_rules_right_amounts`, `74_balance_sheet_indented_subitems`,
`balance-sheet-two-columns-of-figures`, `362`).

## What it costs, and why it is not landed

Full corpus pass on the patched engine (`p2w.py --force`, 212 of 212 measured), compared against the
committed `RANKING.csv`:

| | |
|---|---|
| documents worse | **17** |
| documents better | 5 |
| unchanged | 190 |
| worst | `electricity-bill` 1.33 -> **2.33** share@5 |
| over the gate's own tolerance | `330_cad_drawing_sheet` 4.91 -> **5.22** |

`regress.py --check` and `gate.py` both refuse. The cost is real and it is not noise: the engine is
deterministic, the `.docx` bytes changed, and LibreOffice lays out the redistributed rows at their new
heights. **LibreOffice does not quantise to pixels, so on that renderer the redistribution is pure
loss** - the rows move by up to half a pixel and nothing is gained, because there was nothing to
gain: the drift it corrects only exists in Google.

The engine was reverted (`git checkout -- app/`). Nothing was landed.

## The two conditions tried, and why neither is the answer

1. **`ruleTwHere == 0`** (an unruled row has no visible edge to move). Still cost
   `electricity-bill` 360->375->390 twips and 17 documents worse: that table has no rules in the row
   box either.
2. **`ruleTwHere == 0 && !exactRows`**. Excluded the target: `362` is `exactRows` (the pass measured
   its row edges), so it fell back to 168 and the fix did not apply.

**The discriminator is neither of those. It is whether the table's row heights are uniform** - a
grid whose pitch repeats is a line grid whose total must be preserved; a table of individually
measured boxes is already placed where the page drew it and has no pitch to preserve. That needs a
pre-pass over the rows to compute `rowHeightTw` for all of them before the first is written, which is
a bigger change than the one measured here and did not fit this slot.

## What the next run should do

1. Compute every row's `rowHeightTw` in a pre-pass, before the emit loop.
2. Apply the cumulative pixel snap only when those values are uniform (all equal).
3. Measure `electricity-bill` and `330_cad_drawing_sheet` FIRST - they are the two documents that
   carry the cost, and they are cheap to convert and score.
4. Only then run the full pass. If the uniform test holds, `362` and its eight neighbours become
   candidates for CLEAN and the proxy should not move at all.

A second, independent question this measurement raises: `18_displacement`'s tolerance is
`clamp(0.35*size, 1.5, 4.5)` pt, which is 2.0-6.0 px at 96 dpi. **A renderer that quantises row
heights to 1 px cannot in principle be held to a sub-pixel cumulative position**, so any table
document with more than about a dozen rows has a floor under its `med_dy` that no construct in the
`.docx` can remove. That is worth a decision with evidence: either the check tolerates one pixel of
accumulated quantisation per page, or every table document with a fractional pitch is permanently
unfixable.
