# `18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER` does not reproduce. Refuted in both renderers.

**Slot:** 22 Nov 14:58 IST fixer (claim held). **Engine:** `462353f9` (baseline), all measurements fresh on this sandbox.

## What I believed, from the handoff

`LAST-MESSAGE.md` (13:56) and `HANDOFF.json` carry-over both said: apply
`patches/18-spacer-before-rowpitch-rowrule.patch` (the handoff names it
`18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch`; the file on disk is the former), ratchet it,
and `two-tables-stacked-with-no-gap` goes **41/42 -> 42/42 PASS, n_out 55 -> 0**, median -4.66 -> +0.05.
The carry-over was explicit that this patch moves **every ruled table in the corpus** and that the gate
refused it unratcheted.

## What I measured

The patch applies clean. It has seven hunks and **four independent mechanisms**, so I bisected it rather
than accepting or rejecting it whole. Everything below is a fresh build (41-47 s) plus a fresh screen.

### LibreOffice proxy — `screen.py`, the same six documents at every step

| document | baseline | spacer only (h1-2) | spacer+rowpitch (h1-3) | full patch (h1-7) |
|:--|--:|--:|--:|--:|
| `insurance-policy-schedule` | 0.53 | 0.53 | 0.53 | **33.55** (+33.02) |
| `mobile-bill` | 1.55 | 1.55 | **12.66** (+11.11) | **36.90** (+35.35) |
| `table-with-no-header-row` | 0.61 | 0.61 | 0.61 | **36.40** (+35.79) |
| `two-tables-stacked-with-no-gap` | 0.77 | 0.77 | **3.29** (+2.52) | **30.02** (+29.25) |
| `product-catalogue-code-left-price-right` | 0.47 | 0.47 | 0.47 | 0.47 |
| `74_balance_sheet_indented_subitems` | 0.03 | 0.03 | 0.03 | 0.03 |

Baseline row reproduces `benchmarks/RANKING.csv` exactly (`6 measured, 6 same`), so the instrument is
sound and the regression is the patch's, not a stale table.

**The spacer half (hunks 1-2) is invisible to LibreOffice: 6 same, 0 better, 0 worse.** That is the
expected signature of a construct Google undercharges and LibreOffice honours - it is also why
`screen.py` can never judge this half, and why the last run had to spend Google round trips on it.

**The row/cell half (hunks 3-7) is what regresses.** Hunk 3 alone (row pitch: take the table's average
`rowTw` instead of the row's own `rowEdge` when they agree within 20 twips) takes `mobile-bill`
1.55 -> 12.66. Hunks 4-7 (row-rule subtraction from `w:trHeight`, one-pitch cell advance) add another
+24 on top.

### Google — the renderer of record, fresh round trips, engine `462353f9`

`GOOGLEDRIVE_CREATE_FILE(application/vnd.google-apps.document)` -> `GOOGLEDRIVE_DOWNLOAD_FILE(pdf)` ->
`verify_google.py --docx`.

| document | build | Google | vs baseline |
|:--|:--|:--|:--|
| `two-tables-stacked-with-no-gap` | baseline (`benchmarks/gverify/*.json`) | 46/47, fail `18_displacement` | - |
| `two-tables-stacked-with-no-gap` | spacer only | **46/47**, fail `18_displacement` | **no change** |
| `two-tables-stacked-with-no-gap` | **full patch** | **46/47**, fail `18_displacement` `{source: 0, render: 1}` | **no change** |
| `mobile-bill` | baseline | 46/47 | - |
| `mobile-bill` | spacer only | **43/47, `01_page_count` 1 -> 2** | **REGRESSION** |

## What is now true

1. **The 42/42 claim does not reproduce.** On the engine in the tree, the full patch leaves
   `two-tables-stacked-with-no-gap` at **46/47 with the same single failing check** it had at baseline.
   The number in the handoff was measured against an engine state that is not the one the patch applies
   to - the same failure mode `SETTLED.md` records for four commits after the baseline. `18_displacement`
   reports `{source: 0, render: 1}`: one page, and that page fails. Nothing moved.

2. **The spacer half is not free, and it is not neutral in Google.** `w:before` is charged 1:1
   (see the agent measurement below) where `w:line` was charged ~0.2156x, so moving a gap from one to the
   other **adds real height in Google**. On `mobile-bill` that surplus is enough to spill a full page:
   `01_page_count` 1 -> 2.

   **And the obvious explanation is WRONG - I checked it rather than shipping it.** `DocxWriter.java:5875`
   is `ctx.flowTw += spacerTw`, i.e. the engine already charges its own pagination model the DECLARED
   value, and `w:before` now renders exactly that declared value. **Model and render agree after the
   patch; they did not before** (the model over-charged by 4.6x, so the engine used to break pages
   EARLIER than Google needed). So this is not a pagination-model mismatch, and "fix `flowTw`" is not
   the lead.

   What the extra page actually says is the opposite, and it is more useful: **`mobile-bill` was only
   fitting on one page because Google was under-charging that gap by ~4.9 pt.** With the gap charged
   honestly the page no longer fits, so the document carries a real surplus somewhere else of at least
   that much. The only thing `flowTw` does not model is the spacer paragraph's own 0.1552 pt line box -
   two of those is 0.31 pt, nowhere near 4.9. That surplus is the open question and it is the lead.

3. **The row/cell half is a large LibreOffice regression** (+29 to +36 on four documents) and moves
   nothing in Google on the one document it was meant to fix. It cannot be kept under
   "no document gets worse".

## The one thing worth carrying forward

**`w:before` on a spacer paragraph is charged exactly `V/20` pt by Google, with no floor, no threshold,
no cap, and no scale factor for small values.** Measured over 25 values from 1 to 4320 twips, max residual
0.000000 pt, run present or absent. The spacer paragraph's own line box with `w:line=1 w:lineRule="exact"`
adds a constant **0.1552 pt**; with `w:line` absent it is 2.5873 pt. And `w:line` is confirmed to be read
as a multiple of 240 of the paragraph mark's own line height - `h = 1.1499 * s_eff * max(L/240, 0.06)`,
`s_eff` clamped to 2.25 pt for `w:sz=2` and `w:sz=4` - which is the **0.2156x** the 13:56 run measured.
Full curve, method and residuals: `18_displacement-WBEFORE-IS-1TO1-GOOGLE-1005-agentA.md`.

**So the residual on `mobile-bill` is not Google over-charging a small spacer, and it is not a
pagination-model mismatch either.** `w:before` is arithmetically right and `flowTw` already models it.
The extra page is a REAL surplus: the document only fitted before because Google was under-charging that
gap by ~4.9 pt, and the honest charge removes the slack. **The lead is to find that surplus** - and the
honest way to find it is to keep the spacer fix (it is a correctness fix, LibreOffice-neutral) and
measure `mobile-bill` page by page for what else is over-tall, not to reach for `flowTw`.

## What would prove this wrong

A build of `462353f9` + the full patch scoring `two-tables-stacked-with-no-gap` at 42/42 in Google. I ran
exactly that and got 46/47. If a later run gets 42/42, the difference is in the build, and the place to
look is whether `tools/p2w-bench/build-engine.sh` recompiled `DocxWriter` at all - check the `ENGINE`
fingerprint in `/scratch/work/p2w/screen-out/` changes with every build, as it did here
(`462353f9` -> `+186cbb083b` -> `+e7a895d2b6` -> `+bf1370a39e`).
