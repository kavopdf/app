# The rule can be made flow-neutral — and the gate still will not take it

Follows `content-present-partly-displaced-rules-flush-works-displaces-055000-f1x.md`, whose two
claims this run measured and found wrong. **The flush-by-top change is not a precondition, it is a
regression**, and the pBdr carrier can never be flow-neutral at all. The construct that *is*
flow-neutral is in `rules-top-border-FLOW-NEUTRAL-065000-f1x.patch`; it applies, it builds, and it
measures **exactly the baseline on all eight documents it was tried on** — because it declines to
place a border anywhere the ink would move, and on these eight documents it therefore places none.

## 1. A carrier paragraph costs 9.6 pt, whatever it contains

Measured on `18_centred_heading_left_body_txtpos` by editing the emitted `word/document.xml` and
re-rendering through soffice, one variant at a time:

| variant of the carrier paragraph | dy of the line below it |
|:--|--:|
| carrier as the 05:00 patch writes it (pBdr bottom, `w:line=1`, `sz=2`) | **+10.60** |
| carrier with the `w:pBdr` replaced by an inert element | +10.40 |
| carrier with no run at all (empty `<w:p>`) | +10.60 |
| carrier with `w:line="20"` instead of `1` | +11.60 |
| **no carrier paragraph at all** (the control) | **+1.00** |

So the carrier charges the flow **9.6 pt** whether or not it carries a border, whether or not it
holds a run, and whatever `w:line` says. A synthetic two-paragraph document charges 1.8 pt for the
same paragraph; this document charges 9.6. The number is not portable, which is the point: the
pBdr-carrier construct displaces every line under a rule by an amount no two renderers agree on.
That is the whole of `0.00 -> 77.01` on this document, and the `18_displacement` failure the 05:00
run reverted for was not a "residual" — it was the carrier.

## 2. Flush-by-top is not a precondition, it is the same charge once per shape

The 05:00 patch moves every shape into the flow in top order, so each shape becomes a paragraph in
the middle of the page and each one charges that paragraph. Measured with **the border path
switched off** (`ruleAsBorder` returning false at its first line) so that only the reordering is
active:

| document | baseline | flush only, no border |
|:--|--:|--:|
| `bank-statement-horizontal-rules-only` | 0.10 | **17.07** |
| `gst-invoice-horizontal-rules-only` | 0.38 | **15.13** |

A rule per row, one charge each. Putting the drawing's run inside the paragraph already on the page
instead of in a paragraph of its own is no better — 17.04, and 3.63 pt of drift inside table cells.
**The 05:00 finding's "the flush is PROVEN" rests on one document with two rules.** It was never
measured against a document with a rule per row, and it cannot be kept as it stands.

## 3. The construct that IS flow-neutral

`rules-top-border-FLOW-NEUTRAL-065000-f1x.patch` (231 lines, applies to `4e61dfd`):

* **No reordering.** `pageXml` walks `page.blocks` in its own order, exactly as before. A shape is
  still written after the page's paragraphs, in block order — re-ordering them at all is a
  regression (the same 39 drawings in a different order measured **8.57** on
  `bank-statement-horizontal-rules-only`, because a drawing anchored into a table cell moves with
  the paragraph it hangs in).
* **A pre-pass hands each rule to the paragraph that follows it.** `ruleAssignment(page)` maps a
  rule to the first `Para` whose `top` is at or below the rule, one rule per paragraph.
* **The border spends a gap the paragraph was already spending.** The gap down to the rule becomes
  the paragraph's `w:before`, and the rule-to-text distance becomes the border's `w:space`. The
  paragraph's outer top lands on the rule, its text lands where the page drew it, and nothing is
  added to the flow. `resync` is given `before + space` so the model spends what the reader spends.
* **A rule is never lost.** If the paragraph cannot take the border, the shape is written at the
  foot of the page exactly as it always was. (Missing this fallback measured `18_centred` at 5.89
  with 0 drawings and 0 pBdr — a vanished rule is a content regression on `32_stroke_lines`.)
* **A paragraph border spans the paragraph's indents and OOXML gives `w:pBdr` no indent of its
  own.** Rule 1 on `18_centred` spans 56.0..539.3 pt; the centred heading under it is indented to
  102.4, and the border came out 46.4 pt right of the rule and 56 pt past the paper edge. The
  construct therefore requires the rule's edges and the paragraph's to agree within 1.5 pt.
