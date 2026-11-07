# TXT position score

Share of .txt lines whose leading spaces put them in the column the PDF drew them at.

## How it is measured

    expected column = pdf_x / charW
    actual column   = leading spaces in the .txt line
    pass            = |expected - actual| <= max(2, 8 %)

`charW` is the same character width `TxtWriter` uses - one value for the whole
document, taken from the size the page drew most of its characters at, weighted by
character count. Measuring against a different formula would report a good file as
broken, so the scorer and the writer must always agree.

## The ratchet

    score fell    -> the change is reverted
    score same    -> fine
    score rose    -> accept, and record the new baseline

## History

| Date | Score | Lines | Documents | What changed |
|------|-------|-------|-----------|--------------|
| 6 Nov | 67.2 % | - | 208 | before the rewrite: leading spaces came from each line's own font size |
| 7 Nov | **96.1 %** | 17777 | 208 | one character width for the document, blank lines from the measured pitch, numeric cells right-aligned against their cell's right edge |

The 7 Nov figure is measured over every line of all 208 documents, with the same
formula the writer uses. It is not a sample.

## Where it still loses

| Document | Score | Why |
|----------|-------|-----|
| 64_newspaper_uneven_columns_ad_boxes | 10.4 % | uneven columns: a column that is not a fixed grid cannot be carried by a fixed character width |
| 05_round_company_seal_curved_text | 24.7 % | text on a circle has no column to sit in |
| 60_page_border | 26.6 % | a page border is not text and has no column |

These are the honest floor of what a plain-text column model can express. They are
recorded, not hidden, and they are not reasons to widen the tolerance for everything
else.
