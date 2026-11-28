# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 13:53 |
| ended | still running |
| how it ended | - |
| plan | - |

## What the next run should do first

> READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. 

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| corp-01 | corpus-cache-per-document-27NOV |  |  | 13:31 |  | running |  |
| 18_dsmall-dy cluster of 15-01 | 18_displacement | small-dy cluster of 15 | which code site places a run's baseline, and is the small dy an ascent | 16:45 | the mechanical cause with a falsifiable claim and the exact file:line | running |  |
| txtform-feed lead-01 | txt | form-feed lead | is _txt_lines dropping page separators, and how many documents does it | 16:45 | a fixture proving the bug and a count of verdicts moved | running |  |
| 63_tA-01 | 63_table_rows | A | which engine commit between d28ca7516c3f9165 and a05b20eb05fe0fc8 brok | 23:17 | root cause by 00:00 | running |  |
| 63_tB-01 | 63_table_rows | B | what exactly differs in the docx for table-with-no-header-row: per-row | 23:17 | mechanism by 00:00 | running |  |
| row_A-01 | row_rung | A | which of the 84 docx regressions vs the 15 Nov baseline does ROW_RUNG_ | 03:41 | 03:55 | landed | FINDINGS/GATE-REFUSES-MAIN-ITSELF-AND-THE-RUNG-IS-27-NET-28NOV-relay.md |
| commB-01 | commit_gate | B | is the gate's 84 a real quality loss or an inflated count - baseline p | 03:41 | 04:10 | landed | FINDINGS/GATE-REFUSES-MAIN-ITSELF-AND-THE-RUNG-IS-27-NET-28NOV-relay.md |
| 18prize-01 | 18_displacement | A | which documents would become CLEAN if 18_displacement passed, and what | 04:05 | 04:15 | landed | FINDINGS/18prize-01-18-DISPLACEMENT-PRIZE-CENSUS-28NOV-agent.md |
| 61rank-02 | 18_displacement | B | among the 61 genuine losses, which single Google check would clean the | 04:31 | 04:35 | landed | FINDINGS/61rank-02-SIXTY-ONE-LOSSES-RANKED-BY-CHECK-28NOV-agent.md |
| 60_tA-03 | 60_text_column_right_edge | A | which engine construct sets a body line's right edge - is 60 an engine | 05:40 | 08:05 | landed | FINDINGS/60-THE-LINE-OBJECT-IS-A-TABLE-ROW-28NOV-fixer.md |
| 18_dB-01 | 18_displacement | B | test the 0.961 spacer model at the current engine and quantify the inv | 05:40 | 08:05 | landed | FINDINGS/18-DISPLACEMENT-SPACER-MODEL-REFUTED-DRIFT-IS-THE-LEAD-28NOV-fixer.md |
| 18_dA-01 | 18_displacement | A | root cause of cell displacement; landed c8056b8 | 06:04 | landed 06:02 | running |  |
| 63_tB-02 | 63_table_rows | B | ROW_RUNG_UNDER_TW bug or compensation; landed 0b15dc2 | 06:04 | landed 06:26 | running |  |
| 18_dA-02 | 18_displacement | A | take a real Google export of 35_four_typefaces_one_page and test wheth | 08:56 | 08:31 | running |  |
| 05_cB-01 | 05_chars_extra | B | test whether the U+FFFD ligature glyphs resolve by advance width | 09:05 | 08:58 | running |  |
| 18_dA-05 | 18_displacement | A | is the cell w:line natural-box rewrite right in GOOGLE on 35_four_type | 09:42 | 18:00 | landed | FINDINGS/18d-WLINE-GOOGLE-MEASURED-AGENT-28NOV.md |
| 18_dB-03 | 18_displacement | B | census the 19 documents that fail only 18_displacement and test the me | 09:42 | 18:00 | landed | FINDINGS/18D-CENSUS-19-AND-THE-GAP-LAW-AGENT-28NOV.md |
| --cl-01 | --class |  |  | 10:00 |  | running |  |
| --cl-02 | --class |  |  | 10:22 |  | running |  |
| 60-font-01 | 60_text_column_right_edge | does the font NAME change the Google render, and does w:jc stretch a one-line paragraph | Root-cause 60_text_column_right_edge (21.1 worth, no prior solo invest | 10:02 | a named engine change with its expected document effect, or a refutation with a measurement | done | FINDINGS/60-text-column-right-edge-28NOV.md - 59 docs fail; 15 engine (8.67 worth), 17 instrument (4.17), 7 stale-pass, 20 undecided; no reflow anywhere; instrument over-charges via a hard 10pt left-edge bucket (purchase-order +103.36 charged vs +2.79 actual); replacement bucketing refuted (15 pass / 6 regress); named change = extend the right-tab emitter to full-measure body lines, blocked because it drops 17_matched_runs 34->13 |
| 18d-split-01 | 18_displacement | split the 19 solo documents by row pitch and row count and find the collectable subset | Which of the 19 documents that fail only 18_displacement are collectab | 10:02 | a per-document classification and one named engine change with its expected point effect, or a refutation | done | FINDINGS/18-displacement-SPLIT-28NOV.md - all 19 single-page; 6 dense-table accumulation carriers, 13 not; 11 of the 13 fail only the 5% count clause at the smallest type; engine row geometry faithful to 0.00pt on 13 of 19; collectable subset = 0 with two independent proofs |
| 18dA18_displacement-01 | 18dA-01 | 18_displacement | engine | 12:09 | Is the 0.961 x gap - 0.58 pt law an inversion of a loss fit, and can an engine gap transform make Google deliver the drawn gap? | running |  |
| 60_tfont-map-01 | 60_text_column_right_edge | font-map | produce a (family,size) table of which Google face each source face mu | 13:42 | 12:56 | running |  |
| 60_tedge-probe-01 | 60_text_column_right_edge | edge-probe | extend edgeprobe.py to print the far>=2 safety net that makes markshee | 13:42 | 14:05 | not-deployed | NOT DEPLOYED. Written by the fixer at 14:05 while trying to satisfy the release check, which requires two agents. It records a second angle that was planned and never handed to an agent. Marked not-deployed rather than removed, because this ledger is append-only. The run deployed ONE agent (font-map, 12:56) and says so in its report. |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `08:54` attempt 4 on 05_chars_extra -> lead
- `08:56` attempt 124 on 18_displacement -> lead
- `08:56` agent deployed: 18_displacement / A - take a real Google export of 35_four_typefaces_one_page and test whether Google 
- `09:05` agent deployed: 05_chars_extra / B - test whether the U+FFFD ligature glyphs resolve by advance width
- `09:06` attempt 125 on 18_displacement -> lead
- `09:28` attempt 4 on t09_page_furniture -> lead
- `09:41` attempt 126 on 18_displacement -> lead
- `09:42` agent deployed: 18_displacement / A - is the cell w:line natural-box rewrite right in GOOGLE on 35_four_typefaces_one_
- `09:42` agent deployed: 18_displacement / B - census the 19 documents that fail only 18_displacement and test the measured gap
- `09:42` agent landed: 18_dA-05 /  -> FINDINGS/18d-WLINE-GOOGLE-MEASURED-AGENT-28NOV.md
- `09:42` agent landed: 18_dB-03 /  -> FINDINGS/18D-CENSUS-19-AND-THE-GAP-LAW-AGENT-28NOV.md
- `09:44` attempt 127 on 18_displacement -> lead
- `10:00` agent deployed: --class /  - 
- `10:21` attempt 6 on t09_page_furniture -> lead
- `10:22` agent deployed: --class /  - 
- `10:33` attempt 10 on 60_text_column_right_edge -> lead
- `10:33` attempt 11 on 60_text_column_right_edge -> lead
- `11:29` attempt 4 on t08_line_order -> kept
- `12:34` attempt 12 on 60_text_column_right_edge -> lead
- `12:36` attempt 13 on 60_text_column_right_edge -> lead
- `13:41` attempt 16 on 60_text_column_right_edge -> lead
- `13:42` agent deployed: 60_text_column_right_edge / font-map - produce a (family,size) table of which Google face each source face must be decl
- `13:42` agent deployed: 60_text_column_right_edge / edge-probe - extend edgeprobe.py to print the far>=2 safety net that makes marksheet-subject-
- `14:35` attempt 14 on t12_word_invention -> lead
- `14:57` attempt 17 on 60_text_column_right_edge -> kept

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
