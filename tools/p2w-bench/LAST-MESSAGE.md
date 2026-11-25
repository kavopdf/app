# P2W Fixer - Run Report

**25 Nov 2026 · slot 09:13 → running IST · 44 min**

> No change was kept this run. The numbers below say what was tried.

## What this run did

**It found that three instruments were each answering "how much of the corpus has been measured" with a
count of files, and that one of them was answering it backwards.**

`stage.py:measured()`, `health.py:compute()` and `pending.py:288` all asked a directory how many `.json`
files it held. 213 files exist; **86 carry the engine on HEAD**. So the stage a fixer is told to work in
read `fix`, the watchdog read `done 213 of 213`, and the pending list named the 86 documents measured
today as the stale ones while the 105 stale results stayed invisible.

| Instrument | Before | After |
|:--|:--|:--|
| `stage.py` | `stage: fix` / `measured: 213 through Google (191 scored, 22 refused)` | `stage: measure-google (changed from fix)` / `measured: 82 through Google (60 scored, 22 refused)` |
| `health.py` measure-google | `done 213 of 213` | `moving 82 of 213` |
| `health.py` matrix | `done 213 of 82` | `done 213 of 213` |
| `pending.py` docx table | `86 document(s) still carry a verdict from an older engine: 09_stamp_font_not_embedded, ...` | `105 document(s) ...: 11_stamp_with_signature_image, ...` |

The `matrix` row was a second bug the first exposed: its denominator was the Google count, so as soon as
that count became engine-aware the line printed a fraction greater than one. The `pending.py` row was
checked against an **independent census** - count the engine stamps in `benchmarks/gverify/*.json` with a
separate script, and against `gverify._engine_now()` - before and after the edit, not through the tool
being edited.

### The ledger, because `classpick.py` will not open a class until it is empty

Six pending rows were the ledger disagreeing with itself about whether something had been measured or
implemented. Each was closed against a named file or line:

| Row | Closed because |
|:--|:--|
| `stage.py` counts a result file as a measurement | fixed this run; the row was also **7 cells in a 6-cell table**, which is why `pending.py` could not read it at all |
| the claim is advisory (two fixers, one slot) | (a) is already implemented: `round.py:501-503`, `:543-566`, `:420-431`, `:441-461`; `test_claim_remote.py` asserts both halves |
| `--release-fixer` refused on a pending count | `round.py:975-993` honours `--force` and prints `FORCED past N pending item(s)` |
| `74_balance_sheet_indented_subitems` never committed | committed and current: 41/42, engine `85b8735f`, 03:14:41, failing `18_displacement` |
| a subagent has no repo (x2) | **refuted by measurement**: both subagents cloned the repository themselves this run and returned 40 KB each |

**PENDING 16 -> 12**: six closed, two arrived from `fa5bd53b` (the 09:10 gverify pass). Measured with
`pending.py` in the same clone, before and after. The pending count did not fall for the `pending.py:288`
fix - the row is a `[measure]` row and the number inside it changed, which is the point.

### The lead on the class the rotation names

`18_displacement` is the highest-leverage check: 13 documents fail it alone, 8 fail it with
`60_text_column_right_edge`, and it appears in 40 of the 47 failure shapes. The proposal lands two patches:

- **partial spend at `DocxWriter.java:6117-6137`** - three integers and one guard condition on the table-gap
  spacer, `before + line` preserved to the twip so LibreOffice should be byte-neutral. Predicted +3 clean.
  Its own warning: the guard's `slackTw` reads the **source** page's white space, which is anti-correlated
  with the defect (688 tw of measured slack on `68_journal` against a 144 pt gap whose absence already moved
  the render 114 pt up).
- **`w:pgMar w:top` per-page section** - the Google-proven shape, 37 -> 40/42 on the probe, but a
  page-structure change that needs the `budgetTw` subtraction.

