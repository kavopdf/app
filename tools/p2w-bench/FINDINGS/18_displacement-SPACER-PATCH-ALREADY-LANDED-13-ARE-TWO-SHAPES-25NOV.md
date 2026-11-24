# 18_displacement: the spacer patch is already landed, and the 13 one-check-away documents are two shapes

**Measured 25 Nov 2026, fixer run. Read this before applying `18_displacement-engine-topoffset-101951-cda8.md`.**

## What the old finding says, and why it is stale

`18_displacement-engine-topoffset-101951-cda8.md` ends with *"the smallest patch is one append() in the
spacer, at DocxWriter.java:5826-5828 - move the gap out of the line box and into the before-gap"* and status
`complete`. **That patch is already in the engine.** The spacer emitter is now `DocxWriter.java:6050-6115`
(the line numbers in the old finding have moved by ~190 lines) and it already splits the gap:

    spendable == true   ->  w:before="<spacerTw - 1>"  w:line="1"  w:lineRule="exact"
    spendable == false  ->  w:before="0"               w:line="<spacerTw>"  w:lineRule="exact"

with the reason written in the source: *"Google delivers w:before on an empty paragraph 1:1 and w:line on
the same paragraph at roughly a fifth ... spending the gap unguarded took mobile-bill and
insurance-policy-schedule from 46/47 on one page to 43/47 on two, content lost (slot 23:10, 22 Nov,
measured in Google both ways)."*

So the residual `18_displacement` is not an unapplied patch. **It is the guard refusing to spend, and a
second construct that has no spacer at all.** A run that starts from the old finding will re-implement a
change that is already in the tree.

## What was measured

Source of the document list: `benchmarks/gverify/*.json` filtered to `engine == b7699196` and
`status == "ok"`. **24 of the 187 current documents fail exactly one check, and 13 of those 24 fail only
`18_displacement`.** Those 13 are the cheapest documents in the corpus: one construct each stands between
them and CLEAN.

Counting the spacer paragraphs in their own converted `.docx` (a spacer = a paragraph whose mark is
`<w:sz w:val="2"/>` and whose `w:line` is over 100 twips):

| document | spacers | un-split | gap carried in `w:line` (pt) |
|:--|--:|--:|--:|
| 68_journal_wide_table_spanning | 1 | 1 | 144.0 |
| 72_bank_statement_no_rules_right_amounts | 1 | 1 | 18.3 |
| bus-timetable-station-left-times-right | 1 | 1 | 6.3 |
| table-with-no-header-row | 1 | 1 | 12.3 |
| two-tables-stacked-with-no-gap | 1 | 1 | 12.3 |
| mobile-bill | 3 | 3 | 25.0 |
| insurance-policy-schedule | 3 | 3 | 26.8 |
| 16_right_aligned_amounts_txtpos | 1 | **0** | - |
| 36_embedded_subset_font | 1 | **0** | - |
| 74_balance_sheet_indented_subitems | 2 | **0** | - |
| balance-sheet-two-columns-of-figures | 2 | **0** | - |
| 31_times_body_arial_headings | 0 | **0** | - |
| 71_invoice_space_aligned_no_rules | 0 | **0** | - |

**7 documents carry 11 un-split spacers. 6 documents carry none at all.**

The six with no un-split spacer have no page break either (`<w:br w:type="page"/>` count is 0 in all six)
and their rows are floored, not pitched: `w:trHeight w:hRule="atLeast"` at 380/400/320/360/340/232-320
twips. That is the **second** construct the old finding already names - *"rows are floored by `w:trHeight
w:hRule='atLeast'` ... that is the +1.85 to +3.6 pt per 100 pt of depth"* - and it needs the row patch, not
the spacer patch.

## What is now true

1. **No single spacer change can make all 13 clean.** The ceiling for the spacer construct is 7, and two of
   those seven (`mobile-bill`, `insurance-policy-schedule`) are the exact pair the guard was written to
   protect - spending their gap unguarded is measured to cost them three checks on two pages.
2. **The remaining 6 are a different construct and are worth separating from the class.** They are the
   progressive-drift shape, and they are the cheapest 6 documents in the corpus once the row pitch is
   understood, because none of them carries the guard's trade-off.
3. **The guard's `slackTw` test is the thing to attack, not the emission.** `spendable` is
   `slackTw > 0 && ctx.spacerSplitTw + roomWantTw + rowExcessTw <= slackTw`, and `slackTw` is
   `ctx.budgetTw - pageInkBottomPt`. Every one of the 7 is refused by that arithmetic, and the arithmetic
   uses a fixed `15 twips per row` excess - a number the row-construct measurement above can now replace
   with a measured one.

## What would prove this wrong

Convert the 6 no-spacer documents with only the spacer guard relaxed and find their `18_displacement`
still fails - that is the expected result and it is what separates the shapes. If instead they move, then
the spacer is reaching them through a path this census did not see (a spacer inside a column cell, which
`ctx.inColumn` handles differently) and this split is wrong.

The discriminator for the 7 is one Google round-trip: `68_journal_wide_table_spanning` carries a single
144 pt un-split spacer, the largest in the corpus, so if relaxing the guard for it does not move its dy,
the guard is not what is holding that document up.

## The transferable rule

**A FINDINGS entry marked `complete` is a claim about a tree that has since moved.** Grep the symbol, not
the line number, before applying a patch a finding describes - and when the patch is already there, the
finding's status is the thing that needs correcting, because the next run reads the status first.
