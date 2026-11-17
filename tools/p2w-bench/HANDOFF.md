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

> THREE ANGLES MEASURED AND CLOSED, AND THE THIRD ONE SAYS THE FIX IS BIGGER THAN A SLOT-SIZED CHANGE. (1) The cantSplit rule cannot close 041122: built as specified it fires on 1 of 213 and moves nothing; rebuilt on the height the renderer really lays out it fires on 4 of 213 and still moves nothing (209 of 213 byte-identical, the 4 measured: 041122 10/10 pages identical, Account_Opening_Form_Fillable_filled 10/10 identical, itr-computation 68.12 -> 68.12, 64_newspaper 9.11 -> 9.11). (2) Dropping cantSplit on a wrap-aware height makes 041122 WORSE, 10 -> 11 pages: with hRule=atLeast a split row leaves a fragment the renderer charges again. (3) Charging the row its wrapped height in w:trHeight - the mechanism that actually explains the gap - does grow the row it was aimed at (the instruction page's content runs to 711.5 instead of 683.6) but the document is STILL 11 pages, because rows that used to fit are now charged more, p7 falls from 91 lines to 90 and a one-line p8 appears. So it is a cascade, not a one-row fix. THE MEASURED FACTS: the breaking row is one cell 11000 tw (550 pt) wide holding nine paragraphs at w:line 240 tw and w:sz 20, 828 characters; the writer charges 9 x 240 + rule = 2220 tw (111 pt); the render spends ~156 pt because four of those paragraphs wrap into two lines in DejaVu where they fit one line in the source face. A Helvetica advance-width helper on the standard-14 metrics PDFBox ships is the right metric and it compiles and runs. The engine is at HEAD - nothing from any of these three experiments is in the tree; the neutral cantSplit change is carried as patches/cantsplit-only-where-keepable.patch (38 lines, applies cleanly) and not in the engine only because DocxWriter.java is 458 KB and the one working commit path takes file contents inline. OPERATIONAL FACTS THIS RUN PAID FOR: scipy was missing, so every position() call fell back to the 400-step dilation ladder - single-document measurements ran past 200 s and three calls died on the tool timeout before it was found (p2w.py installs scipy inside main(), so a run calling measure_doc() directly never gets it: pip install scipy first). gh api writes are 403 'Resource not accessible by integration', the same wall as git push - GITHUB_COMMIT_MULTIPLE_FILES is the only write path. round.py --release-fixer REFUSES while pending.py lists work, and pending.py's carry-over item IS HANDOFF.json's own 'next', so a run cannot release cleanly by design: it ends when the platform ends it.

## What the next run should do first

> Do the corpus diff before anything else on the wrap charge - it touches every ruled table, not four documents. Apply the wrap charge that is already written and measured: a Helvetica advance-width helper (PDType1Font.HELVETICA / HELVETICA_BOLD, standard-14 metrics PDFBox ships, within a few per cent of DejaVu Sans), each cell's text split on its own paragraph breaks, lines = ceil(textWidth / (spanTw - insetTw)), and the row charged max(declared rowHeightTw, wrapped lines x rowLineTw) written into w:trHeight (hRule=atLeast makes it a floor the renderer will not go below). That version compiles, runs, and does what it should on the row it targets - 041122's instruction page content moves from 683.6 to 711.5 - but it re-lays out EVERY ruled table, so on 041122 alone it goes 10 -> 11 pages because a row that used to fit is now charged more and p7 loses a line. So: re-convert all 213 documents with it, diff the .docx entry by entry and write down HOW MANY change before measuring a single one - the answer decides whether this fits in a slot at all. If it is most of the corpus, that is a ratchet job for a run with the whole hour, not a fixer slot; say so in BLOCKERS.md rather than half-measuring it. Do NOT pair it with dropping cantSplit - that combination was measured at 11 pages too. pip install scipy before any measurement or every call dies on the tool timeout.

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
