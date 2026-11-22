**22 Nov 2026 · slot 11:53 → running IST · 13 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 12:06 | **lead** | 1/16 | 18-spacer bundle: 68_journal 41/42 -> 42/42 in Google (live round trip). Blast radius on clean docs measured at 1 of 23, not 13. mobile-bill identical 31/42 with and without the patch, so the 11:27 cl |

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
check (`32_stroke_lines`, 23.3) — and it is the only class carrying an implemented, Google-proved lead.
The patch `patches/18-spacer-before-rowpitch-rowrule.patch` bundles five constructs aimed at it, and
the last run left it blocked on the corpus measure, not on evidence.

## What this slot settled

**1. The construct works, on a real document, in Google.** `68_journal` — the document the old
2880-twip spacer cap truncated by 4.05 pt — goes 41/42 → 42/42 on the patched engine. One round trip:
ConvertOne → Drive create-as-Google-Doc → export PDF → `gverify.py --collect` → 42/42.

**2. The blast radius is one document.** The 10:05 finding counted 124 spacer-bearing documents and
could not say which of the clean ones would move. Converted the 23 documents that pass all their Google
checks on the patched build and read every spacer paragraph out of their XML: **exactly one of them
carries a spacer**, and it is `68_journal`, which was 41/42 and is now clean. Twenty-two carry none.
The construct cannot reach them.

**3. The `mobile-bill` claim does not reproduce — in either direction.** Patched, `mobile-bill` scores
**31/42**, eleven checks failing. That reads as a catastrophe until the control: the unpatched HEAD
engine, rebuilt and put through the identical round trip, also scores **31/42 with the same eleven
checks failing, check for check**. The patch does not move that document at all. The `31/42` is this
build's behaviour under the current verifier and is **not** comparable to the committed `46/47` (a
47-check run); neither number should be quoted as the document's score. The 11:27 report's
"41/42 → 42/42" on `mobile-bill` is therefore unsupported on this build, and the next run must not
build on it.

## Why nothing is committed

`gate.py --budget 250` measures ~26 of 213 documents per call, and on a fresh pod the corpus has to be
rebuilt from nothing first (~7 min of ConvertOne, then ~35 min of measurement). That does not fit a
slot, and the pre-commit gate refuses an engine change it has not ratcheted. The patch stays a patch,
the finding is written down, and the next run inherits both.

## Subagents

Two were started before my own attempt. The first returned the blocker that matters, now measured twice over: **a sub-agent sandbox has neither the repository nor Drive.** It could not read `/scratch/work/CS` (its own pod is empty) and could not upload. Any task whose answer is a repo file or a Google number has to be done by the run itself; delegate only work whose inputs can be copied in with `files=`.

## Timing

| | |
|:--|:--|
| Slot window | 11:53 → running · 13 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 15 |
| Longest silence | **5.5 min** — from 11:53:42, after `reading state, deciding class` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **8 min** | `##############` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **3 min** | `######` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

DO NOT build the 0.9634 row scale or the hairline cell box for single-line cells - both measured inert. Build against rowParts>1: raise the row floor to the true 368 twips (the floor is quantised 8 twips low at 360) OR take w:before off the continuation paragraphs inside a wrapped cell. Google grows 360-twip rows to 19.0/20.0; source pitch is 18.40; mobile-bill rows 5-12 hold 6 w:p on 3 columns and render at 20.0 = 2.0 pt of growth. Prove on mobile-bill and insurance-policy-schedule FIRST - they are the only two documents blocking a spacer construct already measured to take 6 documents clean (68_journal 42/42 this run). Then land the spacer (w:before + hairline w:line=1 at 5868-5875, cap 2880->4320 at 5852,5866) with it.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
