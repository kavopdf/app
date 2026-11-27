# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 16:06 |
| ended | 16:46 |
| how it ended | forced |
| plan | - |

## What the next run should do first

> READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 33 item(s) you can close - run pending.py and take them in its order before the class below. 

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| 18_dB-01 | 18_displacement | B | single-page half: is the exact-line spacer charged proportionally by G | 16:18 | 15:28 | landed | FINDINGS/18-displacement-SINGLE-PAGE-SPACER-MEASURED-26NOV-explore.md |
| 44_hA-01 | 44_header_footer | A | is flowFromBox the second anchor site and does the foot-band guard tra | 17:43 | 17:39 | running |  |
| --he-01 | --help |  |  | 19:43 |  | running |  |
| t09_A-01 | t09_page_furniture | A | is the 125 single-char present a TxtWriter line-assembly defect or a t | 20:47 | 19:45 | running |  |
| 18_dA-02 | 18_displacement | A | find the single construct behind the displaced runs on the 25 document | 22:14 | 16:10 | landed | FINDINGS/18-displacement-DOMINANT-SUBCAUSE-27NOV-agent.md |
| commA-01 | commit_gate | A | which clause of aa496ebe moves itr-computation and can it be split fro | 23:19 | 17:33 | running |  |
| triaA-01 | triage | A | which of the 113 failing checks buys the most clean documents, with th | 01:12 | 18:55 | running |  |
| ssimB-01 | ssim | B | what caps the 99 percent SSIM goal - is the deficit concentrated or un | 01:12 | 19:00 | running |  |
| Expl-01 | Explore:docx construct ranking by documents-cleared (10-row table, rung rule named first) |  |  | 05:51 |  | running |  |
| Expl-02 | Explore:txt failure root cause (8 docs, 12 check-instances; recommended the t01 character unit) |  |  | 05:51 |  | running |  |
| 60_tA-01 | 60_text_column_right_edge | A | which engine construct sets a body line's right edge, and which fixes  | 08:04 | 07:40 | landed | FINDINGS/RIGHT-TAB-POSITION-60-EDGE-27NOV-fixer.md |
| gateB-01 | gate | B | why does regress.py --check refuse on unmodified HEAD | 08:04 | 07:41 | landed | FINDINGS/GATE-PREREQUISITES-ARE-THE-REAL-BLOCKER-27NOV-fixer.md |
| 60_tA-02 | 60_text_column_right_edge | A | which engine construct sets a body line's right edge, and which fixes  | 08:12 | 07:40 | landed | FINDINGS/RIGHT-TAB-POSITION-60-EDGE-27NOV-fixer.md |
| gateB-02 | gate | B | why does regress.py --check refuse on unmodified HEAD | 08:12 | 07:41 | landed | FINDINGS/GATE-PREREQUISITES-ARE-THE-REAL-BLOCKER-27NOV-fixer.md |
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

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `08:12` agent landed: 60_text_column_right_edge / A -> FINDINGS/RIGHT-TAB-POSITION-60-EDGE-27NOV-fixer.md
- `08:12` agent landed: gate / B -> FINDINGS/GATE-PREREQUISITES-ARE-THE-REAL-BLOCKER-27NOV-fixer.md
- `09:13` attempt 104 on 18_displacement -> lead
- `09:14` agent deployed: 18-displacement w:pBdr probe: measured Google 15.00 vs 15.75, finding committed /  - 
- `09:42` attempt 105 on 18_displacement -> lead
- `09:46` attempt 13 on t12_word_invention -> lead
- `10:56` attempt 106 on 18_displacement -> lead
- `10:58` agent deployed: 18_displacement / A - which sub-cause of the displacement survives every eliminated one, measured on o
- `10:58` agent deployed: 60_text_column_right_edge / B - how many CLEAN documents does fixing 60 alone win, and is there a live construct
- `10:58` agent landed: 18_displacement / A -> FINDINGS/18-displacement-DOMINANT-SUBCAUSE-27NOV-agent.md
- `10:58` agent landed: 60_text_column_right_edge / B -> FINDINGS/60-COLUMN-RIGHT-EDGE-CENSUS-27NOV-agent.md
- `11:21` agent deployed: 18dA-03 / 18_displacement - baseline placement inside the hairline exact line box
- `11:21` agent deployed: 60tB-02 / 60_text_column_right_edge - the right-tab line is split by our own reader
- `11:54` attempt 107 on 18_displacement -> lead
- `12:08` agent deployed: 18_displacement / A - Does the +2.70 pt charge on 31_times come from the baseline's placement in a hai
- `12:08` agent deployed: 18_displacement / B - Is 18_displacement's dy an ascent artifact - bbox top vs baseline origin - and h
- `12:08` agent landed: 18_displacement / A -> FINDINGS/18dA-03-ASCENT-NOT-DISPLACEMENT-MEASURED-27NOV-relay.md
- `12:08` agent landed: 18_displacement / B -> FINDINGS/18dA-03-ASCENT-NOT-DISPLACEMENT-MEASURED-27NOV-relay.md
- `13:31` agent deployed: corpus-cache-per-document-27NOV /  - 
- `14:42` attempt 21 on t01_word_accuracy -> lead (0/3 moved)
- `15:24` attempt 108 on 18_displacement -> lead
- `16:43` attempt 109 on 18_displacement -> lead
- `16:45` agent deployed: 18_displacement / small-dy cluster of 15 - which code site places a run's baseline, and is the small dy an ascent artefact 
- `16:45` agent deployed: txt / form-feed lead - is _txt_lines dropping page separators, and how many documents does it clear
- `16:50` attempt 110 on 18_displacement -> kept

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
