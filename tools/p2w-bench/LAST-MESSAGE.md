# Fixer report - 2026-11-23 15:02

```
# P2W Fixer - Run Report

**23 Nov 2026 · slot 15:02 → 16:38 IST · 1h 36m**


> **Nothing was kept.** One attempt, refuted in Google with the prediction written down first. The
> run's real product is a measurement: the spacer guard *can* be opened on `72_bank`, the -15 pt
> table lift disappears when it is, and the document still fails — because the gap the engine
> computes is about 4.5 pt larger than the page needs. That is a different defect from the one the
> class was being blamed for, and it is now on the record.

## What this run measured

The pod was fresh, so 40 of the 90 minutes went on infrastructure that has to exist before anything
can be measured: `corpus-fetch` (211 PDFs), the engine build, and the corpus conversion. Two things
about that are worth writing down for the next fresh pod.

**1. `ConvertOne` silently produces an empty document when run from the wrong directory.** It reads
its font assets from a *relative* path, `System.getProperty("p2w.assets", "libs/aar/assets")`
(`tools/engine-verify/ConvertOne.java:32`). Run from anywhere but `tools/engine-verify` it exits 0,
prints `pages=1 paragraphs=0`, and writes a 739-byte `document.xml` with no paragraphs and a 0-byte
`.txt`. I measured that as 32/42 in Google before noticing, which would have been reported as a
catastrophic engine regression. It is not one: the same PDF converted from the right directory is
41/42. A run that hand-runs `ConvertOne` must `cd tools/engine-verify` first, and a `paragraphs=0`
line in its output means the conversion did not happen.

**2. `gverify.py --collect` accepts a `file://` URL.** The Drive download tool returns a local
workspace path, not a signed URL, and `collect` pipes its argument to `curl`. `curl -sL file:///…`
works, so a Google measurement is three tool calls and one shell call with no extra plumbing.

## The attempt: the row-excess constant in the spacer guard

`classpick.py --leverage` puts `18_displacement` first at **34.6 CLEAN documents**. The handoff's
proposed lever for it was dead on arrival — a sub-agent re-measured the carrier paragraphs and
`pageBody()` already does the merge — so the attempt went at the guard instead.

`DocxWriter.java:6051` charges a page `15 * pageRowCount` twips of room before it may split a table
gap into `w:before` (which Google honours 1:1) plus a one-twip hairline in `w:line` (which Google
delivers at ~0.155 pt). `72_bank_statement_no_rules_right_amounts` needs 616 tw and has 558, so the
guard refuses it and the whole 18.3 pt gap is written as `w:line`, which Google under-delivers by
~15 pt — measured, not remembered: the table body sat 14.7-15.0 pt high, worst run `10,53,042.55`
at dy -28.24.

At 11 tw/row it needs 544 and fits. **It opened.** The docx went from `w:line="366"` to
`w:before="365" w:line="1"`, and in Google the -15 pt lift vanished — the table body came back
inside tolerance (dy +3.23, ratio 1.07). But the page then sat **4.85 pt low** as a block, including
the header line the table's spacer cannot move, and 7 of 80 runs exceeded tolerance against a budget
of 4. **41/42 before, 41/42 after.** Reverted; nothing committed to the engine.

What that leaves behind: the gap `extraAbs = t.rowTopPt - flowTopPt(ctx)` computes is ~4.5 pt larger
than the gap the page needs. A document that spends it exactly overshoots. That is the next thing to
measure, and it is cheaper than the class it was hiding under.

## The two agents

Both ran and landed inside the turn rather than in the background — a scheduled run has nobody to
answer later, so the platform ran them inline.

`A-displacement` refuted the handoff's lever at HEAD (`pageBody()` already merges; the live gap is
`columnPage()`, and the repo ships an unlanded Google-measured patch for it), and priced the
`18_displacement` mechanism as the table-gap spacer with 7 of the 13 solo-18 documents carrying one.
`B-txt` found that 5 of the 8 `t12_word_invention` documents add **0 characters** under a
whitespace-stripped multiset — they are a check-side artefact, not a writer construct — and that the
writer-side yield of the whole class is 1 document (`600_reviewed_invoice_with_annotations`, whose
annotation `/Contents` is hoisted by `PdfToWord.java:956-965` after the appearance has already drawn
the same text). Neither is a fix; both are recorded here so the next run starts from them.


## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **0** of the **0** re-measured on this engine - **190** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 190 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `00_page_count` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 16:34 | **partial** | 2/23 | LANDED the column-page shape merge (21 documents change in document.xml, 361 124->40 paragraphs, 401 52->27, 301 untouched at 85). Corpus on this tree: 212/212 scored, 0 documents worse, regress PASS, |
| 16:39 | **lead** | 0/None | rowExcessTw 15->11 opens the spacer guard on 72_bank (w:line=366 -> w:before=365+w:line=1) and removes the -15pt table lift, but the page lands 4.85pt low and 7/80 runs exceed tolerance against a budg |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `00_pA-02` | which construct costs 350_question_paper its second  | 16:37 | - | not recorded |
| `gverB-01` | why gverify --collect cannot read the download resul | 16:37 | - | not recorded |

## Timing

| | |
|:--|:--|
| Slot window | 15:02 → 16:38 · 1h 36m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 20 |
| Longest silence | **30.6 min** — from 15:18:23, after `lastmessage.py: running a tool for its numbers` |
| Silences over 2 min | 6 |
| Obstacles | 2 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | `health.py --stalled` exits 0 and the fix row reads moving, 1 attempt(s) in the last 3 h, stage age 1.2 h. `st |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **15 min** | `####` |
| measure or build - a conversion, screen or compile writes no beacon | **54 min** | `#############` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **8 min** | `##` |
| other - not attributed to a tool | **8 min** | `##` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

00_page_count: measure 041122-Account_Opening_Form in Google (2464 drawing-only paragraphs, nine pages, worst score in the corpus at 98.65) - the scale test for the carrier paragraph. Then 350_question_paper: FINDINGS/00_page_count-350-INLINE-PICTURE-CARRIES-THE-LINE-1120-agent.md charges picture() lines 2542-2564 (an unplaced picture emitted <wp:inline> in a paragraph with no w:pPr, inheriting sz=22 and w:after=120 from docDefaults, which spacingTw cannot see); the patch beside it is UNCOMPILED. Then w:tcBorders for 32_stroke_lines/05_chars_extra.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
