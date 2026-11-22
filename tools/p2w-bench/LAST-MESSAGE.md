# P2W Fixer - Run Report

**22 Nov 2026 · slot 11:14 → 11:26 IST · 11 min**

> The row growth that blocked the spacer is solved and measured in Google: mobile-bill 41/42 -> 42/42.
> It is carried as a patch, not committed, because the trHeight edit needs the corpus-wide gate pass
> and `p2w.py --budget` is a *time* limit (26 of 213 documents per 250 s) that does not resume.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 11:21 | **lead** | 0/3 | One Google probe settles what a row is laid at: laid = max(declared trHeight, 1.15 x cell type size) + border, exactly, across 13 declared heights at 10 and 18 pt. No threshold; the 'content term' is |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

Two, both before my own attempt, both used.

| Agent | Given | Returned |
|:--|:--|:--|
| Row-height probe | build a 17-configuration .docx with python-docx and measure each row's laid height in Google | **could not run the Google leg** - a sub-agent cannot upload (`upload` refuses `/scratch/output` for a delegated task; an s3key from a local path is 403). It built and returned the probe .docx files with LibreOffice numbers, clearly labelled as not Google. I ran the upload myself. |
| Cell-emitter diff | read `DocxWriter.java` and produce a minimal `git apply`-able diff making a cell of N paragraphs of pitch P advance N*P | a line-numbered diff that passes `git apply --check`, the method and range (cell paragraphs 6412-6737), and the finding that the multi-paragraph path is **not** the one `mobile-bill` takes |

The first agent's failed leg is worth recording: **the sub-agent sandbox cannot reach Drive**, so any
task whose answer is a Google number has to be done by the run itself.

## Timing

| | |
|:--|:--|
| Slot window | 11:14 → 11:26 · 11 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **5.0 min** — from 11:14:33, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **The relay's own pre-claim heartbeat makes a dead claim read live.** `round.py --heartbeat` writes `fixer_las |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **5 min** | `#########` |
| record - attempt, handoff, class rows | **1 min** | `##` |
| report - the report and the chain | **1 min** | `##` |
| other - not attributed to a tool | **4 min** | `#########` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

**Land `patches/18-spacer-before-rowpitch-rowrule.patch` - it is proved on four documents in Google
and blocked only on the corpus measure.** In this order:

    git apply patches/18-spacer-before-rowpitch-rowrule.patch
    bash tools/p2w-bench/build-engine.sh
    python3 benchmarks/gate.py --budget 250     # repeat until STATE.json carries the tree
    python3 tools/p2w-bench/regress.py --check
    # then the Google ratchet over the 13 clean spacer-bearing documents + the 16 that fail
    # 18_displacement, listed in FINDINGS/18_displacement-table-spacer-CONFIRMED-...-1005-f1x.md

Two facts this slot settled that the previous instruction had wrong:

1. **The 6-paragraph rows on mobile-bill are six cells with ONE paragraph each**, not two paragraphs
   per cell. The `cps.size() >= 2` path is never entered there; a diff against it moves nothing
   (built, measured, no change).
2. **Google charges a row's rule on top of `w:trHeight`**, not inside it. Dose-response measured in
   one document: trHeight 368 / 358 / 348 twips laid out 19.73 / 19.04 / 18.35 pt. The engine's
   comment at `DocxWriter.java:6153` says the opposite and is what the last three runs built on.

`insurance-policy-schedule` is the one document the patch does not close (41/42, `18` alone, one page
- its HEAD score). Its residual is not the spacer and not the row rule. Do not re-derive it.

**Do not judge this patch in soffice.** soffice charges `w:before + w:line`, so it is blind to the
spacer edit and sees the trHeight edit as a pure shortening; a soffice `share@5px` regression here is
the proxy disagreeing with the phone.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
