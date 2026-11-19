# P2W Fixer — Run Report

**19 Nov 2026 · slot 16:11 → 17:18 IST · 1h 07m**

> A justified line was being written left-aligned: the page spreads a line's inter-word spaces to reach its measure and the writer used the face's natural space, so every word on the line slid left by a share of the missing width. Built, measured, and it moves five of the class's ten documents with nothing worse — then the run ended 46 documents into a 213-document corpus pass, so **nothing was kept**. The change is a patch in `patches/`, not an engine commit.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 37 of 212 |
| Corpus improvement vs 15 Nov | **+29.90%** — mean 6.15 → 4.31 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **21** of 212 — the rest are still off |
| Moved but still open | **16** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-partly-lost` |
| Committed | **29** files in 7 commit(s) from `0b8c821` |

## What was tried

| At | Document | Outcome | Moved | What it measured | Verdict |
|--:|:--|:--|--:|:--|:--|
| 16:58 | `content-partly-lost` (10 open) | **partial** | 5/10 | justified lines emitted left-aligned. The model now carries the measured shortfall (`Box.stretchPt`/`Line.stretchPt`, set by `stretchOf()` against a per-page 3rd-percentile gap floor) and `DocxWriter` emits `w:spacing` in `flowFromBox()` and `lineParagraph()`. Screen: `policy-2col-spanning-section-heading` 5.37 → 1.76, `academic-paper-ieee-2col-abstract` 8.09 → 5.02, `magazine-2col-pullquote-spanning` 3.49 → 1.45, `304_package_insert_small_print` 3.41 → 2.47, `landscape-page-inside-portrait-document` 1.45 → 0.62. 5 same, **0 worse**. | **the mechanism is real** — and it is not block placement: the spanning block lands within 0.16 pt horizontally and 1.2 pt vertically, and the displaced ink is the right tail of every justified body line |

## Why nothing was kept

`regress.py --check` is the gate and there is no override: no commit lands unless the whole corpus has been measured with the engine as it stands and no document got worse. The screen passed at 16:58; the corpus pass needs 213 documents at 22–24 per 4.5-minute call, roughly nine calls. Three calls got to **46 of 213** before the run ended. An engine change with no kept attempt is auto-reverted at release, so I reverted it myself and committed the diff as `patches/PATCH-justified-lines-spacing.patch` — `git apply --check` passes against `0a9de90` and the tree is clean.

## The two mistakes that each cost a screen

| Mistake | What it cost | The fix |
|:--|:--|:--|
| A 0.06 em cap on the spacing | 8.09 → 6.54 only. 26 pt of missing measure over 45 characters is 11 twips a character, and 0.06 em at 9 pt *is* 11 | cap is now 0.30 em |
| Measuring a word gap as `next.x − (prev.x + prev.width)` | On `academic-paper-ieee-2col-abstract` every justified line reported `med=NaN` and 0 lines were accepted, because **a space is a glyph** on that document — the gap between two glyph boxes is ~0 | measure from the last **non-space** glyph's advance end; 56 lines accepted |

## A tool bug that was costing every run its work

`round.py --release-fixer` auto-reverts an engine change that no attempt kept. **The commit it reverts to was never written by anything** — `fixer_engine_at_claim` is only ever read, so it held a fossil, `2945cb0`, older than the previous run's kept per-row separator stroke. On this run's first release attempt it checked out that pre-fix engine and **removed a measured, committed fix for 22 documents from the working tree**, printing "reverted: the engine changed this run" and telling me to commit it. A run that obeyed would have published the regression the 18 Nov fix removed. Fixed in `d26141e`: `claim()` now records the field from the live `git log`, and the guard **does not revert a clean engine tree** — when there is no uncommitted engine diff there is nothing to revert, and it refuses instead. Written up in `INCIDENTS.md`.

## Subagents

| Agent | Document | Sent to find | Deployed | Landed | Result |
|:--|:--|:--|--:|:--|:--|
| `6JNXNK2E2K8Y0AJKDXY3J8WQ8Z` | the four 2-column spanning documents | which ink is displaced, horizontal or vertical, and where in the engine | 16:22 | 16:32 | **root cause found, and the obvious suspect refuted** — the spanning block is placed correctly (0.16 pt / 1.2 pt); the displaced ink is the right tail of justified body lines, short by up to 36 pt at the last word, accumulated word by word. `DocxWriter.lineParagraph` emits no `w:jc` and no `w:spacing`. Landed as `1ba1f98`. |

It ran inline for 10 minutes rather than in the background — a scheduled run has no one to answer later, so the platform ran it in the turn. That is the 17.3-minute silence below, and it is why only one agent was deployed.

## Timing

| | |
|:--|:--|
| Session | 16:11 → 17:18 · **1h 07m** |
| Slot window | 16:11 → 17:18 · 1h 07m |
| Before the claim | 0 min |
| Tool beats | 18 |
| Longest silence | **17.3 min** — from 16:11:34, after `pending.py` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 need a human |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **14 min** | `#######` |
| measure or build - a conversion, screen or compile writes no beacon | **31 min** | `###############` |
| record - attempt, handoff, class rows | **1 min** | `#` |

