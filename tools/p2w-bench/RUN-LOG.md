| 13 Nov 00:53 | fixer | round 1: applied the confirmed table-spacer patch (w:before carries the gap, w:line=1), 20 documents through Drive on 2a68de6-dc3d644: 20_within_10pt FAIL->pass on 362_price_list_dense (51->53) and balance-sheet-two-columns (40->44), 10 controls held; ratchet exit 1 with 4 regressions (362 44_header_footer, 316 59_shape_anchor newly failing; 40_devanagari 37->36, newsletter-3col 40->39), 3 of 18 moved; engine reverted |
| 13 Nov 00:57 | fixer | round 1, second attempt on the same class: refined the spacer patch so a zero scaled gap keeps the shipped shape, engine 2a68de6-d2a3183; 5 affected documents through Drive scored identically to the unrefined build (362 53, 316 55, 40_devanagari 36, newsletter-3col 39, balance-sheet 44) with the same 4 newly failing checks - zero-gap theory ruled out; engine reverted, 30 bench Docs deleted |
| 13 Nov 01:45 | fixer | slot claimed - fixer running |
| 13 Nov 02:18 | fixer | round 1, third attempt on 20_within_10pt (+4): applied the confirmed table-spacer patch AND the untested clamp (spacerTw capped by the page's own baseline arithmetic, (t.top - lastBaseline) - prevLine, when smaller than the flow-model gap), engine 2a68de6-df33807; 5 documents through Drive with Google PDF export: 362_price_list_dense 51->53 (20_within_10pt, 18_median_dy now pass, 44_header_footer newly fails), balance-sheet 40->44 (4 now pass, none newly fail), 40_devanagari 37->37 with NO newly failing check - the clamp removed that regression the unclamped patch had at 36, newsletter-3col 40->39 (14_filled_shapes newly failing), 316 54->55 (59_shape_anchor newly failing). Regressions fell 4->3 but the ratchet would still reject, so engine reverted, attempt recorded reverted (0 of 5 moved engine-relative). Clamp theory RULED OUT; new UNTESTED theory: the remaining three are band-crossing checks, not spacer height. 5 Google Docs deleted. |
| 13 Nov 02:50 | fixer | slot claimed - fixer running |
| 13 Nov 02:50 | fixer | round 1, 47_margins (new class, 0 attempts): diagnosed from the 208 recorded rows, no engine change. 47_margins is ONE element at the page's left edge, not a page shift - 186 rows report render x0=0 while x1 is +3 and y0 is within 10 pt on 178 of 189, and a real 56 pt shift would have moved x1 too. Converted all 208 documents and correlated against the recorded rows: the 12 documents with no table and no drawing reproduce the source's left edge exactly (57/57, 56/56, 28/28, 14/14, 62/62), while 0 of the 192 documents holding a table or a drawing pass. Body-flow placement is exact, so the defect is in the table or drawing emitter. 362_price_list_dense emits w:tblInd=600 (30 pt, equal to the source x0 of 30) and LibreOffice renders it at 30.1 - correct - while Google reports 0, so Google is not honouring tblInd with pgMar left=0. Two confirmed hypotheses and one untested fix written; no patch built and nothing measured on Google, so the attempt is recorded 'error' and the class stays OPEN. Slot released at 03:27, 37 minutes after the claim. |
| 13 Nov 03:44 | fixer | slot claimed - fixer running |
| 13 Nov 04:40 | fixer | slot claimed - fixer running |
| 13 Nov 05:41 | fixer | slot claimed - fixer running |
| 13 Nov 06:47 | fixer | slot claimed - fixer running |
| 13 Nov 06:57 | fixer | slot claimed - fixer running |
| 13 Nov 07:40 | fixer | slot claimed - fixer running |
| 13 Nov 08:40 | fixer | slot claimed - fixer running |
| 13 Nov 09:45 | fixer | slot claimed - fixer running |
| 13 Nov 11:05 | baseline | started | phase measure |
| 13 Nov 11:06 | baseline | slot claimed - baseline running |
| 13 Nov 11:08 | baseline | measured 600_reviewed_invoice_with_annotations 43/59 docx, 4/5 txt |
| 13 Nov 11:09 | baseline | measured 601_fillable_admission_form 44/59 docx, 4/5 txt |
| 13 Nov 11:10 | baseline | measured 602_bookmarked_annual_report 53/59 docx, 4/5 txt |
| 13 Nov 11:11 | baseline | released slot, advanced measure -> classify |
| 13 Nov 11:24 | classifier | slot claimed - classifier running |
| 16 Nov 06:07 | baseline | slot claimed - baseline running |
| 16 Nov 07:46 | classifier | slot claimed - classifier running |
| 16 Nov 07:48 | fixer | slot claimed - fixer running |
| 16 Nov 08:53 | fixer | slot claimed - fixer running |
| 16 Nov 03:42 | fixer | attempt content-missing-partly-replaced -> error (0/? moved) |
| 16 Nov 09:12 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 16 Nov 09:54 | fixer | slot claimed - fixer running |
| 16 Nov 10:00 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 16 Nov 10:50 | fixer | slot claimed - fixer running |
| 16 Nov 05:39 | fixer | attempt content-missing-partly-replaced -> error |
| 16 Nov 05:40 | fixer | attempt content-missing-nothing-in-its-place -> error |
| 16 Nov 05:41 | fixer | attempt content-missing-partly-replaced -> error |
| 16 Nov 11:11 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 16 Nov 11:53 | fixer | slot claimed - fixer running |
| 16 Nov 06:54 | fixer | attempt content-missing-nothing-in-its-place -> kept (22/30 moved) |
| 16 Nov 12:30 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 16 Nov 12:46 | fixer | slot claimed - fixer running |
| 16 Nov 08:21 | fixer | attempt content-missing-partly-replaced -> error |
| 16 Nov 08:22 | fixer | attempt content-missing-nothing-in-its-place -> kept (31/212 moved) |
| 16 Nov 14:55 | fixer | slot claimed - fixer running |
| 16 Nov 15:48 | fixer | attempt content-missing-partly-replaced -> kept (1/30 moved) |
| 16 Nov 16:18 | fixer | attempt content-missing-nothing-in-its-place -> kept (31/212 moved) |
| 16 Nov 17:23 | fixer | slot claimed - fixer running |
| 16 Nov 18:10 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 17 Nov 09:21 | fixer | slot claimed - fixer running |
| 17 Nov 11:16 | fixer | attempt content-missing-partly-replaced -> partial (1/13 moved) |
| 17 Nov 12:04 | fixer | slot claimed - fixer running |
| 17 Nov 12:30 | fixer | attempt content-missing-partly-replaced -> reverted (0/16 moved) |
| 17 Nov 12:51 | fixer | slot claimed - fixer running |
| 17 Nov 13:13 | fixer | attempt content-missing-partly-replaced -> error |
| 17 Nov 14:34 | fixer | attempt content-missing-partly-replaced -> partial (2/16 moved) |
| 17 Nov 14:39 | fixer | slot claimed - fixer running |
| 17 Nov 15:36 | fixer | attempt content-missing-partly-replaced -> partial (1/30 moved) |
| 17 Nov 16:35 | fixer | slot claimed - fixer running |
| 17 Nov 17:34 | fixer | attempt content-missing-partly-replaced -> reverted (0/213 moved) |
| 17 Nov 17:46 | fixer | slot claimed - fixer running |
| 17 Nov 18:22 | fixer | attempt content-missing-partly-replaced -> reverted (0/16 moved) |
| 17 Nov 18:34 | fixer | attempt content-missing-partly-replaced -> reverted (0/16 moved) |
| 17 Nov 18:45 | fixer | attempt content-missing-partly-replaced -> reverted (0/16 moved) |
| 17 Nov 18:45 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 17 Nov 18:56 | fixer | slot claimed - fixer running |
| 17 Nov 19:31 | fixer | attempt content-missing-partly-replaced -> partial (1/3 moved) |
| 17 Nov 19:35 | fixer | attempt content-missing-partly-replaced -> kept (3/3 moved) |
| 17 Nov 23:02 | baseline | slot claimed - baseline running |
| 17 Nov 23:43 | classifier | slot claimed - classifier running |
| 18 Nov 09:54 | fixer | slot claimed - fixer running |
| 18 Nov 11:55 | fixer | attempt content-missing-nothing-in-its-place -> reverted (0/30 moved) |
| 18 Nov 12:58 | fixer | slot claimed - fixer running |
| 18 Nov 13:44 | fixer | attempt single-element-far-out -> partial (1/1 moved) |
| 18 Nov 14:50 | fixer | slot claimed - fixer running |
| 18 Nov 14:51 | fixer | attempt content-partly-lost-and-displaced -> partial (1/7 moved) |
| 18 Nov 15:28 | fixer | attempt content-partly-lost-and-displaced -> kept (1/210 moved) |
| 18 Nov 15:58 | fixer | slot claimed - fixer running |
| 18 Nov 16:11 | fixer | attempt content-partly-lost-and-displaced -> reverted (0/7 moved) |
| 18 Nov 16:23 | fixer | attempt content-partly-lost-and-displaced -> reverted (0/7 moved) |
| 18 Nov 16:52 | fixer | slot claimed - fixer running |
| 18 Nov 17:00 | fixer | attempt content-missing-partly-replaced -> reverted (0/16 moved) |
| 18 Nov 18:00 | fixer | slot claimed - fixer running |
| 18 Nov 19:07 | fixer | attempt content-missing-nothing-in-its-place -> kept (22/29 moved) |
| 19 Nov 16:11 | fixer | slot claimed - fixer running |
| 19 Nov 16:58 | fixer | attempt content-partly-lost -> partial (5/10 moved) |
| 19 Nov 18:00 | fixer | slot claimed - fixer running |
| 19 Nov 18:40 | fixer | attempt content-present-partly-displaced -> reverted (0/18 moved) |
| 19 Nov 18:53 | fixer | slot claimed - fixer running |
| 19 Nov 21:59 | fixer | slot claimed - fixer running |
| 19 Nov 22:30 | fixer | attempt content-present-partly-displaced -> kept (13/18 moved) |
| 19 Nov 22:32 | fixer | attempt content-present-partly-displaced -> kept (13/18 moved) |
| 19 Nov 22:59 | fixer | attempt content-present-partly-displaced -> reverted (0/24 moved) |
| 19 Nov 23:00 | fixer | attempt content-present-partly-displaced -> kept (13/18 moved) |
| 19 Nov 23:53 | fixer | slot claimed - fixer running |
| 19 Nov 23:56 | fixer | attempt content-present-partly-displaced -> error (0/18 moved) |
| 20 Nov 00:24 | fixer | attempt content-present-partly-displaced -> kept (2/18 moved) |
| 20 Nov 01:21 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 01:52 | fixer | slot claimed - fixer running |
| 20 Nov 02:25 | fixer | attempt content-present-partly-displaced -> kept (1/23 moved) |
| 20 Nov 03:40 | fixer | attempt content-present-partly-displaced -> kept (1/23 moved) |
| 20 Nov 03:42 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 03:53 | fixer | slot claimed - fixer running |
| 20 Nov 04:03 | fixer | attempt content-present-partly-displaced -> error (0/23 moved) |
| 20 Nov 04:14 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 04:59 | fixer | slot claimed - fixer running |
| 20 Nov 05:11 | fixer | attempt content-present-partly-displaced -> partial (2/23 moved) |
| 20 Nov 05:17 | fixer | attempt content-present-partly-displaced -> reverted (0/23 moved) |
| 20 Nov 05:51 | fixer | slot claimed - fixer running |
| 20 Nov 05:53 | fixer | attempt content-present-partly-displaced -> reverted (0/23 moved) |
| 20 Nov 06:20 | fixer | attempt content-present-partly-displaced -> reverted (0/23 moved) |
| 20 Nov 06:21 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 06:53 | fixer | slot claimed - fixer running |
| 20 Nov 07:13 | fixer | attempt content-partly-lost-and-displaced -> partial (1/6 moved) |
| 20 Nov 07:59 | fixer | attempt content-partly-lost-and-displaced -> kept (1/6 moved) |
| 20 Nov 08:00 | fixer | attempt content-partly-lost-and-displaced -> kept (1/6 moved) |
| 20 Nov 08:52 | fixer | slot claimed - fixer running |
| 20 Nov 09:22 | fixer | attempt content-present-partly-displaced -> reverted (0/23 moved) |
| 20 Nov 09:24 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 09:25 | fixer | slot re-claimed by a status check, then released again - the claim was accidental, no work was done under it |
| 20 Nov 09:58 | fixer | slot claimed - fixer running |
| 20 Nov 10:36 | fixer | attempt 18_displacement -> reverted (0/107 moved) |
| 20 Nov 10:38 | fixer | attempt 18_displacement -> reverted (0/107 moved) |
| 20 Nov 10:41 | fixer | attempt 18_displacement -> reverted (0/107 moved) |
| 20 Nov 10:43 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 10:51 | fixer | slot claimed - fixer running |
| 20 Nov 10:52 | fixer | attempt t13_amount_columns -> error |
| 20 Nov 11:51 | fixer | attempt t13_amount_columns -> kept (10/18 moved) |
| 20 Nov 11:59 | fixer | attempt t13_amount_columns -> kept (2/18 moved) |
| 20 Nov 12:03 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 12:52 | fixer | slot claimed - fixer running |
| 20 Nov 13:34 | fixer | attempt 47_margins -> partial (3/13 moved) |
| 20 Nov 13:34 | fixer | attempt 47_margins -> reverted (0/13 moved) |
| 20 Nov 13:37 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 13:54 | fixer | slot claimed - fixer running |
| 20 Nov 14:35 | fixer | attempt 47_margins -> reverted (0/26 moved) |
| 20 Nov 15:07 | fixer | attempt 47_margins -> reverted (0/26 moved) |
| 20 Nov 15:08 | fixer | attempt 47_margins -> partial (2/26 moved) |
| 20 Nov 15:55 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 15:55 | fixer | slot claimed - fixer running |
| 20 Nov 16:14 | fixer | attempt t13_amount_columns -> reverted (0/26 moved) |
| 20 Nov 17:06 | fixer | attempt t13_amount_columns -> kept (5/6 moved) |
| 20 Nov 17:08 | fixer | attempt t13_amount_columns -> reverted (0/1 moved) |
| 20 Nov 17:12 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 17:59 | fixer | slot claimed - fixer running |
| 20 Nov 18:00 | fixer | attempt t13_amount_columns -> reverted (0/6 moved) |
| 20 Nov 19:24 | fixer | attempt t13_amount_columns -> kept (1/? moved) |
| 20 Nov 19:27 | fixer | attempt t12_word_invention -> reverted (0/12 moved) |
| 20 Nov 19:29 | fixer | attempt t12_word_invention -> reverted (0/12 moved) |
| 20 Nov 19:33 | fixer | attempt t08_line_order -> reverted (0/10 moved) |
| 20 Nov 19:33 | fixer | attempt t08_line_order -> reverted (0/10 moved) |
| 20 Nov 20:01 | fixer | slot claimed - fixer running |
| 20 Nov 20:28 | fixer | attempt 47_margins -> reverted (0/14 moved) |
| 20 Nov 20:44 | fixer | attempt 47_margins -> reverted (0/14 moved) |
| 20 Nov 20:46 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 20:58 | fixer | slot claimed - fixer running |
| 20 Nov 20:59 | fixer | attempt t01_word_accuracy -> reverted (0/10 moved) |
| 20 Nov 21:22 | fixer | attempt t01_word_accuracy -> kept (3/10 moved) |
| 20 Nov 21:46 | fixer | attempt t01_word_accuracy -> reverted (0/10 moved) |
| 20 Nov 21:49 | fixer | attempt t01_word_accuracy -> kept (0/10 moved) |
| 20 Nov 21:57 | fixer | slot claimed - fixer running |
| 20 Nov 22:39 | fixer | attempt t01_word_accuracy -> reverted (2/7 moved) |
| 20 Nov 22:43 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 20 Nov 22:54 | fixer | slot claimed - fixer running |
| 20 Nov 23:16 | fixer | attempt t01_word_accuracy -> kept (2/7 moved) |
| 20 Nov 23:23 | fixer | attempt t01_word_accuracy -> reverted (0/5 moved) |
| 21 Nov 00:57 | fixer | slot claimed - fixer running |
| 21 Nov 00:57 | fixer | attempt t01_word_accuracy -> reverted (0/5 moved) |
| 21 Nov 01:41 | fixer | attempt t01_word_accuracy -> reverted (0/5 moved) |
| 21 Nov 01:47 | fixer | attempt t01_word_accuracy -> reverted (0/5 moved) |
| 21 Nov 01:51 | fixer | attempt t01_word_accuracy -> reverted (0/5 moved) |
| 21 Nov 01:51 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 21 Nov 02:52 | fixer | slot claimed - fixer running |
| 21 Nov 03:25 | fixer | attempt 47_margins -> partial (2/26 moved) |
| 21 Nov 03:36 | fixer | attempt 47_margins -> partial (2/26 moved) |
| 21 Nov 03:57 | fixer | slot claimed - fixer running |
| 21 Nov 04:34 | fixer | attempt t01_word_accuracy -> partial (1/? moved) |
| 21 Nov 04:34 | fixer | attempt t01_word_accuracy -> partial (1/5 moved) |
| 21 Nov 04:36 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 21 Nov 07:14 | fixer | slot claimed - fixer running |
| 21 Nov 07:16 | fixer | attempt 47_margins -> partial (0/26 moved) |
| 21 Nov 07:58 | fixer | slot claimed - fixer running |
| 21 Nov 10:39 | fixer | attempt t01_word_accuracy -> reverted (0/213 moved) |
| 21 Nov 10:45 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 21 Nov 11:18 | fixer | slot claimed - fixer running |
| 21 Nov 11:35 | fixer | attempt t02_position -> error |
| 21 Nov 11:36 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 21 Nov 12:12 | fixer | slot claimed - fixer running |
| 21 Nov 12:46 | fixer | attempt 32_stroke_lines -> error (0/37 moved) |
| 21 Nov 12:49 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 21 Nov 13:18 | fixer | slot claimed - fixer running |
| 21 Nov 13:30 | fixer | attempt t01_word_accuracy -> reverted (0/6 moved) |
| 21 Nov 11:52 | fixer | slot claimed - fixer running |
| 21 Nov 13:43 | fixer | attempt 47_margins -> error |
| 21 Nov 13:54 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 21 Nov 13:54 | fixer | slot claimed - fixer running |
| 21 Nov 14:42 | fixer | attempt t01_word_accuracy -> kept (1/5 moved) |
| 21 Nov 14:42 | fixer | attempt t01_word_accuracy -> kept (1/5 moved) |
| 21 Nov 14:49 | fixer | attempt t01_word_accuracy -> reverted (0/3 moved) |
| 21 Nov 14:51 | fixer | slot FORCED released - see INCIDENTS.md for why |
| 21 Nov 15:17 | fixer | slot claimed - fixer running |
| 21 Nov 15:48 | fixer | attempt 47_margins -> partial (1/213 moved) |
| 21 Nov 15:58 | fixer | slot claimed - fixer running |
| 21 Nov 17:25 | fixer | attempt 47_margins -> reverted (0/5 moved) |
