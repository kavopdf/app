# Visual score

The share of documents that pass the eight questions AND had every page looked at.
Ratchets up. A document that passes the computed questions but whose pages were never
opened is not counted here - `looked.py` decides that, not this file.

## How a document passes

    1. sidebyside.py --record was run, and every page image was opened
    2. every page has a verdict in LOOKED.tsv that is PASS, with what was seen
    3. every applicable computed question passes

## Measured

| Date | Documents | Passed | Score | Note |
|------|-----------|--------|-------|------|
| 7 Nov | 3 | 0 | 0 % | first measurement, on 300/301/302/303 only |

Not a baseline yet - three documents is not the corpus. It becomes one when a full
batch has been through both halves of the check.

## What the first measurement found

    300_prescription_rx     2.3 % of pixels differ   QR identical, only drift
    303_discharge_summary   3.7 % of pixels differ   WARNING SIGNS wraps to two lines;
                                                     both signature labels sit lower
                                                     than the PDF drew them
    301_lab_report_panel    9 % of rows in sequence  every label first, then every value

Two of those three were found by looking, not by any of the eight computed answers.

## The thresholds are gone

Until 7 Nov the eight questions decided with numbers picked by hand: reading order
passed at 95 %, a chart needed five paths and then half as many, emphasis needed a
ratio of 1.05 and 85 % of it. Each is now a comparison with something the PDF says -
1.0 for a sequence, zero-or-not for a path, the PDF's own heading lines for emphasis.
A threshold nobody can justify decides a document is broken, or lets a broken one
through, and neither can be argued with afterwards.
