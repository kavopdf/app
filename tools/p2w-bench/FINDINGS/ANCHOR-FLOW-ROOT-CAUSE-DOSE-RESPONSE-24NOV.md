# The 105.7 pt is not a font error: it is the carrier's w:line="1"

**Diagnosed 24 Nov by an agent with a dose-response experiment, then code-verified here.**

## What the recorded figure actually is

The claim lives in `DocxWriter.java:328-329`. Three of its four numbers do not reproduce on any build
that can be constructed from the repository:

| recorded | measured |
|---|---|
| 51 flowed lines | 51 is the census's `flowFromBox` CALL count - it is 51 in every build. Real flowed paragraphs at HEAD: **6** |
| 27 anchored boxes | **62** at HEAD |
| 21 overlaps | **0** at HEAD |
| median abs(dy) 105.7 pt | **101.85** (parent of the fix), **110.48**, **112.28** - not to the digit |

`git log -S"105.7"` puts it in `bf2355c9` (15 Nov) and its parent `2ee35964` gives 101.85. The figure
came from an instrumented private build not in the repo. **The phenomenon is real; the digit is not
reproducible.** Anyone quoting 105.7 should quote 101.85-112.28 instead.

## The cause, measured

The box model is **exact**: `posOffset` from the page top, median abs(dy) **0.02 pt** against the source
PDF on every build, every box. The flow model is what is wrong.

**H7 (the operative one).** Every anchored box is carried by a paragraph that emits
`w:before="0" w:after="0" w:line="1" w:lineRule="exact"` - 0.05 pt of flow advance. `anchorKeepsFlow`
then advances `ctx.flowY` by the advance that line WOULD have had as a flow line, which was never
written. So the engine and the file disagree at every box, one-signed, cumulative.

Dose-response, rendered: changing ONLY that `w:line` moves the worst flowed-line dy from **-101.82**
(1) to **-15.42** (65) to **+70.98** (129). Slope **1.350 pt per twip = 27/20**, zero at `w:line = 76`.

**H8 (the structural one, and why the boxes exist).** The flow is 1-D and cannot move backwards. A line
whose measured y is above the flow gets `w:before="0"` and lands one pitch low (`place()` returns
`{0, linePt}` for `d <= 0`). The engine emits a two-column band column-by-column, so the right column
lands below the left column's last line. Pure flow: median **+112.28**, max **+138.78**, and **18 of 54**
flowed lines have a negative required gap, worst **-85.05 pt**. The offset moves in exact page-pitch
steps (1, 2, 8.7, 10.8 pitches), each step at a column change.

So: **boxes = 0.02 pt of position error plus a rasterised image of text; no boxes = up to 138.78 pt of
position error and real text.** That is the trade, as a number.

## What HEAD actually does

`PAGE_POSITION_ON_ANCHOR` does not repair the disagreement - it **suppresses** it. After the first
anchor the page is absolute, so no flowed line ever follows a box (6 flowed paragraphs, all above the
first box). The defect is still there; it is no longer reachable. That is why the boxes cannot be
removed without the drift returning.

## H1-H6, all refuted by measurement

Line-height/leading: single-column tail advance error **0.000 pt** over 9 pairs, and 13 consecutive
lines at a CONSTANT +138.75 pt - a per-line leading error cannot be constant. Baseline-vs-top: median
**+0.02 pt** over 29-52 boxes. `w:after` is `"0"` on every paragraph. `w:tbl` count **0** on this page.
`w:pgMar w:top="0"`. The engine's box y equals PyMuPDF's span ORIGIN to 0.02 pt.

## The three routes, and what gates them

(a) resync `flowY` from the emitted `(before=0, line=1)` - then the next flowed line must close
k x 12.85 pt, which the gap ceilings (`GAP_CAP_TW` 2400, `GAP_CAP_SPEND_TW` 20000) and `fitPage` clamp.
**The clamp puts the line back where the box was carrying it, and the box returns.** This is the
measured reason removing the boxes was tried and reverted.

(b) write the page pitch into the carrier's `w:line`. The dose fit says this is the whole disagreement,
at the cost of k x 12.85 pt of real page height - the pagination the caps exist to prevent.

(c) **Emit a band's two columns as ONE paragraph with tab stops at the measured x**, so the flow's
sequence IS the page's y sequence and no line is ever above the flow. The engine already does exactly
this for form rows (`flowRow`, :3546). It eliminates the 18-of-54 negative gaps by construction.
**NOT MEASURED - nobody has built it.**

