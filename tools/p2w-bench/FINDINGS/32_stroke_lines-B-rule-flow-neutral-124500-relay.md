# Why the flow-neutral top-border rule patch declines, and whether a preceding-paragraph bottom border would be neutral

Scope: read-only analysis of `kavopdf/app` at `HEAD`, the patch
`tools/p2w-bench/FINDINGS/rules-top-border-FLOW-NEUTRAL-065000-f1x.patch`, its finding
`content-present-partly-displaced-rules-are-flow-neutral-065000-f1x.md`, the engine source, and
measurement of the source PDFs. Nothing in the repository was modified and nothing was built.

---

## 0. Provenance of the PDFs (the corpus is not in the repo)

The corpus PDFs are **not** in the repository. `benchmarks/` contains only
`corpus-extra/` (3 PDFs) and `realworld/` (2 PDFs); none of the eight documents named in the
06:50 finding is there. They are fetched by the bench harness itself from the project's own
release, `benchmarks/p2w.py:66,888`:

```
ROOT="/scratch/work/p2w"; CORPUS=ROOT+"/corpus"; DOCX=ROOT+"/out"
...
sh(f"gh release download corpus-v1 --repo kavopdf/app -p '{z}.zip' -O '{c}' --clobber",130)
```

with `ZIPS=["p2w-all-groups","p2w-batch-1","pdf-to-word-test-corpus-v3","p2w-round2-additions"]`
(`p2w.py:83`). All four assets exist on release `corpus-v1` and were downloaded and unpacked, so
**part 2 was done on the real source PDFs** — 213 PDFs, 164 of them containing at least one
horizontal hairline, 2136 hairline rules in total.

Geometry was read with PyMuPDF (`get_drawings()` for the rules, `get_text("dict")` for the text
lines), and the engine's own arithmetic (`DocxWriter.java:4322`, `absTop = b.y - 0.8 * hairlinePt(size)`,
`hairlinePt = min(0.069*size, 0.6485)`) was applied to the measured baselines so that the numbers
below are in the same units the guard compares.

---

## 1. The exact guard that declines, and its arithmetic

