# The refused table spacer delivers 22.9% of the gap it declares - and the guard never knew

**Class:** `18_displacement` · **Outcome:** lead (measured, not committed) · **26 Nov 2026, slot 07:31**

## The two findings this rests on

Both were committed earlier in this slot by two subagents.

1. `FINDINGS/18_displacement-CLAUSE-NOT-DS-074250-71ae.md` — for all 25 documents that fail
   *only* `18_displacement`, the clause that fires is **over_tolerance**, 25 of 25. The
   `if not ds` branch fires on **0**. So the class is vertical position, not run matching, and
   `SETTLED.md` §4c's `not_ds` hypothesis is settled against, not confirmed.
2. `FINDINGS/w-line-exact-GOOGLE-CHARGE-075617-f0cc.md` — Google charges an exact line box of
   `L` twips on a faceless `w:sz=2` mark at **`2.74663 × max(L/240, 0.06)` pt**, not `L/20`.
   Measured over 17 points across four faces, residual ≤ 0.0007 pt. The `2.5873` that
   `DocxWriter.java` quoted is that law with the Arial ratio substituted for the Calibri one
   Google substitutes for a run that names no face.

## What that means for the refused spacer

`DocxWriter.java` writes a table-top gap two ways. The *spendable* branch splits it — hairline in
`w:line`, the rest in `w:before` — and is accurate to 0.11 pt. The **refused** branch, taken when
the page has no room for the whole gap, declares the whole gap as `w:line`:

    <w:spacing w:before="0" w:after="0" w:line="2880" w:lineRule="exact"/><w:rPr><w:sz w:val="2"/></w:rPr>

At the law above that delivers `2.74663/12 = 0.228886` of the declared gap. 2880 twips asks for
144.00 pt and Google draws **32.96**. Every row under the table sits **111.04 pt high**.

**Census, from the corpus as it stood at `981ff1fa35e2cf67`:** 62 documents, 141 instances.

## The change (in the working tree, not committed)

The guard refuses because the page has no room for the *whole* gap. It says nothing about the
22.9% the construct is already delivering — and that 22.9% is already being spent, unguarded, with
the guard unaware. So the refused branch now hands Google the room it actually has, as `w:before`
(honoured exactly and additively), floored at what the old construct already charged:

    oldChargePt   = 2.74663 * max(spacerTw/240, 0.06)
    floorTw       = round(oldChargePt * 20)          // the old construct's own charge, in twips
    roomLeftTw    = slackTw - spacerSplitTw - rowExcessTw
    partialTw     = min(spacerTw - 1, max(floorTw, roomLeftTw))
    beforeTw      = max(0, partialTw - 3)            // 3.30 twips = the hairline's charge
    w:line        = 1

A refused spacer can therefore only move the table **towards** where the source drew it, never
away, and never past the paper's bottom edge.

## Measured, before and after

Engine `981ff1fa35e2cf67` (before) vs `2c7141b7eeb9a0fe` (after). All 213 documents converted on
both engines; the 62 documents carrying a refused spacer compared construct by construct on
`word/document.xml`, delivered gap computed from the law above.

| | |
|:--|--:|
| Documents carrying a refused spacer | 62 |
| Instances compared | 141 |
| Documents that gained gap | **37** |
| Documents unchanged | 24 |
| Documents that lost gap | 1 |
| Largest single-document gain | **+51.04 pt** (`374_org_chart`) |

Gains of 10 pt or more: `gst-invoice-multipage-item-table` +26.20, `403_crossword_puzzle` +24.86,
`23_timetable_grid_txtpos` +17.21, `343_air_waybill` +15.50,
`invoice-line-items-qty-rate-amount` +13.47, `340_bill_of_lading` +12.08,
`02_stamp_rotated_15deg_upleft` +11.54, `13_stamp_non_english` +10.75,
`56_table_indented_from_margin` +10.53, `390_wide_data_appendix` +10.30,
`72_bank_statement_no_rules_right_amounts` +10.23.

## The one regression, and the correction

`itr-computation-with-slab-table` lost **0.258 pt** across 5 instances. Cause: the first cut of
`floorTw` was `round(0.2289 * spacerTw)`, which omits the law's `0.06` floor clause and therefore
under-states the old charge for a spacer under 14.4 twips. `floorTw` is now
`round(20 * oldChargePt)` — the old construct's charge converted back to twips — and the
never-worse invariant then holds by construction.

Re-checked arithmetically over the same 141 instances in the no-room branch (the worst case):
worst-case delta **−0.0085 pt**, which is the 3-twip hairline offset against its 3.30-twip charge,
not a real loss, and 176× below the check's 1.5 pt floor.

## Why it is a lead and not a kept fix

The change moves 37 documents, so the commit gate will not skip: `regress.py --check` demands a
full-corpus re-measurement through Google for a `.docx` change that moves the corpus, and the
slot did not have the minutes for that after the two corpus conversions. **Nothing is committed
but this file.** The next run should:

1. apply the two hunks in `DocxWriter.java` around line 6121 (refused branch only),
2. run `pod-prep.sh` to conversion-complete, then the full `regress.py --check` pass,
3. watch `374_org_chart`, `403_crossword_puzzle` and `23_timetable_grid_txtpos` first — they gain
   the most and are therefore where an over-spend would show as content loss,
4. expect `18_displacement` to move on the subset of the 25 solo documents that carry a refused
   spacer. It will not clear the class on its own: agent A found 14 of the 25 carry no refused
   spacer at all.

## What would prove this wrong

- A document where the table now sits *below* where the source drew it. The change only ever adds
  gap, so an overshoot means `slackTw` over-states the room — check `ctx.pageInkBottomPt`.
- `374_org_chart` losing content at the page foot: +51.04 pt is the largest spend in the corpus.
- Google charging the `w:before` differently from the additive 1/20 pt per twip that agent B
  measured. That was measured on `w:before` directly (240 tw → 12.0000 pt), so it should hold.