## The measurement that should gate any of these

dy on the FLOWED lines of a two-positioner page must stop being a function of the carrier's `w:line`.
Today it is a perfect line (slope 27/20, residual 0). After a correct change the slope must be zero.

## Code facts verified here, in the repository

    DocxWriter.java:5626   w:before="0" w:after="0" w:line="1" w:lineRule="exact"   CONFIRMED
    DocxWriter.java:4152   place() returns {before, linePt}; before clamped to 0      CONFIRMED
    DocxWriter.java:4188   anchorKeepsFlow, called at :3670 and :4589                CONFIRMED

## Open

- Does Google charge the `w:line="1"` carrier as a FULL line? Google is known to rewrite
  `w:line="1" exact` to an auto line. If so, Google's flowed lines after a box land LOW - the opposite
  sign to LibreOffice. **Untested: no Drive credentials in that pod.** Three artifacts (`prev`, dose65,
  dose129) uploaded to Docs would settle it in one run.
- Which build produced 105.7 / 27 / 21 - not in the repository.
- Does route (c) hold the page to one sheet? Not built.
# Measurements - policy-2col-spanning-section-heading

Engine built from HEAD (b7699196 tree) with tools/p2w-bench/build-engine.sh; corpus from the
corpus-v1 release assets; every .docx rendered with LibreOffice 7.4 headless; every position
read from the PDF text layer with PyMuPDF (span origin = baseline).

## 1. Rendered vertical displacement, per build (61/61 source lines matched)

| build | lines | median dy | median abs dy | min | max |
|---|---:|---:|---:|---:|---:|
| head | 61 | -0.02 | 0.02 | -0.02 | +0.08 |
| p0 | 61 | -0.02 | 0.02 | -0.02 | +12.98 |
| prev | 61 | -0.02 | 0.02 | -101.82 | +12.98 |
| pagepos_0_anchorkeep_0 | 61 | +110.48 | 110.48 | -0.02 | +136.38 |
| noanchor | 61 | +112.28 | 112.28 | -0.02 | +138.78 |
| dose65 | 61 | -0.02 | 0.02 | -15.42 | +16.18 |
| dose129 | 61 | -0.02 | 0.02 | -0.02 | +70.98 |

`prev` = the commit before the one that introduced PAGE_POSITION_ON_ANCHOR (bf2355c9^).
`p0` = HEAD with -Dp2w.pagepos=0. `pagepos_0_anchorkeep_0` = HEAD with -Dp2w.pagepos=0 -Dp2w.anchorkeep=0.
`noanchor` = HEAD with -Dp2w.zganchor=false -Dp2w.pagepos=0 (pure flow).
`dose65`/`dose129` = the `prev` .docx with only the anchored box carrier's w:line changed to 65 / 129 twips.

## 2. Dose-response: the carrier paragraph's w:line sets the flow's displacement

| carrier w:line (twips) | carrier advance (pt) | worst flowed-line dy, rendered |
|---:|---:|---:|
| 1 | 0.05 | -101.82 |
| 65 | 3.25 | -15.42 |
| 129 | 6.45 | +70.98 |

slope = (70.98 - (-15.42)) / (129 - 65) = 1.350 pt per twip = 27/20: 27 anchored carriers sit above
the median flowed line. Zero displacement would need w:line = 76 twips (3.82 pt).

## 3. The two-positioner page, line by line (build `prev`)

29 lines are anchored boxes (dy 0.00); the flowed lines below them sit up to 101.82 pt high.

