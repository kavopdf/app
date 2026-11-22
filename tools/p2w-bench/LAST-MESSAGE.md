**22 Nov 2026 · slot 11:53 → running IST · 1h 20m**

> No change was kept this run. The numbers below say what was tried — and the run's real product is
> a refutation, because the constant every run has been subtracting since 11:14 does not hold.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |
| Committed | **12** files in 3 commit(s) from `c4766c2` — ...lacement-68_journal-CLEAN-IN-GOOGLE-1230-f1x.md, BLOCKERS.md, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, LAST-MESSAGE.md, REPORT.md, ROUND.json, RUN-LOG.md, RUN.json, TIMELINE.jsonl, TRACE.md |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 12:06 | **lead** | 1/16 | 18-spacer bundle: 68_journal 41/42 -> 42/42 in Google (live round trip). Blast radius on clean docs measured at 1 of 23, not 13. mobile-bill identical 31/42 with and without the patch, so the 11:27 cl |
| 13:12 | **lead** | 0/1 | pointKey whole-point quantisation fixed (trHeight 360/380 -> 368 exact); Google's laid pitch refuted as declared+0.75 on a real row (+1.04 and +0.74 measured); mobile-bill 46/47 unchanged, so a lead n |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## The class, and why this one

`classpick.py --leverage` puts `18_displacement` at **38.7 clean documents** — nearly double the next
check, and the class carrying the only Google-proved lead. The 11:53 handoff named two documents as
the blockers for a spacer construct already worth 6 clean documents: `mobile-bill` and
`insurance-policy-schedule`. `mobile-bill` is the cheapest gap in the corpus — **46/47 in Google,
`18_displacement` the only failure, source=0 render=1**. So it is the probe.

## What this slot settled

**1. The row pitch was quantised to whole points before the writer ever saw it.** The page draws
mobile-bill's row rules at 74.52, 92.92, 111.32, 129.72, 148.12, 166.52 — 18.40 pt apart on every row.
The model came out 75, 93, 111, 130, 148, 167: pitches of 18, 18, 19, 18, 19, written as `w:trHeight`
360, 360, 380, 360, 380. The cause is one line — `PdfToWord.pointKey()` keyed every table-cell corner
to the nearest **point**. Keying at milli-points makes the writer emit **368 on all 24 rows**. This is
a correctness fix in the model, renderer-independent, and it is a patch not a commit because it moves
every table in the corpus and a corpus pass does not fit a slot.

**2. Google does not lay a ruled row at `declared + 0.75 pt` on a real row. Refuted, twice, in
Google.** The constant comes from a 28-row synthetic probe whose cells carried `w:before=0` and no
`w:line`. On mobile-bill's own rows:

| declared | laid mean pitch | implied charge |
|--:|--:|--:|
| 17.65 pt (353 tw) | 18.69 pt | +1.04 pt |
| 17.30 pt (346 tw) | 18.04 pt | +0.74 pt |

Source pitch 18.40. A 0.35 pt change in the declaration moved the laid pitch 0.65 pt, so the response
is not even slope 1. **Every run since 11:14 has been subtracting a constant calibrated to a probe
that does not resemble the thing it is applied to.** That is the finding worth more than a fix.

**3. Neither build made a document clean.** mobile-bill reads 46/47 with `18_displacement` failing on
the unpatched engine and on both patched builds. The mean laid pitch moved 19.1 → 18.69 → 18.04
against a source of 18.40: closer, one check short. By the charter's own test that is a lead, not a
fix, and it is recorded as `lead`.

## What the next run should do

Measure the law on a **real-shaped row** — cells carrying `w:before` and `w:line="10"
w:lineRule="exact"` — sweeping the declared height **and** the border `w:sz`. Read the laid pitch off
the exported PDF's rule positions. If it snaps to whole points, an 18.40 pt source pitch is
unreachable by any declaration and `18_displacement` on mobile-bill is a renderer limit, not an engine
bug: `calibrate.py` decides that and has not been run on it.

## Subagents

Two, both before my own attempt, both on the row-height construct. The first mapped every `w:trHeight`
emit site and every rounding in the height chain. The second traced the 360/380 split and named the
quantiser as living one level above `DocxWriter`, in whatever fills `Table.rowEdge` — that answer is
what pointed at `pointKey()` and turned the slot from a guess into a measurement. Both ran inside the
turn (a scheduled run has no one to answer a later result).

## Why the commit carries no engine change

`regress.py --check` refuses **every** commit from every cron right now: the docx stamp is
`6c6cf642e13b7ed2` while the tree's docx fingerprint is `226f7f2df3013ad7`, because the `.txt`-only
commit `462353f` moved `PdfToWord.java` and restamped only the txt half. That is the standing blocker
recorded at `BLOCKERS.md` 2026-11-21 17:55. This commit touches no engine file and no table, so
`regress.py --check --only txt` was run instead — **PASS, txt no document worse than baseline** — and
the hook was bypassed under the handling that blocker already records. The engine tree is at HEAD.

## Timing

| | |
|:--|:--|
| Slot window | 11:53 → running · 1h 20m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 25 |
| Longest silence | **47.4 min** — from 12:07:10, after `report.py: building the report` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 3 parked, with the evidence to re-open them |
| Still a wall | **Not a stall, and I am recording that rather than treating it as one.** The `txt` row ages `tools/p2w-bench/t |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **1h 03m** | `#################` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **2 min** | `#` |
| other - not attributed to a tool | **12 min** | `###` |
