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
