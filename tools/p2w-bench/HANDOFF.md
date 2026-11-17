# HANDOFF - read this before you pick a class

## NEEDS A HUMAN - no future run can clear these

A run tried, could not, and it was not a system limit. Every run after this one
will hit the same wall until one of these is changed by a person.

| # | what it is | what was tried | what must change | when |
|---|---|---|---|---|
| 0 | subagents cannot commit their findings to kavopdf/app (git push 403 'denied to Onyx-Node'; | retried once each, verified 403 not 422, verified repo exists and my o | grant the GitHub App write access to kavopdf/app, or give subagent san | 11:23 |

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 12:04 |
| ended | 12:39 |
| how it ended | released |
| plan | - |

## The picture, in the words of the run that left it

> 041122's spill is now measured and its cause is named. The pending item asked for rendered row heights against declared trHeight: r2 +9.0, r19 +8.5, r20 +20.7, r23 +108.9, every other row exact. They grow by WHOLE LINES, not by a paragraph property - r23 has 20 source lines and rendered 26, its w:before sums to 24 pt and its w:line is exact 240 tw = the source's own 12 pt pitch. The extra lines are wraps: the docx names Effra, the renderer substitutes Noto Sans (16.9 % wider on the same string), and the cell gives the source's longest line 0.5 % of slack. Ruled out by measurement: w:before, w:line, w:cantSplit, the sizePt bug, the pieces index. Also disproved: our page 7 is NOT table 17 - it is page 6's page furniture (heading bar, footer rule, page number at y -7.5) whose anchor paragraphs were pushed off page 6; table 17 begins on our page 8. Second finding: building a metric clone of the source's own font from the PDF's /Widths arrays (installed to ~/.fonts) takes r2 to its declared 84.1 and r23 from 340.4 to 256.4 - the wrap theory confirmed - but the document still renders 12 pages, because the engine's own line box (240 tw = 12.0 pt) is taller than the pitch its own row height assumes (231.5 pt for 20 lines = 11.6 pt each). That 0.4 pt a line is the engine-side residual and it is the next thing to change. Nothing was committed to the engine this run: the font work is a harness measurement, not a fix, and a half-working font install would have moved the corpus without a mechanism.

## What the next run should do first

> Make the CELL line box carry the source's measured pitch in twips instead of a rounded em multiple: DocxWriter writes w:line=240 for a 10 pt cell line while the row the engine itself declares is 4630 tw (231.5 pt) for 20 lines, i.e. 11.6 pt a line. Find the pitch used by the pieces/cell path (DocxWriter.java:8121 documents a 1.25 em cell factor; the emitted value is 1.2 em), make it the measured pitch rounded to the nearest twip, rebuild, and check r23's rendered bottom rule against 231.5 on 041122 before anything else. Then re-check the three separate overflows one at a time: our p7 (page 6's anchored furniture - anchor the page's shapes to content that STARTS on that page, not to a trailing empty paragraph), our p9 (r23), our p11. Do not re-derive the wrap: HYPOTHESES.md has the numbers, and the font clone recipe if the renderer is to be made font-faithful.

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

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
