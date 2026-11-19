# 75_merged_header_cell_three_columns — the one defect w:vMerge did NOT fix, measured

Engine: `6bff144` (this run's commit: w:vMerge from `spanR`, and a rectangle spanning rows is a
merge only when its text occupies fewer row bands than it covers).

## Where the document stands

    27.31 -> 7.62 share@5px, text_recall 100, invent5 7.23
    Google 39/47 -> 41/47 (43_within_10pt_x and 47_margins now pass)
    LibreOffice 44/47; both renderers still fail 64_table_span_across and 65_table_span_down

Word-by-word against the source page, every word now lands within 1.3 pt except one:

| word | source | ours | error |
|:--|:--|:--|:--|
| Depot | y 139.3 | y 139.4 | ok |
| SCHEDULED | y 130.8 | y 131.6 | ok |
| Fleet held | y 139.8 | y 139.9 | ok |
| **Breakdowns** | **y 139.8, x 461.0** | **y 152.0, x 399.8** | **one cell to the left, one line down** |
| Services / 1,842 / 6,42,180 / 1,284.42 | 149.2 / 165.4 | 149.9 / 166.0 | ok |
| Yeshwanthpur, 184, 42 | 165.4 | 166.0 | ok |

So the whole table is placed correctly and the only remaining defect is a **horizontal** one:
"Fleet held" and "Breakdowns" are two adjacent header cells on the page and we emit them as one
2-column cell stacked over two lines.

## The cause, unchanged from the 13:04 finding

`RuleCollector.appendRectangle` (`PdfToWord.java:6245`) records four table RULES for every `re`,
whether it was stroked with `S`, filled with `f`, or both. The page shades the header with one
fill covering both cells:

    q .9 .92 .96 rg 394 681.89 124 34 re f Q      <- 394..518 x 126..160, no stroke

`intersectionsToCells` then closes the only rectangle there is over that fill — 394..518, two
columns wide — and `tableFromCells` reads the width as `gridSpan=2`. The page never drew a
separator at x=456 above y=143, so the engine is not missing a rule: it is treating a paint
region as a cell outline.

## What this run did NOT do, and why

* **Dropping fill-only rectangles from the rule list was already measured and refused** (27.31 ->
  46.58 on the pre-fix engine). A shading-only table with no strokes at all would lose its grid.
* The honest fix is to carry the paint operator: a rectangle contributes a cell EDGE only where it
  was stroked (`S`, `B`), while a fill contributes only its extent, usable as evidence of a merge
  but not as a separator. That touches `RuleCollector` and every table pass, and it needs its own
  full 213-document verification — it is a run of its own, not a tail to this one.
* A cheaper targeted test, worth doing first because it needs no paint operator: a rectangle whose
  width covers >1 column is a horizontal merge only when no glyph in it sits in more than one
  COLUMN band (the same band argument this run used for rows). Here "Fleet held" and "Breakdowns"
  are in two distinct column bands, so it would split; a genuine `SCHEDULED` merge holds one run
  of text across three columns and would stay merged. **Untested — do not assume it works.**

## What would prove the paint-operator theory wrong

If a page whose cells are *only* filled and never stroked (no `S` anywhere in the table band) came
back with no table at all after the change, the fill is carrying the grid legitimately and the
distinction has to be weaker than stroke-vs-fill.
