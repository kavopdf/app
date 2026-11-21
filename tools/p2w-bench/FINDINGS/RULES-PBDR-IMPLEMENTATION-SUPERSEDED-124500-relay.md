# The pBdr carry-over is superseded, and the carry-over itself was the defect

**Class:** `32_stroke_lines` (largest in Google) · **Engine:** unchanged this run · **Measured:** 21 Nov 2026, 12:12–12:45 IST

## What the carry-over said

`HANDOFF.json["next"]` and `pending.py` item 1 both said: *"Land the pBdr rule replacement:
FINDINGS/RULES-PBDR-IMPLEMENTATION.md ... Screen 32_stroke_lines first, then the full corpus pass.
The finding predicts 124 documents cleared."*

That instruction is three findings out of date. Every run since 19 Nov has read it, spent its first
minutes on it, and re-derived the same three results. This file exists so no run reads it again.

## The three findings that settle it, in order

| finding | what it measured | number |
|:--|:--|:--|
| `...rules-cannot-flow-044000-f1x.md` | a rule is appended to `page.blocks` AFTER the page's paragraphs (`PdfToWord.java:7122`), so `s.topPt > ctx.flowY` is false for every rule on every page | the `w:before` gap is **never** computed; the implementation is correct and **inert** |
| `...rules-flush-works-displaces-055000-f1x.md` | the precondition was built (flush shapes by top) and the border landed at the right y | `18_centred_heading_left_body_txtpos` `18_displacement` **PASS -> FAIL**; reverted |
| `...rules-are-flow-neutral-065000-f1x.md` | a carrier paragraph costs **9.6 pt of flow whatever it contains** - border, inert element, no run, any `w:line` | `0.00 -> 77.01` on that document; the carrier IS the displacement |

The mechanism is not the gap formula. **It is that `w:pBdr` needs a paragraph, and a paragraph costs
9.6 pt on this engine.** No value of `w:before` removes a cost the carrier charges before `w:before`
is read.

## Verified again this run, independently of those findings

Two subagents were deployed on this question and both answers are in `FINDINGS/`-adjacent reports
(`pbdr-verification.md`, `rule-flow-neutral.md`). The parts I re-checked in the tree myself:

1. **`ruleAsBorder` and `w:pBdr` do not exist in the engine.** `rg "pBdr|ruleAsBorder"` over
   `app/src/main/java` returns nothing. The only borders are table-side (`DocxWriter.java:6419`,
   `w:tcBorders><w:bottom`, fed from `t.rowStroke`, not from a `Shape`).
2. **Every symbol the implementation needs is present**, so "it will not compile" is not the reason
   it is unlanded: `flowY` (:787), `flowBoxPt` (:793), `newPage` (:795), `pageWidthPt` (:913),
   `isHairline` (:2845), `hex` (:2690), `LINE_BASE = 0.8f` (:214), `TWIPS_PER_PT = 20.0` (:51, a
   `double`, so the snippet needs `(int) Math.max(0L, ...)` - cosmetic).
3. **The 065000 patch's guard is unsatisfiable by construction, and I confirmed the line.** In
   `flowFromBox` (`DocxWriter.java:4204-4205`) a left-aligned paragraph gets `rightTw = 0`, so
   `textRightPt` collapses to `pageWidthPt`. The guard's right-hand test therefore demands
   `|(s.x + s.w) - pageWidthPt| <= 1.5` - **the rule must reach the paper edge**. Measured over the
   2136 hairline rules in the 213 source PDFs: **1 of 2136 passes on the right, 0 of 2136 on both
   edges.** Declining was the correct behaviour; the construct cannot be written as a border that
   spans the paragraph's indent box, because that box is the paper.
4. **The ceiling is the hook, not the guard.** `...rule-guard-was-not-the-blocker-100700-f1x.md`
   measured it: on `bank-statement-horizontal-rules-only`, 36 of 39 rules belong to paragraphs the
   TABLE writer emits, so `pendRuleConsume` is reached 3 times for 39 rules. Every loosening of the
   guard bought at most 3 borders on a document made entirely of rules.

## Decision, and what would reopen it

The pBdr-carrier construct is **closed**, not parked: it is refuted by measurement, three ways, and
the carry-over is cleared so the gate stops handing it to the next run.

What would reopen it, and nothing short of it:

* a construct that draws a horizontal rule **without adding a paragraph to the flow** - a table row
  border, a bottom border on the paragraph the page already drew above the rule, or something not
  tried yet; and
* a measurement that shows the rule's ink lands at the page's own y on a document with a rule at the
  head, mid-page and in a footer, with `18_displacement` no worse.

The next run's attempt at `32_stroke_lines` should start from **"no new paragraph"**, not from this
file.

## Ruled out this run, so it is not retried

* Loosening the 065000 guard (containment, ink, indents-from-rule, centred excluded): measured
  10:07, ceiling 3 of 39.
* Flush-by-top: measured 05:50, `18_displacement` PASS -> FAIL.
* Carrier paragraph in any form: measured 06:50, 9.6 pt, not portable across renderers.
