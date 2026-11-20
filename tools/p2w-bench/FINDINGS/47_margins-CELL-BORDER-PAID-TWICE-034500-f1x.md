# 47_margins: the cell's own border was paid twice

**21 Nov 2026, 03:45 IST, fixer.** Class `47_margins` (26 documents in Google). Outcome: mechanism
proved, patch written and measured on nine documents - **two improved, none worse** - and NOT landed,
because landing needs a full corpus pass that this slot did not have. The patch is
`patches/47-margins-cell-border-inset.patch`. Read this before you spend a run on the class.

## The defect

`DocxWriter.insetTw()` measures a cell's text x from the cell's **left edge on the page**, and the
writer then draws a rule of its own on that edge (`w:tblBorders` / `w:insideV`, from the page's own
stroke weights). A renderer lays the cell's content **inside its border**, so the text lands at

    edge + borderWidth + w:ind

where `w:ind` is already the page's own inset. The border the writer added is therefore paid a second
time, in full, on every cell of every ruled table.

## The proof, and it is one XML edit

`404_sudoku_grid`: nine 44 pt columns, `w:sz="16"` = 2 pt on `left` and `insideV`. All 30 of the
document's unregistered runs sat exactly **2.1 pt right** of the page (`src 115.9 -> ren 118.0`,
`159.9 -> 162.0`, identical on every column). Editing only the emitted XML - `w:left` and
`w:insideV` set to `nil`, nothing else touched - moved all 30 to within **0.1 pt** (`116.0`, `160.0`).
The border contributed exactly 2.0 pt; the residual 0.1 pt is the pre-existing substitution error.

## The patch

Subtract the border this cell gets on its left side, in twips = `w:sz * 2.5`: the table's `left` rule
in column 0, the `insideV` rule in every other column, and 0 where that side is not drawn. Applied at
both `w:ind` emission sites - the string-cell path and `cellParaXml` through `pInset`.

**It is applied AFTER the widening and overflow arithmetic, not to `insetTw` itself.** The first
version subtracted early and changed which cells got widened over their empty neighbours; on
`78_mixed_english_devanagari_line` that moved four runs 36.8 pt. A layout decision taken to fix a
position. Keep the subtraction at the emission site.

## Measured - same-engine pair, or nothing

Every number below is a HEAD build and a patched build of the **same tree**, both rendered through
soffice and scored by `verify_google.py` with the 42 checks. LibreOffice, so this is the proxy, not
the verdict.

| document | before | after | 47_margins |
|---|---|---|---|
| `404_sudoku_grid` | 46/47 | **47/47** | 30 unregistered / 2.1 pt -> 0 / 0.1 pt - **PASS** |
| `76_devanagari_table` | 45/47 | **46/47** | 6 unregistered / 0.6 pt -> 2 / 0.1 pt - **PASS** |
| `07_stamp_over_table` | 37/42 | 37/42 | unchanged |
| `21_form_labels_x60_values_x300_txtpos` | 40/42 | 40/42 | unchanged |
| `365_recipe_card` | 41/42 | 41/42 | unchanged |
| `39_small_caps_letter_spacing` | 40/42 | 40/42 | unchanged |
| `78_mixed_english_devanagari_line` | 40/42 | 40/42 | unchanged |
| `brochure-3col-with-sidebar-box` | 41/42 | 41/42 | unchanged |
| `product-catalogue-code-left-price-right` | 41/42 | 41/42 | unchanged |

Two documents moved, seven did not, none got worse.

## THE TABLES ARE STALE FOR THIS CLASS, AGAIN

`benchmarks/gverify-lo` carries `76_devanagari_table` at **39/47** and
`78_mixed_english_devanagari_line` at **36/42** with `47_margins` passing. A pristine HEAD build
scores **45/47** and **40/42**, and 78's `47_margins` **fails** on HEAD at 4 unregistered. Judge
nothing on this class against the committed table; build both sides and compare them.

## What the remaining failures are not

On the seven documents the patch does not move, the check's own **median error is already 0.1 pt** -
the margin itself is right - and what fails is the per-page **tail of unregistered runs**. That is a
different defect from this one and it is not the border. Do not re-aim this patch at them.

## To land it

    git apply tools/p2w-bench/patches/47-margins-cell-border-inset.patch
    bash tools/p2w-bench/build-engine.sh
    # a FULL corpus pass, because the gate refuses an unmeasured engine:
    git push                      # p2w.py builds from origin/main, not from your working tree
    python3 /scratch/work/p2w.py --force --budget 250     # repeat until docx and txt are complete
    python3 tools/p2w-bench/restamp_txt.py --run --force
    python3 tools/p2w-bench/regress.py --stamp
    python3 tools/p2w-bench/regress.py --check

Then measure `404_sudoku_grid` and `76_devanagari_table` in **Google** before the corpus pass: if
Google does not inset a cell's content by its border width, this patch is wrong for the user's
renderer even though it is right for the proxy. That is the one measurement this run could not take.
