# Three fixes tried against Google's layout, all measured, none landed

Document: `18_centred_heading_left_body_txtpos` (1 p). Baseline through Google: **40/42**, failing
`05_chars_extra` (one U+200B the page never had) and `32_stroke_lines` (both rules lost).

Every change below was built, uploaded, exported and scored with the same 42 checks. None of them is
committed, because none of them helped.

## 1. Rules as paragraph borders (`w:pBdr`) — the construct works, the position does not

`ruleAsBorder()` in `DocxWriter.shape()`: a hairline becomes a one-twip paragraph carrying
`<w:pBdr><w:bottom .../></w:pBdr>` with the indents set to the rule's x range.

| | rules drawn | rules lost | U+200B | score |
|---|---:|---:|---:|---|
| before (drawing) | 0 | 2 of 2 | 1 | 40/42 |
| after (pBdr) | **2** | 1 of 2 | 1 | 40/42 |

Google draws a `w:pBdr` rule, which the drawing never was. But **a paragraph border is placed by
flow, not at an absolute y**: both rules landed at y=807.5 and 808.5, at the foot of the page, when
one of them belongs at the head. A rule this engine draws is absolutely positioned and `w:pBdr` cannot
be. So the construct is right for a rule that sits where its paragraph sits, and wrong for this engine.

## 2. Real page margins (`w:pgMar`) — worse

`w:pgMar` was zero on every document; Google then applies its own. Set to 1440 twips on all sides and
every `w:ind` and every `wp:posOffset` reduced by the same amount, so the absolute positions should be
unchanged:

| | first span | rules | U+200B | score |
|---|---|---|---:|---:|---|
| pgMar 0 | (195.7, 58.6) | 0 | 1 | **40/42** |
| pgMar 1440 | (195.7, **130.6**) | 0 | 0 | **32/42** |

The text moved down 72 pt - exactly one 1440-twip margin - so the offset subtraction did not reach
whatever actually places that line. It did remove the U+200B, which says the anchor was margin-related,
but it costs eight checks to save one.

## 3. Font substitution — already recorded, also worse

See `GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md`: `w:w`, `w:spacing` and embedded faces are all ignored by
Google; scaling `w:sz` to match the width matches the width and scores 19.82 % against 16.28 %.

## What this adds up to

Google's layout differs from this engine's in at least three independent ways - absolute rule
position, page-margin origin, and font metrics - and each fix that addresses one makes another worse.
A single-construct change is not going to close the class. What is needed is to decide **which
coordinate system the .docx should be written in** and then write all of it in that one, rather than
patching constructs one at a time.

That is a design decision, not a patch, and it is the next thing to settle before more code is
written. Writing it down here so the next attempt does not spend another turn on a fourth construct.

## 4. Margin-relative coordinate system — also worse

The reasoning: with `pgMar` at 1440 the first span's **x did not move** (195.7 either way) and only
**y moved +72**, so the missing piece had to be the vertical origin - `w:spacing w:before`, not
`wp:posOffset`. Set `pgMar` to 1440 on all sides and subtracted it from `w:ind w:left`,
`w:ind w:right`, `w:spacing w:before` and every `wp:posOffset`:

| | first span | rules | U+200B | score |
|---|---|---|---:|---:|
| pgMar 0 (shipped) | (195.7, 58.6) | 0 | 1 | **40/42** |
| pgMar 1440, indents only | (195.7, 130.6) | 0 | 0 | 32/42 |
| pgMar 1440, indents + spacing + offsets | (195.7, 61.1) | 0 | 1 | **34/42** |

The vertical origin is closer (61.1 against the page's 58.4) but the score is still four checks worse
than doing nothing, and the U+200B comes back. Rewriting the coordinate system of a document that is
already 40/42 correct in Google is not a trade worth making.

## Four attempts, one conclusion

    rules as w:pBdr                     40/42 -> 40/42    construct right, placement wrong
    w:pgMar + indents                   40/42 -> 32/42    worse
    w:pgMar + indents + spacing + offsets 40/42 -> 34/42  worse
    font metrics (w:w, w:spacing, w:sz) 40/42 -> worse

**None of these is the fix, and that is the finding.** The engine positions everything absolutely
against a zero-margin page; Google lays out in its own coordinate system with its own font
substitution and does not honour the constructs that carry absolute placement. Each construct this
engine leans on is honoured by LibreOffice and dropped by Google, so the failure is not in any one of
them - it is in the assumption that a .docx can be used as an absolutely-positioned canvas.

What that means practically: closing this class is not a patch to `DocxWriter`. It is a decision about
whether the .docx is authored as flowing text (and the layout approximated) or as a canvas (and Google
is accepted as a renderer that will not match). Four measured attempts say the second cannot be made
to work and the first has not been attempted.

Do not try a fifth construct. Decide the model first.
