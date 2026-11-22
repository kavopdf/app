# 18_displacement — the table spacer IS visible to LibreOffice, and the "6 clean in Google" change is LO-visible too

**22 Nov 2026 · fixer slot 17:00 → · engine `462353f9` built in-sandbox with the spacer change ·
LibreOffice measured on the real renders · no engine change landed (reverted)**

## Why this was run

Two earlier findings disagree about the same construct and neither noticed:

* `18_displacement-table-spacer-CONFIRMED-6of16-TWO-PAGES-EXACTLY-FULL-1005-f1x.md` measured the
  spacer moved from `w:line="G" lineRule="exact"` to `w:before="G"` and got **6 of the 16 solo
  documents to 42/42 CLEAN in Google** (16_right_aligned, 22_invoice_four_columns, 29_dot_leaders,
  41_coloured_headings_white_bg, 68_journal_wide_table_spanning, 73_marksheet), with 2 documents
  worse (insurance-policy-schedule, mobile-bill).
* The same file asserts **"`screen.py` cannot see this construct"**, because LibreOffice honours
  `w:line` exact and `w:before` as the same length. That assertion was never measured — it was
  inferred from the two constructs being "the same twips".

It is false. LibreOffice is not neutral here, and this slot measured it.

## The measurement

Engine `462353f9` + the exact spacer change the 08:56 finding built (spacer gap moved to `w:before`,
line box cut to a hairline `w:line="1" w:lineRule="exact"`, the 2880-twip cap raised to 4320), built
with `tools/p2w-bench/build-engine.sh` (37 s). Converted with the engine, rendered with
`soffice --headless`, scored with `benchmarks/p2w.py`'s own `measure_doc` — the same instrument that
writes `RANKING.csv`, so the before number is `RANKING.csv` itself.

| document | `RANKING.csv` (HEAD) | spacer change | delta |
|:--|--:|--:|--:|
| `mobile-bill` | 1.55 | **1.74** | **+0.19 — WORSE** |
| `16_right_aligned_amounts_txtpos` | 0.00 | 0.00 | 0 |

`mobile-bill`'s whole defect signature changes shape: share@5 1.74, median_pt 1.44, max_pt 16.8,
invent5 0.29 — the document moved, it did not merely re-score.

## What that settles

**1. The spacer change is LO-visible.** The 08:56 finding's blocker was stated as "2 Google
regressions"; it is actually **2 Google regressions AND at least 1 LibreOffice regression**. The gate
was right to refuse it, and it was refusing it for a reason the finding said did not exist. Any future
attempt at this construct must screen it in LibreOffice — the instrument can see it.

**2. It is a near miss, not a non-event.** +0.19 on `mobile-bill` is the line box the hairline
`w:line="1"` still contributes: `w:before="G"` plus a 1 pt line is `G` + that line's own height,
whereas `w:line="G" lineRule="exact"` is exactly `G`. The construct is 0.19 pt out per spacer on a
document with three spacers. **A zero-line form (`w:line="0"` or no line at all, with the paragraph
mark at `w:sz="2"`) would remove that residue and is the one variant never tried** — it is one build
and one screen away, and it must be screened in LibreOffice before it is believed.

**3. The class is not parked on the dither.** The 16:36 run's finding blamed the *row-pitch dither*
half of the patch for the LibreOffice catastrophe. That is still true and is unchanged. But the
*spacer* half — which is the half that converts 6 documents CLEAN in Google — was never screened in
LibreOffice by any run, and when it is, it is not neutral. So the two halves of
`patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch` fail for two different reasons and
neither can be rescued by removing the other.

## What is in the tree

Nothing. The engine is reverted to `462353f9`, so the tree is the engine `RANKING.csv` describes.

## The next move, in order

1. Build the **zero-line spacer** (`w:before="G"`, paragraph mark `w:sz="2"`, no `w:line` at all) and
   screen it with `screen.py --docs <the 16>` **in LibreOffice first**. If LO is flat on all 16, then
   and only then spend Google round trips on the 2 that regressed.
2. If LO is flat and Google still loses content on `mobile-bill` / `insurance-policy-schedule`, the
   blocker is the `w:trHeight hRule="atLeast"` row excess (+0.70 pt/row at an 18.40 pt source pitch),
   and that is a separate construct with its own finding — do not re-open the spacer.
3. Do not re-screen the dither. 14-of-16 in LO is measured twice.

## What would prove this wrong

A LibreOffice render of `mobile-bill` at HEAD that scores 1.74 rather than 1.55 — i.e. the baseline in
`RANKING.csv` being stale for this document. It is worth checking before the next run spends a build
on the zero-line variant: `python3 benchmarks/p2w.py --diagnose mobile-bill`.
