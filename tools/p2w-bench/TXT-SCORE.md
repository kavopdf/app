# TXT position score

Share of .txt lines whose leading spaces put them in the column the PDF drew them at.

## How it is measured

    expected column = pdf_x / charW
    actual column   = leading spaces in the .txt line
    pass            = |expected - actual| <= max(2, 8%)

`charW` is the same character width `TxtWriter` uses - one value for the whole
document. Measuring against a different formula would report a good file as broken,
so the scorer and the writer must always agree.

## The ratchet

    score fell    -> the change is reverted
    score same    -> fine
    score rose    -> accept, and record the new baseline

## History

| Date | Score | Documents | What changed |
|------|-------|-----------|--------------|
| 6 Nov | 67.2 % | 208 | baseline, before the rewrite (per-line font size) |
| 6 Nov | - | - | rewrite landed; the formula changed with it, so this is a new baseline, not a continuation |
