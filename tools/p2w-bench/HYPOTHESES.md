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

- UNTESTED - The ~10 pt table-top offset is the empty spacer paragraph emitted before the table (362 emits w:before=0 w:line=276 exact before the first w:tbl); Google renders it taller than the gap the flow already charged
  evidence: 362_price_list_dense document.xml: the subtitle paragraph is w:line=149 and the spacer before the table is w:line=276 (=13.8 pt asked); the PDF's gap between the subtitle baseline (y=47.1) and the table's first row (y=68.7) is 21.6 pt. Measured dy steps +9.8 pt exactly at the table's first row. Test: vary only the spacer's w:line and read the first row's dy.
  recorded: 2026-11-12 20:49


## 53_embedded_faces

- RULED OUT - Naming the metric-compatible family Google renders (Liberation Serif/Mono -> Times New Roman/Courier New, DejaVu Serif -> Times New Roman, DejaVu Sans -> Verdana) in w:rFonts makes Google keep the face
  evidence: 10 docs through Drive, 20 Nov: 53_embedded_faces passed on only 2 (313_power_of_attorney, 317_rti_response); kept=0 of 1-8 source faces on the other 8, incl 34_monospace_document (Courier New emitted, source=1 kept=0) and 35_four_typefaces (source=8 kept=0). Google still does not report the named family back. Score fell on 317 (56->55) and 3 docs gained new failures (18_median_dy, 19_worst_dy, 20_within_10pt, 41_block_spacing).
  recorded: 2026-11-12 19:52

