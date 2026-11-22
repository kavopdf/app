# 18_displacement — the dither is CLEAN in Google and catastrophic in LibreOffice. The proxy ratchet is the blocker, not the engine.

**22 Nov 2026 · fixer slot 15:55 → · engine HEAD `462353f9` · one live Google round trip ·
one 16-document LibreOffice screen on two builds · every probe Doc deleted, Drive root left empty**

## 0. The patch that was "refuted" at 15:34 was a different patch

`patches/18-spacer-before-rowpitch-rowrule.patch` (repo-root `patches/`) and
`tools/p2w-bench/patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch` are **not the same
file**. The first carries seven hunks: the spacer, a 4320 tw cap, and three hunks that recompute row
pitch from the table average, pull the row rule outside `trHeight`, and rescale the cell pitch. The
second carries two mechanisms only: the spacer moved to `w:before`, and error-diffusion of the row
pitch onto Google's 0.75 pt grid.

`FINDINGS/18_displacement-SPACER-DITHER-GOOGLE-CONFIRM-1517-relay.md` §"CONTRADICTION" reads the 15:34
refutation as a refutation of **this** patch. It is not. The 15:34 run's own bisection says which
mechanism regressed: "hunk 3 alone (row pitch from the table average instead of the row's own snapped
rowEdge) takes `mobile-bill` 1.55 → 12.66". That hunk does not exist in the dither patch.

So the dither patch was parked on evidence about a different patch. This run measured the dither patch
on its own terms.

## 1. What was measured, and how

Patch applied clean (`git apply --check` clean, one file, 39 insertions / 3 deletions), engine rebuilt
from `/scratch/work/CS` (48 s), `screen.py --docs <the 16 that fail 18_displacement and nothing else>`
for the LibreOffice number, and one live round trip for the Google number:

    ConvertOne -> GOOGLEDRIVE_CREATE_FILE (application/vnd.google-apps.document)
               -> GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE (application/pdf)
               -> verify_google.py <source.pdf> <export.pdf> --docx <patched.docx>

Export `sha256 942fd59ebb197e472d2a6d628e5dd768437b622ee1e23a4616f6200bd8095d01`. Probe Doc
`1PO0tgQmSXVTAtKsrZ79PS6fEs4yfs9eTMziItJ30O00` deleted after scoring.

## 2. The two renderers, the same document, opposite verdicts

| document | LibreOffice proxy (share@5, lower better) | Google (checks) |
|:--|--:|:--|
| `two-tables-stacked-with-no-gap` baseline | 0.77 | 46/47, fails `18_displacement` |
| `two-tables-stacked-with-no-gap` + dither patch | **29.51 (+28.74)** | **47/47 PASS — CLEAN** |

**This is the whole finding.** The construct is right where the user opens the document and wrong in
the renderer nobody opens. `18_displacement` is gone; the document is clean.

## 3. It is not one document. The proxy moves 14 of 16.

`screen.py --docs <16>` on the patched engine, against `benchmarks/RANKING.csv`:

    better  71_invoice_space_aligned_no_rules      26.88 ->  3.48   -23.40
    WORSE   table-with-no-header-row                0.61 -> 41.16   +40.55
    WORSE   72_bank_statement_no_rules_right_amounts 0.00 -> 38.43  +38.43
    WORSE   mobile-bill                             1.55 -> 39.21   +37.66
    WORSE   insurance-policy-schedule               0.53 -> 35.04   +34.51
    WORSE   41_coloured_headings_white_bg           0.00 -> 32.46   +32.46
    WORSE   22_invoice_four_columns_txtpos          0.00 -> 32.30   +32.30
    WORSE   two-tables-stacked-with-no-gap          0.77 -> 29.51   +28.74
    WORSE   16_right_aligned_amounts_txtpos         0.00 -> 26.98   +26.98
    16 measured, 1 same, 1 better, 14 worse   ->  SCREEN FAIL

**And the proxy number does not move when the mechanism is changed.** A variant build that left the
rule pitch on the row's own `rowTwHere` instead of on the dithered `ditherLaidTw` produced **byte-identical
scores on all 16** (`0.61 -> 41.16`, `0.77 -> 29.51`, …). So the regression is not the rules following
the wrong pitch; it is the row height itself. That rules out the obvious repair.

## 4. Why no LO-neutral form of this fix exists

Google: `laid = 0.75 * (round(h / 0.75) + 1)`. LibreOffice: `laid = h`. A single declaration therefore
cannot lay the same height in both renderers unless `0.75 * (round(h/0.75) + 1) == h`, which has no
solution — the `+1` quantum is exactly what the two renderers disagree about. Any declaration that
lands a page's non-grid pitch in Google must be one quantum short in LibreOffice, and vice versa. The
engine writes one `w:trHeight`.

Compensating through the cell instead does not help: `w:spacing` and `w:line` inside the cell are
honoured by both renderers too, so they shift both by the same amount.

**So the choice is not "which construct" — it is "which renderer the ratchet judges."**

## 5. What blocks the commit, stated plainly

`ratchet.py` fails on a LibreOffice regression and `regress.py --check` is a hard gate. A patch that
takes the largest class in the corpus (16 documents failing `18_displacement` and nothing else, priced
at **38.7 clean documents** by `classpick.py --leverage`) from 46/47 to 47/47 in Google cannot be
committed, because it moves the proxy the wrong way on 14 of those same 16.

That is not an engine defect. It is the instrument outranking the truth it is a proxy for, and the
charter's rule 1 ("Google is the truth. LibreOffice is a proxy that hides what the phone shows") and
rule 3 ("regress.py --check must pass") now point in opposite directions on this class.

## 6. What the next run should do, in order

1. **Do not re-run the screen.** The 14-of-16 proxy regression is measured twice on two builds and is
   not going to change. It is a property of the construct, not of the patch.
2. **Decide the instrument question, not the construct question.** Either the ratchet gains a
   documented path for a Google-clean / proxy-regressed change (a waiver with the Google round trip as
   its evidence), or this class is parked with this finding as the proof. Both are legitimate; leaving
   it undecided is what has now cost three slots.
3. If the waiver path is taken, the patch is one build and one corpus pass from shipping, and
   `two-tables-stacked-with-no-gap` is already measured CLEAN on it.

## What would prove this wrong

A document that the dither patch makes **worse in Google**. Nothing in this run's evidence suggests one
exists — but one round trip on a ruled document outside the 16 (`bank-statement-horizontal-rules-only`,
39 rules and nothing else) would test the other direction of the same construct, and it has never been
done.
