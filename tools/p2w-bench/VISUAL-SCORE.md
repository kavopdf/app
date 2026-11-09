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
| 8 Nov | 13 | 4 | 31 % | g53 batch 1, the multi-column class: 9 fail, 8 of them on pagecount |
| 8 Nov | 15 | 12 | 80 % | v3 batch 1 re-run after the gap fix: 3 fail (303 breaks, 311 weld, 315 columns) |
| 2026-11-09 | 15 | 4 | 27 % | v3 batch 3 after the column-edge fix: 11 fail, 20 findings verified 1 refuted |
| 8 Nov | 13 | 6 | 46 % | g53 batch 3, the tax-invoice class: 7 fail, after two engine fixes cleared 9 of the 13 documents of the spill and the dropped header line |
| 8 Nov | 10 | 5 | 50 % | the D group, and the corpus is now fully scored: 113 PASS / 95 FAIL of 208, last row per document |
| 8 Nov | 15 | 8 | 53 % | v3 batch 1 final sweep: 7 fail (301, 303, 305, 306, 311, 314, 315), 306 new on a 7.2 pt table-extent finding |
| 2026-11-09 | 15 | 9 | 60 % | v3 318-340: 6 fail, 21 findings 21 verified 0 refuted; 3 pass on the eye against an order finding (the tab-join measurement bug) |
| 2026-11-09 | 15 | 9 | 60 % | v3 341-370: 6 fail, 14 findings 14 verified 0 refuted; 3 pass on the eye against an order finding (band join), 1 shapes claim refuted (352's border is exact) |

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
| 2026-11-07 | 300_prescription_rx | FAIL | moved:Not valid for medico-legal purposes 270.2 pt up; moved:Dr. Meera Krishnan 270.1 pt up |
| 2026-11-07 | 301_lab_report_panel | FAIL | moved:ANANYA RAO 26.2 pt down; moved:H = above reference interval 146.9 pt up; reading order 78.7 % |
| 2026-11-07 | 302_radiology_report | FAIL | moved:Dr. A. Bhat 231.5 pt up; moved:This report is based on the images provided 231.5 pt up |
| 2026-11-07 | 303_discharge_summary | FAIL | moved:ANANYA RAO, 34/F 8.2 pt down off its row; moved:Resident Medical Officer 192.7 pt up |
| 2026-11-07 | 304_package_insert_small_print | PASS | six headings keep their weight, every line breaks where the PDF breaks; the emphasis question fails only because 6.8 pt rounds to 6.5 |
| 2026-11-07 | 305_vaccination_certificate | FAIL | moved:This is a computer generated certificate 351.8 pt up; the round seal's characters land one per baseline |
| 2026-11-07 | 306_clinical_protocol_synopsis | PASS | both tables keep every row and every X in its own cell, page count 1/1 |
| 2026-11-07 | 310_court_judgment | PASS | centred heading on the page centre after the indent fix, eight numbered paragraphs wrap at the PDF breaks |
| 2026-11-07 | 311_fir_police_form | FAIL | moved:Copy forwarded to 162.5 pt up; moved:Signature of Officer in charge 27.2 pt down; reading order 90.2 % |
| 2026-11-07 | 312_affidavit_stamp_paper | FAIL | moved:BEFORE ME 72.2 pt up, its box left empty; moved:Notary Public, Bengaluru 72.2 pt up |
| 2026-11-07 | 313_power_of_attorney | PASS | heading, five clauses, schedule and witness block on the PDF baselines |
| 2026-11-07 | 314_tender_rfp_boq | FAIL | moved:Meridian Consulting Pvt Ltd 189.7 pt up; moved:lot 13.4 pt up |
| 2026-11-07 | 315_gazette_notification | FAIL | three columns stacked into one flow; moved:[No. 4/2/2024-WDRA] 229.5 pt up; reading order 29.1 % |
| 2026-11-07 | 316_contract_with_schedules | PASS | table, schedule and signature row on the PDF baselines; q6's 1-against-0 shape count was refuted 1 against 1 |
| 2026-11-07 | 317_rti_response | PASS | centred heading on the page centre after the indent fix, five numbered points in order |
| 2026-11-07 | 341_shipping_manifest | PASS | all 24 rows and the totals footer hold the PDF's own lines; the footer sits 53 pt high under the table |
| 2026-11-07 | 342_packing_list | PASS | carton table, marks box, declaration and both signature blocks in place |
| 2026-11-07 | 343_air_waybill | FAIL | wraps:12 - the Pieces cell splits "12" into "1" and "2"; order 81.2 % |
| 2026-11-07 | 344_customs_declaration | FAIL | moved:Assessing officer -284.0 pt; moved:E-mail: customs@shreeji.example -286.0 pt |
| 2026-11-07 | 350_question_paper | FAIL | pagecount 1 in / 2 out; the [08] marks land 434.8 pt low |
| 2026-11-07 | 351_omr_answer_sheet | FAIL | moved:Signature of candidate -358.4 pt; moved:Signature of invigilator -359.4 pt |
| 2026-11-07 | 352_certificate_ornate_border | PASS | Dr. S. Iyer and Prof. A. Bose back on the PDF's baseline after the gap fix |
| 2026-11-07 | 353_admit_card | FAIL | moved:VENUE +107.7 pt; the label/value block is still a four-column table |
| 2026-11-07 | 360_restaurant_menu | FAIL | wraps:Butter Chicken - five MAINS prices fall onto the line below |
| 2026-11-07 | 361_product_catalogue_grid | PASS | card text sits below the photograph again and every card keeps all three lines |
| 2026-11-07 | 362_price_list_dense | PASS | 84 rows in three columns keep every code and rate |
| 2026-11-07 | 363_warranty_card | FAIL | moved:Customer care: 1800-123-4471 (toll free) -251.0 pt |
| 2026-11-07 | 364_event_ticket | FAIL | count:WS24-4471-0082 - twice in the PDF, once in the render |
| 2026-11-07 | 365_recipe_card | FAIL | wraps:Cornflour - "2 tbsp" splits across two lines |
| 2026-11-07 | 370_offer_letter | FAIL | wraps:Provident fund (employer contribution) - the component column is too narrow |
| 2026-11-07 | 371_experience_certificate | PASS | signature, place and date back at the foot of the page after the gap fix |

## v3 batch 4 (372-401, 15 documents), 7 Nov - looked at, measured, verified, and no fix passed the ratchet

15 pages, 15 verdicts, no page PENDING. 18 findings emitted, 13 VERIFIED, 2 REFUTED,
3 UNVERIFIABLE. 6 pass, 9 fail. Nothing was fixed: the one fix this batch earned - the
table height that clamps a page's foot - regressed 39 documents on page count and was
reverted. See "Table height" in REMAINING-DEFECTS.md.

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-07 | 372_timesheet_grid | PASS | header band, timesheet grid, both signature rules and the note sit on the PDF's own rows |
| 2026-11-07 | 373_leave_application_form | FAIL | moved:ANANYA RAO 17.1 pt, moved:Earned 100.3 pt - the label-over-value cells are emitted as side-by-side columns |
| 2026-11-07 | 374_org_chart | FAIL | moved:Total headcount -329.3 pt, moved:Vacancies -329.3 pt - the page's foot is clamped by the table blocker |
| 2026-11-07 | 375_attendance_register | FAIL | moved:Verified by -172.4 pt, moved:P = present -172.3 pt |
| 2026-11-07 | 380_runbook_terminal_output | FAIL | the Escalation line is bold in the render and regular in the PDF - emphasis has no claim type, so verify.py answers UNVERIFIABLE |
| 2026-11-07 | 381_incident_report_timeline | FAIL | moved:Distribution: Operations, Engineering, Customer Success 240.8 pt up |
| 2026-11-07 | 382_architecture_diagram | PASS | all seven boxes, their labels and every connector on the PDF's own coordinates |
| 2026-11-07 | 383_api_docs_page | FAIL | the RESPONSE FIELDS table carries a fourth empty column and row rules the PDF does not draw - no claim type describes a table's shape |
| 2026-11-07 | 390_wide_data_appendix | PASS | header band, 21 columns and every figure on the PDF's rows; the eye first read the header as S.No and both sides say Sample |
| 2026-11-07 | 391_survey_questionnaire_grid | PASS | header band, eight statement rows and every tick in its own column |
| 2026-11-07 | 392_statistical_console_output | PASS | every coefficient row and both summary blocks on the PDF's lines |
| 2026-11-07 | 393_spectrum_peak_table | FAIL | moved:Figure 1: absorbance spectrum 132.7 pt up - the peak table is drawn over the chart and the table below it is empty |
| 2026-11-07 | 394_map_with_legend | PASS | boundary, roads, river, four markers and the legend box on the PDF's coordinates |
| 2026-11-07 | 400_comic_page_speech_bubbles | FAIL | reading order 42.1 % - 23 rows in the render against the PDF's 15, and one speech bubble loses its outline |
| 2026-11-07 | 401_trifold_brochure | FAIL | overlap 3 pairs against the PDF's 0; moved:CONTACT US -484.1 pt - the three panels stack instead of standing side by side |
| 2026-11-07 | 300_prescription_rx | FAIL | moved:Dr. Meera Krishnan 270.1 pt up - the signature block is a flowed paragraph and the page's own 270 pt gap is clamped to 120 |
| 2026-11-07 | 301_lab_report_panel | FAIL | moved:ANANYA RAO 26.2 pt down; order 78.7 % - the four-column header band becomes five paragraphs because each row's cells were measured 1 pt apart and the row is cut at the first field that starts left of the one before it |
| 2026-11-07 | 302_radiology_report | FAIL | moved:ANANYA RAO -9.8 pt - the ruled header grid starts 8.6 pt above the page |
| 2026-11-07 | 303_discharge_summary | FAIL | order 88.5 % - 25 rows in the PDF against 27 in the render. wraps:WARNING SIGNS was claimed and REFUTED (2 lines on both sides) |
| 2026-11-07 | 304_package_insert_small_print | PASS | every heading and line break on the PDF page, 0.4 % of pixels differ. The emphasis question failed on 6 lines the eye sees bold - a measurement bug, see CLAIM-LEDGER |
| 2026-11-07 | 305_vaccination_certificate | FAIL | moved:This is a computer generated certificate 351.8 pt up; order 47.1 % |
| 2026-11-07 | 306_clinical_protocol_synopsis | PASS | both tables, every row and every tick column on the PDF layout |
| 2026-11-07 | 310_court_judgment | PASS | all eight numbered paragraphs and the JUDGE block on the PDF page |
| 2026-11-07 | 311_fir_police_form | FAIL | moved:Mobile 91.8 pt - the label is welded into the address cell (2 in the PDF, 1 in the render); order 90.2 % |
| 2026-11-07 | 312_affidavit_stamp_paper | PASS | stamp box, five paragraphs, DEPONENT and the notary seal in place. order 60.9 % is a measurement bug - the eye passed, so the eye decides |
| 2026-11-07 | 313_power_of_attorney | PASS | every paragraph, the SCHEDULE and both signature rules on the PDF page |
| 2026-11-07 | 314_tender_rfp_boq | FAIL | moved:Grand total -20.7 pt - both tables sit high because the model's table height is short |
| 2026-11-07 | 315_gazette_notification | FAIL | moved:The Gazette of India 55.9 pt down; order 29.1 % - three columns stack into one flow, the masthead lands after column 1 |
| 2026-11-07 | 316_contract_with_schedules | PASS | four clauses and the SCHEDULE C table on the PDF page, 1/1 pages. shapes was claimed and REFUTED (1 on both sides) |
| 2026-11-07 | 317_rti_response | PASS | heading, date block, five numbered points and the enclosure line all in place |
| 2026-11-08 | 300_prescription_rx | FAIL | moved:Dr. Meera Krishnan 270.1 pt - the signature block is a flowed paragraph and the page's own 270 pt gap is clamped to 120 |
| 2026-11-08 | 301_lab_report_panel | FAIL | moved:ANANYA RAO 26.2 pt down; order 78.7 % - the four-column header band's values are absorbed into the results table as an extra header row |
| 2026-11-08 | 302_radiology_report | FAIL | moved:Dr. A. Bhat, MD, DNB (Radiodiagnosis) 231.5 pt up - the signature block, the same clamped-gap class |
| 2026-11-08 | 303_discharge_summary | FAIL | breaks:WARNING SIGNS (the PDF's line ends at 'needed', no render line does); order 88.5 %, 25 rows against 27 |
| 2026-11-08 | 304_package_insert_small_print | PASS | every heading and line break on the page, 0.4 % of pixels differ |
| 2026-11-08 | 305_vaccination_certificate | FAIL | moved:This is a computer generated certificate 351.8 pt up; order 47.1 % |
| 2026-11-08 | 306_clinical_protocol_synopsis | PASS | both tables, every row and every tick column on the PDF layout |
| 2026-11-08 | 310_court_judgment | PASS | all eight numbered paragraphs and the JUDGE block on the page |
| 2026-11-08 | 311_fir_police_form | FAIL | moved:Mobile 91.8 pt - the label is welded into the address cell (2 in the PDF, 1 in the render); order 90.2 % |
| 2026-11-08 | 312_affidavit_stamp_paper | PASS | stamp box, five paragraphs, DEPONENT and the notary seal in place. order 60.9 % and emphasis 18/20 are measurement bugs - the eye passed, so the eye decides |
| 2026-11-08 | 313_power_of_attorney | PASS | every paragraph, the SCHEDULE and both signature rules on the page |
| 2026-11-08 | 314_tender_rfp_boq | FAIL | moved:Grand total -20.7 pt - both tables sit high because the model's table height is short |
| 2026-11-08 | 315_gazette_notification | FAIL | moved:The Gazette of India 55.9 pt down; order 29.1 % - three columns stack into one flow |
| 2026-11-08 | 316_contract_with_schedules | PASS | four clauses and the SCHEDULE C table on the page; shapes was claimed and REFUTED (1 on both sides) |
| 2026-11-08 | 317_rti_response | PASS | heading, date block, five numbered points and the enclosure line in place |
| 2026-11-08 | 318_court_summons_form | FAIL | moved:Returnable within 30 days 7.8 pt - the table above it renders 7.8 pt shorter than the model's own extent. Was 337.6 pt: the 120 pt gap clamp on table pages, fixed this run |
| 2026-11-08 | 320_balance_sheet_statutory | FAIL | moved:As per our report of even date 8.9 pt - the same short-table class. Was 215.1 pt before the gap clamp fix |
| 2026-11-08 | 321_auditors_report | PASS | six paragraphs, the signature block and the firm registration line all on the PDF page |
| 2026-11-08 | 322_mutual_fund_factsheet | FAIL | moved:EXPENSE RATIO 34.9 pt - the four-column header band splits into two rows, EXPENSE RATIO and FUND MANAGER falling to the second |
| 2026-11-08 | 323_credit_card_statement | FAIL | moved:CREDIT LIMIT 32.4 pt - the same band split, CREDIT LIMIT and AVAILABLE on a row of their own |
| 2026-11-08 | 324_loan_amortisation_schedule | PASS | seven pages, all 240 rows of the schedule in place, page count 7 in and 7 out |
| 2026-11-08 | 325_demat_holdings_statement | FAIL | moved:This statement is generated electronically 9.4 pt - the short-table class. Was 306.5 pt before the gap clamp fix |
| 2026-11-08 | 326_itr_computation | FAIL | order 94.9 % - Place: Bengaluru sits 31 pt high and the slab table's last row is one row out |
| 2026-11-08 | 330_cad_drawing_sheet | FAIL | pagecount - 1 page in, 2 out: the dimension lines and the north arrow spill onto a second sheet |
| 2026-11-08 | 331_pid_diagram | PASS | every box, valve and legend entry on the page. order 93.3 % is a measurement artifact, the eye passed |
| 2026-11-08 | 332_bom_on_drawing | FAIL | pagecount - 1 page in, 2 out: the bill of materials table and the assembly drawing split across two sheets |
| 2026-11-08 | 333_datasheet_spec_tables | PASS | all three specification tables and the footer now exact. Was 167.5 pt out before the gap clamp fix |
| 2026-11-08 | 334_patent_document | PASS | title, abstract, FIG. 1 and all five claims on the page. order 89.7 % is a measurement artifact, the eye passed |
| 2026-11-08 | 335_msds_safety_data_sheet | PASS | eight numbered sections, the pictogram row and the composition table all in place |
| 2026-11-08 | 340_bill_of_lading | PASS | every cell of the form and the barcode caption now exact. Was 293.1 pt out before the gap clamp fix |
| 2026-11-08 | 341_shipping_manifest | FAIL | pagecount - 1 page in, 2 out; the manifest table spills onto a second sheet |
| 2026-11-08 | 342_packing_list | PASS | header, exporter block, four-row table, totals, marks box, declaration and signature on the PDF baselines |
| 2026-11-08 | 343_air_waybill | FAIL | order 90.3 % of 15 rows; the Pieces cell that set "12" as "1" over "2" was fixed this run (was 17 rows), one line still outside tolerance |
| 2026-11-08 | 344_customs_declaration | PASS | title band, two-column field grid, item table, CLEARED stamp and both boxes in place |
| 2026-11-08 | 350_question_paper | FAIL | pagecount - 1 page in, 2 out; order 39.3 % of 52 rows, every question is one paragraph with a gap |
| 2026-11-08 | 351_omr_answer_sheet | FAIL | rules - 11 rules in the PDF, 32 in the render; the bubble grid is drawn inside a ruled table the page does not have |
| 2026-11-08 | 352_certificate_ornate_border | PASS | ornate double border, five text blocks, the seal and both signatures on the PDF rows. order 46.8 % is the seal's per-character text - measurement, the eye passed |
| 2026-11-08 | 353_admit_card | FAIL | moved:DATE OF BIRTH 81.0 pt - the label/value band is emitted as separate rows; order 63.0 % |
| 2026-11-08 | 360_restaurant_menu | FAIL | order 61.5 % of 17 rows - the right column's dot-leader tab stop runs past the margin and each price wraps to the next line |
| 2026-11-08 | 361_product_catalogue_grid | PASS | all six cards with image, title, price, code and barcode on the PDF grid |
| 2026-11-08 | 362_price_list_dense | PASS | three column groups, every row of every group in place, footer line in place |
| 2026-11-08 | 363_warranty_card | PASS | title box, product block, six terms, sticker box, QR and both footers on the PDF rows. order 87.0 % counts the QR modules - measurement, the eye passed |
| 2026-11-08 | 364_event_ticket | FAIL | missing:ADMIT ONE - the rotated sidebar label is gone; only a clipped "WAREHOU" survives at x=565 |
| 2026-11-08 | 365_recipe_card | FAIL | wraps:2 tbs, wraps:to taste - the amount column is fragmented into three grid columns and every two-word cell breaks; order 89.7 % |
| 2026-11-08 | 370_offer_letter | PASS | letterhead, ref, address, subject, body, five-row table and signature block on the PDF baselines. order 93.1 % and the shapes claim both came back measurement |
| 2026-11-08 | 402_calendar_month_grid | FAIL | pagecount 1 in / 2 out, order 72.0 % of 12 rows; the 7-row calendar is charged more height than the page gave it and Board meeting wraps inside its cell |
| 2026-11-08 | 403_crossword_puzzle | PASS | grid, all 12 numbers, both clue columns and the footer on the PDF lines. Was FAIL on rules 0 vs 11: the clue columns carried a box the page never draws, fixed this run |
| 2026-11-08 | 404_sudoku_grid | FAIL | rules 8 in the PDF against 20 in the render - the 3x3 box rules are thick filled rules on the page and every line in the render is the same hairline, so the puzzle loses its structure |
| 2026-11-08 | 405_sheet_music_lyrics | PASS | title, chord row, three staves with their lyrics and the footer all on the PDF lines |
| 2026-11-08 | 406_passport_mrz_page | FAIL | moved:BENGALURU 43.2 pt - the Place of birth value falls out of its row and the Sex value takes a line of its own. Was 50.7 pt and 19 invented rules before the border fix |
| 2026-11-08 | 407_id_card_front_back | PASS | both card faces, photo, terms block, two barcodes and the caption in place |
| 2026-11-08 | 410_form_xobject_reused | FAIL | moved:Invoice line item 62.2 pt - all three Form XObject blocks sit about 61 pt above where the page draws them |
| 2026-11-08 | 411_nested_xobject_transforms | FAIL | count:NESTED FORM 1 in the PDF against 2 in the render - the heading is emitted a second time inside the rotated nested form |
| 2026-11-08 | 412_page_labels_roman | PASS | five pages, each heading and both lines on the PDF baselines |
| 2026-11-08 | 413_tagged_pdf_actualtext | PASS | the ActualText replacement is what the render carries, which is what the text layer says |
| 2026-11-08 | 414_transparency_softmask | PASS | blue bar at the page's own rect and fill, both text lines in place. The charts FAIL was the tool counting an erased grey rect and missing a bar written as four border lines |
| 2026-11-08 | 415_inline_images | FAIL | moved:The checkerboard above is an inline image 153 pt - the inline image is gone and its caption has risen into its place |
| 2026-11-08 | 417_rotate180_and_mirrored | FAIL | missing:Page 2 - mirrored text - page 1 is right, upright as /Rotate should give; page 2's mirrored line comes out a garbled reversal |
| 2026-11-08 | 416_many_tiny_pages | PASS | 300 pages in and 300 out, every record's heading, serial/status/batch line and note on the PDF baselines. The moved claim I first recorded was my bbox-top read, not the baseline; the verifier put it at 1.7 pt |
| 2026-11-08 | 01_stamp_rotated_15deg_upright | FAIL | moved:AUTHORISED SIGNATORY 44.5 pt and the footer 136.2 pt high - the 15-degree stamp is written axis-aligned, the settled rotated-stamp class |
| 2026-11-08 | 02_stamp_rotated_15deg_upleft | FAIL | moved:GOODS RECEIVED IN ORDER - the stamp is axis-aligned and the footer sits 113.5 pt high; order 91.5 % |
| 2026-11-08 | 03_stamp_vertical_90deg | FAIL | moved:INTERNAL AUDIT USE ONLY - the 90-degree stamp is axis-aligned and every line below it 189.1 pt down; order 16.0 % of 28 rows |
| 2026-11-08 | 04_stamp_180deg_upside_down | FAIL | moved:DUPLICATE ISSUED -186.5 pt - the 180-degree stamp is written upright and the block below it 105.6 pt down |
| 2026-11-08 | 05_round_company_seal_curved_text | PASS | seal, curved text and body on the PDF rows. order 62.5 % counts the seal's per-character text - measurement, the eye passed |
| 2026-11-08 | 06_rect_paid_stamp_red_transparent | FAIL | moved:NET AMOUNT 120.9 pt - the totals column is interleaved with the left column into one flow, so the page no longer fits and its gaps are clamped |
| 2026-11-08 | 07_stamp_over_table | FAIL | moved:Grand Total 7.5 pt and the footer 181.2 pt high - the page's gaps are clamped; the eye failed, no measure finding |
| 2026-11-08 | 08_two_overlapping_stamps | FAIL | moved:PAID -14.2 pt - both stamps sit right of where the page draws them, and the footer 274.7 pt high |
| 2026-11-08 | 09_stamp_font_not_embedded | FAIL | moved:FY 2024-25 17.0 pt - the stamp is drawn from the non-embedded face and sits right and lower than the page's |
| 2026-11-08 | 10_stamp_as_image | FAIL | moved:ORDER CONFIRMED - the image stamp is placed off the page's box and the page's gaps are clamped, footer 195.2 pt high |
| 2026-11-08 | 11_stamp_with_signature_image | FAIL | moved:SANCTIONED - the stamp sits right of the page's and the footer 158.6 pt high. My wraps claim was REFUTED: both sides carry two lines |
| 2026-11-08 | 12_stamp_across_page_break | FAIL | moved:SUB-REGISTRAR 56.4 pt on page 2; the body sits 136.0 pt down on both pages and the stamp box is empty on page 2 |
| 2026-11-08 | 13_stamp_non_english | FAIL | moved:प्रमाणित प्रतिलिपि -17.0 pt - the Devanagari stamp sits right of the page's and smaller; footer 192.2 pt high |
| 2026-11-08 | 14_stamp_chars_positioned_td | PASS | the per-character positioned stamp text and the six-row table on the PDF rows; order 96.4 % |
| 2026-11-08 | 15_stamp_on_scanned_page | PASS | the stamp's two lines land within 2.5 pt. The box's rotation is gone, but the shapes claim came back UNVERIFIABLE - recorded as a blind spot, not a pass of the eye |
| 2026-11-08 | 16_right_aligned_amounts_txtpos | PASS | ledger rows, right-aligned amounts and the closing-balance sentence on the PDF rows |
| 2026-11-08 | 17_three_column_widths_txtpos | PASS | trip sheet's three column groups and the revenue column at their PDF widths |
| 2026-11-08 | 18_centred_heading_left_body_txtpos | PASS | centred head, five numbered items and the footer on the PDF lines |
| 2026-11-08 | 19_hanging_indent_txtpos | PASS | hanging-indent clauses and the approval line on the PDF lines |
| 2026-11-08 | 20_numbered_list_separate_column_txtpos | FAIL | pagecount 1 in / 2 out and moved:I have read and understood 101.4 pt - every numbered item is two paragraphs, the marker column and the text column |
| 2026-11-08 | 21_form_labels_x60_values_x300_txtpos | PASS | labels and values on the page's rows, word set identical to the PDF |
| 2026-11-08 | 22_invoice_four_columns_txtpos | PASS | four columns, quantities, rates and amounts on the PDF rows |
| 2026-11-08 | 23_timetable_grid_txtpos | PASS | grid rules and every period cell on the page's rows, word set identical |
| 2026-11-08 | 24_address_block_indents_txtpos | PASS | indented address blocks and the signature block on the PDF rows |
| 2026-11-08 | 25_signature_block_underscores_txtpos | PASS | both signature rules and the annexure rates on the PDF rows |
| 2026-11-08 | 26_footnote_marker_bottom_note_txtpos | PASS | footnote marker and the bottom note on the page's lines |
| 2026-11-08 | 27_two_column_left_short_txtpos | FAIL | moved:Residents of the ward - 129.7 pt in the PDF, 183.4 in the render, the whole right column block sits 54 pt low |
| 2026-11-08 | 28_value_overflows_cell_txtpos | PASS | the overflow row sits where the page draws it. order 79.1 % is a measurement blind spot - the page's description deliberately overruns its cell, so the row bands do not pair |
| 2026-11-08 | 29_dot_leaders_txtpos | PASS | dot leaders and right-aligned amounts on the PDF rows |
| 2026-11-08 | 30_mixed_font_sizes_one_baseline_txtpos | FAIL | moved:Counselling and seat allotment - 192.6 pt in the PDF, 222.3 in the render; the 01 drops onto a line of its own |
| 2026-11-08 | 31_times_body_arial_headings | PASS | Times body and sans headings on the page's lines |
| 2026-11-08 | 32_serif_nondefault_body | PASS | serif body and italic headings on the PDF lines |
| 2026-11-08 | 33_sans_nondefault_body | PASS | sans body, heading band and table on the PDF rows |
| 2026-11-08 | 34_monospace_document | PASS | courier column alignment held, every statement on its PDF line |
| 2026-11-08 | 35_four_typefaces_one_page | PASS | four faces, marks table and totals line on the PDF rows |
| 2026-11-08 | 36_embedded_subset_font | PASS | subset face renders, field table and both paragraphs on the PDF rows |
| 2026-11-08 | 37_font_not_embedded_substitution | PASS | substituted faces and every line on the PDF baselines |
| 2026-11-08 | 38_faux_bold_italic_synthesised | FAIL | count:Study of self-compacting concrete - the page draws the subtitle twice at y=118.2 to fake bold and the render carries both copies on one line, so the subtitle appears twice |
| 2026-11-08 | 39_small_caps_letter_spacing | FAIL | the letter-spaced headings lose their spaces - NOTICE TO MEMBERS renders as NOTICETOMEMBERS. order 86.5 % of 18 rows |
| 2026-11-08 | 40_devanagari_shaping_font | PASS | Devanagari shapes correctly, table and paragraphs on the PDF rows. order 92.7 % is a measurement blind spot - the shaping pass pairs rows by text |
| 2026-11-08 | 41_coloured_headings_white_bg | PASS | coloured section headings and the price column on the page lines |
| 2026-11-08 | 42_table_coloured_header_alternating_rows | PASS | navy header, alternating row shading and every figure on the page rows |
| 2026-11-08 | 43_red_stamp_over_black_text | PASS | red stamp in place over the body text; order 81.6 % is a measurement blind spot - the stamp's lines band differently from the page's |
| 2026-11-08 | 44_coloured_underlined_hyperlinks | PASS | blue underlined link list and the right-hand URLs on the page lines |
| 2026-11-08 | 45_coloured_callout_box | PASS | amber-ruled callout box with its pale fill in the page position |
| 2026-11-08 | 46_chart_coloured_labels_body_text | PASS | twelve bars in the page colours with their value labels and axis; order 85.7 % counts chart labels as rows |
| 2026-11-08 | 47_grey_body_black_headings | PASS | grey body under black headings, every clause on the page lines |
| 2026-11-08 | 48_form_coloured_border_coloured_values | PASS | ruled form box, label column and bold values on the page rows |
| 2026-11-08 | 49_coloured_background_block_paragraph | PASS | navy filled block with white text, body on the page lines |
| 2026-11-08 | 50_invoice_coloured_total_row | PASS | six-line invoice table and the navy total row with its amount; order 92.3 % splits the total row off the words line |
| 2026-11-08 | 51_two_cm_margins | PASS | page frame at 2 cm and every paragraph inside it on the page lines |
| 2026-11-08 | 52_one_cm_margin_wide_body | PASS | wide body block, green header row and right-aligned figures |
| 2026-11-08 | 53_single_space_body_15_headings | PASS | single-spaced body under 15 pt headings, page lines held |
| 2026-11-08 | 54_two_column_body_full_width_header_footer | FAIL | moved:On the domestic side 153.6 pt and moved:The institute 153.8 pt - the right column is laid out after the left one, not beside it |
| 2026-11-08 | 55_sidebar_box_beside_body | FAIL | pagecount 1 in and 2 out, moved:PROJECT AT A GLANCE 227.7 pt, shapes 1 in the PDF and 0 in the render |
| 2026-11-08 | 56_table_indented_from_margin | FAIL | missing:640.00 - the Rate cell is 22.9 pt wide and the value needs 23.4, so the last digit wraps onto its own line inside the cell |
| 2026-11-08 | 57_centred_title_page_left_body_pages | FAIL | moved:SRI VINAYAKA INSTITUTE OF TECHNOLOGY -243.4 pt; the title page block sits at the top of the sheet instead of the page's centre band |
| 2026-11-08 | 58_header_rule_footer_rule | PASS | header and footer rules both present; the eye missed the 0.4 pt footer rule at 130 dpi and the rule test was excluding a 1.2000000476 pt band |
| 2026-11-08 | 59_landscape_mixed_portrait | PASS | portrait page and the landscape sheet with its five-row measurements table on the page rows |
| 2026-11-08 | 60_page_border | FAIL | moved:Dr. S. Vedavathi 20.8 pt - the right signature block and the date are pushed down onto the seal's top arc |

### b80 batch 4 (61-80), 8 Nov - the multi-column class

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-08 | 61_two_col_abstract_spanning | PASS | two columns and the spanning abstract box, 39 lines within 0.2 pt; order 52.9 % is a measurement blind spot - row banding counts a two-column page twice |
| 2026-11-08 | 62_two_col_newsletter_pull_quote | FAIL | moved:Tank rehabilitation restores water to nine villages 28.0 pt - the masthead's right-hand date becomes its own paragraph and pushes the whole page down |
| 2026-11-08 | 63_three_column_brochure | FAIL | moved:THE ESTATE 29.5 pt, pagecount 1 in and 2 out - three columns stacked into one flow |
| 2026-11-08 | 64_newspaper_uneven_columns_ad_boxes | FAIL | pagecount 1 in and 5 out - three unequal columns become a three-column table of column fragments |
| 2026-11-08 | 65_two_col_full_width_figure_caption | FAIL | moved:Figure 1 168.0 pt, pagecount 1 in and 2 out - the chart is taken apart and the two columns stacked |
| 2026-11-08 | 66_two_col_footnotes_bottom | PASS | two columns, footnotes at the page foot, every line on the page coordinates; order 38.5 % is the same row-banding blind spot |
| 2026-11-08 | 67_two_col_with_sidebar | FAIL | moved:COURSE AT A GLANCE 355.4 pt, pagecount 1 in and 2 out - the sidebar box is lost and its text joins the body flow |
| 2026-11-08 | 68_journal_wide_table_spanning | PASS | two text columns and the full-width table on the page rows |
| 2026-11-08 | 69_two_col_legal_numbered_clauses | FAIL | moved:The principal shall supply grey fabric 12.0 pt - each clause number sits on its own baseline above the clause |
| 2026-11-08 | 70_magazine_drop_cap_photo_caption | FAIL | moved:The harvest that begins in the dark 13.5 pt - the masthead and its strapline are two paragraphs, so the strapline's box pushes the page down |
| 2026-11-08 | 71_invoice_space_aligned_no_rules | PASS | borderless table with every column on the page column and the amounts right; order 94.3 % |
| 2026-11-08 | 72_bank_statement_no_rules_right_amounts | PASS | thirty statement rows on the page baselines with the debit and credit columns kept |
| 2026-11-08 | 73_marksheet_subject_marks_grade | PASS | eight subject rows on the page baselines, marks and grades in their columns |
| 2026-11-08 | 74_balance_sheet_indented_subitems | PASS | indented sub-items keep their hierarchy and both figure columns |
| 2026-11-08 | 75_merged_header_cell_three_columns | FAIL | moved:Yeshwanthpur 36.1 pt, pagecount 1 in and 2 out - the merged header cell becomes an empty band and adds a column |
| 2026-11-08 | 76_devanagari_table | PASS | Devanagari shapes, five-row table and the notice paragraphs on the page rows |
| 2026-11-08 | 77_arabic_rtl_document | FAIL | moved:2025 0884 38.0 pt, pagecount 1 in and 2 out - the invoice number is split at its slashes and the table's columns are reversed |
| 2026-11-08 | 78_mixed_english_devanagari_line | FAIL | wraps:Amount paid - the Latin and Devanagari runs are split onto four baselines, pagecount 1 in and 2 out |
| 2026-11-08 | 79_inr_indian_digit_grouping_table | PASS | four-row table with Indian digit grouping and the words line under it |
| 2026-11-08 | 80_gstin_pan_cin_ifsc_table | PASS | five dealer boxes with their rules and both identifier columns on the page rows; order 92.3 % is the row-banding blind spot |

### g53 corpus - batch 1 (A 1-10, B 11-13), 8 Nov - the multi-column class

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-08 | academic-paper-ieee-2col-abstract | FAIL | pagecount - 2 pages in the PDF, 3 in the render; order 61.7 % of 68 rows, 0.0 % of 43 on page 2 |
| 2026-11-08 | admission-form-labels-left-boxes-right | PASS | twenty-two numbered fields, every box on its rule, declaration band at the foot |
| 2026-11-08 | annual-review-2col-uneven-columns | FAIL | wraps:KAVERI MILLS LIMITED - the PDF's two masthead lines are merged into one; order 57.9 % of 34 rows |
| 2026-11-08 | balance-sheet-two-columns-of-figures | PASS | both figure columns on the page baselines, 25 rows in sequence |
| 2026-11-08 | brochure-3col-with-sidebar-box | FAIL | pagecount 1 in, 2 out; shapes 4 in the PDF and 0 in the render; order 37.9 % of 43 rows |
| 2026-11-08 | bus-timetable-station-left-times-right | FAIL | breaks:05:45 - every departure time splits after the colon; pagecount 1 in, 2 out; order 4.0 % of 39 rows |
| 2026-11-08 | journal-2col-with-footnotes | FAIL | pagecount 1 in, 2 out - the second sheet is blank; order 92.3 % of 57 rows |
| 2026-11-08 | magazine-2col-pullquote-spanning | PASS | two columns, photo and pull quote on the page rows; order 76.3 % is the row-banding blind spot |
| 2026-11-08 | newsletter-3col-header-footer | FAIL | pagecount 1 in, 2 out; shapes 3 in the PDF and 0 in the render; order 32.3 % of 57 rows |
| 2026-11-08 | newspaper-2col-fullwidth-headline | FAIL | pagecount 1 in, 2 out - the photograph is pushed to the second sheet; order 28.6 % of 41 rows |
| 2026-11-08 | policy-2col-spanning-section-heading | FAIL | pagecount 1 in, 2 out; shapes 1 in the PDF and 0 in the render; order 31.6 % of 41 rows |
| 2026-11-08 | price-list-2col-dense-right-aligned | PASS | 46 rows in sequence, 420 rules in both; the eye's overlap claim was REFUTED, 0 pairs either side |
| 2026-11-08 | report-2col-table-spanning-both-columns | FAIL | pagecount 1 in, 2 out - the second sheet carries only the footer rule; order 51.2 % of 35 rows |

Thirteen documents, 14 pages in the PDF and 22 in the render, every page opened before any
number was read. 34 findings: 32 verified, 1 refuted, 1 unverifiable. **4 pass, 9 fail.**

### v3 corpus - batch 1 (300-317), re-run 8 Nov 09:06 under the gap fix

Fifteen documents, one page each, every page opened before any number was read. The first
run of this batch found five failures; after the D-09 gap fix four of them closed and the
batch was looked at again from the new renders.

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-08 | 300_prescription_rx | PASS | Rx table, advice and the footer on the page rows; the footer is 8.2 pt from the PDF after the gap fix |
| 2026-11-08 | 301_lab_report_panel | PASS | panel band, ten-row table and the signature block in place; order 78.7 % is the row-banding blind spot |
| 2026-11-08 | 302_radiology_report | PASS | signature block at the foot where the PDF drew it |
| 2026-11-08 | 303_discharge_summary | FAIL | breaks:WARNING SIGNS - the PDF's line ends at "needed" and no render line does |
| 2026-11-08 | 304_package_insert_small_print | PASS | six numbered sections, bold heads, the same line breaks |
| 2026-11-08 | 305_vaccination_certificate | PASS | footer line 1.4 pt from the PDF after the gap fix, was 351.8 pt high |
| 2026-11-08 | 306_clinical_protocol_synopsis | PASS | synopsis table and the schedule grid complete, marks in their cells |
| 2026-11-08 | 310_court_judgment | PASS | cause title, eight numbered paragraphs and the JUDGE block |
| 2026-11-08 | 311_fir_police_form | FAIL | count:Mobile - the standalone Mobile label is welded onto the address cell |
| 2026-11-08 | 312_affidavit_stamp_paper | PASS | notary box and its label together at the foot, 10.4 pt from the PDF, was 72.2 pt |
| 2026-11-08 | 313_power_of_attorney | PASS | recitals, four numbered powers, schedule and witness rules |
| 2026-11-08 | 314_tender_rfp_boq | PASS | both tables complete, the tax rows under the BOQ |
| 2026-11-08 | 315_gazette_notification | FAIL | moved:The Gazette of India 55.9 pt - the three columns are still one flow (D-08) |
| 2026-11-08 | 316_contract_with_schedules | PASS | four clauses, schedules A and B, the schedule C charge table |
| 2026-11-08 | 317_rti_response | PASS | letter head, five numbered points and the enclosure line |

**12 pass, 3 fail.** 9 findings, all 9 verified against the PDF, none refuted. Three
documents were decided by the eye against the numbers (301, 305, 312) - all three are the
row-banding blind spot in the order question, recorded in REMAINING-DEFECTS.md, not page
defects.

## A stale row is not a verdict

A FAIL row records what the eye and the verifier saw on the date in its Date column. The
engine changes between runs, so a row written before a fix can name a reason that no longer
exists.

Verified on 8 Nov: every one of the 208 documents now produces the same page count as its
PDF, so any FAIL row whose reason is only `pagecount` is out of date. Those rows are not
edited - the history is the point - but they must be re-read before they are counted as
failures. The 09:00 digest counts PASS rows, so a stale FAIL overstates the work left, never
understates it, which is the safe direction to be wrong in.


## g53 corpus - batch 2 (B 14-20, C 21-26), 8 Nov - the statements class

Thirteen documents, 15 pages in the PDF. Every page opened before any number was read.
26 findings: 25 verified, 0 refuted, 1 unverifiable. **7 pass, 6 fail.**

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-08 | admit-card | PASS | candidate field grid, examination schedule and five instructions; order 84.2 % and one overlap are measurement, the page is faithful |
| 2026-11-08 | balance-sheet-and-profit-loss | PASS | balance sheet and statement of profit and loss, both year columns on the page rows |
| 2026-11-08 | bank-statement-5-pages | PASS | five statement pages, every row and the closing balance; order 78.9 % counts the header band twice |
| 2026-11-08 | bank-statement-horizontal-rules-only | FAIL | pagecount - 1 page in the PDF, 2 in the render; the 28 rows are set taller than the page drew them and the table runs past the sheet |
| 2026-11-08 | boq-horizontal-rules-only | PASS | five schedule sections, every quantity, rate and amount on the page rows |
| 2026-11-08 | boq-tender-bill-of-quantities | FAIL | pagecount - 1 page in, 2 out; the table grows and the signature block is pushed off the sheet |
| 2026-11-08 | invoice-line-items-qty-rate-amount | PASS | table, totals and words line on the page rows; the eye's extra:DUE claim was REFUTED, 0 lines on either side |
| 2026-11-08 | marksheet-subject-left-marks-right | FAIL | wraps:A+ 90 - the grading scale is one line on the page and the render spends three |
| 2026-11-08 | payslip-label-left-amount-right | FAIL | moved:Net pay for the month 116.4 pt - the earnings and deductions tables are set with taller rows |
| 2026-11-08 | price-list-right-aligned-amounts | PASS | 24 items with code, MOQ and the right-aligned trade price; order 96.6 % is measurement |
| 2026-11-08 | product-catalogue-code-left-price-right | FAIL | pagecount - 1 page in the PDF, 2 in the render; order 88.2 % of 104 rows |
| 2026-11-08 | question-paper-marks-right-margin | PASS | ten numbered questions and the marks column at the right margin; order 95.7 % is measurement |
| 2026-11-08 | table-of-contents-dot-leaders | FAIL | pagecount - 1 page in, 2 out; order 8.2 % of 24 rows against 49, the entries are set with growing gaps |

Four of the six failures are one cause: a table whose rows are set taller than the page drew
them. The row pitch, the cell line height and the cell margins are all already the page's own
numbers, so the excess is not in the writer's arithmetic - it is in what the render adds to a
row the writer asked for with `w:hRule="atLeast"`. That is a measurement, not a guess, and it
is the next thing to take. Recorded in REMAINING-DEFECTS.md.

Five documents passed the eye and failed a computed question. All five are the reading-order
question on a page whose rows band differently from the PDF's - the measurement blind spot
already recorded, not a page defect.

## g53 corpus - batch 3 (C 27-39), 8 Nov - the tax-invoice and statement class

Thirteen documents, 14 pages in the PDF. Every page opened before any number was read; every
finding verified against the PDF. 23 findings: 22 verified, 0 refuted, 1 unverifiable.
**6 pass, 7 fail.**

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-08 | delivery-challan | PASS | company header line, both tables and the totals in place; the rotated stamp sits lower than the page drew it, the settled stamp limit |
| 2026-11-08 | electricity-bill | PASS | bill head, consumer grid, both charge tables and the net amount on the page rows |
| 2026-11-08 | eway-bill | PASS | consignor and consignee boxes, both tables, every value in place |
| 2026-11-08 | form16-part-b | PASS | PART B on the certificate line, table 1 at the page's own y on page 1, table 2 and the verification block on page 2 |
| 2026-11-08 | gst-invoice-3line-items | FAIL | overlap - 0 overlapping pairs in the PDF, 3 in the render: the SUPPLIER and BILLED TO box rules run through the address lines |
| 2026-11-08 | gst-invoice-horizontal-rules-only | FAIL | moved:A. Deshpande -84.7 pt: the signature block sits 85 pt above where the page drew it |
| 2026-11-08 | gst-invoice-multipage-item-table | PASS | TAX INVOICE on the header line and all four sheets: rows 1-11, 12-22, 23-33, row 34 with the total and the signature |
| 2026-11-08 | gst-invoice-with-qr-code | FAIL | wraps:Rate - the Rate header and its values are broken over two lines in a column too narrow; order 55.4 % of 28 rows against 37 |
| 2026-11-08 | insurance-policy-schedule | FAIL | moved:Authorised signatory 8.4 pt, and the table below it runs 0.9 pt a row taller than the page's pitch |
| 2026-11-08 | itr-computation-with-slab-table | FAIL | pagecount - table 3 runs past the sheet and finishes on a second one; tables 1 and 2 now start on the page's own y |
| 2026-11-08 | marksheet-university-consolidated | FAIL | wraps:Maximum marks - one line on the page, two in the render |
| 2026-11-08 | mobile-bill | PASS | both tables, the amount column and the words line on the page rows |
| 2026-11-08 | mutual-fund-statement | FAIL | pagecount 2 in / 3 out, wraps:Purchase value (Rs), moved:Account number 44.9 pt - table 5 is set as loose lines, not a table |
| 2026-11-08 | property-tax-receipt | PASS | the two rings of the PMC stamp now draw, carried as a freeform under the rotated matrix; header grid, table 1 and the amount in words on the page rows |
| 2026-11-08 | purchase-order | FAIL | moved:M. Sathe -36.9 pt: the signature block sits 37 pt above the rule the page drew it under |
| 2026-11-08 | salary-slip-corporate | PASS | both tables, the net pay line and the YTD table on the page rows; the numbers fail on order and emphasis, both measurement (D-09) |
| 2026-11-08 | salary-slip-factory-wages | PASS | both tables, the deduction column and the amount in words on the page rows |

Five of the seven failures were measured on the engine as it stood at the start of this batch:
nine of the thirteen documents spilled a sheet and six dropped a header line, all from one
cause. Both fixes are in the engine and committed; what is left on these seven is written up
in REMAINING-DEFECTS.md.

Four documents passed the eye and failed `order` - delivery-challan, electricity-bill,
form16-part-b and gst-invoice-multipage-item-table. All four are the row-banding blind spot
(D-03), named by `looked.py --combine` as "eye (numbers wrong - repair the tool)". The pages
are faithful and the documents stay PASS.

## The D group - landscape and rotated pages, tables across a break, merged cells, shadow text (10 documents, 8 Nov)

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-08 | landscape-page-inside-portrait-document | PASS | section break now starts a page - the landscape sheet's header lands at 46.6 pt against the page's 47.6, was 0.4; table and footer carry the corpus-wide 8.8 pt table-top gap |
| 2026-11-08 | one-page-rotated-180-degrees | FAIL | moved:Corrective actions closed within 30 days - the upside-down table is un-rotated to the top and an empty ruled grid is left below, order 6.7 % of 15 rows |
| 2026-11-08 | table-across-page-break-repeated-header | PASS | header repeated on all three sheets, rows 1-42 and the closing stock line on the page rows |
| 2026-11-08 | table-inside-two-column-page | FAIL | order 79.5 % of 40 rows against 43 - the two columns are collapsed into one flow so the right column runs down the left |
| 2026-11-08 | table-with-merged-cells | FAIL | order 62.2 % of 24 rows against 21, moved:West -9.7 pt, wraps:Headcount by quarter 2 lines into 3 - the merged Region cell is split |
| 2026-11-08 | table-with-no-header-row | PASS | 30 rows, every value and the no-header note on the page rows |
| 2026-11-08 | table-with-rotated-header | FAIL | moved:Downtime (hrs) -27.0 pt, moved:Cost per piece (Rs) -33.0 pt, order 81.1 % - the vertical header labels land inside the May 2026 row |
| 2026-11-08 | text-held-twice-shadow-text | FAIL | pagecount 1 in / 2 out, order 59.6 % of 21 rows against 26 - the shadow copy is emitted as a second line and pushes the sheet over |
| 2026-11-08 | two-tables-stacked-with-no-gap | PASS | both tables, the totals row and the pallet row on the page rows |
| 2026-11-08 | very-long-single-column-table | PASS | 96 rows over three sheets, header repeated, footer on the page rows |

Five pass, five fail. This closes the corpus: 208 of 208 documents now have a row, and the
final sweep over all 208 is the only place one is called finished.


## v3 corpus — batch 1 (300-317), re-run 8 Nov 08:38 — the second pass, every page looked at again

Fifteen documents, fifteen pages, all seventeen steps in order. Every page was opened and judged
before any number was read. Eleven findings, 11 verified, 0 refuted, 0 unverifiable. Ten pass, five
fail, and one document where the eye and the numbers disagree.

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-08 | 300_prescription_rx | PASS | Rx, medicine table, advice, signature and QR on the page rows; the table sits 12.4 pt high, under what the eye can see |
| 2026-11-08 | 301_lab_report_panel | FAIL | moved:MPL03184471 verified, worst offset 34.3 pt - the four-column patient band is emitted as four paragraphs on drifting baselines, and the band's extra height pushes the table 19.9 pt down |
| 2026-11-08 | 302_radiology_report | PASS | label band, findings and the signature block where the PDF drew them; the labels sit 9.3 pt high, under what the eye can see |
| 2026-11-08 | 303_discharge_summary | FAIL | breaks:WARNING SIGNS verified - the PDF's line overruns its margin by 1.4 pt and its tail is off the paper; the render wraps it onto a second line |
| 2026-11-08 | 304_package_insert_small_print | PASS | six numbered sections, bold heads and every line break the same; the emphasis question reports 6 of 9 lost and the render is bold - tool blind spot |
| 2026-11-08 | 305_vaccination_certificate | PASS | table, seal and QR in place; the eye passed and the numbers failed, so the order question is the measurement bug - the PDF draws each cell as its own line and the render joins them with tabs |
| 2026-11-08 | 306_clinical_protocol_synopsis | PASS | synopsis table and the schedule grid complete, marks in their cells; the table sits 4.7 pt high |
| 2026-11-08 | 310_court_judgment | PASS | cause title, eight numbered paragraphs and the JUDGE block; the centred heading renders 17.5 % narrower because the page tracks it and the run carries no w:spacing |
| 2026-11-08 | 311_fir_police_form | FAIL | missing:560067 verified - the render breaks the pin as '5 60067' and welds the Mobile label onto the address cell |
| 2026-11-08 | 312_affidavit_stamp_paper | FAIL | extra:NOTARY verified - the circular notary seal repeats its arc text, the PDF draws it once; the seal is a rotated stamp, one try only |
| 2026-11-08 | 313_power_of_attorney | PASS | recitals, four numbered powers, schedule and witness rules |
| 2026-11-08 | 314_tender_rfp_boq | PASS | both tables complete, the tax rows under the BOQ, every sub-total figure whole; the BOQ table sits 6.4 pt high |
| 2026-11-08 | 315_gazette_notification | FAIL | moved:into force on the date of their verified, 69.8 pt - the three columns run 70 pt long and push the footer down the sheet; the column pitch is 12.6 pt against the page's 8.3 |
| 2026-11-08 | 316_contract_with_schedules | PASS | four clauses, schedules A and B and the schedule C charge table; the charge table sits 3.2 pt high |
| 2026-11-08 | 317_rti_response | PASS | letter head, five numbered points and the enclosure line |

The five fails are all one of three causes: a band of label/value pairs split into one paragraph
per field (301), a table's own top y not reproduced (311), a column pitch taken across a column break
(315), a rotated seal's arc text repeated (312), and a line the PDF drew past the right margin being
wrapped instead (303). None of them was fixed this run; each is recorded with its measurement and
its tries.
| 2026-11-08 | 318_court_summons_form | PASS | cause title, cause table, notice and the court seal; the PDF's notice line overruns its margin and the render keeps the word |
| 2026-11-08 | 320_balance_sheet_statutory | PASS | both statements, every figure in its column and the signature block |
| 2026-11-08 | 321_auditors_report | PASS | six numbered paragraphs, the basis and key-audit-matter heads and the signature block |
| 2026-11-08 | 322_mutual_fund_factsheet | PASS | scheme, holdings and sector tables, the riskometer dial and the footer note |
| 2026-11-08 | 323_credit_card_statement | PASS | ledger, rewards summary, spend-by-category bars and the barcode |
| 2026-11-08 | 324_loan_amortisation_schedule | PASS | seven sheets, 40 rows each, every figure in its column; the last sheet is the header alone on both sides |
| 2026-11-08 | 325_demat_holdings_statement | PASS | holdings table, transaction table and the portfolio total |
| 2026-11-08 | 326_itr_computation | PASS | both schedules, the verification block and the QR |
| 2026-11-08 | 330_cad_drawing_sheet | PASS | plan, dimension strings, revision table and title block; the hatched zone renders as a grey fill |
| 2026-11-08 | 331_pid_diagram | PASS | every label back inside its equipment box after the anchored-position fix |
| 2026-11-08 | 332_bom_on_drawing | PASS | one sheet now; the BOM table and the assembly drawing with its bubbles |
| 2026-11-08 | 333_datasheet_spec_tables | PASS | three spec tables, every value in its column |
| 2026-11-08 | 334_patent_document | PASS | form, abstract, FIG.1 boxes with their labels and the claims |
| 2026-11-08 | 335_msds_safety_data_sheet | PASS | eight numbered sections, the pictograms and the composition table |
| 2026-11-08 | 340_bill_of_lading | PASS | party boxes, goods table, totals and the barcode |
| 2026-11-08 | 402_calendar_month_grid | FAIL | wraps:Board meeting verified - one line on the page, two in the render, and the annotation cell is 76 pt wide; the page count is now right (the grid no longer doubles its annotated rows), and the footer sits 4.2 pt high |

## Rows older than 8 Nov are suspect

Seventeen FAIL rows were re-checked on 8 Nov by converting the documents again. Every one of the
seventeen now has the right page count, and three of them (56_table_indented_from_margin,
bus-timetable-station-left-times-right, 303_discharge_summary) no longer fail on the specific
claim their row records. Those rows are stale.

They are left as they are rather than edited by hand, because a row is evidence of what was seen
at a run and rewriting it by hand would make the file say something no run observed. The next
full visual run will overwrite them with what it actually finds.

| 2026-11-08 | 300_prescription_rx | PASS | header band, patient box, Rx table, advice, signature and QR all in place |
| 2026-11-08 | 301_lab_report_panel | FAIL | moved:MPL03184471 (34.3 pt) and moved:REFERRED BY (8.0 pt) - the four-column label/value band is emitted one field per paragraph |
| 2026-11-08 | 302_radiology_report | PASS | letterhead, patient band, findings and impression paragraphs, signature |
| 2026-11-08 | 303_discharge_summary | FAIL | breaks:WARNING SIGNS - the PDF's line ends at 'needed', the render puts 'day.' on a second line |
| 2026-11-08 | 304_package_insert_small_print | PASS | six numbered sections in small print, one column, every paragraph whole |
| 2026-11-08 | 305_vaccination_certificate | FAIL | the circular seal's arc text is emitted as horizontal runs - 'TIONAL' and 'IMMUNISATION' land 8-10 pt left of their glyphs, reading order 47.1 % of 27 rows |
| 2026-11-08 | 306_clinical_protocol_synopsis | PASS | synopsis table and the schedule-of-assessments grid, every column in place |
| 2026-11-08 | 310_court_judgment | PASS | cause title, eight numbered paragraphs and the signature block |
| 2026-11-08 | 311_fir_police_form | FAIL | missing:560067 - the render welds 'Bengaluru 560067' to 'Mobile', and the table sits 15.7 pt high |
| 2026-11-08 | 312_affidavit_stamp_paper | PASS | stamp paper box, five paragraphs, verification and the notary seal; eye passed, order 67.6 % is the known tab-joined-row measurement bug |
| 2026-11-08 | 313_power_of_attorney | PASS | title, four numbered clauses, schedule and signature lines |
| 2026-11-08 | 314_tender_rfp_boq | FAIL | moved:Sub-total -24.2 pt: the BOQ's own rules land within 0.1 pt of the page's (15.0 pt pitch, 288.4 vs 288.5), but the cell text sits one row high - 'Earthwork' at 265.2 against the page's 278.0 |
| 2026-11-08 | 315_gazette_notification | FAIL | moved:RAJESH KUMAR, Jt. Secy. +69.8 pt - the three-column page's footer is placed at the flow's end instead of at the page's own y; order 47.1 % of 21 rows |
| 2026-11-08 | 316_contract_with_schedules | PASS | five numbered clauses and the Schedule C charges table |
| 2026-11-08 | 317_rti_response | PASS | letter head, date, six numbered points and the enclosure line |
| 2026-11-08 | 371_experience_certificate | FAIL | order - 28 rows in the PDF, 24 in the render, 61.5 % in sequence; the seal's arc text is emitted per glyph and its two circles are not drawn |
| 2026-11-08 | 372_timesheet_grid | PASS | grid, every day column and the totals row on the page's rows; the navy band is back |
| 2026-11-08 | 373_leave_application_form | FAIL | moved:Family function at native place -22.4 pt: the Reason row is one line short, so its text sits on the row rule |
| 2026-11-08 | 374_org_chart | PASS | the three bottom boxes print label, name and staff on their own lines after the cell-line floor was made to work; the footer under the table now sits 7 pt low |
| 2026-11-08 | 375_attendance_register | PASS | navy band, 12 employee rows and 31 day columns on the page's grid |
| 2026-11-08 | 380_runbook_terminal_output | PASS | navy band, four numbered steps and their dark code blocks on the page's lines |
| 2026-11-08 | 381_incident_report_timeline | PASS | title band, summary, timeline table and action items on the page's rows |
| 2026-11-08 | 382_architecture_diagram | PASS | six boxes, their fills, every arrow and label on the page's positions |
| 2026-11-08 | 383_api_docs_page | PASS | navy band, both spec tables, the curl block and the JSON response |
| 2026-11-08 | 390_wide_data_appendix | PASS | eleven columns and all 17 records, every figure in its column |
| 2026-11-08 | 391_survey_questionnaire_grid | PASS | five Likert headers and every tick in its column; the PDF's own text layer holds the same welded header ("Strongly\\x00agree Agree"), so the eye's first read was wrong |
| 2026-11-08 | 392_statistical_console_output | PASS | monospace console output, coefficient table and the note, line for line |
| 2026-11-08 | 393_spectrum_peak_table | PASS | the spectrum chart and the five-column peak table on the page's rows |
| 2026-11-08 | 394_map_with_legend | PASS | polygon, river, both roads, every marker, the legend, scale bar and north arrow |
| 2026-11-08 | 400_comic_page_speech_bubbles | FAIL | moved:412 pallets -166.2 pt, moved:MEANWHILE, AT THE LOADING DOCK -159.6 pt, moved:Ship by noon -166.9 pt - the third row of panels is a sheet high and its bubble text rises to the panel top |
| 2026-11-08 | 303_discharge_summary | FAIL | moved:WARNING SIGNS verified on both axes - x=28.0 in the PDF against 16.6 in the render, 11.4 pt and seven times the x tolerance, with 2.8 pt on y; the line also wraps, order 88.5 % of 25 rows with 27 in the render. Two fixes measured and reverted - see REMAINING-DEFECTS.md |
| 2026-11-08 | 56_table_indented_from_margin | PASS | re-checked 8 Nov 20:20: eye pass - the rate table is indented 44 pt from the margin with all nine rows and both signature blocks. The numbers' order 93.0 % of 21 rows is the tab-joined-row measurement bug, recorded as a blind spot, not a defect |
| 2026-11-08 | bus-timetable-station-left-times-right | FAIL | pagecount verified 1 in / 2 out, moved:10:15 verified at 66.8 pt (the DEPART and ARRIVE cells are stacked), order 4.0 % of 39 rows against 60 |
| 2026-11-08 | 303_discharge_summary | FAIL | order 88.5 % of 25 rows, the tab-joined-row measurement bug; the eye's wraps:WARNING SIGNS was REFUTED by the verifier - 2 lines on both sides - so no wrap defect was fixed |

## v3 batch 1 (300-317) - final sweep, 8 Nov 21:03 - 15 documents, every page looked at, every finding verified

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-08 | 300_prescription_rx | PASS | header band, patient box, Rx table, advice, signature and QR all on the page's lines |
| 2026-11-08 | 301_lab_report_panel | FAIL | moved:MPL03184471 34.3 pt, moved:REFERRED BY 8.0 pt - the four-column label/value band is emitted one field per paragraph |
| 2026-11-08 | 302_radiology_report | PASS | letterhead, patient band, findings and impression, signature on the page's lines |
| 2026-11-08 | 303_discharge_summary | FAIL | breaks:WARNING SIGNS verified - the PDF's line ends at 'needed' and no render line does |
| 2026-11-08 | 304_package_insert_small_print | PASS | six numbered sections in small print, every paragraph whole |
| 2026-11-08 | 305_vaccination_certificate | FAIL | moved:IMMUNISATION unverifiable - the seal's arc text is drawn per glyph, so the needle is on neither side; order 47.1 % of 27 rows |
| 2026-11-08 | 306_clinical_protocol_synopsis | FAIL | moved:SCHEDULE OF ASSESSMENTS 7.2 pt high - the synopsis table above renders 7.2 pt short of the page's own extent |
| 2026-11-08 | 310_court_judgment | PASS | cause title, eight numbered paragraphs and the signature block |
| 2026-11-08 | 311_fir_police_form | FAIL | missing:560067 and moved:Mobile 61.3 pt - the pin is cut at the cell edge and '60067Mobile' welded |
| 2026-11-08 | 312_affidavit_stamp_paper | PASS | stamp paper box, five paragraphs, verification and the notary seal; eye passed, order 67.6 % is the tab-joined-row measurement bug |
| 2026-11-08 | 313_power_of_attorney | PASS | title, four numbered clauses, schedule and signature lines |
| 2026-11-08 | 314_tender_rfp_boq | FAIL | moved:Sub-total 27.0 pt - the BOQ's rows render taller than the page's own 12.2 pt pitch |
| 2026-11-08 | 315_gazette_notification | FAIL | moved:RAJESH KUMAR 69.8 pt, order 47.1 % of 21 rows - the three-column page's footer sits at the flow's end |
| 2026-11-08 | 316_contract_with_schedules | PASS | five numbered clauses and the Schedule C charges table |
| 2026-11-08 | 317_rti_response | PASS | letter head, date, six numbered points and the enclosure line |

8 pass, 7 fail. 16 findings, 14 verified, 1 refuted (314 wraps:Average annual turnover - 2 lines on
both sides), 1 unverifiable (305 moved:IMMUNISATION). One disagreement: 312's eye passed while the
numbers failed on order 67.6 % - the tab-joined-row measurement bug, not a document defect. 306 is
new to this list: the synopsis table renders 7.2 pt short and the heading under it rides up.

## v3 batch 2 (318-340) - final sweep, 8 Nov 23:09 - 15 documents, 22 pages, every page looked at, every finding verified

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-08 | 318_court_summons_form | FAIL | breaks:TAKE NOTICE ... determined in your verified - the PDF's line ends at "your" and no render line does; the render fits "absence." onto the same line |
| 2026-11-08 | 320_balance_sheet_statutory | PASS | statutory profit and loss, sixteen rows and the notes extract, every figure in its column |
| 2026-11-08 | 321_auditors_report | PASS | letterhead, opinion, basis, five numbered paragraphs and the signature block, line for line |
| 2026-11-08 | 322_mutual_fund_factsheet | PASS | nav band, both tables, the riskometer dial and the footer; eye passed, the numbers failed on reading order only - the tab-joined-row measurement bug |
| 2026-11-08 | 323_credit_card_statement | FAIL | count:Travel, count:Shopping, count:Fuel, count:Groceries, count:Health all verified - the spend-by-category block keeps its six amounts and loses five of its six labels |
| 2026-11-08 | 324_loan_amortisation_schedule | PASS | seven sheets, forty amortisation rows each, every figure in its column; the last sheet is blank in the PDF and blank in the render |
| 2026-11-08 | 325_demat_holdings_statement | PASS | holder band, seven holdings and three transactions in their columns; eye passed, the numbers failed on reading order only - the tab-joined-row measurement bug |
| 2026-11-08 | 326_itr_computation | FAIL | moved:Total tax payable verified at x 163.1->135.3, y 390.9->377.3 - the three summary rows are emitted below the tax table instead of in it |
| 2026-11-08 | 330_cad_drawing_sheet | PASS | plan, dimension labels, revision table and title block on the page positions; eye passed, the numbers failed on reading order only - the tab-joined-row measurement bug |
| 2026-11-08 | 331_pid_diagram | PASS | both pumps, the valves, the loop, the legend box and the note |
| 2026-11-08 | 332_bom_on_drawing | FAIL | moved:2 6.8 pt and moved:5 7.6 pt after the cellsFilled fix; before it the frame was written as an invented 7x3 table at 33.1 pt with 68 rules against the page's 43 |
| 2026-11-08 | 333_datasheet_spec_tables | PASS | three spec tables, every parameter and every pin row in its column |
| 2026-11-08 | 334_patent_document | PASS | form 1 head, abstract, the fig 1 boxes and five claims |
| 2026-11-08 | 335_msds_safety_data_sheet | PASS | four pictograms, eight numbered sections and the composition table |
| 2026-11-08 | 340_bill_of_lading | PASS | every box, two item rows, the total line and the barcode |

11 pass, 4 fail. 18 findings, 16 verified, 2 refuted (326 count:Taxable amount - the header cell
spans two grid columns and python-docx reports it twice; 332 order - 100 % after the fix). Three
disagreements, all the same measurement bug: 322, 325 and 330 passed the eye and failed the
numbers on reading order alone, because the PDF draws each cell as its own line and the render
joins a row's cells with tabs. That blind spot is now recorded seven times and is not a document
defect.

v3 batch 3 (342-371), processed from scratch: 15 documents, 16 pages, every page opened at 130 dpi
before visual.py was run. 21 findings emitted, 20 verified, 1 refuted. 4 pass, 11 fail. Two engine
fixes shipped this run, both measured: the column-edge subtraction in DocxWriter (which put three
lines at x=0.1) and the size-aware shapes check in verify.py (which had called two real losses
refuted because the counts happened to match).

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-09 | 342_packing_list | PASS | header band, exporter and consignee block, five-column table, total line, marks box and declaration |
| 2026-11-09 | 343_air_waybill | FAIL | order 81.2 % of 15 rows, 17 in the render - each "1,144.00" cell wraps its last 0 onto a line of its own |
| 2026-11-09 | 344_customs_declaration | FAIL | moved:CLEARED verified 9.8 pt high; the eye saw the stamp off its place and the numbers held it |
| 2026-11-09 | 350_question_paper | FAIL | pagecount 1 -> 2: page 1 runs on to a second sheet |
| 2026-11-09 | 351_omr_answer_sheet | FAIL | rules 13 in the PDF, 32 in the render - a ruled grid is drawn round rows 16-45 |
| 2026-11-09 | 352_certificate_ornate_border | FAIL | shapes 12 (8 large) in the PDF, 12 (4 large) in the render - both page borders are gone, only the corner curls are drawn |
| 2026-11-09 | 353_admit_card | FAIL | moved:Controller of Examinations 47.6 pt low - the Paper table above it is charged more height than the page's rows |
| 2026-11-09 | 360_restaurant_menu | FAIL | moved:Butter Naan 149.1 pt up - the four menu groups are drawn as tables with a tighter row pitch than the page |
| 2026-11-09 | 361_product_catalogue_grid | PASS | six product cards in two rows of three, image, name, MRP, code and barcode in each |
| 2026-11-09 | 362_price_list_dense | PASS | six columns of item, code and price with the heading and the footnote |
| 2026-11-09 | 363_warranty_card | PASS | warranty box, six terms, sticker box, QR and the register URL under its own text |
| 2026-11-09 | 364_event_ticket | FAIL | count:WS24-4471-0082 2 in the PDF, 1 in the render - the tear-off stub loses its ticket number |
| 2026-11-09 | 365_recipe_card | FAIL | wraps:to taste - the PDF has 2 lines, the render wraps them into 3 |
| 2026-11-09 | 370_offer_letter | FAIL | moved:6,00,000 13.0 pt high - the offer table's rows are shorter than the page's own pitch |
| 2026-11-09 | 371_experience_certificate | FAIL | shapes 2 large in the PDF, 0 in the render - the seal's two rings come out as 16 x 9 pt blobs |

v3 batch 4 (372-401), processed from scratch on 9 Nov: 15 documents, 15 pages, every page opened
at 130 dpi before visual.py was run. 6 findings emitted on the first pass, 6 verified, 0 refuted;
after the fix 5 findings, 5 verified. 12 pass, 3 fail.

One engine fix shipped, and it is the fix for a whole class of page. `bandLeftTw` subtracted the
column's left edge from a paragraph's indent whenever the column pass had found more than one band -
but a form or a brochure panel page has gutters, so its paragraphs carry column 1, 2 and 3 while the
section still declares ONE column and the writer never emits `w:cols w:num`. The subtraction then
collapsed the line to x=0. On 401_trifold_brochure the middle panel's heading and first line were
drawn on top of the cover panel, 300.6 pt left of where the page put them; after the fix they sit at
300.8 against the page's 300.6. It also corrected the x of 400's bottom block (-27.9 pt -> 0.1).
G2 clean on 208, position ratchet clean on 208 (no REGRESSED line), 28.5 % of lines in tolerance
against the 11.7 % recorded in the baseline.

The eye passed 373_leave_application_form and the numbers caught it: 15 of 17 emphasised lines had
lost their bold. Re-opened the page at 2.4x and the eye agreed - "ANANYA RAO", "Operations
Analytics" and "12-04-2021" are bold in the PDF and regular in the render, because the writer joins
the label and the value into one run with a `w:br` and emits no `w:b`. Recorded as an eye blind spot
at 130 dpi and as the missing claim type the ledger already names.

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-09 | 372_timesheet_grid | PASS | header band, five project rows, day columns, totals and signatures all in place |
| 2026-11-09 | 373_leave_application_form | FAIL | rules 11 in the PDF, 28 in the render - every label/value cell is split into two table rows, so six extra dividers cut through the field block, and the values lose their bold |
| 2026-11-09 | 374_org_chart | PASS | four levels of boxes and every connector, footnote lines at the foot |
| 2026-11-09 | 375_attendance_register | PASS | employee column and 31 day columns with the P/A marks, footer legend |
| 2026-11-09 | 380_runbook_terminal_output | PASS | four numbered steps, four dark code blocks, escalation line |
| 2026-11-09 | 381_incident_report_timeline | PASS | header band, summary, eight-row timeline table, action items table |
| 2026-11-09 | 382_architecture_diagram | PASS | seven boxes, connectors, edge labels and the footer notes |
| 2026-11-09 | 383_api_docs_page | PASS | header band, four tables, request and response blocks |
| 2026-11-09 | 390_wide_data_appendix | PASS | 21-column measurement table, all header labels and 12 sample rows |
| 2026-11-09 | 391_survey_questionnaire_grid | PASS | nine statements, five rating columns, tick marks in the right cells, comment rules |
| 2026-11-09 | 392_statistical_console_output | PASS | R console output line for line, coefficient table, signif codes |
| 2026-11-09 | 393_spectrum_peak_table | PASS | spectrum chart and the three-row peak table |
| 2026-11-09 | 394_map_with_legend | PASS | site polygon, river, roads, markers, legend, scale bar and compass |
| 2026-11-09 | 400_comic_page_speech_bubbles | FAIL | moved:MEANWHILE verified 173.8 pt high - the bottom panel and its whole block ride above the row-2 panels, and reading order is 80.0 % of 15 rows |
| 2026-11-09 | 401_trifold_brochure | FAIL | missing:CONTACT US - the rotated back panel is drawn 79 pt right of the page's 743, so its lines run off the sheet and the render loses them. The indent defect that put WHY CHAKAN on the cover panel is fixed |

b80 batch 1 (01-15 stamps, 16-20 txtpos), re-processed from scratch on 9 Nov: 20 documents, 21 pages,
every page opened at 130 dpi before visual.py was run. 34 findings emitted, 32 verified, 1 refuted,
1 unverifiable. 8 pass, 12 fail.

One tool fix shipped: `rotated:<text>` is a tenth claim type, and it exists because nine of these
documents could not be claimed at all. A 15-degree stamp is written as a text box carrying
`<a:xfrm rot>`; the geometry is right and LibreOffice draws the words level. `moved:` measured the
words 3.9 pt across and called them in tolerance, `missing:` found them in the render's text layer,
`count:` matched on both sides - so every one of the nine came back UNVERIFIABLE and the document's
FAIL had nothing behind it. The check compares the PDF line's writing direction with the render's:
'15.0 degrees in the PDF, 0.0 in the render'. First written modulo 180, which refuted 04 - an
upside-down stamp is not the same line as an upright one - and the full-turn comparison fixed it.

Everything else in this batch is a known class: the rotated stamp (settled, D-16/ST-A), the footer
that rides above the page's own line on a page carrying a table (D-01's remaining half, blocked on
table height), and 20's number-and-clause on separate paragraphs (D-07's family, measured and
reverted on 8 Nov). No new engine fix was warranted and none was made.

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-09 | 01_stamp_rotated_15deg_upright | FAIL | rotated:AUTHORISED SIGNATORY - 15.0 degrees in the PDF, 0.0 in the render; the footer 125.3 pt high |
| 2026-11-09 | 02_stamp_rotated_15deg_upleft | FAIL | rotated:GOODS RECEIVED - 15.0 degrees in the PDF, 0.0 in the render; the footer 130.8 pt high |
| 2026-11-09 | 03_stamp_vertical_90deg | FAIL | rotated:INTERNAL AUDIT - 90.0 degrees in the PDF, 0.0 in the render; the footer 255.1 pt high |
| 2026-11-09 | 04_stamp_180deg_upside_down | FAIL | rotated:DUPLICATE ISSUED - 180.0 degrees in the PDF, 0.0 in the render; the footer 130.8 pt high |
| 2026-11-09 | 05_round_company_seal_curved_text | FAIL | the seal's arc text lands across the body 600 pt above the seal; moved:BENGALURU is UNVERIFIABLE because the arc is drawn one glyph at a time |
| 2026-11-09 | 06_rect_paid_stamp_red_transparent | FAIL | rotated:PAID - 8.0 degrees in the PDF, 0.0 in the render |
| 2026-11-09 | 07_stamp_over_table | FAIL | rotated:QUALITY APPROVED - 12.0 degrees in the PDF, 0.0 in the render; moved:KAVERI TEXTILES 30.9 pt, footer 182.9 pt high |
| 2026-11-09 | 08_two_overlapping_stamps | FAIL | rotated:PAID - 9.0 degrees in the PDF, 0.0 in the render |
| 2026-11-09 | 09_stamp_font_not_embedded | FAIL | rotated:AUDITED - 11.0 degrees in the PDF, 0.0 in the render |
| 2026-11-09 | 10_stamp_as_image | PASS | stamp, table and totals all on the page's own rows |
| 2026-11-09 | 11_stamp_with_signature_image | PASS | stamp, signature squiggle and the four body blocks in place; order 88.4 % is the tab-joined-row blind spot |
| 2026-11-09 | 12_stamp_across_page_break | PASS | both pages: agreement body, schedule of property and the SUB-REGISTRAR stamp |
| 2026-11-09 | 13_stamp_non_english | PASS | the Kannada stamp is drawn at its angle and its words survive |
| 2026-11-09 | 14_stamp_chars_positioned_td | FAIL | moved:Inspection certificate QA/IC/2025/1147 - the footer sits 229.6 pt above the page's own line |
| 2026-11-09 | 15_stamp_on_scanned_page | FAIL | moved:TRUE COPY -78.3 pt across and 722.5 pt up; the 9-degree stamp lands at the top of the sheet |
| 2026-11-09 | 16_right_aligned_amounts_txtpos | PASS | ledger rows, right-aligned amounts and the closing balance line |
| 2026-11-09 | 17_three_column_widths_txtpos | PASS | 0.0 % of pixels differ |
| 2026-11-09 | 18_centred_heading_left_body_txtpos | PASS | 0.0 % of pixels differ |
| 2026-11-09 | 19_hanging_indent_txtpos | PASS | 0.0 % of pixels differ |
| 2026-11-09 | 20_numbered_list_separate_column_txtpos | FAIL | moved:2. 12.4 pt - the number and its clause are two paragraphs, so every item starts its text a line below its number |

