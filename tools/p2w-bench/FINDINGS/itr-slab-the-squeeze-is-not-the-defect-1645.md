# itr-computation-with-slab-table (50.80) — the squeeze is NOT the residual, measured twice

Run starting 15:58 IST, 18 Nov. The handoff said: implement the anchor rule in `DocxWriter`'s
zero-gap branch so the running footer (drawn at 811.4 inside table 3's band) is anchored at its own
y, and the page's f=0.974 squeeze — the thing that drifts every row -0.45 pt — goes away.

Both halves of that were tested. Neither is true, and the numbers below are why.

## 1. The anchor rule has nothing to anchor on this document

`-Dp2w.traceLines` over the converted document shows 18 line records and NOT ONE of them is the
footer:

    flowRow  y=53.35   R. SUBRAMANIAN & CO.
    flowRow  y=63.35   Chartered Accountants · ICAI Reg. no. 004412S
    table    top=85.35
    flowFromBox y=154.35  Table 1. Slab rates applicable for AY 2027-28
    table    top=160.0
    flowFromBox y=305.15  Table 2. Computation of total income
    table    top=311.0
    flowFromBox y=695.15  Table 3. Computation of tax liability
    table    top=701.0

`zeroGap=0 zeroGapWorst=0.0 zeroGapAnchored=0`. The footer is a **row of table 3**, not a flow
paragraph after it — `word/document.xml` carries it as a `w:tc` paragraph ("Computation prepared on
12 August 2026 · AY 2027-28") inside a `w:tr`. So `afterTablePt` never sees it, the zero-gap branch
never runs on it, and the anchor rule — implemented or not — cannot move it.

A version of the anchor rule WAS written into the `afterTablePt` branch (a negative `edgeGap` treated
as a position, `anchorBox` + `anchorKeepsFlow`) and reverted uncommitted: it is dead code on this
document, and committing a behaviour change that fires on no measured document is exactly what the
patches directory is full of.

## 2. Removing the squeeze makes the document WORSE

The overrun is real and it is in the table's charge:

    TBLDBG table 3  keep=9/11  writtenRowsTw=2908  flowTwBefore=14290  top=701.0  paper=841.89
    FLOW   needTw=17278  budgetTw=16836  writtenTw=16595  f=0.974

The band is 140.9 pt (701.0 -> 841.9); the charge is 145.4 pt plus a flow that had already run 13.5 pt
ahead of the table's top, which is the 22 pt of overrun. So the obvious next move is to stop charging
a clipped table past the paper — hold the ledger at the budget once `keepRows < rows`:

    needTw 17278 -> 16836, f 0.974 -> 0.994
    SCREEN: itr-computation-with-slab-table  50.80 -> 70.85   (+20.05 WORSE)

LESS squeeze scored worse, by 20 points. Whatever the residual is, it is not the compression: the
squeeze is compensating for a page whose content really is taller than the sheet, and releasing it
lets the bottom of table 3 fall off the paper. Reverted; engine back to `1ba86d7`, re-screened at
50.80 (1 same).

## 3. What the page actually looks like (rendered, line by line)

Source y vs ours, at f=0.994 (the unsqueezed page):

    src     ours   line
     44.8   38.8   R. SUBRAMANIAN & CO.
     58.1   40.0   Chartered Accountants ...        <- ours puts "COMPUTATION OF TOTAL INCOME"
     46.0   48.7   COMPUTATION OF TOTAL INCOME      <- (src 46.0) ABOVE it: the two are SWAPPED
    165.2  160.0   Slab / Total income range / ...  (every cell of table 1: -5.2)
    316.0  310.7   Particulars (table 2: -5.3, growing to -7.2 by the foot)
    706.0  699.4   Particulars (table 3: -6.6)
    811.4  804.5   Computation prepared on ...      <- the footer ROW, out of order:
    816.4  812.0   Less: advance tax paid             the page draws it at 811.4 AFTER
    834.8  827.5   Balance tax payable                the 816.4/834.8 rows

Three separate defects, none of them the squeeze:

1. **Header order.** The engine emits "COMPUTATION OF TOTAL INCOME" before "Chartered Accountants",
   where the page draws it above at y=46.0 and the firm line at 58.1 — a reading-order inversion in
   the first three lines of the page.
2. **Cell text sits ~5.2 pt high in every table row.** The cells fall to the fallback
   `cellBeforeTw = LINE_BASE * (rowLineTw - cellBoxTw)` with `rowLineTw` = 190 twips for a row whose
   pitch is 368 twips (18.4 pt), so the baseline lands 7.6 pt into the row where the page draws it
   12.6 pt in. `rowLineTw` is the cell's LINE, capped by `naturalLineHere` at 200 twips; the fallback
   assumes it equals the row's pitch, which is true only for short rows. This is the largest single
   term (it is a flat -5.2 across 100+ cells) and it is a change that touches EVERY table on the
   corpus — it needs a corpus pass, not a screen.
3. **The footer row is emitted in the middle of the last rows**, so the last two rows of table 3 come
   out below it in the flow while the page draws the footer last (at 811.4, inside the band).

## What to do next on this document

Not the anchor rule. Start with (2): `cellBeforeTw`'s fallback using the row's own pitch where the
cell's line is much shorter than the row, measured on the table documents that already score well
before any corpus pass. Then (1), which is a reading-order question in `PdfToWord`'s paragraph order,
not a placement one.
