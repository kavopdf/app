# P2W Fixer - Run Report

**28 Nov 2026 · slot 12:36 → running IST · 1 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **3 disagreement(s)** - kept change: 1 code commit(s) in this window, first: 60_text_column_right_edge: the justify-pin is re vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; .txt age: measured 7.2 h ago vs nothing re-measures it on a schedule; run window: RUN.json says this run began at 12:36 vs TIMELINE.jsonl records the claim at 11:59, so the window was reset and the duration is short |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **48** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (64 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 12:34 | **lead** | 0/None | Google round trip refutes the justify-pin: 313 41/42 HEAD vs 40/42 pinned, 60 still FAIL (under-run 60.97pt -> 57.92pt, tolerance 48), plus a new 18_displacement. Cause is face substitution: source De |
| 12:36 | **lead** | 0/None | Google round trip (6 probes): face substitution is the cause. 313 HEAD 41/42 (60 FAIL, edge 477.66 vs src 538.63) -> Verdana face 42/42 PASS (edge 536.15); 302 HEAD 41/42 -> Verdana 42/42 PASS. Georgi |

## Why nothing moved, in this run's own words

> The slot did not land a document because the honest measurement said the change on the table would
> cost one, and then a different change turned out to be right but too large to prove inside the slot.
>
> The lead I inherited was a justify-pin: set the paragraph's right indent to its band's widest line,
> justify it, and add a trailing line break so the line is no longer a last line. On a face-substituted
> LibreOffice render it made all five documents whose only Google failure is `60_text_column_right_edge`
> clean. I did not trust it, so I put it through the real Drive round trip on one document, and Google
> refused it: still failing, and now also failing `18_displacement`. That is the trade the charter
> forbids, and the proxy had hidden it completely. So the first attempt of this run is a refutation, not
> a fix, and it is the most useful thing the run produced.
>
> Refuting it forced the question of what the check is actually measuring, and the answer is not a
> paragraph property. The source PDFs use DejaVu at 10 pt; the engine declares DejaVu at 10 pt; Google
> Docs does not carry DejaVu and draws something about fifteen per cent narrower, so every line stops
> short of the column. Every fix in the "stretch the line" family is therefore aimed at a variable the
> renderer is not reading. I tested the variable that is read — the face — with three one-attribute
> probes and a real round trip each. A Georgia probe moved the edge by a third of a point, which is the
> control: the probe mechanism works, and a face that merely looks similar is worth nothing. A size
> probe fixed the edge exactly and broke a check that exists to forbid changing the size. Verdana fixed
> the edge, kept every other check passing, and took the document to 42 of 42 in Google; a second
> document, with two declared families rather than one, went to 42 of 42 the same way.
>
> That is a real fix for two of five documents and a strong lead for the class, and I am recording it as
> a lead because I cannot honestly call it more. It is a `.docx` change, so it owes a full-corpus
> `.docx` re-measure, and that is fifty-four minutes on a slot that also had to fetch and convert a cold
> corpus. The gate is not what stopped me and neither is the engine. The clock stopped me, and the
> report should say so rather than dress two measured documents up as a kept attempt.
>
> What I would have done with another twenty minutes, in order: the three remaining documents through
> the round trip, because a face that is right at 10 pt may be wrong at 8 or 14 and the mapping has to
> be keyed on family and size rather than applied globally; then the mapping in the engine; then the
> corpus pass. The falsifier is written into the findings file so the next run can fail it on purpose.

### The run before this one said

> | At | Outcome | Moved | What it measured |
> |--:|:--|--:|:--|
> | 12:34 | **lead** | 0/None | Google round trip refutes the justify-pin: 313 41/42 HEAD vs 40/42 pinned, 60 still FAIL (under-run 60.97pt -> 57.92pt, tolerance 48), plus a new 18_displacement. Cause is face substitution: source De |
> | 12:36 | **lead** | 0/None | Google round trip (6 probes): face substitution is the cause. 313 HEAD 41/42 (60 FAIL, edge 477.66 vs src 538.63) -> Verdana face 42/42 PASS (edge 536.15); 302 HEAD 41/42 -> Verdana 42/42 PASS. Georgi |

Accounts share 7% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **7.2 h ago** - nothing re-measures this on a schedule; run `txt_gate.py --score 60` |
| Scored | **214** of 214 |
| Clean - every applicable check passes | **209** (97.7%) |
| Failing at least one check | **5** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 12:36 → running · 1 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 6 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| report - the report and the chain | **1 min** | `######################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
