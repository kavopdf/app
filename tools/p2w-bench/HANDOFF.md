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
| started | 23:49 |
| ended | 02:01 |
| how it ended | forced |
| plan | - |

## The picture, in the words of the run that left it

> 04_chars_missing, PROVEN IN GOOGLE. spendWideGap() + -Dp2w.pagepos=0 -Dp2w.anchorkeep=0 -Dp2w.zganchor=false takes 69_two_col_legal_numbered_clauses 36 boxes/1358 chars -> 0/0 and 35/42 -> 39/42 (04, 45, 13, 44, 17, 10_font_sizes, 38_list_markers all pass). -Dp2w.footband=0.80 is the only value that zeroes 69 AND leaves 330_cad exactly as HEAD; 0.85 leaves 7 boxes, 0.70 spends in the drawing sheet. But 26_text_overlap is render=11 at BOTH band 0.80 and band 0.0, so the band cannot separate safe gaps from unsafe ones - the missing guard is a look-ahead. Engine reverted, nothing committed to it.

## What the next run should do first

> READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 20 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 20 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 19 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 19 item(s) you can close - run pending.py and take them in its order before the class below. Implement the look-ahead in spendWideGap: spend the gap only when no line remaining on this page targets a baseline below this one. Keep -Dp2w.footband=0.80. Target: 39/42 on 69 with 26_text_overlap back to 0, 330_cad unchanged. Then the corpus pass + ratchet. Do not work gapCapTw (1469 chars) - the latch (24920 chars) is the multiplier. The 47 04-failing docs with <200 boxed chars are stamps and need a check-side rule, not a writer change.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| 18_dA-03 | 18_displacement | A | audit the pending gate: which of the 21 closable items are still true | 02:35 | 03:05 | landed | PENDING-AUDIT.md |
| 18_dB-01 | 18_displacement | B | table block-top gap and per-row height in DocxWriter | 02:35 | 03:10 | landed | 18_displacement-STEP-IS-THE-UNSPENDABLE-SPACER-0323.md |
| 18_dA-04 | 18_displacement | A | what is settled, refuted and left as a patch on this class | 04:38 | 10 min | landed | FINDINGS/18_displacement-STEP-IS-THE-UNSPENDABLE-SPACER-0323.md (memo returned in-run; 13 refuted leads, spacer-guard .patch committed but not applied) |
| 18_dB-02 | 18_displacement | B | if the table-top step were removed, which documents become CLEAN | 04:38 | 10 min | landed | step-removal alone reaches 4 documents, all already 42/42 in benchmarks/gverify - the class ceiling is 14, not 40 |
| 18_drowheight-prepass-01 | 18_displacement | rowheight-prepass | produce a minimal compilable two-pass emit for the atLeast trHeight th | 06:34 | a unified diff that applies and compiles, plus the catch that an all-equal test skips the target document | landed | FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch |
| 18_drowpitch-census-01 | 18_displacement | rowpitch-census | census the table row pitch of every corpus PDF and classify uniform-fr | 06:34 | a CSV and a count per class, so the guard's population is measured rather than assumed | landed | no corpus in its sandbox; it built and validated the census tool against four synthetic PDFs with known pitch and reported zero documents rather than inventing numbers. The census was run here on the 211 real .docx instead: 85 documents under guard A, 54 under guard B. |
| A1 | 25_invisible_text | check-definition | what does 25_invisible_text compare, and which construct makes 48 docu | 07:03 | the check's operands and a named Java site, so a fix could be attempted | landed | the check stopped at the FIRST fill under a run's corner. A Google export opens with a page-sized white rect and rasterises our bands into images, so white type on an orange band matched the sheet. This run's fix; 5 documents went 42/42. |
| A2 | 18_displacement | row-height-law | what law does Google use to lay a table row's height, and what LO-inva | 07:22 | a law fitted to the committed Google numbers, and one falsifiable change | landed | row = 0.75*round((max(trHeight,content)+rule)/0.75): trHeight is a quantised floor, not a length. 362 is unruled, so it does not ramp +0.75/row - the carry-over's 21.75 pt is ruled-table arithmetic. The LO-invariant change is DocxWriter:6468 declaring the row one rule short; it must be tested on a ruled document, not 362. |
| 18_dA-05 | 18_displacement | A | is the page-height guard why no table-top spacer is ever spent on the  | 08:20 | 08:05 | landed | 18_displacement-FULL-PASS-DOES-NOT-FIT-A-SLOT-0650-fixer.md |
| 60_tB-01 | 60_text_column_right_edge | B | is 60 or 18 reading the paper instead of the defect - the 25_invisible | 08:20 | 08:05 | landed | FINDINGS/60_text_column_right_edge-VERDICT-MIXED-1115-fixer.md |
| 60_tB-02 | 60_text_column_right_edge | B | is 60 or 18 reading the paper - the 25_invisible_text precedent | 12:28 | 11:19 | landed | FINDINGS/60_text_column_right_edge-VERDICT-MIXED-1115-fixer.md |
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

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `14:00` agent deployed: conversion cost /  - 
- `14:00` agent deployed: txt discrepancy /  - 
- `14:00` agent deployed: 18_displacement / A - where does the 11 s/doc conversion go, and the smallest change that makes --forc
- `14:00` agent deployed: 18_displacement / B - why do RANKING-TXT.csv and the report disagree by 50 documents
- `15:36` attempt 56 on 18_displacement -> lead
- `16:46` attempt 57 on 18_displacement -> lead
- `18:27` agent deployed: 60edge / 60_text_column_right_edge - A - is the right edge the engine's or the face's
- `18:27` agent deployed: pc23 / 00_page_count - B - what is on the extra page of the 23 refusals
- `18:28` attempt 8 on 00_page_count -> lead (0/23 moved)
- `18:30` attempt 9 on 00_page_count -> lead (0/23 moved)
- `18:34` attempt 5 on 60_text_column_right_edge -> lead (0/5 moved)
- `19:53` attempt 3 on 04_chars_missing -> lead
- `20:50` attempt 4 on 04_chars_missing -> lead (0/26 moved)
- `22:34` agent deployed: anchored-box patch design: six ctx.positioned sites, one emitter, class-free rule, CLEAN set, falsifiers /  - 
- `22:34` agent deployed: clean-count audit: all 36 clean documents were offered 42 checks and never saw 62-66 /  - 
- `22:39` attempt 58 on 18_displacement -> lead
- `01:09` attempt 59 on 18_displacement -> lead
- `02:00` attempt 61 on 18_displacement -> lead
- `02:59` attempt 5 on 04_chars_missing -> lead (0/64 moved)
- `02:59` agent deployed: gap-cap patch: traced DocxWriter, produced spendWideGap() foot-band patch, applied and reverted as a no-op on 69/323/311; census: cap = 1469 chars over 23 of 35 positioned pages /  - 
- `02:59` agent deployed: zero-gap census: the latch is 655 lines/24920 chars vs the rule's 12 lines/358; pagepos=0 + anchorkeep=0 changes no page count across 213 /  - 
- `03:12` attempt 6 on 04_chars_missing -> lead (1/64 moved)
- `03:12` agent deployed: Google verification: 69_two_col_legal 35/42 -> 39/42 on the spendWideGap build, 26_text_overlap=11 is the price /  - 
- `03:21` attempt 7 on 04_chars_missing -> lead (1/64 moved)
- `03:21` agent deployed: band sweep: footband 0.80 zeroes 69 and spares 330_cad; 26_text_overlap=11 at both 0.80 and 0.0 /  - 

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