## 9 Nov, 03:07 IST - b80 batch 2 (21-40), the typeface and text-position batch

Twenty documents, one page each, all seventeen steps in order. Every page opened at 130 dpi
before visual.py was run. Fifteen pass, five fail. Eleven findings emitted, nine verified
against the PDF, two refuted, none unverifiable.

Position for the batch: 47.8 % of lines within tolerance (x 1.5 pt, y 3.0 pt, size 0.5 pt,
colour CIE76 3), font size 100.0 %, font name 80.0 %, colour 99.7 %. These are the txtpos
documents, so a line tolerance of about half is the batch's own character, not a regression:
no baseline was moved.

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-09 | 21_form_labels_x60_values_x300_txtpos | PASS | label/value band at x=60 and x=300, 15 rows, declaration, certificate block and footer |
| 2026-11-09 | 22_invoice_four_columns_txtpos | PASS | four columns, 12 item rows, tax block and amount-in-words line |
| 2026-11-09 | 23_timetable_grid_txtpos | PASS | 7 day rows x 7 period columns, every code in its cell, legend and Principal |
| 2026-11-09 | 24_address_block_indents_txtpos | PASS | nested address indents stepwise, enclosures and signature block |
| 2026-11-09 | 25_signature_block_underscores_txtpos | PASS | two signature blocks with rules, annexure rates table, witnesses |
| 2026-11-09 | 26_footnote_marker_bottom_note_txtpos | PASS | abstract, body, the marker line and the bottom footnote |
| 2026-11-09 | 27_two_column_left_short_txtpos | FAIL | moved:In other news verified y 472.2 -> 501.9 (29.7 pt); order 84.2 % of 27 rows, 30 in the render |
| 2026-11-09 | 28_value_overflows_cell_txtpos | FAIL | order 79.1 % of 20 rows, 23 in the render; missing:Nos and overlap both REFUTED |
| 2026-11-09 | 29_dot_leaders_txtpos | PASS | dot leaders to every price, totals block right aligned |
| 2026-11-09 | 30_mixed_font_sizes_one_baseline_txtpos | FAIL | wraps:ADMISSION NOTIFICATION 2025-26 verified 2 lines -> 3; B.E. / B.Tech. - First Year left the heading's baseline |
| 2026-11-09 | 31_times_body_arial_headings | PASS | heading band, numbered resolutions, proxy paragraph and signature |
| 2026-11-09 | 32_serif_nondefault_body | PASS | serif body with italic headings, four paragraphs, imprint line |
| 2026-11-09 | 33_sans_nondefault_body | PASS | section bar, six-row timing table, two paragraphs, prepared/approved line |
| 2026-11-09 | 34_monospace_document | PASS | 36 numbered lines in column, PICTURE clauses aligned, closing note |
| 2026-11-09 | 35_four_typefaces_one_page | PASS | marks table, total line, faces note and signature line |
| 2026-11-09 | 36_embedded_subset_font | PASS | eight-row certificate table, certification paragraph, signature block |
| 2026-11-09 | 37_font_not_embedded_substitution | PASS | circular head, subject line, two body paragraphs and signature |
| 2026-11-09 | 38_faux_bold_italic_synthesised | FAIL | count:Study of self-compacting concrete using quarry dust as partial replacement verified 2 in the PDF, 1 in the render - both copies joined into one paragraph |
| 2026-11-09 | 39_small_caps_letter_spacing | FAIL | moved:N O T I C E T O M E M B E R S verified 13.2 pt low; the tracked heading loses its letter spacing, 172 pt wide in the PDF against 116 in the render |
| 2026-11-09 | 40_devanagari_shaping_font | PASS | devanagari head, dates, paragraph, six-row table and signature |

