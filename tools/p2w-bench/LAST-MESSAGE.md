# Fixer report - 2026-11-24 15:43

```
# P2W Fixer - Run Report

**24 Nov 2026 · slot 15:43 → running IST · 10 min**

> No change was kept this run, and the reason is the result: the construct the charter calls its
> biggest defect cleans **zero** documents on its own. Three measured attempts, one of them an
> infrastructure fix that lets any run commit at all.

## Progress

| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **35** of the **186** re-measured on this engine - **4** of the 190 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `04_chars_missing` - taken from the pending list (26 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 15:43 | **lead** | 0/None | anchored-text-box census: the 120 pt cap is 16% of the box text and the pagepos cascade 17%; spending every gap removes 15.9% but displaces 3 documents worse, and no document has 04/45 as its only fai |

## The txt

| | |
|:--|:--|
| Measured | **57 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*One deployed (anchor census).* It instrumented a private copy of the engine, proved the build
output-identical to HEAD on **213 of 213** documents, and returned the per-page census.

## Timing

| | |
|:--|:--|
| Slot window | 15:43 → running · 11 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 67 |
| Longest silence | **6.4 min** — from 15:43:41, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **2 min** | `#####` |
| report - the report and the chain | **8 min** | `#################` |
## What I decided, and why

The slot was not free when I arrived. The previous fixer claimed at 08:47 UTC and went silent; my first
four claims read `fixer busy - last activity 41 min ago (stale after 45 min)`. I waited the window out in
pod time, and by then that run had committed its handoff, worked, and released at 09:33 — so I claimed a
free slot at 15:03 and lost no work to it. Worth recording because the failure mode is the one the user
complained about: a run that claims, writes a handoff, and stops.

**Class: the anchored-text-box construct (the `04_chars_missing` / `45_char_accuracy` axis).** Not because
the tool said so, but because the charter names it "the largest engine defect anyone has found, ~166
document-failures from one threshold". I took that claim as the thing to test first. **It is wrong, and
that is the main result of this run.**

## Three measured attempts

**1. Spend every gap (`ctx.spendGaps = true`), rebuilt, all 213 re-converted.** Refuted. It removes 15.9 %
of the box text (23,794 → 20,024 characters) and changes no document's page count, but it displaces three
documents measurably worse — `330_cad_drawing_sheet` median 3.14 → 16.77 pt, `table-inside-two-column-page`
max 9.17 → 92.01 pt, `newsletter-3col-header-footer` max 6.26 → 28.36 pt. Rule 3 refuses it.

**2. The `ZERO_GAP_ANCHOR` cascade on its own (`-Dp2w.pagepos=0`), all 213 re-converted into a separate
cache.** A lead, not a fix: 61 → 61 documents, 1,037 → 897 boxes, 23,794 → 19,757 characters (−17.0 %).
No document stops carrying boxes, because after the flow resyncs the next line anchors on its own negative
gap. This also corrects the record: the note that `pagepos=0` "moved the box count only 495 to 483" was a
box count on a subset — the flag is worth 4,037 characters corpus-wide.

**3. The question the charter demands before every attempt — *if this works, which documents become CLEAN?***
Answered from the committed Google verdicts against the 213 `.docx` built at HEAD: **zero.**
65 documents fail `04_chars_missing` and 54 of them carry boxes; 37 fail `45_char_accuracy` and 35 carry
boxes; **not one document has `04` and/or `45` as its only failures.** Emptying every anchored box in the
corpus takes 54 documents from "fails 04" to "fails something else". It is a real defect — a Docs user
gets a picture of a footer instead of a footer — but it is not a document-mover, and a run that spends its
slot on it reports zero moved and is right.

**What is a document-mover: 24 documents fail exactly one check, and 13 of those fail only
`18_displacement`.** `classpick.py --leverage` agrees — 18_displacement is worth 39.1 clean documents,
60_text_column_right_edge 19.8, 04_chars_missing 14.4. And `18_displacement`'s two constructs are the same
`w:before` rewrite the box problem needs: one line the flow cannot reach, written at the page's own y
instead of as an anchored box. **One rewrite, three classes. That is where the next run should start.**

## What I fixed that a run could not fix before

Two mechanical reasons no run could commit, both measured here:

- **The corpus cache was keyed on `git rev-parse HEAD`**, so every commit — including a findings-only
  commit — invalidated all 213 `.docx`. `regress.py` calls `corpus-convert --ensure` from inside the
  pre-commit gate, so the gate paid a 200 s rebuild and ran past the 300 s call limit. My first gate run
  after two findings commits died at 240 s. The key is now a sha256 of the engine sources, the same
  quantity the gate prints. **The gate now runs in 19.9 s with the `.docx` checks live** — `google-safe :
  no construct Google ignores has spread` — where before it printed PASS having exercised nothing.
- **A fresh pod has no java.** The gate's own message says so and then PASSes. `jdk-fetch.sh` installs
  Temurin 17 from api.adoptium.net to the path `corpus-convert.py` already looks for. The corpus then
  converts in 200 s across 6 shards, which is how this run measured anything at all.

Also fixed: `corpus-convert.py` alone looked for the corpus in `/scratch/work/CORP/` while `corpus-fetch.sh`
and every other tool use `/scratch/work/p2w/corpus`. On a pod that had just fetched it with the repo's own
script it reported `corpus PDFs : 0 (none found)` and COLD with 213 `.docx` cached.

## What I did not do, and what would overturn me

- **No Google render this run.** Every box number is read from `word/document.xml`; the effect on the 42
  checks is predicted from character counts, not re-verified in Docs. The `gverify` cron is the instrument
  for that.
- **The proposal is unmeasured:** write an unreachable line as `w:before` at the page's own y rather than
  as an anchored box. Nothing in this run tested it, so it is a proposal, not a result.
- **Three pages disagree with my model** — on `311_fir_police_form`, `323_credit_card_statement` and
  `353_admit_card` the re-evaluated page height is under the paper yet the engine's own `pageFits` said no.
  Unresolved; the suspicion is `page.blocks` differing between the two call sites.

Everything above is in `tools/p2w-bench/FINDINGS/ANCHORED-BOX-CENSUS-CAP-IS-16PCT-24NOV.md` and
`tools/p2w-bench/FINDINGS/ONE-CHECK-AWAY-24NOV.md`, both committed and pushed.

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 27 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 27 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 26 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 27 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. PENDING FIRST: 23 item(s) you can close - run pending.py and take them in its order before the class below. 18_displacement: APPLY tools/p2w-bench/FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch, build, then START the slot with the 212-document pass (p2w.py --force --budget 250, repeat) - that pass is the whole cost. It is measured: 362_price_list_dense 41/42 -> 42/42 in Google, electricity-bill and 330_cad_drawing_sheet byte-identical. Do NOT re-run the trHeight=max(content,line-15) probe - it is refuted and the guard makes it unnecessary. After the pass: regress.py --check, --stamp, commit app/+RANKING.csv, attempt.py --class 18_displacement. Then check the 9 documents named in FINDINGS/18_displacement-UNIFORM-PITCH-GUARD-GOOGLE-42of42-0450-fixer.md for a uniform pitch.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
