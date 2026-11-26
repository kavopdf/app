# `60_text_column_right_edge` — 61 store-failing documents re-measured on the current engine

**27 Nov 2026 · agent B, read-only, deployed by the 02:19 fixer run · engine `a4d8fca469bba636`**

> **READ THE LAST SECTION FIRST.** The LibreOffice proxy measures 46 of these 61 documents as
> passing; Google's own store, re-measured within two hours, fails **all 61**. The 46 is the proxy
> being blind, not the class being fixed. The class is worth 61, and only `gverify` can judge it.

Extends `60-text-column-right-edge-ROOTCAUSE-2110-agentA.md` (26 Nov), which established the
mechanism (M1: the right edge is the resolved face's advance, i.e. font substitution). This file
does not re-argue the mechanism. It supplies the measurement that file said it could not make:
**the check run on all 61 store-failing documents against the current engine's own output.**

## What was measured

- The check's arithmetic copied verbatim from `tools/p2w-bench/verify_google.py:2646-2790`
  (`BAND=0.06`, `RIGHT_OVERRUN=6.0`, `RIGHT_UNDERRUN=8.0`, `COL_MIN_LINES=3`,
  `COL_MIN_SHARE=0.05`, `SLACK_CAP=40.0`, `page_lines` / `columns` / `edge` unchanged).
- **Source PDF vs the LibreOffice render of the `.docx` this engine emitted.** This is the
  proxy, not Google. Every number below is a proxy measurement.
- 61 documents that carry `60` in `failed` in `benchmarks/gverify/*.json`, plus **8 controls**
  taken from the stamp documents (`01_stamp_rotated_15deg_upright` … `09_stamp_font_not_embedded`).

## The controls pass, so the harness is calibrated

**8 of 8 controls pass** — every `01`–`09_stamp_*` document measures inside tolerance. A harness
that had drifted would fail controls too.

## The result: 46 of the 61 no longer fail in the proxy

| | documents |
|:--|:--|
| store-failing documents re-measured | 61 |
| pass the edge test in the LibreOffice proxy | **46** |
| still fail | **15** (9 over, 6 under) |

Split by the engine stamp recorded on the store row:

| store engine stamp | rows | now pass in proxy |
|:--|:--|:--|
| `025fe9deda5ac7b1` (older) | 41 | 29 |
| `a4d8fca469bba636` (**current**) | 20 | **17** |

**The 20 rows measured on the current engine are the load-bearing ones.** They are not stale: the
document was scored by Google on the engine in this tree, and on that same output the LibreOffice
proxy now measures the column edge as correct on 17 of them.

## The 15 that still fail — no constant

| document | page | left | src | ren | delta | tolerance | |
|:--|--:|--:|--:|--:|--:|--:|:--|
| 323_credit_card_statement | 1 | 28.00 | 549.12 | 357.70 | **-191.42** | 27.79 | UNDER |
| 360_restaurant_menu | 1 | 52.00 | 144.12 | 285.70 | **+141.58** | 36.77 | OVER |
| 360_restaurant_menu | 1 | 329.64 | 424.06 | 563.30 | +139.24 | 31.49 | OVER |
| 79_inr_indian_digit_grouping_table | 1 | 132.27 | 289.97 | 149.70 | -140.27 | 23.72 | UNDER |
| purchase-order | 1 | 428.30 | 449.71 | 552.68 | +102.98 | 23.51 | OVER |
| 77_arabic_rtl_document | 1 | 322.60 | 334.02 | 428.90 | +94.88 | 17.42 | OVER |
| gst-invoice-horizontal-rules-only | 1 | 426.22 | 549.92 | 456.46 | -93.46 | 33.19 | UNDER |
| balance-sheet-and-profit-loss | 2 | 446.70 | 552.77 | 464.76 | -88.00 | 28.02 | UNDER |
| delivery-challan | 1 | 422.76 | 473.53 | 550.94 | +77.41 | 27.61 | OVER |
| 38_faux_bold_italic_synthesised | 1 | 55.41 | 511.58 | 568.37 | +56.79 | 31.66 | OVER |
| text-held-twice-shadow-text | 1 | 45.35 | 551.99 | 589.24 | +37.25 | 28.04 | OVER |
| question-paper-marks-right-margin | 1 | 56.69 | 468.16 | 504.10 | +35.94 | 12.75 | OVER |
| 318_court_summons_form | 1 | 446.47 | 460.09 | 495.58 | +35.48 | 15.54 | OVER |
| one-page-rotated-180-degrees | 2 | 366.88 | 513.28 | 477.06 | -36.22 | 24.10 | UNDER |
| 28_value_overflows_cell_txtpos | 1 | 86.00 | 404.82 | 433.16 | +28.34 | 27.69 | OVER |
| boq-tender-bill-of-quantities | 1 | 39.69 | 472.29 | 451.54 | -20.74 | 13.78 | UNDER |

**Deltas run from -191.42 to +141.58, in both signs.** There is no shared constant, so there is
no single edge value to write that would fix this class. That is consistent with M1: the delta is
the difference between the advance of the face the PDF used and the advance of the face the
renderer resolved, which varies with the string.

## The independent check — and it REFUTES the reading above

The 46 is a proxy number and I said so, so I went and tested it against the one source that is not
my own harness: the Google verdict store, which the `:20 gverify` cron had re-measured.

**All 61 store rows were re-measured through Google within the two hours before this was written
(mtime age < 2 h on every one of the 61).** Against those fresh rows:

| | Google | LibreOffice proxy |
|:--|:--|:--|
| fails `60` | **61 of 61** | 15 of 61 |
| passes `60` | 0 of 61 | 46 of 61 |

- Every one of my **15** proxy failures is a Google failure. **15 of 15 agree** — so the proxy is
  not mis-measuring; where it sees a fault, the fault is real.
- Every one of my **46** proxy passes is a Google **failure**. **46 of 46 disagree.**

**So the "46 already pass" reading is wrong, and I withdraw it.** The class is not smaller than
`classpick.py` says; it is 61 documents by Google's own fresh count, and the LibreOffice proxy is
blind to 46 of them — 75% of the class.

## What this actually changes for the next run

1. **`60_text_column_right_edge` cannot be worked with `regress.py` or `verify-change.py` at all.**
   Those instruments see 15 of the 61. A change that closes the other 46 will measure **INERT** in
   the LibreOffice proxy, and a run that trusts that verdict will throw away a working fix — the
   exact failure the brief records for the 19 Nov run at 46 of 213. The only instrument that can
   judge this class is `gverify`.
2. **This is the charter's non-negotiable #1, quantified on one class:** LibreOffice hides 75% of
   it. The 46 documents are not "already fixed"; they are faults the proxy cannot see.
3. **Do not re-derive M1.** Read `60-text-column-right-edge-ROOTCAUSE-2110-agentA.md`; the
   mechanism is font substitution and it is already established. The 46 Google-only failures are
   the face-advance cases where LibreOffice's substitution happens to land inside the column.
4. **A workable plan, given (1):** make the change that M1 implies, render only the 61 with
   `gverify` (not 213), and accept the commit on `regress.py --check` showing nothing worse in the
   proxy — because the proxy cannot see the improvement either. State that in the attempt.

## What would prove this wrong

- A `gverify` run on the same 20 current-engine documents that reproduces the store's `60`
  failure on the same `.docx` that the LibreOffice proxy measures as passing. That would mean the
  proxy and Google disagree on the same file — which is the claim — but it would move the count
  from 17 to 20 and change the class's worth, not the mechanism.
- Finding a document in the 46 where the *source* column edge was mis-read (the `columns` /
  `edge` clustering picking the wrong cluster). I did not re-derive `edge()` per document, so this
  is the weakest point in the 46.

## What I did not do

- **No Google measurement of my own.** All 69 harness measurements are source PDF vs LibreOffice
  render. The Google side in the final section is the `gverify` store's rows, read as data — it is
  not a measurement I made.
- **No engine change.** This is a diagnosis; the parent run owns every engine change.
- The `46` is a proxy count, not a claim that 46 documents are clean in Google Docs.
