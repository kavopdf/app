# HANDOFF - read this before you pick a class

Written by handoff.py on every claim, every attempt, every agent and every release.
It is never more than one attempt old. If the claim in ROUND.json is older than the
stale limit, the run that wrote this died without releasing - treat its plan as
unfinished work, not as a result.

## The run that wrote this

| | |
|---|---|
| started | 17:59 |
| ended | still running |
| how it ended | - |
| plan | - |

## The picture, in the words of the run that left it

> 47_margins taken on the rotation (classpick rotated off 18_displacement: 3 attempts, 0 moved). The class is DEFINED: 47_margins is verify_google.py:3960-4170 - per page, horizontally only: (a) the page's left ink anchor must be within 3.0 pt of the source's, (b) matched run pairs are unregistered at |d|>2.0 pt with budget max(2, round(5% n)). w:pgMar is 0 on all four sides, a hard constant at DocxWriter.java:2268-2269, and is NOT the mechanism - Google places ink at pgMar+ind. The lever is flowFromBox (DocxWriter.java:4159-4188, :4391-4392): left-aligned lines pin their ink, centred and right lines delegate their left edge to the renderer's text width. Two constructs measured, both reverted, both diffs in FINDINGS/47_margins-MECHANISM-133500-f2.md. The one to carry forward is the space-led indent: strip the leading ASCII spaces and emit inkX-b.x as w:ind w:left (needs Box.inkX = visibleX in PdfToWord). It is position-neutral in the declared face, moves nothing worse on any of the 13, and drives the Google counter to zero on 392/380/383 under the substitution proxy - but reaches flowFromBox in only 3 of 13, and a Google-only mechanism is flat in a LibreOffice measurement by construction, so the corpus pass cannot see it. Next: extend it to the cell emitter, where 40/77/78's space-led lines live, then run benchmarks/gate.py --budget 250 in its own call and confirm RANKING.csv's mtime moved.

## What the next run should do first

> 47_margins: re-measure the class against a fresh render, not the tables - 392_statistical_console_output already reads 0.06 and passes all 42 checks on this engine while RANKING.csv says 1.61 and both gverify tables say 47_margins FAIL, so the class is at most 25 documents. Then pull the thread FINDINGS/47_margins-REACH-140500.md leaves open: 360_restaurant_menu's body column was 12 pt left (source 52, render 40) and 9 runs are still 11.9 pt out; the leading-space indent and the centred-line constructs are both capped under the 25% bar and must not be retried.

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
| contA-06 | content-present-partly-displaced | A | after rules become w:pBdr, which construct still emits the U+200B anch | 03:54 | expected by 05:00 | landed | FINDINGS/content-present-partly-displaced-zerowidth-040040-7c1e.md |
| contB-06 | content-present-partly-displaced | B | mobile-bill share5 43.87 and electricity-bill 46.85 with max_pt only 1 | 03:54 | expected by 05:00 | landed | FINDINGS/content-present-partly-displaced-subpx-041118-ed1d.md |
| contB-07 | content-partly-lost-and-displaced | B | why two corpus documents lose ~60% of their ink at 5px: absent or move | 07:59 | landed | landed | tools/p2w-bench/FINDINGS/content-partly-lost-and-displaced-twocol-tables-0700-f1x.md |
| contA-07 | content-partly-lost | A | is the justified-line spacing fix missing from the engine or already l | 07:59 | landed | landed | tools/p2w-bench/FINDINGS/content-partly-lost-JUSTIFY-already-landed-0700-f1x.md |
| contA-08 | content-present-partly-displaced | A | is the rule-as-drawing construct still in the engine and is the pBdr p | 08:58 | 09:00 | landed | FINDINGS/content-present-partly-displaced-rule-guard-was-not-the-blocker-100700-f1x.md |
| contB-08 | content-present-partly-displaced | B | how much of 18_displacement the rule construct can explain, and which  | 08:58 | 09:00 | landed | FINDINGS/content-present-partly-displaced-rule-guard-was-not-the-blocker-100700-f1x.md |
| 18_dA-01 | 18_displacement | A | Quantify the dy signature: across the Google renders that fail 18_disp | 09:59 | expected by 10:45 | landed | tools/p2w-bench/FINDINGS/18_displacement-dy-shape-101323-4fa7.md |
| 18_dB-01 | 18_displacement | B | Find the engine code path that decides each line's vertical position i | 09:59 | expected by 10:45 | landed | tools/p2w-bench/FINDINGS/18_displacement-engine-topoffset-101951-cda8.md |
| t13_A-01 | t13_amount_columns | A | which writer path emits the misaligned amounts, proven by build | 12:00 | 11:05 | landed | FINDINGS/t13-writer-path-110501-f3de.md |
| t13_B-01 | t13_amount_columns | B | census of the 18 documents: table path vs paragraph path | 12:00 | 11:06 | landed |  |
| 47_mA-01-01 | 47_margins | A-01 | what 47_margins actually compares, and where the page margin is emitte | 13:36 | 13:00 | landed | FINDINGS/47_margins-MECHANISM-133500-f2.md |
| 47_mB-01-01 | 47_margins | B-01 | the space-led indent construct on 47_margins | 13:36 | 13:00 | landed | FINDINGS/47_margins-MECHANISM-133500-f2.md |
| 47_mA-01 | 47_margins | A | which code path emits a table-cell line, and how a cell's horizontal p | 14:02 | landed | landed | tools/p2w-bench/FINDINGS/47_margins-CELLPATH-A-150000.md |
| 47_mB-01 | 47_margins | B | why 40_devanagari_shaping_font and 76_devanagari_table score 10.48 and | 14:02 | landed | landed | tools/p2w-bench/FINDINGS/47_margins-DIAGNOSE40-B-150000.md |
| t13_A-02 | t13_amount_columns | A | per-document map of every offending t13 line: source column x, leading | 17:09 | six remaining docs diagnosed line by line | landed | FINDINGS/t13-page-end-column-KEPT-172000.md |
| t13_B-02 | t13_amount_columns | B | reach of a per-page end column across the whole .txt corpus, before an | 17:09 | which of 213 improve and which regress | landed | FINDINGS/t13-page-end-column-KEPT-172000.md |

