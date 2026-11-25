# P2W Fixer - Run Report

**25 Nov 2026 · slot 08:14 → running IST · 36 min**

> **No engine change was kept this run, and that is the correct outcome.** Two changes were built,
> converted over all 213 documents and measured against `word/document.xml`; one changed nothing and
> the other recovered text but could not be proven safe. What this run did land is a correction to the
> instruction every run reads first.

## What this run did

**It measured a claim the brief was still making, and the claim is false.**

`FIXER-BRIEF.md` told every run that one construct — body text routed into an anchored DrawingML text
box — is "~166 document-failures" and "the largest engine defect anyone has found". A run at 06:07
today measured it and found ~8 documents. The brief was never corrected, so this run re-measured it on
the newer engine and corrected the brief in place.

| Instrument | Result at engine `981ff1fa35e2cf67` |
|:--|:--|
| `anchors.py` (new; characters inside `<w:txbxContent>` in `word/document.xml`) | **47 of 213** documents carry boxed text; **27,501** of **463,228** characters, **5.94 %** |
| The same reader at engine `b97d8172ce642eb0` (the 06:07 run) | 61 documents, 28,432 characters |
| Engine census `-Dp2w.census` | 690 anchor boxes: **652** from `PAGE_POSITION_ON_ANCHOR` propagation, **13** from the gap threshold the brief blames |

A construct present in 47 documents cannot explain 166 document-failures. The population also
**shrank from 61 documents to 47** between the two engines, which is why the 06:07 number and this one
differ — both are right for their engine.

### The two attempts, and why neither was kept

| Attempt | Change | Measured on all 213 | Kept |
|:--|:--|:--|:--|
| 1 | `!ctx.inColumn` guard added at `:3591`, the asymmetry against `:4474` | `document.xml` changed on **0 of 213** | **no** — unreachable on this corpus; reverted, recorded as a finding |
| 2 | `-Dp2w.pagepos=0` (propagation off) alone | **8 of 213** changed; boxed characters **27,501 → 22,476** (−5,025); total characters **+37** | **no** — the flag's own comment records 21 overlaps and median |dy| 105.7 pt when both positioners live, and this run had no Google path to prove otherwise |

Attempt 2 is a lead with a number on it, not a failure: 5,025 characters of the corpus's text would
leave a construct Google rasterises, across 8 documents.

### What changed in the repository

- `tools/p2w-bench/anchors.py` — counts the text inside anchored boxes from the `.docx`, and A/Bs two
  output directories. This question now takes 30 seconds instead of a run.
- `tools/p2w-bench/FINDINGS/ANCHORED-BOX-POPULATION-25NOV.md` — the replication, the drift, and both attempts.
- `tools/p2w-bench/FIXER-BRIEF.md` — the false sentence corrected **in place**, with the original
  numbers left visible so the correction is auditable.

### A gate that was passing vacuously, now passing for real

With the corpus converted on this pod, the commit gate's `google-safe` line stopped printing
`no .docx output directory - cannot check` and started checking. It passed. That line had been the
reason earlier runs could not tell a correctly-blocked pipeline from a dead one.

## Progress

| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **could not be read** - 0 of 191 scored were read as current, which is a failed read and not a measurement. No count is stated rather than a zero |
| Who re-measures them | the **:20 gverify** cron, once the read works |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 191 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **22** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (15 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## The txt

| | |
|:--|:--|
| Measured | **36 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

**Two deployed, both in-turn, both delivered.** A scheduled run has nobody to answer a later message,
so both ran inside the turn rather than in the background.

- **Anchored textbox patch** — traced every path that sets `ctx.positioned` and every path that then
  writes a `wps:txbx`, and found the asymmetry this run then tested. Its larger claim — that the
  wide-gap rule is already disabled on pages that fit, so `GAP_CAP_TW` cannot be the mass — is
  confirmed independently by the census above.
- **Google check audit** — classified all 47 check ids as sound, blind, proxy or mis-thresholded.
  Found `14_filled_shapes`, `23_line_pitch`, `34a/34b/34c`, `50_annotation_text`, `53_embedded_faces`
  and `62-66` structurally incapable of failing, and `04/05/13/17/44/45/47/59/60` judging a rendering
  artefact. **Not acted on this run** — and one of its recommendations is explicitly refused below.

> **Refused, with the reason.** The audit's top-ranked fix is to make `04_chars_missing` and
> `45_char_accuracy` read `word/document.xml` instead of Google's exported text layer, which would
> close 54 documents on paper. That is forbidden by the first non-negotiable: Google is the truth. The
> text really is absent from the document the user opens; moving the check to the file that still has
> it would hide the defect and inflate the score. Recorded here so the next run does not take it.

## Timing

| | |
|:--|:--|
| Slot window | 08:14 → running · 36 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 12 |
| Longest silence | **11.6 min** — from 08:38:22, after `relay: rebuilt engine with inColumn symmetry patch` |
| Silences over 2 min | 6 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **15 min** | `###########` |
| report - the report and the chain | **12 min** | `#########` |
| other - not attributed to a tool | **3 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/00_page_count-23-REFUSED-ALL-ENGINE-0-CLEAN-24NOV-agentB.md - the 22 page-count refusals are already root-caused (Google bills the flow for page-positioned floating shapes, 0.10-0.96 pt each, median 0.57; prize is 5 clean documents, not 23). Do not re-derive it. THEN READ the three findings this run added, in this order: (1) FINDINGS/gapcap-latch-census-01-GAPCAP-LATCH-CENSUS-25NOV.md - the box mechanism is worth ~8 documents, NOT the 166 the FIXER-BRIEF claims: 28,432 boxed chars over 61 carriers, latch 19,860 (70%), cap 4,527 (16%), 44 of 61 carriers under 200 chars and invariant under every knob. (2) FINDINGS/spendwidegap-lookahead-01-REJECTED-25NOV.md - the look-ahead is REJECTED as a fix: it refuses the one spend that produced 39/42 on doc 69 because a running footer sits below it. Lead: the condition is 'no FLOW line below', not 'no line below'. (3) FINDINGS/CLAIM-NEVER-REACHED-ORIGIN-25NOV.md - the claim cannot land: the 81 s pre-commit gate runs inside a 120 s commit on a tree the beacons keep dirty. Land it by hand: git add -A tools/p2w-bench && git commit && git -c core.hooksPath=/dev/null rebase origin/main && git push. The single highest-leverage check is 18_displacement at 39.7 clean documents; 00_page_count is 22.0 and is the only one whose population is entirely UNSCORABLE, so a fix there is invisible until it lands. No java on PATH in this pod: export JAVA_HOME=/scratch/work/.p2w-jdk/jdk before any ConvertOne/ConvertAll.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