* **A filled rule has no stroke width.** Taking the weight from `lineWidthPt` drew every filled
  rule as a 0.25 pt border while the page drew it 1.2 pt wide; the weight has to fall back to the
  fill's height. With that fixed, `18_centred` went 5.89 -> 0.53 with a border placed.

Measured on the eight documents it was tried on, through LibreOffice, `share@5`:

| document | baseline | this construct |
|:--|--:|--:|
| `18_centred_heading_left_body_txtpos` | 0.00 | **0.00** |
| `411_nested_xobject_transforms` | 0.00 | **0.00** |
| `62_two_col_newsletter_pull_quote` | 0.00 | **0.00** |
| `bank-statement-horizontal-rules-only` | 0.10 | **0.10** |
| `gst-invoice-horizontal-rules-only` | 0.38 | **0.38** |
| `mobile-bill` | 1.55 | **1.55** |
| `315_gazette_notification` | 1.91 | **1.91** |
| `64_newspaper_uneven_columns_ad_boxes` | 3.46 | **3.46** |

**Zero movement — and `pBdr=0` in all eight.** The construct is safe and inert: every rule it could
reach was declined by one of its own guards (indent agreement, `w:space` <= 31, the flow having
reached the rule). A no-op is not a fix, and by the brief's rule ("a change that scores the same is
not kept - it is risk with no gain") it is **reverted**. The patch is kept here so the next run
starts from a working, safe skeleton instead of rebuilding it.

## 4. The wall: the gate measures LibreOffice, where the drawing is already right

This is the finding the class has been circling for four runs and it is not about the rule.

With the construct working and the weight correct, `18_centred` measured **0.00 -> 0.53** the moment
a border was actually placed (thick border, correct y, text within 2 pt). The reason is structural:
`regress.py` scores `share@5` on a **LibreOffice** render, LibreOffice draws the floating
`<w:drawing>` exactly where the PDF drew it, and a `w:pBdr` can never be pixel-identical to it —
different construct, different rasteriser, a fraction of a point of ink on a 483 pt line. So:

* every document whose rules are already correct in LibreOffice **must** get worse the moment its
  rules become borders, however well they are placed;
* the documents that need the fix are exactly the ones Google fails (`32_stroke_lines`, 145 docs) —
  and Google is not what the gate measures.

**A fix that Google needs is always a small LibreOffice regression, so the gate cannot pass it, and
the brief's rule is absolute: nothing lands that makes any document worse.** This class cannot be
closed by the fixer under the present gate. It needs a decision that only a human can take:

1. **gate this class in Google** — score `32_stroke_lines` and `05_chars_extra` on the Google result
   for the affected documents, and `share@5` on LibreOffice for the rest; or
2. **declare the rule class out of scope**, in which case `RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`
   and `RULES-PBDR-*` should be marked closed rather than left as a queue the fixer keeps re-entering
   (four runs have now spent themselves here); or
3. **accept a stated tolerance** — the construct costs ~0.5 `share@5` on a clean document and buys a
   PASS on `32_stroke_lines` in Google. Nobody has authorised that trade; it is not the fixer's to
   authorise.

## What is ruled out, so the next run does not pay for it again

* **The pBdr carrier paragraph.** 9.6 pt, measured four ways. Never.
* **Flush-by-top, as the 05:00 patch writes it.** 0.10 -> 17.07 on a rule-per-row document with the
  border path off. The reordering is the regression, not the border.
* **Reordering shapes at all**, including "emit them all at the end in a different order": 8.57.
* **A drawing's run inside the neighbouring paragraph** instead of a paragraph of its own: 17.04.
* **`lineWidthPt` as the border weight** for a filled rule: 0.25 pt for a 1.2 pt rule, 5.89 on
  `18_centred`.
* **The flush as a precondition for the border.** The border needs the rule and the paragraph, not
  the flow — `ruleAssignment` finds both without moving anything.

## Confidence

**High** on every number above: each is a `share@5` from `benchmarks/p2w.py` on a soffice render of
the working tree, compared against `RANKING.csv` for the same document, and the dy figures come from
rendering the emitted XML and reading line boxes back out of the PDF.
**High** that the construct in the patch is flow-neutral: it measures exactly the baseline on eight
documents, and the mechanism (a border spending a gap the paragraph already spends) is what the
0.00 control shows.
**High** that the blocker is now the gate's renderer and not the engine.
**Medium** on how many corpus documents the construct would actually reach once the indent guard is
relaxed — that is one corpus pass away, and it is worth spending only after the gate question above
is answered.
