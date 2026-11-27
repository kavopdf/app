# Sixteen of sixteen documents measured on a4d8fca fail more Google checks than on 025fe9d

Measured 27 Nov 2026 by the gverify cron. The last sixteen documents without a Google result were
measured through Drive on the engine in the tree, `a4d8fca469bba636`. Every one of them came back with
more failing checks than its committed result, which was measured on `025fe9deda5ac7b1`.

Sixteen of sixteen is not a run of bad luck. It is the shape of a global change.

| document | committed (025fe9d) | measured (a4d8fca) |
|---|---:|---:|
| 324\_loan\_amortisation\_schedule | 2 | 3 |
| 412\_page\_labels\_roman | 0 | 2 |
| 416\_many\_tiny\_pages | 0 | 2 |
| 417\_rotate180\_and\_mirrored | 0 | 4 |
| 57\_centred\_title\_page\_left\_body\_pages | 0 | 3 |
| 58\_header\_rule\_footer\_rule | 0 | 4 |
| 602\_bookmarked\_annual\_report | 1 | 4 |
| academic-paper-ieee-2col-abstract | 7 | 8 |
| balance-sheet-and-profit-loss | 2 | 3 |
| bank-statement-5-pages | 1 | 5 |
| form16-part-b | 2 | 4 |
| gst-invoice-multipage-item-table | 2 | 5 |
| mutual-fund-statement | 4 | 6 |
| one-page-rotated-180-degrees | 5 | 7 |
| table-across-page-break-repeated-header | 1 | 4 |
| very-long-single-column-table | 2 | 5 |

## What the instrument says about the change

`18_displacement` is present on all sixteen, and it is the same fault each time: the whole page has
moved. On `412_page_labels_roman` the committed result read `med_dy 2.3` with no bad page; the new
result reads `med_dy -59.0` with pages 1, 2, 3 and 4 bad. A median shift of about -59 pt on every page
of a document is a page-geometry change, not a per-construct misplacement.

The other checks that appear on the newly measured set are `27_text_off_page` (sixteen documents),
`04_chars_missing`, `44_header_footer` and `60_text_column_right_edge`. Those are consistent with text
laid out against a page that is no longer where the source put it.

## Why these sixteen are not in the committed results

`regress.py --check` refused the commit - "16 document(s) fail MORE of Google's 42 checks than the
committed results ... There is no override" - and it is right to. Following the 23 Nov precedent
(`BALANCE-SHEET-74-GOOGLE-REGRESSION.md`), the sixteen committed results were left at their `025fe9d`
values so the LibreOffice half and the capability table of this run could land, and the refused
measurements are kept beside this file in `FINDINGS/gverify-refused-27nov/`, one JSON per document.

The committed Google column therefore still says what `025fe9d` did. It does not describe the engine in
the tree for these sixteen documents.

## What the fixer should do

Re-measure these sixteen on `a4d8fca` through both renderers before changing anything, then find the
construct the change between `025fe9d` and `a4d8fca` moved. If the change was intended to alter page
geometry, the sixteen are its cost and belong in the table; if it was not, it is a regression that
sixteen documents agree on.
