# 18_displacement: the cell's line box is 0.6 pt. That is the mechanism, and it kills the proposed fix.

**28 Nov 2026, relay slot 05:14.** Two agents were deployed this run. Agent A proposed: a table cell's
text is displaced because the row's top edge is invented from a *pitch* while the cell's baseline is
written from a *box*, so the text lands `(1 - LINE_BASE) x before` low, and the fix is to write
`w:before = 0` with `w:line` set to the row's pitch. Agent B measured the same population from the
other side and found a **constant offset with no drift** (+0.62 to +4.72 pt), while Google at HEAD
reads the same rows `med_dy 0.1`, 47/47.

**Both are describing the same thing, and agent A's fix is the wrong one. Do not land it.**

## What the .docx actually declares

Read out of the converted documents in `/scratch/work/p2w/out` (engine as at `a05b20eb`, the tree):

| document | row | `w:trHeight` | cell `w:before` | cell `w:line` | `lineRule` |
|:--|--:|--:|--:|--:|:--|
| `35_four_typefaces_one_page` | 0-2 | 380 tw = 19.00 pt | **368 tw = 18.40 pt** | **12 tw = 0.60 pt** | exact |
| `71_invoice_space_aligned_no_rules` | 0 | 360 tw = 18.00 pt | **348 tw = 17.40 pt** | **12 tw = 0.60 pt** | exact |
| `71_invoice_space_aligned_no_rules` | 1-2 | 360 tw = 18.00 pt | 180 tw = 9.00 pt | 180 tw = 9.00 pt | exact |

A 12 pt font in a 0.60 pt line box. The box is 5% of the natural line height of the glyphs it holds.

## The arithmetic

The engine's own placement is **self-consistent and correct**: it preserves the baseline the page
drew. For `35_four_typefaces_one_page` row 0, `before = wantPt - LINE_BASE x box` with
`wantPt = 18.88 pt` gives `18.40 = 18.88 - 0.8 x 0.60`, and the renderer puts the baseline back at
`18.40 + 0.8 x 0.60 = 18.88 pt`. Nothing in that pair loses a point.

What is not portable is **where the renderer puts a baseline inside a 0.60 pt exact line box**. The
position is 96% `before` and 4% box. A renderer that clamps an exact line box up to the glyph's
natural height moves the baseline by a fixed amount and never by a ramping one - which is exactly
the signature agent B measured: a constant +0.62 to +4.72 pt, identical on a table at the top of a
page and a table 210 pt down it, with no growth down the rows.

## The page, measured

`35_four_typefaces_one_page`, page 1: rules at y = 136.0, 155.0, 174.0 (19.0 pt pitch); the header
row's text bbox is y0 139.18, y1 151.44, so its baseline is **148.80 = 12.80 pt below the row top**
at 136.0. `71_invoice_space_aligned_no_rules`, page 1: header row text baseline 155.94 against a
table top near 143, so ~13 pt below its row top. Two documents, two pitches, one answer: the page
puts cell text a fixed fraction of a pitch below the row top, and the engine reproduces it.

## Why `w:before = 0, w:line = pitch` must not be landed

It moves every cell's baseline in **Google** by `-before` - 18.40 pt on `35_four_typefaces_one_page`,
17.40 pt on `71_invoice_space_aligned_no_rules`. Google is the truth and Google currently reads those
rows at `med_dy 0.1`, 47/47. The change is not a correction of a displacement; it is a 18 pt
displacement, in the renderer the score is taken in. The LibreOffice number would improve by 3.70 pt
and the Google number would fall off a cliff - the exact trade the `ROW_RUNG_UNDER_TW` history
records twice (`37be1707`, `6865f403`): a LibreOffice-looking fix that Google refuses.

The same code carries the rejected variant in its own comment at `DocxWriter.java` - *"Writing
before = rowLineTw - box instead moved every cell 0.2 x row pitch lower and 18_median_dy went 64 ->
100 documents."*

## What would settle it, for the next run

1. Take a **Google** export of `35_four_typefaces_one_page` (none exists in the repo) and read the
   header row's baseline. If it is 12.80 pt below the row top, the engine is right and the class is a
   LibreOffice artefact that no engine change can pay down.
2. If the real question is the clamp, the candidate is not `before` at all: it is **`w:line`**.
   `0.60 pt` is not a line box, it is a floor that two renderers floor differently. Give the cell the
   font's natural line box and move the same difference into `before` so the baseline is preserved
   by construction - `before' = wantPt - LINE_BASE x box'` - and the pair is then portable because
   neither term is sub-glyph. This has **not** been measured; it is the next attempt, and it predicts
   a zero move in Google if and only if Google is preserving the baseline today.

## Ruled out

- Flow text: exact to <= 0.04 pt on 14 lines across three documents (agent A, this run).
- `LINE_BASE`'s value: 0.8 is right for LibreOffice's exact box; the defect is not the constant.
- A per-row ramp in the cell top: agent B measured none - the offset is constant, and a ramp is the
  `ROW_RUNG_UNDER_TW` path, which is a deliberate Google compensation and stays.
- `worst_dy` 26.3 / 101.4 readings: `verify_google.py` pairing repeated numeric cells, not movement.
