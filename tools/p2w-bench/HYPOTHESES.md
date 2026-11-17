# Hypotheses - what was tried, and what it proved

One section per defect class. Written by `hypothesis.py`, read by every attempt
before it forms its own theory. The point is that attempt twelve starts where
attempt eleven finished instead of where attempt one started.

RULED OUT entries are the expensive ones - they cost a calibration run each.
Do not re-test one without new evidence, and if you do, say what changed.

## 20_within_10pt (+4)

- CONFIRMED - Google renders w:line as a multiple of the substitute face's line height, so a 12 pt pitch advances 11.5 pt and the flow creeps up the page a little on every line
  evidence: Three probes through Drive on 12 Nov, one 12 pt advance each: w:line=240/before=0 -> 11.5 pt advance; w:line=14/before=226 -> 11.99 pt; w:line=1/before=239 -> 12.64 pt. Advance = w:before + 0.069 em, face-independent.
  recorded: 2026-11-12 13:22

- RULED OUT - Converting only the page-body flow (flowFromBox and flowRow) to a hairline box plus absolute w:before fixes the class
  evidence: 20 docs through Drive. 20_within_10pt: 62_two_col_newsletter_pull_quote 7->100, balance-sheet-and-profit-loss 7->53, 362_price_list_dense 1->15; 390_wide_data_appendix 1->1, electricity-bill 6->6, 57_centred 0->0. 1 of the 10 failing documents moved to pass. 8 of the 20 scored lower than baseline, newly failing 01_page_count/24_page_breaks/55_orientation_mix (311, 332), 27_text_off_page, 39_image_position, 44_header_footer.
  recorded: 2026-11-12 13:22

- UNTESTED - The same hairline-plus-before model in the table-cell path (rowLineTw) is where the class's dominant documents actually live
  evidence: electricity-bill and 362_price_list_dense are table/form documents; their body-flow lines are a minority, and both moved less than the body-only model predicts (6->6, 1->15)
  recorded: 2026-11-12 13:22

- RULED OUT - The class's dominant table documents fail because the line pitch inside the cells (rowLineTw) is wrong
  evidence: 362_price_list_dense converted with the current engine (2a68de6) and measured against Google's own export: 257 of 258 lines matched, dy = 2.6 pt on the page's first line, jumps to 13.6 pt at the table's first row and reaches only 16.7 pt at the page foot. That is one ~10 pt step at the table's top plus ~3 pt of drift over the whole 257-line table (0.012 pt/line), not a per-line pitch error inside the cells. Code: cells emit PdfToWord.Para through emitBlock -> para -> flowFromBox, the same method the reverted body-flow attempt already changed, so there is no separate cell pitch path to fix.
  recorded: 2026-11-12 20:49

- CONFIRMED - The ~10 pt table-top offset is the empty spacer paragraph emitted before the table
  evidence: 362_price_list_dense, 5 docx variants through Drive, ONLY the spacer varied: as emitted (w:line=276 exact, mark sz=2) first-row dy -13.59; spacer deleted -16.75; w:line=1 -16.58; w:line=240 auto -14.00. The spacer as emitted contributes 3.16 pt of the 13.8 pt asked, so the table rises 10.6 pt and every row under it. NOTE THE SIGN: the spacer is too SHORT, not too tall as the untested entry guessed - removing it made the table 3.2 pt worse, not better.
  recorded: 2026-11-12 21:54

- CONFIRMED - Charging the spacer gap in w:before with w:line=1 (hairline) puts the table's top where the page drew it
  evidence: Same document, one line changed in the spacer: w:before=276 w:line=1 -> first-row dy -13.59 -> -2.78 (page base offset is -2.7 to -3.8), 18_median_dy FAIL -> pass, 51/59 -> 53/59. w:before is honoured exactly and face-independent; w:line is a multiple of the PARAGRAPH MARK's line height (sz=2 -> 1 pt), which is why 276 twips bought 3.16 pt. Confirmed on ONE document - the 20-document measurement did not run, so the class outcome is untested. Patch: tools/p2w-bench/patches/table-spacer-before-not-line.patch (one append() in DocxWriter around line 4157).
  recorded: 2026-11-12 21:54

- CONFIRMED - Charging the table spacer in w:before with w:line=1 fixes the class's table documents
  evidence: Patch applied and measured on Google's render for 2 documents before the slot ran out: 362_price_list_dense 51/59 -> 53/59 and 20_within_10pt now passes (18_median_dy FAIL->pass), electricity-bill 45/59 -> 45/59 unchanged (its 20_within_10pt render is still 23 of 100, 19_worst_dy 198.6 - a different cause). 0 of 2 regressed. The 20-document round was NOT run: only 2 documents reached Drive, so the class outcome is still uncomputed. Engine reverted, patch at patches/table-spacer-before-not-line.patch.
  recorded: 2026-11-12 22:52

- CONFIRMED - The spacer-before patch holds when re-measured through a Google PDF export
  evidence: Corrected rig (Drive Doc exported as PDF, not docx). 362_price_list_dense 51/59 -> 53/59, 20_within_10pt FAIL -> pass, 18_median_dy pass; 316_contract_with_schedules 54/59 -> 55/59 (20_within_10pt still fails, render 67/100); 27_two_column_left_short_txtpos 54/59 -> 54/59 (unchanged, 20_within_10pt still fails); control 413_tagged_pdf_actualtext 58/59 -> 58/59 (reproduces baseline exactly, no regression). 4 of the 20 documents ran; the class outcome is still uncomputed.
  recorded: 2026-11-13 00:00

- CONFIRMED - The spacer-before patch moves the class's table documents to pass
  evidence: 20 documents through Drive on engine 2a68de6-dc3d644, Google PDF export, verifier 59 checks: 20_within_10pt FAIL->pass on 362_price_list_dense (51/59->53/59) and balance-sheet-two-columns-of-figures (40/59->44/59, also 07_table_rows, 18_median_dy, 29_blank_where_ink_was now pass). 10 controls held their scores: 15_stamp_on_scanned_page 42, 19_hanging_indent_txtpos 53, 310_court_judgment 53, 317_rti_response 56, 45_coloured_callout_box 55, 54_two_column... 50, 413_tagged_pdf_actualtext 58; 331_pid_diagram 39->40, 371_experience_certificate 40->41, table-with-no-header-row 54->55. The mechanism holds: the table top lands where the page drew it.
  recorded: 2026-11-13 00:53

- RULED OUT - The spacer-before patch is safe to ship
  evidence: Same 20-document round, ratchet exit 1: 4 documents below their mark. NEWLY FAILING checks on documents whose score did not fall: 362_price_list_dense 44_header_footer, 316_contract_with_schedules 59_shape_anchor. Score fell: 40_devanagari_shaping_font 37->36 (30_ink_where_blank_was), newsletter-3col-header-footer 40->39 (14_filled_shapes). The target moved on only 2 of the 10 failing documents (20%, below the third that 'improved' needs). Engine reverted.
  recorded: 2026-11-13 00:53

- UNTESTED - The regressions are documents where the emitted spacerTw exceeds the gap the page actually drew, so charging it in w:before pushes the table and everything under it down past where the page drew them; clamp the spacer to the measured gap rather than the flow remainder
  evidence: The patch makes the spacer render at its full asked height (276 twips = 13.8 pt) where before it rendered 3.16 pt, so the table and all following flow move DOWN by ~10.6 pt. On 362 and balance-sheet that is the correction; on 40_devanagari, newsletter-3col, 316 and 362's header/footer the new position is worse, which is what an over-large spacer looks like. Untested: no clamp has been built.
  recorded: 2026-11-13 00:53

