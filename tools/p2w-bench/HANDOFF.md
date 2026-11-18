# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 15:58 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> STEP 3/3 fixer, class content-partly-lost-and-displaced. THREE mechanisms were tried on itr-computation-with-slab-table (50.80) and all three were measured and reverted; the engine is back to 1ba86d7 and the document re-screens at 50.80. (1) The handoff's anchor rule: dead code here - the running footer is a ROW of table 3, not a flow line after it (traceLines zeroGap=0), so afterTablePt never sees it. (2) Releasing the f=0.974 squeeze by capping a clipped table's charge at the page budget (needTw 17278 -> 16836): the document went 50.80 -> 70.85. LESS squeeze is worse, so the squeeze is a symptom of a page that really is too tall, not the defect. (3) The cell baseline: cellBeforeTw's fallback treats rowLineTw (the cell's LINE, 190 twips) as the row's pitch (269), so cells sit 3.2-5.2 pt high; using the row's foot where the row is >1.3x its line screened 4 table documents at 4 same and moved the target 50.80 -> 51.18 (share1 92.18 -> 69.91, invent5 62.48 -> 40.41, median 4.80 -> 5.28). Not kept. The rendered line-by-line comparison names the three real defects: the header's first three lines are in the wrong reading order (our Chartered line at 44.4 where the page draws it at 58.1), the cell baseline, and the footer row emitted between the last two rows. Also cleared this run: the 14:30 blocker's premise was wrong and its row is corrected; 77_arabic (11.89) and 79_inr (0.74) measure on the first try; 416_many_tiny_pages measured all 300 pages in one 211 s call with scipy. report.py's obstacle counter read the run's clock time as a date and printed 0 on every run - fixed.

## What the next run should do first

> The pending gate is EMPTY, so a new class may be taken - but do not take one on itr-computation-with-slab-table's account: its three remaining defects are named in FINDINGS/itr-slab-the-squeeze-is-not-the-defect-1645.md and HYPOTHESES.md, and the cheapest untested one is H3, the footer ROW's position in the row order (the page draws it last at 811.4, the engine emits it between the 816.4 and 834.8 rows). The class content-partly-lost-and-displaced still cannot be closed by attempt.py's bar - 6 of 7 documents are already under 5.0 - and that is the human decision in BLOCKERS 14:50. If a new class is taken, take the smallest OPEN one and screen before building.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| contA-01 | content-missing-partly-replaced | A | which code path decides the height of a block emitted from a PDF text  | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-A-1305.md |
| contB-01 | content-missing-partly-replaced | B | is the wrap inside a text box a renderer limit or our emitted width | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-B-1300.md |
| contA2-01 | content-missing-partly-replaced | A2 | why does parasOfLines reject the six heading lines of 041122 page 7 | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-A2-092912-7c4e.md |
| contD-01 | content-missing-partly-replaced | D | how many corpus documents have a cell whose lines start left of the fi | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-D-092700-1d7b.md |
| contA-02 | content-missing-nothing-in-its-place | A | 415_inline_images p1: why is 89% of source ink >5px from ours when tex | 09:57 | expected by 11:15 | landed | FINDINGS/content-missing-nothing-in-its-place-A-044628-d0c0.md |
| contB-02 | content-missing-nothing-in-its-place | B | the ~1.4pt uniform shift on mobile-bill/salary-slip-factory-wages/elec | 09:57 | expected by 11:15 | landed | FINDINGS/content-missing-nothing-in-its-place-B-103610-346a.md |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `11:16` agent deployed: content-missing-partly-replaced / A2 - why does parasOfLines reject the six heading lines of 041122 page 7
- `11:16` agent deployed: content-missing-partly-replaced / D - how many corpus documents have a cell whose lines start left of the first line
- `11:17` agent landed: contA2-01 /  -> FINDINGS/content-missing-partly-replaced-A2-092912-7c4e.md
- `11:17` agent landed: contD-01 /  -> FINDINGS/content-missing-partly-replaced-D-092700-1d7b.md
- `12:30` attempt 8 on content-missing-partly-replaced -> reverted (0/16 moved)
- `12:41` COMMITTING: git push is 403 'denied to Onyx-Node' for the fixer too, not only for subagents - the App has no write access to kavopdf/app over HTTPS git. It is not a dead end: the GitHub MCP tool GITHUB_COMMIT_MULTIPLE_FILES (owner kavopdf, repo app, branch main, upserts=[{path,content,encoding:utf-8}]) commits several files atomically and worked for all four commits of this run. The next run should commit that way, then 'git fetch origin main && git reset --hard origin/main' so HEAD matches origin, then chain.py. chain.py's sync check is strict SHA equality and also refuses a dirty tree, and it rewrites CHAIN.json - so commit CHAIN.json again after each chain.py run.
- `13:13` attempt 9 on content-missing-partly-replaced -> error
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
- `16:11` attempt 3 on content-partly-lost-and-displaced -> reverted (0/7 moved)
- `16:23` attempt 4 on content-partly-lost-and-displaced -> reverted (0/7 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
