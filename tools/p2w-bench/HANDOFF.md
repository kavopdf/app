# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 06:53 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> A NESTED TABLE INSIDE A LAYOUT CELL LEFT THE CELL'S ANCHOR POINTING AT THE ROW'S TOP. columnPage() sets ctx.afterTablePt = rowEndPt per cell; table() writes a nested w:tbl plus a 4pt carrier as raw XML, so nothing cleared it, and the first paragraph after the nested table was placed at topPt - afterTablePt = the distance from the LAYOUT ROW's top, not the nested table's bottom. Measured with temporary stderr prints on table-inside-two-column-page: flowY was already right (232.0 = row bottom 228 + 4pt carrier) while the caption under the metrics table took w:before=2600tw (130pt) where the page drew 4.2pt, sitting 115.4pt low with the three paragraphs below it. The fix is one line: when ctx.inColumn, clear ctx.afterTablePt = -1f in table()'s row-bottom block. table-inside-two-column-page 38.11 -> 35.87, share@10 29.13 -> 9.70, max_pt 82.08 -> 21.60, p90 64.32 -> 6.24. Full corpus: 212 of 213 measured (416_many_tiny_pages EXEMPT, carried), 1 better, 211 same, 0 worse; regress.py --check PASS on both formats; Google result byte-identical to the pre-change one (42/47, same five fails).

## What the next run should do first

> content-partly-lost-and-displaced: itr-computation-with-slab-table (share5 42.33, share@10 27.40, share@20 7.85) - table rows are written at their own w:trHeight of 351/370 tw against the page's uniform 368 tw, so the page compresses by 0.5pt a row and -14.31pt by the last row (DocxWriter.java:6182 and :6271-6273; the arithmetic that yields 351 is NOT verified). The other four OPEN documents in this class are 31_times_body_arial_headings 1.04, 370_offer_letter 2.70, 14_stamp_chars_positioned_td 3.89, 75_merged_header_cell_three_columns 7.62. The rule class stays blocked pending a human.

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
| contB-07 | content-partly-lost-and-displaced | B | why two corpus documents lose ~60% of their ink at 5px: absent or move | 07:59 | landed | landed | tools/p2w-bench/FINDINGS/content-partly-lost-and-displaced-twocol-tables-0700-f1x.md |
| contA-07 | content-partly-lost | A | is the justified-line spacing fix missing from the engine or already l | 07:59 | landed | landed | tools/p2w-bench/FINDINGS/content-partly-lost-JUSTIFY-already-landed-0700-f1x.md |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

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
- `07:13` attempt 5 on content-partly-lost-and-displaced -> partial (1/6 moved)
- `07:59` attempt 6 on content-partly-lost-and-displaced -> kept (1/6 moved)
- `07:59` agent deployed: content-partly-lost-and-displaced / B - why two corpus documents lose ~60% of their ink at 5px: absent or moved
- `07:59` agent landed: contB-07 /  -> tools/p2w-bench/FINDINGS/content-partly-lost-and-displaced-twocol-tables-0700-f1x.md
- `07:59` agent deployed: content-partly-lost / A - is the justified-line spacing fix missing from the engine or already landed
- `07:59` agent landed: contA-07 /  -> tools/p2w-bench/FINDINGS/content-partly-lost-JUSTIFY-already-landed-0700-f1x.md

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
