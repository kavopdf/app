# t13_amount_columns: the path census of all 18, and how far each construct reaches

20 Nov, by a subagent (engine built, all 18 PDFs from the corpus-v1 release, every document converted
through `TxtWriter` with a temporary stderr print - reverted, tree restored, rebuilt clean). The agent
ran out of its budget before writing this file; the numbers are its measurement, the write-up is the
fixer's. Nothing here is inferred from the source alone.

## Which path emits the misaligned amounts

| path | documents |
|---|---|
| Table only | 14 - 01_stamp_rotated_15deg_upright, 10_stamp_as_image, 22_invoice_four_columns_txtpos, 362_price_list_dense, 72_bank_statement_no_rules_right_amounts, balance-sheet-and-profit-loss, balance-sheet-two-columns-of-figures, electricity-bill, form16-part-b, gst-invoice-3line-items, gst-invoice-multipage-item-table, itr-computation-with-slab-table, payslip-label-left-amount-right, purchase-order |
| Paragraph only | 2 - bank-statement-horizontal-rules-only, gst-invoice-horizontal-rules-only |
| Mixed in one column | 2 - 29_dot_leaders_txtpos, 74_balance_sheet_indented_subitems |

## How far each construct reaches, measured

| construct | t13 pass of 18 | corpus checks |
|:--|--:|--:|
| per-table-column end column | 10 | 161 -> 171 |
| + a paragraph rule | 13 | -> 174 |
| + page-level bands pooling Para and Table right edges | 15 | -> 176 |

None of the three regressed a single document on the agent's sample.

The fixer then built the first two for real and measured them on the whole corpus: the table construct
10 better / 0 worse (checks 1784 -> 1794), the paragraph construct a further 2 better / 0 worse
(1794 -> 1796). `t13_amount_columns` now holds 6 documents.

## Is a paragraph rule derivable? Yes, but not from existing fields

`Para` carries only `lineX/lineY/lineSize` (`PdfToWord.java:142-144`, filled at `5344-5346`), and
`appendPara` uses only `int pad = column(lx, charW)` (`TxtWriter.java:342`) - there is no right edge
on the paragraph path at all. The right edge exists upstream: `Line.right` (`PdfToWord.java:3208`, set
at `3638` and `3906`) and `Box.right` (`:213`). One field mirrored onto `Para` plus a page-level band
pass reaches both paragraph-only documents.

The fixer's shipped paragraph construct needs no new field: it recovers the same information from the
page's own numeric line ends (see the second section of `t13-table-end-column-KEPT-115500-f1x.md`).

## What is left

Pooling the two emitters onto ONE per-page ruler is the remaining construct, measured at 15 of 18 by
this census. `balance-sheet-two-columns-of-figures` needs one pair merged that is two columns apart,
which no one-column window reaches.
