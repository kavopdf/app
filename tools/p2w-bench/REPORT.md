# P2W Fixer - Run Report

**23 Nov 2026 · slot 13:20 → running IST · 2h 44m**

> No change was kept this run. The carried lever was refuted in Google with three probe documents, and the
> class it was aimed at turned out not to be one class.

## The class choice, and why

`classpick.py` suggested `18_displacement` (34.5 CLEAN documents). I took `00_page_count` instead, and the
reason is arithmetic: the 23 `page_count_refused` documents are **not in the 42-check denominator at all**.
A document that draws the wrong number of pages is refused, so nobody has ever scored it — `60_page_border`
is refused while LibreOffice scores it **41/42**. Twenty-three documents sit outside the measurement, and
`00_page_count` is the only class whose fix turns an unscored document into a scored one. 18_displacement
was worked at 13:20 and 14:58 and reverted twice; the question worth buying with this slot was why a third
of the refusals exist.

## What the measurement found

The 13:20 report's NEXT LEVER was: *Google keeps the empty paragraph that carries a page-positioned shape,
it costs ~0.83 pt, merge them into one paragraph.* Measured on HEAD, in this order:

1. **The carrier paragraphs are not there.** Converted all 23 with `ConvertOne`, one JVM each: **18 of 22
   have zero drawing-only paragraphs**. Only `041122` (2), `401_trifold_brochure` (21) and
   `361_product_catalogue_grid` (91) have any. The 2 464 the 0530 finding cites are not in this tree.
2. **LibreOffice renders the right page count on 21 of the 22.** Only `041122` is wrong locally (9 → 10).
   So the class is Google-only, and the "fixed-in-LO-only 23" column is the honest description of it.
3. **Three Google probes, on HEAD, uploaded → converted → exported → deleted.** `60_page_border` renders
   **2 pages with 0 characters on page 2**, and its 62 `wp:anchor` shapes arrive as **62 rasterised images
   split 46 / 16 across the two pages**. `350_question_paper` also renders 2 pages, but page 2 carries 8
   real characters — a genuine one-line overflow, a different fault wearing the same class name. Adding a
   trailing empty paragraph to `60_page_border` changed nothing: 2 pages before, 2 pages after.

So the mechanism is **Google rasterising N independent page-positioned shapes and laying them out in flow**,
not the paragraph that carries them. The falsifiable next test is one probe: replace `60_page_border`'s 62
shapes with one shape, or with `w:pgBorders`, and Google should render 1 page. That is a `DocxWriter`
change and it was not made in the remaining minutes — an unmeasured engine change is a guess, and rule 2
says a guess goes in FINDINGS.

## Note on the run record — a pipeline bug with evidence

`RUN.json` says this run started at **13:20** with **2 attempts**; the claim this run took was stamped at
**15:16**. The 13:20 run was killed and never released its slot, and `round.py`'s takeover path refreshed the
claim without calling `_run_record("start")` — the archive-and-restart block at `round.py:512-533` sits in
the *no-existing-claim* branch, so a stale claim is taken over silently. The consequence is that this run's
duration and attempt count are reported against the dead run's record: the 2h 44m below is 1h 48m of the
13:20 run plus this one. `runclock.py` reads the claim, not `RUN.json`, and correctly said 33 min at 16:18.
Not fixed — it is a change to the round machine, and it wants its own measurement.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **0** of the **2** re-measured on this engine - **188** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 188 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `00_page_count` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 14:02 | **reverted** | 0/None | partial spend of the table-gap spacer: Google 68_journal 41/42 -> 40/42, adds 59_shape_anchor, fixes nothing; flow-invariant so LibreOffice could not have caught it |
| 16:05 | **lead** | 0/None | Measured the 23 page_count_refused documents on HEAD: 18 of 22 have zero drawing-only paragraphs, so the carried 'carrier paragraph costs 0.83pt' lever is dead. 21 of 22 render the correct page count |

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
| `A-merge` | the column-page shape merge: does the handoff's `shape()` lever exist at HEAD, and where is the live gap? | 15:17 | 15:28 | 11 min |
| `B-anchors` | `anchorShape()`'s one-paragraph-per-anchor carriers: how many, how safe to collapse, worth a slot? | 15:28 | 15:49 | 21 min |

## Timing

| | |
|:--|:--|
| Slot window | 13:20 → running · 2h 45m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 30 |
| Longest silence | **52.3 min** — from 14:16:06, after `relay: fixer claimed the slot (the :50/:10 slot, found free)` |
| Silences over 2 min | 10 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **23 min** | `###` |
| measure or build - a conversion, screen or compile writes no beacon | **1h 08m** | `#########` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **1h 01m** | `########` |
| other - not attributed to a tool | **11 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

00_page_count: mechanism MEASURED, fix not landed. FINDINGS/00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md. Google rasterises each page-positioned floating shape and keeps the paragraph that carries it, and that empty paragraph costs ~0.83 pt of flow (w:line="1" exact is NOT honoured for it): 108 of them = 89.9 pt on 301_lab_report_panel against 44.5 pt of free page, so a 1-page source renders 2 pages. Deleting all 108 -> 1 page at the same text y (the control). 22 of the 23 refused documents emit ALL their drawing-only paragraphs AFTER the last text paragraph; counts 7..2464. 350_question_paper has 1 and is NOT explained by this. Refuted and measured, do not retry: drop-last, prstGeom-rect, wrapSquare, framePr. VOID (my probe bug, never measured): merge-into-one-paragraph and attach-to-text. NEXT LEVER, cheapest in the writer: merge the drawing-only paragraphs of a page into ONE (DocxWriter.shape(), DocxWriter.java:2726) - saves 107 x 0.83 = 88.8 pt against 89.9 pt needed here, a one-point margin, so measure it; then w:tcBorders through the table writer. This is the same construct as 32_stroke_lines and 05_chars_extra: one mechanism, three check families.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

## Subagent results

`A-merge` — the handoff's proposed lever is **already in the tree**: `pageBody()` at 1318-1414 writes a
page's shapes as bare runs joined to an existing paragraph, so re-implementing it in `shape()` (2893, not
2726) is a no-op. The live gap is the **column page** path, `columnPage()` 1745 → `after.add(b)` 1985-1989 →
`emitBlock()` 2271, and the repo already ships an unlanded, Google-measured patch for it. Agent re-verified
it: applies clean on HEAD, compiles, `<w:p>` 40 → 29 on a synthetic two-column page with all 12 `wp:anchor`
offsets identical and in order, LibreOffice 1 page both ways. **0 documents claimable CLEAN**: the four
re-measured in Google after a merge came out 39/42, 37/42, 41/42 and one still refused.

`B-anchors` — `anchorShape()` (5523, `<w:p>` written at 5583) writes **one complete `<w:p>` per anchored text
box**; 1 037 of the corpus's 1 319 drawing-only paragraphs come from it, across 61 documents. A post-pass
`collapseAnchorParas(pg)` at the two `pageBody()` call sites removes **920 paragraph marks on 38 documents**
and is provably anchor-preserving: all 213 documents keep every anchor attribute, offset, `relativeHeight`,
`behindDoc` and document order, and mechanically re-splitting reproduces the old `document.xml` byte for byte
in 211/213. LibreOffice page count unchanged on all 38, 33/38 pixel-identical. It buys **45.7 pt** of the
engine's own flow model corpus-wide. **Not applied** — no Google measurement, and no document becomes CLEAN
on that evidence alone.

Both patches are committed under `tools/p2w-bench/FINDINGS/` with their measurements, unapplied.
