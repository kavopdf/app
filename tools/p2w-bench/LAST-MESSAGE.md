# P2W Fixer - Run Report

**23 Nov 2026 · slot 17:00 → running IST · 42 min**

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
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 17:41 | **lead** | 0/190 | Google render is runnable in a fixer slot: JDK from GitHub releases + verify-engine compile + Drive round trip. Two rows re-measured on HEAD in Google, see below. |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

**Two, both landed, both read.** `Google hides our text` and `Google moves our text` - the two halves of the largest class in the corpus. Committed as `FINDINGS/04_chars_missing-25_invisible_text-TXBX-IS-RASTERISED-1750-agent.md` and `FINDINGS/18_displacement-FOUR-MECHANISMS-AND-THE-ROWPITCH-REFUTATION-1750-agent.md`.

## Timing

| | |
|:--|:--|
| Slot window | 17:00 → running · 42 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **33.0 min** — from 17:00:55, after `gaps.py: reading the timeline` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **33 min** | `##################` |
| measure or build - a conversion, screen or compile writes no beacon | **7 min** | `####` |
| report - the report and the chain | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## What this run established

**1. The Google render is not a credential the pipeline is missing. It is a JDK the sandbox does not
ship.** `PENDING-NOW.md` opens by saying nothing on its list can be closed without `java`, and reads
as if a run may or may not be able to measure. It can. Temurin 17 comes off a GitHub release in 34 s,
`tools/verify-engine.sh`'s four maven URLs supply PDFBox, the engine compiles in 28 s, and three
Drive calls give Google's own render of any document. The full recipe, timed, is in
`FINDINGS/GOOGLE-RENDER-IS-RUNNABLE-IN-A-FIXER-SLOT-1750-fixer.md`. Every future run should do this
at the top of its slot and measure its change in Google, not in soffice.

**2. Two Google rows moved off the old engine, and one of them improved.** Both documents were
sitting on `462353f`; both are now measured on HEAD `b7699196`:

| document | was | now | cleared |
|---|---|---|---|
| `bank-statement-5-pages` | 40/47 | **42/47** | `05_chars_extra`, `32_stroke_lines` |
| `mobile-bill` | 46/47 | 46/47 | none - confirmed not worse on HEAD |

`bank-statement-5-pages` gaining two checks is a result the pipeline did not have, because the table
was reporting an engine two commits back. `mobile-bill` is now the corpus's cleanest single-construct
test case: at HEAD it fails **one** check, `18_displacement`, and nothing else.

**3. The largest class in the corpus has a named construct, and it is not displacement.**
`18_displacement` fails 101 documents in Google against 20 in LibreOffice. The agent measured where
the failing text lives: 44.8% of characters in table cells, 52.9% in plain paragraphs, 2.3% in
anchored text boxes; the engine emits no `w:framePr` and no multi-column sections. So the class is
reflow, not placement, and it is four mechanisms: a table-gap spacer spent in `w:line` (53 documents),
a page-top gap in `w:before` (16), text inside an anchored shape (23), and table row pitch (30).

**4. Two of those four are already refuted in the source, and the agent did not know.**
`DocxWriter.java:6396-6402` records that subtracting a quantum from `w:trHeight` was measured and
lost more documents than it fixed (electricity-bill's 18.0/19.0 alternation became 17.5/18.5). The
agent's Rank 3 recommendation is that exact change. The row-pitch floor stands.

## The construct worth the next attempt

`04_chars_missing` fails 65 documents in Google and 2 in LibreOffice; `25_invisible_text` fails 48 and
0. The agent found the separator, and it is clean:

| face | construct | failing docs carrying it | clean docs carrying it |
|---|---|---:|---:|
| text dropped | text in `<wps:txbx><w:txbxContent>` inside an anchored `wps:wsp` | **54 of the 65** | **0 of the 30** |
| text hidden | a fill band written as a shape behind white flow text | **48 of the 48** | **0 of the 30** |

Google rasterises the shape, so its text leaves the text layer and its fill leaves the ink layer.
Every other candidate was counted and refuted on real XML - `w:vanish`, `w:specVanish`, `w:webHidden`,
`w:position`, `w:framePr`, `w:fitText`, `w:shd`, `w:highlight`, `w:spacing`, `w:trPr/w:hidden`,
`w:ins`/`w:del`, `w:tblpPr`, VML - absent from all three sets. This is the largest single lever found
this round and it is the next attempt: route a shape's text into the flow, or into a 1x1 table that
carries the fill as `w:shd`, and keep `wps:txbx` only for rotated lines.

## What I did not do, and why

I made no engine change. Each candidate was checked against the source before being built: the
spacer split is refused by an arithmetic guard that reserves the row excess it correctly predicts
(reducing the reservation spills the table, and partial spend is refuted by live Google measurement);
the row-pitch rung is refuted in `DocxWriter.java` itself; the `wps:txbx` rewrite is the right fix but
is a structural change to every anchored shape and this slot reached it with 15 minutes left, which is
not enough to build, convert and Google-measure it honestly. It is recorded as the lead instead of
being half-landed. `regress.py --check` passes and nothing was made worse.

## Next run

`04_chars_missing`/`25_invisible_text` via `wps:txbx`: take `300_prescription_rx` (a fill band behind white text), `66_two_col_footnotes_bottom` (footnote text in a `wps:txbx`) and `mobile-bill` (the single-check `18_displacement` case) - convert all three at HEAD and Google-render them as the before, then move the shape text into a 1x1 table carrying `w:shd` and re-render. The rig is in `FINDINGS/GOOGLE-RENDER-IS-RUNNABLE-IN-A-FIXER-SLOT-1750-fixer.md`; build it first, it costs 90 s. Do not re-try the row-pitch rung - `DocxWriter.java:6396-6402` already measured it.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

