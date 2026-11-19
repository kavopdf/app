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
