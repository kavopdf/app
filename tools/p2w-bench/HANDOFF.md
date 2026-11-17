# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 10:50 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> The class measurement now completes: soffice finishes its conversion and then never exits (both the oosplash wrapper and soffice.bin called directly; the PDF is complete on disk ~90 s in and the process is still alive 240 s later), so p2w.py now launches it in its own session, waits for the output files to settle and kills the session. That - not a hard PDF - is what kept the nine-page forms unmeasurable and the 232f622 ratchet off disk. 213/213 measured, 31 improvements, 0 regressions, RANKING.csv and STATE.json committed. Two instrument bugs found and fixed on the way: the render cache was keyed by document NAME, so a render made before an engine change scored the new engine (041122 was measured against its 10:07 render), and soffice_pdf could return a pre-existing file at the output path - that one produced a false 'fixed' result I have retracted in ATTEMPTS.json. scipy was absent again and was installed.

## What the next run should do first

> Fix the 041122 page-7 spill. The '12 twips of residue' theory is dead: the real cause is measured and it is 186 pt, not 1.2. Page 7 row 2 cell 2 is ONE paragraph (no w:br, no paras record) whose text is the six heading lines welded with SPACES by PdfToWord:8653, carrying the FIRST line's x as its inset (tcW 10636, ind 9452, so 1184 twips = 59.2 pt usable). The renderer lays that one paragraph out as TWENTY-SEVEN lines at 10 pt, y 23.4-293.4 = 270 pt, in a row whose w:trHeight declares 84.1 pt (1682 twips). The table therefore lays out ~186 pt taller than the 842 pt sheet, the last row (the Verification block) does not fit, w:cantSplit moves it to a new page, and 9 pages come out as 10. The fit guard is blind to this because spacingTw charges w:trHeight and never the wrap. Tried and ruled out this run: (a) one w:p per line of a welded cell in DocxWriter (shipped, no-op here - the cell text carries no newline), (b) joining cell lines with a newline at PdfToWord:8653 so that path fires (reverted: still 10 pages, page 7 went 99 -> 108 lines), (c) shaving w:trHeight (last run, 16746, still 10 pages). The next thing to try is the one the mechanism points at: a welded paragraph's inset must be the block's LEFTMOST line x, not the first line's - the heading's lines start at x 232-377 (centred) and 513 (right-aligned), so an inset of ~191 pt instead of 472.6 pt gives the paragraph ~340 pt of width and ~3 lines instead of 27. Measure page count with a render into an EMPTY directory - a render that can return a pre-existing file has already cost this pipeline one false fix.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| contA-01 | content-missing-partly-replaced | A | which code path decides the height of a block emitted from a PDF text  | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-A-1305.md |
| contB-01 | content-missing-partly-replaced | B | is the wrap inside a text box a renderer limit or our emitted width | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-B-1300.md |

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

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
