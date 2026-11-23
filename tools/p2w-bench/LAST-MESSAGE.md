# P2W Fixer - Run Report

**23 Nov 2026 · slot 17:58 → running IST · 34 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **0** of the **2** re-measured on this engine - **188** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 188 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `44_header_footer` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 18:33 | **lead** | 0/None | running foot is a row: flowRow anchors it past gapCapTw, Google drops the box text entirely. footBand change measured in Google: 27_two_column_left_short_txtpos 40/42 -> 42/42 PASS, txbx 4->0, pages 1 |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

**Two, both landed, both read, both source-grounded.**

- *txbx rewrite design* — censused every `w:txbxContent` site (one: `DocxWriter.java:5664` inside
  `anchorShape()` at 5580), and proposed deleting the `ctx.positioned` blanket latch at 3126-3133.
  **Refuted this run by census**: `anchorPos=0` on all four 2-3-check documents. Recorded.
- *fill band design* — designed the `w:shd`-in-a-1x1-table rewrite for `25_invisible_text`, and in
  doing so argued against its own premise (`14_filled_shapes` passes 0/213, so Google does keep the
  band as a vector fill). Its `25_invisible_text`-is-an-instrument-bug hypothesis was then **refuted
  by measurement** on `300_prescription_rx` (first-match and nearest fill agree, 0/0 source, 2/2
  render). Both reports are in the slot's transcript; the surviving conclusions are in FINDINGS/.

## Timing

| | |
|:--|:--|
| Slot window | 17:58 → running · 35 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 17 |
| Longest silence | **20.3 min** — from 17:58:36, after `report.py: building the report` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **23 min** | `###############` |
| other - not attributed to a tool | **11 min** | `#######` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

**`44_header_footer` / `04_chars_missing`: the same defect has a second site, and it is the bigger one.**
`FINDINGS/RUNNING-FOOT-IS-A-ROW-GOOGLE-DROPS-THE-BOX-1855-fixer.md` has the root cause and the
patch (`FINDINGS/running-foot-spends-the-gap-1855-fixer.patch`, measured 40/42 -> 42/42 in Google on
`27_two_column_left_short_txtpos`). It is a **lead, not landed**, for one reason only: landing it needs
the whole corpus restamped (`benchmarks/p2w.py --force`), which is minutes the slot did not have.

Do this in order:

1. Run `benchmarks/p2w.py --force` first, before anything else, so the restamp is not the thing that
   runs out of slot.
2. Apply the patch. `27_` and `46_` go to zero text boxes; `55_sidebar_box_beside_body` and
   `61_two_col_abstract_spanning` do **not** — their footer reaches `flowFromBox`, which anchors the
   same oversized gap. **`flowFromBox` is the second site and the larger one.** Fix both, then restamp.
3. Measure in Google, not soffice: Drive upload -> convert to `application/vnd.google-apps.document`
   -> export PDF -> `verify_google.py --docx`. It costs ~90 s a document and the recipe is in
   `FINDINGS/GOOGLE-RENDER-IS-RUNNABLE-IN-A-FIXER-SLOT-1750-fixer.md`.

Do not re-try the `ctx.positioned` latch, the `containerOf` band guard, or the `25_invisible_text`
instrument theory. All three were built or measured this run and all three are refuted above.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

