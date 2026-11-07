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

## The record - one row per document, appended, last row wins

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-07 | 300_prescription_rx | PASS | header band, patient box, Rx table, advice, signature and QR all on their own rows; only the trailing signature block flows higher than the page-bottom anchor |
| 2026-11-07 | 301_lab_report_panel | FAIL | moved:ANANYA RAO 26.2 pt, moved:COLLECTED 8.0 pt - the four-column form band is emitted cell by cell on drifting baselines |
| 2026-11-07 | 302_radiology_report | FAIL | moved:PATIENT NAME -8.6 pt - the patient band's first label leaves its own row |
| 2026-11-07 | 303_discharge_summary | PASS | body, table and signature on the PDF's rows; the PDF's own WARNING line overruns its margin by 1.4 pt and loses its tail, the render wraps and keeps it - reading order 88.5 % is a measurement alarm |
| 2026-11-07 | 304_package_insert_small_print | PASS | every heading and paragraph on the PDF's own baselines |
| 2026-11-07 | 305_vaccination_certificate | PASS | masthead, name block, dose table and QR match; the round seal is a rotated stamp, axis-aligned by the OOXML limit - reading order 47.1 % is the seal |
| 2026-11-07 | 306_clinical_protocol_synopsis | PASS | synopsis table and schedule-of-assessments grid carry the PDF's rows and marks |
| 2026-11-07 | 310_court_judgment | PASS | heading, parties, numbered paragraphs and the Sd/- JUDGE row on the PDF's baselines |
| 2026-11-07 | 311_fir_police_form | FAIL | moved:Mobile - the Mobile label welds onto the address cell and leaves its column; reading order 90.2 % |
| 2026-11-07 | 312_affidavit_stamp_paper | FAIL | moved:BEFORE ME and moved:Note: affidavits, both 72.2 pt high - the notary box renders empty with the footnote inside it |
| 2026-11-07 | 313_power_of_attorney | PASS | title, recitals, schedule and the signature rule on the PDF's baselines |
| 2026-11-07 | 314_tender_rfp_boq | PASS | BOQ rows and amount column exact; every total keeps every digit, 8,39,69,600 at x 467.7-513.0 on both sides |
| 2026-11-07 | 315_gazette_notification | FAIL | moved:publication in the Official Gazette +184.8 pt, moved:The Gazette of India +55.9 pt - the three columns stack into one flow |
| 2026-11-07 | 316_contract_with_schedules | PASS | clauses and the Schedule C table on the PDF's baselines |
| 2026-11-07 | 317_rti_response | PASS | letter head, subject, numbered points and signature block on the PDF's baselines |

v3 batch 1 (the first fifteen of the 75), re-processed from scratch under the
eye-then-numbers order. 10 pass, 5 fail. Every finding above came back VERIFIED from
verify.py against the PDF; the eye's first claims on 301 (two labels), 303 (the WARNING wrap)
and 314 (both totals) were REFUTED and are recorded as corrected rather than fixed.

v3 batch 2 (318-340), re-processed from scratch under the eye-then-numbers order: 23 pages
looked at, 30 findings emitted, 20 verified, 10 refuted. 7 pass, 8 fail. Every FAIL names a
claim verify.py held against the PDF. 326 passes on a named measurement bug: 74 lines on both
sides, identical text, identical order, and question 1 still scores it 94.9 %.

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-07 | 318_court_summons_form | FAIL | moved:Returnable within 30 days 337.6 pt up; the SERVICE checkbox glyphs leave their labels |
| 2026-11-07 | 320_balance_sheet_statutory | PASS | profit-and-loss rows, note column, notes extract and both signature blocks on the PDF baselines |
| 2026-11-07 | 321_auditors_report | PASS | headings, six numbered paragraphs and the auditor block wrap at the PDF line breaks |
| 2026-11-07 | 322_mutual_fund_factsheet | FAIL | moved:EXPENSE RATIO 34.9 pt, moved:FUND MANAGER 54.5 pt, moved:RISKOMETER 71.3 pt |
| 2026-11-07 | 323_credit_card_statement | FAIL | 42 shapes in the PDF against 17 in the render - 25 bars lost; reading order 63.5 % |
| 2026-11-07 | 324_loan_amortisation_schedule | PASS | all 240 rows on seven pages keep month order, six columns and every figure |
| 2026-11-07 | 325_demat_holdings_statement | FAIL | moved:This statement is generated electronically 306.5 pt up |
| 2026-11-07 | 326_itr_computation | PASS | every line present in order; the 94.9 % is a row-band measurement bug, not a defect |
| 2026-11-07 | 330_cad_drawing_sheet | FAIL | pagecount: 1 page in the PDF, 2 in the render |
| 2026-11-07 | 331_pid_diagram | FAIL | reading order 93.3 % and the label sequence 50.0 % - diagram labels reorder around the shapes |
| 2026-11-07 | 332_bom_on_drawing | FAIL | pagecount 1 in / 2 out; 15 shapes in the PDF against 0 in the render |
| 2026-11-07 | 333_datasheet_spec_tables | PASS | three spec tables and the pin table keep every cell and row |
| 2026-11-07 | 334_patent_document | FAIL | moved:16 19.5 pt down; reading order 89.7 % |
| 2026-11-07 | 335_msds_safety_data_sheet | PASS | pictograms, eight numbered sections and the composition table on the PDF baselines |
| 2026-11-07 | 340_bill_of_lading | PASS | every band, the item table, the signature row and the barcode on the PDF rows |
