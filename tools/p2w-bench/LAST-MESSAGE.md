# P2W Fixer - Run Report

**24 Nov 2026 · slot 23:58 → running IST · 27 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **13** of the **63** re-measured on this engine - **127** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **3** run(s) for the 127 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 00:09 | **lead** | 0/13 | instrument now prints med_dy/worst_dy/med_dx (KEPT); unruled row-excess quantum 15->5 twips spends the table-gap spacer on 72_bank_statement and takes Google med_dy -13.0->+1.1, worst 28.2->4.8, still 41/42 |
| 00:24 | **lead** | 0/13 | instrument prints med_dy/worst_dy/med_dx (KEPT+committed, cross-checked to 0.1pt against independent PyMuPDF); unruled row-excess quantum 15->5 spends the table-gap spacer, Google med_dy -13.0->+1.1 worst 28.2->4.8; row-height compensation REFUTED (Google +1.1->-4.2, LO 42/42->41/42); corpus pass 43s/doc did not fit, engine reverted |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

One was deployed, to `18_displacement`, and it **returned nothing usable**: its sandbox had no clone of
this repo, so it fell back to a public probe repo of 27 loose `.docx` and could not read
`benchmarks/gverify/` or the converter source. It did return one true structural fact about writer
output — 2,081 `<w:spacing>` elements, every one `lineRule="exact"`, 85.3 % with `w:line` ≤ 13 twips —
which is the same construct this run then measured directly. The lesson is mechanical: a subagent has
no access to `/scratch/work`, so the repository has to be named as a clone instruction, not a path.
No second agent was deployed; the slot was spent measuring instead.

## The class I picked, and why

`classpick.py` **refused** — `PENDING FIRST: 28 item(s) you can close`. `pending.py` names the first of
them: the last run's carry-over, four dead `[agent]` rows on `18_displacement`, five `[ratchet]` rows
and 13 `[blocker]` rows whose action is real. `18_displacement` also carries the largest leverage in
the table (`classpick.py --leverage`: **34.7 clean documents**, first place), and two of the dead agent
rows were on it. So the class was taken on the pending list's own evidence, not on a suggestion.

## The construct

`18_displacement` was steering blind. It computed `med_dy`, `worst_dy` and `med_dx` at
`verify_google.py:5653-5655` and threw all three away; the stored result carried
`name/status/passed/total/failed/engine` and nothing else. **That is now fixed and committed** — the
check carries the distance as its detail and `gverify.py --collect` stores it. Two independent
confirmations: a document compared against itself scores 42/42 with `med_dy 0.0`, and the live Google
render of `72_bank_statement` reads `med_dy -13.0` against **-12.9** from a separate PyMuPDF baseline
match that does not use the edited tool.

With the distance in hand, the fault on `72_bank_statement` (one of the 13 that fail only this check)
is **two** things, not one: a **13.3 pt step** at the table's top, then a **0.25 pt/row** drift that
partly pays it back. The step is the table-gap spacer — one `w:line="366"` paragraph with
`w:before="0"`, and Google charges a `w:line`-exact box on an `sz=2` mark a fifth of what it declares
(14.36 pt predicted short, **13.3 pt** measured).

The engine already knows how to fix this: it splits the spacer, hairline in `w:line` and the rest in
`w:before`, which Google honours 1:1 — but only where its room test passes, and the test charges
`15 twips × pageRowCount` for row growth. Traced with a new `-Dp2w.debugSpacer`, the page has 558 twips
of slack and the guard asks 616: **refused by 2.9 pt**, which leaves the table the whole gap too high.
Those 15 twips are `TABLE_BORDER_TW`, and `:6245` says the rule is a *ruled*-row rule — "an unruled
table draws no rule and keeps its full pitch". `72_bank_statement` has no rules. Charging it 5 twips a
row (its measured growth) makes the page spend the gap: **Google `med_dy` -13.0 → +1.1, `worst_dy`
28.2 → 4.8**, page count unchanged, and every ruled table byte-identical.

It still reads 41/42. The residual is the cell's own line advance inside an unruled row, and the
obvious fix for it — writing unruled rows 5 twips short — was **built and refuted**: Google got worse
(`+1.1 → -4.2`), because Google already honours `w:trHeight` and the drift is inside the cell, and
LibreOffice lost `18_displacement` (42/42 → 41/42). Both numbers are in the finding so the next run
does not pay for them again.

The engine change is **reverted, not landed**. `regress.py --check` refuses an engine the corpus has
not been measured on, and `benchmarks/p2w.py --force` ran at **43 s a document on this pod** — 33 in
250 s, then 7 in the next 250 s, i.e. ~2.5 hours for 213 against the 40 minutes the brief budgets. The
measurement is recorded; the recipe is one line at `DocxWriter.java:6093`.

## The gates

`regress.py --check` **PASS** on the committed tree (nothing worse in docx or txt, table matches the
engine). `measure_gate.py` **NOT READY** — RANKING.csv is stamped on docx engine
`3e7f7c4475343a35` and the tree is `56ad3a0a115ae19f` after this run's own commits, which is the same
"unmeasured engine" refusal, not a new fault. `google_safe.py` could not run — no `.docx` output
directory exists on a fresh pod, so no construct was spread and none was refused.

## Four probes, all mine, all deleted

Four Google Docs were created in `KavoPDF-Verify` this run, never in the Drive root, and all four were
deleted after scoring. Nothing in the user's Drive remains, and nothing outside my own probe documents
was deleted.

## Timing

| | |
|:--|:--|
| Slot window | 23:58 → running · 28 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 24 |
| Longest silence | **6.5 min** — from 00:18:24, after `lastmessage.py: running a tool for its numbers` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **6 min** | `#####` |
| measure or build - a conversion, screen or compile writes no beacon | **3 min** | `###` |
| record - attempt, handoff, class rows | **6 min** | `#####` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **10 min** | `########` |
