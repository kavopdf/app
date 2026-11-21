# P2W Fixer - Run Report

**21 Nov 2026 · slot 18:17 → 19:22 IST · 1h 05m**

> No engine change was kept. What landed is the fix that makes an engine change landable at all: the
> corpus pass could not finish, so `RANKING.csv` was never written, so `regress.py --check` could
> never pass, so no patch could be gated. Two silent defects in `benchmarks/p2w.py` are fixed and
> proved. The cell-border patch that had been waiting on that measurement is refuted by it.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 4 attempt(s), 0 kept |
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
| 18:20 | **reverted** | 1/210 | `patches/47-margins-cell-border-inset.patch` measured on all 210 documents instead of the nine it was proposed on. `404_sudoku_grid` 0.27 → 0.00 and three more improved, but 24 got worse - `table-with-no-header-row` 0.61 → 0.86, `two-tables-stacked-with-no-gap` 0.77 → 1.07, `bank-statement-5-pages` 0.56 → 0.60 - and the gate refused. The nine-document sample was too small, not wrong: every document in it had a 2 pt rule, and the documents that got worse have thin or absent left rules where subtracting the full border moves text off a position the renderer had already placed correctly. Reverted; the engine is back at the committed state. |
| 18:05 | **kept (tools)** | - | `benchmarks/p2w.py`: `rank()` crashed with `KeyError: 'doc'` on `DIST/416_many_tiny_pages.partial.json` - the resumable-window note `measure()` itself writes - **after** 211 of 212 documents were measured, killing the run before `RANKING.csv` was written. And `EXEMPT.json` was read from one hard-coded path that does not exist when the script is run from `/scratch/work`, which `FIXER-BRIEF.md` tells every run to do; the `except` swallowed it, `want` counted the exempt 300-page document, and `complete` could never be true. Both fixed, `RANKING.csv` now written with 210 rows. |

## What actually landed

Commit `8ef686e`, gate PASS, two defects in `benchmarks/p2w.py`.

The first: `measure()` keeps a resumable window for any document over 80 pages in
`DIST/<doc>.partial.json`, which has no `doc` key. `rank()` read every `DIST/*.json` and indexed
`d['doc']`. Measured at 13:58, the traceback arrived after `chunk 1: measured 211 of 212` - the pass
was finished and only the report was lost. `results()` now returns `DIST/*.json` minus
`*.partial.json`, and the three readers of `DIST` use it.

The second: `EXEMPT.json` was opened at `dirname(__file__)/../tools/p2w-bench/EXEMPT.json`, which
resolves only when the script runs from `benchmarks/` inside a clone. From `/scratch/work` it does not
exist, the `except` returned an empty set, and `want` counted `416_many_tiny_pages` - excluded by
design because 300 pages cannot be measured inside one command. `complete` was never true, so this
tool wrote `RANKING.partial.csv` on every run of its life. `_exempt_paths()` now uses the same
list-of-places shape as `_realworld_dirs()`, which already solved this exact problem for
`benchmarks/realworld/`, and a miss warns instead of passing silently.

Before: `measured 210/211 remaining 1`, published table untouched. After: `measured 210/210
remaining 0`, `RANKING.csv` written. That is 211 PDFs minus one exempt, which is the arithmetic
`want` should always have done.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **190** (89.2%) |
| Failing at least one check | **23** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

One agent, on `47_margins`: which documents carry the class, which check fails on each, what the
twelve existing findings already refute, and the one change with the highest measured reach. It
returned the class table, the refutation list, and the cell-border arithmetic - which is what this
run then measured on the whole corpus and refuted. No second agent ran; the slot went to the corpus
pass that the first agent's answer required.

## Timing

| | |
|:--|:--|
| Slot window | 18:17 → 19:22 · 1h 05m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 28 |
| Longest silence | **9.2 min** — from 19:11:04, after `report.py: building the report` |
| Silences over 2 min | 7 |
| Obstacles | 4 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **4 min** | `##` |
| fix - diagnose and change the engine | **7 min** | `#####` |
| measure or build - a conversion, screen or compile writes no beacon | **9 min** | `######` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **13 min** | `########` |

## A gate that passed while measuring the wrong table

Worth more than the patch it cost. After the corpus pass, `regress.py --check` printed PASS with the
patched engine stamped. It had compared `benchmarks/RANKING.csv` - still the old table, still the old
engine's numbers - and the `--stamp` had written the new fingerprint over it. A table measured on one
engine, stamped as another, and a green tick.

Writing the real measurement into `benchmarks/RANKING.csv` and re-checking turned the same gate into
`docx: 24 REGRESSION(S)`. The first PASS was not a pass; it was the gate reading a file nobody had
updated. This is the sixth-tool shape the brief describes, caught only because the number was
compared against the table rather than against the tool that printed it.

## Next run

The boundary the refutation leaves is `w:sz`. Subtract the cell's border only where the rule the
writer draws is at least 1 pt (`sz >= 8`): `404_sudoku_grid` carries `sz=16` and the 24 documents that
got worse carry thin or nil left rules. That is a hypothesis with a number attached, not a
measurement - it needs one 210-document pass, and the number to beat is 4 improved / 24 worse
becoming at least 2 improved / 0 worse. With the corpus pass working, that pass now ends in a
`RANKING.csv` instead of a traceback, which is the whole reason this run spent its slot on the tool.

Two runs held this tree at once again: a second fixer claimed at 18:17 while this one held the slot
from 17:53, and the rebase put its `RUN.json` in place of this run's, which is why the slot window
above is that run's clock and not this one's.
