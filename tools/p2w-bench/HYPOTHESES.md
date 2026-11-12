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

