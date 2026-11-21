# 32_stroke_lines — the guarded carrier wins in Google and destroys 54 documents in LibreOffice. Falsified on the corpus, 22 Nov 03:14-04:05.

**What the previous run believed.** `rule-carrier-horizontal-only-2008.patch` was one build from
landing: 13 of the 16 `{05_chars_extra, 32_stroke_lines}` documents at 42/42 in Google, measured
through Drive, and the only thing missing was the 213-document pass that stamps the engine.

**What this run measured.** The 13 Google wins are real. The patch also moves **54 documents the
wrong way** on the LibreOffice proxy, by 8 to 98 share@5 points, and `regress.py --check` refuses it
with 58 regressions. It is not landable as written.

| | |
|:--|:--|
| Engine | HEAD `5954eb6` + `patches/rule-carrier-horizontal-only-2008.patch`, built in 36 s |
| Corpus pass | 213 converted, 212 scored, 4 slices of ~275 s |
| Better | **52** documents |
| Worse | **54** documents — `regress.py --check`: 58 REGRESSION(S), REFUSED |
| Clean in the proxy (share@5 <= 1.0) | 120 -> 121 |
| Google (already measured by the 01:53 slot) | 13 of 16 at 42/42 |

The worst movers, all up:

    50_invoice_coloured_total_row          0.00 -> 84.13
    08_two_overlapping_stamps              0.11 -> 77.23
    product-catalogue-code-left-price-right 1.71 -> 85.32
    02_stamp_rotated_15deg_upleft          0.00 -> 69.22
    03_stamp_vertical_90deg               16.98 -> 48.36
    79_inr_indian_digit_grouping_table     0.74 -> 32.78

## The instrument is not the problem - and this was tested before the verdict was written

Prediction, written first: if the regressions are the patch's, HEAD's engine reproduces the committed
baseline on the same documents, in this sandbox, on this pipeline. If they are the instrument's, HEAD
reads the same bad numbers.

    document                                 baseline   HEAD engine   patched engine
    08_two_overlapping_stamps                  0.11        0.11           77.23
    50_invoice_coloured_total_row              0.00        0.00           84.13
    79_inr_indian_digit_grouping_table         0.74        0.74           32.78
    415_inline_images                         89.04        0.00            0.00

HEAD reproduces the baseline to the digit on all three regressed documents. The patch is the cause.

The fourth row is the control that caught a different lie: `415_inline_images` scores **0.00 on
HEAD**, against 89.04 in `RANKING-BASELINE.csv`. The baseline table is stale for that document, as
`SETTLED.md` already says for `392` and `360`. Any count of "better" against that table is inflated
by staleness, and the first reading of this pass (52 better / 0 worse, against the committed
`RANKING.csv` rather than a fresh render) was exactly that mistake: `benchmarks/RANKING.csv` is
written by hand from `/scratch/output/RANKING.csv`, not by `p2w.rank()`, so `regress.py --check`
will pass a table from an older engine once the stamp is moved. **A stamp proves the table was
made by this engine only if the table was replaced by this run.**

## The cause: a carrier count, not a rule count

`isRuleShape` is right about a page's rules and wrong about a table's separators. Counting the
floating carriers each document actually received (`<w:tblpPr>` in the patched `.docx`):

| group | documents | carriers, median |
|:--|--:|--:|
| regressed | 54 | **9** |
| unchanged | 106 | **1** |

And within the 16 target documents the same split shows up: 14 of them carry 2-3 carriers and are
unchanged or better (17, 18, 19, 24, 26, 32, 334, 34, 37, 45, 47, 49, 53, 74), while the two that
regress carry 21 (`product-catalogue-code-left-price-right`, 1.71 -> 85.32) and 2 but sit on a
table (`315_gazette_notification`, 1.96 -> 15.87).

So a document with 21 carriers is not a page with 21 rules. The horizontal guard removed 3608 of
4595 carriers as 8-twip verticals; what is left still contains **horizontal 8-twip table
separators**, and a floating 1x1 table nested inside a table cell displaces the cell's flow in
LibreOffice. The stamp documents are the same defect in another dress: the shape is a stamp's
frame, not a rule, and it became a table.

**The narrowing the next run should test, in one line of the same predicate:** a band that the
table writer already draws as a cell border, or that sits inside a table cell or a stamp frame,
must not get a carrier. Not a cap on carriers per page - that is a special case. The test is
whether the shape's box coincides with a cell or row edge.

## What would prove this wrong

Verify three regressed documents (`08_two_overlapping_stamps`, `50_invoice_coloured_total_row`,
`product-catalogue-code-left-price-right`) in **Google** on the patched engine. If Google renders
all three at 42/42, the 54 are a LibreOffice-only artefact of nested floating tables and the
predicate does not need narrowing - the proxy is over-weighting a construct Google honours, which
would be an instrument finding, not a fix. If Google shows them displaced, the narrowing above is
the work. That is the one measurement this slot did not have time for, and it is the whole
question.

## Also measured

* The `.txt` is unchanged by the patch across the **whole corpus**, not just the 16:
  `restamp_txt.py --run` scored 213 in 34 s, 0 newly clean, 0 newly failing, 213 unchanged, and
  `RANKING-TXT-BASELINE.csv` came back byte-identical. 197 of 213 clean.
* The patch touches `DocxWriter.java` only, and the engine sources are byte-identical between
  `462353f` (the engine the 13 Google rows were measured on) and HEAD `5954eb6` - `git diff
  462353f9 HEAD -- app/src/main/java/com/kavopdf/app/engine/` is empty. The 13 rows are valid for
  this tree; they are kept in `benchmarks/gverify-carrier-2008/` and **not** merged into
  `benchmarks/gverify/`, because the engine that would carry them is not the engine in the tree.
* Evidence kept: `/scratch/work/RANKING-patched.csv` is not in the repository - the patched numbers
  are in the tables above. The engine is reverted, the tree is clean, `regress.py --check` PASSES.
