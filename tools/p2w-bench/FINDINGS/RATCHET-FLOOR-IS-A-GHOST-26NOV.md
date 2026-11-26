# The gate's ratchet floor is a measurement of an engine that is not in the tree

**Measured 26 Nov 2026, fixer slot 23:56 IST. No engine code in this commit.**

## What was wrong

`benchmarks/RANKING.csv` at HEAD describes engine **aa496ebe**, not the tree. Commit `ee5a00d6`
restored `DocxWriter.java` to `9f0a8207`; `git diff --stat 9f0a8207 HEAD -- app` is empty, so the
tree is `9f0a8207`. The committed table was never re-measured after the restore: commit `344aff13`
landed the aa496ebe rows while its own subject says "RANKING.csv not committed".

So the gate was refusing on three rows that describe a reverted engine:
`39_small_caps_letter_spacing 0.72 -> 0.80`, `newsletter-3col-header-footer 3.45 -> 86.30`,
`350_question_paper 0.11 -> 0.12`.

## What the tree actually measures

Full corpus, 212 of 212 scored, engine `a4d8fca469bba636` (= `9f0a8207`), soffice render,
`python3 benchmarks/p2w.py` in seven resumable passes:

    table   tools/p2w-bench/FINDINGS/evidence-26NOV/RANKING-26NOV-reverted-engine-212.csv

| | 15 Nov baseline | this tree |
|:--|--:|--:|
| mean share@5 | 6.15 | **3.71** |
| documents at share@5 <= 1.0 (99 %) | 120 | **153** |
| regressions vs baseline | - | **0** |

The three rows the gate names are not regressions on this tree:

    39_small_caps_letter_spacing     0.72 -> 0.70   clean
    newsletter-3col-header-footer    3.45 -> 0.20   clean      (re-measured directly: 0.20, 1 page)
    350_question_paper               0.11 -> 0.11   clean

`newsletter-3col-header-footer` at 86.30 and page count 2 was produced by aa496ebe and does not
reproduce: converted at HEAD it is 1 page, 79 paragraphs, share@5 0.20.

## The contradiction that keeps the slot blocked

With the refreshed table in the working tree, `regress.py --check` stops naming those three and names
one instead:

    itr-computation-with-slab-table   9.10 -> 42.33   share@5 up vs the last commit

`9.10` is aa496ebe's number; aa496ebe is not in the tree. Measured at HEAD it is 42.33, twice, by two
routes (the corpus pass and a direct `measure_doc`). So:

* `regress.py` **requires** the table to describe the tree (engine-fingerprint check), and
* `regress.py` **requires** no row to be worse than the committed table (ratchet floor), and
* the committed table describes an engine that is no longer the tree.

After a revert those two cannot both hold. The gate has no state in which a revert can be committed,
which is why three consecutive runs wrote a report about being stuck. The floor should be the
baseline for any row whose committed value came from a different engine - that is a tool change and
it is **not** made here.

## The lead: re-landing the page-top patch

aa496ebe's only engine change is `sectionTopTw()` measuring the page margin from `page.blocks[0]`.
`PdfToWord` orders a column page's blocks by column then y, so on a page with a full-width header band
`blocks[0]` is the top of column 0, below the band. Hypothesis: use the topmost block instead and the
patch keeps itr's gain without newsletter's damage.

**Refuted on five documents.** Patch `PATCHES/pagetop-topmost-block-26NOV.patch` re-lands aa496ebe
with `sectionTopTw()` taking the minimum-y block (identity still returned for any block that is not a
Para/Box, which preserves the 401 guard). Compiled and converted at HEAD:

| document | reverted tree | topmost-block variant | aa496ebe |
|:--|--:|--:|--:|
| newsletter-3col-header-footer | 0.20 | 0.20 | 86.30 |
| itr-computation-with-slab-table | 42.33 | 42.33 | 9.10 |
| 600_reviewed_invoice_with_annotations | 62.46 | 62.46 | 62.46 |
| 39_small_caps_letter_spacing | 0.70 | 0.70 | 0.80 |
| 401_trifold_brochure (the guard doc) | - | 0.03 clean | - |

Not one document moved, so the variant is a no-op, not a fix: itr's 9.10 does not come from the block
that `sectionTopTw` reads. The next run should not re-try this. It should bisect aa496ebe against
**itr-computation-with-slab-table** alone - that is the one document that pays for the patch - and
find which of the patch's 135 lines moves it, because the patch is worth keeping only if its gain can
be had without newsletter's 86-point loss.
