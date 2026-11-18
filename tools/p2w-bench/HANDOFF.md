# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 18:00 |
| ended | 19:08 |
| how it ended | released |
| plan | - |

## The picture, in the words of the run that left it

> The per-row separator stroke is kept: DocxWriter.table() now emits a per-cell w:tcBorders/w:bottom where a table's interior rule is heavier or darker than the table's single insideH. Full corpus 212 measured: 33 better, 179 same, 0 worse. content-missing-nothing-in-its-place went 22 of 29 better, best drop 17.36 (salary-slip-factory-wages 18.09->0.73).

## What the next run should do first

> Take the next class, content-partly-lost (11 open). The class-wide screen now covers the whole corpus in about 30 minutes across 6 calls via screen.py --docs with the full RANKING.csv document list - p2w.py --budget does NOT resume and cannot finish a corpus pass inside the 300 s cap, so use screen.py --docs. Do not retry run-size-from-sizePt-not-Tf, the anchor rule, the cell-baseline fallback, or the row separator stroke - the last is now implemented.

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
- `16:12` attempt 3 on content-partly-lost-and-displaced -> kept (1/7 moved)
- `17:00` attempt 18 on content-missing-partly-replaced -> reverted (0/16 moved)
- `19:07` attempt 7 on content-missing-nothing-in-its-place -> kept (22/29 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
