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
| started | 11:15 |
| ended | 13:09 |
| how it ended | forced |
| plan | - |

## The picture, in the words of the run that left it

> 18_displacement: the residual on the 13 sole-failure documents is TWO constructs whose errors cancel, and that is why 20 attempts moved 4. Four live Google round trips this slot: med_dy -2.8 (362_price_list_dense), -3.0 (bus-timetable), -6.7 (mobile-bill), -13.0 (72_bank_statement); worst_dy 5.4/4.9/10.0/28.2; med_dx -0.2..+0.2 on all four; bad_pages [0] on all four. Run-by-run profiles: at every table's block top the gap is lost (-8.76, -4.19, -4.08 pt on mobile-bill) and inside every table each row is laid 0.75 pt too tall, so dy climbs back to 0 at the footer. 24 rows x 0.75 = 18 pt of ramp against 17.0 pt of step. Each half refuted alone because spending the spacer overflows (the DocxWriter guard at :6074 names mobile-bill and insurance-policy-schedule) and the row declaration change alone leaves the step uncompensated. The untried pair: deliver the gap through the first-row cell w:before (measured 1:1 by Google, 66 probes, error 0.000000) AND reduce w:trHeight by the same per-row amount, so the table total is unchanged. 362_price_list_dense has no step, only a monotone ramp, so it is the document that proves or refutes the pair. All 13 are converted in /scratch/work/p2w/out.

## What the next run should do first

