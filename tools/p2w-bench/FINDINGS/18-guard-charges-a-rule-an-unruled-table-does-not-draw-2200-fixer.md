# The spacer guard charges 0.75 pt per row for a rule an unruled table does not draw

24 Nov 2026, fixer. Slot 02:51 IST. Not committed: `regress.py --check` refuses an engine whose corpus
table is unmeasured, and `benchmarks/p2w.py` does not finish 212 documents inside one sandbox command
(see "Why this is a patch and not a commit" below). The patch is
`FINDINGS/18-guard-unruled-row-excess-2200.patch`.

## What the guard does today

`DocxWriter.emitTable`, the spacer guard:

```java
int rowExcessTw = 15 * Math.max(0, ctx.pageRowCount);   // 0.75 pt per row, every row
int slackTw    = ctx.budgetTw - Math.round(ctx.pageInkBottomPt * TWIPS_PER_PT);
boolean spendable = slackTw > 0
        && ctx.spacerSplitTw + roomWantTw + rowExcessTw <= slackTw;
```

When the gap is not spendable the gap is written as `w:line` alone, and Google lays `w:line` at about a
fifth of what it declares. So every refused spacer is a table sitting that far too high in Google — the
`18_displacement` construct. `rowExcessTw` is what makes the guard refuse.

## The charge contradicts the file's own rule

The `w:trHeight` block in the same method states the law the engine already relies on:

> An unruled table draws no rule and keeps its full pitch.

The row excess is 0.75 pt per row *because the renderer adds the row's own rule to it*. A table whose six
sides are all `w:val="nil"` has no rule to add. The guard charges it anyway.

## Measured, on this engine (`b97d8172ce642eb0`), from the emitted XML

Every document that has a spacer the guard decided, with its border census and its row count:

| document | spacers (before, line) | nil sides | rows | verdict |
|---|---|--:|--:|---|
| `68_journal_wide_table_spanning` | (0, 2880) | 6 | 7 | refused, unruled |
| `72_bank_statement_no_rules_right_amounts` | (0, 366) | 6 | 18 | refused, unruled |
| `bus-timetable-station-left-times-right` | (0, 127) | 6 | 33 | refused, unruled |
| `table-with-no-header-row` | (0, 247) | 0 | 26 | refused, **ruled** |
| `two-tables-stacked-with-no-gap` | (0, 247) | 0 | 13 | refused, **ruled** |
| `mobile-bill` | (0,248)(0,128)(0,124) | 0 | 24 | refused, **ruled** |
| `insurance-policy-schedule` | (0,288)(0,128)(0,120) | 0 | 22 | refused, **ruled** |
| `16_right_aligned_amounts_txtpos` | (92, 1) | 6 | 13 | spent |
| `362_price_list_dense` | (303, 1) | 6 | 29 | spent |
| `36_embedded_subset_font` | (267, 1) | 6 | 7 | spent |
| `balance-sheet-two-columns-of-figures` | (251,1)(0,1) | 12 | 16 | one spent, one 1-twip |

So of the three unruled-and-refused documents, the guard is charging 105, 270 and 495 twips of row
excess that no rule exists to justify.

## The patch

Charge the page's **ruled** rows, not the page's rows: `pageRuledRows(page)` sums `rows.size()` only over
tables where `t.ruled` or any `t.sideDrawn[i]` is true. One line changes in the guard.

**The charge is deliberately NOT also de-duplicated per page.** A page with three spacers charges the
count three times, which is over-conservative — but `mobile-bill` and `insurance-policy-schedule` are
exactly the pages where spending a gap unguarded was measured in Google to cost a page (46/47 on one
page to 43/47 on two, slot 23:10 on 22 Nov). Nothing measured supports loosening that, so only the rule
the page does not draw is removed.

## Before and after, measured, both formats, all 13 documents

`ConvertOne` on the 13, then a member-by-member diff of each `.docx` zip:

    document.xml changed ....... 2 of 13   72_bank_statement_no_rules_right_amounts,
                                           bus-timetable-station-left-times-right
    every other member .......... 0 of 13   (including all 12 other document.xml)
    every .txt .................. 0 of 13

And the two that changed changed exactly as intended — the gap moves from `w:line` into `w:before`
with the sum preserved to the twip:

   72_bank   base (before=0,  line=366) sum 366  ->  after (before=365, line=1) sum 366
   bus-time  base (before=0,  line=127) sum 127  ->  after (before=126, line=1) sum 127

## Why this cannot regress anything

Both branches of the guard emit a paragraph whose `w:before + w:line` equals `spacerTw` to the twip. A
renderer that honours both properties therefore lays the identical gap whichever branch runs. So the
change **cannot move a LibreOffice or Word render of any document**; it can only move what Google draws,
and only on a document where the guard flips from refused to spent. That is why the diff above is 2
document.xml of 13 and why the `.txt` half is untouched.

## What it is worth, honestly

`72_bank` and `bus-timetable` flip. The gap Google now draws grows by

    72_bank    366 - 2.5873*max(366/240, 0.06) = 366 tw - 287.3 tw = 78.7 tw = 3.93 pt
    bus-time   127 - 2.5873*max(127/240, 0.06) = 127 tw -  99.6 tw = 27.4 tw = 1.37 pt

against recorded displacements of `med_dy` -13.0 (worst 28.2) and -3.0 (worst 4.9). **Neither document
becomes clean.** This is a lead, not a win: it removes 3.93 pt and 1.37 pt of a 13.0 pt and 3.0 pt
displacement, and it removes a guard over-charge that was suppressing the correct construct on unruled
tables. `68_journal` does not flip (2860 tw of gap against far less slack) and is genuinely blocked.

## Why this is a patch and not a commit

`regress.py --check` on the changed tree:

    ENGINE CHANGED (docx): table measured on 3e7f7c4475343a35, the tree is 3e656727d8a12797
    REFUSED. This commit would land a regression or an unmeasured engine. There is no override.

The table it wants comes from `benchmarks/p2w.py`, which starts from `docx 0/213, measured 0/212` on a
fresh pod and did not checkpoint a single document in 295 s (`--budget 280`). **A 90-minute slot cannot
host that pass, and nothing can be committed from a slot that cannot host it.** The pass must be made
resumable, or the pass must be a cron of its own, before any engine change can land at all.
