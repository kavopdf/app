# 47_margins (b): the 2.01 pt is a SPACE's advance, and a tab stop closes it to 0.10

**21 Nov 2026, ~07:30 IST, fixer. Second attempt of the run.** Class `47_margins`. The first attempt
landed the column-edge fix (`rowColumnEdges()` reports the leftmost start, not the cluster mean);
this one takes the next document on the census's winnable list, `365_recipe_card`, and the answer is
not an indent value.

## The measurement, source against render

`365_recipe_card` page 1, the five METHOD steps. Source PDF and the soffice render of the .docx the
engine writes, both read with PyMuPDF, x in points:

| | source | render (HEAD) |
|:--|--:|--:|
| `1.` pen | 40.00 | 40.10 |
| the space after it | 49.15 | 49.30 (inside the following span) |
| the step text's ink | **54.00** | **51.99** |

The paragraph is `<w:ind w:left="800" .../>` = 40 pt, correct to 0.10. The text run's literal string
begins with a space — `" Mix the grated paneer, ..."` — so the step's ink x is

    paragraph pen + "1." advance + the space's advance

and the space's advance is **4.85 pt in the source's face and 2.69 pt in the substituted face the
document names** (`DejaVuSerif`, `w:sz 17` = 8.5 pt). The 2.01 pt is the difference between two
faces' space glyphs, not a margin, not an indent, and not the cell-border defect.

## The construct that closes it, measured

One XML edit on the emitted .docx and nothing else: give each of the five paragraphs
`<w:tabs><w:tab w:val="left" w:pos="1080"/></w:tabs>` and replace the leading space in the run with
`<w:tab/>`. Tab stop 1080 twips = 54 pt from the left margin, which is the source's own ink x.

| | source | HEAD | tab-stop edit |
|:--|--:|--:|--:|
| step text's ink | 54.00 | 51.99 | **54.10** |
| `1.` pen | 40.00 | 40.10 | 40.10 |

A tab stop is a position; a space is an advance in whichever face renders it. 2.01 pt -> 0.10 pt,
which is the document's own substitution floor.

## Why this is a finding and not a patch

The construct is **not** "strip leading spaces". A leading space that carries text to a column is
the same shape as a space that is simply a word separator, and the corpus is full of both — the
space-aligned invoice documents (`71_invoice_space_aligned_no_rules`) are built out of the second
kind. The emitter needs a guard: emit a tab stop only when the run's leading spaces move the ink by
more than the registration tolerance AND the resulting x is a position the page reuses, which is a
property of the page, not of the paragraph. That guard has to be measured over all 213 documents,
and a corpus pass is what this run spent on the first fix.

Two earlier runs attacked this same shape and moved nothing (`ATTEMPTS.json` 13:34 moved 3 with a
space-as-indent change, 14:35 moved 0 with an `anchorBox` version). Read those before writing the
guard: the 13:34 record is the one that had the right idea and the wrong site.

## What it is not

* Not the border. `sz` is 0 on this document's tables and the steps are flow paragraphs.
* Not the indent. `w:ind 800` reproduces the source's `40.00` as `40.10`.
* Not the run size. `w:sz 17` is the source's 8.5 pt and the check's `10_font_sizes` passes.
