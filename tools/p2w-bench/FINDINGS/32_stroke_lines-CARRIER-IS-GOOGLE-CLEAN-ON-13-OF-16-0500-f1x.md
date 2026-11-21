# The carrier is not falsified in Google. It is Google-clean on 13 of 16 documents, and the only thing stopping it is 41 documents nobody has measured.

Run 04:18, 22 Nov. Engine HEAD 462353f9. Evidence read, not re-measured by this run: the
committed Google results in `benchmarks/gverify-carrier-2008/` (16 documents, all scored with
`engine_patch: rule-carrier-horizontal-only-2008` on this same engine) against the committed HEAD
Google results in `benchmarks/gverify/`.

## The table

| document | HEAD Google | carrier Google | |
|:--|--:|--:|:--|
| 17_three_column_widths_txtpos | 40/42 `05`,`32` | **42/42** | CLEAN |
| 18_centred_heading_left_body_txtpos | 40/42 `05`,`32` | **42/42** | CLEAN |
| 19_hanging_indent_txtpos | 40/42 `05`,`32` | **42/42** | CLEAN |
| 24_address_block_indents_txtpos | 40/42 `05`,`32` | **42/42** | CLEAN |
| 26_footnote_marker_bottom_note_txtpos | 40/42 `05`,`32` | **42/42** | CLEAN |
| 315_gazette_notification | 40/42 `05`,`32` | 41/42 `32` | improved, not clean |
| 32_serif_nondefault_body | 40/42 `05`,`32` | **42/42** | CLEAN |
| 334_patent_document | 40/42 `05`,`32` | **42/42** | CLEAN |
| 34_monospace_document | 40/42 `05`,`32` | **42/42** | CLEAN |
| 37_font_not_embedded_substitution | 40/42 `05`,`32` | **42/42** | CLEAN |
| 45_coloured_callout_box | 40/42 `05`,`32` | **42/42** | CLEAN |
| 47_grey_body_black_headings | 40/42 `05`,`32` | **42/42** | CLEAN |
| 49_coloured_background_block_paragraph | 40/42 `05`,`32` | 41/42 `32` | improved, not clean |
| 53_single_space_body_15_headings | 40/42 `05`,`32` | **42/42** | CLEAN |
| 74_balance_sheet_indented_subitems | 40/42 `05`,`32` | **42/42** | CLEAN |
| product-catalogue-code-left-price-right | 40/42 `05`,`32` | 41/42 `32` | improved, not clean |

**16 measured, 13 reach 42/42, 0 regress in Google, and every one of the 16 clears
`05_chars_extra`** — the U+200B the dropped drawing used to leave behind. That is +13 CLEAN
documents in the renderer the user opens, from a patch the last two runs called dead.

`32_stroke_lines` is worth 36.5 clean documents and `05_chars_extra` 35.2; the {05,32} shape is 16
documents, the largest single shape in the corpus. This patch is the one construct for both.

## Why it is not landed

Not Google. LibreOffice. The 04:00 run's corpus pass found 54 documents worse on the proxy and
`regress.py` refused. This run's two measurements say what that regression actually is:

1. **It is not nesting.** Across 22 documents and 156 carrier tables the maximum `tc-depth` of any
   carrier is **0** — every carrier's parent is `w:body`. The "floating table nested inside a table
   cell" that the last report named as the blocker does not exist in the emitted XML.
2. **The prescribed fix is a no-op.** The guard the last run asked for — "a rule whose anchor
   paragraph sits inside a `w:tc` keeps the drawing" — cannot fire, because no `Shape` is ever
   routed into a cell (`columnPage` gives every shape `home[i] = -2` and emits it at body level).
   Implemented and built, the guard never fired once and output was byte-identical to HEAD on five
   PDFs (43→43, 65→65, 1→1, 2→2, 2→2).
3. **What the regression is:** body-flow displacement that overflows the page. 7 of 8 regressed
   documents go from 1 page to 2–3 pages; 0 of 14 unchanged documents gain a page. It is not
   dose–response — 41 carriers gives +15.57 while 10 carriers gives +83.89.

And the gate already has the door for exactly this case, written into `regress.py` itself:

> A LIBREOFFICE REGRESSION IS ALLOWED WHEN GOOGLE IMPROVED ON THE SAME DOCUMENT.

That exemption needs `benchmarks/gverify/<doc>.json` in the working tree. Sixteen documents have a
carrier Google result; **38 of the 54 LO regressions do not.**

## What would land it

1. Apply `tools/p2w-bench/patches/rule-carrier-horizontal-only-2008.patch`, build, run the corpus
   pass, and take the exact list of LO regressions (the 04:00 list is in `benchmarks/blast-carrier-2008.json`).
2. Google-measure the regressed documents that have no carrier result — `gverify.py --plan 60`
   takes sixty a run, so one gverify run closes it.
3. Each one that improves in Google is then allowed by `regress.py` by its own rule; each one that
   does not is a real regression and stays out.
4. Commit `benchmarks/gverify/` with the carrier results *and* the engine patch in the same push.

Do not narrow the predicate first. It has nothing to narrow: the property that separates the 45
vacuous documents is on the source side, and the cell guard is a measured no-op.
