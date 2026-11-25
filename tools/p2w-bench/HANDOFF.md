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
| started | 12:13 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> The row-pitch dither fires: A/B on the engine's own output shows declared w:trHeight moving 18.0/19.0 -> 17.15/18.15 pt on mobile-bill, salary-slip-corporate and very-long-single-column-table (patch subtracts the 0.875 pt rule charge). It is a lead, not a kept fix: the rendered share@5 could not be obtained because screen.py's soffice prerender hangs (BLOCKERS 25 Nov, 3 x 280 s calls). The spacer half of the same proposal (always w:before, drop the budget guard) was never applied and should stay separate. The repo holds three inconsistent laws for w:line exact on an sz=2 empty paragraph - resolve that before leaning on the construct.

## What the next run should do first

> READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. Fix or bypass the screen.py soffice prerender hang FIRST - it blocks every rendered attempt. Then judge the dither by share@5 on mobile-bill, electricity-bill, salary-slip-corporate, very-long-single-column-table before a corpus pass.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| 04_cA-01 | 04_chars_missing | A | real writer defect or instrument, and how much t01/t12 already explain | 12:28 | 11:21 | landed | FINDINGS/04_chars_missing-REAL-WRITER-DEFECT-1115-fixer.md |
| conv-01 | conversion cost |  |  | 14:00 |  | running |  |
| txt -01 | txt discrepancy |  |  | 14:00 |  | running |  |
| 18_dA-06 | 18_displacement | A | where does the 11 s/doc conversion go, and the smallest change that ma | 14:00 | 13:16 | landed | 18_displacement-FULL-PASS-DOES-NOT-FIT-A-SLOT-0650-fixer.md |
| 18_dB-03 | 18_displacement | B | why do RANKING-TXT.csv and the report disagree by 50 documents | 14:00 | 13:18 | running |  |
| 60ed60_text_column_right_edge-01 | 60_text_column_right_edge | A | is the right edge the engine's or the face's | 18:27 |  | landed | FINDINGS/60_text_column_right_edge-EDGE-IS-THE-FACE-4GOOGLE-1INSTRUMENT-24NOV-agentA.md |
| pc2300_page_count-01 | 00_page_count | B | what is on the extra page of the 23 refusals | 18:27 |  | landed | FINDINGS/00_page_count-23-REFUSED-ALL-ENGINE-0-CLEAN-24NOV-agentB.md |
| anch-01 | anchored-box patch design: six ctx.positioned sites, one emitter, class-free rule, CLEAN set, falsifiers |  |  | 22:34 |  | running |  |
| clea-01 | clean-count audit: all 36 clean documents were offered 42 checks and never saw 62-66 |  |  | 22:34 |  | running |  |
| gap--01 | gap-cap patch: traced DocxWriter, produced spendWideGap() foot-band patch, applied and reverted as a no-op on 69/323/311; census: cap = 1469 chars over 23 of 35 positioned pages |  |  | 02:59 |  | running |  |
| zero-01 | zero-gap census: the latch is 655 lines/24920 chars vs the rule's 12 lines/358; pagepos=0 + anchorkeep=0 changes no page count across 213 |  |  | 02:59 |  | running |  |
| Goog-01 | Google verification: 69_two_col_legal 35/42 -> 39/42 on the spendWideGap build, 26_text_overlap=11 is the price |  |  | 03:12 |  | running |  |
| band-01 | band sweep: footband 0.80 zeroes 69 and spares 330_cad; 26_text_overlap=11 at both 0.80 and 0.0 |  |  | 03:21 |  | running |  |
| 25_iinvisible-text-blind-01 | 25_invisible_text | invisible-text-blind | is the check blind after the 24 Nov sheet filter, and can it fail agai | 04:24 | 22:05 | landed | FINDINGS/25_iinvisible-text-blind-25NOV.md |
| invisible-text-blind-01 | 25_invisible_text | instrument | is 25_invisible_text blind after the 24 Nov sheet filter, and can it b | 05:20 |  | landed |  |
| gapcap-risk-01 | 18_displacement | engine | which documents become worse if the gap-cap + zero-gap-anchor pair shi | 05:20 |  | landed |  |
| gapcap-latch-census-01 | 04_chars_missing | engine | what does gapCapTw do to the corpus and which documents become CLEAN i | 06:20 |  | landed | FINDINGS/gapcap-latch-census-01-GAPCAP-LATCH-CENSUS-25NOV.md - 28,432 boxed chars over 61 carriers; latch 70%, cap 16%, not additive; ceiling ~8 documents, not 166 |
| spendwidegap-lookahead-01 | 18_displacement | engine | does the spendWideGap look-ahead hold doc 69 at 39/42 with 26_text_ove | 06:20 |  | landed | FINDINGS/spendwidegap-lookahead-01-REJECTED-25NOV.md - REJECTED: it refuses the spend that made 39/42; 209/213 byte-identical, 4 changed all toward more anchoring |
| 18-DISPLACEMENT-PROPOSAL-25NOV | 18_displacement | engine | where in DocxWriter does w:before / exact line height leave a gap Goog | 09:36 |  | landed | FINDINGS/18-DISPLACEMENT-PROPOSAL-25NOV.md - place() at :4149 is DEAD CODE (zero callers), so the mechanism DOCS-ROOT-CAUSES-24NOV names cannot be patched; spacing()'s pageFirst arg is always false; w:beforeLines emitted nowhere. Patch (b) = 3 ints + 1 guard at :6117-6137; patch (a) = w:pgMar w:top per page. |
| PENDING-ANSWERS-25NOV | - | ledger | for each of the pending items, is it closeable, and with what evidence | 09:36 |  | landed | 5 CLOSE / 8 STILL OPEN / 1 REFUSE of the 14; five were closed by the parent run, PENDING 16 -> 10. Also found pending.py:288 counts the MODAL engine, so the '60 documents on an older engine' line is inverted (131 are stale). |
| 18_dA-01 | 18_displacement | A | split the 14 solo documents by construct and name the smallest lever t | 10:47 | 10:45 | landed | FINDINGS/18_dA-01-18_displacement-agent-return-25NOV.md |
| 18-D-01 | 18-DISPLACEMENT-LIVE-PATH-25NOV |  |  | 10:51 |  | running |  |
| Expl-01 | Explore: 18_displacement row-pitch dither + three inconsistent w:line exact laws |  |  | 12:05 |  | landed | FINDINGS/Expl-01-18-DISPLACEMENT-ROW-PITCH-DITHER-25NOV.md |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `02:00` attempt 61 on 18_displacement -> lead
- `02:59` attempt 5 on 04_chars_missing -> lead (0/64 moved)
- `02:59` agent deployed: gap-cap patch: traced DocxWriter, produced spendWideGap() foot-band patch, applied and reverted as a no-op on 69/323/311; census: cap = 1469 chars over 23 of 35 positioned pages /  - 
- `02:59` agent deployed: zero-gap census: the latch is 655 lines/24920 chars vs the rule's 12 lines/358; pagepos=0 + anchorkeep=0 changes no page count across 213 /  - 
- `03:12` attempt 6 on 04_chars_missing -> lead (1/64 moved)
- `03:12` agent deployed: Google verification: 69_two_col_legal 35/42 -> 39/42 on the spendWideGap build, 26_text_overlap=11 is the price /  - 
- `03:21` attempt 7 on 04_chars_missing -> lead (1/64 moved)
- `03:21` agent deployed: band sweep: footband 0.80 zeroes 69 and spares 330_cad; 26_text_overlap=11 at both 0.80 and 0.0 /  - 
- `04:23` attempt 8 on 04_chars_missing -> lead
- `04:24` agent deployed: 25_invisible_text / invisible-text-blind - is the check blind after the 24 Nov sheet filter, and can it fail again
- `04:24` agent landed: 25_invisible_text / invisible-text-blind -> FINDINGS/invisible-text-blind-25_invisible_text-25NOV.md
- `05:34` attempt 3 on 25_invisible_text -> lead
- `05:45` attempt 62 on 18_displacement -> lead
- `07:47` attempt 9 on 04_chars_missing -> lead
- `08:54` attempt 10 on 04_chars_missing -> lead (0/213 moved)
- `09:25` attempt 63 on 18_displacement -> lead
- `09:52` attempt 64 on 18_displacement -> lead (0/213 moved)
- `10:45` attempt 65 on 18_displacement -> lead (0/14 moved)
- `10:47` agent deployed: 18_displacement / A - split the 14 solo documents by construct and name the smallest lever that reache
- `10:48` agent landed: 18_displacement / A -> FINDINGS/18_dA-01-18_displacement-agent-return-25NOV.md
- `10:51` agent deployed: 18-DISPLACEMENT-LIVE-PATH-25NOV /  - 
- `12:03` attempt 19 on content-present-partly-displaced -> lead (0/23 moved)
- `12:05` agent deployed: Explore: 18_displacement row-pitch dither + three inconsistent w:line exact laws /  - 
- `12:05` agent deployed: A2: none - one agent deployed this run /  - 
- `13:21` attempt 20 on content-present-partly-displaced -> lead

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