| source y | rendered y | dy | x | text |
|---:|---:|---:|---:|---|
| 55.02 | 55.00 | -0.02 | 51 | NIRVAAN PACKAGING INDUSTRIES |
| 55.02 | 55.00 | -0.02 | 374 | STAFF HANDBOOK  ·  REVISION 6  ·  APRIL 2026 |
| 81.02 | 81.00 | -0.02 | 51 | Section 4 |
| 103.02 | 103.00 | -0.02 | 51 | Leave and Attendance |
| 117.02 | 117.00 | -0.02 | 51 | Entitlement, procedure and consequences of unauthori |
| 136.22 | 136.20 | -0.02 | 51 | This section sets out the entitlement to leave for a |
| 136.22 | 136.20 | -0.02 | 308 | Sick leave is granted on production of a medical cer |
| 149.12 | 149.10 | -0.02 | 51 | employees, the procedure for applying for it, and th |
| 149.12 | 162.10 | +12.98 | 308 | where the absence exceeds two consecutive working da |
| 162.02 | 175.00 | +12.98 | 51 | consequences of taking leave without prior approval. |
| 162.02 | 162.00 | -0.02 | 308 | Certificates must be issued by a registered medical  |
| 174.92 | 174.90 | -0.02 | 51 | to employees on probation only to the extent stated  |
| 174.92 | 174.90 | -0.02 | 308 | and submitted within five working days of returning  |
| 187.82 | 187.80 | -0.02 | 51 | 4.7. Employees on fixed-term contracts should refer  |
| 187.82 | 187.80 | -0.02 | 308 | Where an employee is hospitalised, the certificate m |
| 200.72 | 200.70 | -0.02 | 51 | of their appointment letter, which prevail where the |
| 200.72 | 200.70 | -0.02 | 308 | submitted by a family member, and the reporting requ |
| 213.62 | 213.60 | -0.02 | 51 | this section. |
| 213.62 | 213.60 | -0.02 | 308 | waived. |
| 233.52 | 233.50 | -0.02 | 308 | Maternity leave is granted for twenty-six weeks for  |
| 233.52 | 195.30 | -38.22 | 51 | Earned leave accrues at the rate of one and three-qu |
| 246.42 | 246.40 | -0.02 | 308 | children, and for twelve weeks thereafter, in accord |
| 246.42 | 208.20 | -38.22 | 51 | for each completed month of service, credited on the |
| 259.32 | 259.30 | -0.02 | 308 | the Maternity Benefit Act as amended. An employee ad |
| 259.32 | 221.10 | -38.22 | 51 | working day of the following month. An employee may |
| 272.22 | 272.20 | -0.02 | 308 | child below three months of age is entitled to twelv |
| 272.22 | 234.00 | -38.22 | 51 | accumulate up to forty-five days. Accrual beyond tha |
| 285.12 | 285.10 | -0.02 | 308 | Notice must be given at least eight weeks before the |
| 285.12 | 246.90 | -38.22 | 51 | lapses at the end of the calendar year and is not en |
| 298.02 | 298.00 | -0.02 | 308 | date of commencement, accompanied by a certificate f |
| 298.02 | 259.80 | -38.22 | 51 | Earned leave may be availed in units of not less tha |
| 310.92 | 310.90 | -0.02 | 308 | attending doctor. |
| 317.92 | 279.70 | -38.22 | 51 | Casual leave is granted for short, unforeseen absenc |
| 330.82 | 330.80 | -0.02 | 51 | limited to seven days in a calendar year. It may not |
| 330.82 | 330.80 | -0.02 | 308 | An application for leave must be submitted through t |
| 343.72 | 343.70 | -0.02 | 51 | with earned leave without the written approval of th |
| 343.72 | 343.70 | -0.02 | 308 | portal at least seven days before the first day of a |
| 356.62 | 356.60 | -0.02 | 51 | department head, and it may not be taken immediately |
| 356.62 | 356.60 | -0.02 | 308 | for casual and sick leave, where the application mus |
| 369.52 | 369.50 | -0.02 | 51 | after a public holiday except in an emergency, in wh |
| 369.52 | 369.50 | -0.02 | 308 | submitted on the first day of absence and in any cas |
| 382.42 | 382.40 | -0.02 | 51 | reason must be recorded in the leave application its |
| 382.42 | 382.40 | -0.02 | 308 | than twenty-four hours after the absence begins. App |
| 395.32 | 293.50 | -101.82 | 308 | that remain unapproved for more than three working d |
| 408.22 | 306.40 | -101.82 | 308 | escalated to the department head automatically. |
| 451.02 | 349.20 | -101.82 | 59 | 4.5 Leave without pay and the effect on continuity o |
| 463.02 | 361.20 | -101.82 | 59 | Applies to all permanent employees, and to employees |
| 494.22 | 392.40 | -101.82 | 51 | Absence without approved leave for more than three |
| 507.12 | 405.30 | -101.82 | 51 | consecutive working days is treated as unauthorised  |
| 520.02 | 418.20 | -101.82 | 51 | The employee will be issued a written notice to expl |
| 532.92 | 431.10 | -101.82 | 51 | no satisfactory explanation is received within seven |
| 545.82 | 444.00 | -101.82 | 51 | period may be treated as a break in service for the  |
| 558.72 | 456.90 | -101.82 | 51 | continuity, subject to the procedure in Section 9. |
| 578.62 | 476.80 | -101.82 | 51 | Leave taken in excess of entitlement is treated as l |
| 591.52 | 489.70 | -101.82 | 51 | pay and recovered from the following month's salary. |
| 604.42 | 502.60 | -101.82 | 51 | employee resigns with leave without pay outstanding, |
| 617.32 | 515.50 | -101.82 | 51 | amount is adjusted against the final settlement. Ear |
| 630.22 | 528.40 | -101.82 | 51 | balance at the time of resignation is encashed at th |
| 643.12 | 541.30 | -101.82 | 51 | last drawn basic salary. |
| 810.71 | 810.70 | -0.01 | 51 | Nirvaan Packaging Industries  ·  Human Resources |
| 810.71 | 810.70 | -0.01 | 540 | 4 |

