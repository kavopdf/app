# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 10:50 |
| ended | 12:22 |
| how it ended | released |
| plan | - |

## The picture, in the words of the run that left it

> The 041122 spill is a TEXT BOX, not a table cell - the 16 Nov finding, not this run's. This run re-derived the font-size bug because patches/ was never committed (it did not exist in the repository at all) and HYPOTHESES.md pointed at patches/run-size-from-sizePt-not-Tf.patch. That patch is now real and committed, with a patches/README.md saying how to apply it. Read HYPOTHESES.md before forming a theory - three of this run's hours went on work the file already records as done.

## What the next run should do first

> Apply patches/run-size-from-sizePt-not-Tf.patch, rebuild, then fix the page spill in DocxWriter's ANCHOR path, not the ruled table: 041122 carries 378 wps:txbx text boxes, the 'Annexure-1' heading exists twice (x 513.9-571.5, 58 pt wide, and x 573.1-584.0, 11 pt wide), and the 20-line wrap lives inside a box whose width was taken from a table column. With the patch applied the document emits 10 pages against the source's 9, and its pages 1-6 already read 1.6-48 %@5, so the spill is the whole remaining gap. Measure page count, not %@5, until pages_ours == pages_src: the metric is saturated at ~99 % on this document while it is 1 pt and cannot see a layout change.

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
- `12:20` attempt 7 on content-missing-partly-replaced -> reverted (0/16 moved)
- `12:20` attempt 8 on content-missing-partly-replaced -> reverted (0/16 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
