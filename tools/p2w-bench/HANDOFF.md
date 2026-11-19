# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 21:59 |
| ended | 22:35 |
| how it ended | released |
| plan | - |

## The picture, in the words of the run that left it

> The class file's own rows say 24 OPEN for content-present-partly-displaced (the summary table said 18 and classrow.py --write recounted it; its duplicate-header bug is fixed in this run - it inserted a second identical 'Documents measured' line on every run that found nothing to change). TWO things are settled with numbers. (1) bank-statement-horizontal-rules-only is CLEAN at 0.10 on main: 13518ff fixed the split-row before/flowY drift. The same document also has a second, deeper cause - rowTables never runs because rowGapOk's floor max(size*2.4,16) rejects every 18.4 pt row pair (PdfToWord:9701); a patch that widens it to the run's own pitch (patches/rowgapok-run-pitch.patch) measured 6.89 -> 0.14 on engine 3abfa85 with 6 other class docs unchanged, and is now SUPERSEDED and unproven on the current engine. Do not apply it on the old numbers. (2) 75_merged_header_cell_three_columns (27.31) is NOT that mechanism and is untouched by that patch: spanR is computed at PdfToWord:7950 and read by nothing, so no w:vMerge is ever written, and a glyph's row comes from the cell's top edge at 7846. Also: the engine moved under this run - 13518ff landed at 22:30 IST while the fixer slot was claimed at 21:59, which round.py's claim did not prevent; whoever owns round.py should look at that.

## What the next run should do first

> content-present-partly-displaced, 24 OPEN. Take 75_merged_header_cell_three_columns (27.31, the worst in the class): implement w:vMerge in DocxWriter's table emission from the spanR PdfToWord:7950 already computes, and bucket each glyph by its own baseline band instead of the cell's top edge (7846) - the sibling finding says both are needed and that the band test alone moves Depot to the wrong row. Do not retry dropping fill-only rules from the Edge list (27.31 -> 46.58). Do not apply patches/rowgapok-run-pitch.patch on its old numbers.

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

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

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
- `18:41` agent landed: content-present-partly-displaced / A -> tools/p2w-bench/FINDINGS/content-present-partly-displaced-mergedheader-130426-4bd9.md
- `18:41` agent landed: content-present-partly-displaced / B -> (no file)
- `18:41` Agent B was registered but never deployed: the first subagent ran inline for 19 minutes (a scheduled run has no one to answer later, so the platform ran it in the turn), which left no room for a second. Angle B is carried forward unanswered in the handoff context: the ~0.34 pt per positioned row accumulation on bank-statement-horizontal-rules-only.
- `19:31` flowRow/flowFromBox baseline accounting: a row the page drew as one baseline but emitted as two+ paragraphs landed each continuation one hairline box lower and the pitch solver never took it back. recordBaseline() now records the baseline the flow actually reached. Screen: 3 improved (bank-statement 6.89->0.10, toc-dot-leaders 8.52->4.97, 65_two_col 4.91->1.75), 0 worse. Corpus pass running.
- `22:30` attempt 2 on content-present-partly-displaced -> kept (13/18 moved)
- `22:31` agent deployed: content-present-partly-displaced / A - bank-statement-horizontal-rules-only: which code path decides row pitch when the
- `22:31` agent deployed: content-present-partly-displaced / B - blast radius of w:vMerge across the 18 documents in the class
- `22:32` attempt 3 on content-present-partly-displaced -> kept (13/18 moved)
- `22:35` agent landed: contA-04 /  -> FINDINGS/content-present-partly-displaced-bankpitch-133100-d68d.md
- `22:35` agent landed: contB-04 /  -> FINDINGS/content-present-partly-displaced-vmergescope-133908-a7c4.md
- `22:59` attempt 3 on content-present-partly-displaced -> reverted (0/24 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
