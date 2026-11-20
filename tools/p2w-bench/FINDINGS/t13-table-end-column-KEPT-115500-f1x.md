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

---

# Second attempt, same slot: the paragraph path, and what it is worth

`t13` after the table fix holds 8 documents. Two of them (bank-statement-horizontal-rules-only,
gst-invoice-horizontal-rules-only) emit their amounts from the PARAGRAPH path, which has no right
edge at all: `Para` carries `lineX/lineY/lineSize` and `appendPara` writes `column(lineX)` and
nothing else. So a numeric paragraph line ends at `column(lineX) + length`, and the ruler's rounding
splits a page column across two adjacent `.txt` columns. Measured, in the .txt:

    29_dot_leaders_txtpos            91 x11, 92 x5
    74_balance_sheet_indented_subitems  87 x6, 88 x6, 107 x6, 108 x6
    balance-sheet-two-columns-of-figures 52 x9, 54 x2, 62 x9, 63 x2, 107 x10, 108 x3, 116 x10, 117 x3
    gst-invoice-horizontal-rules-only  94 x5, 95 x1, 109 x3, 110 x4, 131 x3, 132 x4
    bank-statement-horizontal-rules-only 142 x14, 143 x14

Every remaining failure is an off-by-one split, not a layout error.

## The change

`paraEndSnap()` builds, per page, a map from an end column to the column it should be padded to: an
end column whose immediate neighbour is also an end column (of the page's own numeric paragraph
lines) merges into it, transitively, and the component keeps its highest value. `appendPara` applies
it to a numeric line after computing its pad. It only ever pads - a line never moves left - and it
cannot change a line count.

## The measurement, and how it was bounded honestly

Whole corpus, compared with the table fix alone:

    better 2   worse 0   same 211        checks passed 1794 -> 1796
    bank-statement-horizontal-rules-only 9 -> 10   gst-invoice-horizontal-rules-only 9 -> 10

Only documents whose .txt CAN change were re-converted, and that is a proof, not a shortcut: the snap
is the identity map unless the page already has two numeric paragraph lines whose end columns differ
by exactly one. Scanning all 213 `.txt` files for any pair of amount end columns one apart - a superset
of the paragraph-only condition, since it also counts table cells - found **10 documents**. Those ten
were re-converted and all 213 were re-scored. A document with no adjacent pair cannot have a paragraph
adjacency either, so its snap is the identity and its bytes cannot move.

## What is left, measured

6 of the original 18 still fail `t13_amount_columns`, and none of them is a one-column split:

* `balance-sheet-two-columns-of-figures` needs one pair merged that is TWO columns apart (52 and 54).
  Widening the window to two is a layout claim the measurement does not support; left alone.
* `74_balance_sheet_indented_subitems`, `29_dot_leaders_txtpos`, `gst-invoice-multipage-item-table`
  and `itr-computation-with-slab-table` fail because the table path and the paragraph path are
  measured separately: the table cells converge on their own end column, the paragraph lines converge
  on theirs, and the two maxima differ. Pooling them per page - the census agent measured that
  variant at 15 of 18 - is the next construct, and it is a change to how the two emitters share one
  ruler, not another special case.
* `22_invoice_four_columns_txtpos` fails one column of two.

Total for the slot: `t13_amount_columns` 18 documents -> 6, clean documents 167 -> 179, corpus checks
1784 -> 1796, 0 documents worse at any point.
