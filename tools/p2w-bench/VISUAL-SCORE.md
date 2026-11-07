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
| 7 Nov | 12 / 13 | 13 | v3 batch 4 (372-394), after three measurement fixes in visual.py — rows compared by baseline and text instead of line index, and a soft hyphen's U+0000 treated as a space. The 0 / 4 row above was measured with the old index pairing and is superseded; those four have not been re-measured. |

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

## What the batch-4 measurement changed

The first measurement is only worth having if the questions are answered the same way twice, and
three of the eight were not.

Question 1 compared line *i* of the PDF with line *i* of the render. Rule 3 of the brief forbids
index pairing, and it charged the writer for a construct it is required to use: three labels on one
baseline become one paragraph with a tab stop at each label's x, so the two lines that are no
longer separate shifted every line after them. 382_architecture_diagram scored 14 % on a page whose
rows were all in the right place; it scores 67 % now, which is its real 77 pt drift.

Grouping a row by the line's box top rather than its baseline split "TRANSPORT" off an org chart
row: two fields on one baseline set in different faces report tops 3 pt apart. 374_org_chart went
from 55 % to a pass on that alone.

A soft hyphen or zero-width joiner reaches the text extractor as U+0000. It was kept in the PDF's
text and dropped from the render's, so 391_survey_questionnaire_grid was charged for two words
present on both sides. It is now a space — not deleted, because deleting it welds "strongly" to
"agree".

Question 7 had been answering `unsure` on every page: pyzbar needs a system libzbar this image does
not carry and cannot install. It now falls back to OpenCV's QR and barcode decoders.