## 9 Nov 05:03 IST — b80 batch 3 (41-60), the colour and layout class

Twenty documents, 23 pages, every page opened at 130 dpi before visual.py ran, every finding
verified against the PDF. Thirteen pass, seven fail. Nineteen findings: fifteen verified, one
refuted, three unverifiable.

No colour finding at all in a batch whose whole subject is colour: navy header bands,
alternating row fills, green form borders and values, the yellow callout, the navy block with
white text, grey body under black headings and blue underlined links all came through.

Position for the batch was not recorded - the position ratchet runs at the end of a batch and
the engine did not change this run, so no baseline was touched.

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-09 | 41_coloured_headings_white_bg | PASS | green title and brown section headings, three sections, nine items, footer rule |
| 2026-11-09 | 42_table_coloured_header_alternating_rows | PASS | navy header band, alternating row fill, seven rows, right-aligned amounts |
| 2026-11-09 | 43_red_stamp_over_black_text | PASS | rasterised red stamp at its own angle over the body text, signature block |
| 2026-11-09 | 44_coloured_underlined_hyperlinks | PASS | five blue underlined links with grey urls, circular body and signature |
| 2026-11-09 | 45_coloured_callout_box | PASS | yellow callout with its border, body above and below, signature block |
| 2026-11-09 | 46_chart_coloured_labels_body_text | FAIL | moved:60.2 verified 4.9 pt; the chart is rebuilt larger, its gridlines are gone and the value labels sit inside the bars |
| 2026-11-09 | 47_grey_body_black_headings | PASS | grey body text under black headings, three numbered sections, keywords line |
| 2026-11-09 | 48_form_coloured_border_coloured_values | PASS | green form border, bold green values, twelve label rows, declaration |
| 2026-11-09 | 49_coloured_background_block_paragraph | PASS | navy block with four lines of white text, body below it |
| 2026-11-09 | 50_invoice_coloured_total_row | PASS | navy header and total row, six item rows, right-aligned amounts, amount in words |
| 2026-11-09 | 51_two_cm_margins | PASS | 2 cm margins on all sides, border box, three paragraphs, signature block |
| 2026-11-09 | 52_one_cm_margin_wide_body | FAIL | moved:434.2 verified -12.7 pt; the table's header row is collapsed and its text is clipped at the top edge |
| 2026-11-09 | 53_single_space_body_15_headings | PASS | 1.5 line headings, single-spaced body, four paragraphs, note and signature |
| 2026-11-09 | 54_two_column_body_full_width_header_footer | FAIL | moved:twenty dollars per tonne verified 54.9 pt, moved:above fifty hectares 110.0 pt; the columns are poured into one flow and each runs at twice its pitch |
| 2026-11-09 | 55_sidebar_box_beside_body | FAIL | shapes verified 1 against 2; the sidebar loses its fill, and moved:restored under the project 10.8 pt low |
| 2026-11-09 | 56_table_indented_from_margin | FAIL | moved:Shrinkage and fastness testing verified -11.8 pt; the header row is collapsed and clipped, the rows run tighter than the page |
| 2026-11-09 | 57_centred_title_page_left_body_pages | FAIL | moved:SRI VINAYAKA INSTITUTE OF TECHNOLOGY verified -126.4 pt; the title block sits at the top of the sheet instead of centred |
| 2026-11-09 | 58_header_rule_footer_rule | PASS | header rule with the by-law label and the footer rule, on both pages |
| 2026-11-09 | 59_landscape_mixed_portrait | PASS | portrait page then landscape page, the landscape table's every column and row in place |
| 2026-11-09 | 60_page_border | FAIL | missing:KENGERI CAMPUS unverifiable (per-glyph arc); the seal's arc text is gone, only the rings and SEAL 2025 remain |
| 2026-11-09 | 300_prescription_rx | PASS | header band, patient box, four-row Rx table, advice block, signature and QR code |
| 2026-11-09 | 301_lab_report_panel | FAIL | moved:MPL03184471 verified 8.7 pt; the label/value band is emitted one field per paragraph so the four values sit ragged, and order 94.7 % |
| 2026-11-09 | 302_radiology_report | PASS | header rule, patient and study band, findings and impression in the page's own order |
| 2026-11-09 | 303_discharge_summary | FAIL | breaks:WARNING SIGNS verified; the page's line runs past the paper and the render wraps 4 times a day. onto a second line |
| 2026-11-09 | 304_package_insert_small_print | PASS | small print leaflet, seven numbered sections, contents of the pack, marketing block |
| 2026-11-09 | 305_vaccination_certificate | FAIL | order 42.9 % of 27 rows, 29 in the render; the seal's arc text is written as horizontal runs (moved:NATIONAL IMMUNISATION refuted, it matched the title) |
| 2026-11-09 | 306_clinical_protocol_synopsis | FAIL | moved:Sponsor verified 4.7 pt high; the assessment table's first row sits 4.7 pt above the page's (x verified correct, the eye read it as an indent) |
| 2026-11-09 | 310_court_judgment | PASS | centred cause title, between/and block, eight numbered paragraphs, Sd/- JUDGE |
| 2026-11-09 | 311_fir_police_form | FAIL | missing:560067 verified; Bengaluru 560067 arrives as Bengaluru 5 60067Mobile, and moved:Mobile 66.9 pt - the D-07 baseline join |
| 2026-11-09 | 312_affidavit_stamp_paper | PASS | stamp paper box, affidavit body, deponent and verification, notary seal with its arc text |
| 2026-11-09 | 313_power_of_attorney | PASS | centred title, four numbered powers, schedule, principal and witness rules |
| 2026-11-09 | 314_tender_rfp_boq | FAIL | moved:Sub-total verified -24.2 pt; the rows run at 13.2 pt against the page's 15.0 so the drift grows down the table |
| 2026-11-09 | 315_gazette_notification | FAIL | moved:RAJESH KUMAR, Jt. Secy. verified +69.8 pt; the three-column page's footer is placed at the end of the flow, order 47.1 % |
| 2026-11-09 | 316_contract_with_schedules | PASS | four numbered clauses, schedule A and C with its four-row charges table, signature rules |
| 2026-11-09 | 317_rti_response | PASS | letterhead, date, subject line, six numbered points, enclosure |
| 2026-11-09 | 318_court_summons_form | FAIL | moved:B verified 160.5 pt; the seal's arc text is scattered to the page's left edge, order 50.0 % |
| 2026-11-09 | 320_balance_sheet_statutory | PASS | statement of profit and loss, the notes table and both signature blocks in the page's own places |
| 2026-11-09 | 321_auditors_report | PASS | six numbered sections, bold headings, signature block |
| 2026-11-09 | 322_mutual_fund_factsheet | FAIL | moved:very high risk verified 70.0 pt; the riskometer legend and caption sit below the dial, order 89.2 % |
| 2026-11-09 | 323_credit_card_statement | FAIL | count:Shopping verified 3 in the PDF 2 in the render; the spend-by-category labels are gone, moved:Other 58.3 pt |
| 2026-11-09 | 324_loan_amortisation_schedule | FAIL | moved:4,164,306.09 verified -5.5 pt; the schedule's table sits 5.5 pt high on all seven pages |
| 2026-11-09 | 325_demat_holdings_statement | PASS | holder band, seven-column ISIN table, total value, transactions table (order 92.3 % is the tab-join measurement bug) |
| 2026-11-09 | 326_itr_computation | PASS | name band, schedule table, tax computation table, verification and QR code (order 94.9 % is the same measurement bug) |
| 2026-11-09 | 330_cad_drawing_sheet | PASS | dimension lines with labels, column dots, hatch, north arrow, both title tables (order 81.1 % is the same measurement bug) |
| 2026-11-09 | 331_pid_diagram | PASS | two pumps, valves, pipe runs with arrows, legend box, footer |
| 2026-11-09 | 332_bom_on_drawing | FAIL | moved:8.40 verified -5.2 pt; the BOM table sits 5.2 pt high and its header row lost the grey fill |
| 2026-11-09 | 333_datasheet_spec_tables | FAIL | moved:SPI clock frequency verified -24.0 pt; section 2's rows are pitched short so rules cut through the text |
| 2026-11-09 | 334_patent_document | PASS | form heading, title, abstract, the three-box figure with arrows, five claims, footer |
| 2026-11-09 | 335_msds_safety_data_sheet | PASS | four hazard diamonds, sections 1-8, the CAS table, footnote |
| 2026-11-09 | 340_bill_of_lading | PASS | shipper/consignee/notify grid, vessel band, cargo table with total, on-board clause, three signature boxes, barcode |

