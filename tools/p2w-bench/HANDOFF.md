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
| started | 15:05 |
| ended | 17:03 |
| how it ended | forced |
| plan | - |

## The picture, in the words of the run that left it

> t12 is fixed: the unit is the character, not the token. txt corpus 199 -> 202 of 213 clean, 5 newly clean, 0 of 213 newly failing, landed as 23d0b1db. The screen.py 'soffice hang' is closed as a finding: it is the scipy fallback in edt(), not soffice - with scipy present a 23-document screen finishes in 190 s. Two instrument defects found and NOT fixed: _ensure_scipy() spends up to 220 s of a 280 s budget and only warns; p2w.py:1112 imports scipy.ndimage inside a try/except so colour_share/tone_share become None and coloured_px 0 on a scipy-less pod, silently blinding every colour or tone judgement.

## What the next run should do first

> READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 15 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. FIRST ATTEMPT: add the drawnByAppearance(apDrawn, ...) guard to the annotationRuns loop in PdfToWord.pageText() (~line 956) - its sibling loop at line 947 already has it. Measured on one document: 600_reviewed_invoice_with_annotations goes 20 tokens/83 chars -> 7 tokens/30 chars, paragraphs 14 -> 13. Needs the 213-document docx ratchet before it lands. SECOND: the (Authorised signatory) duplication on 041122-Account_Opening_Form and Account_Opening_Form_Fillable_filled is a table-row/paragraph overlap, a different construct, and clearing it closes the last 2 txt documents that are not the annotation one. THIRD: _ensure_scipy() should refuse rather than warn, and p2w.py:1112 must not swallow the scipy.ndimage import - see FINDINGS/SCREEN-HANG-IS-SCIPY-NOT-SOFFICE-25NOV.md.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
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
| instA-01 | instrument | A | the soffice prerender wedge and the scipy prerequisite - landed 7c7ab1 | 15:12 | 14:19 | landed | FINDINGS/RANKING-TXT-TWO-FILES-25NOV.md |
| scresoffice prerender-01 | screen-hang | soffice prerender | does soffice block screen.py, and where exactly | 17:03 | a screen that finishes inside its budget | landed | tools/p2w-bench/FINDINGS/SCREEN-HANG-IS-SCIPY-NOT-SOFFICE-25NOV.md |
| t12_txt instrument-01 | t12_word_invention | txt instrument | is t12's unit the word or the character | 17:03 | which txt documents become clean | landed | tools/p2w-bench/FINDINGS/T12-UNIT-IS-CHARACTER-25NOV.md |
| SCREsoffice prerender-01 | SCREEN-HANG-IS-SCIPY-NOT-SOFFICE | soffice prerender | does soffice block screen.py, and where exactly | 17:05 | a screen that finishes inside its budget | landed | tools/p2w-bench/FINDINGS/SCREEN-HANG-IS-SCIPY-NOT-SOFFICE-25NOV.md |
| T12-txt instrument-01 | T12-UNIT-IS-CHARACTER | txt instrument | is t12's unit the word or the character | 17:05 | which txt documents become clean | landed | tools/p2w-bench/FINDINGS/T12-UNIT-IS-CHARACTER-25NOV.md |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `09:52` attempt 64 on 18_displacement -> lead (0/213 moved)
- `10:45` attempt 65 on 18_displacement -> lead (0/14 moved)
- `10:47` agent deployed: 18_displacement / A - split the 14 solo documents by construct and name the smallest lever that reache
- `10:48` agent landed: 18_displacement / A -> FINDINGS/18_dA-01-18_displacement-agent-return-25NOV.md
- `10:51` agent deployed: 18-DISPLACEMENT-LIVE-PATH-25NOV /  - 
- `12:03` attempt 19 on content-present-partly-displaced -> lead (0/23 moved)
- `12:05` agent deployed: Explore: 18_displacement row-pitch dither + three inconsistent w:line exact laws /  - 
- `12:05` agent deployed: A2: none - one agent deployed this run /  - 
- `14:01` attempt 67 on 18_displacement -> lead
- `15:06` attempt 23 on content-present-partly-displaced -> kept
- `15:06` attempt 24 on content-present-partly-displaced -> kept
- `15:12` agent deployed: instrument / A - the soffice prerender wedge and the scipy prerequisite - landed 7c7ab124 and 738
- `15:12` agent landed: instrument / A -> FINDINGS/RANKING-TXT-TWO-FILES-25NOV.md
- `15:30` attempt 25 on content-present-partly-displaced -> kept
- `15:30` attempt 26 on content-present-partly-displaced -> kept
- `17:02` attempt 6 on t12_word_invention -> kept (5/8 moved)
- `17:03` agent deployed: screen-hang / soffice prerender - does soffice block screen.py, and where exactly
- `17:03` agent deployed: t12_word_invention / txt instrument - is t12's unit the word or the character
- `17:03` agent landed: screen-hang / soffice prerender -> tools/p2w-bench/FINDINGS/SCREEN-HANG-IS-SCIPY-NOT-SOFFICE-25NOV.md
- `17:03` agent landed: t12_word_invention / txt instrument -> tools/p2w-bench/FINDINGS/T12-UNIT-IS-CHARACTER-25NOV.md
- `17:05` agent deployed: SCREEN-HANG-IS-SCIPY-NOT-SOFFICE / soffice prerender - does soffice block screen.py, and where exactly
- `17:05` agent deployed: T12-UNIT-IS-CHARACTER / txt instrument - is t12's unit the word or the character
- `17:05` agent landed: SCREEN-HANG-IS-SCIPY-NOT-SOFFICE / soffice prerender -> tools/p2w-bench/FINDINGS/SCREEN-HANG-IS-SCIPY-NOT-SOFFICE-25NOV.md
- `17:05` agent landed: T12-UNIT-IS-CHARACTER / txt instrument -> tools/p2w-bench/FINDINGS/T12-UNIT-IS-CHARACTER-25NOV.md
- `17:05` attempt 7 on t12_word_invention -> kept (5/8 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
