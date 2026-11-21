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
| started | 11:52 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> stage.py was reporting 'classify' on every fresh clone for a day, and three watchdog passes blamed the classifier cron for it. The cause was in stage.py, not the cron: it compared benchmarks/DEFECT-CLASSES.md (the previous pipeline's ghost, which nothing regenerates) against the gverify results by filesystem mtime, and a git clone stamps every file with the checkout time, so the comparison was decided by unpack order - measured 21 Nov, 05:47:52 against 05:47:53. Fixed and pushed de5d216: the live table is DEFECT-CLASSES-GOOGLE.md and currency is judged by the last commit touching each path (gverify 42bdcda 01:44:38, table e86a88a 04:47:32). stage.py now reads 'fix' with 185 failing documents, and both negative tests still fire. Two agents landed: 32_stroke_lines is the biggest open Google class (145 docs, 144 of them LibreOffice-draws-Google-drops) and its root cause is that every standalone rule leaves DocxWriter.shape() at line 2772 as a floating <w:drawing>/<wp:anchor>, which google_safe.py already lists twice as ignored by Google; FINDINGS/RULES-PBDR-IMPLEMENTATION.md holds the measured pBdr replacement (0 -> 2 rules on the probe document) and the ctx.flowY = s.topPt line whose omission turns it into a regression. The t02_position two-line claim from 47_margins-TXT-HALF-IS-T02-1055-f1x.md is REFUTED as a two-format fix: flippedPage reaches only buildPara, lineX is read only by TxtWriter, and 47_margins already passes on all five t02 documents in the stored LibreOffice table. Its third line as written deletes the only guard protecting 15_stamp_on_scanned_page; use 'if (g.dirx > -0.5f) return false;' instead.

## What the next run should do first

> Land the pBdr rule replacement: FINDINGS/RULES-PBDR-IMPLEMENTATION.md, first statement of DocxWriter.shape() at line 2772 (return before line 2779), carrying the ctx.flowY = s.topPt update. Screen 32_stroke_lines first, then the full corpus pass. The finding predicts 124 documents cleared among the 144 LibreOffice-only ones, and all 145 if the residual is only the footer rule.

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

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `00:57` attempt 8 on t01_word_accuracy -> reverted (0/5 moved)
- `01:41` agent deployed: t01_word_accuracy / A - is the handed diagnosis (nested form matrix disagreement, rotated line off page)
- `01:41` agent deployed: t01_word_accuracy / B - why does 39_small_caps_letter_spacing lose 8 words and invent 2 - writer or refe
- `01:41` agent landed: t01_word_accuracy / A -> FINDINGS/411-nested-xobject-matrix-1940.md
- `01:41` agent landed: t01_word_accuracy / B -> FINDINGS/39-small-caps-gap-threshold-0150-fixer.md
- `01:41` attempt 9 on t01_word_accuracy -> reverted (0/5 moved)
- `01:47` attempt 10 on t01_word_accuracy -> reverted (0/5 moved)
- `01:51` attempt 11 on t01_word_accuracy -> reverted (0/5 moved)
- `03:25` attempt 11 on 47_margins -> partial (2/26 moved)
- `03:36` attempt 12 on 47_margins -> partial (2/26 moved)
- `04:34` attempt 12 on t01_word_accuracy -> partial
- `04:34` attempt 13 on t01_word_accuracy -> partial (1/5 moved)
- `04:36` agent deployed: t01_word_accuracy / A - census of every widget appearance stream over all 213 documents - how many widge
- `04:36` agent deployed: t01_word_accuracy / B - implement the /AP /N glyph walk in its own clone and measure 601 and the Account
- `04:36` agent landed: t01_word_accuracy / A -> FINDINGS/widget-ap-glyph-walk-0436-f1x.md
- `04:36` agent landed: t01_word_accuracy / B -> FINDINGS/widget-ap-glyph-walk-0436-f1x.md
- `07:16` attempt 13 on 47_margins -> partial (0/26 moved)
- `10:39` attempt 14 on t01_word_accuracy -> reverted (0/213 moved)
- `11:16` attempt 15 on t01_word_accuracy -> partial (0/5 moved)
- `11:34` agent deployed: 32_stroke_lines / B - why Google drops the rules LibreOffice draws, and which construct replaces them
- `11:34` agent deployed: t02_position / A - is the two-line 47_margins/t02 claim a real two-format fix
- `11:34` agent landed: 32_stroke_lines / B -> tools/p2w-bench/FINDINGS/32_stroke_lines-google-drop-113048-9597.md
- `11:34` agent landed: t02_position / A -> tools/p2w-bench/FINDINGS/t02_position-two-line-claim-112617-0bfd.md
- `11:35` attempt 1 on t02_position -> error
- `13:43` attempt 14 on 47_margins -> error

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