The patch declines in one place, `pendRuleConsume`, which returns `-1` ("the rule must keep its
drawing") from **two** conditions. Patch lines 151–175, quoted verbatim:

```
151|    private static int pendRuleConsume(float absTop, int leftTw, int rightTw, Ctx ctx) {
152|        if (ctx.pendRulePt < 0f) return -1;
153|        float from = flowTopPt(ctx);
154|        float gapPt = ctx.pendRulePt - from;
155|        float spacePt = absTop - ctx.pendRulePt;
156|        ctx.pendRulePt = -1f;
157|        ctx.pendRulePlaced = false;
158|        // w:space is whole points and its schema maximum is 31; a rule further than that above
159|        // the text, or one the flow has not reached, keeps its drawing.
160|        if (ctx.inColumn || ctx.newPage || gapPt < -0.5f || spacePt < 0f || spacePt > 31f) {
161|            return -1;
162|        }
163|        // The border spans this paragraph's indents and cannot be given its own (see
164|        // ruleAssignment), so the two must agree before the rule is written this way.
165|        float ruleLeftPt = (float) (ctx.pendRuleLeftTw / TWIPS_PER_PT);
166|        float ruleRightPt = (float) (ctx.pageWidthPt - ctx.pendRuleRightTw / TWIPS_PER_PT);
167|        float textLeftPt = (float) (leftTw / TWIPS_PER_PT);
168|        float textRightPt = (float) (ctx.pageWidthPt - rightTw / TWIPS_PER_PT);
169|        if (Math.abs(ruleLeftPt - textLeftPt) > 1.5f
170|                || Math.abs(ruleRightPt - textRightPt) > 1.5f) {
171|            return -1;
172|        }
173|        ctx.pendRulePlaced = true;
174|        return Math.round(spacePt);
175|    }
```

### 1a. The arithmetic of the first guard (line 160)

* `gapPt = pendRulePt - flowTopPt(ctx)` — the rule's y minus where the flow already is. Negative
  means the flow has already reached or passed the rule (the shapes are attached after the page's
  paragraphs, and a row/table edge or an anchored line can leave `flowY` below the rule). `-0.5 pt`
  is the tolerance.
* `spacePt = absTop - pendRulePt` — the line-box top of the following paragraph minus the rule's y,
  i.e. the distance the border's `w:space` has to carry. It must be `0 <= spacePt <= 31` because
  `w:space` is whole points and its schema maximum is 31.
* `ctx.inColumn` — the following paragraph is a table cell; `ctx.newPage` — it is the first line of a
  page. Either declines outright.

**This guard is not what rejects the corpus.** Measured over the 2136 corpus rules: `spacePt` in
`[0, 31]` for **2055 (96.2 %)** — median 10.19 pt, p95 27.93 pt. So the `w:space <= 31` limb the
06:50 finding lists as one of the reasons accounts for 3.8 % of rules, not the 100 %.

### 1b. The arithmetic of the second guard (lines 165–172) — this is the one that declines everything

`pendRuleLeftTw`/`pendRuleRightTw` are set in `pendRuleFrom` (patch lines 135–137) as
`round(s.xPt * 20)` and `round((pageWidthPt - (s.xPt + s.wPt)) * 20)`, so the comparisons reduce to

* left: `|s.x - leftTw/20| <= 1.5` — the rule's left end vs the paragraph's left indent, and
* right: `|(s.x + s.w) - (pageWidthPt - rightTw/20)| <= 1.5`.

`leftTw` and `rightTw` come from `flowFromBox` (`DocxWriter.java:4204–4234`):

```
4204|        int leftTw = (int) Math.max(0L, Math.round(b.x * TWIPS_PER_PT));
4205|        int rightTw = 0;
...
4224|        } else if (p.align == 1) {          // centred
4225|            float centre = (b.x + b.right) / 2f;
4226|            if (Math.abs(centre - ctx.pageWidthPt / 2f) > 2f) {
4227|                rightTw = ... (pageWidthPt - b.right)
4228|            } else {
4229|                leftTw = 0;                  // centred on the paper: whole text area
4230|            }
4231|        } else if (p.align == 2) {          // right-aligned
4232|            leftTw = 0;
4233|            rightTw = ...
4234|        }
```

**For a left-aligned paragraph — the ordinary case — `rightTw` is 0, so `textRightPt = pageWidthPt`
exactly.** The right-hand test therefore collapses to an identity about the *writer*, not about the
document:

```
|(s.x + s.w) - pageWidthPt| <= 1.5      i.e.  the rule must reach within 1.5 pt of the PAPER edge
```

A hairline in a PDF almost never does: it is drawn to the text-area margin, which sits the right
margin inside the paper. Measured over the 2136 corpus rules, the distance from the rule's right end
to the paper edge is:

| | pt |
|:--|--:|
| min | 0.00 |
| p25 | 39.68 |
| median | **45.35** |
| p75 | 56.69 |
| p95 | 300.28 |
| max | 701.89 |

**Rules passing the right-edge test: 1 of 2136 (0.05 %). Rules passing both edge tests: 0 of 2136
(0.00 %).** The left test alone passes 563 of 2136 (26.4 %) — its median is 3.00 pt, because a rule
in a ruled table starts at the cell's padding, 3 pt left of the text.

The guard is thus *unsatisfiable by construction* for a left-aligned following paragraph: the
border it would write spans from the paragraph's left indent to the **paper's right edge**, which is
over-long by the right margin — 45.35 pt on `bank-statement-horizontal-rules-only`, 42.52 pt on
`mobile-bill`, 28.00 pt on `315_gazette_notification`, 56.00 pt on `18_centred_heading_left_body_txtpos`.
Declining is the correct thing for the patch to do, but the defect it is protecting against is that
`w:pBdr` has no indent of its own and the writer gives a left-aligned paragraph `w:right="0"`.

This is confirmed independently by the later finding
`content-present-partly-displaced-rule-guard-was-not-the-blocker-100700-f1x.md`, which recorded the
guard's own diagnostic on `bank-statement-horizontal-rules-only` as
`rule 45.35..549.93 text 45.35..595.28` — the same 45.35 pt, and the paragraph's rectangle running to
595.28, the paper width.

### 1c. Upstream gates that can also drop a rule before the guard is ever reached

In `ruleAssignment` (patch lines 98–124): not a `Shape`; not `isHairline`; `|hPt| > |wPt|` (vertical);
`rgb < 0`; no `Para` with `q.top >= s.topPt - 0.5` (`pick < 0` → `continue`, nothing assigned); a
paragraph that already carries a top border (`out[j] >= 0`). And after assignment, a pending rule that
is set for a paragraph the patch never writes is silently overwritten — on
`bank-statement-horizontal-rules-only` 36 of 39 assigned rules belong to paragraphs emitted by the
table writer rather than `flowFromBox`, so `pendRuleConsume` is reached 3 times for 39 rules (10:07
finding, section "Why 3 and not 39").

---

## 2. Measured gaps above and below the rule, from the source PDFs

Answer to the question as posed: **the rule is never flush with the following paragraph's top, and
the gap is not the reason it declines.** There is a gap of 4.68–20.20 pt of ink below every rule, and
the engine's line box (`baseline − 0.8 * hairlinePt`) starts 9.44–29.48 pt below it. All of those
values are inside the `0..31` window, so the space limb of the guard passes; the edge limb is what
rejects them.

Per-rule geometry (points; `above` = previous line's ink bottom → rule top, `below` = rule bottom →
next line's ink top, `spacePt` = rule top → engine line-box top, `dLeft`/`dRight` = the two edge
mismatches the guard computes):

| document | rule y | above | below | spacePt | dLeft | dRight | following line |
|:--|--:|--:|--:|--:|--:|--:|:--|
| `18_centred_heading_left_body_txtpos` | 110.0 | 8.06 | 20.20 | 29.48 | 56.00 | 56.00 | "NOTICE INVITING APPLICATIONS…" (centred) |
| `18_centred_heading_left_body_txtpos` | 793.9 | 204.05 | 4.87 | 11.56 | 0.00 | 56.00 | "Notice DIC/TMK/2025-26/0447…" |
| `bank-statement-horizontal-rules-only` | 72.3 | 4.52 | 4.79 | 10.56 | 0.00 | 45.35 | "Account holder: KASTURA HOME…" |
| `bank-statement-horizontal-rules-only` | 121.8 | 7.12 | 4.68 | 9.44 | 3.00 | 45.35 | "01-09-2026" |
| `bank-statement-horizontal-rules-only` | 140.2 | 7.12 | 4.68 | 9.44 | 3.00 | 45.35 | "02-09-2026" |
| `gst-invoice-horizontal-rules-only` | 147.3 | 11.43 | 14.81 | 20.00 | 3.00 | 45.35 | "Sr." |
| `gst-invoice-horizontal-rules-only` | 175.8 | 6.39 | 4.81 | 10.00 | 3.00 | 45.35 | "1" |
| `mobile-bill` | 68.5 | 4.56 | 10.86 | 16.19 | 3.00 | 42.52 | "Mobile number" |
| `mobile-bill` | 111.3 | 6.14 | 4.86 | 10.19 | 3.00 | 42.52 | "Address" |
| `315_gazette_notification` | 60.0 | 4.20 | 6.68 | 11.61 | 0.00 | 28.00 | "PUBLISHED BY AUTHORITY" |
| `315_gazette_notification` | 78.0 | 4.32 | 9.06 | 13.64 | 0.00 | 28.00 | "(1)" |
| `64_newspaper_uneven_columns_ad_boxes` | 70.0 | 4.27 | 8.64 | 21.48 | 0.00 | 56.00 | "Water scheme for Vinayaka Nagar…" |
| `64_newspaper_uneven_columns_ad_boxes` | 793.9 | 72.16 | 5.32 | 11.59 | 0.00 | 56.00 | "The Tumakuru Times • 19 Sept…" |
| `62_two_col_newsletter_pull_quote` | 793.9 | 329.01 | 5.32 | 11.59 | 0.00 | 56.00 | "The Kunigal Herald • Issue 47…" |

Summary over the eight documents named in the 06:50 finding (94 hairline rules; `411_nested_xobject_transforms`
has none):

| document | rules | median above | median below | median spacePt | rules passing left | rules passing right |
|:--|--:|--:|--:|--:|--:|--:|
| `18_centred_heading_left_body_txtpos` | 2 | 106.06 | 12.54 | 20.52 | 1 | 0 |
| `411_nested_xobject_transforms` | 0 | – | – | – | – | – |
| `62_two_col_newsletter_pull_quote` | 1 | 329.01 | 5.32 | 11.59 | 1 | 0 |
| `bank-statement-horizontal-rules-only` | 39 | 7.12 | 4.68 | 9.44 | 6 | 0 |
| `gst-invoice-horizontal-rules-only` | 16 | 6.39 | 4.81 | 10.00 | 4 | 0 |
| `mobile-bill` | 32 | 6.14 | 4.86 | 10.19 | 4 | 0 |
| `315_gazette_notification` | 2 | 4.26 | 7.87 | 12.62 | 2 | 0 |
| `64_newspaper_uneven_columns_ad_boxes` | 2 | 38.22 | 6.98 | 16.54 | 2 | 0 |

Two facts that matter for part 3 fall out of the same table:

* **the gap above and the gap below are different numbers.** `|above − below| <= 1 pt` for only
  **7 of 94** rules in these eight documents (4 on `bank-statement`, 3 on `mobile-bill`, 0 elsewhere);
  the median absolute difference is ~2.3 pt, and on the footer rules it is 198.7 pt
  (`18_centred`), 66.8 pt (`64_newspaper`), 323.7 pt (`62_two_col`).
* **the gap above exceeds 31 pt** (the `w:space` schema maximum) for **217 of 2133 corpus rules
  (10.2 %)**, up to 688 pt.

Caveat, stated plainly: the guard's `gapPt` term is `pendRulePt − flowTopPt(ctx)`, and `flowTopPt` is
engine state (the model's flow position after the preceding blocks, including table/row edges and
`anchorBox` placements). It cannot be recomputed from the PDF alone, so this note does **not** claim
how often `gapPt < -0.5` fires. The `inColumn` and `newPage` limbs are likewise engine state. The
edge limb and the `spacePt` limb are fully computable from the PDF, and those are the two reported
above: `spacePt` passes 96.2 % of rules, the edge test passes 0.

---

## 3. Would a preceding-paragraph `w:pBdr` bottom, with `w:space` = the gap below the rule and the following paragraph's `w:before` reduced by the same amount, be flow-neutral by construction?

**No — not as posed, and not by construction even after the arithmetic is fixed.**

### 3a. As posed it is not even geometrically correct

A bottom border's `w:space` is measured from the *preceding* paragraph's text bottom, not from
anything about the following paragraph. So the value that lands the ink on the rule is the gap
**above** the rule (`R − B`), not the gap below it. With `w:space` set to the gap below, the ink lands
`|above − below|` away from the rule — 0 pt in only 7 of 94 rules measured, 2–3 pt typically, and
~200–330 pt on the footer rules where the rule sits far below the last body line. So the variant, as
described, misplaces the rule on almost every rule in the corpus before flow is even discussed.

### 3b. Corrected to `w:space` = gap above, it is neutral only in the idealised reader model

Take `B` = the preceding paragraph's box bottom, `R` = the rule's y, `T` = the following paragraph's
box top, `before` = the following paragraph's `w:before` as the engine already computes it
(`before = T − B`), `s` = `w:space`, `w` = border width in points (`w:sz / 8`).

A reader that draws the border `s` below the preceding text and grows the paragraph's height by
`s + w` gives the following paragraph's box top as `B + s + w + (before − d)`. Flow-neutral requires

```
B + s + w + before − d = T = B + before   =>   d = s + w,   and ink on the rule => s = R − B
```

so the neutral form is **`w:space` = gap above the rule, `w:before` reduced by (gap above + border
width)**. That identity holds, so in that reader model the construct is neutral *in principle* — the
same model the top-border patch relies on (`modelTw = beforeTw + ruleSpacePt * TWIPS_PER_PT`, patch
line 217).

What breaks it:

1. **The border's own width is not compensated by "the same amount".** Reducing `before` by `s` alone
   leaves the following text `w` lower than the page drew it: 0.75 pt at `sz=6`, 1.2 pt for the 1.2 pt
   filled rule the 06:50 finding fixed. One error per rule, and on the paragraphs that take the pitch
   branch (`before` derived from `pitch`, not from `absTop`) it carries into the next row — on
   `bank-statement-horizontal-rules-only` (39 rules, pitch branch in use, `0.45 pt/row` already
   leaking per the bankpitch findings) that is up to ~29 pt down the page.
2. **`d` is a subtraction from a value computed elsewhere, so it clamps at 0.** `before` is 0 in
   several live branches: the page's first line (`ctx.newPage`), a paragraph placed at a table or row
   edge (`afterTablePt`), an anchored/`positioned` line, and whenever the flow has already overshot
   (`absBeforeTw` floored at 0, `spacing()` floors `b` at 0). Where `before < s + w` the compensation
   cannot be applied and everything below shifts down by the un-compensated remainder — the exact
   failure the top-border patch avoids with its `gapPt < -0.5f` guard, because it *sets*
   `before = R − flowTop` from two absolute coordinates instead of subtracting from a third party's
   number. (Honest bound: on the 94 rules measured, the pitch-derived `before` was ~17.8 pt against a
   needed ~5–8 pt, so **0 of 94 clamp** — this is a latent breaker on this corpus, not an observed one.)
3. **`w:space <= 31 pt`.** 217 of 2133 corpus rules (10.2 %) sit more than 31 pt below the preceding
   text, up to 688 pt. A bottom border cannot reach them at all: the ink lands up to ~650 pt too high.
   The top-border variant is exposed to the same 31 pt ceiling, but on the *other* side, and the
   measured `spacePt` distribution there passes 96.2 % of rules.
4. **Page breaks.** A bottom border belongs to the preceding paragraph, so when the following
   paragraph starts a new page the border is drawn at the foot of the previous page, not at the rule's
   y — and the `w:before` reduction at a page top is absorbed or dropped by the reader, so the error
   is doubled rather than cancelled. The top-border variant has the mirror-image failure, but it is
   explicitly guarded (`ctx.newPage` in the guard at patch line 160, which keeps the drawing).
5. **It inherits the same unsatisfiable edge test.** The border spans the preceding paragraph's indent
   box, and `flowFromBox` gives a left-aligned paragraph `w:right="0"` (`DocxWriter.java:4205`), so the
   border still runs to the paper's right edge — over-long by the right margin — unless the same 1.5 pt
   edge guard is applied, and that guard rejects **0 of 2136** corpus rules. The variant moves the
   indent problem to the other neighbour; it does not escape it.
6. **The hook problem is unchanged.** On `bank-statement-horizontal-rules-only` 36 of 39 rules attach
   to paragraphs the table writer emits, which `flowFromBox` never writes. A preceding-paragraph
   variant hooks the same paragraphs and therefore reaches the same 3.

### 3c. Verdict

* Flow-neutral **by construction**: only in the corrected form (`w:space` = gap *above*, `before`
  reduced by gap-above + `w:sz/8`), and only in a reader that adds `space + width` outside the
  paragraph's box and honours a reduced `w:before` at a page top. That is an assumption about the
  reader, not a property of the construct.
* As written in the question — `w:space` = gap below, `before` reduced by the same amount — it is
  neutral in no sense: the ink is misplaced by `|above − below|` on 87 of 94 rules, and the text below
  every rule is pushed down by the uncompensated border width.
* Compared with the top-border construct, the bottom-border construct is strictly worse on this
  corpus: it needs the same edge guard (0/2136 pass), reaches the same 3 of 39 rules through the
  paragraph hook, adds a 31 pt ceiling that 10.2 % of rules already exceed, adds a clamp-at-zero hazard
  that the top-border form has no analogue for, and adds the wrong-page failure at page breaks.

### 3d. The caveat that applies to both variants

The 06:50 finding's "**High** that the construct in the patch is flow-neutral" rests on a table in
which every one of the eight documents measured **exactly** the baseline *and* `pBdr=0` in all eight —
i.e. neutrality was measured on a no-op. The only measurement with a border actually placed was
`18_centred` at `0.00 -> 0.53`, which the finding attributes to rasteriser difference between a
`w:pBdr` and a `<w:drawing>`; a 0.53 `share@5` on a single document cannot distinguish that from a
sub-point flow displacement. So *both* variants are "flow-neutral by construction" as an argument
about OOXML semantics, and **neither has been measured with borders actually placed**. Any claim to
the contrary should be checked by converting a document, counting `w:pBdr` in `word/document.xml`, and
reading the line boxes back out of the render — the 10:07 finding's own recommended gate.

---

## Files / commands behind the numbers

* `rules-top-border-FLOW-NEUTRAL-065000-f1x.patch` (231 lines), read in full; guard at lines 151–175.
* `content-present-partly-displaced-rules-are-flow-neutral-065000-f1x.md` (143 lines), read in full.
* `content-present-partly-displaced-rule-guard-was-not-the-blocker-100700-f1x.md` (88 lines) —
  independent confirmation of the 45.35..549.93 vs 45.35..595.28 diagnostic and of the table-path hook.
* `DocxWriter.java:149–169` (`spacing`), `4204–4234` (`leftTw`/`rightTw`), `4322` (`absTop`),
  `3875–3887` (`hairlinePt`); `PdfToWord.java:96–133` (`Para.top` = first-line y).
* Corpus: release `corpus-v1` of `kavopdf/app`, assets `p2w-all-groups`, `p2w-batch-1`,
  `pdf-to-word-test-corpus-v3`, `p2w-round2-additions` (213 PDFs, 164 with hairlines, 2136 rules).
* Measurement scripts kept outside the repo: `/scratch/work/measure_rules.py`,
  `/scratch/work/guard_census.py`, `/scratch/work/corpus_census.py`.
