# P2W Fixer - Run Report

**21 Nov 2026 · slot 07:14 → running IST · 2 min**

> A layout column's left edge was the AVERAGE of where its lines start, and an average is a place no
> line starts. Two documents went from failing to passing in LibreOffice, one of them confirmed in
> Google, and the full corpus was measured and gated to land it.

The Progress table below is report.py's window, and it opens at the 07:14 re-claim: the slot expired
while the 213-document pass was running, so the attempt that landed is recorded at 07:12 and falls
just outside it. **Two documents were improved and kept this run** - the prose under What was tried
names them and the commits are 7112d76 and 6d6a0de.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `47_margins` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 07:12 | **kept** | 2/26 | A LAYOUT COLUMN'S EDGE IS A PLACE ITS LINES START, NOT THEIR MEAN. `DocxWriter.rowColumnEdges()` reports each cluster of fragment starts as its running mean. A borderless layout-table cell draws its text at the cell's left edge plus `w:ind`, and `w:ind` cannot be negative - the emitter writes `Math.max(0, leftTw - bandLeftTw(...))`, which silently drops the difference - so every line drawn LEFT of the mean edge is displaced right by a constant. |
| 07:16 | **partial** | 0/26 | THE NEXT DOCUMENT'S 2.01 pt IS A SPACE'S ADVANCE, NOT AN INDENT. `365_recipe_card`'s five METHOD steps carry `w:ind 800` = 40 pt and the source puts the "1." at 40.00 while the render puts it at 40.10 - the indent is right. The run's text literally begins with a space, so the step's ink x is the paragraph pen plus "1." plus the space's advance, and that advance is 4.85 pt in the source's face and 2.69 pt in the substituted DejaVuSerif. |

### The landed construct, and why it is right

Both documents are borderless layout tables - every `w:tblBorders` is `none`, every `tblCellMar` is
0, `tblInd` equals the page margin - so the cell-border double charge proved at 03:45 cannot explain
either one. The edge itself was wrong.

`brochure-3col-with-sidebar-box`: the third column's 25 fragments are 15 at 392.13 (the body) and 10
at 400.13 (the sidebar's key/value list, 8 pt inside it). The mean is 395.33, so the grid's third edge
was 395.33 and the body's indent was clamped to 0. Fifteen runs rendered at 395.40, a constant +3.27
over a 0.00 spread.

`product-catalogue-code-left-price-right`: the second column's 41 fragments span 516.07 to 529.82, the
mean is 524.12, and fourteen runs at 516.07 and 521.57 were clamped to indent 0 - the constant +8.1 and
+2.6 the class reports. The two constants were never two insets; they were the two price widths.

Taking the leftmost start instead gives 392.13 and 516.07, every line's indent becomes its own distance
from the column's start, and every line lands on its page x.

| document | before | after | 47\_margins |
|:--|--:|--:|:--|
| `brochure-3col-with-sidebar-box` | 41/42 | **42/42** | 15 runs / +3.27 -> **0 / +0.07** |
| `product-catalogue-code-left-price-right` | 41/42 | **42/42** | 29 runs / +8.13 -> **0 / +0.13** |

Six control documents - `404_sudoku_grid`, `76_devanagari_table`, `78_mixed_english_devanagari_line`,
`365_recipe_card`, `07_stamp_over_table`, `21_form_labels_x60_values_x300_txtpos` - show no run moving
more than 0.10 pt, and five of the six .docx are byte-identical to HEAD.

### Google decides, and Google agreed

The patched .docx was uploaded to Drive, converted to a Google Doc, exported as PDF and scored with the
same 42 checks:

    brochure-3col-with-sidebar-box   HEAD     37/42   47_margins FAIL
    brochure-3col-with-sidebar-box   patched  38/42   47_margins PASS

Google improved on the document, so the gate ALLOWED its LibreOffice share@5 going 2.30 -> 2.45 - the
first time the allowance has been used - and the change landed. That is the rule the brief sets: a
LibreOffice score that rises is not a reason to revert when Google fell.

### The gate, and the one judgement in it

The change is gated on `COLUMN_EDGE_SPLIT = 2 pt`: a cluster's edge becomes its leftmost member only
when the mean sits more than 2 pt right of it. Ungated, `07_stamp_over_table`'s first column (5 x 356.0
and 1 x 362.0, mean 357.0) moves six runs 1.00 pt each toward the page. That is a control moving more
than 0.5 pt, so it is not what shipped; the 1.1 pt error it would close is left open deliberately and
is the first thing to re-measure if the class is re-opened.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

Two agents, both before the run's own attempt, both given a problem rather than a grep.

1. **47_margins census** (20 min) - a per-document cause classification of all 26 documents of the
   class: median and max x-error, unregistered runs, table cell or flow paragraph, constant or
   scattered. It found 10 of the 26 already pass on this build and the committed tables are stale for
   them, sorted the rest into six constant-offset documents and six scattered-tail ones, and named the
   smallest first proof in each class. That census is what picked the two documents this run fixed and
   the one it took second.
2. **Borderless cell inset** (18 min) - given the two documents whose cell edges were off by a
   constant in a table with no borders at all, it found `rowColumnEdges()` reporting the cluster mean,
   wrote the patch, and measured a same-tree HEAD/patched pair on eight documents. Its numbers
   reproduced exactly when this run built and scored both sides itself.

## Timing

| | |
|:--|:--|
| Slot window | 07:14 → running · 2 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 7 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| report - the report and the chain | **1 min** | `###########` |
| other - not attributed to a tool | **1 min** | `###########` |
