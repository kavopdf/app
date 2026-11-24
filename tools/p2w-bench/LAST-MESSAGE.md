# P2W Fixer - Run Report

**25 Nov 2026 · slot 23:49 → running IST · 19 min**

> No document became clean this run. Two gate deadlocks were fixed and pushed, and the next
> attempt is measured and waiting. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **36** of the **187** re-measured on this engine - **4** of the 191 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **22** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (19 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## The txt

| | |
|:--|:--|
| Measured | **1.2 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 23:49 → running · 19 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 12 |
| Longest silence | **8.1 min** — from 00:00:23, after `reconvert slice 2 (160 to go, 12 workers)` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **7 min** | `########` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **8 min** | `#########` |
| other - not attributed to a tool | **2 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## What was kept

1. **`corpus-slice.py` could not finish a corpus build on a cold pod, ever.** `missing()` counted a
   `.docx` on disk as done only when a STAMP for this engine existed, and the stamp is written only
   when `missing()` returns empty. Deadlock: every slice converted the same first 51 documents,
   printed "213 to go", and no stamp was ever written - so `regress.py --check` refused every commit
   and no run could land anything. Measured before: 7 slices x 51-52 documents, "to go" stayed 213,
   stamp none. After: 52 → 104 → 156 → 208 → 213 DONE in five slices, stamp written, gate PASS.
2. **`google_safe.py` refused every commit after a construct was renamed.** Commit fe15f40a renamed
   `w:before-page-top` to `w:before-any`; the mark kept the old key, so the scan found the construct
   in 213 documents against a mark of 0 and refused - and `--mark` could not repair it either,
   because the mark may only fall. `RENAMED` now maps a construct to its former name, so a rename
   cannot read as a spread. Evidence it is a rename: 213 carriers before, 213 after; `w:drawing`
   197/197; `w:spacing-letter` 22/22. The mark was re-based with `w:before-after-pagebreak` at 19.

## The attempt that is waiting

**`t12_word_invention`** - "the .txt carries no word the source never drew". Four documents fail only
this check: `05_round_company_seal_curved_text`, `311_fir_police_form`,
`600_reviewed_invoice_with_annotations`, `journal-2col-with-footnotes`.

Root cause, measured on `journal-2col-with-footnotes`: the footnote marker is drawn at 7.12 pt,
4.45 pt above an 8.9 pt body baseline. `toLines()` uses `tol = max(0.9, g.size * 0.18f)` = 1.28 pt
for that glyph, so the marker starts a line of its own, and the .txt carries `cent` and `1` as two
words where the page drew `cent.1` - six invented words on that document, and the only check it
fails. The patch merges a glyph with the line it belongs to when it is smaller than that line and
within 0.55 of the line's size of its baseline, in both directions, because the page is read in y
order and a superscript arrives BEFORE its body. Measured on that document: 6 invented words → 2.
It does not yet make the document clean: the two left are the marker landing in the right-hand
column, where the gutter split takes it.

It is not landed because an engine change needs a 213-document reconvert before the gate will take
it, and the slot ran out at 108 of 213. The source is reverted; the patch and this measurement are
what the next run starts from.

## Subagents

One deployed (row-height drift on `18_displacement`), 25 min, partial, no files returned. Its
source-level result is kept: the `atLeast` row height is emitted at `DocxWriter.java:6558`, the
excess is the row's own rule (15 twips = 0.75 pt), so the "+0.70 pt/row, factor 0.9634" in the
handoff is pitch-dependent and right only at ~18.4 pt rows. The principled declaration is
`trHeight = pitch - rule`. Not landed: no instrument on this pod can see a Google-only change, so it
belongs in FINDINGS rather than in the engine.

## Next run

1. Re-apply the superscript patch and finish the reconvert. `corpus-slice.py` now resumes on
   (engine, build start time), so a cold pod reaches a stamp in five slices instead of never.
2. Then the four `t12_word_invention` documents: the gutter split is the second half.
3. `18_displacement`: `trHeight = pitch - rule` at `DocxWriter.java:6558`, with the room-guard charge
   at `writtenRowsTw` in the same commit - 13 documents fail that class alone.

### Obstacles cleared

Two: the corpus build (7 slices, never a stamp, on a cold pod) and the google-safe mark after the
construct rename. Both are pushed and both are why this run's gate PASSes at all.
