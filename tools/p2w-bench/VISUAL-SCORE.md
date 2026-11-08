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
