
# P2W Fixer - Run Report

**21 Nov 2026 · slot 18:17 → 19:22 IST · 1h 05m**

> **Read the clock with care.** The record above is the window RUN.json holds, and it covers two runs: the
> 18:17 run died at 19:11 holding the slot with its report already pushed, and **this relay claimed the slot
> at 19:26** and worked to 20:45. The 4 attempts before 19:22 are its; the fifth is mine. The dead claim was
> cleared with `--release-fixer --force` after `status.py` read SILENT with no beacon for 11 minutes.
>
> No engine change was kept. What this run produced is a **construct proven on a real document in Google**,
> a saved patch, and the two numbers that were blocking it.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 5 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## The result: the rule carrier lands on a real document

The 18:17 run measured `w:tblpPr` on a synthetic probe and said the next run should convert
`394_map_with_legend` — 3 rules, `32_stroke_lines` alone, 41/42 — and score it. That is what this run did,
and the construct works:

| | Google | LibreOffice proxy | `32_stroke_lines` |
|:--|--:|--:|:--|
| before (engine `7112d76`, committed record) | **41/42** | 42/42 | 1 rule lost |
| after (the patch) | **42/42** | 42/42 | 0 lost |

Both are Google's own export scored by the 42 checks: the before is
`benchmarks/gverify/394_map_with_legend.json`, the after is this run's Drive round trip. Two things the
probe did not know, both of them the engine writing something the page never drew:

* **A table's default cell margin is 5.4 pt.** With no `w:tblCellMar` every rule lands 5.4 pt left of
  `w:tblpPr`'s x; the 20 pt rule then covered **73 %** of its own length against the 80 % floor and read as
  lost. Zeroed, it renders at 395.30 for 395.28 asked.
* **The predicate has to be the instrument's own.** Cut at 2.5 pt, the document's third rule — a 20 x 3.0 pt
  legend swatch — stayed on the anchored-drawing path Google drops, and Google scored **41/42** with exactly
  that rule missing. `RULE_THIN` is **4.0 pt**; the predicate now matches it.

## Why it is a patch and not a commit

`regress.py --check` refuses an engine change the corpus tables were not measured on, and the hook runs it.
Measuring 213 documents costs **~21 s of JVM per document to convert alone** — timed here on
`300_prescription_rx`, 20.8 s — so **~75 minutes** before any rendering or comparison. That is a slot and a
half from a cold sandbox with no corpus, no JDK and no build.

So: `tools/p2w-bench/patches/rule-carrier-tblppr-2008.patch` (186 lines, one file) and
`FINDINGS/32_stroke_lines-RULE-CARRIER-LANDED-2008.md` (the measurement, the traps, what is still
unmeasured). Rebuilt from the patch, the `.docx`'s `word/document.xml` is byte-identical to the one Google
scored 42/42. The next run applies it with `git apply` and measures the corpus.

## What was tried



| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 19:10 | **lead** | 0/15 | RECLASSIFIED 21 Nov from "reverted" to "lead": the construct WAS measured through Google and the finding is committed - it is not a refuted idea, the implementation ran out of slot. tblpPr floating carrier MEASURED THROUGH GOOGLE: rule at y=399.5 for 400pt asked, BELOW at 11.92 = the no-table contro |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **190** (89.2%) |
| Failing at least one check | **23** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

*None deployed this run* — that is the record, and it is the 18:17 run's. **This run deployed one:** an
Explore agent that returned the rule-emission site and a complete 147-line diff for `DocxWriter.shape()`, verified to apply on a fresh clone. It flagged the `tblBorders`/`tblLayout` schema-order question and chose
the `CT_TblPrBase` order, which is correct and which this run then built and measured. It took 5.4 minutes.
**One agent, not the two the brief requires** — the slot was 18 minutes old before the claim succeeded.
That is this run's clearest failure.

## Timing

| | |
|:--|:--|
| Slot window | 18:17 → 19:22 · 1h 05m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 28 |
| Longest silence | **9.2 min** — from 19:11:04, after `report.py: building the report` |
| Silences over 2 min | 7 |
| Obstacles | 4 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **4 min** | `##` |
| fix - diagnose and change the engine | **7 min** | `#####` |
| measure or build - a conversion, screen or compile writes no beacon | **9 min** | `######` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **13 min** | `########` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Judge the t08 verifier question before touching the engine: is t08_line_order measuring line order or drawing order? FINDINGS/t08_line_order-DRAWING-ORDER-1740.md has the numbers (10 of 10 rows clear when only our own line sequence is put into drawing order). The agent's proposed one-line sort of _src_pages is NOT obviously right - it would compare sorted-vs-sorted. Decide with a falsification: construct a .txt whose lines are deliberately swapped in y and confirm t08 still fires after the change. Then take t01_word_accuracy's .docx half or 32_stroke_lines' cell-border construct.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

## Obstacles, and the wall behind the last three reports

* **A dead claim costs the next run 18 minutes.** Three `--claim-fixer` calls each committed locally, lost
  the push to a concurrent cron, then read their own fresh stamp back as "another run claimed first". The
  tool cannot tell its own claim from a stranger's after a failed push.
* **The cold-sandbox tax is 12 minutes** before any work: JDK, the 213-document corpus from the release
  zips, the PDFBox AAR, the engine build. Every run pays it.
* **A 213-document corpus measurement does not fit a slot.** 21 s per document of conversion, one JVM per
  document by design (`ConvertAll` carries state and is banned). Until that is parallelised, **no engine
  change can be committed by any fixer run** — this is the wall behind every "patch ready, no slot to
  measure it" in the last three reports, and it is worth a tool.
* **Two Google Docs left in Drive**, in `KavoPDF-Test-Outputs`: `394_map_with_legend (relay tblpPr probe)`
  and `... (relay tblpPr v2)`. They are the evidence for the two numbers above, and nothing is deleted in
  the user's Drive. Nothing was written to the Drive root.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

