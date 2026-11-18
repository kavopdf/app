# P2W Fixer — Run Report

**18 Nov 2026 · session 18:00 → 19:12 IST · 1h 12m**

> One missing `w:tcBorders` broke twenty-two documents at once: a table's heavier header rule was collapsed into the table's single `insideH` and drawn nowhere, and emitting it per row took `salary-slip-factory-wages` from 18.09 to 0.73 and the corpus mean from 6.15 to 4.46 with nothing worse.

## Progress

| | |
|:--|:--|
| Documents improved this run | **22** — 1 attempt(s), 1 kept |
| Documents improved, round total | 36 of 212 |
| Corpus improvement vs 15 Nov | **+27.52%** — mean 6.15 → 4.46 |
| Regressions | **none** |
| Exempt, not measured | **1** — `416_many_tiny_pages` |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-missing-nothing-in-its-place` — **10 open, down from 29**, 8 of the 10 already below 5.0 |
| Open documents, whole corpus | **70**, down from **91** at the start of the run |
| Committed | **34** files in 2 commit(s) from `139599f` |

## What was tried

| At | Document | Outcome | Moved | What it measured | Verdict |
|--:|:--|:--|--:|:--|:--|
| 19:07 | `salary-slip-factory-wages` (+21 more) | **kept** | 22/29 | per-row separator stroke: table interior rules whose weight or colour differs from the table's `insideH` are emitted as per-cell `w:tcBorders/w:bottom` instead of collapsing into one border. `salary-slip-factory-wages` 18.09 → 0.73, `mobile-bill` 18.48 → 1.55, `two-tables-stacked-with-no-gap` 17.20 → 0.77. Full corpus 212 measured: 33 better, 179 same, 0 worse. | **the mechanism was real** — a geometric loss, not a flow one |

## Subagents

| Agent | Document | Sent to find | Deployed | Landed | Took | Result |
|:--|:--|:--|--:|--:|--:|:--|
| `5S300FMPRQ93E9CSJF7KM2K2KV` | `salary-slip-factory-wages` | why a page whose every baseline is within 1.5 pt still has 18 % of its ink 26–71 pt out | 18:31 | 18:54 | 23 min | **root cause found** — 4 000 of 22 818 source ink pixels were three 0.9 pt header rules the page draws over a 0.45 pt grey one; `insideStroke()` collapsed both into the table's single `insideH`, so 96.9 % of the far ink was drawn nowhere |

## Timing

| | |
|:--|:--|
| Session | 18:00 → 19:08 · **1h 08m** |
| Slot window | 18:00 → 19:08 · 1h 08m |
| Before the claim | 0 min - pod setup, cloning and retries |
| Tool beats | 20 |
| Longest silence | **66.9 min** — from 18:00:10, after `gaps.py: reading the timeline` |
| Silences over 2 min | 1 |
| Obstacles | 1 cleared · 0 need a human |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **1h 06m** | `######################` |
| record - attempt, handoff, class rows | **0 min** | `#` |

## What the fix is

`DocxWriter.table()` had one `w:tblBorders insideH` for a whole table, so when a page drew one interior rule heavier or darker than the rest — the usual header rule under a table head — the writer collapsed it into the table's body rule and the heavier stroke was drawn nowhere. The engine now carries `Table#rowStroke`: each separator's own stroke, read through `edgeStroke()`, which prefers the heavier rule when two are drawn on top of each other. Where that stroke differs from the table's `insideH` by at least one eighth-point or in colour, `table()` emits a per-cell `w:tcBorders/w:bottom` for that row instead. Interior edges only; a table without such a rule emits byte-identical output, which is why 179 of 212 documents did not move by a single point.

## Best results, round to date

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `salary-slip-factory-wages` | 18.09 | 0.73 | -17.36 |
| `mobile-bill` | 18.48 | 1.55 | -16.93 |
| `two-tables-stacked-with-no-gap` | 17.20 | 0.77 | -16.43 |

## Honest gaps

The corpus number is real but it was not produced by `benchmarks/p2w.py`. `p2w.py --budget 260` does not resume: it restarts `docx 0/213` on every call and spends the whole budget converting, so it measured **0 of 213 twice in a row**. The 212-document ratchet was run with `screen.py --docs` over the full `RANKING.csv` list instead, which does cache and resume; `benchmarks/RANKING.csv` and `benchmarks/STATE.json` were then written from those 212 measurement files. That is the same instrument `p2w.py` uses, but it is not the pipeline's own publisher, and the next run should confirm the two agree.

`416_many_tiny_pages` is still unmeasured — 300 pages, one command, no result written. `itr-computation-with-slab-table` (42.33) was not touched; its third defect, the footer row of table 3 emitted between rows the page draws around it, is still the only item left standing in `content-partly-lost-and-displaced`.

Eight of the ten documents still OPEN in this class already score below 5.0 — they are open because the class row asks for *clean*, not for *under the line*. `annual-review-2col-uneven-columns` (5.77) and `23_timetable_grid_txtpos` (5.16) are the two that still have ink in the wrong place, and neither has a heavier interior rule to explain it.

`chain.py --after-release` still reports the sandbox at `2945cb0` against origin `4c48b1a`, because the commit was published through the GitHub API and the local `HEAD` cannot advance without a push. The work is on `main` at `139599f`; only the local ref is behind.

## Why the silence

The 66.9-minute gap is not a hung run. It is the one inline subagent (23 min, no beacon while it converted and rendered) followed by the corpus ratchet: six `screen.py --docs` calls at roughly five minutes each, each one converting and soffice-rendering its own batch. A conversion loop and a soffice render write no beacon, exactly as `SETTLED.md` warns.

## Verdict per idea

| Idea | Verdict |
|:--|:--|
| per-row separator stroke (`Table#rowStroke` + per-cell `w:tcBorders`) | **kept** — 33 better, 0 worse on 212 |
| `p2w.py --budget` as the corpus pass | **dead here** — it cannot finish inside the 300 s cap and does not resume |
| re-testing `run-size-from-sizePt-not-Tf`, the anchor rule, the cell-baseline fallback | not attempted — all refuted on this engine, recorded in `SETTLED.md` |

## Next run

Take `content-partly-lost` (9 open). The corpus pass is `screen.py --docs "$(python3 -c "import csv;print(','.join(r['document'] for r in csv.DictReader(open('benchmarks/RANKING.csv'))))")"` — about six calls, and it resumes. Do not spend a call on `p2w.py --budget`, and do not retry the row separator stroke: it is implemented.

---

*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv.*