- RULED OUT - The 13 Nov regressions come from spacers whose scaled gap is zero being changed from w:line=0 to w:line=1
  evidence: Refined patch (engine 2a68de6-d2a3183): emit the shipped spacer shape when the scaled gap is 0, the w:before form only for a real gap. Re-measured the 5 affected documents through Drive, Google PDF export: every score identical to the unrefined build - 362_price_list_dense 53/59, 316_contract_with_schedules 55/59, 40_devanagari_shaping_font 36/59, newsletter-3col-header-footer 39/59, balance-sheet-two-columns-of-figures 44/59 - and the same four checks still newly failing (44_header_footer, 59_shape_anchor, 30_ink_where_blank_was, 14_filled_shapes). Those documents carry real gaps, not zero ones, so the regressions come from the spacer's height, not from its zero case.
  recorded: 2026-11-13 00:57

- CONFIRMED - A document can gain the class's check and lose another in the same render, so the patch must be judged per check and not per score: 362_price_list_dense rose 51->53 with 20_within_10pt passing while 44_header_footer began failing
  evidence: 362_price_list_dense on engine 2a68de6-dc3d644: 51/59 -> 53/59, 20_within_10pt FAIL->pass, and 44_header_footer newly failing. The score rose and the ratchet still rejected it. Any future spacer work on this class has to clear 44_header_footer and 59_shape_anchor as well as move 20_within_10pt.
  recorded: 2026-11-13 00:57

- RULED OUT - Clamping the spacer to the gap the page's own baseline arithmetic gives (smaller of flow-model gap and (t.top - lastBaseline) - prevLine) removes the over-large spacers
  evidence: Clamp + w:before emission, 5 documents through Drive on the patched engine, Google PDF export, 59 checks: 362_price_list_dense 51->53 (20_within_10pt and 18_median_dy now pass, but 44_header_footer newly fails), balance-sheet 40->44 (4 now pass, none newly fail), 40_devanagari 37->37 with NO newly failing check (the patch without the clamp had 37->36 via 30_ink_where_blank_was - the clamp fixed that one), newsletter-3col 40->39 (14_filled_shapes newly failing), 316 54->55 (59_shape_anchor newly failing). So the clamp removes 1 of the 4 regressions but not the other 3; the ratchet would still reject.
  recorded: 2026-11-13 01:49

- UNTESTED - The remaining regressions are not spacer height: 44_header_footer on 362, 59_shape_anchor on 316 and 14_filled_shapes on newsletter-3col are header/footer, shape-anchor and filled-shape checks, so the extra 10.6 pt the spacer now occupies moves a page's flow across a band those checks measure rather than placing the table wrongly
  evidence: Clamp variant measured 13 Nov 01:45 run: 362 53/59 with 44_header_footer newly failing; 316 55/59 with 59_shape_anchor newly failing; newsletter-3col 39/59 with 14_filled_shapes newly failing; 40_devanagari fully restored by the clamp (37/59, no newly failing). Untested: nobody has measured whether those three documents' page-flow crosses a band, e.g. by dumping the page count and the y of the flow after the table.
  recorded: 2026-11-13 01:49

- CONFIRMED - The class's mass is not the table spacer: 187 of 208 documents fail 20_within_10pt, 70 of them with worst_dy over 100 pt and 56 with a page count that differs from the source, so the ~10.6 pt table-top correction can only ever reach the near-miss tail
  evidence: RESULTS.jsonl, engine 2a68de6, 208 rows: 187 fail 20_within_10pt; render value buckets <50:133, 50-69:30, 70-79:2, 80-89:14, >=90:8; 70 rows have 19_worst_dy>100; 56 rows have 01_page_count render != source. Near-miss set (within_10pt>=80 and worst_dy<60) is only 16 rows. The spacer patch's own 20-document round moved 2 of 10 failing documents.
  recorded: 2026-11-13 04:43

- CONFIRMED - The 86 worst documents that keep the source's page count and score under 50% on 20_within_10pt are dominated by the 47_margins element at x=0, not by line pitch: 83 of the 86 also fail 47_margins and 84 fail 18_median_dy with a large negative constant offset
  evidence: RESULTS.jsonl, engine 2a68de6: of 131 failing rows whose page count matches the source, 86 score <50 on 20_within_10pt; among those 86 the co-failing checks are 20_within_10pt 86, 18_median_dy 84, 47_margins 83, 19_worst_dy 80, 29_blank_where_ink_was 66, 22_reading_order 65. Median dy on the examples is a constant shift, not a drift: 304_package_insert_small_print -44.8, 23_timetable_grid_txtpos -30.6, 303_discharge_summary -19.4; 47_margins render x0 is 0 against source x0 28/56 on 23 and 303.
  recorded: 2026-11-13 04:43

- RULED OUT - Suppressing whitespace-only anchored text boxes in the emitter removes the x=0 element, so 47_margins stops reporting it and the class's 86 worst documents recover their left extent
  evidence: Local conversion of the two documents the entry cites, engine 2a68de6: 362_price_list_dense.docx has 0 wp:anchor, 0 wps:txbx and 0 whitespace-only runs (its 7 empty spacer paragraphs carry no runs at all); 316_contract_with_schedules.docx has 1 anchor, which is a shape with no text box, and 0 whitespace-only runs. Code: DocxWriter.flowParagraph:3081 returns on whitespace-only text and runXml emits a run only for non-empty text, so the emitter has no whitespace text box to suppress and the patch would be a no-op. The x=0 block Google reports is not a whitespace text box we emit.
  recorded: 2026-11-13 05:44

- UNTESTED - The class's mass is a per-line drift, not a step: Google renders w:line as a multiple of the substitute face's line height, so the flowed pitch asked in twips comes back short and the error accumulates down the page; the fix is to scale w:line by the face size in the flow emitter
  evidence: 304_package_insert_small_print, engine 2a68de6: 17 flowed paragraphs, no table and no anchor; sectPr margins all 0 and first paragraph w:before=296 twips=14.8 pt against the PDF's first line top 16.4 pt, so the top of the page is placed correctly. Recorded: 18_median_dy -44.8, 19_worst_dy +90.8, 20_within_10pt 12/100, 23_line_pitch 5.0 against source 7.8. Dominant run size 6.2 pt with w:line=143 twips (7.15 pt asked); calibrate.py's model (line/240)*1.15*size predicts 4.25 pt for that pair, measured 5.0 - direction right, constant not. Untested: no per-line dy dump through Drive and no scaled-w:line build has been measured.
  recorded: 2026-11-13 05:44

- CONFIRMED - Google renders w:line as a multiple of the substitute face's line height, so the flowed pitch asked in twips comes back short and the error accumulates down the page; emitting the advance as a hairline box (w:line=1) plus w:before = advance - 0.069*size reproduces the page's own pitch face-independently
  evidence: Patched engine 2a68de6-d80a524, 20 documents through Drive, Google PDF export, 59 checks. 304_package_insert_small_print 51->58, 20_within_10pt 12->100, 18_median_dy -44.8 -> pass, 23_line_pitch 5.0 -> pass; emitted w:before=147 twips (7.35 pt) + 0.069*6.2 = 7.78 pt against the PDF's 7.8 pt pitch. 34_monospace_document 53->56, 334_patent_document 47->53, 321_auditors_report 54->57. 3 of the 10 failing documents now PASS the target check outright and 4 of 10 moved the right way.
  recorded: 2026-11-13 06:56

- RULED OUT - The hairline-plus-before flow emitter is safe to ship as it stands
  evidence: Same 20-document round, engine 2a68de6-d80a524: ratchet.py FAIL - 6 documents below their best. 317_rti_response 56/59 same score but 41_block_spacing newly failing; 35_four_typefaces_one_page 54->53; 49_coloured_background_block_paragraph 55->54 (14_filled_shapes); 57_centred_title_page_left_body_pages 48/59 same score but 27_text_off_page and 44_header_footer newly failing; academic-paper-ieee-2col-abstract 46->41 (01_page_count, 07_table_rows, 23_line_pitch, 24_page_breaks); table-with-no-header-row 54->53 with 20_within_10pt newly failing. Reverted with git checkout -- app/src; patch kept at patches/hairline-flow-before.patch.
  recorded: 2026-11-13 06:56

