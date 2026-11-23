# 18_displacement — the LO proxy is NOT lying: the 30–36 is a real 1 pt-per-row compression in LibreOffice, verified twice

**Run:** 23 Nov 2026, 20:13 IST, agent A. **Bases:** HEAD `88d8eefc` (patch does not apply here — see §1)
and `462353f9`, the engine the 15:34 bisect measured, where it applies clean. Builds: `build-engine.sh`,
37–43 s each. Conversion: `ConvertOne`, one JVM per document. Every score below is a fresh measurement
on this pod; nothing is copied from `RANKING.csv`.

## 0. The question, and the answer in one line

The 16:12 finding says the proxy's 30–36 "is not the page's layout" because the patched `mobile-bill`
renders as one page with the same content. **Both of those observations are true and the inference is
false.** The page has the same content and the same page count and is still 20 pt out of place at the
bottom, because every ruled row in it is 1 pt shorter than the page drew. An independent line-position
reading of the same two PDFs, written for this run and sharing no code with `benchmarks/p2w.py`, agrees
with the repo's share@5 to within the difference between an ink count and a line count.

## 1. Which tree this patch can even be judged on

`patches/18-spacer-before-rowpitch-rowrule.patch` **does not apply at HEAD**:

    $ git apply --check patches/18-spacer-before-rowpitch-rowrule.patch
    error: patch failed: app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:5863

Hunk 1 applies at an offset of 181 lines; hunk 2 fails outright, because HEAD's `DocxWriter` now carries
a *guarded* version of the same mechanism — the spacer split into `w:before` + a one-twip hairline
`w:line`, gated by a room test on the page's own ink bottom (`ctx.budgetTw - pageInkBottomPt`, slot 23:10
of 22 Nov). The patch predates that guard and rewrites the same lines unguarded. So the patch is no
longer a candidate for HEAD at all, and the only honest way to test the claim made about it is on the
engine it was measured on: **`462353f9`**, where `git apply --check` is clean (one file, 118 changed
lines).

Everything below is `462353f9` + the patch, versus `462353f9` clean. Both builds measured on this pod in
this run; the baseline row reproduces the 15:34 table and `RANKING.csv` to the hundredth.

## 2. The numbers

| document | baseline share@5 | patched share@5 | pages baseline | pages patched | my independent line-shift (lines > 2.4 pt; median / max) | verdict |
|:--|--:|--:|:--:|:--:|:--|:--|
| `mobile-bill` | 1.55 | **36.90** | 1 | 1 | **82.1 %** of 112 lines; 7.43 / 20.01 pt | real LO displacement |
| `table-with-no-header-row` | 0.61 | **36.40** | 1 | 1 | **83.7 %** of 215 lines; 12.28 / 25.91 pt | real LO displacement |
| `insurance-policy-schedule` | 0.53 | **33.55** | 1 | 1 | **81.3 %** of 107 lines; 6.09 / 19.01 pt | real LO displacement |
| `two-tables-stacked-with-no-gap` | 0.77 | **30.02** | 1 | 1 | **61.1 %** of 72 lines; 4.18 / 10.91 pt | real LO displacement |
| `product-catalogue-code-left-price-right` | 0.47 | 0.47 | 1 | 1 | 0.0 %; 0.00 / 0.00 pt | unchanged |
| `74_balance_sheet_indented_subitems` | 0.03 | 0.03 | 1 | 1 | 0.0 %; 0.10 / 0.10 pt | unchanged |

Reproducing the 15:34 table exactly (36.90 / 36.40 / 33.55 / 30.02 / 0.47 / 0.03), so the regression is
the patch's and not a stale table, a different build, or a batch effect.

**No document changes page count in LibreOffice.** 1 → 1 on all six, page boxes identical
(595.3 × 841.9). **No document loses a character**: `text_recall` 100.00, `chars_missing` 0 on both
sides of all six. And `invent5` tracks `share5` (33.67 vs 36.90, 32.91 vs 36.40, 31.20 vs 33.55,
25.27 vs 30.02) — ink is present in both places and offset, which is the signature of a shift, not of
loss or of invention.

## 3. The two PDFs, looked at

