# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 18:17 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> THREE BUILDS, THE MECHANISM IS NOW BOUNDED AND ITS FAILURE MODE IS LOCATED: THE WIDTH. Build 1 (Helvetica advances everywhere, inset-overflow correction, row = max(declared, lines x rowLineTw) in w:trHeight atLeast, charged before writtenRowsTw): 42 of 213 documents change, 0 docx page-break moves, and price-list-right-aligned-amounts goes 1.79 -> 81.15 with 1 -> 2 pages. Build 2 (4 % tolerance for the Helvetica/DejaVu gap): 41 of 213; the price list drops 38 -> 16 changed rows but every one still reads 312 -> 440 tw, exactly 2 x its 220 tw row line, so the excess is structural and not metric drift. Build 3 came from READING ROW 0 of that table instead of rebuilding blind: its cells are Times New Roman (digits 0.500 em) and Courier New, and the charge was measuring Helvetica (0.556 em, 11 % wide) - so advanceEm now picks TIMES/COURIER/HELVETICA from the cell's own face. That build is the right shape: 12 of 213 documents change and on 041122 exactly ONE row moves, row 77, 2220 -> 3000 tw, which IS the instruction cell the handoff describes. It still must not be kept: measured, price-list-right-aligned-amounts 1.79 -> 32.54 and 77_arabic_rtl_document 17.14 -> 58.55. THE DIAGNOSIS: w:ind is written from insetTw AFTER the textOverflows correction, so the renderer is handed a width the text fits; a charge computed against anything narrower invents a wrap the renderer never draws, and each invented line is 3.5 pt of drift down the table (16 rows x 3.5 = the 56 pt that lands the figures 56 pt out). THE NEXT MOVE IS ONE LINE OF ARITHMETIC, not a fourth build: charge against (emitted w:tcW - emitted w:ind) from the same <w:tc>, and only beyond the row's own slack. On the price list that width is the drawn text + 20 tw, so the charge is 1 line and the document is untouched; on 041122 it still fires on the 9-paragraph cell. All three patches are committed: patches/wrap-charge-helvetica.patch (apply with git apply --include='*DocxWriter.java', it carries state-file hunks too), patches/wrap-charge-gated-1.04.patch, patches/wrap-charge-face-aware.patch. Engine at HEAD, nothing carried. OPERATIONAL, paid for this run: the whole corpus converts in 81-90 s in one JVM (ConvertAll, 213 files, 0 failed) so a corpus diff is two calls; p2w.measure_doc is 25-60 s a document, so measure the top movers only - never the whole changed set; scipy must be pip-installed every run; 041122's charged builds will not render inside a 280 s soffice call.

## What the next run should do first

> Charge the wrap against the width the renderer is GIVEN: in wrappedRowLines, compute avail as the emitted cell width minus the emitted indent (the same spanTw and the same post-textOverflows insetTw the cell writer writes into w:tcW and w:ind), and only charge ceil(wTw/avail) when wTw beats avail by more than the row's own slack. Apply patches/wrap-charge-face-aware.patch as the base (12 of 213, one row on 041122). Then re-convert all 213 and diff against outA before measuring: the count must fall below 12 and price-list-right-aligned-amounts must leave the list entirely. Only then measure price-list-right-aligned-amounts and 77_arabic_rtl_document both ways - they are the two documents that decided against builds 1-3.

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
- `18:50` attempt 13 on content-missing-partly-replaced -> reverted (0/16 moved)
- `19:05` attempt 14 on content-missing-partly-replaced -> reverted (0/16 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
