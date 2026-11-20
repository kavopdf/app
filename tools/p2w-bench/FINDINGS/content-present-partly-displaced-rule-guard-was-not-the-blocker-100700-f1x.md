# The rule-border guard was never the blocker. The paragraph hook is.

**Class:** `content-present-partly-displaced` (23 OPEN) · **Engine:** reverted, tree at `ea9dfd7`
**Measured:** 20 Nov 2026, 09:20–10:05 IST

## The question

`benchmarks/DEFECT-CLASSES-GOOGLE.md` says the top two Google classes are one construct:
`32_stroke_lines` 145 documents, `05_chars_extra` 141, both from a rule written as a floating
`<w:drawing>` that Google drops while keeping its anchor
(`FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`). The engine still writes every rule that way
(`DocxWriter.shape()`, DocxWriter.java:2726 — no border branch at all).

`FINDINGS/rules-top-border-FLOW-NEUTRAL-065000-f1x.patch` is the known-good mechanism: hand the rule
to the paragraph the page drew it above, as that paragraph's `w:top` border, with the gap in
`w:before` and the rule-to-text distance in the border's `w:space`. It applies cleanly to the live
tree. Its one weak point, named in the patch, is a guard that demands the rule and the paragraph
AGREE on both horizontal edges within 1.5 pt — and the reasoning offered for loosening it was that
the gate now allows a LibreOffice regression when Google improved on the same document.

## What was tried, in order

1. **Patch applied as written, with its own guard.** Converted
   `bank-statement-horizontal-rules-only` (39 hairline rules, 57 paragraphs) and counted the XML:
   **0 `w:pBdr`, 39 `w:drawing`.** The guard declined every rule on the one document built entirely
   of rules.
2. **Guard loosened to containment** — the rule must cover the paragraph's span, so a border drawn
   between the paragraph's indents can add no ink outside the rule. Still **0 `w:pBdr`**, and the
   diagnostic printed the reason: `rule 45.35..549.93 text 45.35..595.28`. The rectangle being
   compared was the paragraph's **indent box**, and that box is the paper width whenever the right
   indent is 0. It is not the rule's rectangle and it is not the line's either.
3. **Measured against the line's own ink instead** (`Para.left`/`Para.right`), and wrote the
   paragraph's indents FROM the rule so the border lands exactly on it: `EDGE rule 45.35..549.93 ink
   45.35..261.35`. A rule under a table row spans the whole text column while the line under it is
   short, so edge agreement cannot hold for the construct this class is made of.
4. **Containment on the ink, indents written from the rule, centred lines excluded** (`p.align == 1`
   is re-centred by a narrower box). First real borders: **3 `w:pBdr`, 36 `w:drawing`.**

## Why 3 and not 39

`pendRuleConsume` was reached **3 times** for 39 assigned rules. The other 36 paragraphs never reach
the paragraph path at all: rules under table rows are emitted through the table writer, not
`flowFromBox`, so a pending rule set for such a paragraph is overwritten by the next one before
anything consumes it. **The guard is not the ceiling. The hook is.** Every loosening of the guard
above bought at most three borders on a document with thirty-nine rules, because thirty-six of them
are attached to paragraphs this patch never writes.

## The measurement

`screen.py --class "content-present-partly-displaced"`, 23 of 23 measured, engine
`ea9dfd7+b77d706f61`:

    23 measured, 15 same, 0 better, 8 worse

    65_two_col_full_width_figure_caption      1.75 -> 4.61   +2.86
    admit-card                                1.89 -> 4.69   +2.80
    price-list-2col-dense-right-aligned       2.69 -> 5.27   +2.58
    66_two_col_footnotes_bottom               2.92 -> 3.98   +1.06
    70_magazine_drop_cap_photo_caption        1.16 -> 1.97   +0.81
    table-of-contents-dot-leaders             4.97 -> 5.76   +0.79
    landscape-page-inside-portrait-document   1.02 -> 1.64   +0.62
    very-long-single-column-table             2.38 -> 2.98   +0.60

SCREEN FAIL. Reverted; nothing committed to the engine.

The eight documents that got worse are the ones where a border WAS placed: the three-border change is
enough to move `admit-card` and `price-list-2col-dense-right-aligned` by ~2.7 points, so a border
placed where the page has no rule, or placed on a line whose gap accounting is off by a point, costs
more than the drawing it replaced. That is a warning for the next attempt: the borders that do get
written are not yet free.

## What the next run should do

Do not loosen the guard again — it has now been loosened twice and bought nothing. The work is in the
**table path**: give a rule to the table row or cell that sits under it (`w:top` on `w:tcBorders`,
or a top border on the row's first cell), because that is where 36 of the 39 rules on
`bank-statement-horizontal-rules-only` actually live. That is new work, not a patch to apply.

Second, the 8 regressions say the placement must be verified per document before the class is
re-screened: convert, count `w:pBdr` in `word/document.xml`, and if the count is 0 the change is not
being exercised and a flat screen means nothing.

## Tooling note, and it cost 12 minutes

`scipy` was absent on a fresh pod. Without it `edt()` takes the 40-mask fallback and the screen sat in
"prerender" for two consecutive 280 s calls without measuring anything. SETTLED.md says install it
before measuring; it is worth making `screen.py` refuse to start when `scipy` is missing rather than
spend the run's budget proving it.
