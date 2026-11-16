# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 14:58 |
| ended | still running |
| how it ended | - |
| plan | Close the carry-over: fix the 041122 page-7 spill on content-missing-partly-replaced (one 24-row w:tbl, rows atLeast+cantSplit, shaveToFit no-op at depth 0), then ratchet at corpus scale with RANKING.csv committed. |

## The picture, in the words of the run that left it

> The 232f622 fix is in the engine and measured on 30 class documents. It has never been ratcheted. Two nine-page bank forms cannot be converted by soffice inside the 290 s call limit, which is why the class measurement stalls - that is a tooling problem, not an engine one.

## What the next run should do first

> Fix the 041122 page spill on content-missing-partly-replaced, now localised: page 7 is ONE 24-row w:tbl (zero w:txbxContent), its rows are written w:trHeight hRule=atLeast + w:cantSplit (DocxWriter.java:6086/:6123), and the page's whole flow is that table so shaveToFit (:495-560, depth==0 w:before only) is a no-op and the page goes out 12 twips over target. Shaving w:trHeight alone does NOT work (16746, still 10 pages) because the row is laid out at content+rule; the repair must reduce the row's CONTENT height together with its trHeight. The fit guard's trigger is writtenTw > pageBudgetTw - p2w.fitreserve (default 96). Ratchet it with benchmarks/p2w.py --budget 250 then gate.py --ratchet-only.

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

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
