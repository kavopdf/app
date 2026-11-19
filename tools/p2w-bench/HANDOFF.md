# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 18:00 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> content-present-partly-displaced (18 OPEN) is NOT one mechanism - measured on four documents: 75_merged_header welds two header columns and shifts rows by one (22.07 pt); bank-statement accumulates 0.34 pt per positioned row (source pitch 18.4, ours 18.74) to +5.77 pt by y421; 374_org_chart is -0.18 pt at the top and +4.48 pt in the bottom box row; payslip is a constant -3.45 pt in one block. The subagent's root cause is confirmed by reading the code and is in FINDINGS/content-present-partly-displaced-mergedheader-130426-4bd9.md: cells are cut from drawn rectangles, a fill-only shading band becomes a gridSpan, and spanR is computed at PdfToWord:7950 and read by nothing so no w:vMerge is ever written. Dropping fill-only rules from the Edge list (PdfToWord:1275) is REFUTED - 27.31 -> 46.58 and 2 pages, because on this page the shading band is the only rule that closes the header cells. Do not retry it.

## What the next run should do first

> Implement w:vMerge in DocxWriter's table emission from the spanR PdfToWord already computes (PdfToWord:7950 writes it, nothing reads it). Screen 75_merged_header_cell_three_columns plus the 17 other content-present-partly-displaced documents. Do not retry dropping fill-only rules from the Edge list - measured 27.31 -> 46.58.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| contA-01 | content-missing-partly-replaced | A | which code path decides the height of a block emitted from a PDF text  | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-A-1305.md |
| contB-01 | content-missing-partly-replaced | B | is the wrap inside a text box a renderer limit or our emitted width | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-B-1300.md |
| contA2-01 | content-missing-partly-replaced | A2 | why does parasOfLines reject the six heading lines of 041122 page 7 | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-A2-092912-7c4e.md |
| contD-01 | content-missing-partly-replaced | D | how many corpus documents have a cell whose lines start left of the fi | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-D-092700-1d7b.md |
| contA-02 | content-missing-nothing-in-its-place | A | 415_inline_images p1: why is 89% of source ink >5px from ours when tex | 09:57 | expected by 11:15 | landed | FINDINGS/content-missing-nothing-in-its-place-A-044628-d0c0.md |
| contB-02 | content-missing-nothing-in-its-place | B | the ~1.4pt uniform shift on mobile-bill/salary-slip-factory-wages/elec | 09:57 | expected by 11:15 | landed | FINDINGS/content-missing-nothing-in-its-place-B-103610-346a.md |
| contA-03 | content-present-partly-displaced | A | 75_merged_header_cell_three_columns: the table body is 22 pt low and e | 18:16 | expected 19:05 | running |  |
| contB-03 | content-present-partly-displaced | B | 13 of the 18 documents are within 1 pt everywhere except a few rows th | 18:16 | expected 19:05 | running |  |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `14:34` attempt 10 on content-missing-partly-replaced -> partial (2/16 moved)
- `15:36` attempt 11 on content-missing-partly-replaced -> partial (1/30 moved)
- `17:32` attempt 12 on content-missing-partly-replaced -> reverted (0/4 moved)
- `18:22` attempt 13 on content-missing-partly-replaced -> reverted (0/16 moved)
- `18:34` attempt 14 on content-missing-partly-replaced -> reverted (0/16 moved)
- `18:45` attempt 15 on content-missing-partly-replaced -> reverted (0/16 moved)
- `19:31` attempt 16 on content-missing-partly-replaced -> partial (1/3 moved)
- `19:35` attempt 17 on content-missing-partly-replaced -> kept (3/3 moved)
- `09:57` agent deployed: content-missing-nothing-in-its-place / A - 415_inline_images p1: why is 89% of source ink >5px from ours when text_recall i
- `09:57` agent deployed: content-missing-nothing-in-its-place / B - the ~1.4pt uniform shift on mobile-bill/salary-slip-factory-wages/electricity-bi
- `11:50` agent landed: contA-02 /  -> FINDINGS/content-missing-nothing-in-its-place-A-044628-d0c0.md
- `11:50` agent landed: contB-02 /  -> FINDINGS/content-missing-nothing-in-its-place-B-103610-346a.md
- `11:55` attempt 6 on content-missing-nothing-in-its-place -> reverted (0/30 moved)
- `13:44` attempt 1 on single-element-far-out -> partial (1/1 moved)
- `14:51` attempt 1 on content-partly-lost-and-displaced -> partial (1/7 moved)
- `15:28` attempt 2 on content-partly-lost-and-displaced -> kept (1/210 moved)
- `16:12` attempt 3 on content-partly-lost-and-displaced -> kept (1/7 moved)
- `17:00` attempt 18 on content-missing-partly-replaced -> reverted (0/16 moved)
- `19:07` attempt 7 on content-missing-nothing-in-its-place -> kept (22/29 moved)
- `16:58` attempt 1 on content-partly-lost -> partial (5/10 moved)
- `16:58` measured, screened, not ratcheted: the justified-line fix is a patch in patches/, not an engine change
- `18:01` 18:00 run: carry-over verified DONE - the justified-lines fix landed as 4147d54 with a full corpus ratchet (53 of 213 improved, mean 4.13, regress.py --check PASS, txt 213/213). Taking content-present-partly-displaced (18 open, most documents).
- `18:16` agent deployed: content-present-partly-displaced / A - 75_merged_header_cell_three_columns: the table body is 22 pt low and each data r
- `18:16` agent deployed: content-present-partly-displaced / B - 13 of the 18 documents are within 1 pt everywhere except a few rows that are 3-5
- `18:40` attempt 1 on content-present-partly-displaced -> reverted (0/18 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