## v3 corpus - batch 3 (341-370), 9 Nov

Fifteen documents, sixteen pages (350 carries two). Every page opened before any number was read;
every finding verified against the PDF: 14 findings, 14 verified, 0 refuted, 0 unverifiable.
Nine pass, six fail. Run started 08:08 IST.

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-09 | 341_shipping_manifest | PASS | 12-column manifest table with all 24 rows, header band, totals line and footer in the page's own places |
| 2026-11-09 | 342_packing_list | PASS | carton table, totals line, marks and numbers box, declaration and signature |
| 2026-11-09 | 343_air_waybill | FAIL | moved:Declared value verified +7.0 pt; the fourth label of the header band sits low while the other three are on the page's baseline, 2 overlap pairs |
| 2026-11-09 | 344_customs_declaration | PASS | IEC/customs grid, item table, total value line, CLEARED stamp and both signature boxes |
| 2026-11-09 | 350_question_paper | FAIL | pagecount verified 1 page in the PDF and 2 in the render; the five modules spill onto a second sheet, order 40.7 % of 52 rows |
| 2026-11-09 | 351_omr_answer_sheet | FAIL | rules verified 13 in the PDF 15 in the render; the bubble grid is put in a ruled table box the page does not draw and the last rows spill below it |
| 2026-11-09 | 352_certificate_ornate_border | FAIL | order verified 21 rows in the PDF 25 in the render; the seal's arc text is emitted as horizontal runs. shapes REFUTED - the ornate border and its corner curls are exact |
| 2026-11-09 | 353_admit_card | PASS | photo box, register band, paper table, venue, instructions, QR and barcode (order 78.4 % is the band-join measurement) |
| 2026-11-09 | 360_restaurant_menu | FAIL | rules verified 5 in the PDF 13 in the render; both menu blocks are enclosed in ruled boxes the page does not draw, with empty rows between items |
| 2026-11-09 | 361_product_catalogue_grid | PASS | six product cards with image, title, price, code, min order and barcode |
| 2026-11-09 | 362_price_list_dense | PASS | three groups of 19 rows of code, name and price in the page's three columns |
| 2026-11-09 | 363_warranty_card | PASS | header box, model band, six numbered terms, sticker box, QR and footer |
| 2026-11-09 | 364_event_ticket | PASS | ticket band, delegate block, rotated edge text, tear-off stub and barcode (order 88.9 % is the rotated edge text joining a band) |
| 2026-11-09 | 365_recipe_card | FAIL | wraps:to taste verified; the ingredient amounts wrap onto a second line, so 2 tbsp becomes 2 over tbsp |
| 2026-11-09 | 370_offer_letter | PASS | letterhead, ref and date, subject, salary table, acceptance paragraph and signature block (order 93.1 % is the table header band split) |

