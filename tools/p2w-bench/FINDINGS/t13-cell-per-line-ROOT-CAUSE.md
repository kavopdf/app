# t13_amount_columns: the .txt puts one table CELL on a line, not one table ROW

Found 19 Nov by the agent, offline, with no `java` and no engine build. Every number below
was read from the files in `/scratch/work/p2w/` and from `verify_txt.py` itself.

This is the largest single lever in the .txt: `t13_amount_columns` holds **30 of 64 failing
documents, and 24 of those fail on nothing else.**

---

## What the .txt does

`gst-invoice-3line-items` is a three-item GST invoice with nine table columns. The .txt emits
**one line per cell**, each cell starting further right than the last:

```
          #
               Description of goods
                                                  HSN
                                                              Qty
                                                                   Unit
                                                                               Rate
                                                                                      Taxable value
                                                                                                    CGST 9%
                                                                                                               SGST 9%
                                                                                                                                Total
          1
               MS Hex Bolt M10 x 60mm, zinc plated
                                                  7318
                                                            1,500
                                                                   Nos
                                                                              18.50
                                                                                          27,750.00
                                                                                                     2,497.50
                                                                                                                2,497.50
                                                                                                                             32,745.00
```

The page draws `1 | MS Hex Bolt M10 x 60mm, zinc plated | 7318 | 1,500 | Nos | 18.50 |
27,750.00 | 2,497.50 | 2,497.50 | 32,745.00` as **one row**. The .txt splits it into ten lines.

**This is not the agreed format.** Option A is "layout-preserving text, rows on one line,
columns aligned by spaces". A table row is one line; here it is ten.

## Why that fails t13

t13 asks one thing: do the amounts of a right-aligned column all **end at the same character
column** in the .txt? When each cell sits on its own line, an amount's end position is just
its own length, so `7,522.50` ends at 133 and `13,806.00` ends at 134 — same column on the
page, different column in the .txt. The check is right to fail it.

Measured, on this document:

```
source columns (end_col -> the amounts that end there)
  col  83 : 18.50  4.25  7.80  285.00  214.50
  col  99 : 27,750.00  11,700.00  1,42,500.00  1,07,250.00  2,95,575.00
  col 109 : 2,497.50  573.75  1,053.00  12,825.00  9,652.50  26,601.75
  col 120 : 2,497.50  1,053.00  12,825.00  9,652.50  26,601.75
  col 133 : 32,745.00  7,522.50  13,806.00          <- the one that fails
  col 134 : 1,68,150.00  1,26,555.00  3,48,778.50

where those tokens ended in the .txt
  7,522.50   -> [133]
  13,806.00  -> [134]
  32,745.00  -> [134]
```

Column 133 needs all three to end at one place; they end at 134, 133, 134.

## The fix is in the writer, not in the check

`TxtWriter.write()` must emit a table row as **one line**, with each cell placed at the
character column its x-coordinate implies, padded with spaces. That is what t02 already
measures for body text and what a reader needs in order to compare `9.50` with `1,240.00`.

Do not "fix" this by loosening t13. The amounts genuinely do not line up.

---

## A second defect, in the check, found while proving the first

`compare()` keys the .txt's amounts by **token** and keeps only the first end position:

```python
txt_ends.setdefault(ln[span[0]:span[1]], []).append(span[1])
...
got = txt_ends.get(tok)
ends.append(got[0])          # <-- always the FIRST occurrence
```

On an invoice, the CGST column and the SGST column often hold **the same values**. Here
`2,497.50`, `1,053.00`, `12,825.00`, `9,652.50` and `26,601.75` each occur twice, ending at
109 and at 120. Both source columns look up the same list and both take `got[0]`, so the SGST
column is judged against the CGST position and passes for the wrong reason.

**This makes t13 pass columns it should fail.** Fixing it will make more documents fail, not
fewer — which is the honest direction, but it must be done deliberately and the scores
re-baselined, not slipped in.

The correct key is the occurrence, matched in reading order, not the token text.

---

## What to do first

1. Fix `TxtWriter.write()` so a table row is one line with space-aligned columns. Re-measure
   the .txt. Expect `t13` to drop sharply — possibly to near zero — because the amounts will
   finally share an end column.
2. **Only then** fix the `got[0]` defect in `verify_txt.py`, and re-baseline
   `RANKING-TXT-BASELINE.csv` in the same commit, saying so.
3. Re-run `classify_txt.py` and `step_txt.py`.

Doing (2) before (1) would mix a writer fix with a measurement fix and make it impossible to
tell which one moved the number.
