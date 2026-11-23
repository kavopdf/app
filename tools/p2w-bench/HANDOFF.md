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
| started | 02:19 |
| ended | 02:37 |
| how it ended | forced |
| plan | - |

## The picture, in the words of the run that left it

> 18_displacement: the residual on the 13 sole-failure documents is TWO constructs whose errors cancel, and that is why 20 attempts moved 4. Four live Google round trips this slot: med_dy -2.8 (362_price_list_dense), -3.0 (bus-timetable), -6.7 (mobile-bill), -13.0 (72_bank_statement); worst_dy 5.4/4.9/10.0/28.2; med_dx -0.2..+0.2 on all four; bad_pages [0] on all four. Run-by-run profiles: at every table's block top the gap is lost (-8.76, -4.19, -4.08 pt on mobile-bill) and inside every table each row is laid 0.75 pt too tall, so dy climbs back to 0 at the footer. 24 rows x 0.75 = 18 pt of ramp against 17.0 pt of step. Each half refuted alone because spending the spacer overflows (the DocxWriter guard at :6074 names mobile-bill and insurance-policy-schedule) and the row declaration change alone leaves the step uncompensated. The untried pair: deliver the gap through the first-row cell w:before (measured 1:1 by Google, 66 probes, error 0.000000) AND reduce w:trHeight by the same per-row amount, so the table total is unchanged. 362_price_list_dense has no step, only a monotone ramp, so it is the document that proves or refutes the pair. All 13 are converted in /scratch/work/p2w/out.

## What the next run should do first

