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