## v3 corpus - batch 5 (402-417), 9 Nov

Thirteen documents, eighteen pages (412 carries five, 417 two). Every page opened before any
number was read; every finding verified against the PDF: 11 findings, 11 verified, 0 refuted,
0 unverifiable. Six pass, seven fail. 416_many_tiny_pages (300 pages) is deferred to its own run,
because a page-by-page look at it is 300 images and it is the only document in the corpus that
size. Run started 09:02 IST.

| Date | Document | Verdict | Why |
|---|---|---|---|
| 2026-11-09 | 402_calendar_month_grid | FAIL | wraps:Board meeting verified; the 25 cell wraps onto two lines where the page keeps Board meeting on one, which also makes 13 rows against the page's 12 |
| 2026-11-09 | 403_crossword_puzzle | PASS | 15x15 grid with its numbering, both clue columns and the footer in the page's places |
| 2026-11-09 | 404_sudoku_grid | PASS | 9x9 grid, the given digits and every box rule match |
| 2026-11-09 | 405_sheet_music_lyrics | PASS | three staves, chord symbols above them and the lyric lines below |
| 2026-11-09 | 406_passport_mrz_page | FAIL | count:BENGALURU verified 2 in the PDF 1 in the render; the Place of birth value is dropped where Place of issue keeps its own, and the .docx holds it once, so the loss is in the model, not the render |
| 2026-11-09 | 407_id_card_front_back | PASS | both cards, photo, barcode and the terms block |
| 2026-11-09 | 410_form_xobject_reused | FAIL | moved:Invoice line item verified 62.2 pt worst; all three XObject blocks sit 57.7 pt high because the blank space above the first block is not reproduced |
| 2026-11-09 | 411_nested_xobject_transforms | FAIL | moved:NESTED FORM verified 35.6 pt; the nested form's 1.6x scale is lost, so the 16 pt title comes out 10 pt and the rotated copy is pushed to x=-3.6 |
| 2026-11-09 | 412_page_labels_roman | PASS | all five pages, cover, front matter and body, with the page labels the file declares |
| 2026-11-09 | 413_tagged_pdf_actualtext | PASS | ActualText honoured by design: the glyph line is replaced by the key's text, which is the document's own point, and line 2 matches |
| 2026-11-09 | 414_transparency_softmask | FAIL | shapes verified 3 drawings in the PDF 1 in the render; the luminosity-masked bar is also drawn red where the page draws blue |
| 2026-11-09 | 415_inline_images | FAIL | moved:The checkerboard verified 149 pt; the inline image is blank in the render and the two lines under it rise to the top of the page |
| 2026-11-09 | 417_rotate180_and_mirrored | FAIL | missing:Page 2 verified; page 1 is right (/Rotate 180 ignored on purpose, the render upright as the page's note asks), page 2's mirrored text comes out as reversed per-glyph runs |
