# 18_displacement: "make the cell content equal w:trHeight" is REFUTED corpus-wide

**27 Nov 2026, relay slot 03:13 IST.** Measured, then reverted. Nothing landed.

## The construct

A one-line table row is written with `w:trHeight` = the page's pitch and a cell content of
`w:before + w:line` = `LINE_BASE * (rowLineTw - box) + box`, i.e. about **0.8 of the pitch**: 32 to 77
twips short of the row's own declared height on a 160-385 twip pitch. A renderer that lays the ROW
(LibreOffice) honours `w:trHeight` and is unaffected; a renderer that lays the CELL collapses the row and
drifts upward row by row.

The 26 Nov probe (carried in `LAST-MESSAGE.md` of run 02:24, never committed as a finding) took
`362_price_list_dense` 41/42 -> 42/42 and `16_right_aligned_amounts_txtpos` 41/42 -> 42/42 in **Google**
by raising `w:before` to the row's height and changing nothing else.

## What I changed (DocxWriter.java, reverted)

Two hunks, 23 lines, no new numbers:

1. after `rowHeightTw` is final: `boolean oneLineRow = rowParts == 1 && rowTwHere > 0 && rowCapTw <= 0;`
2. immediately before the single-paragraph cell's `<w:p>` is emitted (the multi-paragraph path has
   already `continue`d):
   `if (oneLineRow && !cell.isEmpty() && vspan <= 1 && !vCont && cellSz > 0f) cellBeforeTw = Math.max(cellBeforeTw, rowHeightTw - cellBoxTw);`

Guards: a wrapped row (`rowParts > 1`), a vertically merged cell (`vspan > 1` / `vCont`), an empty cell and
the row cut at the paper's bottom (`rowCapTw > 0`) all keep the old pair.

## It fires where it should

On the rebuilt corpus, share of `(before + line)` pairs that now equal their row's `w:trHeight`:

| document | equal pairs |
|:--|--:|
| `362_price_list_dense` | 255 / 260 |
| `318_court_summons_form` | 12 / 12 |
| `36_embedded_subset_font` | 10 / 14 |
| `16_right_aligned_amounts_txtpos` | 15 / 65 |
| `402_calendar_month_grid` (the recorded breaker) | 10 / 47 - mostly excluded, as intended |

## It loses 91 documents to win 13, on the proxy

Full corpus rebuilt (213/213) and measured on the new engine, 204 of 212 scored before the slot ran out.
`median_pt`, published table vs the new one:

| | documents |
|:--|--:|
| better | 13 |
| worse | **91** |
| unchanged | 100 |
| corpus mean `median_pt` | 2.274 -> **2.641** |

Worst: `23_timetable_grid_txtpos` 0.96 -> 12.48 (+11.52), `404_sudoku_grid` 1.44 -> 7.68,
`402_calendar_month_grid` 0.96 -> 6.24, `electricity-bill` 0.96 -> 5.76, `form16-part-b` 0.96 -> 5.28.
Best: `newsletter-3col-header-footer` 72.48 -> 0.96, `text-held-twice-shadow-text` 29.28 -> 12.00,
`07_stamp_over_table` 12.96 -> 2.88, `326_itr_computation` 10.56 -> 2.88.

The pattern is the collision itself: every document that got worse is a ruled table whose rows the page
drew at the pitch, and every document that got better is one whose rows were already collapsing. The
change moves the baseline **0.2 of the pitch down inside the row** for all of them, and only the collapsing
ones needed it.

## What this settles, and what it does not

- It settles that the rule **cannot be landed on the LibreOffice table**, which is the table the gate reads.
  This is the third form of this construct to be measured and refused: `w:before = rowLineTw - box`
  (recorded in the code at `DocxWriter.java:6867` as `18_median_dy` 64 -> 100), shortening `w:trHeight`
  instead (recorded at `:6467`, `electricity-bill` 18.0/19.0 -> 17.5/18.5), and this one.
- It does **not** settle whether Google gains. The only Google evidence is 2 documents, from a run whose
  probe files are gone. A rule that trades 91 proxy documents for 2 Google documents is not a trade anyone
  can defend without a Google measurement of the same 91, and that measurement is the missing instrument,
  not the missing patch.

## The patch, for whoever measures Google next

`git apply` this against `DocxWriter.java` (41-line diff, saved beside this finding as
`18-displacement-ROWH-CONTENT-EQUAL-TRHEIGHT-27NOV.patch`), rebuild with `pod-prep.sh`, then measure
**Google** on the 91 documents listed by comparing `benchmarks/RANKING.csv` with the run's
`RANKING.partial.csv`. Do not land it on the LibreOffice column: it reads worse by construction there and
that is not evidence about Google.
