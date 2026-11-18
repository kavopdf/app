# content-partly-lost-and-displaced — itr-computation-with-slab-table: the page was squeezed for ink nobody can see

Measured 18 Nov, fixer run starting 13:50. The class was 7 documents; six of them were already
under 5.0 share@5 (1.73, 2.29, 2.62, 3.46, 3.89, 4.93) and only this one was badly broken at 68.82.

## What the numbers said

    share5 68.82   median 9.60   p90 36.96   max 133.92   invent5 65.2   text_recall 100.0

Every character was present. 65 % of our ink was invented and 69 % of the page's ink was more than
5 px from ours, with a median displacement of 9.6 pt - the shape of a whole-page offset, not of a
lost element. Comparing the two PDFs line by line: our first line sat at y=11.2 where the page drew
it at 44.8. A constant 33.6 pt lift, growing to 48.9 pt at the foot of the sheet.

## The cause, in three steps

1. **The PDF draws its last table past the bottom of its own sheet.** Its horizontal rules run
   701.2 ... 830.0, 848.4, 866.8, 885.2 on an 841.9 pt page. Every viewer clips the last three; the
   engine reproduced them as rows.
2. **So the model of the page was taller than the paper.** `need=18160 twips` (908 pt) against
   `budget=16836` (841.8 pt). The engine's fitter answers an overrun with a global squeeze:
   `f = min(1, budget/need)`, floored at 0.85, and every gap and every row on the sheet is written
   through it.
3. **The squeeze came off the top of the page first.** The first paragraph's `w:before` went
   1057 twips to 392 (52.85 pt -> 19.6 pt), and `fitPage` then clamped every other gap it could
   reach. That is the 33.6 pt lift, and it is why a document with a perfect text recall scores 68.82.

Confirmed by instrumenting the squeeze branch: the same document printed `need=18160 written=17782
budget=16836` and three attempts at f=0.927/0.900/0.875, none of which fit, the shortest of which
was still adopted.

## The fix (in this run's commit)

`DocxWriter.table()` now computes `keepRows`: rows whose top edge is below `ctx.pageHeightPt` are not
emitted, and the row that straddles the edge is cut at it (`rowCapTw`, applied to the row height and
to the cell's own `w:line`, because the renderer lays a row out at `max(trHeight, content + rule)`).

    share5 68.82 -> 50.80    median 9.60 -> 4.80    p90 36.96 -> 16.32
    class screen: 7 measured, 1 better, 6 same, 0 worse
    corpus ratchet: 210 compared, 1 better, 0 worse, 209 unchanged

Blast radius, measured rather than argued: a `-Dp2w.clipDbg` census over all 213 conversions shows
the branch fires on exactly this one document (rows 11 -> 9), and `word/document.xml` is byte-identical
between the old and the new engine on an 11-document sample (10 SAME, 1 DIFF = this document).
Note: comparing the `.docx` FILES is useless — zip timestamps differ on every run and all 11 read DIFF.

## What is left on this document (50.80, not 0)

The remaining 22 pt of overrun is the running footer. The page draws "Computation prepared on 12
August 2026 · AY 2027-28" at y=811.4, INSIDE table 3's band (701 -> 885); the flow can only place it
after the table's clipped bottom at 841. So the page still squeezes at f=0.974 and every row drifts
-0.45 pt, accumulating to -13 pt by the foot of the sheet.

The fix is already described in the code and not implemented: the zero-gap branch in
`DocxWriter` (~line 4235) counts a line the page drew ABOVE the flow's current position, and its
comment says such a line "is anchored at its own y and the running position is re-synced to it" —
but the code only counts it and writes `before=0`. Implementing the anchor is the next step, and it
should take this document well under 20.

## A second thing this class cannot do

Six of its seven documents are already under 5.0 share@5 and stay in the class only through `max_pt`.
`attempt.py` keeps an attempt at `moved >= max(2, 25 % of the class)`, so no single mechanism can
keep an attempt on this class, and `classrow.py` cannot mark a document FIXED whose baseline was
already below 5.0. The class is a decision for a human (BLOCKERS.md, 14:50), not a fix.
