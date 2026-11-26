# 18_displacement: a single-line cell is written shorter than its own row, and Google lays the cell

**27 Nov 2026, fixer. Engine `a4de7df896875a39`. Two documents taken from 41/42 to 42/42 in Google
by editing four characters of XML per document and nothing else.**

## The result first

| document | before (Google, this run) | probe | after (Google, this run) | full check set |
|---|---|---|---|---|
| `362_price_list_dense` | 41/42, `18_displacement`, 181 of 257 runs out | `w:before` 128 -> 160 | **42/42 PASS** | 42/42 |
| `16_right_aligned_amounts_txtpos` | 41/42, `18_displacement`, 7 of 64 runs out | `w:before` 152 -> 190 | **42/42 PASS** | 42/42 |

Both were measured twice: `dy.py` for the per-run picture, then `verify_google.py` over the whole
42-check set on the same export. The predictions were written to
`FINDINGS/PREDICTION-362.md` **before** each render was uploaded. Both were confirmed; one of the
two predicted mechanisms was wrong and is corrected below.

## The construct

Every one of these documents is a table. Each row declares its own height:

    <w:trHeight w:val="168" w:hRule="atLeast"/>        (8.4 pt)

and each cell inside it declares a paragraph height that is **not** that number:

    <w:spacing w:before="128" w:after="0" w:line="8" w:lineRule="exact"/>    (136 tw = 6.8 pt)

| document | rows | `w:trHeight` | `w:before + w:line` | short by |
|---|---|---|---|---|
| `362_price_list_dense` | 29 | 168 tw (8.4 pt) | 136 tw (6.8 pt) | **32 tw (1.60 pt)** |
| `16_right_aligned_amounts_txtpos` | 13 | 380 tw (19.0 pt) | 342 tw (17.1 pt) | **38 tw (1.90 pt)** |
| `36_embedded_subset_font` | 7 | 400 tw (20.0 pt) | 323 tw (16.15 pt) | **77 tw (3.85 pt)** |

Google lays the **cell's** height, not `w:trHeight`. The repo already knew trHeight is a floor it
does not honour (`FINDINGS/18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-`), but drew the opposite
conclusion from it: if trHeight is ignored, the cell content is the row, so a cell written 32 tw
short of its row makes every row 1.6 pt short. Setting the cell to the row's own height makes the
page land.

## Two different symptoms, one arithmetic

This is the part the prediction got wrong, and it matters for the next run.

- **`362` is the accumulating case.** dy was a line: `-6.19 - 0.01475*y`, rms 0.51. After the probe:
  `+0.69 - 0.00017*y`, rms 0.28 - the slope fell 87x, span 6.81 -> 4.04 pt, **n_out 181 -> 0**. 27
  rows x 0.25 pt is the 6.81 pt the page had drifted.
- **`16_right_aligned` is an offset case, not a drift.** The prediction said "accumulating drift";
  the measurement says otherwise. The slope barely moved (`-0.00681` -> `-0.00585`); what moved was
  the intercept (`-2.48` -> `-1.29`). The table sat 1.9 pt high as a block, which put 7 of 64 runs
  outside a 3.15 pt tolerance; centring it put **n_out 7 -> 0**.

So the same 32-77 tw deficit produces a ramp when the rows are the whole page and a rigid offset when
the table is one block on it. A fix must be judged on **n_out**, not on whether the slope fell.

## What the engine does now, and why it is not already this

`DocxWriter.java:6480` computes the cell's line height:

    int cellLineHere = contentTwHere > 0 ? contentTwHere : 200;

and `:6508` picks it for a single-line cell:

    int baseLineTw = rowParts > 1 ? naturalLineHere : cellLineHere;

The intent in the comment at `:6326-6340` is exactly the probe - *"a cell that holds ONE line keeps
the pitch as its line height"* - but on `362` the written line is **8 tw (0.4 pt)**, not the row's
168 tw, and `contentTwHere` is evidently 8, not the pitch. That is the bug: the single-line branch
is chosen and then fills the line from the wrong quantity, so the row's own height never reaches the
cell.

**The known breaker, and why the rule must be scoped.** The comment records that setting the line to
the row's whole pitch "breaks a different one: a cell the page drew on TWO lines is charged the pitch
twice and the row doubles. That is `402_calendar_month_grid`, whose six-week grid arrived as nine
rows". `402` is in the same one-away list as these two. So the rule is:

> For a row whose **every** cell holds exactly one line, the cell paragraph's
> `w:before + w:line` must equal that row's `w:trHeight`. For a row with any multi-line cell, nothing
> changes.

`402_calendar_month_grid` (trHeight 1240, cells summing to 335) is the document that proves the scope
is needed, and it is the first thing to measure after the change.

## What is NOT proved

- **The engine has not been changed.** The probe is a hand-edited `.docx` for two documents. Landing
  this is a corpus-wide engine change and needs the 212-document table re-measured on the new engine
  before the gate will take it. That pass was not run this slot.
- **`36_embedded_subset_font`** shares the construct (77 tw short) and was not probed. It is the third
  one-away document this rule should clear, and the cheapest next test.
- **`31_times_body_arial_headings` is NOT this construct** - it has no table at all. Its dy is
  `+2.79 + 0.00291*y`, rms 0.40, n_out 4 against a budget of 2. It is flow text with a pitch error
  ~0.05 pt a line, and it needs a different fix.
- **`itr-computation-with-slab-table`** (42.33 share@5) has multi-line cells (trHeight 351, cells 1 and
  217) and is not addressed by this rule.

## Reproduce

    python3 tools/p2w-bench/dy.py corpus/<doc>.pdf <google-export>.pdf
    python3 tools/p2w-bench/verify_google.py corpus/<doc>.pdf <google-export>.pdf

The two probe exports are kept at `/scratch/work/p2w/gverify/gd/362_probe_before160.pdf` and
`16_probe_before380.pdf` for this slot only; the Google Docs themselves were deleted, as the rule
requires.