> NEXT RUN: (1) THE PREVIOUS PAIR IS REFUTED - do not spend a slot on it. content+rule==pitch and hRule=atLeast make a trHeight-only change a no-op, and a cell-level gap escapes fitPage/shaveToFit (FINDINGS/18_displacement-STEP-IS-THE-UNSPENDABLE-SPACER-0323.md). (2) The class is two disjoint halves: a spacer half (the step at each table top = 0.784 x the declared w:line of an unspendable spacer, confirmed on 4 of 4 documents) and a row half (+0.75 pt per row, 21.75 pt over 362_price_list_dense's 29 rows). (3) FIRST MOVE: one Google round trip on 362_price_list_dense with trHeight = max(content, line-15) on rows where line > content only - LO-invariant by construction, and it tells you whether Google lays trHeight+rule or max(trHeight, content+rule). (4) The 4 ratchet rows need one corpus pass (~40 min) - start the slot with it, do not end with it. (5) The 9 REOPEN rows in PENDING-AUDIT.md are decisions with evidence attached.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| 18_dtrheight-emitter-01 | 18_displacement | trheight-emitter | every place the engine emits trHeight/hRule, and whether 0.9634 belong | 10:08 | a unified diff and the list of emitters | landed | FINDINGS/18_displacement-cellbox-REFUTES-ROWSCALE-1035-f1x.md |
| 18_drow-growth-mechanism-01 | 18_displacement | row-growth-mechanism | given the real DocxWriter.java, which emitted number Google ignores wh | 10:09 | the mechanism with arithmetic, one recommended edit, and the rows it must not touch | landed | FINDINGS/18_displacement-cellbox-REFUTES-ROWSCALE-1035-f1x.md |
| 18_dA-05 | 18_displacement | A | consolidated every FINDINGS file and the two row emitters into one dos | 11:23 | 11:19 | landed | FINDINGS/18_displacement-PARTIAL-SPEND-REGRESSES-GOOGLE-1428-relay.md |
| 18_dB-04 | 18_displacement | B | recomputed leverage from benchmarks/gverify/*.json without classpick.p | 11:23 | 11:20 | landed | DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed. |
| 18_dA-06 | 18_displacement | A | static map of every writer that emits w:trHeight and cell w:spacing, a | 13:57 | expected by 14:30 | landed | DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed. |
| 18_dB-05 | 18_displacement | B | from the three measured declared->laid points compute the declaration  | 13:57 | expected by 14:30 | landed | ANSWERED: the 18.5 pt rung does not exist. The laid pitch ladder is laid = 0.75*(round(declared/0.75)+1), so laid pitch is always a multiple of 0.75 pt and 18.5 is not on it; the nearest rung to an 18.40 pt source is 18.75. No declaration lands 18.5, so this question is closed rather than answered with a value. See FINDINGS/18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md. |
| 00_pA-01 | 00_page_count | A | from the committed gverify JSONs and CENSUS.csv, how many documents do | 05:13 | 05:00 | landed | FINDINGS/18disp-prize-sizing-agentA.md |
| 00_pB-01 | 00_page_count | B | re-measure every claim of the page-count finding from the exported PDF | 05:13 | 05:40 | landed | FINDINGS/00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md |
| 18_dresidual-census-01 | 18_d | residual-census | which current-engine documents fail 18_displacement, and what has FIND | 06:17 | a per-document table plus the check arithmetic, from committed files only | landed | FINDINGS/18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md - 58 of 213 Google results are on the current engine (98be7c3c); 24 fail 18_displacement, only 2 fail it alone (16_right_aligned_amounts_txtpos, 31_times_body_arial_headings); the 16-document solo population is stamped 462353f9, not current. Killed the row-pitch lead before a round trip was spent. |
| 18_dblast-radius-01 | 18_d | blast-radius | the exact writer rule for w:trHeight/w:hRule, what the row-pitch patch | 06:17 | a blast-radius list and a verdict on whether the 18.5 pt rung is worth a Google round trip | landed | FINDINGS/18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md - the laid row-pitch ladder is 0.75*(round(d/0.75)+1) so 18.5 pt is unreachable and the nearest rung to an 18.40 pt source is 18.75; no document is both one check from clean and reachable by a row-height declaration. Refuted the run's opening plan before any build. |
| A118_displacement-01 | A1 | 18_displacement | writer-construct | 13:21 | Which single .docx writer construct causes the 18_displacement failures that 13+ documents fail alone, and which documents go CLEAN if fixed | landed | DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed. |
| B160_text_column_right_edge-01 | B1 | 60_text_column_right_edge | right-edge+shape_anchor | 13:21 | Is 60_text_column_right_edge the same construct as 59_shape_anchor (they travel together) and what minimal writer change clears both | landed | DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed. |
| 00_pA-02 | 00_page_count | A | which construct costs 350_question_paper its second page in Google - i | 16:37 | a charged line in DocxWriter and one general rule | landed | tools/p2w-bench/FINDINGS/00_page_count-350-INLINE-PICTURE-CARRIES-THE-LINE-1120-agent.md |
| gverB-01 | gverify | B | why gverify --collect cannot read the download result the Drive tool r | 16:37 | a fix with a test | landed | tools/p2w-bench/FINDINGS/gverify-COLLECT-DOWNLOAD-SHAPE-1120-agent.md |
| 18A-01 | 18_displacement | A | is the LO regression on the spacer+trHeight patch a real layout change | 20:15 | is the LO regression on the spacer+trHeight patch a real layout change or a proxy artefact | landed | FINDINGS/18_displacement-LO-PROXY-VERDICT-2013-agentA.md |
| 18B-01 | 18_displacement | B | is there a construct that gives Google the row pitch without changing  | 20:44 | is there a construct that gives Google the row pitch without changing what LibreOffice draws | landed | FINDINGS/18_displacement-TRHEIGHT-CROSS-RENDERER-1506-agentB.md |
| 04_c-01 | 04_chars_missing construct: Google drops wps:txbx text; missing multiset fully explained by anchored boxes on 9 docs |  |  | 23:32 |  | landed | DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed. |
| 44_h-01 | 44_header_footer: .txt half clean (0 lost/duplicated across 31); 20 of 28 feet are floating anchors, 8 flow and still fail |  |  | 23:32 |  | landed | DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed. |
| 18_dA-01 | 18_displacement | A | which single failing Google check, if fixed, makes the most documents  | 02:00 | landed | landed | DUPLICATE - this run registered the same two agents twice; the ids held by RUN.json are 18_dA-02 / 04_cB-02, and the finding is on those. |
| 04_cB-01 | 04_chars_missing | B | is the missing-char multiset fully explained by anchored text boxes on | 02:00 | landed | landed | DUPLICATE - this run registered the same two agents twice; the ids held by RUN.json are 18_dA-02 / 04_cB-02, and the finding is on those. |
| 18_dA-02 | 18_displacement | A | which single failing Google check, if fixed, makes the most documents  | 02:07 | landed | landed | FINDINGS/18_displacement-SOLE-FAILURE-13-DOCS-0120-agentA.md |
| 04_cB-02 | 04_chars_missing | B | is the missing-char multiset fully explained by anchored text boxes | 02:07 | landed | landed | FINDINGS/04_chars_missing-TXBX-CLAIM-REFUTED-54of65-0120-agentB.md |
| 18_dA-03 | 18_displacement | A | audit the pending gate: which of the 21 closable items are still true | 02:35 | 03:05 | landed | PENDING-AUDIT.md |
| 18_dB-01 | 18_displacement | B | table block-top gap and per-row height in DocxWriter | 02:35 | 03:10 | landed | 18_displacement-STEP-IS-THE-UNSPENDABLE-SPACER-0323.md |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `00:09` attempt 16 on content-present-partly-displaced -> lead (0/13 moved)
- `00:25` attempt 17 on content-present-partly-displaced -> lead (0/13 moved)
- `00:30` attempt 18 on content-present-partly-displaced -> lead (0/13 moved)
- `01:42` attempt 3 on t12_word_invention -> lead (0/213 moved)
- `01:43` attempt 6 on 00_page_count -> lead (0/213 moved)
- `02:00` agent deployed: 18_displacement / A - which single failing Google check, if fixed, makes the most documents CLEAN
- `02:00` agent deployed: 04_chars_missing / B - is the missing-char multiset fully explained by anchored text boxes on 9 docs
- `02:07` agent deployed: 18_displacement / A - which single failing Google check, if fixed, makes the most documents CLEAN
- `02:07` agent deployed: 04_chars_missing / B - is the missing-char multiset fully explained by anchored text boxes
- `02:07` agent landed: 18_dB-04 /  -> DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed.
- `02:07` agent landed: 18_dA-06 /  -> DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed.
- `02:07` agent landed: A118_displacement-01 /  -> DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed.
- `02:07` agent landed: B160_text_column_right_edge-01 /  -> DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed.
- `02:07` agent landed: 04_c-01 /  -> DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed.
- `02:07` agent landed: 44_h-01 /  -> DEAD - no file in FINDINGS/ names this id; the run that deployed it ended without landing it. Closed 24 Nov, not re-deployed.
- `02:07` agent landed: 18_dA-01 /  -> DUPLICATE - this run registered the same two agents twice; the ids held by RUN.json are 18_dA-02 / 04_cB-02, and the finding is on those.
- `02:07` agent landed: 04_cB-01 /  -> DUPLICATE - this run registered the same two agents twice; the ids held by RUN.json are 18_dA-02 / 04_cB-02, and the finding is on those.
- `02:07` agent landed: 18_dA-02 /  -> FINDINGS/18_displacement-SOLE-FAILURE-13-DOCS-0120-agentA.md
- `02:07` agent landed: 04_cB-02 /  -> FINDINGS/04_chars_missing-TXBX-CLAIM-REFUTED-54of65-0120-agentB.md
- `02:08` attempt 42 on 18_displacement -> lead (0/13 moved)
- `02:34` attempt 43 on 18_displacement -> lead (0/13 moved)
- `02:35` agent deployed: 18_displacement / A - audit the pending gate: which of the 21 closable items are still true
- `02:35` agent deployed: 18_displacement / B - table block-top gap and per-row height in DocxWriter
- `02:37` agent landed: 18_dA-03 /  -> PENDING-AUDIT.md
- `02:37` agent landed: 18_dB-01 /  -> 18_displacement-STEP-IS-THE-UNSPENDABLE-SPACER-0323.md

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
