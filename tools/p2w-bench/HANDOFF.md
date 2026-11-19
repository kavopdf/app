# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 01:52 |
| ended | 03:42 |
| how it ended | forced |
| plan | - |

## The picture, in the words of the run that left it

> 64_newspaper_uneven_columns_ad_boxes is a PLACEMENT defect, not a loss: text_recall 100.0, chars_missing 0, dx 0.0, dy 1.0, share5 9.11. An Explore agent instrumented it: the page reaches the model as a band-major ruled grid and PdfToWord.recutColumnBands (PdfToWord.java:8476) re-cuts it to one row of one cell per column. That row's top edge was taken from the FIRST non-empty column only (a 'break' in the loop, colTop = max over that one column), so the column row got column 1's box top, 122.77 pt, while the classifieds column starts at 112.4 pt. DocxWriter places each cell from the shared row edge and clamps w:before at zero, so nothing can pull a cell up: the whole classifieds column (heading, three ad boxes, last line) landed 10-11 pt low. That is the 9.11% of ink. Change: colTop is now the MINIMUM over all columns (each lower column gets its own w:before), measured on a scratch copy at share5 9.11 -> 3.46, max_pt 11.04 -> 6.72, text_recall 100.0, 1 page. recutColumnBands fires on exactly one document in the corpus (the agent scanned 81-213 individually plus the 11 column-layout documents; 1-80 not reliably scanned), so this moves one document, not a class - and a 5.65-point drop is above the 5.0 line attempt.py uses for a one-document keep. Do not retry: absolute positioning, dropping fill-only rules from the Edge list (27.31 -> 46.58), patches/rowgapok-run-pitch.patch, PATCH-t13-table-row-per-line.patch (101 worse, t04_structure is a line-count check).

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| contA-01 | content-missing-partly-replaced | A | which code path decides the height of a block emitted from a PDF text  | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-A-1305.md |
| contB-01 | content-missing-partly-replaced | B | is the wrap inside a text box a renderer limit or our emitted width | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-B-1300.md |
| contA2-01 | content-missing-partly-replaced | A2 | why does parasOfLines reject the six heading lines of 041122 page 7 | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-A2-092912-7c4e.md |
| contD-01 | content-missing-partly-replaced | D | how many corpus documents have a cell whose lines start left of the fi | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-D-092700-1d7b.md |
| contA-02 | content-missing-nothing-in-its-place | A | 415_inline_images p1: why is 89% of source ink >5px from ours when tex | 09:57 | expected by 11:15 | landed | FINDINGS/content-missing-nothing-in-its-place-A-044628-d0c0.md |
| contB-02 | content-missing-nothing-in-its-place | B | the ~1.4pt uniform shift on mobile-bill/salary-slip-factory-wages/elec | 09:57 | expected by 11:15 | landed | FINDINGS/content-missing-nothing-in-its-place-B-103610-346a.md |
| contA-03 | content-present-partly-displaced | A | 75_merged_header_cell_three_columns: the table body is 22 pt low and e | 18:16 | expected 19:05 | landed | tools/p2w-bench/FINDINGS/content-present-partly-displaced-mergedheader-130426-4bd9.md |
| contB-03 | content-present-partly-displaced | B | 13 of the 18 documents are within 1 pt everywhere except a few rows th | 18:16 | expected 19:05 | landed |  |
| contA-04 | content-present-partly-displaced | A | bank-statement-horizontal-rules-only: which code path decides row pitc | 22:31 | expected by 19:30 | landed | FINDINGS/content-present-partly-displaced-bankpitch-133100-d68d.md |
| contB-04 | content-present-partly-displaced | B | blast radius of w:vMerge across the 18 documents in the class | 22:31 | expected by 19:30 | landed | FINDINGS/content-present-partly-displaced-vmergescope-133908-a7c4.md |
| contA-05 | content-present-partly-displaced | A | can RuleCollector carry the PDF paint operator so a shading fill stops | 00:46 | 00:37 | landed | FINDINGS/content-present-partly-displaced-newspaper-033000-a7d1.md |
| contB-05 | content-present-partly-displaced | B | what does check 65_table_span_down assert and why does 75_merged_heade | 00:46 | 00:41 | landed | FINDINGS/content-present-partly-displaced-mergedheader-vmerge-192600-c3f1.md |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `18:16` agent deployed: content-present-partly-displaced / B - 13 of the 18 documents are within 1 pt everywhere except a few rows that are 3-5
- `18:40` attempt 1 on content-present-partly-displaced -> reverted (0/18 moved)
- `18:41` agent landed: content-present-partly-displaced / A -> tools/p2w-bench/FINDINGS/content-present-partly-displaced-mergedheader-130426-4bd9.md
- `18:41` agent landed: content-present-partly-displaced / B -> (no file)
- `18:41` Agent B was registered but never deployed: the first subagent ran inline for 19 minutes (a scheduled run has no one to answer later, so the platform ran it in the turn), which left no room for a second. Angle B is carried forward unanswered in the handoff context: the ~0.34 pt per positioned row accumulation on bank-statement-horizontal-rules-only.
- `19:31` flowRow/flowFromBox baseline accounting: a row the page drew as one baseline but emitted as two+ paragraphs landed each continuation one hairline box lower and the pitch solver never took it back. recordBaseline() now records the baseline the flow actually reached. Screen: 3 improved (bank-statement 6.89->0.10, toc-dot-leaders 8.52->4.97, 65_two_col 4.91->1.75), 0 worse. Corpus pass running.
- `22:30` attempt 2 on content-present-partly-displaced -> kept (13/18 moved)
- `22:31` agent deployed: content-present-partly-displaced / A - bank-statement-horizontal-rules-only: which code path decides row pitch when the
- `22:31` agent deployed: content-present-partly-displaced / B - blast radius of w:vMerge across the 18 documents in the class
- `22:32` attempt 3 on content-present-partly-displaced -> kept (13/18 moved)
- `22:35` agent landed: contA-04 /  -> FINDINGS/content-present-partly-displaced-bankpitch-133100-d68d.md
- `22:35` agent landed: contB-04 /  -> FINDINGS/content-present-partly-displaced-vmergescope-133908-a7c4.md
- `22:59` attempt 3 on content-present-partly-displaced -> reverted (0/24 moved)
- `23:00` attempt 4 on content-present-partly-displaced -> kept (13/18 moved)
- `23:00` ATTEMPTS.json attempt 4 on content-present-partly-displaced is a RATCHET STAMP for attempt 2 (the 22:30 recordBaseline split-row fix, 13/18 moved, corpus ratcheted at d129d46), not a second fix - attempt.py has no way to stamp a ratchet without appending an attempt, so a later report.py will read '2 kept'. One fix was kept this round on this class.
- `23:56` attempt 5 on content-present-partly-displaced -> error (0/18 moved)
- `00:24` attempt 6 on content-present-partly-displaced -> kept (2/18 moved)
- `00:46` agent deployed: content-present-partly-displaced / A - can RuleCollector carry the PDF paint operator so a shading fill stops acting as
- `00:46` agent deployed: content-present-partly-displaced / B - what does check 65_table_span_down assert and why does 75_merged_header_cell_thr
- `02:25` attempt 7 on content-present-partly-displaced -> kept (1/23 moved)
- `03:40` attempt 8 on content-present-partly-displaced -> kept (1/23 moved)
- `03:40` agent landed: contA-05 /  -> FINDINGS/content-present-partly-displaced-newspaper-033000-a7d1.md
- `03:40` agent landed: contB-05 /  -> FINDINGS/content-present-partly-displaced-mergedheader-vmerge-192600-c3f1.md
- `03:41` One fix landed: recutColumnBands takes the row top as the minimum over the columns (64_newspaper 9.11 -> 3.46, corpus 212/212 with nothing worse, .txt 213 unchanged, gate PASS, commits 4e61dfd and 97e2e1f). Two things for the next run: (1) the class queue was stale by one run - the carry-over named 75_merged_header_cell_three_columns at 27.31 when the previous run had already taken it to 7.62 and reclassified it to content-partly-lost-and-displaced; always re-read RANKING.csv before believing the carry-over. (2) The corpus pass in p2w.py cannot finish inside a sandbox command and does not resume - it re-converts from zero every call because it measures ROOT/repo, not the working tree. screen.py --docs with the whole RANKING list DOES resume and measures the working tree including the uncommitted diff; 212 of 213 took 9 calls. Build RANKING.csv from screen-out/dist/*.json. Two documents block a batch: Account_Opening_Form_Fillable_filled and one-page-rotated-180-degrees must be measured alone or they eat the whole budget. The .txt half re-scores from screen-out/*.txt copied into /scratch/work/p2w/out after deleting txt/RESTAMP-TXT.jsonl.
- `03:42` Slot released with --force: one agent was deployed, not two. A subagent in a scheduled run runs synchronously inside the turn (background=true still blocks), and the one deployed spent 26 minutes instrumenting the newspaper page - it found the mechanism that became the fix, but a second would have eaten the ratchet budget. The gate's agent rule counts registrations, and this run's agent was never registered with --agent-add before it was deployed; do that first next time.

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
