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


## 53_embedded_faces

- RULED OUT - Naming the metric-compatible family Google renders (Liberation Serif/Mono -> Times New Roman/Courier New, DejaVu Serif -> Times New Roman, DejaVu Sans -> Verdana) in w:rFonts makes Google keep the face
  evidence: 10 docs through Drive, 20 Nov: 53_embedded_faces passed on only 2 (313_power_of_attorney, 317_rti_response); kept=0 of 1-8 source faces on the other 8, incl 34_monospace_document (Courier New emitted, source=1 kept=0) and 35_four_typefaces (source=8 kept=0). Google still does not report the named family back. Score fell on 317 (56->55) and 3 docs gained new failures (18_median_dy, 19_worst_dy, 20_within_10pt, 41_block_spacing).
  recorded: 2026-11-12 19:52

