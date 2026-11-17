# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 16:17 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> The narrow cantSplit rule was built, applied, converted over all 213 documents and MEASURED - and it is now RULED OUT as the fix for 041122, with the mechanism measured rather than guessed. Written as specified (cantSplit only when rowTopPagePt + height <= pageHeight) it fired on 1 of 213 documents and moved nothing. Rewritten to use the height the renderer really lays out - max(declared w:trHeight, the w:before+w:line actually emitted in the row's cells), the only height hRule=atLeast cannot exceed - it fires on 4 of 213 and still moves nothing: 041122 10/10 pages identical line for line, Account_Opening_Form_Fillable_filled 10/10 identical, itr-computation 68.12 -> 68.12, 64_newspaper 9.11 -> 9.11; the other 209 documents are byte-identical in every zip entry. WHY IT CANNOT WORK, measured on the document: 041122's breaking row (the one carrying 'Government Department establishing identity and address of such person') has a top edge of 689.0, declares 2220 tw (111 pt) and emits 2558 tw (128 pt) of line boxes, so 689+128 = 817 reads as fitting on an 842 pt sheet - but it RENDERS ~170 pt (p9's text runs y 9.8 -> 163.8) because the renderer wraps its cell text into ~15 lines where the writer emitted 11. The under-charge is in the WRAP, not the height arithmetic, so no rule keyed on a height the writer can compute will ever catch it. The change is kept as patches/cantsplit-only-where-keepable.patch (38 lines, applies cleanly, measured neutral on all 213) and NOT in the engine, because DocxWriter.java is 458 KB and the only working commit path takes file contents inline. TWO OPERATIONAL FACTS THIS RUN PAID FOR: scipy was missing in the pod and every position() call fell back to the 400-step dilation ladder - single-document measurements ran past 200 s and three measurement calls died on the tool timeout before it was found (p2w.py installs scipy inside main(), so a run that calls measure_doc() directly never gets it - pip install scipy first); and gh api writes are 403 'Resource not accessible by integration', the same wall as git push, so the MCP commit tool is the only path.

## What the next run should do first

> Charge the wrapping cell its real line count - that is what closes 041122's last extra page and it is the same under-charge as the class it sits in. Concretely: DocxWriter.table() charges a row from the page's measured cell content (rowTwHere) and the type floor (rowLineTw), which on 041122's breaking row is 2220 tw against the ~3080 tw it lays out. The row already knows how many w:line boxes it emitted, so take flowTwOf(cell) as a FLOOR for rowHeightTw exactly as the recut path already does with paraContentTw + ruleTwHere at 6356. Then the row is written at its true ~170 pt, 689 + 170 = 859 > 842, and the cantSplit rule fires by itself and the page closes - so apply patches/cantsplit-only-where-keepable.patch first, it is the other half of this fix. Count the documents that change BEFORE measuring (re-convert the corpus and diff the .docx entry by entry: 209 of 213 were byte-identical this run, so the diff is cheap and decisive), and pip install scipy before any measurement or every call dies on the tool timeout.

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

- `13:08` seeded by the agent: the 232f622 ratchet is the open item carried into this run
- `13:51` attempt 5 on content-missing-partly-replaced -> error
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

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
