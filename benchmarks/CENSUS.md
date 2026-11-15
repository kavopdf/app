# Census - the evidence layer

## Why it exists

`ATTEMPTS.json`: 19 attempts over four classes, **zero kept**, fourteen of them on one
class. The fixer was not failing at patching. It was guessing at *what* to patch, because
it was given a number and a name and nothing else:

    415_inline_images, 89.04 %@5, content-loss, max 153 pt, 1 page

From that, a mechanism had to be inferred. A pixel score cannot tell you that four images
are missing. A structural diff can.

## What it measures

For every document the ranking calls defective, the source's element counts beside the
output's:

    src_chars / docx_chars        characters
    src_images / docx_images      raster images  vs  inline pictures
    src_drawings / docx_cells     drawn rules    vs  table cells
    src_annots                    annotation objects (reported, not compared)

plus `worst_page`, so a reader can open the page that carries the worst displacement.

## The signal is a hypothesis, and it says so

The counts are facts. `signal` is a candidate mechanism, and it fires only when the
evidence is unambiguous:

    images-none-extracted   source has images, the docx has none
    images-mostly-missing   fewer than half kept
    rules-not-tables        many drawn lines in, zero table cells out
    text-missing            under 85 % of the source's characters
    annotations-present     the source carries annotations
    none-identified         the counts do not point at one cause

`none-identified` is a real answer. A wrong mechanism is worse than no mechanism, because
it sends the fixer after a patch that cannot work.

## Verified on real files

Four real PDFs from the corpus with four deliberately different .docx outputs:

| document | src chars | docx chars | src draws | docx cells | signal | correct |
|---|---|---|---|---|---|---|
| 01_stamp_rotated_15deg_upright | 1471 | 2000 | 19 | 0 | none-identified | yes - the docx holds MORE text, no images, 19 rules is below the table threshold |
| 02_stamp_rotated_15deg_upleft | 1430 | 13 | 23 | 0 | text-missing | yes - 13 is under 85 % of 1430 |
| 23_timetable_grid_txtpos | 909 | 24 | 26 | 24 | text-missing | yes - the table IS present so rules-not-tables correctly did not fire |
| 62_two_col_newsletter_pull_quote | 1788 | 1788 | 5 | 0 | none-identified | yes - the full text was copied |

Each branch was exercised against a real PDF and a real .docx read through the real
parsers, not a mock.

## How it is used

`benchmarks/CENSUS.md` groups the same data by signal with a document count per mechanism.
The fixer is told to start with the signal covering the most documents: **one mechanism
fixed once clears every document under it**, which is worth more than clearing one document
twenty times.

The census runs in the baseline cron, right after the measurement, because it needs the
PDFs and the .docx files and those only exist during that run. Its output is committed, so
the fixer - which runs in a later, wiped sandbox - reads it without needing the files.

## What it does not do

It does not say the fix is easy, and it does not replace measuring. It answers one question
the score could not: what kind of thing is missing. Whether a patch can restore it is still
the fixer's work, and the ratchet still decides.
