# P2W Fixer - Run Report

**20 Nov 2026 · slot 06:53 → running IST · 1h 06m**

> One fix kept, and it is a real engine bug rather than a tuning knob. **A nested table inside a
> layout cell never cleared the cell's anchor**, so the first paragraph after it was placed against
> the *layout row's* top edge instead of the nested table's bottom. On `table-inside-two-column-page`
> the caption under the metrics table carried `w:before="2600"` (130 pt) where the page drew 4.2 pt,
> and the caption plus the three paragraphs below it sat **115.4 pt too low** — 78 % of that
> document's whole deficit. One line fixes it. Corpus ratcheted 212 of 213 with nothing worse, and
> the Google result for the improved document is **byte-identical to the pre-change one**.

## Progress

| | |
|:--|:--|
| Documents improved this run | **1** — 2 attempt(s), 1 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **32** of 213 — the rest are still off |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-partly-lost-and-displaced` |
| Committed | **16** files in 1 commit(s) from `8ae59eb` |

## Timing

| | |
|:--|:--|
| Slot window | 06:53 → running · 1h 06m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 23 |
| Longest silence | **45.5 min** — from 07:13:33, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 need a human |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **5 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **59 min** | `####################` |
| report - the report and the chain | **0 min** | `#` |

## The fix

`columnPage()` sets `ctx.afterTablePt = rowEndPt` for each cell so the cell's first line is placed
against the layout row's top edge. When the cell holds a **nested `w:tbl`**, `table()` writes the
table and its 4 pt carrier as raw XML — the carrier never passes through the paragraph path — so
nothing cleared `afterTablePt`. The next paragraph took the `afterTablePt` branch in `flowFromBox()`
and was placed at `topPt - afterTablePt`: the distance from the **row's top**, not the table's bottom.

Instrumented on the document (temporary stderr prints, since removed):

    NESTED top=117.0 bottom=228.0 rowBottom=228.0 flowY=-1.0 afterTbl=107.4 carrier=true carrierTw=80
    BIGBEFORE before=2600 absTop=237.37903 flowY=232.0 inCol=true newPage=false y=237.7544

`flowY` was already correct (232.0 = row bottom 228 + 4 pt carrier). The paragraph was placed from
107.4 instead. The change is `ctx.afterTablePt = -1f` when `ctx.inColumn`, in `table()`'s row-bottom
block — the paragraph is then placed from the flow, which is where the reader is.

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `table-inside-two-column-page` share@5 | 38.11 | 35.87 | -2.24 |
| — share@10 | 29.13 | 9.70 | -19.43 |
| — max_pt | 82.08 | 21.60 | -60.48 |
| — p90_pt | 64.32 | 6.24 | -58.08 |

The share@5 gain is small because what is left on that page is a uniform ~2.9 pt offset (median
2.88 pt = 6 px), not the 115 pt outlier — the outlier is gone and share@10 and p90 say so.

## The gates

| Gate | Result |
|:--|:--|
| Class screen (6 docs) | 1 better, 5 same, **0 worse** |
| Corpus ratchet | **212 of 213** re-measured, 1 better, 211 same, **0 worse** |
| `regress.py --check` | **PASS** — docx and txt, table matches engine `4089fdf7bf647365` |
| Google (`gverify.py`, Drive round trip) | **42/47, identical to the pre-change result** — same five fails (`04_chars_missing`, `05_chars_extra`, `18_displacement`, `32_stroke_lines`, `44_header_footer`) |

The Google leg was run as the brief requires: the document the change improved was staged, uploaded
to Drive as a Google Doc, exported to PDF and scored through the 42 checks. The stored pre-change
result is in `benchmarks/gverify/`; the two files are identical field for field.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **167** (78.4%) |
| Failing at least one check | **46** |
| Most common failure | `t13_amount_columns` - 18 documents |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 07:13 | **partial** | 1/6 | attempt 14: a nested table inside a layout cell no longer leaves the cell's afterTablePt pointing at the layout row's top - it is cleared so the first paragraph after the nested table is placed from flowY (the row bottom + carrier) |
| 07:59 | **kept** | 1/6 | ratchet stamp for attempt 14: 212 of 213 documents re-measured on the new engine, 1 better, 211 same, 0 worse; regress PASS on docx and txt; Google identical 42/47 |

## Subagents

Two, both landed this run, both read-only.

| Agent | Sent to find | Answer |
|:--|:--|:--|
| `contA-07` | is the justified-line spacing fix missing from the engine, or already landed | **Already landed** — every `+` line of `PATCH-justified-lines-spacing.patch` is in the tree as commit `4147d54`. The patch fails to apply because it is already applied. |
| `contB-07` | why two documents lose ~60 % of their ink at 5 px — absent or moved | **Neither loses any ink.** `text_recall 100`, chars equal, 0 unmatched words. It is all displacement: A is the nested-table anchor above; B (`itr-computation-with-slab-table`) is table row pitch: 351 and 370 tw against the page's 368. |

## Two things worth carrying forward

1. **`itr-computation-with-slab-table` is the next document in this class and it is a different
   mechanism.** Rows are written at their own `w:trHeight` — 351 and 370 tw — against the page's uniform
   368, so the page compresses ~0.5 pt a row and −14.31 pt by the last row. share@5 42.33,
   share@10 27.40, share@20 7.85. `DocxWriter.java:6182` and `:6271-6273`; the arithmetic that
   yields 351 is **not** verified — that is the first thing to check.
2. **The rule class is still blocked by the gate, not the engine.** Nothing this run changes that.
   It needs a human: gate it in Google, declare it out of scope, or authorise a stated tolerance.

## Obstacles

None cleared, none needing a human beyond the rule-class question already standing in
`BLOCKERS.md`. One tooling note for the next run: `screen.py --docs` with all 213 names stops
making progress after ~117 documents inside the 290 s command limit, and a call killed by
`timeout` loses its buffered output — run it in explicit batches of ~30 with `python3 -u`, which
measured the remaining 92 documents in four calls.

## Next run

`content-partly-lost-and-displaced`: start with `itr-computation-with-slab-table`'s row pitch. The
other four OPEN documents in the class are `31_times_body_arial_headings` 1.04,
`370_offer_letter` 2.70, `14_stamp_chars_positioned_td` 3.89 and
`75_merged_header_cell_three_columns` 7.62.
