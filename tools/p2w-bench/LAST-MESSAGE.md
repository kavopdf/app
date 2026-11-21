**22 Nov 2026 · fixer slot 01:53 → running IST · 1h 42m**

**The carrier patch is a global substitution, and it rewrites a clean document.**

> The handoff said `rule-carrier-horizontal-only-2008.patch` was "13 of 16 documents to 42/42 in
> Google, one build away". Both numbers are true. Nobody had measured the other 197 documents, and
> this run did: **161 of 213** `.docx` files change, including `51_two_cm_margins`, which
> passes **all 42** checks in Google today. It cannot land as it stands.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, — the documents both renderers scored in Google |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## What this run measured, and why it stops here

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 02:55 | measured | 0 | Corpus fetched (213 PDFs), patched engine built in 38 s. Both subagents returned: one proved the docx table is already stale against HEAD *before* any patch (`6c6cf642e13b7ed2` committed vs `226f7f2df3013ad7` in the tree), the other confirmed the 13/16 Google result from the committed JSONs. |
| 03:05 | falsified the instrument | 0 | HEAD converted twice, once here and once in an independent pod: canonical hashes agree on all 16 documents both runs converted. A raw-byte hash would have reported 213 false differences - zip entry mtimes differ between runs of the same engine. |
| 03:30 | **measured** | 0 | All 213 documents converted on HEAD and on HEAD+patch (p50 7.2 s/doc). **161 change, 52 do not.** Cross-referenced with `benchmarks/gverify/`: 143 fail `32_stroke_lines`, **5 pass it**, 13 are `page_count_refused` with no Google score at all. |
| 03:35 | **lead** | 0 | The five that change while passing `32_stroke_lines`: `51_two_cm_margins` (42/42 today, 2 drawings -> 1 drawing + 1 table), `77_arabic_rtl_document`, `373_leave_application_form`, `374_org_chart`, `382_architecture_diagram`. The 13 refused include the three heaviest horizontal-rule documents. |

## The arithmetic that decides it

The patch is not a repair for a failing construct - it is a **substitution applied to every
horizontal rule shape in the corpus**. That is why 143 gain candidates come with 5 documents that
were already right and 13 that no Google score can defend. `regress.py` would not catch it: its
Google regression check reads `benchmarks/gverify/`, so a changed document with no new result keeps
its old count and reads as no regression.

What would make this land, in order of cost:

1. **Narrow the predicate** so it cannot fire where the rule already renders. The five + thirteen
   above are the exact set it has to be right about, and `benchmarks/blast-carrier-2008.json` names
   them. This is one build, and it is what the next slot should do.
2. **Google-score all 161.** Complete, honest, and 100-120 minutes at the measured 36-45 s per
   document through Drive - two slots, with the upload/export loop that has failed runs before.

## Falsification

| test | expected | measured |
|:--|:--|:--|
| HEAD converts identically in two independent pods | identical canonical hashes | **identical, 16 of 16** |
| the patch changes only the 16 measured documents | 16 | **161** - falsified |
| a clean document is untouched | untouched | **`51_two_cm_margins` rewritten** - falsified |
| the changed set is exactly the `32`-failing set | equal | **143 of the 161** - 5 pass 32, 13 unscored |
| `regress.py --check` after reverting the engine | PASS | **PASS** |

## Subagents

Two, both finished inside this turn (a scheduled run has no later turn for a background result).

**`p2w-runbook`-style cost analysis** (Explore) established that there is no scoped re-measurement:
`p2w.py` has no `--only`, and `_invalidate_if_engine_changed()` deletes all 213 `.docx` on an engine
change by design. It also found the docx table is stale against HEAD **independently of this patch**
- the gate refuses a docx-in-scope commit today for that reason, which is pending blocker 37.

**Carrier claim audit** (Explore) confirmed 13 of 16 at 42/42 from the committed JSONs, confirmed
6 clean of the 192 scored and 186 failing, and found four contradictions in the committed FINDINGS prose,
including a residual table that lists `45_coloured_callout_box` as still failing when its JSON is
42/42. It also flagged that 64 documents are scored out of 47 checks and 2 out of 44, so a
corpus-wide "42/42" yardstick is not like-for-like.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Timing

| | |
|:--|:--|
| Slot window | 01:53 → running · 1h 42m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 19 |
| Longest silence | **41.5 min** — from 02:10:08, after `report.py: building the report` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **21 min** | `#####` |
| measure or build - a conversion, screen or compile writes no beacon | **1h 15m** | `################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **3 min** | `#` |
