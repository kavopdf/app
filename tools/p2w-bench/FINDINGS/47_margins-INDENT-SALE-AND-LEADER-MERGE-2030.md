# 47_margins on 360_restaurant_menu: the indent is sold to buy a line, and the page's own ink does not fit its own column

Written 20 Nov 2026, 20:30 IST, by the fixer run that took `47_margins` on the rotation (attempts 9
and 10 on the class). Two constructs were built and measured end to end. Neither is kept. Read this
before spending a run on the 12 pt on `360_restaurant_menu` - it is the only document in the class
with a real column-position error, and it cannot be fixed by a writer change.

## The mechanism, traced

`360_restaurant_menu`'s menu body is a **table**, not a flow block. `-Dp2w.traceLines` shows the whole
body going through writer `table` twice (top 120.0 and 419.99); only the masthead, subtitle and footer
go through `flowFromBox`.

    1. PdfToWord.java:9469    t.cellX.add(textXs) - each cell's INK x (visibleX(cell.glyphs, cell.x)).
                              The menu names are at x=52; the column's own edge is x=40.
    2. DocxWriter.java:6307   insetTw(t, r, c, x0, edgeTw[c]) -> w:ind w:left = 240 twips = 12 pt.
    3. DocxWriter.java:6362-6366  THE SALE:
                              int needTw = ceil(textR) + 20;
                              boolean textOverflows = insetTw + needTw > spanTw;
                              if (textOverflows) insetTw = Math.max(0, spanTw - needTw);

`spanTw` is 1437 twips (71.85 pt). Menu names run 60-92 pt, so five of them overran the column and
paid for their line with the inset: `Chicken Malai Kebab` and `Mushroom Galouti` gave up all 240 twips
and were set at x=40, `Prawn Koliwada` 225 of them. The page's anchor - the leftmost rounded left edge
shared by at least max(3, 5%) of the page's lines - then read **40 against the source's 52**, and
`47_margins` clause (a) failed on a page whose `w:pgMar` is 0 on all four sides.

**The sale is not vandalism and it is not dead code.** Its own comment records why it exists:
`gst-invoice-with-qr-code`'s Rate column is 840 twips with a 551 twip inset, leaving 289 twips for a
286-twip "Rate" - the page's face fits it, the render's does not, and the word broke as "Rat" over "e".
Delete the sale and that document breaks. Do not "just remove line 6366".

## Construct A - remove the sale

Measured on the fresh pair (source PDF against the soffice render, `verify_google.py`):

| | 47_margins | page anchor | unregistered runs | doc checks | share@5px |
|:--|:--|:--|--:|:--|--:|
| HEAD | FAIL | 52 -> 40 | 9, worst 11.9 pt | 37/42 | 34.43 |
| A: sale removed | **PASS** | 52 -> 52 | **0** | **38/42** | 41.04 (+6.61) |
| A': sale kept only where `needTw <= spanTw` | FAIL | 52 -> 43.0 / 40.9 / 50.1 | 8 | 37/42 | 47.78 (+13.35) |

A flips the check to PASS and takes the document 37/42 -> 38/42, and still loses on the pixel score:
the 13 lines the sale was buying now wrap, at the right x. A' is worse on both.

## Construct B - widen the cell over its leader-dot column

The widening loop in `tableBody` (the `while (c + span < cols && cellAt(...).isEmpty())` at :6344) has
always been able to take room from the cells beside a cell - but only from cells that are **EMPTY**. The
cell to the right of a menu name holds leader dots. It is not empty, so the loop declined, and the writer
fell through to the sale. A new `isLeaderOnly()` (dots, bullets, ellipsis, spaces only) plus a
fit guard lets the cell widen over it, appending the dots into the merged cell so no character is lost
and no column index moves.

It fires: the name cell becomes `gridSpan=2`, `tcW` 4588 twips, `w:ind` 240 - **x pinned at 52, no wrap**.
And it is the best single-document pixel move this class has had: **share@5px 34.43 -> 26.25 (-8.18)**.

It is still a regression, and the checks say why:

    47_margins        9 -> 14 unregistered   the dots' own xink moves 112 pt -> 144 pt (+32 pt);
                                             pinning the name DISPLACES the leader
    13_text_colours   newly fails            the dots are #666666, a merged cell carries one
                                             colour, grey share -33 %
    43_within_10pt_x  newly fails            2 spans moved together by -35.1 pt
    26_text_overlap   6 -> 6                 unchanged
    doc checks        37/42 -> 36/42

## The reason both constructs lose, which is the thing worth keeping

**The page's own ink does not fit its own column.** The name is drawn at x=52 and runs to 144 pt; its
column ends at 111.85 pt. The dots are drawn starting at 112 pt - *inside the name's column* - and run
to about 269 pt. Three positions, one column budget:

* pin the name at 52 and the dots move +32 pt (construct B),
* keep the dots and the name must wrap or give up its indent (construct A).

There is no third option that keeps the page's own grid, because the page did not lay this out on that
grid: it let the text overflow the column and drew the leaders over the overflow. Any writer construct
that respects the grid has to displace one of the three, and `47_margins` measures the displacement of
whichever one it is.

So the class is **not reachable on `360_restaurant_menu` by a writer change**. What would reach it is a
grid that is derived from the ink rather than from the drawing's rectangle - column 0 would be ~92 pt
and the leaders would start at 132 - and that is a table-grid change across every table in the corpus,
not one construct, and it is not provable on one document.

## What the next run should do with the class

* Do **not** rebuild A, A' or B. All three are measured above.
* The class holds 14 documents in the LibreOffice table and 26 in the Google table. `392_statistical_console_output`
  already reads 0.06 and passes 42 of 42 on this engine (see `47_margins-STALE-TABLES-152500.md`), so the
  reachable population is smaller than either table says. Re-measure before believing a count.
* The `.txt` half of the class has not been touched by any of the three attempts. That is the only
  untried direction left on it.
