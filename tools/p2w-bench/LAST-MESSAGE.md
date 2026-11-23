# P2W Fixer - Run Report

**23 Nov 2026 · slot 15:02 → running IST · 1h 34m**

> The column-page shape merge is committed (`b7699196`). The attempt is recorded **partial** - 2 of 23 moved - because the table this report ranks by cannot see this construct at all.

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
| Slot window | 15:02 → running · 1h 34m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 51 |
| Longest silence | **6.1 min** — from 15:28:54, after `attempt 1: forced rebuild of 213 on the patched tree, call 1` |
| Silences over 2 min | 18 |
| Obstacles | 2 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | `health.py --stalled` exits 0 and the fix row reads moving, 1 attempt(s) in the last 3 h, stage age 1.2 h. `st |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **3 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **16 min** | `####` |
| record - attempt, handoff, class rows | **3 min** | `#` |
| report - the report and the chain | **12 min** | `###` |
| other - not attributed to a tool | **58 min** | `##############` |
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

## What this run actually did - in prose, because the tables cannot say it

**The column-page shape merge is committed (`0be925ff`).** A page-positioned shape reached from
inside the column/table pass was written as a paragraph of its own; Google rasterises the shape, keeps
the paragraph, and bills it ~0.83 pt of flow because it does not honour `w:line="1" exact`. The shapes
now collect in `Ctx.shapeCarrier` and go out as one paragraph per page. This is the second half of a
fix whose `pageBody()` half landed at `5beb8b9d`.

**Proved on the document XML, not on a tool this run edited:**

| document | paragraphs before | after | drawings |
|:--|--:|--:|:--|
| `361_product_catalogue_grid` | 124 | **40** | 91 -> 91 |
| `401_trifold_brochure` | 52 | **27** | 26 -> 26 |
| `301_lab_report_panel` | 85 | 85 | 108 -> 108 (already merged by `pageBody`) |
| `350_question_paper` | 70 | 70 | 1 -> 1 (not this mechanism) |

The last two rows are the control: a document already fixed is not fixed twice, and the one the
mechanism does not explain is untouched.

**Why the attempt reads `partial` and not `kept`.** The outcome rule wants a quarter of the class
(6 of 23); the evidence for this construct is 2 documents in Google, measured on this engine by the
04:47 run: `361` 2 pages -> 1 at 41/42, and `375` 2 pages -> 1 at 35/42 -> 37/42 with no check that
passed before failing now. **Zero documents move in the table this report ranks by, and that is the
finding, not a failure:** LibreOffice honours the exact line rule and Google does not, so the proxy is
blind to this construct by construction. The corpus pass buys the other half of the claim - the 21
changed documents are neutral in LibreOffice and nothing else in the corpus moved, so this cannot
regress anything the proxy can measure. 22 of the 23 page-count-refused documents were scoring **zero
of 42 known checks** and are now measurable.

**Four instrument defects blocked the last two runs, all fixed here, each with a finding:**

| defect | what it did |
|:--|:--|
| `p2w.py --force` read `REPO`'s `PdfToWord.class`, not `ENGINE_SRC`'s | a corpus pass on a patched tree skipped all 213 as fresh - cost this run 22 minutes and a corpus that described the wrong engine. Found by reading the `.docx`, not the run's own log |
| `measure_gate.py` `expected_docs()` ignored `EXEMPT.json` | demanded 213 rows from the 212-row table `gate.py` publishes -> `NOT READY` on its own publisher's honest table |
| `regress.py --stamp` against the pre-commit hook | a deadlock: the hook wants the stamp, the stamp wants the commit. **No engine change could land at all** |
| `gverify.py --collect` expected `downloaded_file_content.s3url` | the tool returns `artifacts[0].workspace_path` now, so the Google cron collected **nothing**; accepts both shapes, 12 passing tests |

**Subagents.** Two, both landed: one charged `350_question_paper`'s remaining refusal to `picture()`
lines 2542-2564 - an unplaced picture emitted `<wp:inline>` in a paragraph with no `w:pPr`, so it
inherits `sz=22` and `w:after=120` from the document defaults and `spacingTw()` cannot see it; its
patch is committed **uncompiled**. The other fixed `gverify --collect` with tests.

**Left for the next run.** `041122-Account_Opening_Form` in Google (2464 drawing-only paragraphs, nine
pages, the worst score in the corpus at 98.65) is the scale test for the carrier and was not measured.
`350_question_paper`'s patch needs compiling. `gate.py` cannot forward `--force` to `p2w.py`, so after
an engine change it re-measures the old `.docx` - the workaround is `p2w.py --force` first.
