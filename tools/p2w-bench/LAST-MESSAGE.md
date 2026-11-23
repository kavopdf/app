# Fixer report - 2026-11-24 00:56

```
# P2W Fixer - Run Report

**24 Nov 2026 · slot 00:56 → running IST · 47 min**

> No document moved this run. Two constructs were measured and one named fix was refuted -
> and the refutation is the deliverable: it stops the next run buying a global engine change
> for zero gain.

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
| Working on | `00_page_count` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 01:42 | **lead** | 0/213 | t12's 21 invented words on 600 split into 3 faults; source reader now sees printing annotations (21->20, blast radius 1 doc, no verdict moved); remaining 20 are the converter duplicating FreeText text |
| 01:43 | **lead** | 0/213 | 23 page_count_refused docs: 21 render the RIGHT page count in LibreOffice and one too many in Google (proxy is blind); the 350 inline-picture construct is REFUTED - 0 wp:inline across all 23, the engi |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## The class I picked, and why

`classpick.py` **refused** again - `PENDING FIRST: 28 item(s) you can close` - so the class
came from the pending list's own evidence, as the brief requires. The list names four dead
`[agent]` rows, five `[ratchet]` rows and thirteen `[blocker]` rows. Of those, one is worth a
slot on measurement alone: **`00_page_count`, priced at 23.0 clean documents**
(`classpick.py --leverage`, second place) - and it is not a scoring class at all. It is 23
documents that are **not scored**, so all 42 Google checks are skipped on every one of them.
Nothing else in the pending list can move a document that is currently invisible.

The second attempt took `t12_word_invention` because it is the largest open `.txt` class
(8 of the 14) and the one class this pod can measure end to end without the gverify cron.

## What I measured, and what it costs the next run

**The LibreOffice proxy is blind to 21 of the 23 unscored documents.** I converted all 23 on
the HEAD engine, rendered every `.docx` through LibreOffice, and counted pages against the
source PDF. **21 render the correct number of pages in LibreOffice and one too many in
Google.** Two bank forms are wrong in both (10 and 11 pages against 9). That is
non-negotiable #1 with a number on it: the corpus pass, the ratchet and `regress.py` all read
the proxy, so no amount of LibreOffice measurement will ever see this class.

**"A few points of overflow" is refuted.** Bottom slack on the LibreOffice render, against a
841.9 pt page: `350_question_paper` 3.39 pt, `60_page_border` 17.94 pt,
`305_vaccination_certificate` **58.29 pt**. A document with 58 pt of room still costs Google a
second page, so the general cause is not the last line spilling, and a fix aimed at trimming
the bottom would reach one document.

**`probe-350.java.patch` must not be applied.** The committed `350` finding charges
`DocxWriter.java:2549`'s `<wp:inline>` picture branch, on a premise it states it could not
check - it had neither the PDF nor the `.docx`. Both exist now, and the finding's own
prescribed greps refute it: **0 `<wp:inline>` across all 23 documents**, every picture already
anchored (2653 anchors on the bank forms, 276 on `305`), and `350` is not a drawing-only page
at all - 70 paragraphs of real text and one 0.7 pt rule. That patch changes the emission path
for every unplaced picture in the corpus and would move none of the 23.

**What is left of the class, split by measurement and not by opinion.** The two bank forms
anchor a picture at **842.1 pt on an 841.9 pt sheet** and are wrong in LibreOffice too - a
pagination fault, which belongs with `18_displacement`. For the 21 Google-only ones the next
probe is `305_vaccination_certificate`: 58.29 pt of slack and 276 anchored shapes, so whatever
Google charges there is measurable by subtraction instead of by guess.

**On the `.txt` side, 21 invented words on `600` are three faults, not one.** 7 are the writer
emitting a sticky note's comment body (a sticky note never prints); 13 are the writer
transcribing a FreeText note **twice** (`txt.count("4471") == 2` against
`src.count("4471") == 1`); and 1 - `approved`, a Stamp - is text the source reader could not
see at all, because `get_text("dict")` returns nothing from an annotation's appearance stream.
I fixed the third: `verify_txt.py:glyph_truth()` now reads the `/Contents` of the printing
types only, and `600` goes **21 → 20**. Blast radius measured over all 213 PDFs: **exactly one
document** carries a printing annotation, so nothing else can move and nothing did. No verdict
moved.

The remaining 20 close in the converter, not in `TxtWriter.java` (which has no annotation
code): whatever adds an annotation's `/Contents` to the page text must add **only types that
print** and **only when the content stream did not already draw them** - the same rule
`glyph_truth()` already applies to widget appearance streams, which fixed `601` from 98.8% to
100.0% on 21 Nov. The widget case and this one are the same bug in two places.

## The gates

`regress.py --check` **PASS** on the committed tree (nothing worse in docx or txt, table
matches the engine), and it passed again on the second commit. `measure_gate.py` **READY** -
every document measured. `google_safe.py` could not run: no `.docx` output directory exists on
a fresh pod, so no construct was spread and none was refused.

## Subagents

One was deployed, in the first ten minutes, on the problem that has blocked every engine
landing for days: **can a full 213-document corpus pass fit in a work slot?** It returned a
measured answer, worth more than this run's own attempts.

- The **43 s/document figure the last run reported is not reproducible.** Its serial end-to-end
  cost on a 12-document sample is **8.1 s/document**, so a full serial pass is **~34 minutes**,
  not 2.5 hours. The 43 s came from launching `soffice` once per document; batched twelve at a
  time it is **0.7 s/document**, not 5.5.
- **LibreOffice does not parallelise on a 2-core pod** - two workers with separate profiles
  measured **57% slower**, twice.
- It did **not** get a clean 2-worker end-to-end number, so the 12-17 minute projection it
  offered is arithmetic, not measurement. That gap is in its own summary and is not carried
  here as a result.

That number matters more than either attempt: the 43 s figure is the stated reason a corpus
pass "does not fit", and the same reason five `[ratchet]` rows and `measure_gate` have been
stuck. At 34 minutes a pass fits a 90-minute slot with room for the attempt that follows it.

No second agent was deployed: `delegate_task` runs in the foreground on a scheduled run, so the
first one cost 23 minutes of the slot. The brief's two angles were met by the run's own two
attempts instead.

## What I did not do, and why

I could not measure in Google myself this run. The Drive tools available here cannot convert a
`.docx` to a Google Doc - `GOOGLEDRIVE_UPLOAD_FILE` rejects the `google-apps.document` target
MIME - so the before/after for any Google-side change belongs to the `:20 gverify` cron. That
is why neither attempt claims a Google move, and why the engine was left alone: a Google-only
construct changed without a Google measurement is the one thing the brief forbids.

Nothing was deleted. No Drive file was created and nothing was written to the user's Drive
root; `probe350.docx` was staged in the output directory to reach the upload tool and the
upload was refused before any file was created.

## Timing

| | |
|:--|:--|
| Slot window | 00:56 → running · 47 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 23 |
| Longest silence | **24.4 min** — from 00:56:37, after `pending.py: reading the pending gate` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **3 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **27 min** | `#############` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| other - not attributed to a tool | **12 min** | `######` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

