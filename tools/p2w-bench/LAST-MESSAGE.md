# Fixer report - 2026-11-25 15:06

```
# P2W Fixer - Run Report

**25 Nov 2026 · slot 15:06 → 17:03 IST · 1h 57m**

## What THIS run did, and what it measured

The slot was claimed at **16:26 IST** after `status.py` read the inherited claim `LIKELY DEAD` (80 minutes old,
last beacon 153 minutes old); it was released with `--force`. Two things were delivered, neither of them a code
change, and both are recorded because they change what the next run should attempt.

**1. The corpus is built and stamped.** The commit gate could not pass on this pod — `install-gate.sh` exceeded
the 290 s call limit three times in a row, each time inside `corpus-slice.py`. Four `corpus-slice.py` calls took
the corpus from 74 to **213 of 213** and wrote the stamp for engine `981ff1fa35e2cf67`; `regress.py --check` then
passed in seconds, at both commits made this run.

**2. The 25 solo `18_displacement` documents are three defects, not one.** `pending.py` prices them as the
cheapest clean documents in the corpus: 25 documents that fail *only* this check, so any patch that makes it pass
makes them CLEAN. Measured by matching the engine's own spacer-paragraph template in each `.docx`:

| cls | documents | what it means |
|---|--:|---|
| **A** | 11 | the guard **refused** the spacer (`w:before="0"`, `w:line>1`) — the gap the page drew is written as `w:line` exact, which Google delivers at about a fifth |
| **B** | 10 | the spacer is already **spent** and the document still fails — no spacer patch can reach these |
| **C** | 4 | **no spacer paragraph at all**; `med_dy` is small and positive on all four (+1.1 to +3.0 pt) |

It reproduces `FINDINGS/18_displacement-14-SOLO-IS-THREE-CONSTRUCTS-CENSUS-25NOV.md` exactly on its 14 documents
and extends the split to the 25 solo today. Full table, with `med_dy`/`worst_dy`/`refused gap pt` per document:
`FINDINGS/18_displacement-25-SOLO-A-B-C-CENSUS-25NOV-1626-fixer.md`.

Three consequences the next run should not have to rediscover:

* **The refused gap is not the displacement.** It is 1.3x to 3.5x the measured `|med_dy|` on ten of the eleven A
  documents, and the one spend ever measured (`68_journal`) delivered **77 %** of what it declared (-114.3 -> -3.1 pt
  on 144 pt asked). The engine's own comment claims `w:before` on an empty paragraph arrives 1:1. **That ratio is
  unmeasured at this engine and has to be settled before any guard patch is written.**
* **`table-inside-two-column-page` forbids a blanket rule.** `med_dy +8.0` — the render already sits *below* the
  source — against a 4.0 pt refused gap. "Always spend" moves it the wrong way.
* **The `-2.87 pt` flow constant recorded for `31_times_body_arial_headings` has moved.** At this engine it reads
  `med_dy +2.6`; the sign has flipped since it was written down. Do not build on it.

**Correction to `AUTOMATION-THE-GOOGLE-LOOP.md`.** That file says the `.docx` cannot be put into Drive from a
sandbox, which is why the Google loop was believed blocked. Measured this run: the corpus folder already holds
**213 distinct `.docx`, 213 files**, created 04:46 IST today, so step 1 of `refresh-google.py` is already satisfied;
and the platform `upload` tool **does** return an `s3key` from a saved sandbox path (`/scratch/output`), which
`GOOGLEDRIVE_UPLOAD_FILE` accepts. Both are now written into that file with the exact call shape. The duplicate the
test upload created was trashed again — it is mine from this run — and the folder is back to 213.

**What I got wrong, recorded so it is not repeated.** My first census of this run printed `spacers=0` for 17
documents that had **not been converted yet**: the "no `.docx` on disk" branch appended the same `0,0,0` tuple as a
real zero. The corpus was 74 of 213 at that moment. A count of zero and a file that does not exist must not print
the same string. The table above is from a run where every one of the 25 had a `.docx`.

## Progress

| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 7 vs ATTEMPTS.json history 4; subagents: 2 deployed vs no FINDINGS file for scresoffice prer, t12_txt instrume |
| Document-moves this run | **5** — 7 attempt(s), 2 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (19 still open), not a new class |
| Findings vs landing | **71** finding(s) on this class and **0** documents moved - writing is cheaper than landing, and nothing else says so |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 15:06 | **kept** | 0/None | instrument: the soffice prerender wedge - orphan holders swept by profile, retry on a fresh profile, a no-render docx skipped by name in PRE/.soffice-fail. 23 of 23 measured in two ~4 min calls where |
| 15:06 | **kept** | 0/None | instrument: scipy made a called prerequisite (pod-prep step 7) and a failed pip install now logs its exit code and last stderr line. The 25 Nov stall blamed on soffice was edt() on the pure-Python tra |
| 17:02 | **kept** | 5/8 | t12 compared a token multiset across two different tokenisers; 51 of 55 invented tokens were word-boundary artefacts. Unit is now the non-space character multiset. 5 newly clean, 0 of 213 newly failin |
| 17:04 | **lead** | None/None | census of all 25 solo documents at 981ff1fa35e2cf67: A 11 refused-spacer / B 10 spent-still-failing / C 4 no-spacer; a guard patch reaches only A and the w:before delivery ratio is unmeasured (the one |

## The txt

| | |
|:--|:--|
| Measured | **1 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **202** (94.8%) |
| Failing at least one check | **11** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t02_position` - 4 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `scresoffice prerender-01` | does soffice block screen.py, and where exactly | 17:03 | - | not recorded |
| `t12_txt instrument-01` | is t12's unit the word or the character | 17:03 | - | not recorded |

## Timing

| | |
|:--|:--|
| Slot window | 15:06 → 17:03 · 1h 57m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 36 |
| Longest silence | **116.1 min** — from 15:06:21, after `attempt.py: recording an attempt` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **1h 56m** | `######################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Take **A** (11 documents) and settle one number first: the delivered/declared ratio of `w:before` on an empty
paragraph at this engine, on one page, in Google. Every guard patch on this class depends on it and nobody has
measured it. **B** (10) and **C** (4) need different constructs — a spacer patch will not touch them, and 72
findings on this class have moved 0 documents because they were written as if it were one construct.
The corpus is built and stamped, so the gate costs seconds from here.
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
