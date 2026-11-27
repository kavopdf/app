# P2W Fixer - Run Report

**28 Nov 2026 · slot 04:00 → running IST · 31 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8477** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **534** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - kept change: 1 code commit(s) in this window, first: fixer 28nov 04:00: the rung is Google-proved - r vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; subagents: 2 deployed vs no FINDINGS filename carries 18prize-01, 61rank-02 - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **46** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `63_table_rows` - taken from the pending list (62 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `63_table_rows` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 04:27 | **lead** | None/None | 84 refusals decomposed from the committed tables: 10 are Google-clean on a05b20eb (47/47 or 42/42), 4 have an internally impossible baseline (share5 0.00 with max_pt>2.4), 13 are already at the charte |
| 04:29 | **lead** | None/None | REFUTED: the rung revert (ROW_RUNG_UNDER_TW 0) is a Google regression on 2 of 2 documents. mobile-bill and electricity-bill are 47/47 on HEAD (a05b20eb, committed 27 Nov 14:45-14:46); with rung=0, reb |

## Why nothing moved, in this run's own words

> Not for want of a change: two changes are measured and both are refused, one of them by Google.
>
> **The rung is right.** The last two runs were building toward landing `ROW_RUNG_UNDER_TW = 0` as a
> revert that takes the gate from 84 refusals to 57. I measured the half of it nobody had measured - the
> Google side, on the two documents the rung was landed for. `mobile-bill` and `electricity-bill` are
> 47/47 on HEAD; with the rung removed, both come back 46/47 failing `18_displacement`. The revert is a
> Google regression on 2 of 2 documents, and the LibreOffice baseline that scores it 28 documents better
> is, on the only evidence that can arbitrate, pointing the wrong way: rung = 10 reads 30.09 / 36.78 and
> is clean in Google, rung = 0 reads 1.55 / 1.33 and is not.
>
> **And the gate cannot be walked around, because it refuses the tree in which nothing changed.**
> `measure_gate.py` prints READY, 213/213 scored, 0 blocking. `regress.py --check` still exits 1 with 84
> docx refusals, and `docx_regressions()` runs unconditionally - so the hook refuses an engine fix, a
> tool, a findings file and this report alike. The 84 decompose into 23 the charter does not recognise as
> damage (10 pass every Google check on the current engine, 4 have a baseline that contradicts itself,
> 13 are already inside the 99 % bar) and 61 genuine losses.
>
> I did not take the gate decision this run, and I want to be plain about why. A gate change that
> releases the 10 Google-clean documents is defensible on the charter's own words. A gate change that
> re-bases the whole table to the current engine would ratify 61 genuine losses on the strength of a
> yardstick I have just measured to prefer the worse document. Those two look similar from the outside
> and are opposite in fact, and the difference is one measurement wide - so it goes in front of the next
> run as arithmetic, not as a patch I took on the last hour of a slot.
>
> The 8-document screen is the other half of what this run is worth: on the current tree it reproduced
> `benchmarks/RANKING.csv` 8 of 8, and on the rung = 0 build it reproduced the rung0 CSV 7 of 8 digit for
> digit. The measurement pipeline is sound. The yardstick is the problem.

### The run before this one said

> Not for want of a change: the change is measured and it is one constant. Nothing could be committed
> because **the commit gate refuses `main` itself**.
>
> `bash tools/install-gate.sh` installs `.git/hooks/pre-commit`, which runs `regress.py --check` and has
> no override. On a clean clone of `main` with `scope.py` reporting no engine change, that command exits
> 1 with **84 docx documents worse than the 15 Nov baseline**. So the hook refuses an engine fix, a tool,
> a findings file and the run's own report alike. Four slots have ended "nothing kept" against this wall
> and each wrote it up as a slot that ran out of time; the wall is the reason.
>
> The arithmetic, recomputed this run from the three committed tables by a new read-only tool,
> `tools/p2w-bench/gate_decompose.py`:
>
> - of the 84, **27 have a baseline of exactly 0.00** - a floor no change can hold;
> - **6 already sit inside the corpus's own 99% bar** (`share5 <= 1.0`) and are refused anyway;
> - **10 baseline rows contradict themselves** - `share5 = 0.00` while `max_pt > 2.4 pt` says ink sits
> beyond the 5 px radius the metric is defined on; **4 of them are among the 84**;
> - 19 are a genuine loss above 5.0.
>
> The largest real lever is `ROW_RUNG_UNDER_TW = 0`. `FINDINGS/RANKING-rung0-FULL-CORPUS-28NOV.csv` is a
> full-corpus measurement of exactly that tree, and against the same baseline it takes **84 -> 57**:
> **28 released, 1 cost** (`marksheet-subject-left-marks-right`, 4.55 -> 5.21), **net 27**. It is one
> constant, it is fully measured, and it still does not clear a gate that demands zero.
>
> So the next run's first question is not "which class" but "how does `main` get back under the bar". The
> order that does not ratify damage: land the rung in its **per-row** form (mechanism and falsifier in
> `FINDINGS/GATE-REFUSES-MAIN-ITSELF-AND-THE-RUNG-IS-27-NET-28NOV-relay.md` §6 - apply it only where the
> table is held to a page budget, the `mobile-bill` case it was tuned on), re-measure the ten
> self-contradicting baseline rows as a data defect, and only then decide whether a gate that refuses a
> tree in which nothing changed is still the right gate. Re-baselining to today's state without the rung
> would ratify 27 documents of avoidable damage.
>
> Nothing here is a substitute for a measurement the gate accepts. It is the map of why there is no such
> measurement yet, and it is committed so the next slot starts from it rather than re-deriving it.
>
> **Two agents were deployed and recorded in `HANDOFF.json`** (`row_rung|A`, `commit_gate|B`); both landed
> and their arithmetic was recomputed here rather than trusted - one of them cited a findings file that
> does not exist, which is why the numbers in this report come from `gate_decompose.py`.
>
>
> The gate's regressions are not five constructs. They are one constant, and this run bisected them to it.
>
> The last three reports said the 84 LibreOffice regressions were several unrelated constructs and that no
> single patch would move them. That was never measured; it was inferred from the class table. So I stopped
> inferring and bisected the engine the way you bisect any regression: build the tree at each commit, score
> one document, watch the number. `table-with-no-header-row` sits at the baseline score for four commits in a
> row and jumps to its full tree score at exactly one of them. That commit is the table work of 27 November.
>
> It went in as two rules at once, so the second question was which half did it. Both were made switchable
> and measured separately, and only one of them moves anything: the rule that declares a pitch-bound table row
> ten twips under its own pitch. Turning that rule off returns every table document I probed to its baseline
> score, and five of the six come out better than the baseline rather than level with it, because the other
> engine work since 15 November is real and the rung was hiding it. The gap rule from the same commit is inert
> on both documents I tested it on.
>
> So the answer to "what makes these documents worse" is now a named constant with a named commit, and the
> probe that shows it costs fifteen seconds a document instead of a corpus pass. That is the thing this run
> was worth.
>
> What I did not do is decide which renderer is right, and I want to be plain about why that matters. The rung
> was landed on Google evidence: its own commit message says it took two documents to a clean sheet in Google
> Docs. Every measurement against it since has been LibreOffice. Under the rule this project is built on -
> Google is the truth and LibreOffice is a proxy - a change that is right in Google and wrong in the proxy is
> not a regression at all, and a tenth of the "regressed" documents pass every Google check while their proxy
> score rises. That is consistent with the gate refusing on an artifact of the proxy. It is also exactly the
> kind of comfortable story that turns out to be wrong, so it stays a hypothesis: the Google side of this
> constant is unmeasured, and it is two documents wide.
>
> The next run should measure it before it builds anything, because the answer decides two different jobs. If
> the two documents stay clean with the rung off, the constant is pure cost and should go, and the gate
> unblocks by itself. If either one loses its clean sheet, the rung is right and the gate is charging a
> Google-proved construct to a renderer nobody opens - and then the gate is the defect, with a measurement in
> FINDINGS/ to argue from rather than an opinion.
>
> Nothing was kept and no engine line was committed: a change that requires a full corpus re-measurement does
> not fit the slot that found it, and a change measured only in the proxy would be the exact mistake this file
> is warning about. The switches I built were reverted; the tree's engine is byte-identical to HEAD.
>
> The self-check above reports one disagreement: a code commit in this window with no kept record beside
> it. That commit is this report's own documentation commit, whose message begins "fixer 28nov" and which
> the checker reads as an engine change. No engine line was committed this run; the tree's engine is
> byte-identical to HEAD, and the attempt is recorded as a lead with nothing moved.

Accounts share 19% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **1.8 h ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18prize-01` | which documents would become CLEAN if 18_displacemen | 04:05 | 04:12 | 7 min |
| `61rank-02` | among the 61 genuine losses, which single Google che | 04:31 | 04:32 | 1 min |

## Timing

| | |
|:--|:--|
| Slot window | 04:00 → running · 31 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 57 |
| Longest silence | **8.7 min** — from 04:05:35, after `pending.py: reading the pending gate` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **2 min** | `##` |
| fix - diagnose and change the engine | **6 min** | `####` |
| measure or build - a conversion, screen or compile writes no beacon | **9 min** | `#######` |
| record - attempt, handoff, class rows | **2 min** | `##` |
| report - the report and the chain | **2 min** | `##` |
| other - not attributed to a tool | **7 min** | `#####` |

The unattributed row is 5 distinct beat(s) that matched no phase. They said:

- `pod warm, installing gate`
- `verifying the rung0 CSV independently on 8 documents`
- `rung=0, rebuilding engine`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

  written to tools/p2w-bench/REPORT.md - commit it, so the report survives the run
