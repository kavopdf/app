# `18_displacement`: the spacer-gap model is REFUTED at this engine; the drift is the lead

**28 Nov 2026 · research agent, reported by the fixer · engine `a05b20eb05fe0fc8` · MEASURED**

The corpus brief carried a measured claim: `shift = 0.961 * gap - 0.58 pt`, r = 0.975, and the obvious
inversion — ask for `G = (D + 0.58) / 0.961` — was proposed as the general rule that would pay down the
46.6-document leverage of `18_displacement`. **It does not hold, and the correction is worth zero
documents.** Do not spend a run on it.

## The claim was taken on an engine that no longer exists

The fit is in `FINDINGS/DOCS-ROOT-CAUSES-24NOV.md:609`, at engine `b7699196`. The tree at this
measurement is `a05b20eb05fe0fc8`. Re-taken here, on `403_crossword_puzzle` — the one document that fails
`18_displacement` **alone** — five Google exports differing only in one `w:spacing`, n = 3 gap values,
27 matched runs each:

| leg | measured | claim |
|:--|:--|:--|
| exact-line spacer | `position = 346.12 + 0.2288 * gap`, r = 1.0000, max residual **0.002 pt** | `0.961` |
| | `shift = 0.000 + 0.7712 * gap` | `-0.58 + 0.961 * gap` |

**Google delivers 22.9 % of an exact line height, not 3.9 %** — a factor of 5.9. At gap 58.15 pt the claim
predicts a 55.3 pt shortfall; measured 44.84. `w:before` in the same file delivers **1.003**.

| leg | measured |
|:--|:--|
| page-break `w:before` | page 0 tracks the ask **1:1** exactly (−31.35 pt ask → −31.35 pt move) |
| | pages 1–4 drop **−59.03 pt at all three values** (30.0 / 61.35 / 64.45 pt): slope **0.000** |

The page-break leg is **binary, so it is not invertible.** It needs a construct change — a carrier Google
does not drop — not a constant.

## What the correction actually did

| | before | after |
|:--|--:|--:|
| `w:line` emitted | 350 tw | 376 tw |
| `ACROSS` y | 390.78 | 391.07 (+0.29 pt) |
| `18_displacement` med_dy | −7.7 | −7.5 |
| verdict | 41/42, fails | **41/42, fails** |

0.29 pt of movement against a 10.6 pt worst error and a 4.5 pt tolerance.

## The lead, and it is a different mechanism

Per-run fit on the unmodified document:

    page 0: n=27  med=-9.58  min=-12.24  max=-0.64  span=11.60
    FIT dy = -8.44 - 0.02703*y   rms_resid = 2.93 pt

**The displacement accumulates up the page** — −0.64 pt at the top, −12.24 pt at the bottom, about 2.7 %
of page height. That is not one gap. It is the `w:lineRule="exact"` line box clipping one line at a time
(`SETTLED.md:497`, "Every document's text is clipped at the bottom"), which no spacer constant reaches.

Carrying the whole 58.15 pt gap in `w:before` — the property Google honours 1:1, the strongest version of
the gap fix — moved `med_dy` from **−7.7 to +3.1** and **still fails** (`worst_dy` 5.9). The gap error is
gone; the drift is not.

## How many documents become CLEAN: 0

| evidence | number |
|---|---|
| documents with any empty-spacer exact line height > 6 pt | **27 of 214** |
| of the 18 that fail `18_displacement` alone, documents carrying that lever | **1 of 18** |
| documents failing `18_displacement` that are single-page (no page-break leg) | **90 of 108** |

**The leverage ledger and the store disagree and this run did not reconcile them.**
`classpick.py --leverage` prices `18_displacement` at **46.6 CLEAN documents**; the `gverify` store has
**108 documents failing it, 18 of them alone**. Both cannot be right about the same population, and a
future run should reconcile them before trusting either — a 46.6 that is really 18 changes which class is
worth a slot.

## Where to go next, in order

1. **`w:lineRule="exact"` drift.** On 213 of 213 documents. The engine already has a mode switch
   (`-Dp2w.lineRule=exact|autoflow|auto`, `DocxWriter.java:136-145`) and its own comment records that
   `auto` was measured on the 211-document corpus as "a −3.1 pt median shift of the first line of every
   page and a −1.9 pt median on the lines below it, which is what 18_displacement was reading". That is
   the same magnitude as the drift above and it was **never taken to a verdict**. Test it on
   `403_crossword_puzzle` with a per-run fit, not a median: the question is whether the *slope* goes to
   zero, not whether the median moves.
2. **The page-break drop** — 18 multi-page documents, a real 59 pt error, binary, needs a construct
   Google does not drop.
3. **Do not re-derive the spacer constant.** It is measured, it is small, and it reaches one document.

## What would prove this wrong

A within-document slope near 0.96 on the exact-line leg; a continuation-page drop that scales with
`w:before`; one document going 41/42 → 42/42 under the correction; or a corpus-wide `gverify` on the
patched engine showing a net improvement.

## Residue

The agent published six synthetic probe `.docx` to a public branch `probe/18-displacement-28nov` on
`kavopdf/app` to get them into Drive, and did not delete it — the brief forbids deleting a branch. It is
recorded here and in `BLOCKERS.md` for whoever owns it. **Nothing else was left behind**: all nine probe
Google Docs were deleted and verified gone, and the store files the agent touched were restored to their
committed bytes.
