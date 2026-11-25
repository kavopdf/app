# `18_displacement` rank 1 is FALSIFIED in Google — the declared row box on the pixel grid moves nothing

**25 Nov 2026 · fixer run · repo `kavopdf/app` @ `a4ae24e2` · Google Docs, not LibreOffice.**

`FINDINGS/18-displacement-B-GROUP-CENSUS-25NOV-relay.md` §4 ranks "Google lays a table row's vertical
pitch on whole 0.75 pt CSS pixels while the engine declares the source pitch in twips" as the primary
mechanism for the ten group-B documents, and predicts a fall in `med_dy` / `worst_dy` on all ten.
That prediction was tested on the document with the largest recorded ramp and it is wrong.

## What was changed

`DocxWriter.table()`, the content-table writer. Its rows are written
`<w:trHeight w:val="H" w:hRule="atLeast"/>` where `H` is the page's own pitch in twips. The change
rounded the row's **border box** (`H` + the drawn horizontal rule) UP to a whole multiple of 15 twips
(0.75 pt) and declared `H = snapped − rule`. Ceiling only, so no cell can be clipped; behind one
constant (`ROW_BOX_SNAP_TW = 15`) that makes the change an identity at 0.

Predicted before running: `320_balance_sheet_statutory` `med_dy` +8.2 → +2.5, `worst_dy` 19.4 → 6.5
(the census's own row-snap model, §3.4).

## The declaration moved exactly as designed — verified from the .docx, not from the tool

`w:trHeight` in `word/document.xml`, before → after:

| document | before (twips) | after (twips) | declared box + rule | in pt |
|:--|--:|--:|--:|--:|
| `320_balance_sheet_statutory` | 280 ×16, 260 ×5 | 292 ×16, 262 ×5 | 300, 270 | **15.00, 13.50** |
| `36_embedded_subset_font` | 400 ×7 | 405 ×7 | 405 | **20.25** |

300 twips is 15.00 pt = exactly 20 CSS pixels, and 15.00 pt is the pitch the census *recorded Google
laying* on this document. The engine now declares precisely the number Google was observed to use.
20.25 pt is within 0.05 pt of the 20.2 pt recorded for `36_embedded_subset_font`.

## The measurement — Google, both sides

Render path: upload the .docx → copy as `application/vnd.google-apps.document` → export as PDF
(`grender.py`'s three steps, run through the Drive API) → `verify_google.py` against the corpus PDF.
Both renders are Google's own layout of a .docx that differs only in `w:trHeight`.

| `320_balance_sheet_statutory` | passed | `18_displacement` | `med_dy` | `worst_dy` | runs matched |
|:--|--:|:--|--:|--:|--:|
| before (engine @ `a4ae24e2`) | 41/42 | FAIL | **+8.2** | **19.4** | 73 |
| after (row box on the 0.75 pt grid) | 41/42 | FAIL | **+8.2** | **18.7** | 73 |

`med_dy` is unchanged to the tenth of a point. `worst_dy` moves by 0.7 pt — the size of one snap on one
row, not the collapse the model predicted. No check changed state.

## What that means

The row box is not the lever. `w:trHeight … hRule="atLeast"` is a *floor*: Google lays
`max(trHeight, cell content + rule)`, and here the cell content already exceeds the declared height, so
raising the declaration by up to 0.7 pt per row is absorbed and the laid pitch does not change. The
pitch Google actually uses is computed from the cell's own lines — which is the census's **rank 2**
hypothesis ("the same pixel snap applied per cell line advance"), the one it could not separate from
rank 1 on ten points of evidence.

This also satisfies the census's own stated falsifier for rank 1: *"a .docx in which a table row's
declared height is already a whole multiple of 0.75 pt … yet which still fails `18_displacement` in
Google with a ramp — that would mean the pitch is not the lever."* That document now exists, and it
does.

## What the next run should do instead

Do not re-derive the row snap; it is measured and dead. The remaining candidate is the **per-line term
inside a cell**: every cell paragraph is written `w:line="…" w:lineRule="exact"`. Google must be laying
those lines at its own advance rather than the declared one, because the declared one is already the
source pitch and the row is already exactly as tall as its lines. The discriminating probe is a cell
whose declared `w:line` is already a whole multiple of 15 twips: if Google still drifts, `w:lineRule`
itself is not honoured on import, and the lever is not a number at all.

## Cost and honesty

Two Google renders (one document, before and after), 0 committed engine changes. The patch is reverted,
not left in the tree: it moves nothing in Google and adds up to 0.7 pt per row in LibreOffice, which is
regression risk for no gain.
