# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 10:50 |
| ended | 11:19 |
| how it ended | released |
| plan | - |

## The picture, in the words of the run that left it

> The size fix is IN THE TREE and measured: g.size at PdfToWord:2065 now reads the text rendering matrix scale (the size the page draws at, unrounded) instead of Tf, which is text space. Blast radius proved over all 213 corpus PDFs: exactly 4 documents change, the other 209 emit byte-identical DOCX. 411_nested_xobject_transforms 48.64 -> 0.00 share5 (rank 10 -> rank 1), 38_faux_bold 3.25 -> 0.01, 041122 98.65 -> 97.81, fillable twin 97.62 -> 97.81. RANKING.csv carries those four rows; classrow.py rewrote DEFECT-CLASSES.md. The bank forms now have correct 10 pt text and 22 pages against the source's 9 - that spill is the whole remaining problem on them. The pieces-remap root cause (PdfToWord:8753 indexes pieces with the trimmed column index while pieces is the only per-cell array the keep trim does not re-index) is proven by two agents and measured, and is NOT in the tree: it fixes the page count (9/10 -> 9/9) and invent5 (66.62 -> 0.00) but moves share5 the wrong way, because the score cannot see a spurious page. The engine diff is exactly one hunk in PdfToWord.java.

## What the next run should do first

> Land the pieces remap (parasOfLines(pieces.get(rr).get(keep.get(cc))) at PdfToWord:8753) ON TOP of the size fix now in the tree, then fix the bank forms' spill: with 10 pt text both forms emit 22 pages against 9 and page 7 is nearly blank. The mechanism to look at is the table model's row height and column width for table 18 on page 7 - the FORM NO.60 heading block is one cell whose lines are wrapped, and w:trHeight is charged but the wrap is not, so the table lays out far taller than the sheet. Measure page count with a render into an EMPTY directory (a render can return a pre-existing file at the output path). If the pair still reads worse on share@5, fix the instrument: it compares page k with page k for k <= min(pages), so a document that gains a spurious page is not penalised and one that loses it is not rewarded - pages_src and pages_ours are recorded and never scored.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| contA-01 | content-missing-partly-replaced | A | which code path decides the height of a block emitted from a PDF text  | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-A-1305.md |
| contB-01 | content-missing-partly-replaced | B | is the wrap inside a text box a renderer limit or our emitted width | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-B-1300.md |
| contC-01 | content-missing-partly-replaced | C | why does the welded cell keep its 27-line paragraph when the per-line  | 11:13 | 11:00 | landed | FINDINGS/content-missing-partly-replaced-C-044323-d5fd.md |
| contD-01 | content-missing-partly-replaced | D | blast radius of the pieces-not-remapped bug across the 213-document co | 11:13 | 11:00 | landed | FINDINGS/content-missing-partly-replaced-D-110200-a7c4.md |

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
- `11:13` attempt 7 on content-missing-partly-replaced -> reverted (0/13 moved)
- `11:13` agent deployed: content-missing-partly-replaced / C - why does the welded cell keep its 27-line paragraph when the per-line paragraph 
- `11:13` agent deployed: content-missing-partly-replaced / D - blast radius of the pieces-not-remapped bug across the 213-document corpus
- `11:13` agent landed: content-missing-partly-replaced / C -> FINDINGS/content-missing-partly-replaced-C-044323-d5fd.md
- `11:13` agent landed: content-missing-partly-replaced / D -> FINDINGS/content-missing-partly-replaced-D-110200-a7c4.md
- `11:19` attempt 1 on content-partly-lost -> partial (1/11 moved)
- `11:19` attempt 8 on content-missing-partly-replaced -> partial (1/13 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
