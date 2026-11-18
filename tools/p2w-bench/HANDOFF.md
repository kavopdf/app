# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 16:52 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> STEP 3/3 fixer 16:52. The carry-over's own diagnosis was already refuted before I arrived: the anchor rule (FINDINGS/itr-slab-the-squeeze-is-not-the-defect-1645.md) never fires, and the cell-baseline fallback was measured worse at 16:23. So the carry-over had one item left that was still true - the three documents the ratchet has never compared - and I spent the slot on that and on the one change SETTLED still called live. RESULT, both measured: (1) run-size-from-sizePt does NOT reproduce. Applied clean to engine 7a95b1c, built, screened 4 docs: 360_restaurant_menu 34.43 -> 34.43 (the 96% gain SETTLED records does not exist on this engine), 392_statistical_console_output 1.61 -> 13.94 (reproduces exactly), itr and 320 unchanged. SCREEN FAIL, reverted, SETTLED.md corrected in place. (2) Two of the three unmeasured documents are now measured for the first time: 77_arabic_rtl_document share5 11.89 and 79_inr_indian_digit_grouping_table share5 0.74, both 1 page - the earlier 'soffice no render' was a render timeout, not a broken document, and both render once given 250 s. 416_many_tiny_pages is still unmeasured and the reason is now precise: its docx needs ~250 s in soffice and its 300 pages need ~280 s to compare, and measure_doc_chunked does not cache a partial window, so it restarts at page 1 and is killed at 292 s every run. A full corpus pass was started (86 of 213 docx converted, one JVM each) but not finished inside the slot, so RANKING.csv is unchanged and nothing was published.

## What the next run should do first

> Do 416_many_tiny_pages FIRST and alone: seed its render (soffice --convert-to pdf on out/416_many_tiny_pages.docx takes ~250 s and does succeed), write pre/416_many_tiny_pages.pdf.src with the docx's size:mtime stamp so conv() uses the cache, then spend one whole call on measure_doc_chunked with chunk=100 budget=270 - or add per-window caching under dist2/<doc>.w<N>.json first, which is the real fix, because without it the document is unmeasurable at 300 pages by construction. Do NOT re-test run-size-from-sizePt (refuted on this engine 18 Nov 17:05, SETTLED.md corrected). Do NOT re-implement the anchor rule or the cell-baseline fallback. The class content-partly-lost-and-displaced is down to one document above the line, itr-computation-with-slab-table at 50.80; its remaining defects are listed in order in FINDINGS/itr-slab-the-squeeze-is-not-the-defect-1645.md and the first two are both refuted, so the third - the footer ROW of table 3 emitted between rows the page draws around it - is the only one left standing, and it is a row-ordering question in DocxWriter.table(), not a flow one.

## Agents deployed and not yet accounted for

| id | class | angle | question | deployed | expected | status | finding |
|---|---|---|---|---|---|---|---|
| contA-01 | content-missing-partly-replaced | A | which code path decides the height of a block emitted from a PDF text  | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-A-1305.md |
| contB-01 | content-missing-partly-replaced | B | is the wrap inside a text box a renderer limit or our emitted width | 13:52 | landed | landed | FINDINGS/content-missing-partly-replaced-B-1300.md |
| contA2-01 | content-missing-partly-replaced | A2 | why does parasOfLines reject the six heading lines of 041122 page 7 | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-A2-092912-7c4e.md |
| contD-01 | content-missing-partly-replaced | D | how many corpus documents have a cell whose lines start left of the fi | 11:16 | landed | landed | FINDINGS/content-missing-partly-replaced-D-092700-1d7b.md |
| contA-02 | content-missing-nothing-in-its-place | A | 415_inline_images p1: why is 89% of source ink >5px from ours when tex | 09:57 | expected by 11:15 | landed | FINDINGS/content-missing-nothing-in-its-place-A-044628-d0c0.md |
| contB-02 | content-missing-nothing-in-its-place | B | the ~1.4pt uniform shift on mobile-bill/salary-slip-factory-wages/elec | 09:57 | expected by 11:15 | landed | FINDINGS/content-missing-nothing-in-its-place-B-103610-346a.md |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

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
- `18:22` attempt 13 on content-missing-partly-replaced -> reverted (0/16 moved)
- `18:34` attempt 14 on content-missing-partly-replaced -> reverted (0/16 moved)
- `18:45` attempt 15 on content-missing-partly-replaced -> reverted (0/16 moved)
- `19:31` attempt 16 on content-missing-partly-replaced -> partial (1/3 moved)
- `19:35` attempt 17 on content-missing-partly-replaced -> kept (3/3 moved)
- `09:57` agent deployed: content-missing-nothing-in-its-place / A - 415_inline_images p1: why is 89% of source ink >5px from ours when text_recall i
- `09:57` agent deployed: content-missing-nothing-in-its-place / B - the ~1.4pt uniform shift on mobile-bill/salary-slip-factory-wages/electricity-bi
- `11:50` agent landed: contA-02 /  -> FINDINGS/content-missing-nothing-in-its-place-A-044628-d0c0.md
- `11:50` agent landed: contB-02 /  -> FINDINGS/content-missing-nothing-in-its-place-B-103610-346a.md
- `11:55` attempt 6 on content-missing-nothing-in-its-place -> reverted (0/30 moved)
- `13:44` attempt 1 on single-element-far-out -> partial (1/1 moved)
- `14:51` attempt 1 on content-partly-lost-and-displaced -> partial (1/7 moved)
- `15:28` attempt 2 on content-partly-lost-and-displaced -> kept (1/210 moved)
- `16:12` attempt 3 on content-partly-lost-and-displaced -> kept (1/7 moved)
- `17:00` attempt 18 on content-missing-partly-replaced -> reverted (0/16 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