- UNTESTED - The hairline box changes the page budget the fitter sees: it takes a line's height out of w:line and puts it in w:before, but fitPage still works to linePt*20, so a page near its bottom or a band boundary breaks a line early or late - which is exactly the shape of the six regressions (academic-paper gained 01_page_count and 24_page_breaks, 57_centred gained 44_header_footer, 317 gained 41_block_spacing). Feed fitPage and spacingTw the hairline advance, not the model box
  evidence: Engine 2a68de6-d80a524, 20 documents: every document that LOST a check lost one that depends on where the flow lands on the page (page count, page breaks, header/footer band, block spacing), while every document that GAINED passed the checks that depend only on pitch (18_median_dy, 19_worst_dy, 20_within_10pt, 23_line_pitch). 304 gained 7 and lost 0. Untested: no build has fed the hairline advance to fitPage.
  recorded: 2026-11-13 06:56

- RULED OUT - The page-boundary regressions are the fitter being charged the model's 0.2*prevBox + 0.8*box split instead of the paragraph's own advance, so the hairline spends more paper per line than the fitter budgeted; charging advance = linePt + before and b.y on a page's first line removes them
  evidence: Refined build 2a68de6-d5215cb, same 20 documents through Drive: ratchet.py still FAIL - 7 regressions. 311_fir_police_form 47->45 (01_page_count, 24_page_breaks, 55_orientation_mix), academic-paper 46->42 (01_page_count, 07_table_rows, 24_page_breaks, 41_block_spacing), table-with-no-header-row 54->53, 35_four 54->52 (19_worst_dy), 49_coloured 55->54, 317_rti 56/59 with 41_block_spacing newly failing, 57_centred 48->49 but 27_text_off_page newly failing. The pitch win is unchanged (304 58/59, 34_monospace 56/59, 334_patent 53/59, 321 57/59), so the page-boundary damage is not the budget arithmetic.
  recorded: 2026-11-13 07:00

- UNTESTED - The hairline box moves the glyph band inside the line: with w:line=1 the baseline sits 0.069*size below the box top instead of 0.8*box, so a line whose text the page drew in a header or footer band now renders on the wrong side of that band - which is why 44_header_footer, 27_text_off_page and 41_block_spacing are the checks that move while every pitch check passes. Compare a per-line dy dump of a regressing document against the source before touching the fitter again
  evidence: Two builds, 40 document-renders, identical shape: every check that only depends on pitch (18_median_dy, 19_worst_dy, 20_within_10pt, 23_line_pitch) improves or holds, and every check that depends on which band the flow lands in (44_header_footer, 27_text_off_page, 41_block_spacing, 01_page_count, 24_page_breaks) is what regresses. Untested: no per-line dy dump has been taken on a regressing document.
  recorded: 2026-11-13 07:00

- RULED OUT - Restoring the model's baseline with a split hairline box (w:before = 0.8*box - 0.069*size, w:after = 0.2*prev) keeps both the pitch and the baseline position
  evidence: Three-variant calibration through Drive (Google PDF export), 10 pt Arial, box 12 pt, advance 12 pt, 8 single-line paragraphs, zero margins: A hairline (before=226tw, line=1) first baseline 11.86 pt, pitch 11.99; B control model box (before=0, line=240) first baseline 9.38, pitch 11.50; C split (before=178tw, after=48tw, line=1) first baseline 9.46, pitch 9.59. C's pitch equals before+0.069*size exactly, so Google adds NO w:after between adjacent exact-line paragraphs: the after is ignored and the advance collapses. The split cannot place a baseline independently of the pitch.
  recorded: 2026-11-13 07:43

- CONFIRMED - The hairline construct places every flowed baseline at the full advance below its paragraph top, which is 0.2*prevLinePt lower than the model's 0.8*box placement - a uniform downward offset of the whole flow, which is why the pitch checks gained and only the band checks (44_header_footer, 27_text_off_page, 41_block_spacing, 01_page_count, 24_page_breaks) regressed
  evidence: Same calibration, engine-independent: A first baseline 11.86 pt against B 9.38 at box 12 pt / face 10 pt - a measured +2.48 pt at the top of the flow, close to the predicted 0.2*12 + 0.8*(12-11.5) = 2.8 pt (0.3 pt residual). Pitch is unchanged (A 11.99 vs B 11.50), so the offset is uniform and does not accumulate; it moves the flow across the bands those checks measure, which is the shape of every regression the 06:56 and 07:00 runs recorded.
  recorded: 2026-11-13 07:43

- UNTESTED - The repair is a per-flow-run up-shift, not a spacing change: since w:after is ignored and every PDF line is its own paragraph, subtract 0.2*prevLinePt from the FIRST hairline paragraph of each contiguous flow run and leave every following line at advance - the pitch is untouched because each line's top is the previous line's baseline, so the whole run moves up by the same 2.48 pt
  evidence: Calibration A/B/C above: the offset is uniform per run and identical for every line, so one shift at the run's first line moves all of them; C proves the same result cannot be reached by putting the difference in w:after. Untested: no build has applied the shift at a run start.
  recorded: 2026-11-13 07:43

