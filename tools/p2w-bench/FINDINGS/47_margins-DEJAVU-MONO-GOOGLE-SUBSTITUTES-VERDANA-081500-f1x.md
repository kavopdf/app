# 47_margins: Google substitutes Verdana for DejaVuSansMono, and a monospace column grid cannot survive that

Measured 21 Nov 2026, 06:20-08:15 IST, slot 11:52. Class `47_margins` (25 documents, Google).

## The measurement, on one document, through a real Google render

`392_statistical_console_output` failed **41 of 42** checks and the only failure was
`47_margins`. Its `DETAIL` from `verify_google.py`:

    worst_median_pt 0.2   worst_unregistered 2
    margin_bad  []                                  <- the page's left edge MATCHED
    indent_bad  [{page 1, unregistered 2, worst_pt 34.1}]

So the class name is misleading for this document: it is the INDENT half of the check, not
the margin half. The page anchor was 28.0 on both sides.

The source page draws this R line as TWO runs on one baseline:

    x= 28.0   "Multiple R-squared:  0.8412,"
    x=139.2   "Adjusted R-squared:  0.8371"

The engine writes them as ONE `<w:t>` with a single space between them:

    <w:t xml:space="preserve">Multiple R-squared:  0.8412, Adjusted R-squared:  0.8371 </w:t>

That is text-correct. Where the second column LANDS is decided by the font's advance. The
source face is `DejaVuSansMono` at 6.6 pt, one advance for every glyph, so 29 characters put
the second column at 28.0 + 113.1 = 141.1 - the 139.2 the page drew.

**Google Docs has no DejaVu Sans Mono and substitutes Verdana, which is proportional.**
Read off the exported PDF: `Verdana` on every mono span. The second column then lands at
27.8 + Verdana's advance for those 29 characters, 34.1 pt short. Two matched runs fall
outside the 2.0 pt registration tolerance, one of them 34.1 pt out, and the check fails the
document on `len(out) >= 2 and max > DX_WORST_TOL`.

## What a rename to a face Google has does to it

DejaVu Sans Mono advances 0.602051 em on every glyph; Courier New's metric twin Liberation
Mono advances 0.600098 em (fontTools, printable ASCII, this box). 0.325 % apart.

Hand-editing the .docx `w:rFonts` to `Courier New` and rendering through Google again:

    47_margins          FAIL -> PASS     Google exports the face as CourierNew
    53_embedded_faces   PASS -> FAIL     "dejavusansmono kept 0% of 853 chars"

53 reads the .docx, so the rename reads as a total face loss. Adding
`SAME_FACE["dejavusansmono"] = "couriernew"` - which satisfies both of 53's stated rules, a
rename the engine performs and two faces of the same width - closes that. With both:

| document | before | after |
|---|---|---|
| `392_statistical_console_output` | 41/42, `47_margins` | **42/42 PASS** |
| `380_runbook_terminal_output` | `47_margins` + 1 | `47_margins` PASS |
| `383_api_docs_page` | `47_margins` + 6 | `47_margins` PASS |
| `product-catalogue-code-left-price-right` | `47_margins` + 2 | `47_margins` PASS |

`47_margins` clears on 4 of the class's 25 documents. 21 corpus documents draw a monospaced
face; the four above are the ones in this class.

## Why it was NOT kept

The same rename moves the LibreOffice metric the ratchet scores. Measured as a straight A/B
on the same engine, the .docx differing only in the `w:rFonts` name:

    392_statistical_console_output   DejaVu 1.61  ->  Courier New 2.91   (+1.30)
    406_passport_mrz_page            DejaVu 3.45  ->  Courier New 4.05   (+0.60)

`regress.py --check` reads that as two regressions and refuses the commit, correctly: the
0.325 % narrower advance accumulates along an 80-character console line to 1.7 pt, and the
tail of every line drifts past the 5 px tolerance. The rename buys Google at a cost the
ratchet will not accept. Reverted, engine untouched, table restored.

## What would settle it

A representation whose column position does not depend on the face's advance at all: emit
the gap between two runs on one baseline as a `<w:tab/>` with a tab stop at the second run's
own x (111.2 pt after the paragraph's 28 pt indent), instead of concatenating them into one
`<w:t>`. A tab stop is absolute in both renderers, so it cannot drift with the font, and the
LibreOffice score should not move at all. `392`'s `indent_bad` is exactly the two runs of
that one line, so the document is a clean test: the change is right if `47_margins` passes
in Google and `392`'s `share5` stays at 1.61.

## The second defect this run hit, which blocks every class

The corpus pass reported `measured 0 of 213` for four consecutive runs while 101 .docx had
already been converted. Cause and fix are written into `benchmarks/p2w.py` at `_soffice_warm`
and `benchmarks/gate.py` at `_expected_docs`. Both are landed; the corpus now measures 212 of
213 (416 exempt).
