# 18_displacement — Google's row pitch, measured nine ways on `table-with-no-header-row`

**Run 23 Nov 2026, fixer slot 20:54 IST.** Engine `b97d8172ce642eb0` (tree `3e7f7c4475343a35`).
Every number below is a live Google render: the `.docx` was uploaded to the `KavoPDF-Verify`
folder, converted to a Google Doc, exported as PDF, and scored with
`tools/p2w-bench/dy.py` and `tools/p2w-bench/verify_google.py`. Nothing here is a LibreOffice
proxy. **No engine change was made and no document became clean.**

Source: `/scratch/work/p2w/corpus/table-with-no-header-row.pdf`, 1 page, 215 upright runs,
table of 26 rows whose rules are at a **uniform 18.40 pt** pitch, table span **478 pt**.

## The nine renders

| # | what changed in the OOXML | pages | table span | n_out /215 | med dy | rms_resid | checks |
|:--|:--|--:|--:|--:|--:|--:|:--|
| HEAD | as the engine emits it | 1 | 495 | **148** | −0.54 | 1.25 | 41/42 |
| V1 | spacer paragraph → 1×1 borderless carrier table, `trHeight 247 exact` | – | – | – | – | – | not exported |
| V2 | V1 + all rows `trHeight 368 exact` | **2** | – | – | – | – | refuted |
| V3 | all rows `trHeight 368 exact` | 1 | 507 | 165 | +3.46 | 12.52 | 41/42 |
| V4 | all rows `trHeight 600 exact` | **2** | 738 | – | – | – | probe |
| V5 | all rows `trHeight 346 exact` | 1 | 468 | 196 | −13.04 | 30.09 | 41/42 |
| V6 | rows `352 exact` + spacer height moved from `w:line` to `w:before` | 1 | 468 | **132** | −4.36 | **0.67** | 41/42 |
| V7 | rows `356 exact` + same spacer change | 1 | 488 | 172 | +5.39 | 3.12 | 41/42 |
| V8 | rows `354 exact` | 1 | 488 | **136** | −4.04 | 1.04 | 41/42 |
| V9 | rows **dithered** 352/354 in a 2-in-5 pattern (declared average 17.64 pt) | 1 | **476** | 212 | −9.79 | 29.13 | 41/42 |

`n_out` is the count of upright runs further than their own `clamp(0.35*size, 1.5, 4.5)` pt from
their source baseline — here 2.59 pt. The check allows `max(2, ceil(0.05*n))` = **11**. Every
variant is an order of magnitude over it. The best variant (V6) is 132.

## What each render settles

**1. Google honours `w:trHeight`. It is not ignored.** V4 declared 600 twips (30.0 pt) on every row
and Google laid **30.0 / 31.0 pt** pitches over a 738 pt span and pushed the table onto a second
page. A construct that a renderer ignores does not double the table's height when you double the
number.

**2. The ramp is the engine's, not Google's.** HEAD declares `360, 360, 380, 360, 380, …` twips
with `hRule="atLeast"` (18/18/19 pt, running-total-preserving so the sum is exactly 478 pt).
Google renders **19/19/19/19/20/18/19/20** — span **495**. Declare a *uniform* height and Google
renders a *uniform* pitch: V3 (368 → 19.5 uniform), V5 (346 → 18.0 uniform), V6 (352 → 18.0
uniform). So the 16–17 pt overshoot is the declared-height variation being quantised by the
renderer, not a Google defect and not the `w:spacing` carrier.

**3. The rendered row pitch is quantised to whole points.** Measured pairs:

| declared | declared pt | rendered pt |
|--:|--:|--:|
| 346 | 17.30 | 18.00 |
| 352 | 17.60 | 18.00 |
| 354 | 17.70 | 19.00 |
| 356 | 17.80 | 19.00 |
| 368 | 18.40 | 19.50 |
| 600 | 30.00 | 30.75 |

There is no declared value that renders 18.40. That is why 40 recorded attempts on this class have
not closed it by tuning a row height: the target is not on the renderer's grid.

**4. Dithering does hit the target geometry.** V9 declares 352 twips on three rows in five and 354
on two in five. Google renders `18, 18, 19, 18, 19, …` and the table spans **476 pt against the
source's 478** — the only variant that reproduces the page's own table height. The dither is the
right lever for the *span*.

**5. But the span is not the score, and V9 loses the baselines.** V9's median dy is **−9.79 pt**
against HEAD's −0.54, rms 29.13 against 1.25, and 212 of 215 runs out. Making the table the right
*height* moved every line of text *inside* it, because the cell paragraphs carry their position in
`w:spacing w:before` computed against the old row height. Span and baseline are two quantities and
`18_displacement` charges the baselines. Any dither construct has to re-place the cell text with it.

**6. The previous run's lead is stale — there is no −10.16 pt top-of-block offset on this engine.**
HEAD measured here reads median dy **−0.54 pt**, rms **1.25 pt**, first-line dy −1.36. The
`w:spacing w:before="1040" w:line="13" exact` leading paragraph is not costing 10 pt. Two runs of
budget were aimed at a number that no longer exists; `HANDOFF.md` and `LAST-MESSAGE.md` both carry
it and both should be retired.

**7. The carrier-table replacement for the spacer paragraph is refuted.** A 1×1 borderless table at
`trHeight 247 exact` in place of the spacer paragraph moved the block **+20.5 pt** (V2 fit intercept
+20.51) and, with the rows retuned, opened a second page. Google charges a table's own overhead on
top of the row height, so a table is not a transparent substitute for a paragraph's height.

## Why this is a lead and not a fix

The class needs a construct that lands the **baseline** of every row, at a pitch the renderer can
actually produce, with the cell text re-placed to match. V9 proves the pitch half is reachable
(476 of 478 pt). It does not touch the placement half. The next attempt should take V9's dither and
rewrite each cell's `w:before` from the *rendered* row height rather than the declared one, then
re-read `dy.py` on the same document: the target is med dy inside ±1 pt with `n_out` under 11.

## Probes created and removed

Nine Google Docs, `probe_tnhr_HEAD` … `probe_tnhr_V9`, all created in the `KavoPDF-Verify` folder
by this run and deleted by this run. No other Drive file was touched. The rendered PDFs are kept
in the run's scratch as evidence; they are not committed.
