# Fixer report - 2026-11-27 17:00

```
# P2W Fixer - Run Report

**27 Nov 2026 · slot 17:00 → running IST · 25 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8681** of 9273 (93.6%) on 212 documents |
| Check-instances still failing | **592** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **43** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; kept change: 1 code commit(s) in this window, first: finding: autoflow+autoEm=1.2207 refuted on five  vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **212** re-measured on this engine - **0** of the 212 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **1** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (54 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 17:24 | **lead** | 0/None | autoflow+autoEm1.2207 refuted on five solo-18 documents: scores identical on all five, median dy worse on 3 of 4 with a current baseline (72 -3.12->-6.72). The 26 Nov 42/42 does not reproduce under th |

## Why nothing moved, in this run's own words

> # Why no document moved this run: the one construct with a clean-document record does not reproduce
>
> I took `18_displacement` because it is the only class where a single construct can reach double-digit
> clean documents: 25 of the 212 scored documents fail `18` **and nothing else** (`benchmarks/gverify/`,
> engine `d28ca7516c3f9165`, counted this run). The next largest solo set is `60` at 6 and `59` at 3, and
> the agent work this run confirmed that ceiling — the census on `60_text_column_right_edge` put the engine-reachable
> prize at 3 documents and closed `60-P` as measured-dead, and the class's own history has ~100 FINDINGS
> files of refuted levers.
>
> Within `18`, every page-top lever is already refuted and measured: all 25 solo documents are one page,
> so nothing that acts on pages after the first can touch them. What was left was one record in the tree
> that a *construct* change produced a clean solo-`18` document:
> `-Dp2w.lineRule=autoflow -Dp2w.autoEm=1.2207` → `72_bank_statement` 42/42, 26 Nov 12:00.
>
> **It does not reproduce.** Five solo-`18` documents, five Google renders, one export each, the flag
> verified in the bytes (8 flow paragraphs at `w:line="240" lineRule="auto"`, cells still `exact`):
>
> - no document changes score — all five still fail `18_displacement` and nothing else;
> - the median baseline shift moves **the wrong way on 3 of the 4** documents that have a current-engine
>   baseline to compare against: `72` −3.12 → **−6.72** pt, `16` −2.63 → −3.12, `320` +6.25 → +6.84;
> - one moves the right way by less than a point: `71` +1.12 → +0.37.
>
> Two facts explain the gap, and both were checked rather than assumed. `spacing()`'s `pageFirst`
> compensation is no longer dead code — both flow call sites pass `ctx.newPage` — so this is the same code
> path the 26 Nov build measured. And **check 18 no longer scores the bbox top**: the 26 Nov 18:00 relay
> replaced the scored quantity with `roy`, the origin projected into reading space, precisely so a
> substitute face's ascent cancels. The 42/42 was measured under the old quantity. A clean document on a
> retired instrument is not a lead; it is a number that has to be re-earned.
>
> So the slot's product is a closed lead, not a kept change. What it leaves the next run is the axis that
> has never been tried: `AUTO_LINE_EM` is one number for the whole corpus, and the box it asks for is the
> *substitute* face's line height — `1.15` for a face Google owns (Arial, Times New Roman) and `1.220709`
> for Calibri → Carlito. The engine declares Arial on some paragraphs and nothing on others, so one
> global em is right for at most one of those populations. That is the shape of this result: the two
> documents that declare Arial (`16`, `71`) are the two that moved least badly, and `72`, which declares
> nothing, moved worst. A per-face ratio is the first version of this construct that is not a single
> number, and it is a two-line change at `spacing()`'s call sites.
>
> **Not a blocker, and said plainly:** the corpus was cold on arrival (164 of 214 documents unconverted,
> no stamp) and rebuilding it to 214/214 with `corpus-slice.py` cost the first 20 minutes of the slot. The
> gate then passed in seconds, and `regress.py --check` reports no document worse in either format. That
> rebuild is what makes the next run's first attempt possible inside 90 minutes instead of after a
> 20-minute warm-up.

### The run before this one said

> # Why no document moved this run (one was measured clean, and that is not the same thing)
>
> Because the class was not blocked - it was **mis-measured**, and I spent the slot proving which half of
> the 25 sole-18 documents is the instrument and which half is the page.
>
> `18_displacement` scored `g["ry"] - r["ry"]`, and `ry` is the span's bbox TOP: the origin minus the
> rendered face's own ascent. So the difference it scored was the baseline difference **plus** the
> difference between the source face's ascent and the substituted face's - a font metric. `runs()` now
> publishes `roy`, the origin projected into reading space, and 18 scores that. `ry` is untouched: the
> pair matcher and checks 34/42/43 are keyed on it and must not move.
>
> **Twelve live Google renders, both instruments, the same PDF each time.** One document flipped:
> `31_times_body_arial_headings` 18 FAIL (med +2.6 pt) -> PASS (med +0.9 pt), 41/42 -> **42/42**. No new
> failure on any of the twelve, including the six passing-18 documents I chose for having the smallest
> margin in the store (`07`, `312`, `364`, `393`, `09`, `06`).
>
> **And it refuted the reason I did it.** The hypothesis was that the ascent term explains all 25 sole-18
> documents. It explains one of the five measured. Four carry a real baseline shift of -3.1 to +6.3 pt,
> confirmed by a second script that reads `span["origin"][1]` from both PDFs and imports nothing from the
> file I edited. Those four are Google moving the text, which is the engine's problem.
>
> The second finding is the map for the other 24: two of the twelve are a page-wide **constant**
> (`07` -3.94 pt, 68 % of runs within 1 pt; `06` -1.88 pt, 76 %) and one is the opposite
> (`320` median +6.25, p90 **14.68**, 16 % within 1 pt) - per-block placement that no page offset reaches.

Accounts share 15% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **3.9 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 17:00 → running · 25 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 36 |
| Longest silence | **5.8 min** — from 17:15:07, after `corpus slice 3 of 3` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **2 min** | `###` |
| measure or build - a conversion, screen or compile writes no beacon | **11 min** | `##########` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **8 min** | `#######` |

The unattributed row is 5 distinct beat(s) that matched no phase. They said:

- `corpus slice: 164 to go`
- `corpus slice 2 of 3`
- `corpus slice 3 of 3`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 33 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
