# 18_displacement · THE ROW HEIGHT IS THE LEVER IN GOOGLE, AND IT IS NOT SET TO THE SOURCE PITCH

**25 Nov 2026 · measured in Google's own renderer · 9 arms on `320_balance_sheet_statutory`**

> Rank 1 (w:trHeight snapped to a 0.75 pt grid, `hRule="atLeast"`) was falsified on 25 Nov.
> Rank 2 (the cell's own line box) is now falsified as the *row pitch* lever too — but the probe that
> falsified it found the lever underneath: **the declared `w:trHeight` itself, with `hRule="exact"`,
> moves Google's laid row pitch 1:1 above the cell-content floor, and the engine declares the source
> pitch, which sits exactly ON that floor.** Every row then lays 1.00 pt too tall.

## The nine arms

Every arm is the engine's own `.docx` for this document, edited in XML only, uploaded to Drive,
converted to a Google Doc, exported to PDF and scored with `verify_google.py` against the corpus
original. One render each; `runs_matched` is 73 on all nine, so all nine are the same 73 text runs.

| arm | what changed in the XML | Google passed | `18_displacement` med_dy | worst_dy | laid row pitch (pt) |
|:--|:--|--:|--:|--:|:--|
| BASE | nothing (engine as committed) | 46/47 | **+8.2** | **19.4** | 15.00 ×16, then 13/14 |
| G15_exact | cell `w:line` snapped to whole multiples of 15 twips | 46/47 | +8.2 | 19.4 | 15.00 ×16 |
| X195_exact | whole advance into `w:line` (195/180/15 tw), `w:before=0`, rule `exact` | 45/47 | **+4.6** | 19.4 | 15.00 ×16 |
| A195_atLeast | same 195-twip box, rule `atLeast` (only the keyword differs) | 45/47 | **+6.0** | 19.4 | 15.00 ×16 |
| E280_exact | `w:trHeight` 280/260, `hRule="exact"` | 46/47 | +8.2 | 19.4 | 15.00 ×16 |
| E300_exact | `w:trHeight` 300, `hRule="exact"` | 44/47 | +13.2 | 51.7 | 15/16 |
| E280_exact_lin280 | `hRule="exact"` 280 + cell `w:line=280`, `w:before=0` | 45/47 | −42.1 | 374.3 | 15.00 ×16 |
| **E260_exact** | **`w:trHeight` 260, `hRule="exact"`** | 45/47 | **−4.8** | **8.9** | 13/14 |
| E240_exact | `w:trHeight` 240, `hRule="exact"` | 45/47 | −10.8 | 43.8 | 12/13 |

`laid row pitch` is measured off the horizontal rules in the exported PDF itself — a direct measurement
of where Google put the row boundaries, not an inference from text displacement.

## What this settles, and what it kills

**1. `w:lineRule` IS honoured on import.** `X195_exact` and `A195_atLeast` are the same 195-twip box and
differ only in the keyword: +4.6 against +6.0 on the same 73 runs. The last run left "if they are
identical, `w:lineRule` is not honoured and the lever is not a number" as its discriminator. They are
not identical. **The keyword is honoured and the cell line box is a lever** — a small one, 3.6 pt of
median.

**2. The cell line box does not move the row pitch.** All four cell arms lay 15.00 pt on all 16 rows of
table 0. Changing where text sits inside a cell moves the text, not the rule under it. So rank 2 is
falsified as the *row pitch* mechanism, and the 3.6 pt it does buy is a different (real) effect.

**3. `hRule="atLeast"` vs `"exact"` is invisible at 280 and decisive away from it.** `E280_exact` is
bit-for-bit the base result (+8.2 / 19.4), which is why the last run's 280→300 `atLeast` probe moved
nothing. At 300 `exact` it moves a great deal (+13.2 / 51.7), and at 260 `exact` it moves the other way
(−4.8 / **8.9**, worst more than halved).

**4. The mechanism, stated as a law.** Google lays a row at `max(declared, content)` where content is
about 15.00 pt on these cells, and the engine declares 14.00 pt — just below the floor. Below the floor
the declaration is discarded; above it, it is obeyed 1:1 (300 → 15/16, 260 → 13/14, 240 → 12/13). The
source pitch and the content floor coincide at 280 twips, so the engine gets the worst of both: the
floor wins, every row is 1.00 pt tall, and 16 rows accumulate ≈16 pt — against a `worst_dy` of 19.4.
The floor is the row's **cell content**, not the rule; `w:line` cannot lower it because the text is
taller than the line box the engine declares.

**5. The zero crossing is measurable and is not at 280.** med_dy crosses from +8.2 at 280 to −4.8 at
260, so the declaration that lays the source's 14.00 pt is near **267 twips** (13.35 pt), not 280.
`worst_dy` bottoms out at the same place (19.4 → 8.9 → 43.8).

## The next probe, in one line

Declare `w:trHeight` **268** and **272**, `hRule="exact"`, on the same document; expect `worst_dy` under
5 and `18_displacement` to clear on the arm whose laid pitch is exactly 14.00 — and if it does, the
engine change is one constant (`declared = source_pitch − (floor − source_pitch)`) behind one site, not
a per-class rule.

## Why nothing was landed

`E260_exact` is the only arm that improves both distances, and it is still not landable: it does not
clear `18_displacement`, and it picks up `25_invisible_text`. That check was found on 24 Nov to be
reading the paper rather than the text (a Google export opens with a page-sized white rectangle), so the
new failure is most likely the known-bad check and not this arm — **but it is unverified, and an
unverified regression is a regression.** A −20 twip shift on every table row would also have to be
measured across all 213 documents, and the corpus was still mid-build when the slot ended.

## What was ruled out

- `w:trHeight` + `hRule="atLeast"` as a *grid snap* (last run, and `E280_exact` here: 280 → 15.00).
- The cell line box as the row-pitch driver (all four cell arms lay 15.00).
- `w:lineRule` being ignored on import (X195 vs A195 differ).
- The measurement itself: BASE reproduces the recorded reference to the tenth (+8.2 / 19.4), so the
  instrument, the source PDF and the document are the same ones earlier runs measured.

## Provenance

Probe `.docx` files: `/scratch/output/E240_exact.docx`, `E260_exact.docx`, `E280_exact.docx`,
`E300_exact.docx`, `E280_exact_lin280.docx`, and the four cell arms returned by the subagent
(`base.docx`, `G15_exact.docx`, `X195_exact.docx`, `A195_atLeast.docx`). Google Docs were created in
`KavoPDF-Verify`, exported to PDF, and deleted after the measurement. Per-arm `verify_google.py` JSON
is in `/scratch/work/probe/res/`. Nothing in `app/` or `tools/engine-verify/` was changed by this probe.
