# P2W Fixer - Run Report

**22 Nov 2026 · slot 04:18 → 04:50 IST · 31 min**

> The carrier is not falsified. It is **Google-clean on 13 of the 16 documents already measured through
> Google Docs under it** - all 16 clear `05_chars_extra`, none regresses - and the two runs before this
> one were chasing a blocker that does not exist in the XML. What is missing is 38 Google results, not a
> fix. Nothing was kept this run: the corpus pass that would land it does not fit in a slot.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 04:49 | **lead** | 0/None | Measured the two things the last two runs left open, on committed evidence and two independent measurements: (1) the prescribed cell guard cannot fire - no Shape is ever routed into a w:tc, guard buil |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## What this run adds

The last two runs both worked `32_stroke_lines` and both stopped on a reason that does not survive
measurement. This run measured the two things they left open, and one of them was sitting in the repo
the whole time.

**1. The carrier is Google-clean.** `benchmarks/gverify-carrier-2008/` holds 16 documents scored through
Google Docs with `engine_patch: rule-carrier-horizontal-only-2008` on this same engine (462353f9).
Against the committed HEAD Google results:

| | |
|:--|:--|
| measured under the carrier | **16** |
| reach 42/42 | **13** |
| reach 41/42, `32_stroke_lines` still open | **3** — `315_gazette_notification`, `49_coloured_background_block_paragraph`, `product-catalogue-code-left-price-right` |
| regress in Google | **0** |
| clear `05_chars_extra` | **16 of 16** |

`32_stroke_lines` is worth 36.5 clean documents and `05_chars_extra` 35.2; the `{05,32}` shape is the
largest in the corpus at 16 documents. This one construct clears both, in the renderer the user opens.

**2. The blocker is the proxy, and the prescribed fix for it is a no-op.** The last report named
"a floating table nested inside a table cell" as what kills the carrier, and asked the next run to
guard on it. Two independent measurements:

| test | expected | measured |
|:--|:--|:--|
| carriers are nested in a `w:tc` | tc-depth > 0 somewhere | **max tc-depth 0** across 156 carriers in 22 documents — every carrier's parent is `w:body` |
| the prescribed guard changes the output | some drawings kept | **byte-identical to HEAD on five PDFs** (43→43, 65→65, 1→1, 2→2, 2→2); it never fired once |
| the 54 regressions are cell nesting | displacement inside cells | **no** — 7 of 8 regressed documents gain a page (1 → 2–3 pages), 0 of 14 unchanged documents do |
| displacement scales with carriers per page | dose–response | **no** — 41 carriers gives +15.57, 10 carriers gives +83.89 |

The regressions are body-flow page overflow in LibreOffice. Google does not see them: the same
`product-catalogue-code-left-price-right` that is +85.26 on the proxy scores **41/42 in Google**.

**3. The gate already has the door open.** `regress.py` says, in its own words: *a LibreOffice
regression is allowed when Google improved on the same document*. It needs `benchmarks/gverify/<doc>.json`
in the working tree. Sixteen documents have a carrier result; the rest of the regressed set does not.

## What the next run should build

Not a narrowed predicate, and not the cell guard. **Apply `patches/rule-carrier-horizontal-only-2008.patch`,
run the corpus pass, and close the missing Google results** with `gverify.py --plan 60` on the documents
that regressed and have no carrier result. Each one that improves in Google is then allowed by the gate's
own rule; each one that does not is a real regression and stays out. Land the patch and the gverify
results in the same push.

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `32_sA-03` | can the emitter tell its drawing anchor is inside a  | 04:49 | 23:19 | 0 min |
| `32_sB-02` | is the 54-document carrier regression cell nesting o | 04:49 | 23:19 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 04:18 → 04:50 · 31 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **29.6 min** — from 04:18:54, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **29 min** | `#####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Apply tools/p2w-bench/patches/rule-carrier-horizontal-only-2008.patch, build, run the corpus pass and take the exact LO regressions. The 16 documents already measured in Google under this patch are in benchmarks/gverify-carrier-2008/: 13 reach 42/42, 3 reach 41/42, none regress, all 16 clear 05_chars_extra. regress.py already exempts a LibreOffice regression when Google improved on the same document - it needs benchmarks/gverify/<doc>.json in the working tree. So run gverify --plan 60 over the regressed documents that have no carrier result, and land the patch with those results in the same push. Do NOT build the cell guard the last report asked for: no Shape is ever routed into a w:tc (max tc-depth 0 across 156 carriers in 22 docs) and the guard built byte-identical output on five PDFs.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
