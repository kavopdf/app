# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 09:16 |
| ended | 09:45 |
| how it ended | forced |
| plan | - |

## What the next run should do first

> READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. 

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| 18-d-01 | 18-displacement w:pBdr probe: measured Google 15.00 vs 15.75, finding committed |  |  | 09:14 |  | running |  |
| 18_dA-03 | 18_displacement | A | which sub-cause of the displacement survives every eliminated one, mea | 10:58 | 10:15 | landed | FINDINGS/18dA-03-ASCENT-NOT-DISPLACEMENT-MEASURED-27NOV-relay.md |
| 60_tB-01 | 60_text_column_right_edge | B | how many CLEAN documents does fixing 60 alone win, and is there a live | 10:58 | 10:15 | landed | FINDINGS/60-COLUMN-RIGHT-EDGE-CENSUS-27NOV-agent.md |
| 18dA18_displacement-01 | 18dA-03 | 18_displacement | baseline placement inside the hairline exact line box | 11:21 | Turn the measured 0.312 em renderer baseline vs 0.050 em engine charge into a minimal, measured engine change that makes 18_displacement pass on 31_times_body_arial_headings and its siblings without regressing any document. Expected by 12:35 | running |  |
| 60tB60_text_column_right_edge-01 | 60tB-02 | 60_text_column_right_edge | the right-tab line is split by our own reader | 11:21 | Find why Google's export splits a right-tabbed line into two lines and ours into one (17_matched_runs 34->13), and produce a reader or writer change that keeps the tab's 538.50 pt edge without collapsing 17. Expected by 12:35 | running |  |
| 18_dA-04 | 18_displacement | A | Does the +2.70 pt charge on 31_times come from the baseline's placemen | 12:08 | 12:35 | running |  |
| 18_dB-02 | 18_displacement | B | Is 18_displacement's dy an ascent artifact - bbox top vs baseline orig | 12:08 | 12:35 | landed | FINDINGS/18dA-03-ASCENT-NOT-DISPLACEMENT-MEASURED-27NOV-relay.md |
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

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `03:41` agent landed: commit_gate / B -> FINDINGS/GATE-REFUSES-MAIN-ITSELF-AND-THE-RUNG-IS-27-NET-28NOV-relay.md
- `04:27` attempt 6 on 63_table_rows -> lead
- `04:29` attempt 7 on 63_table_rows -> lead
- `05:39` attempt 9 on 60_text_column_right_edge -> kept
- `05:40` agent deployed: 60_text_column_right_edge / A - which engine construct sets a body line's right edge - is 60 an engine defect or
- `05:40` agent landed: 60_text_column_right_edge / A -> FINDINGS/60-THE-LINE-OBJECT-IS-A-TABLE-ROW-28NOV-fixer.md
- `05:40` agent deployed: 18_displacement / B - test the 0.961 spacer model at the current engine and quantify the inverse corre
- `05:40` agent landed: 18_displacement / B -> FINDINGS/18-DISPLACEMENT-SPACER-MODEL-REFUTED-DRIFT-IS-THE-LEAD-28NOV-fixer.md
- `05:41` attempt 121 on 18_displacement -> error
- `06:04` agent deployed: 18_displacement / A - root cause of cell displacement; landed c8056b8
- `06:04` agent deployed: 63_table_rows / B - ROW_RUNG_UNDER_TW bug or compensation; landed 0b15dc2
- `07:02` attempt 122 on 18_displacement -> lead
- `08:54` attempt 123 on 18_displacement -> lead
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

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
