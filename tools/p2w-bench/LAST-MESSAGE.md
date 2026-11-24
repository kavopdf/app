# P2W Fixer - Run Report

**24 Nov 2026 · slot 20:25 → running IST · 24 min**

> The pipeline was dead on arrival and is alive again. Nothing moved in the .docx table; one document
> moved FAIL -> PASS in Google, and the reason three runs landed nothing is now three commands.

## What was blocking

`regress.py --check` refused **every** commit - including the claim, because the claim is a commit -
because the converted corpus was absent, and on a fresh pod it always was: no JVM, no corpus, and a
corpus build that restarted from zero every time (213 x 10.8 s = 19 min against a 290 s call).
Cleared this run: `corpus-fetch.sh` (213 PDFs, 0 missing) -> `build-engine.sh` (51 s) ->
`corpus-convert.py --ensure`, made **resumable and sharded**: 213 documents warm, stamp
`b97d8172ce642eb0`, ~8 min across two calls, then the gate **PASS**. Two commits landed as a result.

Shard size is 10 on purpose: `p2w.py:1050-1075` measures `ConvertAll` carrying state between the
documents it is handed - `392_statistical_console_output` reads share5 1.61 alone, 1.61 with 11
others, and 28.39 inside 213 in one JVM.

## The attempt: the four-site foot-band rule

`patches/foot-band-spend-the-gap.patch` applied, engine rebuilt, five documents converted:
`w:txbxContent` 2 -> 0 on `27`, `46`, `55`, `61`, `67`; page counts unchanged; every character of
the source survives (one added space where the box became a flowed paragraph). In Google, through
Drive upload -> convert -> export -> `gverify.py --collect`, **`61_two_col_abstract_spanning`
40/42 FAIL -> 42/42 PASS** (was failing `04_chars_missing`, `44_header_footer`). With `27` (42/42 at
the one-site variant) that is two documents whose only failures were the anchored footer row, both
now clean in the renderer the user opens.

Not landed: an engine change needs the full restamp - 26 documents per 250 s budget plus `docx()` at
one JVM per document is ~54 min, and 50 were left. The patch and both renders are committed.

## Instrument finding, not committed

`25_invisible_text` can only pass: the 01:41 commit (`79ef7075`) drops every fill covering >=90 % of
the sheet, and on a Google export the sheet is the only vector fill, so `fills` is empty and
`0 <= s_invisible` is a tautology. 43 stored records fail it from before the fix; the only two
measured after it pass. Written up, not committed - no stored Google export to measure a fix on.

## Subagents

Two, deployed in the first ten minutes: the anchored-box audit (found the four-site patch, the 7 Nov
revert, the census displacement that refutes spend-always) and the `25_invisible_text` audit.

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
| Working on | `-` - taken from the pending list (26 still open), not a new class |

## The txt

| | |
|:--|:--|
| Measured | **38 min ago** |
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
| Slot window | 20:25 → running · 24 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 5 |
| Longest silence | **12.7 min** — from 20:36:42, after `relay: restamping 213 docs on the patched engine (p2w, resumable)` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **10 min** | `#########` |
| report - the report and the chain | **13 min** | `############` |
| other - not attributed to a tool | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |


## Next run

**Three commands before the claim:** `corpus-fetch.sh`, `build-engine.sh`,
`corpus-convert.py --ensure` (repeat until the stamp exists) - without them the gate refuses the
claim itself. **Then land the foot-band patch**: measured in Google on `27` and `61`, restamp ~54 min.
Take displacement on `27` and `61` in `p2w` **before** the restamp: the census refutes spend-always on
displacement, not page count, and neither has been re-measured there.
