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
| started | 20:54 |
| ended | 22:43 |
| how it ended | forced |
| plan | - |

## The picture, in the words of the run that left it

> 18_displacement: the trHeight-absorb construct (trHeight=pitch-20tw + tcMar bottom) was applied, built and measured in Google on 2 documents - tnhr 46/47->46/47, mobile-bill 46/47->46/47, same check, nothing clean. Independent PyMuPDF geometry: the patch halves the drift ramp (16.25->8.38 pt, table span 495->482 vs source 478) but the first line of the block sits at -10.16 pt in BOTH renders and mobile-bill at -15.75, so the residual 18_displacement is a per-document TOP-OF-BLOCK OFFSET that no row construct can touch. LO cost of the patch confirmed by two agents (30-36 share@5 on four documents). Reverted, no engine change landed.

## What the next run should do first

> PENDING FIRST, FIXING SECOND. 81 items are outstanding and the user has asked for them to be cleared before any new class is taken. Run `python3 tools/p2w-bench/pending.py` - it lists them in the order they should be taken and says so itself: 'this is the work. Do not take a new class until it is empty.' The 81 are 72 [blocker] (accumulated watchdog observations, each with a 'can I fix it' line), 5 [ratchet] and 4 [agent]. The 4 agents were deployed 550-700 minutes ago and never committed a finding - they died with their runs, so check FINDINGS/ for the id and close them as dead rather than re-deploying. Clear them in the order pending.py gives. Only when that list is empty does classpick decide a class.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
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
| 18A-01 | 18_displacement | A | is the LO regression on the spacer+trHeight patch a real layout change | 20:15 | is the LO regression on the spacer+trHeight patch a real layout change or a proxy artefact | landed | FINDINGS/18_displacement-LO-PROXY-VERDICT-2013-agentA.md |
| 18B-01 | 18_displacement | B | is there a construct that gives Google the row pitch without changing  | 20:44 | is there a construct that gives Google the row pitch without changing what LibreOffice draws | landed | FINDINGS/18_displacement-TRHEIGHT-CROSS-RENDERER-1506-agentB.md |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

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
- `20:44` attempt 40 on 18_displacement -> reverted (0/16 moved)
- `20:44` agent deployed: 18B-01 / 18_displacement - B
- `20:45` two agents landed and recorded: 18A-01 LO proxy verdict, 18B-01 trHeight cross-renderer
- `21:29` attempt 41 on 18_displacement -> lead

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
