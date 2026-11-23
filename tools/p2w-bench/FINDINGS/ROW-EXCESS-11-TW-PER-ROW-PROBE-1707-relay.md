# The row-excess constant in the spacer guard: 15 tw/row -> 11 tw/row

**Prediction written BEFORE the probe ran, 23 Nov 17:07 IST, engine HEAD 570f5123.**

`DocxWriter.java:6051` charges a page `rowExcessTw = 15 * pageRowCount` of the room it needs
before it may split the table gap into `w:before` (which Google honours 1:1) plus a one-twip
hairline in `w:line` (which Google delivers at ~0.155 pt). At 15 tw/row the guard refuses
`72_bank_statement_no_rules_right_amounts`, whose numbers are:

    spacerTw 366 (18.3 pt)   rows 18   roomWant 346   rowExcess 270   need 616   slack 558

At 11 tw/row the row term is 198, need 544, and 544 <= 558 makes the page spendable.

**Before, measured in Google this run (not remembered):** 72_bank = 41/42, failing only
`18_displacement` (source=0 render=1). The displaced runs are the table body, lifted as a block:
`Opening balance` dy -14.99, `03-04-2025` -14.99, the last amount `10,53,042.55` dy -28.24
(one row pitch below that). So the table starts ~15 pt high — exactly the 18.3 pt gap the guard
is refusing to spend, less the ~3.3 pt the hairline construct delivers.

**Prediction if 11 tw/row is right:** 72_bank -> 42/42 in Google, the table body moving down
~15 pt, one page, no lost characters.

**Prediction if it is wrong:** either 72_bank stays 41/42 (the guard still refuses, or the gap is
spent and the displacement is unchanged), or the page overflows to 2 pages because 11 tw/row
under-charges the row excess Google really lays.

**The control that must not move:** `mobile-bill` and `insurance-policy-schedule` are the two
documents the guard was written for — spending a gap unguarded took them from 46/47 on one page
to 43/47 on two (22 Nov 23:10). At 11 tw/row their row term falls by 4 tw/row, so they may enter
the spendable set too. If either loses a page, 11 is falsified regardless of 72_bank.

## RESULT — REFUTED. Measured in Google, 23 Nov 17:10, one upload each side.

**Before (HEAD 570f5123):** 72_bank = 41/42, `18_displacement` source=0 render=1. The table body
sat 14.7-15.0 pt high; worst run `10,53,042.55` dy -28.24 (ratio 9.38), `Opening balance` -14.99.

**After (rowExcess 11 tw/row):** 72_bank = 41/42, `18_displacement` source=0 render=1. **The guard
did open** — the docx now carries `w:before="365" w:line="1"` where it carried `w:line="366"`, so the
gap is spent the way the code intends. The -15 pt lift is gone: the table body is now within
tolerance (dy +3.23, ratio 1.07). But the page now sits ~4.85 pt LOW as a block — `Page 1` and the
bank's header line, which the table's spacer cannot move, are +4.85, the title +4.66 — and 7 of 80
runs are over tolerance against a budget of `max(2, 5% of 80 = 4)`. Same check, same verdict.

**What this measures that was not known.** The split spends the gap the page needs *plus about
4.5 pt*. Before the split Google delivered ~3.3 pt of the declared 18.3 pt; after it delivers 18.4
and the document lands 4.85 pt low. So the gap the page needs is about **13.5 pt, not the 18.3 pt
`extraAbs` computes** — the spacer is over-measured by roughly 4.5 pt on this document, and the
`18_displacement` that survives is the residue of that overspend, not the under-spend the class
was being blamed for. That is a different defect from the one this attempt was aimed at, and it is
the next thing to measure: `extraAbs = t.rowTopPt - flowTopPt(ctx)` is 4.5 pt too large on a
table whose top rule the page draws.

**Not kept.** 41/42 before and after; nothing moved, so nothing was committed to the engine.
`mobile-bill` and `insurance-policy-schedule` were reconverted with the change and both still
produced one page — they were not measured in Google, so their 46/47 is unrefuted but unproven.
