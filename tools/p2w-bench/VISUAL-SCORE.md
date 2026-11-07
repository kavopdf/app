# Visual score

Share of documents whose every page answers all eight questions. The questions and
their criteria are in the P2W brief; the tool that answers them is
`tools/p2w-bench/visual.py`.

## How a document passes

    A question is N/A - and passes - when the PDF has nothing of that kind on the page.
    A page passes when every applicable question passes.
    A document passes when every page passes.

## The ratchet

    score fell    -> the change is reverted
    score same    -> fine
    score rose    -> accept, and record the new baseline

## History

| Date | Documents passing | Measured | What changed |
|------|-------------------|----------|--------------|
| 7 Nov | 0 / 4 | 4 | first run of visual.py, on the first four v3 documents |

The first measurement is deliberately small: it exists to prove the tool answers the
questions and to have a floor to climb from. It is not a claim about the corpus.

What it found on those four documents: reading order matched the PDF on 84 %, 9 %,
76 % and 84 % of lines. That is a real defect class the count-based gate cannot see -
every word can be present, in the right place, and in the wrong sequence.

## Why this is separate from the regression gate

`gate.py` counts words, blocks, pages and lines. A document can pass all of those and
still look wrong: text in the wrong reading order, a chart drawn as grey rectangles, a
QR code rendered too small to scan, an image region that is an empty white box. Those
are what this score measures, and they are why the visual check is not optional.
