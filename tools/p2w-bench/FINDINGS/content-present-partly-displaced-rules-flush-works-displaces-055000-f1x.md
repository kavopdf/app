# Flush-by-top works, the border lands, and the text below it moves — the residual is 18_displacement

Follows `content-present-partly-displaced-rules-cannot-flow-044000-f1x.md` (the precondition: a rule
is written after the flow has passed it), `RULES-PBDR-IMPLEMENTATION.md` (the code) and
`RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md` (the cause).

**The precondition was met and the construct worked. The change is reverted because it made a clean
document worse, and this file carries the exact diff so the next run does not rebuild it.**

The patch is `rules-flush-by-top-WORKS-DISPLACES-055000-f1x.patch` (163 lines, applies to the tree
this run started on). Read it with the numbers below before re-applying it.

## What was built

Two changes in `DocxWriter.java`, one construct:

1. **`flushShapes()` + a top-ordered emit loop in `pageXml()`.** `PdfToWord.attachShapes` appends
   every shape to `page.blocks` after the paragraphs, so the emit loop reached each shape last on
   its page with the flow already at the foot. The loop now flushes any not-yet-written shape whose
   `topPt` the next Para/Table has reached, in top order, and the rest after the loop. Paragraph and
   table order is untouched; a Shape block is skipped in the loop because `flushShapes` writes it.

2. **`ruleAsBorder()`**, called first in `shape()`: a horizontal hairline becomes a `w:pBdr` bottom
   border with `w:before` computed from `ctx.flowY`, `ctx.flowY = s.topPt` afterwards, and a guard
   that returns false when the rule is at or above the flow (so the drawing path keeps it).

## What it measured

`18_centred_heading_left_body_txtpos`, emitted `word/document.xml`, before and after:

| | before | after |
|:--|--:|--:|
| `<w:pBdr>` | 0 | **2** |
| `<w:drawing>` | 2 | **0** |
| rules at y (page's own) | 110.0, 793.89 | 110.0, 793.89 |
| flow after the last paragraph | 805.9 | 805.9 |

Both rules are written as borders and both land at the y the page drew them at — the thing
`RULES-PBDR-FIX-MEASURED.md` could not do and the reason `rules-cannot-flow` existed. **The
mechanism in the handoff is correct and the flush-by-top change is what makes it work.**

Through Google, same document:

| | before | after |
|:--|:--|:--|
| `32_stroke_lines` | **FAIL** | **PASS** |
| `05_chars_extra` | FAIL | FAIL |
| `18_displacement` | PASS | **FAIL** |
| Google total | 40/42 | 40/42 |

Through LibreOffice the same document went **42/42 → 41/42**, failing `18_displacement`. It was a
`none` document (share@5 0.00, "no defect"). **A clean document made worse in both renderers.**

## Why the displacement, and what is left to solve

The border is placed by flow, so its carrier paragraph charges the page. The rule is now drawn at
the right y, but the text under it is not where it was: `ctx.flowY = s.topPt` was supposed to make
the next paragraph measure its gap from the rule, and it does not fully — a residual of a few points
survives per rule and the document has two of them.

Three things were tried and are ruled out:

* **`below = ctx.flowBoxPt * (1 - LINE_BASE)` subtracted from the gap** (the formula in
  `RULES-PBDR-IMPLEMENTATION.md`): measured on 18_centred, `flowBoxPt` is 0 at the moment the rule is
  flushed, so the term contributes nothing — it is not the residual.
* **`s.kind != 0` (a path, not a rectangle)**: removing that guard changed nothing on 315 and nothing
  on 18_centred. The two rules on 18_centred are plain filled rectangles (`kind=0`, fill `000000`,
  no stroke).
* **The gap arithmetic itself**: border 1 lands within 0.5 pt of its rule on the emitted spacing.
  The error is not in where the border is drawn; it is in where the flow is left afterwards.

**So the residual is the reader's position after the carrier paragraph, not the gap before it.**
The next run should measure that directly: emit the border with `ctx.flowY` unchanged, then read the
`18_displacement` number, and compare it with `ctx.flowY = s.topPt`. One of the two is closer, and
that is one build and one Google round trip to find out.

## A second, larger blocker found on the way: the column path

`315_gazette_notification` is a three-column layout and takes `columnPage()`, which returns **before**
the emit loop the flush was added to. Its two horizontal rules at y 59.6 and 77.8 are written at the
end of the page (`flowY = 751.87`), so `ruleAsBorder` declines both and they stay drawings. Measured:
`pBdr 0, drawings 5` (2 horizontal + 3 vertical), Google 40/42 failing `05_chars_extra` and
`32_stroke_lines`, LibreOffice 42/42 — **unchanged by the whole change**.

`columnPage()` partitions the page into `before`, one cell list per column, and `after`, and emits
those three with plain `emitBlock` loops (`DocxWriter.java:2005`, `:2146`, `:2214`). The horizontal
rules land in `after`, not `before`, which is why the flow has already run to the foot. **A fix that
only touches `pageXml()` cannot reach any multi-column document**, and the corpus has many
(62_two_col, 64_newspaper, 65_two_col, 66_two_col, annual-review-2col, academic-paper-ieee-2col,
brochure-3col, price-list-2col …). That is the next structural question, and it is a separate
construct from this one.

## What this rules out, so the next run does not re-derive it

* **The flush-by-top change is correct and necessary.** Without it `s.topPt > ctx.flowY` is false for
  every rule on the page and pBdr is inert. With it, both rules on 18_centred become borders at the
  page's own ys. Do not go back to pBdr-without-the-flush.
* **pBdr is not a LibreOffice regression by construction** — the drawing path pins the rule at the
  same y. The regression here is `18_displacement`, from the flow, not from the rule's position.
* **`32_stroke_lines` does flip to PASS in Google** when the rule becomes a border. The construct is
  confirmed a third time. The blocker is now displacement, not the rule.

## Why it was reverted and not kept

The brief's rule is absolute: a change that makes any document worse is not kept, and a fix for the
largest class that makes the second-largest worse is not a fix. `18_centred` was clean and is not.
The gate could not be run either — `regress.py --check` needs all 213 re-measured and this run could
not finish a corpus pass. **Reverted, with the diff kept here.**

## Confidence

**High** that the flush is right and the border lands: it is measured on the emitted XML of the
document the earlier finding used, to within 0.5 pt.
**High** that the blocker is now `18_displacement` from the flow, not the rule's placement.
**Medium** that leaving `ctx.flowY` unchanged is the answer — that is one measurement away, not a
theory this run could settle inside its slot.
