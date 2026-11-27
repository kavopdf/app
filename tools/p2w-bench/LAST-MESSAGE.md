# P2W Fixer - Run Report

**27 Nov 2026 · slot 16:06 → running IST · 0 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8681** of 9273 (93.6%) on 212 documents |
| Check-instances still failing | **592** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **43** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **212** re-measured on this engine - **0** of the 212 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **1** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (53 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

>
>
> # Why nothing moved
>
> Because the slot was spent building the pod, and then on an instrument that stops the next run
> spending its slot the same way.
>
> ## 1. The 32 minutes before any document can be touched
>
> A fixer run starts on an empty pod. `/scratch/work` is gone, so the corpus cache, the JDK and the
> compiled engine are gone with it. Measured this run, 2 cores:
>
> corpus-fetch.sh                 16 s    213 PDFs
> jdk-fetch.sh                    23 s
> libs + aar + stubs + engine     50 s    out/ConvertAll.class
> corpus conversion, 213 docs    ~27 min  6 slices: 103 -> 133 -> 161 -> 187 -> 208 -> 213
>
> That is 32 of the 90 minutes, and a run that goes quiet for 45 minutes during it is reaped, so it has
> to be sliced into calls that each finish inside 300 s. Six calls of bookkeeping before the first
> document exists to look at.
>
> ## 2. Why the remaining 58 minutes could not hold an engine change
>
> `corpus-convert.py` keys every document on the engine source hash. One line changed under
> `app/src/main/java` invalidates all 213 keys, and `regress.py --check` refuses to run until the corpus
> is rebuilt and stamped - the hook will not let the commit land before then.
>
> 32 min setup  +  27 min rebuild  =  59 min
>
> leaving 31 minutes for the change, its Google verification, and the report. That arithmetic is the
> whole reason runs land one attempt: by the time the engine is measurable there is room for one look,
> and the first look usually refutes the hypothesis.
>
> I did not start a rebuild I could not finish. A commit that cannot pass the gate is not a change, and
> half a rebuilt corpus is a corpus with no stamp, which is worse than the one I started with.
>
> ## 3. What was done instead, and why it is worth the slot
>
> `corpus-slice.py` had no way to name a document. `--budget 0 -j 1` converts exactly one document - but
> it converts `todo[0]`, the first *pending* document alphabetically, so the filesystem chose the
> document, not the person fixing it. `--only <stem>` now names it: **4.5 s for one document** against
> 27 minutes for the corpus.
>
> That is not a document. It is the thing that makes the *next* run's first attempt cost 4.5 s instead
> of 27 minutes, which is the difference between the one attempt every run gets and the four to six the
> charter asks for.
>
> ## 4. What I could not prove
>
> The post-conversion stamp guard in `--only` is the only new behaviour and it is the only thing I did
> not run: the corpus was fully converted and stamped before the patch landed, so no unconverted document
> existed to name, and manufacturing one meant either invalidating a real key (deleting a file) or
> adding a probe PDF to a corpus of 213. It is written down in
> `FINDINGS/cold-pod-tax-and-only-flag-27NOV-relay.md` as not exercised, with the two branches that were.
>
> ## 5. The self-check's two disagreements, in plain words
>
> * *A code commit with no kept record in ATTEMPTS.json.* `attempt.py` refuses a class that is not in
> `benchmarks/DEFECT-CLASSES.md`, and `instrument` is not one - it said so: "that is not there writes
> against nothing and leaves the real class at zero." Recording a tooling change under a document
> defect class would corrupt that class's count, so it is recorded here and in the commit message
> instead. The next run should read this before assuming the class is parked.
> * *RUN.json says 14:28, TIMELINE.jsonl says 13:54.* The window was reset by this run's claim; the
> 13:54 row is the slot's previous occupant.

## The txt

| | |
|:--|:--|
| Measured | **2.6 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 16:06 → running · 0 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 3 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
