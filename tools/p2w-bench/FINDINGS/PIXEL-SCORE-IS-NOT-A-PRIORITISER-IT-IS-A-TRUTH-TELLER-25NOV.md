# The pixel score does not predict which documents are cheapest to fix. It shows the checks are not the standard.

## What was tested, and why

The obvious use for a visual score is prioritisation: find the documents that are one check away AND already
look right, because those are the cheapest wins. Measured on 213 documents, Google render against source:

    documents with exactly 1 failing check AND SSIM >= 95%:   1
        407_id_card_front_back   ssim 97.4   32_stroke_lines

One. Out of 40 documents that are a single check away from clean.

## And the score does not separate the two groups at all

    SSIM >= 95%:  10 documents   median failing checks 2.0
    SSIM <  95%: 203 documents   median failing checks 2.0

The same median. The visual match and the check count are close to independent, which kills the
prioritisation idea outright: 39 of the 40 one-check-away documents look materially worse than their original,
so making them clean would produce 39 documents that pass every check and still do not look right.

## What it is actually for

    documents passing every applicable check:  42
    documents at 99%+ SSIM:                     4
    documents at 95%+ SSIM:                    10

That gap is the finding. The scorecard says 42 of 213 are done. The render says four of them look like their
original. Both numbers are true and they measure different things: a check asks "is this construct right", and
the product is judged on "does this look like the page the user sent".

So the pixel score is not a lever for choosing work. It is the only number in the tree that says whether the
work being counted is the work the user cares about.

## What follows from it

A run that closes checks and moves neither of those two numbers has not made the product better, and until
today nothing in the report would have shown that. The report now carries the row.

## What this does NOT justify

Ranking by SSIM. The earlier finding stands: SSIM is inflated on sparse pages, where most of the page is white
and two mostly-white pages are structurally similar whatever the ink does. `413_tagged_pdf_actualtext` scores
SSIM 99.2 against an ink overlap of 37.3. Both numbers belong in the row, and neither alone is the answer.

## Measured, not assumed

213 documents, `benchmarks/PIXEL-SCORES-112-DOCS.csv`, one method (`half-res-stride2`), Google render
(`Skia/PDF m160 Google Docs Renderer`) at 150 dpi on a shared pixel grid, cross-referenced against
`benchmarks/gverify/*.json` on engine 981ff1fa35e2cf67.
