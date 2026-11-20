# t13_amount_columns: one end column per table column — 10 documents, 0 worse, KEPT

20 Nov 2026, fixer slot 10:51. Measured on the whole 213-document corpus through the real engine.

## The defect, proven

`TxtWriter.appendTable()` emitted one cell per line and tried to right-align a numeric cell to
**its own cell's right edge**:

    int startCol = column(right, charW) - c.length();
    if (startCol > col) col = startCol;          // TxtWriter.java:375, the line that loses it

`charW` is one ruler for the whole document (0.6 x the weighted-median font size). On a 7 pt amount
column that ruler over-estimates a numeric token's width by about one column: the cell is 7 ruler
columns wide while its content is 8 or 9 characters. `startCol` therefore lands 1-2 columns LEFT of
the cell's own left edge, the guard discards it, and the cell falls back to `baseCol`. The amount then
ends at `baseCol + length` — 134 for a 9-character figure, 133 for an 8-character one. Same page
column, two `.txt` columns. Measured on `gst-invoice-3line-items`:

    DBG TABLE r=1 c=9 baseCol=125 right=552.5905 col=125 num=true  32,745.00   -> ends 134
    DBG TABLE r=2 c=9 baseCol=125 right=552.5905 col=125 num=true   7,522.50   -> ends 133
    DBG TABLE r=3 c=9 baseCol=125 right=552.5905 col=125 num=true  13,806.00   -> ends 134

`cellR` is not NaN and does not differ per row. The clamp is the mechanism; the other candidates are
falsified in `t13-writer-path-110501-f3de.md`.

## The change

Measure the column once — the furthest right any numeric cell in it already reaches, `max(baseCol +
length, column(right))` — and end every numeric cell in that column there. The target is never less
than a cell's own `baseCol + length`, so `startCol >= baseCol` always and the guard can no longer
discard it. Nothing moves left, and the number of lines does not change: only the padding in front of
a figure moves, so `t04_structure`'s line count cannot drift. That is the difference between this and
`PATCH-t13-table-row-per-line.patch`, which was rejected for changing `len(lines)` by a factor of nine.

## The measurement

Whole corpus, one JVM per document, `ConvertOne` from the built tree, `verify_txt.compare()` on every
document, compared against the committed `RANKING-TXT.csv`:

    better 10   worse 0   same 203        checks passed 1784 -> 1794

The ten, all of which stop failing `t13_amount_columns` and become fully clean:

    01_stamp_rotated_15deg_upright      10_stamp_as_image
    362_price_list_dense                72_bank_statement_no_rules_right_amounts
    balance-sheet-and-profit-loss       electricity-bill
    form16-part-b                       gst-invoice-3line-items
    payslip-label-left-amount-right     purchase-order

`restamp_txt.py --report`: 10 documents newly clean, 0 newly failing, 203 unchanged.
Clean documents 167 -> 177 of 213.

## What it does not reach

8 of the 18 still fail `t13_amount_columns`: 22_invoice_four_columns_txtpos, 29_dot_leaders_txtpos,
74_balance_sheet_indented_subitems, balance-sheet-two-columns-of-figures,
bank-statement-horizontal-rules-only, gst-invoice-horizontal-rules-only,
gst-invoice-multipage-item-table, itr-computation-with-slab-table.

Measured path census (`t13-path-census` agent, all 18, engine built, temporary stderr print):
14 table-only, 2 paragraph-only (the two `*-horizontal-rules-only` bank/gst documents), 2 mixed in
one column (29_dot_leaders, 74_balance_sheet_indented_subitems). So the remaining 8 are not one
construct: the paragraph path has no right edge at all (`Para` carries `lineX/lineY/lineSize` only,
`appendPara` uses `column(lx, charW)` and nothing else), while the right edge does exist upstream as
`Line.right` (`PdfToWord.java:3208`) and `Box.right`. A paragraph rule needs a new field on `Para`
plus a page-level band pass, and the same agent measured that variant at 13 of 18 passing (with a
naive rule) and 15 of 18 (with page-level bands pooling Para and Table right edges). That is the next
run's construct, not this one's.

## The gate could not have landed this, and that is fixed here

`scope.py` fell back to "both" for any method it did not know, and `regress.py` then demanded a
re-stamped docx table — while `engine_fingerprint()` hashes every `.java` in the engine, so a
`TxtWriter` edit moves the hash the docx table was stamped with. A `.txt`-only change could therefore
never pass the gate at all. Two edits:

* `scope.py`: `TxtWriter.appendTable` and `TxtWriter.appendPara` are `txt`. Both are private static in
  `TxtWriter` and are called only from `TxtWriter.write()`, which no `.docx` path invokes.
* `regress.py`: a format that `scope.py` has proved out of scope is not stamp-checked. A change
  `scope.py` cannot attribute still leaves the scope empty and stays strict on both stamps, and
  `docx_regressions()` still runs unconditionally.

That is the mechanical reason 46 documents failed the same `.txt` checks for a month: not that nobody
tried, but that nothing a `.txt` run produced could be committed.
