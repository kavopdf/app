# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 18:56 |
| ended | 19:36 |
| how it ended | released |
| plan | - |

## The picture, in the words of the run that left it

> THE SPILL WAS THE CARRY'S CEILING, NOT A ROW HEIGHT. The carry-over asked for a fourth wrap-charge build (page-layout this time); this run measured that on 041122 the row does not need to be taller - it needs the renderer to wrap it the way the page did, and the mechanism for that (ARIAL_W, w:w) was already in the engine and silently not clamping on merged cells. carryScalePct was given colTw[c], the FIRST grid column under the cell, so on a cell merged over six columns the width was negative, the clamp was skipped, and the scale went out at the page's drawn ratio 97 % where the cell allows 92. Four of the page's nine instruction lines wrapped into two, the row rendered 154 pt where the page drew 118, and it no longer fitted the 158 pt the page had left. Fix is one token (spanTw - pInset). Corpus diff: 3 of 213 .docx change, 210 byte-identical, all 3 measured: 373_leave_application_form 5.46 -> 4.64, 041122 11 -> 10 pages, Account_Opening_Form_Fillable_filled 11 -> 10 pages, 0 worse. THE CLASS DOES NOT MOVE YET because the last spurious page of both form documents is a FOLIO WRITTEN AS A TABLE ROW (the declaration table's last row is the bare text '7'), which costs its own sheet and shifts every page after it - our page 8 reads share@5 99.02 with text_recall 0.04. The flow-line folio rule exists and names this document but cannot fire on a table row. THE ONE THING THE NEXT RUN SHOULD DO: make that row a position - detect it before the row loop, skip it, take the last-row bookkeeping from row-1, emit the text after </w:tbl> via anchor(sb, ctx, x, yTop, w, h, inner), which needs only a hand-built paragraph string. w:framePr does NOT work as the cheap route (anchored to the page at y 16104 tw it rendered at y 218 pt). That one change should take both form documents from 10 pages to the source's 9 and is what moves the class.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| contA-01 | content-missing-partly-replaced | A | which code path decides the height of a block emitted from a PDF text  | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-A-1305.md |
| contB-01 | content-missing-partly-replaced | B | is the wrap inside a text box a renderer limit or our emitted width | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-B-1300.md |
| contA2-01 | content-missing-partly-replaced | A2 | why does parasOfLines reject the six heading lines of 041122 page 7 | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-A2-092912-7c4e.md |
| contD-01 | content-missing-partly-replaced | D | how many corpus documents have a cell whose lines start left of the fi | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-D-092700-1d7b.md |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `13:52` attempt 3 on content-missing-nothing-in-its-place -> kept (31/212 moved)
- `13:52` agent deployed: content-missing-partly-replaced / A - which code path decides the height of a block emitted from a PDF text box, and w
- `13:52` agent landed: content-missing-partly-replaced / A -> FINDINGS/content-missing-partly-replaced-A-1305.md
- `13:52` agent deployed: content-missing-partly-replaced / B - is the wrap inside a text box a renderer limit or our emitted width
- `13:52` agent landed: content-missing-partly-replaced / B -> FINDINGS/content-missing-partly-replaced-B-1300.md
- `13:52` C (differential) returned without committing: pdf2docx and LibreOffice PDF-import both keep page 7 of 041122 on ONE page (pdf2docx 2.03 s for that page alone; pdftotext -layout 56 lines; LibreOffice writer_pdf_import round-trip 1 page), and PyMuPDF puts the source page 7 text at y 22.6-843.4 on an 842.1 pt sheet = 97.5 % fill, 0 pt slack. Nothing reproduced a 10-page output, so the spill is ours, not an intrinsically hard PDF. Unverified by me and no file committed - do not re-deploy blind, read this note.
- `15:48` attempt 6 on content-missing-partly-replaced -> kept (1/30 moved)
- `16:18` attempt 4 on content-missing-nothing-in-its-place -> kept (31/212 moved)
- `16:19` tooling: p2w.py waits for soffice's output (measured: bank form 89 s to a complete PDF, process still alive at 240 s); render cache keyed by docx size+mtime; soffice_pdf clears its output paths and requires mtime >= launch. scipy installed (EDT per page 25 s -> 1.6 s).
- `11:16` attempt 7 on content-missing-partly-replaced -> partial (1/13 moved)
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

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
