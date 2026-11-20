# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 06:20 |
| ended | 06:21 |
| how it ended | forced |
| plan | READ FINDINGS/content-present-partly-displaced-rules-are-flow-neutral-065000-f1x.md BEFORE TOUCHING THE RULE CLASS. Two handoff claims are now measured FALSE: (1) the flush-by-top precondition is a regression, not a precondition - with the border path OFF it takes bank-statement 0.10 -> 17.07 and gst-invoice 0.38 -> 15.13, because every shape moved into the flow charges ~9.6 pt; (2) the residual on 18_displacement was never the gap or the flowY bookkeeping - a carrier paragraph costs 9.6 pt in LibreOffice whatever it contains (measured four ways), which is the whole of 0.00 -> 77.01. A flow-neutral construct exists and is in FINDINGS/rules-top-border-FLOW-NEUTRAL-065000-f1x.patch: a pre-pass hands each rule to the paragraph that follows it as a w:top border, the gap becomes w:before and the rule-to-text distance becomes w:space, nothing is reordered and no paragraph is added. It measures EXACTLY baseline on all 8 documents tried (18_centred 0.00, 411 0.00, 62 0.00, bank-statement 0.10, gst-invoice 0.38, mobile-bill 1.55, 315 1.91, 64 3.46) - and places pBdr=0, because its own safety guards decline every rule it could reach. Where a border IS placed, 18_centred goes 0.00 -> 0.53. THAT is the wall and it is not an engine bug: regress.py scores share@5 on a LibreOffice render, LibreOffice draws the floating drawing exactly, and a border can never be pixel-identical - so a fix Google needs is always a small LibreOffice regression, and the brief forbids landing one. DO NOT start another rule-class attempt until a human answers: gate this class in Google (32_stroke_lines / 05_chars_extra on the Google result), declare the class out of scope, or authorise a stated tolerance. Spend the next slot on a class the gate can see. |

## The picture, in the words of the run that left it