- RULED OUT - The refined hairline (advance = linePt + beforeTw, the fitter's own charge, not the 0.2/0.8 model split) is a NEW engine state that had never been measured on twenty documents
  evidence: 13 Nov 08:40 fixer: applied patches/hairline-flow-before-refined.patch, built, converted and measured 7 docs through Drive. The content-hash engine id came out 2a68de6-d5215cb, which ALREADY holds 20 rows in RESULTS.jsonl: this exact patch was measured by an earlier run and reverted. Store, 20 docs: 16 target-failing at baseline, 6 moved (304 51->58, 334 47->53, 321 54->57, 34 53->56, 373 43->47, 406 46->48) = 37.5%, and 5 documents fell below baseline (311 47->45, 35 54->52, 49 55->54, academic-paper 46->42, table-with-no-header 54->53). Check the store for the diff-hash engine id BEFORE building: a saved patch may already have its twenty rows.
  recorded: 2026-11-13 08:45


## 32_stroke_lines

- UNTESTED - The strokes are lost in Google's import of our DrawingML shapes, not omitted by the engine: 05_round_company_seal's docx carries 140 w:drawing elements, but Google's export of it has zero stroked paths while the source PDF has 7 (header rule, footer hairline, 5 seal strokes).
  evidence: docx grep: 140 w:drawing in document.xml. Source drawings: 7 stroked paths (w=1.0 header rule, w=0.5 footer hairline, 5 seal strokes w=0.5-1.6). Store: 05 source=7 render=0; 16_right_aligned source=17 render=0; 01_stamp source=16 render=9. Next test: one DrawingML line in a minimal docx through Drive, then read the exported PDF's drawings.
  recorded: 2026-11-13 09:56

- UNTESTED - Google Docs drops the stroke from our DrawingML shapes: the docx carries 3 shapes with a real a:ln (w=20320/10160/6350, solidFill 0D268C) and 67 a:ln/a:noFill rects, and Google's export of that same docx has zero stroked paths. Horizontal rules should be emitted as w:pBdr, which Google renders.
  evidence: 05_round_company_seal docx: a:ln w=20320/10160/6350 each carrying solidFill 0D268C; 67 prstGeom rect with a:ln/a:noFill. Google export: 0 stroked paths. Source: 7 (header rule 1.0pt, footer hairline 0.5pt, 5 seal strokes). Untested: whether Google keeps a stroke on a minimal w:drawing line, and whether w:pBdr survives - calibrate both before changing the emitter.
  recorded: 2026-11-13 09:56


## 47_margins

- CONFIRMED - The 47_margins failure is one element pinned to the page's left edge, not a page shift: the rightmost extent and the top extent are already correct, so a uniform offset is ruled out by the data itself
  evidence: 208 recorded rows, 186 report render x0=0. Delta medians over the 189 failing rows: x0 -43 (71 of them at -60), y0 -1 (178 of 189 within 10 pt), x1 +3, y1 -6. A real left shift of ~56 pt would move x1 by the same -56; it does not, so exactly one element sits at x=0 while the rest of the page is placed correctly.
  recorded: 2026-11-13 02:54

- CONFIRMED - The element at x=0 comes from the table or the drawing path, not the body-flow path: body paragraphs are placed exactly, so the left offset a table carries (w:tblInd) or a shape carries (wp:posOffset) is what Google loses
  evidence: Control, measured on all 208 converted docx against the recorded rows: the 12 documents with no w:tbl and no w:drawing reproduce the source's left edge exactly - 310 57/57, 412 56/56, 413 56/56, 416 56/56, 417 56/56, 410 56/56, 392 28/28, 304 14/14, 78 62/62. By contrast 0 of the 192 documents containing at least one table or one drawing passes 47_margins (tbl=0/draw=0: 5 pass, 7 fail; every other cell of the table 0 pass). Body-flow placement is therefore exact and the defect is confined to the table and drawing emitters.
  recorded: 2026-11-13 02:54

- UNTESTED - Google does not honour w:tblInd the way LibreOffice does, so a table's left offset must be carried by something Google renders: pgMar left is 0 in every docx the engine emits, so a table whose tblInd is ignored starts at the page edge
  evidence: 362_price_list_dense emits w:tblInd=600 (30 pt) and the source's page-1 x0 is 30; LibreOffice renders the same docx at x0=30.1, exactly right, while Google reports x0=0. No patch was built and nothing was measured on Google this run, so the fix is untested - the correlation above is markup plus the LibreOffice render, not a Google measurement.
  recorded: 2026-11-13 02:54

- RULED OUT - Google drops w:tblInd when w:tblStyle is emitted after it in w:tblPr (CT_TblPrBase is a sequence, so an out-of-order child is discarded)
  evidence: Patch moved w:tblStyle to the first child of w:tblPr in the emitter at DocxWriter:4202, rebuilt, converted 362 and 316, Google PDF export: 362 51/59 and 316 55/59 with 47_margins still render x0=0 - byte-for-byte the baseline checks. Then a purpose-built 5-variant probe docx (one page, pgMar 0, one 4000-twip table each) through Drive: V1 tblInd=600 alone text x=30.0; V2 tblStyle FIRST + tblInd=600 text x=30.0; V5 no tblInd x=0.0. Element order changes nothing; Google honours tblInd either way.
  recorded: 2026-11-13 03:48

- RULED OUT - Google does not honour w:tblInd the way LibreOffice does, so a table whose tblInd is ignored starts at the page edge
  evidence: Same 5-variant probe through Drive, Google PDF export: V1 tblInd=600 -> text x=30.0 (exactly 600 twips = 30 pt); V5 same table with no tblInd -> x=0.0. Google honours it. V3 floating w:tblpPr tblpX=600 -> x=36.0 (also honoured, but placed out of flow at the page top); V4 tblInd=0 + cell paragraph w:ind left=600 -> x=30.0.
  recorded: 2026-11-13 03:48

- CONFIRMED - The x=0 element 47_margins reports is a whitespace-only span anchored at x=0; the table and drawing paths place their content correctly, so the check is reading invisible text as ink
  evidence: 362_price_list_dense Google PDF: every table span starts at x=30.0, identical to the source's 30.0, and the frame/right edge is within 2 pt; the only spans at x=0 are two single spaces at y 52.9 and 302.6. 316_contract_with_schedules: table frame drawings at 78.0..519.0 vs source 77.6..517.6, and again the only x=0 spans are three single spaces (y 472.7, 560.7, 633.1). 413 and 310 have no such span and pass 47_margins. So on these two documents the class is a space-only paragraph emitted with positionH=0, not a lost table indent.
  recorded: 2026-11-13 03:48


## 53_embedded_faces

- RULED OUT - Naming the metric-compatible family Google renders (Liberation Serif/Mono -> Times New Roman/Courier New, DejaVu Serif -> Times New Roman, DejaVu Sans -> Verdana) in w:rFonts makes Google keep the face
  evidence: 10 docs through Drive, 20 Nov: 53_embedded_faces passed on only 2 (313_power_of_attorney, 317_rti_response); kept=0 of 1-8 source faces on the other 8, incl 34_monospace_document (Courier New emitted, source=1 kept=0) and 35_four_typefaces (source=8 kept=0). Google still does not report the named family back. Score fell on 317 (56->55) and 3 docs gained new failures (18_median_dy, 19_worst_dy, 20_within_10pt, 41_block_spacing).
  recorded: 2026-11-12 19:52

- CONFIRMED - Check 53's family() normaliser only stripped hyphenated style suffixes, so the corpus's space-form names ('Liberation Sans Bold') never collapsed to a family and never reached SAME_FACE: kept=0 was structurally guaranteed whatever the engine wrote.
  evidence: 20 docs, 13 Nov: 53 passes on 16 of 20 (was 0 of 20). 01_stamp: src=5 kept=0 before, src=2 kept=1 after, same Google export, only the normaliser changed. Google export of 01_stamp carries ArialMT/Calibri; source carries 'Liberation Sans Bold/Regular' and 'Liberation Serif Regular/Italic/Bold'. The 12 Nov mapping theory was ruled out by this blind instrument, not by its own result.
  recorded: 2026-11-13 09:54


## PIPELINE - the attempt ledger cannot record any of the eight problem classes

- MEASURED - `classify.py --attempt` refuses every name in benchmarks/DEFECT-CLASSES.md,
  because `current_class_names()` builds its keys from verify_google check ids
  (`04_words_missing (+1)`, `20_within_10pt`) and not from the eight derived problem names.
  evidence: 16 Nov 2026 fixer. `classify.py --attempt "content-missing-partly-replaced"
  --outcome reverted` -> "refused: ... is not a class". ATTEMPTS.json's own
  `content-missing-partly-replaced` key was written before this guard existed and can no
  longer be appended to. Consequence: a fixer that follows the brief's instruction to record
  its attempt against a problem class cannot record it at all, and the 19 attempts the brief
  cites are all against retired check ids. The ledger is the fixer's only memory of what it
  already ruled out; until the key is the problem name, that memory cannot grow.
  ACTION: key the ledger off DEFECT-CLASSES.md's `problem` column. Until then an attempt is
  recorded in this file and in TRACE.md, which is what this run did.


## PIPELINE - the measurement is slow because scipy is missing, and that is why slots vanish

- MEASURED - A fresh pod has no scipy, so `p2w.edt()` takes its ladder fallback
  (radius-by-radius dilation, up to 400 iterations per page) instead of
  `scipy.ndimage.distance_transform_edt`.
  evidence: 16 Nov 2026 fixer. Same engine, same three single-page documents
  (415_inline_images, 07_stamp_over_table, 601_fillable_admission_form):
  without scipy the run exceeded the 290 s sandbox call limit twice and returned
  nothing; after `pip install scipy` the identical three measured in 28 s.
  Two nine-page realworld forms still exceeded 290 s after the install, so soffice
  on a 4088-run form is a second, separate cost - but the ladder is the one that
  silently converts "measure a sample" into "measure nothing".
  ACTION FOR THE NEXT RUN, before any attempt: `pip install scipy` (one line, ~20 s),
  then measure. `p2w.validate()` installs scipy itself; any measurement path that
  does not go through validate() must do the same or it measures at ladder speed.
  This is a cost defect, not a fidelity defect: it changes no score, only whether a
  run gets to produce one.


## content-missing-nothing-in-its-place

- CONFIRMED - CONFIRMED: a row separator the page draws heavier than the table's other separators - two coincident rules on one y, 0.45pt grey 0x9B9B9B and 0.9pt black 0x111111 - is dropped, because w:tblBorders holds ONE weight for every insideH and insideStroke's dominant-length tie goes to whichever was inserted first (the grey); the black rule is then drawn nowhere and its ink is absent. FIX: per-row w:tcBorders top.
  evidence: 16 Nov fixer, soffice render, p2w.measure_doc, 30 class docs + 12 controls. mobile-bill 18.48->1.55, salary-slip-factory-wages 18.09->0.73, two-tables-stacked 17.20->0.77, marksheet-university 16.78->0.64, electricity-bill 16.24->1.33, insurance-policy-schedule 13.29->0.53, landscape-page-inside-portrait 13.08->1.45, form16-part-b 12.32->0.77, mutual-fund-statement 12.05->0.21, property-tax-receipt 10.78->0.96, admit-card 10.68->1.89, gst-invoice-multipage 10.44->0.40, delivery-challan 10.26->0.84, table-across-page-break 9.41->0.53. 22 of 30 moved; 0 of 12 controls worse (eway-bill 0.91->0.05). Patch: PdfToWord.Table.rowRule, markSideStrokes.heaviestRuleOn, DocxWriter emits w:tcBorders top for a row whose inkWeight exceeds 1.5x the insideH stroke's.
  recorded: 2026-11-16 12:24


## content-missing-nothing-in-its-place - 16 Nov 10:50 run: the inline image is SKIPPED by name, and the line is now known

- MEASURED (untested as a fix) - The 89.04 %@5 on `415_inline_images` is not an extraction
  failure to be chased in the image path: the content-stream walker throws the operator away
  before anything else sees it.
  evidence: 16 Nov 2026 fixer, corpus-v1 downloaded (211 PDFs).
  `415_inline_images.pdf` page 1: `get_images()` = 0, and its content stream is 381 bytes
  carrying 2 `BI ... ID ... EI` sequences -
  `BI /W 8 /H 8 /CS /G /BPC 8 /F /AHx ID 00FF00FF... EI`. `PdfToWord.java:2715`:
  `if (tok.equals("BI")) { i = skipInlineImage(cs, i); ops.clear(); continue; }`, and
  `skipInlineImage` is at `PdfToWord.java:2906`. So the four bars are dropped by design and
  the text below them moves up into the freed space - which is why the page reads as
  content-LOSS with text_recall still high.
  WHY IT WAS NEVER FIXED: the fix is a decoder, not a correction - parse W/H/CS/BPC/F, build
  the raster, place it at the current CTM, and emit it as the Picture block the XObject path
  already writes. That is a feature with a measured surface, not a one-line guard, and it
  should be taken by a run that has the whole slot for it.
  NEXT: start at `skipInlineImage` (2715/2906). The page's own text says what the bars are
  ("It has no object number and lives inside the content stream."), and the corpus document
  is a one-page, 381-byte reproducer, so a fix can be measured in seconds.


## content-missing-partly-replaced

- UNTESTED - The 9->10 page spill on 041122 is not a text-box height: page 7's .docx carries ZERO w:txbxContent and is one w:tbl of 24 rows, and the page's whole flow is that table, so the fit guard's residue shave (shaveToFit) finds no depth-0 w:before to give up and writes the page 12 twips over its target.
  evidence: 16 Nov 12:46 fixer, subagent A committed FINDINGS/content-missing-partly-replaced-A-1305.md: row height DocxWriter.java:6086 = max(rowHeightTw, paraContentTw+ruleTwHere), written :6123 as w:trHeight hRule=atLeast + w:cantSplit; shaveToFit :495-560 only shaves w:before at depth==0; page 7 writtenTw 16756 vs target 16744 (over=12, left=12). Four repairs measured to fail: shave trHeight (16746, still 10 pages), -Dp2w.fitreserve=700 (10 pages), remove w:cantSplit (page 7 fills to y 838.7, still 10 pages), drop the page-number row (10 pages). NOT verified by me. I measured at HEAD: 041122 share5 98.65, pages 10/9, worst_page 9, text_recall 99.68.
  recorded: 2026-11-16 13:51

- CONFIRMED - The 20-line wrap is renderer-correct for the width we give it, so the defect is our emitted width/indent and not a renderer limit.
  evidence: subagent B, FINDINGS/content-missing-partly-replaced-B-1300.md, three hand-built docx variants rendered with soffice 7.4.7.2: V1 box 58 pt at x 513.9 -> 4 lines (ink 514.0-569.0); V2 box 11 pt at x 573.1 -> 25 lines (ink 573.2-584.2), and the engine's own wrap=none wrapped identically, so wrap=none is no guard in LibreOffice; V3 box 58 pt at x 573.1 (our emitted anchor) -> 4 lines, identical to V1 to the tenth of a point. Anchor x has zero effect on wrapping; width alone decides. Measured side-note: the '11 pt box' is an ink width - a 1 pt-font second copy of the heading inside a 22.8 pt margin cell, not a text box.
  recorded: 2026-11-16 13:51

- RULED OUT - the cell line box carries the wrong pitch (11.6 pt vs the 240 tw it writes)
  evidence: source p7 baselines 579.61/591.61/603.61/615.61 = 12.00 pt exactly; the 4630 tw row is 16 lines at 240 + 562 tw of gaps = 4642 written, 0.6 pt
  recorded: 2026-11-17 14:34

- RULED OUT - an embedded font part makes the reader use the page's own face
  evidence: embedded Effra .odttf + fontTable/embedRegular + settings/embedTrueTypeFonts rendered identically to no embedding: 12 pages, NotoSans, same geometry
  recorded: 2026-11-17 14:34

- CONFIRMED - carrying the page's advance widths in a face the reader has (Arial + w:w) stops the re-wrap
  evidence: 041122 12 -> 11 pages: p6 folio stays on p6, p7 table fits at 795.2 pt against the source's 800.4; block line counts fall; the remaining spurious page is the p7 folio, which is a table cell not a flow line
  recorded: 2026-11-17 14:34


## content-missing-partly-replaced - 16 Nov 09:54 run: the CONFIRMED patch re-measured, and the spill is now a number

- MEASURED - The confirmed `run-size-from-sizePt-not-Tf` patch reproduces to the digit on a
  fresh pod, and the page spill it was blocked on is real, counted, not inferred.
  evidence: 16 Nov 2026 fixer, engine `ead0d0e-d027ee6` (clean + patches/run-size-from-sizePt-not-Tf.patch),
  scipy 1.18.1 present, instrument p2w.render/measure_doc at DPI 150:
  `041122-Account_Opening_Form` share@5 94.92, worst_page 9, text_recall 99.5 %,
  **pages_src 9, pages_ours 10**, problem content-missing-partly-replaced.
  The previous run's worst page was 94.92 after the patch - identical. So the patch is
  deterministic and the measurement is now cheap enough to run: the form converted in 20.1 s
  and the whole document measured in 116 s, inside one 290 s call, once scipy was installed.
  The 290 s limit was the scipy ladder, not soffice. That corrects the 09:12 note, which put
  the second cost on soffice.
  NOT KEPT again, for the same honest reason and one more: the class does not pass, the full
  213-document ratchet still has not run, and pages_ours 10 against pages_src 9 means page 9
  of the source is still compared against page 10 of ours. The spill is the next fix, and it
  is now measurable in one call: make the source's page 7 stop overflowing and pages 7-9 stop
  shifting, and this document should fall to the 18 %@5 its pages 1-6 already read.
  Do not re-derive the size bug and do not re-derive the spill - both are numbers now.


## content-missing-partly-replaced - 16 Nov 10:50 run: the band-by-centre theory is RULED OUT, and the narrow placement is a text box

- RULED OUT - A line the page drew ACROSS a ruled grid is placed in the band containing its
  CENTRE, so a centred heading block lands in whichever narrow band the grid's middle happens
  to be and is wrapped into it; assigning the band by greatest overlap should stop the wrap,
  shrink the row and stop the spill.
  evidence: 16 Nov 2026 fixer, engine (clean + patches/run-size-from-sizePt-not-Tf.patch) plus
  patches/ruled-band-by-overlap-not-centre.patch, scipy 1.18.1 present, p2w.render/measure_doc
  at DPI 150: `041122-Account_Opening_Form` share@5 94.92, worst_page 9, pages_src 9,
  pages_ours 10, text_recall 99.5 - IDENTICAL TO THE DIGIT to the unpatched run, per page too
  (p1 48.22, p2 52.49, p3 10.57, p4 20.39, p5 15.5, p6 1.61, p7 73.99, p8 89.59, p9 94.92).
  The rule fires on no line of page 7: the heading lines are not wider than the band they land
  in ('Annexure-1' is 23 pt of text inside a 58 pt band), so the overlap branch is never taken.
  MEASURED, and it relocates the cause: the .docx carries 378 `wps:txbx` text boxes, and the
  heading exists TWICE - once at x 513.9-571.5 (58 pt wide) and once at x 573.1-584.0 (11 pt
  wide). The 20-line wrap is inside a text box whose width was taken from a table column, not
  inside a ruled table cell, so the ruled pass is the wrong place to look. Patch kept at
  patches/ruled-band-by-overlap-not-centre.patch and REVERTED - it moves nothing and would
  have cost a corpus ratchet to prove it.
  NEXT: the spill's height is the text box, so look at the box's width in DocxWriter's anchor
  path (where a box's extent comes from its block's own line boxes) before the table's rows.


## content-missing-partly-replaced — the nine-page account-opening form class

- CONFIRMED - Every Run in a text box carried the raw `Tf` operand as its point size, not the
  size the glyph was drawn at, so a PDF that puts its scale in the TEXT MATRIX renders at 1 pt
  evidence: 16 Nov 2026 fixer, engine (clean) + patches/run-size-from-sizePt-not-Tf.patch.
  `041122-Account_Opening_Form` p1 content stream: `/TT0 1 Tf` with `6 0 0 6 71.3 493.7 Tm`,
  so PDFBox reports getFontSize()=1.000 and getFontSizeInPt()=6.000 (probe, 25 glyphs, page 1).
  The .docx carried 4088 runs ALL at `w:sz w:val="2"` (1 pt) - `halfPointsDown` floors
  sizePt*2 with a minimum of 2 - and the LibreOffice render was boxes with no words.
  Cause: `runsOf()` and the paragraph/ring paths built `new Run(..., first.size, ...)` from
  `Glyph.size` = getFontSize() (raw Tf), never `Glyph.sizePt` = getFontSizeInPt(). On every
  document where Tf carries the size the two are equal, which is why 211 synthetic documents
  never showed it; a form PDF is exactly the shape that separates them.
  Measured on the class's two real documents (soffice render, benchmarks/p2w.py position()):
  `041122` pages 1-6 mean share@5 82.1 -> 18.3 (p1 40.0->9.4, p3 92.9->10.6, p4 87.1->20.4,
  p5 97.0->15.5, p6 96.8->1.6); worst-page 98.65 -> 94.92. `Account_Opening_Form_Fillable_filled`
  worst-page 97.62 -> 90.31, mean over 9 pages 72.5. No page of `041122` got worse.
  NOT KEPT: the class does not pass and the full 213-document ratchet was not run in this slot,
  so the engine is reverted and the patch is saved at
  patches/run-size-from-sizePt-not-Tf.patch. NEXT WORK, in order:
  (1) run the ratchet on the patch across the corpus - it touches every run in every text box;
  (2) THE REMAINING BLOCKER IS A PAGE SPILL, and it is now the class's real cause. With the
  text at its true 6 pt, `041122` still emits 10 pages against the source's 9 and the fillable
  form 11: source page 7 overflows, everything after it shifts one page, and pages 7-9 read
  74-95 %@5 purely because page i is compared against page i. Fix the spill and the same
  documents should fall from ~90 %@5 to the pages 1-6 range. Do not re-derive the size bug.

- CONFIRMED - The per-cell paragraph matrix (`pieces`) was indexed in the UNTRIMMED column
  space after the empty-column trim, so the multi-line cell path read another column's lines.
  evidence: 17 Nov 2026 fixer. `PdfToWord.buildTables` (~:8686) remaps cells/faces/firstX/
  firstY/colours through `keep` and left `pieces` alone, while the consumer at :8800 reads
  `pieces.get(rr).get(cc)` with `cc` in the trimmed space. 041122 p7 grid is 24x4 with
  keep=[1,2,3]: the heading is original column 2 = trimmed cell 1, but pieces.get(1).get(1) is
  original column 1 (empty), so parasOfLines returned 0, the cell fell back to the welded
  string, and the SIX paragraphs were written into the empty cell to their right - which is
  why the heading appeared twice on that page. Fixed by trimming `pieces` with everything
  else. Predicts every table that drops a column.

- CONFIRMED - The point size is `scalingFactorY` of PDFBox's TextPosition text matrix, and it
  is a SIZE, not a multiplier on the Tf operand. evidence: 17 Nov 2026, probe over three
  documents: 041122 fontSize=1.000 scaleY=10.000 inPt=10.000; 48_form 12/12/12;
  01_stamp fontSize=8.500 scaleY=8.500 inPt=8.000. Multiplying the two squared every ordinary
  page and regressed 192 of 213 documents (12 x 12 = 144 pt) - that wrong version was measured
  and thrown away, not reasoned about. Taking scaleY itself keeps the 8.5 that inPt rounds to
  8, and is 13.0 on text rotated 90 degrees. Full 213-document ratchet WITH the fix:
  208 unchanged, 2 improved (411_nested_xobject_transforms 31.05 -> 0.00;
  041122 98.65 -> 97.62, median displacement 477.6 -> 138.24 pt), 1 regression
  (39_small_caps_letter_spacing 0.72 -> 3.78) and one nil change (05_round_company_seal
  0.19 -> 0.20). This supersedes the reverted patches/run-size-from-sizePt-not-Tf.patch,
  which used the ROUNDED inPt.

- CONFIRMED - `parasOfLines` records each line's own x, `addRecutRow` (:8380) turns it into
  `indentPt`, and the pieces path added the paragraphs WITHOUT it, so indentPt stayed NaN and
  the writer applied one inset - the cell's first-line x - to every paragraph in the cell.
  evidence: 17 Nov 2026. 041122 p7 row 1 wrote all six heading lines at `w:ind 9452`
  (472.6 pt) inside a 10636-dxa cell: 59 pt of usable width, so "Income-tax Rules, 1962"
  (drawn at x 253.7) wrapped inside a 59 pt column. After the fix the six carry
  9452/4255/4705/3830/107/2079 and the row renders at its declared height.

- CONFIRMED (measured, engine change still owed) - the 041122 page spill is a WRAP, not a
  paragraph property, and the wrap is caused by the reference renderer substituting a
  different font. evidence: 17 Nov fixer. Rendered bottom rules of table 17's 24 rows
  against their declared `w:trHeight`, in twips/20: r1 23.2/23.15, r2 93.1/84.1 (+9.0),
  r3-r15 17.3-17.6 each = declared, r16 40.9/40.95, r17 17.3/17.3, r18 17.3/17.25,
  r19 37.6/29.15 (+8.5), r20 61.7/41.0 (+20.7), r21 41.0/41.0, r22 40.8/40.8,
  r23 340.4/231.5 (+108.9) -> spills to our page 9, r24 41.6/41.35. THE ROWS THAT GROW GROW
  BY WHOLE LINES: r23 carries 20 source lines and rendered 26, and its own `w:before` values
  are 0-4 pt each (sum 24.1 pt) with `w:line` exact 240 tw = 12 pt - the source's own pitch.
  So neither `w:before`, nor `w:line exact`, nor `w:cantSplit` is what grows it; the extra
  lines are the growth. The cause of the extra lines: the .docx names Effra (the source's
  font, correctly), the renderer has no Effra, and substitutes Noto Sans - 'Verification'
  at 10 pt measures 52.40 pt in the source's Effra-Bold and 61.24 pt in the substitute
  (+16.9 %). The cell leaves the source's longest line 2.9 pt of slack (line ends x 568.8,
  cell edge 571.9 = 0.5 %), so every full-width line wraps its tail. Ruled out by
  measurement: the sizePt bug and the `pieces` index (both fixed; r1's six heading lines
  carry 9452/4255/4705/3830/107/2079 and render at declared height), `w:before` (24 pt, not
  109), `w:line` (12 pt = source pitch), `w:cantSplit` (only moves an already-taller row).
  Also measured: our page 7 is NOT table 17 - it holds page 6's page furniture (the C7EAFB
  heading bar, the footer rule at y 738.2 and the page number at y -7.5) whose anchor
  paragraphs were pushed off page 6; table 17 starts on our page 8.

