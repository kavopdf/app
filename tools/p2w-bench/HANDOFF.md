# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 09:58 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> Two attempts on 18_displacement, both reverted, both carrying measured facts. (1) the table-spacer construct named by both agents is NOT the cause and forcing its gap into w:before REGRESSES Google 40/47 -> 36/47 on bank-statement-5-pages (LO unchanged 47/47). (2) the real cause is w:before being dropped at page top by Google; proven by a 5-variant probe. The corpus reproduces exactly in LibreOffice against the committed gverify-lo records (362_price_list_dense 42/42, purchase-order 46/47, mobile-bill 47/47, bank-statement-5-pages 47/47 - all MATCH), so the sandbox can measure for real.

## What the next run should do first

> 18_displacement: the page-top gap is PROVEN to be the cause (Google drops w:before there; a trHeight-exact 1x1 table row is honoured to 0.97 pt). Applying it by hand to bank-statement-5-pages fixes the displacement itself (dy median -53.8 -> +0.8) but the document goes 6 pages -> 10 with a blank after each, because (a) the break paragraph already emits a blank page 1 in Google and (b) the 55 pt gap is not charged to the page fill budget. So it is NOT a construct swap: make the gap real AND charge it to the page capacity, and fix the blank page. Engine work, needs a full corpus ratchet. See FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md, second section.

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
| contA-08 | content-present-partly-displaced | A | is the rule-as-drawing construct still in the engine and is the pBdr p | 08:58 | 09:00 | landed | FINDINGS/content-present-partly-displaced-rule-guard-was-not-the-blocker-100700-f1x.md |
| contB-08 | content-present-partly-displaced | B | how much of 18_displacement the rule construct can explain, and which  | 08:58 | 09:00 | landed | FINDINGS/content-present-partly-displaced-rule-guard-was-not-the-blocker-100700-f1x.md |
| 18_dA-01 | 18_displacement | A | Quantify the dy signature: across the Google renders that fail 18_disp | 09:59 | expected by 10:45 | running |  |
| 18_dB-01 | 18_displacement | B | Find the engine code path that decides each line's vertical position i | 09:59 | expected by 10:45 | running |  |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

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
- `08:00` attempt 7 on content-partly-lost-and-displaced -> kept (1/6 moved)
- `09:22` attempt 14 on content-present-partly-displaced -> reverted (0/23 moved)
- `09:22` agent deployed: content-present-partly-displaced / A - is the rule-as-drawing construct still in the engine and is the pBdr path presen
- `09:22` agent landed: content-present-partly-displaced / A -> FINDINGS/content-present-partly-displaced-rule-guard-was-not-the-blocker-100700-f1x.md
- `09:22` agent deployed: content-present-partly-displaced / B - how much of 18_displacement the rule construct can explain, and which displaceme
- `09:22` agent landed: content-present-partly-displaced / B -> FINDINGS/content-present-partly-displaced-rule-guard-was-not-the-blocker-100700-f1x.md
- `09:59` agent deployed: 18_displacement / A - Quantify the dy signature: across the Google renders that fail 18_displacement, 
- `09:59` agent deployed: 18_displacement / B - Find the engine code path that decides each line's vertical position in the emit
- `10:36` attempt 1 on 18_displacement -> reverted (0/107 moved)
- `10:38` attempt 2 on 18_displacement -> reverted (0/107 moved)
- `10:41` attempt 3 on 18_displacement -> reverted (0/107 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
