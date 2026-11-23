# HANDOFF - read this before you pick a class

## PARKED - what was tried, and what would re-open it

A run tried these and could not get through. That is a record of one approach, not a
verdict on the problem: the next run may take any of them again with a genuinely
different idea. What is not worth repeating is the attempt listed below.

| # | what it is | what was tried | what would re-open it | when |
|---|---|---|---|---|
| 0 | the widget-AP walk is refused by one document, and the decision is not a fixer's | measured all three variants corpus-wide: 601 52.39 -> 0.00 and 42/42 d | a person must either authorise the trade (a 1.03 rise on a document al | 10:40 |

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 19:57 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> 00_page_count LANDED (0be925ff): the column-page shape merge is in. 21 documents change in document.xml, 361 124->40 paragraphs and 401 52->27, 301 untouched (pageBody already merged it), 350 untouched (not this mechanism). Corpus 212/212 on this tree, 0 documents worse, regress PASS, measure_gate READY. 0 documents move in the LibreOffice table BY CONSTRUCTION - it honours w:line=1 exact and Google does not - the 2 moved are Google moves from the 04:47 run (361 2pp->1 at 41/42, 375 2pp->1 at 35/42->37/42). 22 of 23 page-count-refused documents were scoring 0 of 42 and are now measurable. Instrument defects fixed this run: p2w --force read REPO's PdfToWord.class not ENGINE_SRC's (a patched tree skipped all 213 as fresh - cost 22 min); measure_gate expected 213 rows from the 212-row table gate.py publishes (EXEMPT.json read for blocked, ignored for expected); regress --stamp and the pre-commit hook deadlocked so no engine change could land at all; gverify --collect could not read artifacts[0].workspace_path so the Google cron collects nothing. STILL OPEN: gate.py cannot forward --force to p2w.py (workaround: p2w --force first, then gate.py).

## What the next run should do first

