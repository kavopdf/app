# `w:trHeight hRule="exact"` on the ruled/whitespace table path: measured, no document worse

25 Nov 2026, fixer run (slot 13:00). Engine HEAD `318c5d4a` + this one-line change.

## The construct

`DocxWriter.java:6584` wrote every row of the main table path with
`<w:trHeight w:val="H" w:hRule="atLeast"/>`. `atLeast` is a *floor*, so the renderer lays the row at
its own content height instead of `H`, and Google's content height is not ours — the row drifts, one
sign, down a dense table. This is construct (3) of the three in `DOCS-ROOT-CAUSES-24NOV.md`
(`18_displacement`, 94 of 102 documents, largest single leverage in the corpus at 54.8 clean documents).

The second `w:trHeight` site (`:2282`, the ruled-column path) **already** writes `exact`, and the file
records its own measured case (`annual-review-2col-uneven-columns`: atLeast → 2 pages, exact → 1 page,
all 41 lines present). So the corpus was carrying two different rules for the same question.

## Census at HEAD (all 213 emitted `word/document.xml`)

| hRule | rows |
|---|---:|
| `atLeast` | **2,278** |
| `exact` | 36 |
| total | 2,314 |

143 of 213 documents carry at least one row; the densest are `324_loan_amortisation_schedule` (246),
`bank-statement-5-pages` (125), `very-long-single-column-table` (99), `041122-Account_Opening_Form` (88).

## The risk, and the test that answers it

`exact` is a *cap*, so a row whose content is taller than `H` is clipped and the text is lost. That is the
one way this change could make a document worse, and it is a renderer-visible fact, so it is measured
against an independent reference: **the source PDF's own text**.

30 documents (the 30 densest by `atLeast` row count, 1,328 rows of the corpus's 2,278) converted by the
baseline engine and by the patched engine, both rendered with LibreOffice to PDF, both compared with the
source PDF.

| | result |
|---|---|
| documents losing words vs their own baseline | **0** |
| documents losing words vs the source PDF | **0** |
| documents whose page count rose | **0** |
| documents whose page count fell toward the source | **2** |
| documents unchanged | 28 |

The two that moved both moved **toward** the source:

| document | pages old → new | words old → new | source |
|---|---|---|---|
| `041122-Account_Opening_Form` | 10 → **9** | 7908 → 7778 | 9 pages, 7448 words |
| `Account_Opening_Form_Fillable_filled` | 11 → **10** | 7917 → 7787 | 9 pages, 7462 words |

Both carried more words than the source on *both* sides; the 130-word drop is the repeated table header
that no longer lands on the extra page. Neither is a word loss against the page.

## The structural check that makes clipping impossible, not merely unobserved

A render test can only say "no text was lost on the 30 I looked at". The stronger question is whether a
row can *ever* declare less height than its own content under this change. Answered by reading the 30
patched `.docx` files directly - every `<w:tr w:trHeight w:hRule="exact">`, against the sum of its cells'
paragraph heights (`w:line` + `w:before`, the same numbers the engine writes):

    exact rows: 1371   rows whose declared height is LESS than their cell content: 0

Zero, across 1,371 rows. That is not a sample result - it is the engine's own arithmetic
(`rowHeightTw = max(rowTwHere, rowLineTw)`, and on the re-cut path floored at `paraContentTw + ruleTwHere`),
so the declared height is a floor of the content by construction. `atLeast` was never buying the content
room the page did not have; it was buying the renderer's own opinion of the content, which is the drift.

This is the second, independent instrument on the same claim, and it agrees with the render test.

## What this does not settle

- **Google was not run.** This measurement is LibreOffice, which is the proxy the charter says is not the
  truth. What it establishes is narrow and worth having: the change clips nothing and adds no page. The
  `18_displacement` gain itself is a Google claim and must be measured with `gverify`.
- The LibreOffice gate *does* see this change — 2 page counts and 2 word counts moved — so it is not
  invisible to `regress.py` as one section of `DOCS-ROOT-CAUSES-24NOV.md` claimed, and the other section's
  claim that it moves the proxy is the correct one.
- Whether Google honours `exact` as the page's own pitch (the 0.75 pt ladder in
  `18_displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md`) is the next measurement, and it is the one
  that decides whether `18_displacement` closes.

## Reproduce

    bash tools/p2w-bench/build-engine.sh            # baseline
    python3 <convert 30 densest>                    # -> old/
    soffice --convert-to pdf --outdir pdfold old/*.docx
    # apply the one-line change, rebuild, repeat -> new/
    # compare page count and word count of each render against the source PDF
