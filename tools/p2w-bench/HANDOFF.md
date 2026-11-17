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
| started | 09:22 |
| ended | 11:21 |
| how it ended | released |
| plan | clear carry-over: fix the 041122 page-7 welded cell inset (first line's x -> block's leftmost line x), measure with an empty render dir |

## The picture, in the words of the run that left it

> Three root causes in the table-cell paragraph path are fixed and measured across 213 documents: (1) the per-cell lines matrix 'pieces' was left in the untrimmed column space while its consumer indexed the trimmed grid, so a multi-line cell read the WRONG column's lines - the six heading paragraphs of 041122 page 7 were written into the empty cell beside them, which is why that heading appeared twice; (2) the point size was taken from the Tf operand, so 041122 - which draws everything as '/TT0 1 Tf' inside a 10x Tm - was emitted as 1214 one-point runs, microprint for the whole bank form; the size is scalingFactorY of the text rendering matrix and it is a size, not a multiplier (multiplying squared it and regressed 192 documents, measured and discarded); (3) each line's own x was computed but never set as the paragraph inset, so all six heading lines carried the first line's 472.6 pt inset in a 531.8 pt cell and wrapped in a 59 pt column. Corpus after all three: 208 unchanged, 411_nested_xobject_transforms 31.05 -> 0.00, 041122 98.65 -> 97.62 with median displacement 477.6 -> 138.24 pt, one regression 39_small_caps_letter_spacing 0.72 -> 3.78. The heading now renders in the right cell, at 10 pt, right-aligned and centred as the source draws it. STILL OPEN: 041122 renders 12 pages against 9 and page 7 is nearly blank - the page-7 table itself renders correctly on page 8, so one row is rendering far taller than its declared trHeight and cantSplit moves it. 416_many_tiny_pages is a MEASURE-ERROR in both the baseline and this run, not new.

## What the next run should do first

> 041122 page-7 spill, third attempt: the text is fixed, the row height is not. With all three paragraph-path fixes in, 041122 renders 12 pages against 9 and page 7 is nearly blank - a shaded row at the top and one rule at the bottom, with the page-7 table itself rendering correctly and close to the source on page 8. The table's declared row heights sum to 16649 twips (832 pt) against an 842 pt sheet, so one row is rendering far taller than its w:trHeight and w:cantSplit is moving it to the next page. Measure the RENDERED height of each of the 24 rows (the y of each row's bottom rule in our own render) against its declared trHeight, name the row that grows and the paragraph property that grows it - w:before, w:line exact, or a wrap. Do NOT re-derive the size bug or the pieces index: both are fixed and measured (HYPOTHESES.md, 17 Nov). Measure page count with a render into an EMPTY directory.

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

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
