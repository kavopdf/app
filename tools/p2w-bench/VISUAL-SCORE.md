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
| 7 Nov | 2 | 1 | 50 % | after the D-01 pitch fix: 316 PASS, 303 FAIL (WARNING SIGNS wraps) |

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

## Documents opened on 7 Nov, after the D-01 pitch fix

| Document | Page | Verdict | What was seen |
|---|---|---|---|
| 303_discharge_summary | 1 | FAIL | `wraps:WARNING SIGNS` - the PDF sets the warning on one line to the right margin, the render breaks it after "than 4". Body text otherwise on its own rows; table rows ~3 pt low. |
| 316_contract_with_schedules | 1 | PASS | body, headings, schedule table and signature row all on the PDF's own baselines. |

`visual.py` agreed with the eye on 303 - reading order 88.5 % of 25 rows, the wrap being the
difference - and could not render 316 ("could not render one side"), which is a tool failure
and not a document verdict; it is the LibreOffice render after a killed run, and 316's
numbers come from `position.py`, which rendered it at 100 %.
