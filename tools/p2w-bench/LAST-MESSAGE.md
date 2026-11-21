# P2W Fixer - Run Report

**21 Nov 2026 · slot 15:58 → 17:44 IST · 1h 45m**

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
| Slot window | 15:58 → 17:44 · 1h 45m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 44 |
| Longest silence | **22.7 min** — from 16:37:48, after `HEAD rebuilt; converting all 213 to out-head for a byte-for-byte docx ` |
| Silences over 2 min | 11 |
| Obstacles | 2 cleared · 2 parked, with the evidence to re-open them |
| Still a wall | `regress.py --check` refuses EVERY commit: the docx stamp is `6c6cf642e13b7ed2` while the tree's docx fingerpr |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **22 min** | `#####` |
| measure or build - a conversion, screen or compile writes no beacon | **1h 09m** | `##############` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **8 min** | `##` |
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

## What actually landed

Commit `462353f`: the `uprightIfPageIsUpsideDown` patch, `.txt`-only by measurement. `one-page-rotated-180-degrees` goes `t02\_position` FAIL to PASS, the `.txt` table goes 189 to **190 clean of 213**, 0 newly failing, and `RANKING-TXT.csv` differs by exactly one row. The `.docx` column is untouched because it does not need to move: HEAD against patched, all 213 documents converted both ways, **213 of 213** `word/document.xml` byte-identical and 212 of 213 `.txt` identical, the one difference being the document the patch is for. The previous run measured 140 and named the 73 it had not; those 73 are measured now.

The commit needed a tool fixed as well as a patch. `regress.py` refused it twice because `scope.py` attributes a change by method name, did not know `PdfToWord.uprightIfPageIsUpsideDown`, and fell back to "both formats". The 20 Nov note in `regress.py` records that same wall stopping the per-table-column `.txt` fix, "and that is why 46 documents have failed the same `.txt` checks for a month". The entry is in the table now with the proof in its comment.

## Three tools that said one thing and did another

- **`round.py --release-fixer`** refused with "If you genuinely must ship it unmeasured: --force" and then ignored `--force`, because the engine branch had no `and not force`. Fixed, and proved with the release that followed.
- **`round.py --heartbeat`** re-stamped `fixer_started` on every beat, so a run that held the slot 2h 37m released as "5 minute(s)" and its claim age meant nothing. Fixed: the beat now writes only `fixer_last_beat` and `fixer_doing_since`, which `claim()` already reads. Proved by setting the claim to ten minutes old, running the beat, and watching the age stay at 10.0 while `last_beat` went to 0.0.
- **`regress.py --only txt`** prints "docx: out of scope - scope.py proved this change cannot move it" even when the scope was forced by the flag and `scope.py` proved nothing. **Not fixed** - left standing, recorded, because the sentence is only a lie in the `--only` case and the fix is a wording change that should not ride along with a measurement.

## The pBdr carrier is refuted - do not retry it

The handoff said to land it first. Twelve class documents, 172 source rules counted with check 32's own detector: 68 rules did become `w:pBdr`, but 48 of the 68 land more than 24 pt from the source rule and LibreOffice gets **worse on 8 of the 12** (32\_stroke lost 0 to 52 across the sample; `bank-statement` 0 to 32, `gst-invoice` 0 to 11). `ctx.flowY = s.topPt` does not save it: shapes are written after the page's paragraphs, so rules above the flow end get `w:before="0"` and pile up - `bank-statement` writes its first line at y = -9.1 pt, off-page. 102 of the 172 rules are vertical strokes `ruleAsBorder` refuses, so the patch is a no-op on two documents. It also needed three `(int)` casts the proposal omitted, because `TWIPS_PER_PT` is a double. The measured alternative for the next slot: `DocxWriter.java:6420` already writes `<w:tcBorders><w:bottom>` and can carry the vertical rules.

## The t08 finding is not to be applied as written

It proposes one line in `verify_txt.py`'s `_src_pages` that sorts the source lines by `(y, x)`. That is editing the measurement to make the number improve, and it would make `t08` compare sorted against sorted. The measurement behind it is real and worth acting on - reordering only our own lines into drawing order clears 10 of the 10 rows - so the engine's geometric order and the check's drawing order genuinely disagree. Which one is wrong is the next run's question, and it needs a falsification: swap two lines in `y` and confirm `t08` still fires after the change.

## Two runs, one tree

The 16:15 fire found this run's claim twelve minutes old because six chained four-minute conversions wrote no beacon between them, judged it stale, and took the slot at 16:16. Both runs produced real work - the relay's `7795c60` is what made the state commit landable - but 65 minutes were spent twice, and the cause was this run's silence, not the tool. A step that runs six four-minute calls is six steps.

## Still open, and where

`restamp_txt.py --apply` writes `STATE-TXT.json` with the engine hash from **before** the commit containing the change, so it can never match what the release compares, and a measured `.txt` change can never prove itself at release. Until that is stamped with `regress.py`'s own `engine_fingerprint("txt")`, a `.txt` fix must release with `--force` and say so - which is what this run did.