- CONFIRMED (environment, and it changes what this class's numbers mean) - installing a
  metric clone of the source's own embedded font takes 041122's table from spill to nearly
  exact. evidence: 17 Nov fixer. Built Effra-Regular/Bold from Liberation Sans with the
  advances read out of the PDF's own `/Widths` arrays (FirstChar 32, w/1000 em; space 0.181
  em against Liberation's 0.278), installed to ~/.fonts, re-rendered into an empty dir:
  r2 93.1 -> 84.1 (= declared), r23 340.4 -> 256.4, page 2 of the table no longer starts a
  new page. Ruled out: kerning (stripping GPOS/kern changed nothing), font *shape* (only the
  advances matter for line breaking). NOT yet enough on its own - still 12 pages, because
  the residual is the engine's own line box: r23's 19-20 paragraphs are emitted at
  `w:line` 240 tw (12.0 pt) while the row the engine itself declares is 4630 tw (231.5 pt)
  for 20 lines at the source's 11.6 pt pitch - the engine's row height and the engine's
  line height disagree by 0.4 pt a line, so a 20-line row overflows by ~8 pt + `w:before`
  before any font is involved. NEXT: make the cell-line box carry the source's measured
  pitch in twips (232, not 240) and re-measure r23 against 231.5.


- CONFIRMED and FIXED (17 Nov 14:39 fixer, DocxWriter.table) - A PAGE'S OWN FOLIO IS NOT A
  ROW OF THE TABLE THE PAGE'S RULES BOUND. 041122 page 7 draws a rule above its folio and a
  frame round the sheet, so the ruled pass hands the folio back as the table's LAST ROW
  (row 23 of 24, cells 363/10636/456 tw, trHeight 827 tw, only text "7"); the page's content
  already ends at y=800.4 of 842, so the row cannot fit, the renderer breaks the sheet and
  the folio costs a whole page (ours 11 against the source's 9). The writer now detects a
  trailing row that is nothing but a folio whose baseline is in the page's bottom band
  (>0.88 page height), leaves it out of the table's height and emits it as an anchored line
  at its own x/y - the treatment the FLOW path already gives a folio. Measured: 041122 11
  pages -> 10, doc share5 97.62 -> 86.25, worst page 7 -> 9. No-regression proof: all 213
  documents re-converted with the patched engine, compared entry by entry inside the .docx -
  212 are byte-identical in every zip entry, so their renders and scores cannot have moved;
  only 041122 differs. Ruled out by measurement: that the table's rows are individually too
  tall (the content rows land on the page's own edges), and that the folio is outside the
  table (it IS a real drawn cell - the fix is about where it is drawn, not whether it is a
  cell).

- OPEN (measured, NOT fixed) - THE INSTRUCTION PAGE'S LAST 17 LINES. After the folio fix,
  our p8 (the instruction page) stops at y=683.6 with 158 pt of the sheet unused, and the
  tail of the table (17 lines, ending at the source's own folio "8") goes to p9. Mechanism,
  measured by rewriting only the .docx and re-rendering: `<w:cantSplit/>` is written on
  EVERY row, and it is a promise the engine cannot keep - a row that does not fit the space
  left on its page takes the whole row to the next sheet instead of breaking where the page
  broke it. With cantSplit stripped from the same .docx (86 occurrences) the page takes 166
  lines instead of 154 and the spill falls from 17 lines to 5: so cantSplit is 12 of the 17
  and the remaining 5 are row height. NOT FIXED because the blast radius is 26 of 213
  documents (every document with a table row written taller than 60 pt - 55_sidebar_box,
  61_two_col_abstract_spanning, 64_newspaper, product-catalogue-code-left-price-right, ...)
  and 26 full position measurements is hours of instrument time in one slot; a change that
  cannot be measured must not be kept. NEXT: a NARROW rule - write cantSplit only when the
  row's own top edge plus its written height still lands inside the page
  (rowTopPagePt + rowHeightTw/pt <= pageHeight), which is the promise cantSplit actually
  makes and which can only fire on rows that provably overflow. Count how many documents it
  fires on before measuring them.

- RULED OUT, THIS RUN (measured) - THE NARROW cantSplit RULE DOES NOT CLOSE 041122, AND NO
  HEIGHT-BASED VERSION OF IT CAN. The rule was built exactly as specified - w:cantSplit
  written only when the row's own top edge plus its height lands inside the page - and
  applied twice. First as specified, on the DECLARED w:trHeight: it fired on 1 of 213
  documents (itr-computation-with-slab-table, 68.12 -> 68.12) and NOT on 041122, because
  every one of 041122's 86 rows fits an 842 pt sheet by its declared height. Then on the
  height the renderer actually lays out - max(declared, the w:before + w:line actually
  emitted in the row's cells), which is the only height hRule="atLeast" cannot exceed: it
  fired on 4 of 213 and still does not close the page. All four measured, no movement:
  041122 10/10 pages identical line for line, Account_Opening_Form_Fillable_filled 10/10
  identical, itr-computation 68.12 -> 68.12, 64_newspaper 9.11 -> 9.11.
  THE MEASURED REASON, and it is the whole point: the breaking row is the one carrying
  "Government Department establishing identity and address of such person". Its top edge is
  689.0, it declares 2220 tw (111 pt) and it emits 2558 tw (128 pt) of line boxes, so
  689 + 128 = 817 pt reads as fitting on an 842 pt sheet. It renders ~170 pt (p9's text runs
  y 9.8 -> 163.8) because the RENDERER WRAPS its cell text into ~15 lines where the writer
  emitted 11. The under-charge is in the WRAP, not in the height arithmetic, so any rule
  keyed on a height the writer can compute will call this row safe. Confirmed on the
  document, not inferred: with cantSplit dropped from that one row the render is unchanged,
  because the rule keeps it (817 <= 842) - the row that DOES lose cantSplit is a 66 pt row at
  top 805, which changes nothing visible.
  CONSEQUENCE FOR THE NEXT RUN: stop working the cantSplit angle. The last extra page is a
  cell whose text wraps into more lines than the writer charged, and that is the same
  under-charge as the class it sits in (content-missing-partly-replaced). Charge the cell
  its real line count and the row's height becomes truthful, at which point a cantSplit rule
  keyed on it fires by itself and the page closes.

- KEPT, THIS RUN (measured neutral on all 213) - cantSplit IS NOW WRITTEN ONLY WHERE IT CAN
  BE KEPT. DocxWriter.table() emits the row's cells first, takes
  laidOutTw = max(rowHeightTw, flowTwOf(row)), and writes w:cantSplit only when
  rowTopPagePt + laidOutTw <= pageHeight. 209 of 213 .docx are byte-identical in every zip
  entry; the 4 that differ are the 4 measured above, and none of them moves a number. It is
  kept because it removes a promise the engine cannot keep wherever that is provable, and it
  costs nothing measurable - but it is NOT the fix for 041122 and must not be counted as one.

  IT IS CARRIED AS A PATCH, NOT IN THE ENGINE, and that is a commit-path fact, not a
  judgement: `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` is 458 KB, git push
  is 403 for everyone, and the only working commit path is the GitHub MCP tool
  GITHUB_COMMIT_MULTIPLE_FILES, which takes file contents inline - a 458 KB file is not a
  payload any run can send. The change is 38 lines and lives at
  `patches/cantsplit-only-where-keepable.patch`; it was verified to apply cleanly to this
  tree (`git apply --check`), built, converted over the whole corpus and measured before
  being set aside. Apply with `git apply patches/cantsplit-only-where-keepable.patch` from
  the repository root and rebuild, exactly as patches/README.md says. Because it moves no
  number, not shipping it costs the project nothing; because the next step below needs it
  (a row charged its true height only closes the page if a cantSplit rule is there to drop
  it), a run that takes that step should apply the patch first.

- MEASURED, THIS RUN - WHERE THE UNDER-CHARGE ACTUALLY IS, IN NUMBERS. The breaking row of
  041122 (docx row 76, the one carrying "Government Department establishing identity and
  address of such person") is ONE cell, 11000 tw (550 pt) wide, holding NINE paragraphs at
  w:line="240" (12 pt) and w:sz="20" (10 pt), 828 characters in total. The writer charges it
  9 x 240 = 2160 tw plus the rule, which is the 2220 tw (111 pt) it declares. The render
  spends ~13 lines on that text (p9's text runs y 9.8 -> 163.8 in twelve baselines, 154 pt
  at 12 pt), i.e. ~156 pt. SO THE ROW IS NOT UNDER-MEASURED BY ARITHMETIC - IT IS
  UNDER-MEASURED BY WRAPPING: the writer emitted one paragraph per source line, and four of
  those paragraphs WRAP INTO TWO LINES in the render, because the source face fits 828
  characters into 550 pt and our DejaVu does not. Nine paragraphs, thirteen lines.
  THE FIX THIS POINTS AT: charge each paragraph the number of lines it will wrap into, using
  the width OUR font gives its text against the cell's own width (ceil(textWidth / cellWidth)),
  instead of assuming one line per source line. That is a real measurement the writer can
  make - it already measures text widths for column widening - and it would put this row at
  ~156 pt, after which top 689 + 156 = 845 > 842 and the cantSplit rule carried in
  patches/cantsplit-only-where-keepable.patch fires by itself and the page closes. It also
  explains, in one mechanism, why this document has resisted eleven attempts: every attempt
  keyed on a height the writer already computes agrees with the writer.

- RULED OUT, THIS RUN (measured, and it made things WORSE) - DROPPING cantSplit ON A
  WRAP-AWARE HEIGHT. The wrap estimate above was built for real: a Helvetica advance-width
  helper (PDType1Font.HELVETICA / HELVETICA_BOLD, the standard-14 metrics PDFBox already
  ships, within a few per cent of the DejaVu Sans these documents are set in), each cell's
  text split on its own paragraph breaks, lines = ceil(textWidth / (spanTw - insetTw)), the
  row charged lines x rowLineTw, and the cantSplit rule keyed on the larger of that, the
  declared height and the emitted line boxes. It compiles and it runs. On 041122 it takes
  the document from 10 pages to ELEVEN: p7 falls from 91 lines to 90, a one-line p8 appears
  (maxy 35.3), and the instruction page is untouched at 683.6 with the same 17 lines spilling
  to p10. So a row that the earlier rule kept whole now breaks, and the break itself costs a
  page. THAT IS THE FINDING, and it redirects the fix: cantSplit is NOT the lever. With
  hRule="atLeast" a split row leaves a fragment the renderer charges again, so removing the
  promise can cost more than it saves. The page has to be closed by charging the row its real
  height in w:trHeight - so the renderer lays the row out at 156 pt and breaks it ITSELF at
  the foot of the sheet - not by removing cantSplit and hoping it breaks well. The engine was
  reverted to HEAD after this measurement; nothing from this experiment is in the tree.

- RULED OUT, THIS RUN (measured) - CHARGING THE ROW ITS WRAPPED HEIGHT CASCADES. Built the
  same way as the previous entry (Helvetica standard-14 advances, per paragraph
  ceil(textWidth / (spanTw - insetTw)), the row charged max(declared, wrapped) x rowLineTw)
  but written into w:trHeight itself - hRule is "atLeast", so the floor is what the renderer
  will not go below - and cantSplit left alone. It works on the row it was aimed at: the
  instruction page's content now runs to 711.5 instead of 683.6, so the breaking row really
  did grow. The document is still ELEVEN pages, and the reason is the cascade: p7 falls from
  91 lines to 90 and a one-line p8 appears, because rows that used to fit the page are now
  charged more and one of them crosses. Charging every under-charged row at once is not a
  one-row fix - it re-lays out every table in the document and the page count is decided by
  the whole sequence, not by the row that overflows. WHAT THAT MEANS FOR THE NEXT RUN: the
  wrap charge is the right mechanism (it is the only one that explains 111 pt charged against
  156 pt laid out), but it cannot be landed blind on one document. Do the corpus diff FIRST -
  re-convert all 213 and count how many .docx change - because this change touches every
  ruled table, not four of them, and the ratchet has to be paid for over the whole corpus in
  a slot that can afford it. The engine was reverted to HEAD after this measurement.

- CLOSED, THIS RUN (measured over the whole corpus) - THE WRAP CHARGE IS 42 OF 213 AND IT
  REGRESSES. Built exactly as the two entries above specify (Helvetica standard-14 advances,
  per paragraph ceil(textWidth / (spanTw - insetTw)), row = max(declared, lines x rowLineTw)
  in w:trHeight atLeast, charged before the page budget so writtenRowsTw sees it), converted
  all 213 documents with it and with the engine at 76f01b2, and diffed word/document.xml entry
  by entry: 42 of 213 differ (20 %), ~400 rows, and ZERO docx page-break changes. So the blast
  radius is slot-sized, not ratchet-sized - the earlier note's fear was wrong about the size.
  What it is wrong about is the direction: measured both ways, price-list-right-aligned-amounts
  goes 1.79 -> 81.15 and 1 -> 2 pages, price-list-2col-dense-right-aligned 2.69 -> 81.69 and
  1 -> 2 pages, 01_stamp_rotated_15deg_upright 0.0 -> 9.3, 03_stamp_vertical_90deg 16.98 ->
  23.19. It reads a right-aligned amount in a narrow column as two lines and doubles 38 of 38
  rows of a table whose page pitch was already right. 041122 is unchanged at 11 pages in the
  first build and could not be rendered inside a 280 s call after the inset correction.
  WHAT THE NEXT RUN NEEDS: the charge has to be gated on the width the RENDERER gets (the
  emitted w:tcW less the inset actually written), not on the page's inset, or it fires on text
  that fits. And the 041122 gap is a PARAGRAPH count (9 line boxes charged, 13 drawn), not a
  width, so the two must not be conflated in one number. Patch kept at
  patches/wrap-charge-helvetica.patch; engine at HEAD. Full numbers:
  FINDINGS/wrap-charge-corpus-diff.md.