> THE FLUSH-BY-TOP PRECONDITION IS SOLVED; THE RESIDUAL IS DISPLACEMENT, NOT THE RULE. The rule class (Google 32_stroke_lines 145 docs, 05_chars_extra 141) needs a rule written as w:pBdr, and the pBdr fix was inert because attachShapes appends shapes after the paragraphs so the flow was always at the foot. This run built the flush: DocxWriter.pageXml now emits a page's shapes in TOP ORDER among its blocks (flush any unwritten shape whose topPt <= the next Para/Table top, rest after the loop; paragraph/table order untouched). That works exactly as predicted - on 18_centred_heading_left_body_txtpos the emitted XML goes 0->2 w:pBdr and 2->0 w:drawing, both rules landing at the page's own ys 110.0 and 793.89 (the earlier finding's 805.9-pt flow problem is gone), and 32_stroke_lines flips FAIL->PASS in Google. It is REVERTED because it makes 18_displacement fail where it passed - LibreOffice 42/42 -> 41/42 on a document that was clean, Google 18_displacement PASS->FAIL - and the brief says a fix for the largest class that breaks the second-largest is not a fix. The exact diff is FINDINGS/rules-flush-by-top-WORKS-DISPLACES-055000-f1x.patch; re-apply it with 'git apply' and fix the flow. THREE THINGS ARE RULED OUT and must not be retried: the below=flowBoxPt*(1-LINE_BASE) term (flowBoxPt is 0 when the rule is flushed, it contributes nothing), the kind!=0 path guard (removing it changed nothing), and the gap arithmetic (border 1 lands within 0.5 pt of its rule). The residual is the READER'S POSITION AFTER the carrier paragraph, not the gap before it: try emitting the border with ctx.flowY UNCHANGED and compare 18_displacement against the ctx.flowY=s.topPt version - one build and one Google round trip. SECOND BLOCKER, larger than it looks: 315_gazette_notification is three-column and takes columnPage(), which returns BEFORE the emit loop, so its two horizontal rules (y 59.6 and 77.8) are written at the foot (flowY 751.87), both declined, and the document measures pBdr 0 / drawings 5 and 40/42 unchanged in Google. columnPage emits three lists (before, cells[c], after) with plain emitBlock loops at DocxWriter.java:2005, :2146 and :2214; the horizontal rules land in 'after'. A pageXml-only fix cannot reach ANY multi-column document, and the corpus has many. That is the next structural question and it is separate from this one.

## What the next run should do first

> READ FINDINGS/content-present-partly-displaced-rules-are-flow-neutral-065000-f1x.md BEFORE TOUCHING THE RULE CLASS. Two handoff claims are now measured FALSE: (1) the flush-by-top precondition is a regression, not a precondition - with the border path OFF it takes bank-statement 0.10 -> 17.07 and gst-invoice 0.38 -> 15.13, because every shape moved into the flow charges ~9.6 pt; (2) the residual on 18_displacement was never the gap or the flowY bookkeeping - a carrier paragraph costs 9.6 pt in LibreOffice whatever it contains (measured four ways), which is the whole of 0.00 -> 77.01. A flow-neutral construct exists and is in FINDINGS/rules-top-border-FLOW-NEUTRAL-065000-f1x.patch: a pre-pass hands each rule to the paragraph that follows it as a w:top border, the gap becomes w:before and the rule-to-text distance becomes w:space, nothing is reordered and no paragraph is added. It measures EXACTLY baseline on all 8 documents tried (18_centred 0.00, 411 0.00, 62 0.00, bank-statement 0.10, gst-invoice 0.38, mobile-bill 1.55, 315 1.91, 64 3.46) - and places pBdr=0, because its own safety guards decline every rule it could reach. Where a border IS placed, 18_centred goes 0.00 -> 0.53. THAT is the wall and it is not an engine bug: regress.py scores share@5 on a LibreOffice render, LibreOffice draws the floating drawing exactly, and a border can never be pixel-identical - so a fix Google needs is always a small LibreOffice regression, and the brief forbids landing one. DO NOT start another rule-class attempt until a human answers: gate this class in Google (32_stroke_lines / 05_chars_extra on the Google result), declare the class out of scope, or authorise a stated tolerance. Spend the next slot on a class the gate can see.

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

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `22:35` agent landed: contB-04 /  -> FINDINGS/content-present-partly-displaced-vmergescope-133908-a7c4.md
- `22:59` attempt 3 on content-present-partly-displaced -> reverted (0/24 moved)
- `23:00` attempt 4 on content-present-partly-displaced -> kept (13/18 moved)
- `23:00` ATTEMPTS.json attempt 4 on content-present-partly-displaced is a RATCHET STAMP for attempt 2 (the 22:30 recordBaseline split-row fix, 13/18 moved, corpus ratcheted at d129d46), not a second fix - attempt.py has no way to stamp a ratchet without appending an attempt, so a later report.py will read '2 kept'. One fix was kept this round on this class.
- `23:56` attempt 5 on content-present-partly-displaced -> error (0/18 moved)
- `00:24` attempt 6 on content-present-partly-displaced -> kept (2/18 moved)
- `00:46` agent deployed: content-present-partly-displaced / A - can RuleCollector carry the PDF paint operator so a shading fill stops acting as
- `00:46` agent deployed: content-present-partly-displaced / B - what does check 65_table_span_down assert and why does 75_merged_header_cell_thr
- `02:25` attempt 7 on content-present-partly-displaced -> kept (1/23 moved)
- `03:40` attempt 8 on content-present-partly-displaced -> kept (1/23 moved)
- `03:40` agent landed: contA-05 /  -> FINDINGS/content-present-partly-displaced-newspaper-033000-a7d1.md
- `03:40` agent landed: contB-05 /  -> FINDINGS/content-present-partly-displaced-mergedheader-vmerge-192600-c3f1.md
- `03:41` One fix landed: recutColumnBands takes the row top as the minimum over the columns (64_newspaper 9.11 -> 3.46, corpus 212/212 with nothing worse, .txt 213 unchanged, gate PASS, commits 4e61dfd and 97e2e1f). Two things for the next run: (1) the class queue was stale by one run - the carry-over named 75_merged_header_cell_three_columns at 27.31 when the previous run had already taken it to 7.62 and reclassified it to content-partly-lost-and-displaced; always re-read RANKING.csv before believing the carry-over. (2) The corpus pass in p2w.py cannot finish inside a sandbox command and does not resume - it re-converts from zero every call because it measures ROOT/repo, not the working tree. screen.py --docs with the whole RANKING list DOES resume and measures the working tree including the uncommitted diff; 212 of 213 took 9 calls. Build RANKING.csv from screen-out/dist/*.json. Two documents block a batch: Account_Opening_Form_Fillable_filled and one-page-rotated-180-degrees must be measured alone or they eat the whole budget. The .txt half re-scores from screen-out/*.txt copied into /scratch/work/p2w/out after deleting txt/RESTAMP-TXT.jsonl.
- `03:42` Slot released with --force: one agent was deployed, not two. A subagent in a scheduled run runs synchronously inside the turn (background=true still blocks), and the one deployed spent 26 minutes instrumenting the newspaper page - it found the mechanism that became the fix, but a second would have eaten the ratchet budget. The gate's agent rule counts registrations, and this run's agent was never registered with --agent-add before it was deployed; do that first next time.
- `03:54` agent deployed: content-present-partly-displaced / A - after rules become w:pBdr, which construct still emits the U+200B anchor at y~79
- `03:54` agent deployed: content-present-partly-displaced / B - mobile-bill share5 43.87 and electricity-bill 46.85 with max_pt only 1.55/1.33: 
- `04:03` attempt 9 on content-present-partly-displaced -> error (0/23 moved)
- `04:03` health.py: _age() now takes the last COMMIT time of the path, not mtime (every cron clones fresh, so every mtime was the clone's, and the report read 0.0 h for all five stages while --stalled could never turn red). _attempts_recent() now parses the ledger's IST stamps with calendar.timegm - IST_OFFSET instead of time.mktime, which read them as pod-local UTC and put every attempt 5.5 h in the future: the watchdog's '6 attempt(s) in 3 h' was 2. Verified: ages 0.0 h -> 0.4 h on all five stages, attempts 6 -> 2. Both blockers closed in BLOCKERS.md.
- `04:04` agent landed: contA-06 /  -> FINDINGS/content-present-partly-displaced-zerowidth-040040-7c1e.md
- `04:13` classrow.py fixed: load_rank() now reads max_pt and the row writer emits (share5, max_pt) into the columns the header names. Every row the tool ever wrote carried share1 under the share5 heading and share5 under max_pt - mobile-bill read 'share@5 43.87, max_pt 1.55', which is impossible arithmetic and cost an agent its whole budget proving the page was fine. Also: the clean-row branch discarded the c[2]=prob correction with out.append(line), so no FIXED-and-clean row ever got its numbers or its problem name repaired; both branches now write the row, and the measured class is preserved on those rows. Verified: 212 of 212 rows now match RANKING.csv on both columns, 0 status changes, 0 document changes, class summary counts identical (12/1 6/16 6/4 6/0 23/0 7/1 130). The queue's real shape: content-present-partly-displaced 23 open at share@5 1.0-4.0 with max_pt 13-17, not the sub-2pt figures the table used to show.
- `04:13` agent landed: contB-06 /  -> FINDINGS/content-present-partly-displaced-subpx-041118-ed1d.md
- `05:11` attempt 10 on content-present-partly-displaced -> partial (2/23 moved)
- `05:17` attempt 11 on content-present-partly-displaced -> reverted (0/23 moved)
- `05:53` attempt 12 on content-present-partly-displaced -> reverted (0/23 moved)
- `06:20` attempt 13 on content-present-partly-displaced -> reverted (0/23 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
