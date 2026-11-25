# Fixer report - 2026-11-25 20:12

```
# P2W Fixer - Run Report

**25 Nov 2026 · slot 20:12 → running IST · 6 min**

> No change was kept this run. The last run's first attempt was taken, reproduced, and **refuted on
> the docx side** - the txt gets one document cleaner and the docx loses 12.71 share5 on that same
> document, because the two paragraphs it deletes sat at the top of the page and the body reflows.

## Progress

| Check-instances passing | **8702** of 9320 (93.4%) on 213 documents |
| Check-instances still failing | **618** |
| Kept attempts vs documents clean | **15** classes with a kept attempt, **42** documents clean - a kept attempt is progress inside a class, not a finished document |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 0 vs ATTEMPTS.json history 1; subagents: 2 deployed vs no FINDINGS file for t12_A-01, t12_B-01 |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (18 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 20:12 | **lead** | 0/None | annotation /Contents hoist patch (PATCHES/600-annotation-runs-subtype-25NOV.patch) reproduced on one engine: 600_reviewed_invoice_with_annotations txt 7/8 -> 8/8 PASS, t12 83 chars -> 0, paragraphs 14 |


### What the numbers are

**The txt half, on one engine, the patch the only difference.** `ConvertOne` twice on
`600_reviewed_invoice_with_annotations`, same pod, same PDF, only `PdfToWord.java` differing.
Paragraphs 14 to 12, and `verify_txt.py` goes 7 of 8 applicable FAIL to 8 of 8 applicable PASS,
`t12_word_invention` 83 invented chars to 0. The whole `.txt` diff is two lines: the note
("Rate for HSN 8536 confirmed with PO.") that no page draws, and the FreeText written a second time.

**The population, by bytes.** `corpus-changed.py --record` after rebuilding all 213 on the patched
engine: 1 changed, 0 never measured - that document and nothing else. 212 outputs are byte-identical,
so no score of theirs can differ.

**The docx cost.** `p2w.py` on the patched tree measured 600 at share5 38.97 where the committed row
(engine `9e2b3e4d`, 13:47) says 51.68; median 11.04 to 6.72, p90 48.96 to 32.64, max 62.88 to 37.44,
text_recall 100.0 and chars_missing 0 both unchanged. The ink did not go missing, it moved up. Rule 3
refuses this. The before column is an older engine, so the 12.71 points include drift and are not yet
proved to be the patch's cost - the A/B is one document and two conversions, and it was not run
because the slot ran out.

**Two agents, in the first ten minutes.** One audited the guard site: the hoist is in `readPage()`
(there is no `pageText()`), the guard is genuinely missing at `:956`, and `annotationContentsOf()`
holds the correct subtype rule while being dead code with zero call sites. The other root-caused the
"(Authorised signatory)" duplication: one page glyph, two model entries, a cell-versus-line granularity
mismatch where `buildRowTable` marks the cell copy consumed and never the raw line, and the duplicate
guard keys on exact text equality so it cannot fire on a weld. Neither diff was applied.

## The txt

| | |
|:--|:--|
| Measured | **1.0 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **204** (95.8%) |
| Failing at least one check | **9** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t12_A-01` | audit the annotation hoist guard: pageText does not  | 20:15 | - | - |
| `t12_B-01` | root-cause the (Authorised signatory) duplication: c | 20:15 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 20:12 → running · 6 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 12 |
| Longest silence | **2.1 min** — from 20:12:19, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **2 min** | `#########` |
| report - the report and the chain | **2 min** | `##########` |
| other - not attributed to a tool | **0 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

**FIRST, and it is one document:** settle whether the annotation patch's docx cost is the patch or
drift. Revert, convert `600_reviewed_invoice_with_annotations` with HEAD, measure, compare against the
patched run in `FINDINGS/ANNOTATION-PATCH-FIXES-TXT-BUT-COSTS-DOCX-25NOV-relay.md`. Two conversions,
one document, minutes - and it decides whether the patch is landable at all.

**SECOND:** the cost is where the hoist is emitted, not that it is emitted. Appending the `/Contents`
paragraphs after the page's own blocks instead of at the top would let the note and the duplicate be
dropped without moving a glyph. That patch is not written.

**THIRD:** the "(Authorised signatory)" duplication is a second, independent one-document fix:
`buildRowTable` marks the cell copy consumed and never the raw line, and the duplicate guard's exact
text equality cannot fire on a weld. Clearing it closes the last two txt documents that are not the
annotation one.

**MEASUREMENT ECONOMY, learned this slot:** a full `p2w.py` pass did 73 of 212 in two 260 s budgets - a
whole slot. `corpus-changed.py --record` then `P2W_CHANGED_ONLY=1 P2W_ENGINE_SRC=<this clone> p2w.py`
measures only what moved, and it writes `RANKING.partial.csv` rather than the published table, so the
stamp path still needs the full pass. Do the A/B on one document with `ConvertOne` + `verify_txt.py`
before spending the corpus.
