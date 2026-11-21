# P2W Fixer - Run Report

**21 Nov 2026 · slot 15:58 → running IST · 1h 43m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 17:00 | **partial** | 1/5 | uprightIfPageIsUpsideDown patch landed: one-page-rotated-180-degrees t02_position FAIL->PASS, 213 of 213 .txt converted+scored, 190 clean (was 189), 0 newly failing. .docx proved byte-identical on all |
| 17:25 | **reverted** | 0/5 | The 180deg guard, built and measured on all 213 documents (213/213 .docx word/document.xml byte-identical, 212/213 .txt identical, one-page-rotated-180-degrees t02_position FAIL->PASS, t02_position 5- |
| 17:39 | **reverted** | 0/145 | pBdr rule carrier REFUTED by measurement, not by argument: patched engine, 12 class documents, 172 source rules counted with check 32's own detector. 68 rules became w:pBdr, but 48 of the 68 land more |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **190** (89.2%) |
| Failing at least one check | **23** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `32_sA-01` | Does the pBdr replacement in FINDINGS/RULES-PBDR-IMP | 15:59 | 12:10 | 101 min |
| `t02_B-01` | The 180deg uprightIfPageIsUpsideDown patch (FINDINGS | 15:59 | 12:09 | 100 min |
| `t08_B-01` | which code path decides the .txt line order, and wha | 17:39 | 12:09 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 15:58 → running · 1h 43m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 40 |
| Longest silence | **22.7 min** — from 16:37:48, after `HEAD rebuilt; converting all 213 to out-head for a byte-for-byte docx ` |
| Silences over 2 min | 11 |
| Obstacles | 2 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **Two fixers ran the same slot and duplicated 65 minutes of work.** This run claimed at 16:16 (`round.py --cla |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **22 min** | `#####` |
| measure or build - a conversion, screen or compile writes no beacon | **1h 09m** | `###############` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **6 min** | `#` |
| other - not attributed to a tool | **3 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Judge the t08 verifier question before touching the engine: is t08_line_order measuring line order or drawing order? FINDINGS/t08_line_order-DRAWING-ORDER-1740.md has the numbers (10 of 10 rows clear when only our own line sequence is put into drawing order). The agent's proposed one-line sort of _src_pages is NOT obviously right - it would compare sorted-vs-sorted. Decide with a falsification: construct a .txt whose lines are deliberately swapped in y and confirm t08 still fires after the change. Then take t01_word_accuracy's .docx half or 32_stroke_lines' cell-border construct.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

## Why the commit needed a tool fixed, not just a patch

`regress.py` refused the commit twice, and both refusals were a hole in `scope.py`, not in the patch. `scope.py` attributes a change by method name, and `PdfToWord.uprightIfPageIsUpsideDown` was not in its table, so it fell back to "change outside a known method, so both formats" and demanded a `.docx` re-measurement the change cannot move. The 20 Nov note in `regress.py` records the same wall stopping the per-table-column `.txt` fix, "and that is why 46 documents have failed the same `.txt` checks for a month". The entry is in the table now, with the proof in its comment. A second hole followed it: once the engine commit landed, `scope.py` saw a clean tree, could attribute nothing, and refused the state commit - the relay fixed that one in `7795c60` while this run was measuring.

## The proof, and what would have proved it wrong

The previous run measured 140 of 213 `.docx` files and named its own gap: the 73 it did not convert. All 213 are converted now, both ways, same corpus, same engine build.

| | compared | identical | different |
|:--|--:|--:|--:|
| `.docx` `word/document.xml`, HEAD vs patched | 213 | **213** | **0** |
| `.txt`, HEAD vs patched | 213 | 212 | 1 - `one-page-rotated-180-degrees`, 8986 to 9312 bytes |

A byte-identical output cannot score differently, so the `.docx` table did not need re-scoring - and that is the only reason it is legitimate to leave the `.docx` column where it was.

## What the pBdr refutation bought

`ctx.flowY = s.topPt` does not save the construct: shapes are written after the page's paragraphs (`PdfToWord.java:7122`), so rules above the flow end get `w:before="0"` and pile up - `bank-statement` writes its first line at y = -9.1 pt, off-page. 102 of the 172 rules are vertical strokes that `ruleAsBorder` refuses, so the patch is a no-op on two documents. It also needed three `(int)` casts the proposal omitted, because `TWIPS_PER_PT` is a double. The next `32_stroke_lines` slot has a measured alternative: `DocxWriter.java:6420` already writes `<w:tcBorders><w:bottom>` and can carry the vertical rules.

## The t08 finding is not to be applied as written

It proposes one line in `verify_txt.py`'s `_src_pages` that sorts the source lines by `(y, x)`. That is editing the measurement to make the number improve, and it would make `t08` compare sorted-against-sorted. The measurement behind it is real: reordering only our own lines into drawing order clears 10 of the 10 rows, so the engine's geometric order and the check's drawing order genuinely disagree. Whether the check or the engine is wrong is the next run's question and it needs a falsification, not an edit.

## Two runs, one slot

The 16:15 fixer fire found this run's claim and claimed anyway at 16:16, so two runs worked the same tree for 65 minutes. Both produced real work - the relay's `7795c60` is what made the state commit landable - but a duplicated slot is a slot spent twice. The claim was not stale at 16:15: it had been refreshed by a heartbeat minutes earlier. That is the wall to look at next: `--heartbeat` refreshes `fixer_started` whether or not the calling run holds the claim, so a second run's first command pushes the first run's staleness clock forward and then walks past it.
