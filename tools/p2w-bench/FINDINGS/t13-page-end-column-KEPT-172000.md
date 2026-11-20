# t13_amount_columns: the end column is the PAGE's, not the table's - KEPT

20 Nov, fixer slot 15:55. Engine `TxtWriter.java` only; scope.py agrees the change cannot reach a
.docx byte. Whole corpus re-converted and re-scored with the new engine: **213 of 213**.

## What it measured

    5 documents no longer fail t13_amount_columns
    0 documents newly failing, on any check
    208 documents unchanged

| document | before | after |
|:--|:--|:--|
| `22_invoice_four_columns_txtpos` | `t13_amount_columns` | clean |
| `29_dot_leaders_txtpos` | `t13_amount_columns` | clean |
| `balance-sheet-two-columns-of-figures` | `t13_amount_columns` | clean |
| `74_balance_sheet_indented_subitems` | `t02_position`, `t13_amount_columns` | `t02_position` |
| `gst-invoice-multipage-item-table` | `t09_page_furniture`, `t13_amount_columns` | `t09_page_furniture` |
| `itr-computation-with-slab-table` | `t08_line_order`, `t13_amount_columns` | `t08_line_order`, `t13_amount_columns` |

The last one did not move. It is the one case the construct cannot reach, and the reason is below.

## The construct

`appendTable` measured its amount end column **inside the call**, from that one `PdfToWord.Table`:
`endCol[ci] = max(baseCol + len, column(cellRight))` over its own numeric cells. `paraEndSnap`
measured the same thing **per page**, from numeric paragraph lines. The two estimators never
consulted each other, and two tables on one page never consulted each other either.

t13 asks one thing: do the rows of one source amount column end at one .txt column. It does not
compare the .txt's absolute offset with the source's, so a constant shift is harmless. A column
covered by two tables therefore fails on the rows of whichever table measured it second-best.

The change hoists the table end column to one set **per page column of the cell's right edge**,
pooled over every table in the document (`tableEndSnap`), and marks those pooled targets in
`paraEndSnap` so the paragraph path and the table path agree on a page that uses both.

Two properties make it safe, and both are structural rather than measured:

* the key is the page column of the cell's **right edge**, so cells of different lengths in one page
  column are one column by construction, not by a length heuristic;
* the target is a max over a set that includes the cell's own `baseCol + len`, so a numeric cell can
  only ever move **right**. No line moves left, so nothing that passes today can lose its column.

Keys one column apart merge transitively, as `paraEndSnap` already did. That is what carries
`gst-invoice-multipage-item-table` across its page break, where page 4's grand total lifts the edge
to one column and pages 1-3 sit on the next.

## What it proved about the six

`22_invoice_four_columns_txtpos`: block 7 ended every figure at 102, block 8 at 103, same right edge
539.276 pt (`column(cellRight)` = 100). One table's longest figure was 9 characters at baseCol 93,
the other's 11 at baseCol 92. 4 of 16 rows were one column away from the other 12.

`29_dot_leaders_txtpos`: 11 dot-leader paragraphs landed on 91, the 5-row totals table on 92. The
paragraph path was right; the table path had no way to see it.

`74_balance_sheet_indented_subitems`: 88/108 against 87/107, same page columns.

`balance-sheet-two-columns-of-figures`: 54/63/108/117 against 52/62/107/116. The 10-character token
that lifted one table's column is the header date `31.03.2026`, which `isNumeric` accepts. Pooling
makes both tables agree without having to decide whether a date is an amount - the date is a
pre-existing quirk of `isNumeric`, and it is not what this fix needed.

## The one it did not fix, and why

`itr-computation-with-slab-table`, measured after the change and left open. The verifier's own ruler
for this document is 4.1616 pt per character and it groups the source's line-final amounts by end
column into 93 (6 rows), 107 (7), 129 (1), 130 (7) and 131 (4). Four of those are columns. The
failing one is 130, and its seven rows arrive in the .txt as 1 at column 130 and 6 at column 132:

    source x   token           .txt end
     503.6     61,000.00            130
     496.5     3,68,680.00          132
     502.7     14,747.20            132
     496.5     3,83,427.20          132
     496.5     3,60,000.00          132
     502.7     10,000.00            132
     502.7     13,427.20            132

`61,000.00` is in a different `PdfToWord.Table` from the other six. Those two tables report cell right
edges of 535.58 pt and 549.92 pt - 14.34 pt apart, which is 3.4 columns on this document's ruler, and
`column()` puts them on 129 and 132. Pooling keys three columns apart are three columns apart, and
joining them would be inventing a column the page did not draw. The source's figures all end within
one column of each other, so the fault is that one table's cell right edge is 14 pt left of where the
page draws the figures - **table geometry in `PdfToWord`, not padding in `TxtWriter`**. `PdfToWord`
owns the .docx as well, so that change needs a .docx measurement and is not a .txt-slot change. That
is where the next run on this class should start, and it should start by measuring which of the two
`cellRight` values is the wrong one.

## How it was measured, so it can be re-derived

    bash tools/p2w-bench/build-engine.sh
    # convert all 213 from the corpus release zips, one document per JVM (ConvertOne)
    python3 tools/p2w-bench/restamp_txt.py --run --budget 260
    python3 tools/p2w-bench/restamp_txt.py --report

`--report` compares the fresh scores against `RANKING-TXT.csv` as it stood before the change.
`--apply` was deliberately **not** used: it rewrites `RANKING-TXT-BASELINE.csv` from the same
results, which makes the gate compare the store against itself. The baseline is the reference and it
was left untouched, so `regress.py --check` compared 213 fresh scores against a table this run never
wrote - and reported no document worse than baseline.