## 4. Pure flow, no anchored boxes (build `noanchor`)

54 flowed lines. The offset moves in exact page-pitch steps at each column change and never recovers.

| source y | rendered y | dy | x | text |
|---:|---:|---:|---:|---|
| 55.02 | 55.00 | -0.02 | 51 | NIRVAAN PACKAGING INDUSTRIES |
| 55.02 | 55.00 | -0.02 | 374 | STAFF HANDBOOK  ·  REVISION 6  ·  APRIL 2026 |
| 81.02 | 81.00 | -0.02 | 51 | Section 4 |
| 103.02 | 103.00 | -0.02 | 51 | Leave and Attendance |
| 117.02 | 117.00 | -0.02 | 51 | Entitlement, procedure and consequences of unauthori |
| 136.22 | 136.20 | -0.02 | 51 | This section sets out the entitlement to leave for a |
| 136.22 | 149.80 | +13.58 | 308 | Sick leave is granted on production of a medical cer |
| 149.12 | 149.10 | -0.02 | 51 | employees, the procedure for applying for it, and th |
| 149.12 | 162.70 | +13.58 | 308 | where the absence exceeds two consecutive working da |
| 162.02 | 175.60 | +13.58 | 51 | consequences of taking leave without prior approval. |
| 162.02 | 176.20 | +14.18 | 308 | Certificates must be issued by a registered medical  |
| 174.92 | 188.50 | +13.58 | 51 | to employees on probation only to the extent stated  |
| 174.92 | 202.10 | +27.18 | 308 | and submitted within five working days of returning  |
| 187.82 | 201.40 | +13.58 | 51 | 4.7. Employees on fixed-term contracts should refer  |
| 187.82 | 215.00 | +27.18 | 308 | Where an employee is hospitalised, the certificate m |
| 200.72 | 227.90 | +27.18 | 51 | of their appointment letter, which prevail where the |
| 200.72 | 228.50 | +27.78 | 308 | submitted by a family member, and the reporting requ |
| 213.62 | 240.80 | +27.18 | 51 | this section. |
| 213.62 | 240.80 | +27.18 | 308 | waived. |
| 233.52 | 345.80 | +112.28 | 308 | Maternity leave is granted for twenty-six weeks for  |
| 233.52 | 260.70 | +27.18 | 51 | Earned leave accrues at the rate of one and three-qu |
| 246.42 | 358.70 | +112.28 | 308 | children, and for twelve weeks thereafter, in accord |
| 246.42 | 273.60 | +27.18 | 51 | for each completed month of service, credited on the |
| 259.32 | 371.60 | +112.28 | 308 | the Maternity Benefit Act as amended. An employee ad |
| 259.32 | 286.50 | +27.18 | 51 | working day of the following month. An employee may |
| 272.22 | 384.50 | +112.28 | 308 | child below three months of age is entitled to twelv |
| 272.22 | 299.40 | +27.18 | 51 | accumulate up to forty-five days. Accrual beyond tha |
| 285.12 | 397.40 | +112.28 | 308 | Notice must be given at least eight weeks before the |
| 285.12 | 312.30 | +27.18 | 51 | lapses at the end of the calendar year and is not en |
| 298.02 | 410.30 | +112.28 | 308 | date of commencement, accompanied by a certificate f |
| 298.02 | 325.20 | +27.18 | 51 | Earned leave may be availed in units of not less tha |
| 310.92 | 423.20 | +112.28 | 308 | attending doctor. |
| 317.92 | 345.10 | +27.18 | 51 | Casual leave is granted for short, unforeseen absenc |
| 330.82 | 443.10 | +112.28 | 51 | limited to seven days in a calendar year. It may not |
| 330.82 | 443.70 | +112.88 | 308 | An application for leave must be submitted through t |
| 343.72 | 456.00 | +112.28 | 51 | with earned leave without the written approval of th |
| 343.72 | 482.50 | +138.78 | 308 | portal at least seven days before the first day of a |
| 356.62 | 468.90 | +112.28 | 51 | department head, and it may not be taken immediately |
| 356.62 | 495.40 | +138.78 | 308 | for casual and sick leave, where the application mus |
| 369.52 | 481.80 | +112.28 | 51 | after a public holiday except in an emergency, in wh |
| 369.52 | 508.30 | +138.78 | 308 | submitted on the first day of absence and in any cas |
| 382.42 | 521.20 | +138.78 | 51 | reason must be recorded in the leave application its |
| 382.42 | 521.20 | +138.78 | 308 | than twenty-four hours after the absence begins. App |
| 395.32 | 534.10 | +138.78 | 308 | that remain unapproved for more than three working d |
| 408.22 | 547.00 | +138.78 | 308 | escalated to the department head automatically. |
| 451.02 | 589.80 | +138.78 | 59 | 4.5 Leave without pay and the effect on continuity o |
| 463.02 | 601.80 | +138.78 | 59 | Applies to all permanent employees, and to employees |
| 494.22 | 633.00 | +138.78 | 51 | Absence without approved leave for more than three |
| 507.12 | 645.90 | +138.78 | 51 | consecutive working days is treated as unauthorised  |
| 520.02 | 658.80 | +138.78 | 51 | The employee will be issued a written notice to expl |
| 532.92 | 671.70 | +138.78 | 51 | no satisfactory explanation is received within seven |
| 545.82 | 684.60 | +138.78 | 51 | period may be treated as a break in service for the  |
| 558.72 | 697.50 | +138.78 | 51 | continuity, subject to the procedure in Section 9. |
| 578.62 | 717.40 | +138.78 | 51 | Leave taken in excess of entitlement is treated as l |
| 591.52 | 730.30 | +138.78 | 51 | pay and recovered from the following month's salary. |
| 604.42 | 743.20 | +138.78 | 51 | employee resigns with leave without pay outstanding, |
| 617.32 | 756.10 | +138.78 | 51 | amount is adjusted against the final settlement. Ear |
| 630.22 | 769.00 | +138.78 | 51 | balance at the time of resignation is encashed at th |
| 643.12 | 781.90 | +138.78 | 51 | last drawn basic salary. |
| 810.71 | 810.70 | -0.01 | 51 | Nirvaan Packaging Industries  ·  Human Resources |
| 810.71 | 810.70 | -0.01 | 540 | 4 |
---