## What the fix is

`PdfToWord` gains `Box.stretchPt` and `Line.stretchPt`. `toParagraphs()` computes a per-page floor from the **3rd percentile** of the page's inter-word gaps — justification only ever widens a gap, so the narrow end is where the face's own space lives — and `buildPara()` sets each box's shortfall to `right − (firstGlyph.x + Σ glyph advances)`. That is a measurement, not a guess: the advances are the face's own, so a ragged line's natural width *is* its extent and its shortfall is zero. Three guards, each a document that got worse without it: a dot leader is already drawn to fill its measure; a complex-script line's substitute face is wider than the page's; and below 3 pt the stretch buys nothing, because `w:sz` is half-points. `DocxWriter.stretchTw()` spreads the shortfall over the line's characters and `runXml` emits it as `w:spacing`.

## Honest gaps

**The `.txt` was not re-scored.** `scope.py` says BOTH, because the model classes changed, so the gate would want the `.txt` measured too. Nothing outside `DocxWriter` reads `stretchPt`, so the `.txt` is *expected* to be byte-identical — but that is a claim about the code, not a measurement, and this run did not turn it into one.

**This implementation is weaker than the lost `855f443`.** `SPEC-justified-lines.md` claims 8.09 → 0.83 and 5.37 → 0.01 with `w:jc="distribute"` plus a right indent at the line's own ink edge. `w:spacing` spreads the missing width over every character, while the page spent it at spaces only, and it gets 5.02 and 1.76. The next step is the spec's own mechanism, not a bigger cap.

**The corpus pass does not resume across runs.** `screen.py` caches under `/scratch/work/p2w`, which does not survive the sandbox, so the 46 documents measured here are worth nothing to the next run. That is why the next run must start the pass from zero and why this run could not finish it.

**`benchmarks/RANKING.csv` is untouched.** It still describes the pre-change engine, which is correct: the engine in the tree is the one it describes.

## Verdict per idea

| Idea | Verdict |
|:--|:--|
| justified-line character spacing (`Box.stretchPt` + `w:spacing`) | **screened, not kept** — 5 of 10 better, 0 worse; the corpus ratchet did not run |
| 0.06 em spacing cap | **dead** — it truncates the fix to a third of what it needs |
| word gap measured from glyph box to glyph box | **dead** — a space is a glyph, and the test sees nothing on the documents it is for |
| block placement / `xyCut` column order as the cause | **refuted twice**, by the subagent with numbers and by this run's own page comparison |

## Next run

Apply `patches/PATCH-justified-lines-spacing.patch`, build, re-screen `content-partly-lost` (expect 5 better, 0 worse), then spend the rest of the run on the corpus pass — `screen.py --docs` with every document in `RANKING.csv`, 22–24 per call in about nine calls, then write `RANKING.csv` and `STATE.json` from `screen-out/dist/*.json`. Re-score the `.txt` too. Do not retry the two mistakes above.

---

*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv.*
