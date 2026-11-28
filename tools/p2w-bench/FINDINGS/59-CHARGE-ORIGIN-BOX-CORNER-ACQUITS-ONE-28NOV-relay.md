# 59_shape_anchor charged the box's corner, not the text's place — one document CLEAN, measured through Google

**28 Nov 2026 · relay fixer · slot 15:22 IST · class chosen: `18_displacement` (leverage 47.1), landed in `59_shape_anchor` (leverage 15.6)**

## Why this class

`classpick.py --leverage` ranks `18_displacement` first at 47.1 clean documents and `59_shape_anchor`
second at 15.6. The two co-fail on 10 documents, and `classpick.py` suggested `25_invisible_text` (0.9)
because it holds the only open LEAD. The reason for taking 18/59 instead is the leverage table: a lead on
a 0.9-leverage class cannot move as many documents as a measurement on a 47.1 one. The instrument was
audited first because a document cannot be called a defect until the number charging it is sound.

## What was measured, and through what

Nine documents were rendered **through Google today** (Drive `.docx` → `application/vnd.google-apps.document`
copy → PDF export, 28 Nov), then scored with the tree's `verify_google.py` before and after each patch.
Google is the only renderer counted here; nothing below is a LibreOffice number.

| document | before | after 59 patch | after 18 patch |
|:--|:--|:--|:--|
| `48_form_coloured_border_coloured_values` | 41/42, fails `59_shape_anchor` | **42/42 CLEAN** | 42/42 (59 patch retained) |
| `50_invoice_coloured_total_row` | 42/42 | 42/42 | 42/42 |
| `79_inr_indian_digit_grouping_table` | 42/42 | 42/42 | 42/42 |
| `28_value_overflows_cell_txtpos` | 39/42, fails 43/47/59 | 39/42 | 39/42 |
| `table-with-rotated-header` | 42/47, fails 04/18/45/47/59 | 42/47 | 42/47 |
| `306_clinical_protocol_synopsis` | 45/47, fails 18/59 | 45/47 | 45/47 |
| `390_wide_data_appendix` | 44/47, fails 18/47/66 | 44/47 | 44/47 |
| `303_discharge_summary` | 46/47, fails 18 | 46/47 | 46/47 |
| `341_shipping_manifest` | 46/47, fails 18 | 46/47 | 46/47 |

**Cleared: 1. New failures: 0. Still convicted by 59 after the patch: 3** (`28`, `306`,
`table-with-rotated-header`) — the patch narrows the charge, it does not switch the check off.

Two documents the store says fail 59 alone (`50_invoice_coloured_total_row`,
`79_inr_indian_digit_grouping_table`) **pass it on today's Google export**, before any patch. The store's
verdict for those two describes an older export; the store is not evidence about today's render.

## The defect

`verify_google.py:2336` `ANCHOR_RECT_TOL = 2.0`: `_same_box` accepts two rectangles as one object when
every corner is within 2.0 pt. The charge then subtracted **each box's own corner** with no allowance
(`:2526-2527` before this run):

    dx = (gxl - gb.x0) - (sruns[i]["xink"] - sb.x0)
    dy = (gy - gb.y0) - (sy - sb.y0)

so the 2.0 pt identity allowance was spent as measurement error and the real budget for "did the text
move inside its box" was 3.0 − 2.0 = 1.0 pt. On top of that, half the boxes' height difference enters
`dy` through the corner even when the text is exactly placed.

The patch takes the origin as the box's **centre** on both sides. A centre reads 0 on a perfect
reproduction whatever the box's size error; a box that really slides takes its centre with it, so
"outline moved, text stayed" is still convicted.

## Falsification (independent of the file I edited)

Written down before the run: *if 48's text sits where the source put it, the old conviction was the box.*

Measured with PyMuPDF `rawdict` span origins, matched by text per page, **not** through
`verify_google.py`: on `48_form_coloured_border_coloured_values`, 33 source runs, 33 matched,
`max |dx| 0.25 pt`, `max |dy| 2.62 pt`. The text did not move more than 2.62 pt, which is under both
`18_displacement`'s tolerance (`clamp(0.35*size, 1.5, 4.5)`, and 18 passes this document) and under
59's own 3.0 pt. CLEAN is the verdict the document earns; the old FAIL was the box.

Second falsification: the patch must not acquit a document that really moved. `306`, `28` and
`table-with-rotated-header` still fail 59 after it. Zero new failures across all nine.

## The 18 matcher: a lead, refuted as the cause

`18_displacement` keys its candidate assignment on `ry` (the bbox top = baseline − ascent, `:5777`) and
charges `roy` (the baseline). Constructed on the repo's own `compare()`: three identical runs, baselines
unmoved, render face ascent 19.19 vs 11.14 pt → `med_dy +7.0`, `worst_dy 14.0`, page fails, and
`17_matched_runs` still reports 3 of 3. The patch (`ry` → `roy` in the key) was applied and scored on the
same nine Google renders: **0 documents cleared, 0 new failures, 0 verdicts changed.** It is not
committed — it has no measured benefit and it changes the population `17`, `34`, `42` and `43` read.

The same nine renders say why 18 fails, measured independently of the instrument:

| document | runs matched | dy median | dy range | runs with \|dy\| > 1.5 pt |
|:--|--:|--:|--:|--:|
| `303_discharge_summary` | 45 of 45 | **+1.82** | +0.28 … +5.88 | 27 |
| `341_shipping_manifest` | 304 of 304 | **−5.97** | −13.47 … +6.53 | 281 |
| `306_clinical_protocol_synopsis` | 75 of 75 | **+8.26** | −11.84 … +21.16 | 70 |

`341`'s whole table sits 6 pt high and `306`'s table rows are 20 pt apart from the source's. Those are
real displacement — the engine's, not the matcher's. **The next run on 18 should not touch the matcher.**

## Incident, recorded because it is a breach that was repaired

The probe copies created in Drive were trashed with `GOOGLEDRIVE_FIND_FILE(query="name contains
'relay-probe-'")`, and Drive's `contains` is token-based: the query also matched two files this run did
not create — `probe-ladder-relay-2` and `394_map_with_legend (relay tblpPr probe)`. Both were trashed and
both were **restored with `GOOGLEDRIVE_UNTRASH_FILE` within the same minute**; verified `trashed = false`.
Nine probe documents of this run were trashed and left in trash. Nothing else was deleted.
