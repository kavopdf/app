# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 03:53 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> THE RULE CLASS HAS A STRUCTURAL PRECONDITION, AND IT IS NOT MET. The largest Google class (32_stroke_lines 53 docs, 05_chars_extra 48) is rules emitted as floating w:drawing that Google drops. The pBdr fix is written (FINDINGS/RULES-PBDR-IMPLEMENTATION.md) and cannot work yet: PdfToWord.attachShapes appends shapes to page.blocks AFTER the paragraphs (PdfToWord.java:7122) and DocxWriter.pageXml writes page.blocks in list order (DocxWriter.java:1324), so when a rule is written ctx.flowY is at the foot of the page - 805.9 pt on 18_centred_heading_left_body_txtpos, against rules at 110.0 and 793.89. w:before can only move a border FORWARD, so it lands at the foot: that is the 19 Nov 'both at 807/808' measurement, and it is why 'rules drawn 2, lost 1 of 2'. Do NOT build pBdr again until shapes are written in top order among the page's blocks (flush any shape whose s.topPt <= the next block's top, before writing that block) - then the guard s.topPt > ctx.flowY starts being true and the gap is real. Also confirmed by an agent this run: there is NO third construct emitting the U+200B. The emitted XML of all 211 corpus docx contains ZERO U+200B - no Java line writes it, it is Google's own placeholder for a dropped floating drawing. The two drawings on that page are the only constructs at the foot. Do not hunt for a third.

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
| contA-06 | content-present-partly-displaced | A | after rules become w:pBdr, which construct still emits the U+200B anch | 03:54 | expected by 05:00 | running |  |
| contB-06 | content-present-partly-displaced | B | mobile-bill share5 43.87 and electricity-bill 46.85 with max_pt only 1 | 03:54 | expected by 05:00 | running |  |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `18:41` Agent B was registered but never deployed: the first subagent ran inline for 19 minutes (a scheduled run has no one to answer later, so the platform ran it in the turn), which left no room for a second. Angle B is carried forward unanswered in the handoff context: the ~0.34 pt per positioned row accumulation on bank-statement-horizontal-rules-only.
- `19:31` flowRow/flowFromBox baseline accounting: a row the page drew as one baseline but emitted as two+ paragraphs landed each continuation one hairline box lower and the pitch solver never took it back. recordBaseline() now records the baseline the flow actually reached. Screen: 3 improved (bank-statement 6.89->0.10, toc-dot-leaders 8.52->4.97, 65_two_col 4.91->1.75), 0 worse. Corpus pass running.
- `22:30` attempt 2 on content-present-partly-displaced -> kept (13/18 moved)
- `22:31` agent deployed: content-present-partly-displaced / A - bank-statement-horizontal-rules-only: which code path decides row pitch when the
- `22:31` agent deployed: content-present-partly-displaced / B - blast radius of w:vMerge across the 18 documents in the class
- `22:32` attempt 3 on content-present-partly-displaced -> kept (13/18 moved)
- `22:35` agent landed: contA-04 /  -> FINDINGS/content-present-partly-displaced-bankpitch-133100-d68d.md
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

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
