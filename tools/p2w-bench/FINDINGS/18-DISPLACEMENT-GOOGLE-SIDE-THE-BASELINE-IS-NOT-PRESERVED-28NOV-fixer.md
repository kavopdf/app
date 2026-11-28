# 18_displacement: Google does NOT preserve the cell baseline — the premise of the `w:line` patch is false

**28 Nov 2026, fixer slot 08:24 IST. The 05:54 run's lead was: "give the cell the font's natural line box
and move the identical difference into `w:before`; this predicts a ZERO move in Google if and only if
Google is already preserving the baseline today." It is falsifiable in one document and it has now been
falsified. The lead's own gap was that no Google export of `35_four_typefaces_one_page` existed anywhere
in the repository. One does now.**

## The measurement

Source PDF vs the Google export of the same `.docx` (uploaded, converted, exported as PDF), row baselines
read from both with PyMuPDF, `line.bbox[1]`:

| row | source | Google export | dy |
|:--|--:|--:|--:|
| header | 139.18 | 137.22 | **−1.96** |
| BCO-401 | 158.18 | 155.97 | −2.21 |
| BCO-402 | 177.18 | 174.72 | −2.46 |
| BCO-403 | 196.18 | 193.47 | −2.71 |
| BCO-404 | 215.18 | 212.22 | −2.96 |
| BCO-405 | 234.18 | 230.97 | −3.21 |
| BCO-406 | 253.18 | 250.47 | −3.71 |
| body lines above the table (45.53, 64.76, 92.74, 112.91) | — | 45.81, 64.12, 93.65, 113.54 | +0.28, −0.64, +0.91, +0.63 |

Google's baselines are not the page's, and the error is not LibreOffice's either: LibreOffice puts these
cells **+3.70 pt low** (the 05:54 run's number) and Google puts them **1.96–3.71 pt high**. Two renderers,
two different signs, and the one the score is taken in moves.

`71_invoice_space_aligned_no_rules`, same method, measured by a second agent on an existing Google export
of the same engine and source (not a fresh upload — that is the weaker half of this evidence, stated
because it is weaker): the six cells written `w:line="180"` read **+1.12 pt** and the one cell written
`w:line="12"` reads **+2.02 pt**. The `w:line` value does move the Google baseline, by ~0.9 pt between the
two settings, and not to zero.

## What is now true

- The 05:54 lead's premise ("Google already preserves the baseline, so the patch predicts zero move") is
  **false**. Google is 2–4 pt high on this document, and the amount depends on the `w:line` value. A patch
  that moves the difference into `w:before` therefore predicts a *change* in Google, not no change — and
  an unpredicted change in the renderer the score is taken in is exactly what the two reverts in this
  class's history were.
- The two renderers disagree in **sign**, so a change validated on `soffice` cannot be inferred into
  Google in this class at all. Any future attempt must take the Google export before it builds.
- The row-level half of the error is a pitch error and is measured separately in
  `18-DISPLACEMENT-TRHEIGHT-ATLEAST-IS-CONTENT-28NOV-fixer.md` (18.75 laid against 19.00 asked).

What would prove this wrong: a fresh upload of the shipped `.docx` for `35_four_typefaces_one_page` whose
export lands the seven rows at their source positions. The export used here reproduces the stored Google
verdict for this document digit for digit (−2.8 med, 3.3 worst, 52 runs), which is the control.