## The open question, closed: Google does NOT charge the carrier a full line

This finding left one branch untested - "does Google charge the `w:line="1"` carrier as a FULL line?
Google is known to rewrite `w:line="1" exact` to an auto line. If so, Google's flowed lines after a box
land LOW - the opposite sign to LibreOffice."

**The repository already answered it, in a correction that was itself a correction.** From
`18_displacement-CORRECTION-1045-relay.md`, written 22 Nov after an audit of the finding it corrects:

    The read-back value w:line="14.399999999999999" w:lineRule="auto" is almost certainly NOT 14.4 pt -
    under lineRule="auto" that attribute is in 240ths of a line, so the export is writing a number this
    run read as points and should not have.

    So the mechanism this finding proposed - "Google substitutes a ~14.4 pt box for the hairline" - is
    withdrawn.

14.4/240 is 0.06 of a line, about 0.78 pt at a 13 pt line height - the same tiny advance LibreOffice
charges (0.05 pt), not a full line. **So the sign does not flip, the two renderers agree on this
quantity, and the experiment that was going to need three .docx files published at a public URL does
not need to happen at all.**

The lesson is the one this session kept repeating: "14.4 pt" was a units error read as points, quoted
onward as a Google behaviour. Anyone pricing a fix against the carrier's `w:line` should price it at
0.06 line, and anyone quoting "Google rewrites it to a full line" is quoting the withdrawn claim.
