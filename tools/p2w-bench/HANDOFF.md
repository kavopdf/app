# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 10:51 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> t13_amount_columns (.txt half) is now 6 documents, not 18. Two constructs landed, both in TxtWriter only: (1) appendTable ends every numeric cell at ONE end column per table column instead of each cell's own right edge, which the 'if (startCol > col)' guard always discarded because the 0.6em ruler over-estimates a 7pt numeric token by a column; (2) paraEndSnap merges a page's numeric paragraph end columns that sit one apart. The remaining 6 need the table and paragraph paths POOLED onto one per-page ruler - measured by an agent at 15 of 18 - plus one doc whose split is two columns wide. The gate itself was the reason the .txt half could never land: engine_fingerprint hashes every .java so a TxtWriter edit always staled the docx stamp and regress.py refused; scope.py now knows TxtWriter.appendTable/appendPara are txt and regress.py does not stamp-check a format scope.py proved out of scope.

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
| 18_dA-01 | 18_displacement | A | Quantify the dy signature: across the Google renders that fail 18_disp | 09:59 | expected by 10:45 | landed | tools/p2w-bench/FINDINGS/18_displacement-dy-shape-101323-4fa7.md |
| 18_dB-01 | 18_displacement | B | Find the engine code path that decides each line's vertical position i | 09:59 | expected by 10:45 | landed | tools/p2w-bench/FINDINGS/18_displacement-engine-topoffset-101951-cda8.md |
| t13_A-01 | t13_amount_columns | A | which writer path emits the misaligned amounts, proven by build | 12:00 | 11:05 | landed | FINDINGS/t13-writer-path-110501-f3de.md |
| t13_B-01 | t13_amount_columns | B | census of the 18 documents: table path vs paragraph path | 12:00 | 11:06 | landed |  |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

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
- `10:42` agent landed: 18_dA-01 /  -> tools/p2w-bench/FINDINGS/18_displacement-dy-shape-101323-4fa7.md
- `10:42` agent landed: 18_dB-01 /  -> tools/p2w-bench/FINDINGS/18_displacement-engine-topoffset-101951-cda8.md
- `10:52` attempt 1 on t13_amount_columns -> error
- `11:51` attempt 2 on t13_amount_columns -> kept (10/18 moved)
- `11:59` attempt 3 on t13_amount_columns -> kept (2/18 moved)
- `12:00` agent deployed: t13_amount_columns / A - which writer path emits the misaligned amounts, proven by build
- `12:00` agent deployed: t13_amount_columns / B - census of the 18 documents: table path vs paragraph path
- `12:00` agent landed: t13_amount_columns / A -> FINDINGS/t13-writer-path-110501-f3de.md
- `12:00` agent landed: t13_amount_columns / B -> (no file)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
