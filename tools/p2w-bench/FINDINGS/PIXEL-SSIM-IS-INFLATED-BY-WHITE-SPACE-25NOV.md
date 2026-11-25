# SSIM and ink-IoU disagree by 62 points on the same page, and SSIM is the one that lies

## Measured on the 112 documents that carry both metrics

    413_tagged_pdf_actualtext      ssim 99.2    ink_iou 37.3
    411_nested_xobject_transforms  ssim 99.0    ink_iou 44.2
    412_page_labels_roman          ssim 98.4    ink_iou 13.1
    407_id_card_front_back         ssim 98.0    ink_iou 94.4

Three of the four best SSIM scores in the corpus come with an ink overlap under 45 %, and one under 14 %.

    112 documents, Google render vs source, one pixel grid
    SSIM >= 99 %: 3      SSIM >= 98 %: 4      SSIM >= 95 %: 9      SSIM >= 90 %: 44
    ink_iou median 39.0  ssim median 88.6

## Why

SSIM is computed over the whole page. On a sparse page most of the page is white, and two mostly-white pages
are structurally similar whatever the ink is doing. `412_page_labels_roman` is a page of small roman numerals
with almost nothing else: its ink is 13 % of the overlap a correct render would give, and SSIM calls it 98.4 %.

`pixel-score.py` already documents this exact failure for `agree`:

    "a deliberately 90-degree-rotated page scored 95.6 % on it, because both pages are mostly white"

SSIM has the same weakness and the docstring does not say so. The tool warns about the metric it trusts least
and not about the metric it ranks by.

## What this means for the ranking

"3 documents at 99 % or better" is not three documents that look right. It is three documents that are mostly
white. A ranking by SSIM alone puts the emptiest pages at the top, which is the opposite of useful when the
question is "which documents look like their original".

## What to change

SSIM should be reported WITH the ink figure beside it and never ranked on alone. The honest composite for
"does this look like the original" is ink-IoU, which `pixel-score.py` itself describes as "the one that behaves
like a reader: a sideways page scores near 0, a page whose lines moved scores high".

If a single number is wanted, gate SSIM by ink: a page below some ink-IoU floor is not ranked by SSIM at all,
because SSIM has nothing but background to compare. That floor is not set here - it needs a measurement on
documents whose answer is already known, and inventing one would be the same mistake as ranking on SSIM.

## Measured, not assumed

Both columns come from `benchmarks/PIXEL-SCORES-112-DOCS.csv`, 112 documents, Google render
(`Skia/PDF m160 Google Docs Renderer`) against the source PDF at 150 dpi on a shared pixel grid.

## And the remaining 101

`skimage` was absent in this pod, so the first pass scored 101 documents with `defects: no_ssim`. After
installing it, SSIM costs about 66 s per document against roughly 2 s for ink-IoU, so a 3-document slice does
not finish inside a 200 s call. The remaining 101 need slices sized to that cost, not to a document count.