PENDING FIRST, FIXING SECOND - AND FIXING RESUMES BY ITSELF WHEN THE LIST IS EMPTY. `python3 tools/p2w-bench/pending.py` lists the 22 items you can close, in the order to take them. classpick.py refuses to name a class until those 22 are gone, so a run that tries to pick one is told to work the list instead. Nothing else changes: when the 22 reach zero, decide() returns a class again and the rotation carries on exactly as before - there is no separate mode to switch back on. The 22 are 4 [agent] (deployed 550-700 min ago, no finding committed - they died with their runs: check FINDINGS/ for the id and close them as dead, never re-deploy blind), 5 [ratchet] (fixes that landed on their own class and were never proved across the corpus - these are the cheapest wins, 38 documents already moved) and 13 [blocker] rows whose 'can I fix it' names a real action. THE OTHER 59 ARE NOT YOURS AND THEY DO NOT BLOCK YOU. `python3 tools/p2w-bench/pending.py --decisions` prints them: each says 'no - this needs a decision, not a patch'. They stay in BLOCKERS.md and in that view so a person can decide; they are never a reason to sit still. A gate that waited for them would never open, which is why it does not. After the 22: classpick picks by expected fixes - 05_chars_extra, then 32_stroke_lines, then 04_chars_missing (65 documents, never tried) and 25_invisible_text (48, never tried). 18_displacement is 8th because 20 attempts there moved 4 documents.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