Both renders of `table-with-no-header-row` are one page, A4, same header, same 26-row table, same
footnote, same footer, and the images are indistinguishable to the eye at 1.6×. The difference is
arithmetic, not structural:

    row pitch, measured between consecutive date cells in the text layer
      source PDF            18.40, 18.40, 18.40, 18.40, 18.40, 18.40
      baseline LO render    18.40, 18.40, 18.40, 18.40, 18.40, 18.40     <- exact
      patched LO render     17.80, 17.80, 16.80, 17.80, 16.80, 17.80     <- 1 pt short

    w:trHeight emitted
      baseline   360 x16, 380 x10   (the row's own snapped rowEdge)
      patched    348 x26            (rowTw 368 - 2 x ruleTwHere 20)

    page ink bottom, 150 dpi
      baseline   1233 px
      patched    1181 px            (52 px = 25 pt higher; nothing clipped, nothing lost)

So the page is not spilled, not clipped, and not re-ordered: **it is compressed**, by the exact amount
hunk 4 subtracts from `w:trHeight`, once per row, and the error accumulates down the table — 0.6 pt at
row 2, 2.9 pt at row 6, 26 pt at the last row. That is what share@5 measures, and it is what the
independent line check measures. Two instruments, two populations (ink pixels and text lines), the same
finding.

The construct behaves differently in the two renderers, and this is the whole of the disagreement:

* **Google charges the row's rule on top of `w:trHeight`.** The patch's own probe: declared
  368/358/348 → laid 19.73/19.04/18.35 pt. At 348 the page's 18.4 pt is reproduced, which is why
  `mobile-bill` and `table-with-no-header-row` are 47/47 in Google.
* **LibreOffice does not.** Declared 348 → laid 17.8/16.8. Nothing is added back, so the rows that were
  the page's 18.4 pt are now 1 pt short each.

The patch's central comment — "`w:trHeight` is a FLOOR — a row whose content needs more than this still
grows to its content, so lowering it cannot clip" — is true in Google and does not hold here. These
cells are written as an absolute placement (`w:before="194" w:line="10" w:lineRule="exact"`), so the
cell's own content needs almost no height, and in LibreOffice nothing grows the row back up to the
page's pitch once the declaration is lowered: 20 twips off every row came out as 1.0–1.1 pt off every
laid row (declared 360/380 → laid 18.4 uniform; declared 348 uniform → laid 17.8 / 16.8, mean 17.3).
LibreOffice's laid pitch is not the declaration row for row — the baseline's 360/380 alternation came
out uniform — but it tracks it one-for-one in the direction and magnitude that matter here, and unlike
Google it adds no rule back. That is a real layout change in LibreOffice, produced by the file, not by
the instrument.

## 4. The independent check, and what it did

`/scratch/work/lineshift.py` (this run's own, ~60 lines, `pymupdf` only) reads every text line out of the
source PDF and out of each LO render, matches them by normalised text — k-th source occurrence to k-th
render occurrence, so the duplicated cells of a table cannot cross-match — and reports the vertical
difference against the same 2.4 pt (5 px at 150 dpi) tolerance share@5 uses. No part of
`benchmarks/p2w.py` is imported.

* Every source line found a partner: 112/112, 215/215, 107/107, 72/72, 106/106, 54/54 — so no text-layer
  ordering artefact, no dropped construct, no duplicated or merged line is in play.
* Baseline renders sit within 1.82 pt of the page on every line of every document (median 0.27–0.87).
* Patched renders are 61–84 % of lines beyond tolerance, median 4.2–12.3 pt, max 10.9–25.9 pt.

The repo's share@5 is *lower* than my line fraction (36 % of ink vs 82 % of lines on `mobile-bill`).
That is the expected relation, not a disagreement: a source line that has moved 8 pt may still have
render ink within 5 px of many of its pixels (the neighbouring line, the row's own rule), whereas the
line as an object is unambiguously out. Both numbers say the same thing about the same page.

## 5. Which half of the patch does it — bisected, because it decides the verdict

Seven hunks, two mechanisms. Split and measured separately on this pod:

| document | baseline | spacer only (h1–2) | row/cell only (h3–7) | full patch (h1–7) |
|:--|--:|--:|--:|--:|
| `mobile-bill` | 1.55 | 1.74 | **41.56** | 36.90 |
| `table-with-no-header-row` | 0.61 | 0.66 | **36.43** | 36.40 |
| `insurance-policy-schedule` | 0.53 | 0.58 | **33.55** | 33.55 |
| `two-tables-stacked-with-no-gap` | 0.77 | 0.81 | **30.01** | 30.02 |

The spacer half is LO-neutral to within 0.19 pt — as the 15:34 run said, and for the reason it gave:
LibreOffice reads `w:line ... lineRule="exact"` as a length, so moving the same twips from `w:line` to
`w:before` changes nothing it draws. **The whole 30–36 is hunks 3–7**, and hunks 3–7 are precisely the
`w:trHeight` reduction. The spacer half is the half Google needed and it costs LibreOffice nothing; the
row half is the half that costs LibreOffice 1 pt a row and, on the one document it was aimed at, buys
Google a correct pitch.

## 6. Verdict

**This is case (a): the proxy is correctly reporting a real layout change.** The commit gate's
LibreOffice refusal on this patch is not an artefact of the soffice measurement path. The page that
LibreOffice draws from the patched `.docx` is 20–26 pt out of register with the source PDF by the bottom
of the first ruled table, every line of it is present, and the displacement is measurable two
independent ways — the repo's ink metric (share@5 30.02–36.90 against 0.03–1.55) and a text-line
comparison written for this run (61–84 % of lines more than 2.4 pt out, median 4.2–12.3 pt, max
25.9 pt). I read the scoring path looking for the artefact the 16:12 finding expects and did not find
one: `position()` compares page *i* of the source with page *i* of the render (`n = min(len(ds),
len(do))`), `pad()` pads both masks to the same shape so a size difference cannot shift the comparison,
`_pix` renders both at the same 150 dpi matrix, `edt()` is the exact Euclidean transform with scipy
present, and the worst-page rule is moot on one-page documents. The four artefact candidates named in
the brief are each excluded by measurement: **page count** matches 1 → 1 on all six; **content pushed
off** is excluded by `text_recall` 100.00 / `chars_missing` 0 and by every line matching; **rows grown**
is the wrong direction — the rows shrank; **text-layer ordering** is excluded by 112/112 and 215/215
lines pairing k-th to k-th; and **soffice dropping a construct** is excluded by the ink extents and the
two page images, which differ only by the 25 pt of accumulated compression.

What *is* wrong is the record around the patch, and it is worth writing down because it is what kept the
class open for three slots. **The 16:12 inference is invalid**: "one page and the same content" is
compatible with a 20 pt displacement, and it was read as if it were evidence of no displacement. **The
"extra page" in the 15:34 finding is Google's, not LibreOffice's**: that run recorded `mobile-bill`
`01_page_count` 1 → 2 for the *spacer-only* build in Google, and the LO screen in this run has that same
spacer-only build at one page (1.74) — so the two runs are not describing two pages, they are describing
one page in two renderers, and the page-count regression belongs to a different renderer than the one
the gate refused on. And **the 30–36 and the 47/47 are both true at once**, because they are not the same
page: they are the two pages one `.docx` makes in two renderers, separated by exactly the 1 pt of rule
that Google adds to `w:trHeight` and LibreOffice does not.

Consequences, stated plainly:

1. The patch is a **cross-renderer trade**, not a free fix: Google goes 46/47 → 47/47 on two documents,
   LibreOffice goes 1.55 → 36.90 on four. The gate is right to refuse it under "no document gets worse".
   Nothing in this measurement supports a waiver, because the LO damage is real.
2. There is no instrument fix to make. If a waiver path is ever wanted for a Google-clean /
   proxy-regressed change, the evidence has to be a renderer-independent statement about the page — not
   "one page, same content", which this patch satisfies while being 26 pt out.
3. The mechanism worth keeping is the **spacer half**: hunks 1–2 are LO-neutral to 0.19 pt here, and
   HEAD already carries a guarded form of them. The row half is the one to give up: a single
   `w:trHeight` cannot be 1 pt short for Google's rule-on-top and exact for LibreOffice's, and the
   attempt to make it both is what produced a 26 pt cumulative error.

## What would prove this wrong

A patched `mobile-bill` or `table-with-no-header-row` whose LO render has the page's 18.4 pt row pitch,
or whose text lines sit within 2.4 pt of the source (my check: `python3 /scratch/work/lineshift.py`,
`over_tol_pct` 0.0 on both sides). I measured 82.1 % and 83.7 %. Also: a page whose LO render is *worse*
than share@5 says — i.e. ink missing or a construct dropped that my line count (112/112, 215/215) and
`chars_missing` 0 do not show. Neither exists on this pod.

## Method and artefacts

    worktree    /scratch/work/base462   = 462353f9 (clean baseline, then + patch, then + each half)
    patched     git apply patches/18-spacer-before-rowpitch-rowrule.patch   (clean)
    halves      /scratch/work/spacer_only.patch, /scratch/work/row_only.patch  (h1-2, h3-7)
    convert     ConvertOne, one JVM per document, per build
    render      soffice 7.4.7.2 --headless --convert-to pdf, one file per invocation
    score       benchmarks/p2w.py measure_doc() -> position() -> share5 (scipy present)
    independent /scratch/work/lineshift.py (pymupdf only, no repo code)
    results     /scratch/work/m/{base462,patched,spacer,rowonly}/results.json

The repo's engine source was not modified beyond applying the patch in this run's own worktree; nothing
was deleted; `REPORT.md` and `LAST-MESSAGE.md` were not touched.