Positive controls from stored verdicts: `68_journal_wide_table_spanning` (41/42),
`72_bank_statement_no_rules_right_amounts` (41/42, predicted clean), `412_page_labels_roman` for the
page-margin patch. Chief false positive to watch: a fall in `runs_matched` - the shape of the refuted
1x1-table variant. **Check first that `place()` at `:4149` has no callers**: the mechanism
`DOCS-ROOT-CAUSES-24NOV.md` names lives in dead code, so a patch written there changes no output.

Why this is a lead and not a patch: the subagent pod has no corpus, and this slot's first 25 minutes went
to building one (213 `.docx`, three slices, cold pod). The patch needs a full-corpus re-convert and a
before/after measure - the next run's first hour, not this one's last twenty minutes.

## Progress

| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 1 vs ATTEMPTS.json history 2 |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **27** of the **86** re-measured on this engine - **105** of the 191 scored are still on an older engine, and **11** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **2** run(s) for the 105 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **22** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (12 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 09:25 | **lead** | 0/None | Google round-trip on 68_journal: guard relaxed (env-gated) moves med_dy -114.3 -> -3.1 pt, 111.2 pt of movement, so the guard is the blocker; but 18 still fails at 3.9 pt and 59_shape_anchor appears ( |
| 09:52 | **lead** | 0/213 | read-only subagent proposal landed as FINDINGS/18-DISPLACEMENT-PROPOSAL-25NOV.md: place() at :4149 is dead code (zero callers) so the mechanism DOCS-ROOT-CAUSES-24NOV.md names cannot be patched; spaci |

## The txt

| | |
|:--|:--|
| Measured | **44 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18-DISPLACEMENT-PROPOSAL-25NOV` | where in DocxWriter does w:before / exact line heigh | 09:36 | 09:41 | 5 min |
| `PENDING-ANSWERS-25NOV` | for each of the pending items, is it closeable, and  | 09:36 | 09:44 | 8 min |

## A clock that could not be trusted

`runclock.py` read **2 min** elapsed and "CHECKPOINT IN 58 MIN" at 10:26 while the claim was taken at
09:13 and three commits had already landed. The cause is visible in the tool's own words: the first
`--heartbeat` printed `run window reset - RUN.json described the run before this claim`, and the rebase
that landed `a323d424` took the remote's `ROUND.json`, resetting `fixer_started` to the moment of the
beat. The claim history and the wall clock are the truth; `RUN.json` was set back to the real claim time
before this report was written, so the slot line above reads 09:13.

The `1 disagreement` in the self-check is the same collision: `ATTEMPTS.json` holds two rows because
commit `f50df76c` landed another run's 09:25 attempt on `68_journal` while this slot was held. This run
recorded one attempt (64, the `18_displacement` lead). Nothing is zeroed and nothing is claimed twice.

## Timing

| | |
|:--|:--|
| Slot window | 09:13 → running · 44 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 44 |
| Longest silence | **24.4 min** — from 09:27:24, after `dead claim cleared by force release` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **24 min** | `############` |
| measure or build - a conversion, screen or compile writes no beacon | **0 min** | `#` |
| record - attempt, handoff, class rows | **3 min** | `##` |
| report - the report and the chain | **2 min** | `#` |
| other - not attributed to a tool | **11 min** | `######` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

**The corpus is built and stamped on this pod** (`/scratch/work/p2w/out`, 213 `.docx`, `981ff1fa35e2cf67`) -
do not spend 25 minutes rebuilding it. **First: the `18_displacement` partial spend** at
`DocxWriter.java:6117-6137` in `FINDINGS/18-DISPLACEMENT-PROPOSAL-25NOV.md`, after confirming `place()` at
`:4149` has no callers. **Then the remaining closeable pending rows** - `pending.py` still refuses a class
(8 closeable, 4 needing a person). **Then the rotation.** `regress.py --check` takes ~12 s warm and passes on
this tree; the pre-commit hook has not refused once today.