A finding lands as a file in tools/p2w-bench/FINDINGS/. Read it even if the agent
that wrote it is long gone - that is why it writes a file instead of replying.

## What happened, most recent last

- `13:34` attempt 4 on 47_margins -> partial (3/13 moved)
- `13:34` attempt 5 on 47_margins -> reverted (0/13 moved)
- `13:34` two attempts on 47_margins, both reverted, both measured; the mechanism is now in FINDINGS and the class is no longer a mystery
- `13:36` agent deployed: 47_margins / A-01 - what 47_margins actually compares, and where the page margin is emitted
- `13:36` agent deployed: 47_margins / B-01 - the space-led indent construct on 47_margins
- `13:36` agent landed: 47_margins / A-01 -> FINDINGS/47_margins-MECHANISM-133500-f2.md
- `13:36` agent landed: 47_margins / B-01 -> FINDINGS/47_margins-MECHANISM-133500-f2.md
- `14:35` attempt 6 on 47_margins -> reverted (0/26 moved)
- `15:07` attempt 7 on 47_margins -> reverted (0/26 moved)
- `15:08` attempt 8 on 47_margins -> partial (2/26 moved)
- `15:12` agent deployed: 47_margins / A - which code path emits a table-cell line, and how a cell's horizontal position is
- `15:12` agent deployed: 47_margins / B - why 40_devanagari_shaping_font and 76_devanagari_table score 10.48 and 7.91 - is
- `15:12` agent landed: 47_mA-01 /  -> tools/p2w-bench/FINDINGS/47_margins-CELLPATH-A-150000.md
- `15:12` agent landed: 47_mB-01 /  -> tools/p2w-bench/FINDINGS/47_margins-DIAGNOSE40-B-150000.md
- `16:14` attempt 4 on t13_amount_columns -> reverted (0/26 moved)
- `17:06` attempt 5 on t13_amount_columns -> kept (5/6 moved)
- `17:08` attempt 6 on t13_amount_columns -> reverted (0/1 moved)
- `17:09` agent deployed: t13_amount_columns / A - per-document map of every offending t13 line: source column x, leading spaces, e
- `17:09` agent deployed: t13_amount_columns / B - reach of a per-page end column across the whole .txt corpus, before and after
- `17:09` agent landed: t13_amount_columns / A -> FINDINGS/t13-page-end-column-KEPT-172000.md
- `17:09` agent landed: t13_amount_columns / B -> FINDINGS/t13-page-end-column-KEPT-172000.md
- `18:00` attempt 7 on t13_amount_columns -> reverted (0/6 moved)
- `19:24` attempt 8 on t13_amount_columns -> kept
- `19:27` attempt 1 on t12_word_invention -> reverted (0/12 moved)
- `19:29` attempt 2 on t12_word_invention -> reverted (0/12 moved)

## Where the rest of the state lives

| file | what it answers |
|---|---|
| ROUND.json | phase, round, who holds which slot |
| ATTEMPTS.json | every attempt on every class, with its outcome |
| HYPOTHESES.md | which theories are confirmed, ruled out, untested |
| FINDINGS/ | what subagents proved, including ones that outlived their run |
| BLOCKERS.md | walls a run could not clear, and what is needed |
| RUN-LOG.md | the timeline, one line per event |
