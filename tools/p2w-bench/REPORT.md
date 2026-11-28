# Fixer report - 2026-11-28 09:28

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 09:28 → running IST · 16 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **3 disagreement(s)** - attempts: RUN.json counter 4 vs ATTEMPTS.json history 3; kept change: 4 code commit(s) in this window, first: findings: the row-pitch excess is not universal  vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; run window: RUN.json says this run began at 09:28 vs TIMELINE.jsonl records the claim at 09:16, so the window was reset and the duration is short |
| Document-moves this run | **0** — 4 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **48** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (63 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 09:28 | **lead** | 0/None | TxtWriter writes a letter-spaced line as one line per glyph while DocxWriter merges it: 305_vaccination_certificate has 47 single-char lines of 85 and fails t08 32/33 because the glyphs land after the |
| 09:41 | **lead** | 0/None | Ten Google variants on three documents: Google's table row advance exceeds the source pitch by +0.10 (16.40 src), +0.13 (18.40) and +0.50 (13.00) pt per row, accumulating 3.9-9.2 pt by the bottom of a |
| 09:44 | **lead** | 0/None | Fourth document: table-inside-two-column-page reproduces the source's 11.8 pt text pitch exactly in Google (11 of 16 gaps 11.8, source identical) because its rows are taller than its text pitch (trHei |

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

> **The decision, and its reason.** `classpick.py --leverage` prices `18_displacement` at **47.1 clean
> documents** and 19 documents that fail nothing else, and the 05:54 run had already root-caused it and
> named its next step: *"give the cell the font's natural line box and move the identical difference into
> `before`"*. That is a falsifiable prediction, so I did not build it — I tested it in Google first. It is
> wrong, and the measurement that refutes it found the real mechanism.
>
> **What I did, in order.** Two agents in the first ten minutes (both ran inside the turn, both negative,
> both committed). Then ten Google variants across three documents: upload, convert, export, and read the
> row pitch out of the export with PyMuPDF. That is the whole run, and it is four measured attempts, not
> one.
>
> **The finding, and it is not the one anyone expected.** Google's table row advance **exceeds** the source
> pitch by a per-document amount, and it accumulates: **+0.10 pt/row** on a 16.40 pt pitch, **+0.13** on
> 18.40, **+0.50** on 13.00 with 6 pt text. Over 24-40 rows that is **+3.9 to +9.2 pt** by the bottom of the
> table, and `18_displacement` allows 2.8 pt. The engine's row geometry is **already exact** — it writes
> `w:trHeight 328` and `before 317 + line 11`, which is the source's 16.40 pt to the twip.
>
> **And no declaration the engine writes can change it.** `w:trHeight` is inert (two values, identical
> export); reducing `w:before` is inert (three values, identical export); the cell's paragraph mark is
> inert; `w:line="0"` reads as single spacing and makes it worse. Only an *increase* of `before` above a
> per-document value is honoured, and it is honoured upward.
>
> **So there was nothing to land, and that is the decision.** The only change the previous run proposed
> (v2 here: same sum, a 12 pt box instead of 0.55) leaves the pitch at 16.500 and moves the table's first
> row **+11.51 pt**. Building it would have cost the corpus pass and produced a Google regression. A
> change I could not measure as an improvement is not a change.
>
> **What I now know that I did not.** `18_displacement` on dense-table documents is a **renderer
> behaviour, not an engine defect** — the fourth construct in this repository where the answer is "Google
> cannot do it". Twelve of the nineteen documents that fail nothing else are 20-plus-row tables, so the
> class's 47.1 price is mostly not collectable. The next run should split those nineteen by their own row
> pitch and row count before spending a slot on any of them, and the split is in the finding.
>
> **What would prove me wrong.** Any Google render of a 20+ row table whose pitch equals its source pitch
> to 0.05 pt; or any variant that moves the delivered pitch while *reducing* `before`. Four attempts at the
> second failed.

## The txt

| | |
|:--|:--|
| Measured | **4.3 h ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-05` | is the cell w:line natural-box rewrite right in GOOG | 09:42 | - | not recorded |
| `18_dB-03` | census the 19 documents that fail only 18_displaceme | 09:42 | - | not recorded |

## Timing

| | |
|:--|:--|
| Slot window | 09:28 → running · 16 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 35 |
| Longest silence | **12.8 min** — from 09:28:54, after `lastmessage.py: running report.py for the numbers` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **0 min** | `#` |
| fix - diagnose and change the engine | **12 min** | `#################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **2 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