> 00_page_count: measure 041122-Account_Opening_Form in Google (2464 drawing-only paragraphs, nine pages, worst score in the corpus at 98.65) - the scale test for the carrier paragraph. Then 350_question_paper: FINDINGS/00_page_count-350-INLINE-PICTURE-CARRIES-THE-LINE-1120-agent.md charges picture() lines 2542-2564 (an unplaced picture emitted <wp:inline> in a paragraph with no w:pPr, inheriting sz=22 and w:after=120 from docDefaults, which spacingTw cannot see); the patch beside it is UNCOMPILED. Then w:tcBorders for 32_stroke_lines/05_chars_extra.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| contA-01 | content-missing-partly-replaced | A | which code path decides the height of a block emitted from a PDF text  | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-A-1305.md |
| contB-01 | content-missing-partly-replaced | B | is the wrap inside a text box a renderer limit or our emitted width | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-B-1300.md |
| contA2-01 | content-missing-partly-replaced | A2 | why does parasOfLines reject the six heading lines of 041122 page 7 | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-A2-092912-7c4e.md |
| contD-01 | content-missing-partly-replaced | D | how many corpus documents have a cell whose lines start left of the fi | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-D-092700-1d7b.md |
| contA-02 | content-missing-nothing-in-its-place | A | 415_inline_images p1: why is 89% of source ink >5px from ours when tex | 09:57 | expected by 11:15 | landed | FINDINGS/content-missing-nothing-in-its-place-A-044628-d0c0.md |
| contB-02 | content-missing-nothing-in-its-place | B | the ~1.4pt uniform shift on mobile-bill/salary-slip-factory-wages/elec | 09:57 | expected by 11:15 | landed | FINDINGS/content-missing-nothing-in-its-place-B-103610-346a.md |
| contA-03 | content-present-partly-displaced | A | 75_merged_header_cell_three_columns: the table body is 22 pt low and e | 18:16 | expected 19:05 | landed | tools/p2w-bench/FINDINGS/content-present-partly-displaced-mergedheader-130426-4bd9.md |
| contB-03 | content-present-partly-displaced | B | 13 of the 18 documents are within 1 pt everywhere except a few rows th | 18:16 | expected 19:05 | landed |  |
| contA-04 | content-present-partly-displaced | A | bank-statement-horizontal-rules-only: which code path decides row pitc | 22:31 | expected by 19:30 | landed | FINDINGS/content-present-partly-displaced-bankpitch-133100-d68d.md |
| contB-04 | content-present-partly-displaced | B | blast radius of w:vMerge across the 18 documents in the class | 22:31 | expected by 19:30 | landed | FINDINGS/content-present-partly-displaced-vmergescope-133908-a7c4.md |
| contA-05 | content-present-partly-displaced | A | can RuleCollector carry the PDF paint operator so a shading fill stops | 00:46 | 00:37 | landed | FINDINGS/content-present-partly-displaced-newspaper-033000-a7d1.md |
| contB-05 | content-present-partly-displaced | B | what does check 65_table_span_down assert and why does 75_merged_heade | 00:46 | 00:41 | landed | FINDINGS/content-present-partly-displaced-mergedheader-vmerge-192600-c3f1.md |
| contA-06 | content-present-partly-displaced | A | after rules become w:pBdr, which construct still emits the U+200B anch | 03:54 | expected by 05:00 | landed | FINDINGS/content-present-partly-displaced-zerowidth-040040-7c1e.md |
| contB-06 | content-present-partly-displaced | B | mobile-bill share5 43.87 and electricity-bill 46.85 with max_pt only 1 | 03:54 | expected by 05:00 | landed | FINDINGS/content-present-partly-displaced-subpx-041118-ed1d.md |
| contB-07 | content-partly-lost-and-displaced | B | why two corpus documents lose ~60% of their ink at 5px: absent or move | 07:59 | landed | landed | tools/p2w-bench/FINDINGS/content-partly-lost-and-displaced-twocol-tables-0700-f1x.md |
| contA-07 | content-partly-lost | A | is the justified-line spacing fix missing from the engine or already l | 07:59 | landed | landed | tools/p2w-bench/FINDINGS/content-partly-lost-JUSTIFY-already-landed-0700-f1x.md |
| contA-08 | content-present-partly-displaced | A | is the rule-as-drawing construct still in the engine and is the pBdr p | 08:58 | 09:00 | landed | FINDINGS/content-present-partly-displaced-rule-guard-was-not-the-blocker-100700-f1x.md |
| contB-08 | content-present-partly-displaced | B | how much of 18_displacement the rule construct can explain, and which  | 08:58 | 09:00 | landed | FINDINGS/content-present-partly-displaced-rule-guard-was-not-the-blocker-100700-f1x.md |
| 18_dA-01 | 18_displacement | A | Quantify the dy signature: across the Google renders that fail 18_disp | 09:59 | expected by 10:45 | landed | tools/p2w-bench/FINDINGS/18_displacement-dy-shape-101323-4fa7.md |
| 18_dB-01 | 18_displacement | B | Find the engine code path that decides each line's vertical position i | 09:59 | expected by 10:45 | landed | tools/p2w-bench/FINDINGS/18_displacement-engine-topoffset-101951-cda8.md |
| t13_A-01 | t13_amount_columns | A | which writer path emits the misaligned amounts, proven by build | 12:00 | 11:05 | landed | FINDINGS/t13-writer-path-110501-f3de.md |
| t13_B-01 | t13_amount_columns | B | census of the 18 documents: table path vs paragraph path | 12:00 | 11:06 | landed |  |
| 47_mA-01-01 | 47_margins | A-01 | what 47_margins actually compares, and where the page margin is emitte | 13:36 | 13:00 | landed | FINDINGS/47_margins-MECHANISM-133500-f2.md |
| 47_mB-01-01 | 47_margins | B-01 | the space-led indent construct on 47_margins | 13:36 | 13:00 | landed | FINDINGS/47_margins-MECHANISM-133500-f2.md |
| 47_mA-01 | 47_margins | A | which code path emits a table-cell line, and how a cell's horizontal p | 14:02 | landed | landed | tools/p2w-bench/FINDINGS/47_margins-CELLPATH-A-150000.md |
| 47_mB-01 | 47_margins | B | why 40_devanagari_shaping_font and 76_devanagari_table score 10.48 and | 14:02 | landed | landed | tools/p2w-bench/FINDINGS/47_margins-DIAGNOSE40-B-150000.md |
| t13_A-02 | t13_amount_columns | A | per-document map of every offending t13 line: source column x, leading | 17:09 | six remaining docs diagnosed line by line | landed | FINDINGS/t13-page-end-column-KEPT-172000.md |
| t13_B-02 | t13_amount_columns | B | reach of a per-page end column across the whole .txt corpus, before an | 17:09 | which of 213 improve and which regress | landed | FINDINGS/t13-page-end-column-KEPT-172000.md |
| t13column census-01 | t13 | column census | which of the six t13 documents still fail at head, the exact end colum | 18:01 | a per-document table with columns, path and a fixable/geometry verdict | landed | tools/p2w-bench/FINDINGS/t13-WELDED-CELL-CLOSED-1820.md |
| t13itr weld fix-01 | t13 | itr weld fix | implement and measure the TxtWriter change that clears itr-computation | 18:11 | a unified diff plus before and after scores for the six and for a wider set | landed | tools/p2w-bench/FINDINGS/t13-WELDED-CELL-CLOSED-1820.md |
| 47maanchor trace-01 | 47margins | anchor trace | which writer construct puts 360_restaurant_menu's body column 12 pt le | 20:07 | FINDINGS/47_margins-INDENT-SALE-AND-LEADER-MERGE-2030.md | landed | FINDINGS/47_margins-INDENT-SALE-AND-LEADER-MERGE-2030.md |
| 47maclass census-01 | 47margins | class census | which clause of 47_margins each document fails, grouped by mechanism,  | 20:33 | FINDINGS/47_margins-INDENT-SALE-AND-LEADER-MERGE-2030.md | landed | FINDINGS/47_margins-INDENT-SALE-AND-LEADER-MERGE-2030.md |
| t01_verifier-tokenisation-01 | t01_word_accuracy | verifier-tokenisation | Does verify_txt.py's t01 tokenisation charge a correct .txt for words  | 21:02 | a per-asymmetry verdict with measured before/after on synthetic cases, and a diff for any instrument bug | landed | Verdict ENGINE for the two bank forms (127 tokens of U+FFFD where the source declares U+0124); two real instrument bugs found (widget /AP double-count, source word boundaries) but neither makes any of the ten pass; 15 asymmetries tested and ruled harmless with numbers. Ruled the instrument out as the explanation for 79/391/406 - which the run then found was wrong: the NUL declaration WAS the instrument's fault. See FINDINGS/t01_word_accuracy-CONTROL-CHARS-2135.md |
| t01_writer-word-drop-01 | t01_word_accuracy | writer-word-drop | Which construct in TxtWriter.java/PdfToWord.java drops words the PDF d | 21:02 | a ranked table with file:line, the exact condition, measured evidence and the minimal fix | landed | No writer drop on either measurable document: 041122's 131 lost tokens are 127 ligature U+FFFD plus 4 genuine; the filled form's 145 are the same 127 plus 18 widget values counted twice by the source. Measured negatives that remove possibilities permanently: nested XObject with a scaling CTM LOST 0, Arabic through logicalOrder LOST 0 (length-preserving), below-paper LOST 0, letterspacing 0.16-0.30em identical both sides. Also: clipToPaper() is dead code and the live filter uses the CropBox ignoring its offset - a page whose CropBox origin is not (0,0) drops visible text (measured: VISIBLE -> V). |
| t01_ToUnicode CMap destination-01 | t01_word_accuracy | ToUnicode CMap destination | Is the U+FFFD the CMap's own answer or a parse failure, and what is th | 22:39 | the root cause with file:line and a patch proven on the two documents | landed | FINDINGS/t01_word_accuracy-FFFD-CMAP-2300-fixer.md |
| t01_adversarial patch review-01 | t01_word_accuracy | adversarial patch review | How can this Identity-H recovery write wrong text into the document? | 22:43 | a ranked list of regression risks with a one-line test each | landed | FINDINGS/fffd-cmap-destination-PATCH-REVIEW-2325.md |
| t01_A-01 | t01_word_accuracy | A | is the U+FFFD glyph a ligature or a single letter, read from the embed | 23:20 | 23:00 | landed | FINDINGS/ligature-identity-UNRECOVERABLE-2350.md |
| t01_B-01 | t01_word_accuracy | B | how many of the 213 documents a cmap-based recovery would reach, and d | 23:20 | 23:04 | landed | FINDINGS/ligature-identity-UNRECOVERABLE-2350.md |
| t01_A-02 | t01_word_accuracy | A | is the handed diagnosis (nested form matrix disagreement, rotated line | 01:41 | 01:15 | landed | FINDINGS/411-nested-xobject-matrix-1940.md |
| t01_B-02 | t01_word_accuracy | B | why does 39_small_caps_letter_spacing lose 8 words and invent 2 - writ | 01:41 | 01:20 | landed | FINDINGS/39-small-caps-gap-threshold-0150-fixer.md |
| t01_A-03 | t01_word_accuracy | A | census of every widget appearance stream over all 213 documents - how  | 04:36 | a blast radius small enough to measure in one run | landed | FINDINGS/widget-ap-glyph-walk-0436-f1x.md |
| t01_B-03 | t01_word_accuracy | B | implement the /AP /N glyph walk in its own clone and measure 601 and t | 04:36 | 601 from 37/42 to 42/42 docx checks, with the instrument's own answer for a tick | landed | FINDINGS/widget-ap-glyph-walk-0436-f1x.md |
| 32_sB-01 | 32_stroke_lines | B | why Google drops the rules LibreOffice draws, and which construct repl | 11:34 | landed | landed | tools/p2w-bench/FINDINGS/32_stroke_lines-google-drop-113048-9597.md |
| t02_A-01 | t02_position | A | is the two-line 47_margins/t02 claim a real two-format fix | 11:34 | landed | landed | tools/p2w-bench/FINDINGS/t02_position-two-line-claim-112617-0bfd.md |
| t01lostwords-01 | t01 | lostwords | which words each of the five documents loses, and why | 13:57 | the missing token list per document | landed | FINDINGS/t01-doubled-draw-both-sides-142100.md |
| t01blastradius-01 | t01 | blastradius | which of 213 documents change verdict under the two source-side change | 13:57 | 2 fixed, 0 regressions | landed | FINDINGS/t01-doubled-draw-both-sides-142100.md |
| 47_mA-02 | 47_margins | A | .docx blast radius of the uprightIfPageIsUpsideDown two-line fix: buil | 15:19 | expected by 16:15 | landed | FINDINGS/47_margins-CELLPATH-A-150000.md |
| 47_mB-02 | 47_margins | B | true size of 47_margins on the CURRENT engine: re-render the class's 2 | 15:19 | expected by 16:15 | landed | FINDINGS/47_margins-DIAGNOSE40-B-150000.md |
| 32_sA-01 | 32_stroke_lines | A | Does the pBdr replacement in FINDINGS/RULES-PBDR-IMPLEMENTATION.md act | 15:59 | expected by 16:20 | landed | FINDINGS/32_stroke_lines-PBDR-REFUTED-1720.md |
| t02_B-01 | t02_position | B | The 180deg uprightIfPageIsUpsideDown patch (FINDINGS, commit 09639d0)  | 15:59 | expected by 16:20 | landed | FINDINGS/47_margins-DOCX-BLAST-RADIUS-155500-6930.md |
| t08_B-01 | t08_line_order | B | which code path decides the .txt line order, and what single structura | 17:39 | expected by 17:45 | landed | FINDINGS/t08_line_order-DRAWING-ORDER-1740.md |
| t08_A-01 | t08_line_order | A | does t08 measure line order or drawing order, decided by synthetic pag | 22:39 | a verdict with both falsifications, not a fix | running |  |
| 32_sA-02 | 32_stroke_lines | A | a census of every rule in the failing documents by placement, and what | 22:39 | counts per sub-population and the cheapest 5 documents | landed | FINDINGS/32_stroke_lines-CELL-GUARD-IS-A-NO-OP-0450-f1x.md |
| 32_sA-03 | 32_stroke_lines | A | can the emitter tell its drawing anchor is inside a w:tc, and is the p | 04:49 | 04:20 | landed | FINDINGS/32_stroke_lines-CELL-GUARD-IS-A-NO-OP-0450-f1x.md |
| 32_sB-02 | 32_stroke_lines | B | is the 54-document carrier regression cell nesting or body-flow page o | 04:49 | 04:20 | landed | FINDINGS/32_stroke_lines-CARRIER-REGRESSION-IS-PAGE-OVERFLOW-0450-f1x.md |
| 32_sA-audit-01 | 32_stroke_lines | A-audit | are the 16 carrier Google results genuine measurement artifacts or han | 05:18 | a per-check map, an export hash, a real timestamp | landed | FINDINGS/32_stroke_lines-CARRIER-GOOGLE-EVIDENCE-IS-NOT-A-MEASUREMENT-0525-f1x.md |
| 32_sB-local-01 | 32_stroke_lines | B-local | does the carrier patch damage clean documents when measured in a clean | 05:18 | 4 of 10 controls worse | landed | FINDINGS/32_stroke_lines-CARRIER-GOOGLE-EVIDENCE-IS-NOT-A-MEASUREMENT-0525-f1x.md |
| 18_dA-02 | 18_displacement | A | what makes a single-page dense table drift in Google - row pitch or th | 07:36 | 07:38 | landed | FINDINGS/18_displacement-single-page-row-pitch-EMITTED-PITCH-IS-EXACT-082000-f1x.md |
| 18_dA-03 | 18_displacement | A | independently re-derive the sixteen and the spacer premise from the re | 08:31 | 08:20 | landed | FINDINGS/18_displacement-SPACER-REFUTED-0900-f1x.md |
| 18_dB-02 | 18_displacement | B | what places a page's first baseline, and is median_pt 0.96 a real offs | 08:31 | 08:40 | landed | FINDINGS/18_displacement-SPACER-REFUTED-0900-f1x.md |
| 18_dA-04 | 18_displacement | A | which clause of the check can fire on a 1.44-2.40 pt document, from th | 09:20 | landed 09:04 | landed | FINDINGS/18_displacement-table-spacer-CONFIRMED-6of16-TWO-PAGES-EXACTLY-FULL-1005-f1x.md |
| 18_dB-03 | 18_displacement | B | do 05/32/59/18 share ONE engine construct in the emitted docx, and nam | 09:20 | landed 09:04 | landed | FINDINGS/18_displacement-table-spacer-CONFIRMED-6of16-TWO-PAGES-EXACTLY-FULL-1005-f1x.md |
| 18_dtrheight-emitter-01 | 18_displacement | trheight-emitter | every place the engine emits trHeight/hRule, and whether 0.9634 belong | 10:08 | a unified diff and the list of emitters | landed | FINDINGS/18_displacement-cellbox-REFUTES-ROWSCALE-1035-f1x.md |
| 18_drow-growth-mechanism-01 | 18_displacement | row-growth-mechanism | given the real DocxWriter.java, which emitted number Google ignores wh | 10:09 | the mechanism with arithmetic, one recommended edit, and the rows it must not touch | landed | FINDINGS/18_displacement-cellbox-REFUTES-ROWSCALE-1035-f1x.md |
| 18_dA-05 | 18_displacement | A | consolidated every FINDINGS file and the two row emitters into one dos | 11:23 | 11:19 | landed | FINDINGS/18_displacement-PARTIAL-SPEND-REGRESSES-GOOGLE-1428-relay.md |
| 18_dB-04 | 18_displacement | B | recomputed leverage from benchmarks/gverify/*.json without classpick.p | 11:23 | 11:20 | running |  |
| 18_dA-06 | 18_displacement | A | static map of every writer that emits w:trHeight and cell w:spacing, a | 13:57 | expected by 14:30 | running |  |
| 18_dB-05 | 18_displacement | B | from the three measured declared->laid points compute the declaration  | 13:57 | expected by 14:30 | landed | ANSWERED: the 18.5 pt rung does not exist. The laid pitch ladder is laid = 0.75*(round(declared/0.75)+1), so laid pitch is always a multiple of 0.75 pt and 18.5 is not on it; the nearest rung to an 18.40 pt source is 18.75. No declaration lands 18.5, so this question is closed rather than answered with a value. See FINDINGS/18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md. |
| 00_pA-01 | 00_page_count | A | from the committed gverify JSONs and CENSUS.csv, how many documents do | 05:13 | 05:00 | landed | FINDINGS/18disp-prize-sizing-agentA.md |
| 00_pB-01 | 00_page_count | B | re-measure every claim of the page-count finding from the exported PDF | 05:13 | 05:40 | landed | FINDINGS/00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md |
| 18_dresidual-census-01 | 18_d | residual-census | which current-engine documents fail 18_displacement, and what has FIND | 06:17 | a per-document table plus the check arithmetic, from committed files only | landed | FINDINGS/18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md - 58 of 213 Google results are on the current engine (98be7c3c); 24 fail 18_displacement, only 2 fail it alone (16_right_aligned_amounts_txtpos, 31_times_body_arial_headings); the 16-document solo population is stamped 462353f9, not current. Killed the row-pitch lead before a round trip was spent. |
| 18_dblast-radius-01 | 18_d | blast-radius | the exact writer rule for w:trHeight/w:hRule, what the row-pitch patch | 06:17 | a blast-radius list and a verdict on whether the 18.5 pt rung is worth a Google round trip | landed | FINDINGS/18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md - the laid row-pitch ladder is 0.75*(round(d/0.75)+1) so 18.5 pt is unreachable and the nearest rung to an 18.40 pt source is 18.75; no document is both one check from clean and reachable by a row-height declaration. Refuted the run's opening plan before any build. |
| A118_displacement-01 | A1 | 18_displacement | writer-construct | 13:21 | Which single .docx writer construct causes the 18_displacement failures that 13+ documents fail alone, and which documents go CLEAN if fixed | running |  |
| B160_text_column_right_edge-01 | B1 | 60_text_column_right_edge | right-edge+shape_anchor | 13:21 | Is 60_text_column_right_edge the same construct as 59_shape_anchor (they travel together) and what minimal writer change clears both | running |  |
| 00_pA-02 | 00_page_count | A | which construct costs 350_question_paper its second page in Google - i | 16:37 | a charged line in DocxWriter and one general rule | landed | tools/p2w-bench/FINDINGS/00_page_count-350-INLINE-PICTURE-CARRIES-THE-LINE-1120-agent.md |
| gverB-01 | gverify | B | why gverify --collect cannot read the download result the Drive tool r | 16:37 | a fix with a test | landed | tools/p2w-bench/FINDINGS/gverify-COLLECT-DOWNLOAD-SHAPE-1120-agent.md |
| 18A-18_displacement-01 | 18A-01 | 18_displacement | A | 20:15 | is the LO regression on the spacer+trHeight patch a real layout change or a proxy artefact | running |  |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `06:15` attempt 34 on 18_displacement -> lead
- `06:17` agent deployed: 18_d / residual-census - which current-engine documents fail 18_displacement, and what has FINDINGS alrea
- `06:17` agent deployed: 18_d / blast-radius - the exact writer rule for w:trHeight/w:hRule, what the row-pitch patch yields, a
- `06:17` agent landed: 18_dresidual-census-01 /  -> FINDINGS/18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md - 58 of 213 Google results are on the current engine (98be7c3c); 24 fail 18_displacement, only 2 fail it alone (16_right_aligned_amounts_txtpos, 31_times_body_arial_headings); the 16-document solo population is stamped 462353f9, not current. Killed the row-pitch lead before a round trip was spent.
- `06:17` agent landed: 18_dblast-radius-01 /  -> FINDINGS/18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md - the laid row-pitch ladder is 0.75*(round(d/0.75)+1) so 18.5 pt is unreachable and the nearest rung to an 18.40 pt source is 18.75; no document is both one check from clean and reachable by a row-height declaration. Refuted the run's opening plan before any build.
- `06:17` agent landed: 18_dB-05 /  -> ANSWERED: the 18.5 pt rung does not exist. The laid pitch ladder is laid = 0.75*(round(declared/0.75)+1), so laid pitch is always a multiple of 0.75 pt and 18.5 is not on it; the nearest rung to an 18.40 pt source is 18.75. No declaration lands 18.5, so this question is closed rather than answered with a value. See FINDINGS/18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md.
- `07:36` attempt 35 on 18_displacement -> lead
- `08:11` attempt 3 on 00_page_count -> kept
- `11:28` attempt 4 on 00_page_count -> lead
- `13:21` agent deployed: A1 / 18_displacement - writer-construct
- `13:21` agent deployed: B1 / 60_text_column_right_edge - right-edge+shape_anchor
- `14:03` attempt 36 on 18_displacement -> reverted
- `14:03` agent landed: 18_displacement / A -> FINDINGS/18_displacement-PARTIAL-SPEND-REGRESSES-GOOGLE-1428-relay.md
- `16:35` attempt 5 on 00_page_count -> partial (2/23 moved)
- `16:37` agent deployed: 00_page_count / A - which construct costs 350_question_paper its second page in Google - it has 1 dr
- `16:37` agent deployed: gverify / B - why gverify --collect cannot read the download result the Drive tool returns now
- `16:37` agent landed: 00_pA-02 /  -> tools/p2w-bench/FINDINGS/00_page_count-350-INLINE-PICTURE-CARRIES-THE-LINE-1120-agent.md
- `16:37` agent landed: gverB-01 /  -> tools/p2w-bench/FINDINGS/gverify-COLLECT-DOWNLOAD-SHAPE-1120-agent.md
- `17:41` attempt 38 on 18_displacement -> lead (0/190 moved)
- `18:34` attempt 2 on 44_header_footer -> lead
- `19:31` attempt 39 on 18_displacement -> reverted
- `19:34` attempt 1 on 60_text_column_right_edge -> lead
- `19:36` attempt 2 on 60_text_column_right_edge -> lead
- `19:39` attempt 3 on 60_text_column_right_edge -> lead
- `20:15` agent deployed: 18A-01 / 18_displacement - A

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