> PENDING FIRST: 23 item(s) you can close - run pending.py and take them in its order before the class below. 18_displacement: APPLY tools/p2w-bench/FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch, build, then START the slot with the 212-document pass (p2w.py --force --budget 250, repeat) - that pass is the whole cost. It is measured: 362_price_list_dense 41/42 -> 42/42 in Google, electricity-bill and 330_cad_drawing_sheet byte-identical. Do NOT re-run the trHeight=max(content,line-15) probe - it is refuted and the guard makes it unnecessary. After the pass: regress.py --check, --stamp, commit app/+RANKING.csv, attempt.py --class 18_displacement. Then check the 9 documents named in FINDINGS/18_displacement-UNIFORM-PITCH-GUARD-GOOGLE-42of42-0450-fixer.md for a uniform pitch.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
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
| 18_dA-04 | 18_displacement | A | what is settled, refuted and left as a patch on this class | 04:38 | 10 min | landed | FINDINGS/18_displacement-STEP-IS-THE-UNSPENDABLE-SPACER-0323.md (memo returned in-run; 13 refuted leads, spacer-guard .patch committed but not applied) |
| 18_dB-02 | 18_displacement | B | if the table-top step were removed, which documents become CLEAN | 04:38 | 10 min | landed | step-removal alone reaches 4 documents, all already 42/42 in benchmarks/gverify - the class ceiling is 14, not 40 |
| 18_drowheight-prepass-01 | 18_displacement | rowheight-prepass | produce a minimal compilable two-pass emit for the atLeast trHeight th | 06:34 | a unified diff that applies and compiles, plus the catch that an all-equal test skips the target document | landed | FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch |
| 18_drowpitch-census-01 | 18_displacement | rowpitch-census | census the table row pitch of every corpus PDF and classify uniform-fr | 06:34 | a CSV and a count per class, so the guard's population is measured rather than assumed | landed | no corpus in its sandbox; it built and validated the census tool against four synthetic PDFs with known pitch and reported zero documents rather than inventing numbers. The census was run here on the 211 real .docx instead: 85 documents under guard A, 54 under guard B. |
| A1 | 25_invisible_text | check-definition | what does 25_invisible_text compare, and which construct makes 48 docu | 07:03 | the check's operands and a named Java site, so a fix could be attempted | landed | the check stopped at the FIRST fill under a run's corner. A Google export opens with a page-sized white rect and rasterises our bands into images, so white type on an orange band matched the sheet. This run's fix; 5 documents went 42/42. |
| A2 | 18_displacement | row-height-law | what law does Google use to lay a table row's height, and what LO-inva | 07:22 | a law fitted to the committed Google numbers, and one falsifiable change | landed | row = 0.75*round((max(trHeight,content)+rule)/0.75): trHeight is a quantised floor, not a length. 362 is unruled, so it does not ramp +0.75/row - the carry-over's 21.75 pt is ruled-table arithmetic. The LO-invariant change is DocxWriter:6468 declaring the row one rule short; it must be tested on a ruled document, not 362. |
| 18_dA-05 | 18_displacement | A | is the page-height guard why no table-top spacer is ever spent on the  | 08:20 | 08:05 | running |  |
| 60_tB-01 | 60_text_column_right_edge | B | is 60 or 18 reading the paper instead of the defect - the 25_invisible | 08:20 | 08:05 | landed | FINDINGS/60_text_column_right_edge-VERDICT-MIXED-1115-fixer.md |
| 60_tB-02 | 60_text_column_right_edge | B | is 60 or 18 reading the paper - the 25_invisible_text precedent | 12:28 | 11:19 | landed | FINDINGS/60_text_column_right_edge-VERDICT-MIXED-1115-fixer.md |
| 04_cA-01 | 04_chars_missing | A | real writer defect or instrument, and how much t01/t12 already explain | 12:28 | 11:21 | landed | FINDINGS/04_chars_missing-REAL-WRITER-DEFECT-1115-fixer.md |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `04:38` agent landed: 18_displacement / B -> step-removal alone reaches 4 documents, all already 42/42 in benchmarks/gverify - the class ceiling is 14, not 40
- `04:39` attempt 7 on 00_page_count -> lead
- `05:50` attempt 45 on 18_displacement -> lead
- `06:32` attempt 46 on 18_displacement -> lead
- `06:34` agent deployed: 18_displacement / rowheight-prepass - produce a minimal compilable two-pass emit for the atLeast trHeight that applies
- `06:34` agent deployed: 18_displacement / rowpitch-census - census the table row pitch of every corpus PDF and classify uniform-fractional, 
- `06:35` agent landed: 18_drowheight-prepass-01 /  -> FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch
- `06:35` agent landed: 18_drowpitch-census-01 /  -> no corpus in its sandbox; it built and validated the census tool against four synthetic PDFs with known pitch and reported zero documents rather than inventing numbers. The census was run here on the 211 real .docx instead: 85 documents under guard A, 54 under guard B.
- `06:38` attempt 47 on 18_displacement -> lead
- `06:40` attempt 48 on 18_displacement -> lead
- `07:11` attempt 1 on 25_invisible_text -> kept (2/5 moved)
- `07:12` attempt 2 on 25_invisible_text -> kept (5/5 moved)
- `07:21` attempt 49 on 18_displacement -> reverted (0/2 moved)
- `08:18` attempt 4 on 60_text_column_right_edge -> lead
- `08:18` attempt 50 on 18_displacement -> lead
- `08:20` agent deployed: 18_displacement / A - is the page-height guard why no table-top spacer is ever spent on the 14 documen
- `08:20` agent deployed: 60_text_column_right_edge / B - is 60 or 18 reading the paper instead of the defect - the 25_invisible_text prec
- `09:17` attempt 51 on 18_displacement -> lead (1/10 moved)
- `12:28` attempt 52 on 18_displacement -> lead
- `12:28` agent deployed: 60_text_column_right_edge / B - is 60 or 18 reading the paper - the 25_invisible_text precedent
- `12:28` agent landed: 60_text_column_right_edge / B -> FINDINGS/60_text_column_right_edge-VERDICT-MIXED-1115-fixer.md
- `12:28` agent deployed: 04_chars_missing / A - real writer defect or instrument, and how much t01/t12 already explains
- `12:28` agent landed: 04_chars_missing / A -> FINDINGS/04_chars_missing-REAL-WRITER-DEFECT-1115-fixer.md
- `12:28` agent landed: 60_text_column_right_edge / B -> FINDINGS/60_text_column_right_edge-VERDICT-MIXED-1115-fixer.md
- `13:07` attempt 54 on 18_displacement -> lead (0/129 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
